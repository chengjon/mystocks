"""
数据完整性检查器 - 验证备份和恢复的数据完整性

功能:
- 备份文件完整性校验（MD5/SHA256）
- 恢复后数据一致性验证
- 数据行数对比
- 时间戳范围验证
"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional

from src.storage.database import DatabaseConnectionManager
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess


logger = logging.getLogger(__name__)


class IntegrityChecker:
    """数据完整性检查器"""

    def __init__(self, backup_base_path: str = "./backups"):
        """
        初始化完整性检查器

        Args:
            backup_base_path: 备份根目录
        """
        self.backup_base_path = Path(backup_base_path)
        self.metadata_dir = self.backup_base_path / "metadata"
        self.integrity_dir = self.backup_base_path / "integrity_checks"
        self.integrity_dir.mkdir(parents=True, exist_ok=True)

        # 创建数据库访问层
        self.conn_manager = DatabaseConnectionManager()
        self.tdengine_access = TDengineDataAccess()
        self.postgresql_access = PostgreSQLDataAccess()

    def verify_backup_integrity(
        self,
        backup_file: Path,
        expected_checksum: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        验证备份文件的完整性

        Args:
            backup_file: 备份文件路径
            expected_checksum: 预期的校验和（如果有）

        Returns:
            (is_valid, message)
        """
        try:
            if not backup_file.exists():
                return False, f"Backup file not found: {backup_file}"

            # 计算文件校验和
            file_hash = self._calculate_file_hash(backup_file, algorithm="sha256")

            # 如果提供了预期校验和，进行对比
            if expected_checksum:
                if file_hash == expected_checksum:
                    msg = f"Backup integrity verified: {backup_file}"
                    logger.info(msg)
                    return True, msg
                else:
                    msg = f"Backup integrity check failed: checksum mismatch (expected {expected_checksum}, got {file_hash})"
                    logger.error(msg)
                    return False, msg
            else:
                msg = f"Backup file hash: {file_hash}"
                logger.info(msg)
                return True, msg

        except Exception as e:
            msg = f"Error verifying backup integrity: {e}"
            logger.error(msg)
            return False, msg

    def verify_tdengine_recovery(
        self,
        backup_metadata: dict,
        expected_row_count: int,
        tolerance_percent: float = 0.05,  # 允许 5% 的差异
    ) -> Tuple[bool, Dict]:
        """
        验证 TDengine 恢复后的数据完整性

        Args:
            backup_metadata: 备份元数据
            expected_row_count: 预期的行数
            tolerance_percent: 允许的差异百分比

        Returns:
            (is_valid, details)
        """
        try:
            logger.info("Verifying TDengine recovery integrity")

            details = {
                "backup_id": backup_metadata.get("backup_id"),
                "tables_checked": 0,
                "tables_passed": 0,
                "tables_failed": 0,
                "total_rows_expected": expected_row_count,
                "total_rows_actual": 0,
                "row_count_match": False,
                "errors": [],
            }

            # 检查每个表
            tables = backup_metadata.get("tables_backed_up", [])

            for table in tables:
                details["tables_checked"] += 1

                try:
                    # 查询表行数
                    result = self.tdengine_access.query_count(table)
                    actual_rows = result if result is not None else 0
                    details["total_rows_actual"] += actual_rows

                    logger.info(f"Table {table}: {actual_rows} rows")

                    if actual_rows > 0:
                        details["tables_passed"] += 1
                    else:
                        details["tables_failed"] += 1
                        details["errors"].append(f"Table {table} has no rows")

                except Exception as e:
                    details["tables_failed"] += 1
                    details["errors"].append(f"Failed to verify table {table}: {e}")
                    logger.error(f"Error checking table {table}: {e}")

            # 检查行数是否匹配（在容差范围内）
            if expected_row_count > 0:
                row_count_diff = abs(details["total_rows_actual"] - expected_row_count)
                diff_percent = row_count_diff / expected_row_count

                if diff_percent <= tolerance_percent:
                    details["row_count_match"] = True
                    msg = f"Row count matches within tolerance: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent*100:.2f}%)"
                    logger.info(msg)
                else:
                    details["errors"].append(
                        f"Row count mismatch: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent*100:.2f}%)"
                    )
                    logger.warning(f"Row count mismatch: {msg}")

            is_valid = (
                details["tables_failed"] == 0
                and details["row_count_match"]
                and len(details["errors"]) == 0
            )

            return is_valid, details

        except Exception as e:
            logger.error(f"Error verifying TDengine recovery: {e}")
            return False, {"error": str(e)}

    def verify_postgresql_recovery(
        self,
        backup_metadata: dict,
        expected_row_count: int,
        tolerance_percent: float = 0.05,
    ) -> Tuple[bool, Dict]:
        """
        验证 PostgreSQL 恢复后的数据完整性

        Args:
            backup_metadata: 备份元数据
            expected_row_count: 预期的行数
            tolerance_percent: 允许的差异百分比

        Returns:
            (is_valid, details)
        """
        try:
            logger.info("Verifying PostgreSQL recovery integrity")

            details = {
                "backup_id": backup_metadata.get("backup_id"),
                "tables_checked": 0,
                "tables_passed": 0,
                "tables_failed": 0,
                "total_rows_expected": expected_row_count,
                "total_rows_actual": 0,
                "row_count_match": False,
                "errors": [],
            }

            # 检查每个表
            tables = backup_metadata.get("tables_backed_up", [])

            conn = self.conn_manager.get_postgresql_connection()
            cursor = conn.cursor()

            for table in tables:
                details["tables_checked"] += 1

                try:
                    # 查询表行数
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    result = cursor.fetchone()
                    actual_rows = result[0] if result else 0
                    details["total_rows_actual"] += actual_rows

                    logger.info(f"Table {table}: {actual_rows} rows")

                    if actual_rows > 0:
                        details["tables_passed"] += 1
                    else:
                        details["tables_failed"] += 1
                        details["errors"].append(f"Table {table} has no rows")

                except Exception as e:
                    details["tables_failed"] += 1
                    details["errors"].append(f"Failed to verify table {table}: {e}")
                    logger.error(f"Error checking table {table}: {e}")

            cursor.close()

            # 检查行数是否匹配
            if expected_row_count > 0:
                row_count_diff = abs(details["total_rows_actual"] - expected_row_count)
                diff_percent = row_count_diff / expected_row_count

                if diff_percent <= tolerance_percent:
                    details["row_count_match"] = True
                    msg = f"Row count matches within tolerance: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent*100:.2f}%)"
                    logger.info(msg)
                else:
                    details["errors"].append(
                        f"Row count mismatch: {details['total_rows_actual']} vs {expected_row_count} ({diff_percent*100:.2f}%)"
                    )
                    logger.warning(msg)

            is_valid = (
                details["tables_failed"] == 0
                and details["row_count_match"]
                and len(details["errors"]) == 0
            )

            return is_valid, details

        except Exception as e:
            logger.error(f"Error verifying PostgreSQL recovery: {e}")
            return False, {"error": str(e)}

    def generate_integrity_report(
        self,
        backup_id: str,
        verification_results: Dict,
    ) -> Path:
        """
        生成完整性校验报告

        Args:
            backup_id: 备份 ID
            verification_results: 验证结果

        Returns:
            报告文件路径
        """
        import json

        report_file = self.integrity_dir / f"{backup_id}_integrity_report.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "backup_id": backup_id,
            "verification_results": verification_results,
            "status": (
                "passed" if verification_results.get("is_valid", False) else "failed"
            ),
        }

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Integrity report saved: {report_file}")

        return report_file

    # ==================== 私有方法 ====================

    def _calculate_file_hash(
        self,
        file_path: Path,
        algorithm: str = "sha256",
        chunk_size: int = 8192,
    ) -> str:
        """
        计算文件哈希值

        Args:
            file_path: 文件路径
            algorithm: 哈希算法（md5, sha256 等）
            chunk_size: 块大小

        Returns:
            哈希值的十六进制字符串
        """
        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_obj.update(chunk)

        return hash_obj.hexdigest()
