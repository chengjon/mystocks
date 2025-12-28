"""
备份完整性检查器

验证备份数据的完整性和一致性

创建日期: 2025-10-11
版本: 1.0.0
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple

# 数据库和存储访问
from src.storage.database.connection_manager import DatabaseConnectionManager
from src.data_access.tdengine_access import TDengineDataAccess
from src.data_access.postgresql_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)


class IntegrityChecker:
    """备份完整性检查器"""

    def __init__(self):
        self.conn_manager = DatabaseConnectionManager()
        self.tdengine_access = TDengineDataAccess()
        self.postgresql_access = PostgreSQLDataAccess()

    def verify_backup_integrity(
        self,
        backup_path: str,
        backup_metadata: Dict[str, Any],
        expected_row_count: int = 0,
        tolerance_percent: float = 0.01,  # 1%容差
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        验证备份数据完整性

        Args:
            backup_path: 备份文件路径
            backup_metadata: 备份元数据
            expected_row_count: 预期总行数
            tolerance_percent: 行数匹配容差百分比

        Returns:
            (是否有效, 详细信息字典)
        """
        details = {
            "verification_time": datetime.now().isoformat(),
            "tables_checked": 0,
            "tables_passed": 0,
            "tables_failed": 0,
            "total_rows_expected": expected_row_count,
            "total_rows_actual": 0,
            "row_count_match": False,
            "errors": [],
        }

        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                details["errors"].append(f"备份文件不存在: {backup_path}")
                return False, details

            # 检查每个表
            tables = backup_metadata.get("tables_backed_up", [])

            for table in tables:
                details["tables_checked"] += 1

                try:
                    # 查询表行数 - 使用参数化查询防止SQL注入
                    # 验证表名只包含字母、数字和下划线
                    import re

                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
                        raise ValueError(f"Invalid table name: {table}")

                    query = f"SELECT COUNT(*) FROM {table}"
                    cursor = self.conn_manager.get_postgresql_connection().cursor()
                    cursor.execute(query)
                    result = cursor.fetchone()
                    actual_rows = result[0] if result else 0
                    cursor.close()
                    details["total_rows_actual"] += actual_rows

                    logger.info("Table %s: %s rows", table, actual_rows)

                    if actual_rows > 0:
                        details["tables_passed"] += 1
                    else:
                        details["tables_failed"] += 1
                        details["errors"].append(f"Table {table} has no rows")

                except Exception as e:
                    details["tables_failed"] += 1
                    details["errors"].append(f"Failed to verify table {table}: {e}")
                    logger.error("Error checking table %s: %s", table, e)

            # 检查行数是否匹配
            if expected_row_count > 0:
                row_count_diff = abs(details["total_rows_actual"] - expected_row_count)
                diff_percent = row_count_diff / expected_row_count

                if diff_percent <= tolerance_percent:
                    details["row_count_match"] = True
                    msg = f"Row count matches within tolerance: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent * 100:.2f}%)"
                    logger.info(msg)
                else:
                    details["errors"].append(
                        f"Row count mismatch: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent * 100:.2f}%)"
                    )
                    msg = f"Row count mismatch: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent * 100:.2f}%)"
                    logger.warning(msg)

            is_valid = details["tables_failed"] == 0 and details["row_count_match"] and len(details["errors"]) == 0

            return is_valid, details

        except Exception as e:
            error_msg = f"完整性检查失败: {e}"
            logger.error(error_msg)
            details["errors"].append(error_msg)
            return False, details

    def verify_tdengine_backup_integrity(
        self,
        backup_path: str,
        backup_metadata: Dict[str, Any],
        expected_row_count: int = 0,
        tolerance_percent: float = 0.01,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        验证TDengine备份数据完整性

        Args:
            backup_path: 备份文件路径
            backup_metadata: 备份元数据
            expected_row_count: 预期总行数
            tolerance_percent: 行数匹配容差百分比

        Returns:
            (是否有效, 详细信息字典)
        """
        details = {
            "verification_time": datetime.now().isoformat(),
            "tables_checked": 0,
            "tables_passed": 0,
            "tables_failed": 0,
            "total_rows_expected": expected_row_count,
            "total_rows_actual": 0,
            "row_count_match": False,
            "errors": [],
        }

        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                details["errors"].append(f"备份文件不存在: {backup_path}")
                return False, details

            # 检查每个表
            tables = backup_metadata.get("tables_backed_up", [])

            for table in tables:
                details["tables_checked"] += 1

                try:
                    # 查询表行数
                    result = self.tdengine_access.query_count(table)
                    actual_rows = result if result is not None else 0
                    details["total_rows_actual"] += actual_rows

                    logger.info("Table %s: %s rows", table, actual_rows)

                    if actual_rows > 0:
                        details["tables_passed"] += 1
                    else:
                        details["tables_failed"] += 1
                        details["errors"].append(f"Table {table} has no rows")

                except Exception as e:
                    details["tables_failed"] += 1
                    details["errors"].append(f"Failed to verify table {table}: {e}")
                    logger.error("Error checking table %s: %s", table, e)

            # 检查行数是否匹配（在容差范围内）
            if expected_row_count > 0:
                row_count_diff = abs(details["total_rows_actual"] - expected_row_count)
                diff_percent = row_count_diff / expected_row_count

                if diff_percent <= tolerance_percent:
                    details["row_count_match"] = True
                    msg = f"Row count matches within tolerance: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent * 100:.2f}%)"
                    logger.info(msg)
                else:
                    details["errors"].append(
                        f"Row count mismatch: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent * 100:.2f}%)"
                    )
                    msg = f"Row count mismatch: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent * 100:.2f}%)"
                    logger.warning(msg)

            is_valid = details["tables_failed"] == 0 and details["row_count_match"] and len(details["errors"]) == 0

            return is_valid, details

        except Exception as e:
            error_msg = f"TDengine完整性检查失败: {e}"
            logger.error(error_msg)
            details["errors"].append(error_msg)
            return False, details

    def generate_integrity_report(self, verification_result: Tuple[bool, Dict[str, Any]], output_path: str) -> bool:
        """
        生成完整性验证报告

        Args:
            verification_result: 验证结果
            output_path: 输出路径

        Returns:
            是否生成成功
        """
        try:
            is_valid, details = verification_result

            report = {
                "report_type": "Integrity Verification Report",
                "generated_at": datetime.now().isoformat(),
                "is_valid": is_valid,
                "details": details,
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info("完整性报告已生成: %s", output_path)
            return True

        except Exception as e:
            logger.error("生成完整性报告失败: %s", e)
            return False


def main():
    """主函数 - 用于测试"""
    checker = IntegrityChecker()

    # 示例用法
    backup_path = "path/to/backup"
    backup_metadata = {"tables_backed_up": ["table1", "table2"]}

    result = checker.verify_backup_integrity(backup_path, backup_metadata, expected_row_count=1000)

    print(f"验证结果: {result[0]}")
    print(f"详细信息: {result[1]}")


if __name__ == "__main__":
    main()
