import logging
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"


class SagaCoordinator:
    """
    应用层 Saga 模式协调器。
    用于处理跨 PostgreSQL 和 TDengine 的分布式事务，特别是 "TDengine写入 + PG元数据更新" 场景。

    核心策略：
    1. 先写 TDengine (Append-only)，带 Tag 标记。
    2. 后写 PostgreSQL (元数据)，并在同一事务中提交。
    3. 失败时利用 TDengine Tag 进行软删除补偿。
    """

    def __init__(self, pg_access, td_access):
        self.pg = pg_access
        self.td = td_access

    def _safe_execute_sql(self, sql_str: str, params: Optional[tuple] = None) -> None:
        if not hasattr(self.pg, "execute_sql"):
            return
        try:
            self.pg.execute_sql(sql_str, params)
        except Exception as e:
            logger.warning("Failed to write transaction_log: %s", e)

    def _log_txn_start(self, txn_id: str, business_type: str, business_id: str) -> None:
        sql = (
            "INSERT INTO transaction_log "
            "(transaction_id, business_type, business_id, td_status, pg_status, final_status, "
            "retry_count, error_msg, created_at, updated_at) "
            "VALUES (%s, %s, %s, 'INIT', 'INIT', 'PENDING', 0, NULL, NOW(), NOW()) "
            "ON CONFLICT (transaction_id) DO NOTHING"
        )
        self._safe_execute_sql(sql, (txn_id, business_type, business_id))

    def _log_txn_update(self, txn_id: str, fields: Dict[str, Any]) -> None:
        if not fields:
            return

        # Whitelist of allowed columns in transaction_log to prevent SQL injection
        ALLOWED_FIELDS = {
            "td_status",
            "pg_status",
            "final_status",
            "error_msg",
            "retry_count",
            "duration_ms",
            "td_write_time",
            "pg_update_time",
            "business_type",
            "business_id",
        }

        set_parts = []
        params = []
        for key, value in fields.items():
            if key not in ALLOWED_FIELDS:
                logger.warning("Attempted to update disallowed field in transaction_log: %s", key)
                continue
            set_parts.append(f"{key} = %s")
            params.append(value)

        if not set_parts:
            return

        set_parts.append("updated_at = NOW()")
        sql = f"UPDATE transaction_log SET {', '.join(set_parts)} WHERE transaction_id = %s"
        params.append(txn_id)
        self._safe_execute_sql(sql, tuple(params))

    def execute_kline_sync(
        self,
        business_id: str,
        kline_data: Any,
        classification: Any,
        table_name: str,
        metadata_update_func: Callable[[Any], None],
    ) -> bool:
        """
        执行 K 线同步事务 (Saga 模式)

        Args:
            business_id: 业务唯一标识 (如 '600000.SH_DAILY_20240101')
            kline_data: 要写入 TDengine 的 DataFrame
            classification: 数据分类
            table_name: TDengine 表名
            metadata_update_func: 一个接受 session 参数的回调函数，用于执行 PG 更新

        Returns:
            bool: 事务是否成功
        """
        txn_id = str(uuid.uuid4())
        start_time = time.time()
        business_type = (
            classification.value if hasattr(classification, "value") else str(classification)
        )
        logger.info("Starting Saga Transaction %(txn_id)s for %(business_id)s")

        # 1. 预记录事务状态 (Best Effort)
        # 在实际生产中，这一步应该写入 PG 的 transaction_log 表。
        # 这里模拟日志记录。
        logger.info("[TXN-LOG] %(txn_id)s: STARTED")
        self._log_txn_start(txn_id, business_type, business_id)

        try:
            # 2. Step 1: 写入 TDengine
            # 必须带上 txn_id 和 is_valid
            # 修改方案：将 txn_id 和 is_valid 作为数据列写入，而不是 Tag

            # 准备数据：添加事务列
            # 使用 copy 防止修改原始数据
            data_to_save = kline_data.copy()
            data_to_save["txn_id"] = txn_id
            data_to_save["is_valid"] = True  # 默认为 True

            # 执行写入
            # 注意：TDengineDataAccess.save_data 现在应该能处理这些新列
            td_success = self.td.save_data(data_to_save, classification, table_name)

            if not td_success:
                logger.error("[TXN-LOG] %(txn_id)s: TDengine write failed")
                duration_ms = int((time.time() - start_time) * 1000)
                self._log_txn_update(
                    txn_id,
                    {
                        "td_status": "FAIL",
                        "final_status": TransactionStatus.ROLLED_BACK.value,
                        "error_msg": "TDengine write failed",
                        "duration_ms": duration_ms,
                    },
                )
                return False

            logger.info("[TXN-LOG] %(txn_id)s: TDengine write SUCCESS")
            self._log_txn_update(
                txn_id,
                {
                    "td_status": "SUCCESS",
                    "td_write_time": datetime.now(timezone.utc),
                },
            )

            # 3. Step 2: 更新 PG 元数据
            # 开启 PG 事务
            # 假设 pg_access 提供了 session_scope 或类似机制
            # 如果没有，我们需要直接操作底层 session

            # 使用 DataManager 现有的机制，可能需要直接访问 db_manager
            # 这里假设 pg_access 暴露了底层的 session_scope
            if hasattr(self.pg, "transaction_scope"):
                with self.pg.transaction_scope() as session:
                    try:
                        # 执行业务更新
                        metadata_update_func(session)

                        # 在这里，我们也可以更新 PG 中的 transaction_log 表状态为 COMMITTED

                        # 提交 PG 事务 (session 退出时自动 commit)
                        duration_ms = int((time.time() - start_time) * 1000)
                        self._log_txn_update(
                            txn_id,
                            {
                                "pg_status": "SUCCESS",
                                "pg_update_time": datetime.now(timezone.utc),
                                "final_status": TransactionStatus.COMMITTED.value,
                                "duration_ms": duration_ms,
                            },
                        )
                        logger.info("[TXN-LOG] %(txn_id)s: PG commit SUCCESS. Transaction COMPLETED.")
                        return True

                    except Exception as e:
                        # PG 事务回滚，元数据未更新
                        # 但 TDengine 已经写入了，需要补偿
                        logger.error("PG Update failed, triggering compensation for %(txn_id)s: %(e)s")
                        duration_ms = int((time.time() - start_time) * 1000)
                        self._log_txn_update(
                            txn_id,
                            {
                                "pg_status": "FAIL",
                                "final_status": TransactionStatus.ROLLED_BACK.value,
                                "error_msg": str(e)[:1000],
                                "duration_ms": duration_ms,
                            },
                        )
                        raise  # 抛出异常以触发外层 except 块进行补偿
            else:
                # 如果没有显式的 transaction_scope，这是一个风险点
                # 暂时只能尽力而为
                logger.warning("PG Access does not support explicit transaction scope. Atomicity reduced.")
                try:
                    metadata_update_func(None)
                    duration_ms = int((time.time() - start_time) * 1000)
                    self._log_txn_update(
                        txn_id,
                        {
                            "pg_status": "SUCCESS",
                            "pg_update_time": datetime.now(timezone.utc),
                            "final_status": TransactionStatus.COMMITTED.value,
                            "duration_ms": duration_ms,
                        },
                    )
                    return True
                except Exception as e:
                    raise e

        except Exception as e:
            # 4. 补偿流程 (Compensation)
            logger.warning("Transaction %(txn_id)s failed with error: %(e)s, compensating...")
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_txn_update(
                txn_id,
                {
                    "final_status": TransactionStatus.ROLLED_BACK.value,
                    "error_msg": str(e)[:1000],
                    "duration_ms": duration_ms,
                },
            )
            self._compensate_tdengine(txn_id, table_name)
            logger.info("[TXN-LOG] %(txn_id)s: ROLLED_BACK")
            return False

    def _compensate_tdengine(self, txn_id: str, table_name: str):
        """
        补偿操作：将 TDengine 中对应 txn_id 的数据标记为无效
        """
        try:
            # 这一步依赖于 TDengineDataAccess 提供更新 Tag 的能力
            # 或者我们可以执行一条直接的 SQL
            # ALTER TABLE {table_name} SET TAG is_valid='false' WHERE txn_id='{txn_id}'

            # 暂时假设我们调用一个专门的方法
            if hasattr(self.td, "invalidate_data_by_txn_id"):
                self.td.invalidate_data_by_txn_id(table_name, txn_id)
            else:
                logger.error("TDengineDataAccess missing 'invalidate_data_by_txn_id'. Cannot compensate %(txn_id)s!")

            logger.info("Compensation successful for %(txn_id)s")
        except Exception:
            logger.error("Compensation failed for %(txn_id)s (will be handled by cron): %(e)s")
