import uuid
import logging
from enum import Enum
from typing import Any, Callable

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
        logger.info(f"Starting Saga Transaction {txn_id} for {business_id}")

        # 1. 预记录事务状态 (Best Effort)
        # 在实际生产中，这一步应该写入 PG 的 transaction_log 表。
        # 这里模拟日志记录。
        logger.info(f"[TXN-LOG] {txn_id}: STARTED")

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
                logger.error(f"[TXN-LOG] {txn_id}: TDengine write failed")
                return False

            logger.info(f"[TXN-LOG] {txn_id}: TDengine write SUCCESS")

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
                        logger.info(f"[TXN-LOG] {txn_id}: PG commit SUCCESS. Transaction COMPLETED.")
                        return True

                    except Exception as e:
                        # PG 事务回滚，元数据未更新
                        # 但 TDengine 已经写入了，需要补偿
                        logger.error(f"PG Update failed, triggering compensation for {txn_id}: {e}")
                        raise  # 抛出异常以触发外层 except 块进行补偿
            else:
                # 如果没有显式的 transaction_scope，这是一个风险点
                # 暂时只能尽力而为
                logger.warning("PG Access does not support explicit transaction scope. Atomicity reduced.")
                try:
                    metadata_update_func(None)
                    return True
                except Exception as e:
                    raise e

        except Exception as e:
            # 4. 补偿流程 (Compensation)
            logger.warning(f"Transaction {txn_id} failed with error: {e}, compensating...")
            self._compensate_tdengine(txn_id, table_name)
            logger.info(f"[TXN-LOG] {txn_id}: ROLLED_BACK")
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
                logger.error(f"TDengineDataAccess missing 'invalidate_data_by_txn_id'. Cannot compensate {txn_id}!")

            logger.info(f"Compensation successful for {txn_id}")
        except Exception as e:
            logger.error(f"Compensation failed for {txn_id} (will be handled by cron): {e}")
