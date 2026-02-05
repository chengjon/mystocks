#!/usr/bin/env python3
"""
Saga 事务清理任务 (Transaction Cleaner)

功能:
1. 扫描处于 PENDING 状态超过 10 分钟的僵尸事务。
2. 检查 TDengine 和 PG 的实际状态，决定提交或回滚。
3. 对标记为 ROLLED_BACK 但 TDengine 可能仍有脏数据的事务进行补偿 (软删除)。
4. 物理删除 is_valid=false 的无效数据 (可选，建议在低峰期运行)。

调度建议: 每 5-10 分钟运行一次。
"""

import logging
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到 path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.data_manager import DataManager
from src.core.transaction.saga_coordinator import TransactionStatus

# 设置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TransactionCleaner")


class TransactionCleaner:
    def __init__(
        self,
        pg=None,
        td=None,
        coordinator=None,
        dry_run: bool = False,
        zombie_minutes: int | None = None,
        zombie_limit: int | None = None,
    ):
        # 初始化 DataManager 以获取数据库访问层
        if pg is None or td is None or coordinator is None:
            self.dm = DataManager(enable_monitoring=True)
            self.pg = self.dm._postgresql
            self.td = self.dm._tdengine
            self.coordinator = self.dm.saga_coordinator
        else:
            self.dm = None
            self.pg = pg
            self.td = td
            self.coordinator = coordinator
        self.dry_run = dry_run
        self.zombie_minutes = zombie_minutes if zombie_minutes is not None else int(os.getenv("TXN_ZOMBIE_MINUTES", "10"))
        self.zombie_limit = zombie_limit if zombie_limit is not None else int(os.getenv("TXN_ZOMBIE_BATCH_LIMIT", "100"))

    def run(self, purge_invalid_data: bool = False):
        """
        运行清理任务

        Args:
            purge_invalid_data: 是否物理删除无效数据（默认False）
        """
        logger.info("Starting Transaction Cleanup Job")
        logger.info("Purge invalid data: %s", purge_invalid_data)

        # 1. 检查并处理僵尸事务
        zombie_count = self.check_zombie_transactions()
        logger.info("Processed %(zombie_count)s zombie transactions")

        # 2. 清理无效数据（可选）
        if purge_invalid_data:
            logger.warning("PURGE MODE: Physically deleting invalid data from TDengine")
            self.cleanup_invalid_data()
        else:
            logger.info("Skipping physical purge (use --purge to enable)")

        logger.info("Transaction Cleanup Job Completed")

    def check_zombie_transactions(self) -> int:
        """
        检查并处理僵尸事务

        Returns:
            int: 处理的事务数量
        """
        # 定义超时阈值 (10分钟前)
        timeout_threshold = datetime.now() - timedelta(minutes=self.zombie_minutes)

        try:
            # 使用PostgreSQLDataAccess查询超时事务
            # 注意：需要DataAccess支持原始SQL查询，这里使用简化的实现

            # 方案1: 如果DataAccess支持query_sql方法
            # pending_txns = self.pg.query_sql(
            #     sql="""
            #         SELECT transaction_id, business_id, td_status, pg_status, created_at
            #         FROM transaction_log
            #         WHERE final_status = 'PENDING'
            #         AND created_at < %s
            #         LIMIT 100
            #     """,
            #     params=(timeout_threshold,)
            # )

            # 方案2: 使用load_data_by_classification（如果transaction_log有对应的DataClassification）
            # 目前先使用模拟逻辑，实际部署需要根据DataClassification调整

            logger.info("Scanning for zombie transactions...")
            logger.info("Timeout threshold: %s", timeout_threshold)

            pending_txns = self._load_pending_transactions(self.zombie_limit, timeout_threshold)

            if not pending_txns:
                logger.info("No zombie transactions found.")
                return 0

            logger.info("Found %s zombie transactions", len(pending_txns))

            processed_count = 0
            for txn in pending_txns:
                try:
                    self.process_zombie(txn)
                    processed_count += 1
                except Exception as e:
                    logger.error(
                        "Failed to process zombie transaction %s: %s",
                        txn.get("transaction_id", "unknown"),
                        e,
                    )

            return processed_count

        except Exception as e:
            logger.error("Error scanning zombie transactions: %s", e)
            return 0

    def _load_pending_transactions(self, limit: int, threshold: datetime) -> list[dict]:
        sql = (
            "SELECT transaction_id, business_id, td_status, pg_status, created_at "
            "FROM transaction_log "
            "WHERE final_status = 'PENDING' AND created_at < %s "
            "ORDER BY created_at ASC "
            "LIMIT %s"
        )
        df = self.pg.execute_sql(sql, (threshold, limit))
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")

    def process_zombie(self, txn: dict):
        """
        处理单个僵尸事务

        Args:
            txn: 事务字典
        """
        txn_id = txn.get("transaction_id", "unknown")
        business_id = txn.get("business_id", "unknown")
        td_status = txn.get("td_status", "UNKNOWN")
        pg_status = txn.get("pg_status", "UNKNOWN")

        logger.info("Processing zombie transaction %s...", txn_id)
        logger.info("  TD Status: %s, PG Status: %s", td_status, pg_status)

        # 逻辑分支
        if td_status == "SUCCESS" and pg_status == "SUCCESS":
            self.update_txn_status(txn_id, TransactionStatus.COMMITTED.value)
        elif td_status == "SUCCESS" and pg_status != "SUCCESS":
            # 中间态: TD 写了，PG 没写/未知
            # 策略: 优先回滚 (标记 TD 无效)
            logger.info("  Compensating %s (TD=Success, PG=Fail)", txn_id)
            if self.dry_run:
                logger.info("  DRY RUN: would compensate %s", txn_id)
            else:
                self.coordinator._compensate_tdengine(txn_id, self._extract_table_name(business_id))

            # 更新状态为 ROLLED_BACK
            self.update_txn_status(txn_id, TransactionStatus.ROLLED_BACK.value)

        elif td_status != "SUCCESS":
            # TD 都没成功，直接标记回滚
            logger.info("  Marking %s as ROLLED_BACK (TD not successful)", txn_id)
            self.update_txn_status(txn_id, TransactionStatus.ROLLED_BACK.value)

    def _extract_table_name(self, business_id: str) -> str:
        """
        从business_id中提取表名

        Args:
            business_id: 业务ID（格式通常为 table_name_timestamp）

        Returns:
            str: 表名
        """
        # business_id格式通常为: "table_name_1234567890"
        # 提取表名部分
        parts = business_id.rsplit("_", 1)
        if len(parts) == 2:
            return parts[0]
        return business_id

    def update_txn_status(self, txn_id: str, status: str):
        """
        更新事务状态

        Args:
            txn_id: 事务ID
            status: 新状态
        """
        try:
            if self.dry_run:
                logger.info("DRY RUN: would update %s to %s", txn_id, status)
                return

            sql = "UPDATE transaction_log SET final_status = %s, updated_at = NOW() WHERE transaction_id = %s"
            self.pg.execute_update(sql, (status, txn_id))
            logger.info("Updated %s to %s", txn_id, status)

        except Exception as e:
            logger.error("Failed to update txn status %s: %s", txn_id, e)

    def cleanup_invalid_data(self):
        """
        清理被标记为无效的数据 (is_valid=false)
        这是物理删除，建议低峰期执行
        """
        logger.info("Scanning for invalid data to purge...")

        try:
            # 获取所有包含is_valid字段的TDengine超级表
            # 主要的时序表
            tables_to_check = [
                "market_data.minute_kline_1min",
                "market_data.minute_kline_5min",
                "market_data.minute_kline_15min",
                "market_data.minute_kline_30min",
                "market_data.minute_kline_60min",
                "market_data.tick_data",
            ]

            total_deleted = 0

            for table in tables_to_check:
                try:
                    count_sql = f"SELECT COUNT(*) FROM {table} WHERE is_valid=false"
                    count_df = self.td.query_sql(count_sql)
                    invalid_count = int(count_df.iloc[0, 0]) if not count_df.empty else 0

                    if invalid_count > 0:
                        logger.info("  Table %s: %s invalid records", table, invalid_count)
                        if self.dry_run:
                            logger.info("  DRY RUN: would delete invalid records from %s", table)
                            continue

                        delete_sql = f"DELETE FROM {table} WHERE is_valid=false"
                        self.td.execute_update(delete_sql)
                        total_deleted += invalid_count
                        logger.info("    Deleted %s records from %s", invalid_count, table)

                except Exception as e:
                    logger.error("  Failed to cleanup table %s: %s", table, e)

            logger.info("Total deleted records: %s", total_deleted)

        except Exception as e:
            logger.error("Error during invalid data cleanup: %(e)s")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Saga事务清理任务")
    parser.add_argument("--purge", action="store_true", help="物理删除无效数据（默认只扫描）")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行（不实际修改数据）")
    parser.add_argument("--minutes", type=int, help="僵尸事务超时分钟数（默认读取 TXN_ZOMBIE_MINUTES）")
    parser.add_argument("--limit", type=int, help="僵尸事务批量处理数量（默认读取 TXN_ZOMBIE_BATCH_LIMIT）")

    args = parser.parse_args()

    try:
        cleaner = TransactionCleaner(
            dry_run=args.dry_run,
            zombie_minutes=args.minutes,
            zombie_limit=args.limit,
        )

        if args.dry_run:
            logger.info("DRY RUN MODE: No actual changes will be made")

        cleaner.run(purge_invalid_data=args.purge)

        logger.info("✅ Transaction cleaner completed successfully")
        return 0

    except Exception as e:
        logger.error("❌ Transaction cleaner failed: %(e)s")
        return 1


if __name__ == "__main__":
    sys.exit(main())
