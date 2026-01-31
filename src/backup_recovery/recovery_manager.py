"""
备份恢复管理器

从备份文件恢复数据到数据库

创建日期: 2025-10-11
版本: 1.0.0
"""

import json
import logging
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.data_access.postgresql_access import PostgreSQLDataAccess
from src.data_access.tdengine_access import TDengineDataAccess

# 数据库和存储访问
from src.storage.database.connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class RecoveryManager:
    """备份恢复管理器"""

    def __init__(self):
        self.conn_manager = DatabaseConnectionManager()
        self.tdengine_access = TDengineDataAccess()
        self.postgresql_access = PostgreSQLDataAccess()

        # 配置目录
        self.tdengine_backup_dir = Path("data/tdengine_backup")
        self.postgresql_backup_dir = Path("data/postgresql_backup")
        self.tdengine_backup_dir.mkdir(parents=True, exist_ok=True)
        self.postgresql_backup_dir.mkdir(parents=True, exist_ok=True)

    def restore_backup(self, backup_file: Path, recovery_id: str = None) -> Tuple[bool, str]:
        """
        恢复备份

        Args:
            backup_file: 备份文件路径
            recovery_id: 恢复任务ID

        Returns:
            (是否成功, 消息)
        """
        if recovery_id is None:
            recovery_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        log_file = Path(f"logs/recovery_{recovery_id}.log")
        self._log_recovery(log_file, f"开始恢复备份: {backup_file}")

        try:
            # 读取备份元数据
            metadata = self._read_backup_metadata(backup_file)
            if not metadata:
                msg = "无法读取备份元数据"
                self._log_recovery(log_file, msg)
                return False, msg

            db_type = metadata.get("database_type", "unknown")
            self._log_recovery(log_file, f"数据库类型: {db_type}")

            # 解压备份
            backup_dir = self.tdengine_backup_dir / f"{recovery_id}_extract"
            backup_dir.mkdir(parents=True, exist_ok=True)

            if backup_file.suffix == ".gz":
                with tarfile.open(backup_file, "r:gz") as tar:
                    # 安全地提取tar文件，防止路径遍历
                    def is_safe_path(path, base_path):
                        """检查tar文件中的路径是否安全，防止路径遍历"""
                        import os

                        # 规范化路径
                        normalized_path = os.path.normpath(path)
                        # 检查是否包含"../"或"..\"
                        if ".." in normalized_path.split(os.sep) or ".." in normalized_path.split("/"):
                            return False
                        # 检查规范化后的路径是否以基础路径开头
                        full_path = os.path.join(base_path, normalized_path)
                        return os.path.commonpath([base_path, full_path]) == base_path

                    # 验证所有成员路径
                    for member in tar.getmembers():
                        if not is_safe_path(member.name, str(backup_dir)):
                            raise ValueError(f"Unsafe path in tar file: {member.name}")

                    tar.extractall(backup_dir)
            else:
                # 已是解压目录
                shutil.copytree(backup_file, backup_dir, dirs_exist_ok=True)

            self._log_recovery(log_file, f"Backup extracted to {backup_dir}")

            # 恢复数据
            restored_count = 0
            parquet_files = list(backup_dir.glob("*.parquet"))

            for parquet_file in parquet_files:
                table_name = parquet_file.stem
                self._log_recovery(log_file, f"Restoring table: {table_name}")

                try:
                    if db_type == "TDengine":
                        # 恢复到TDengine
                        success = self._restore_to_tdengine(parquet_file, table_name)
                    elif db_type == "PostgreSQL":
                        # 恢复到PostgreSQL
                        success = self._restore_to_postgresql(parquet_file, table_name)
                    else:
                        self._log_recovery(log_file, f"Unsupported database type: {db_type}")
                        continue

                    if success:
                        restored_count += 1
                        self._log_recovery(log_file, f"Successfully restored: {table_name}")
                    else:
                        self._log_recovery(log_file, f"Failed to restore: {table_name}")

                except Exception as e:
                    self._log_recovery(log_file, f"Error restoring {table_name}: {e}")

            self._log_recovery(log_file, f"恢复完成: {restored_count} 个表")

            # 清理临时文件
            shutil.rmtree(backup_dir)

            msg = f"恢复成功: {restored_count} 个表"
            self._log_recovery(log_file, msg)
            return True, msg

        except Exception as e:
            error_msg = f"恢复失败: {e}"
            self._log_recovery(log_file, error_msg)
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def _read_backup_metadata(self, backup_file: Path) -> Dict[str, Any]:
        """读取备份元数据"""
        try:
            if backup_file.suffix == ".gz":
                with tarfile.open(backup_file, "r:gz") as tar:
                    # 查找metadata.json文件
                    for member in tar.getmembers():
                        if "metadata.json" in member.name:
                            f = tar.extractfile(member)
                            if f:
                                content = f.read().decode("utf-8")
                                return json.loads(content)
            elif backup_file.is_dir():
                # 目录形式的备份
                metadata_file = backup_file / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        return json.load(f)

        except Exception as e:
            logger.error("读取备份元数据失败: %s", e)

        return {}

    def _restore_to_tdengine(self, parquet_file: Path, table_name: str) -> bool:
        """将数据恢复到TDengine"""
        try:
            # 读取parquet文件
            import pandas as pd

            df = pd.read_parquet(parquet_file)

            # 插入到TDengine
            result = self.tdengine_access.insert_dataframe(table_name, df)
            logger.info("TDengine恢复数据: %s, %s 行", table_name, result)
            return result > 0

        except Exception as e:
            logger.error("恢复到TDengine失败 %s: %s", table_name, e)
            return False

    def _restore_to_postgresql(self, parquet_file: Path, table_name: str) -> bool:
        """将数据恢复到PostgreSQL"""
        try:
            # 读取parquet文件
            import pandas as pd

            df = pd.read_parquet(parquet_file)

            # 插入到PostgreSQL
            result = self.postgresql_access.insert_dataframe(table_name, df)
            logger.info("PostgreSQL恢复数据: %s, %s 行", table_name, result)
            return result > 0

        except Exception as e:
            logger.error("恢复到PostgreSQL失败 %s: %s", table_name, e)
            return False

    def _log_recovery(self, log_file: Path, message: str):
        """记录恢复日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def get_recovery_status(self, recovery_id: str) -> Dict[str, Any]:
        """获取恢复状态"""
        log_file = Path(f"logs/recovery_{recovery_id}.log")
        if not log_file.exists():
            return {"status": "not_found", "message": "恢复任务不存在"}

        # 简单的恢复状态检查
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 检查最后的日志条目
        if lines:
            last_line = lines[-1].strip()
            if "恢复成功" in last_line or "成功: " in last_line:
                status = "completed"
            elif "恢复失败" in last_line or "失败:" in last_line:
                status = "failed"
            else:
                status = "running"
        else:
            status = "unknown"

        return {
            "status": status,
            "log_file": str(log_file),
            "last_update": datetime.now().isoformat(),
        }

    def list_recovery_tasks(self) -> List[Dict[str, Any]]:
        """列出所有恢复任务"""
        recovery_logs = list(Path("logs").glob("recovery_*.log"))
        tasks = []

        for log_file in recovery_logs:
            task_id = log_file.stem.replace("recovery_", "")
            status_info = self.get_recovery_status(task_id)

            tasks.append(
                {
                    "task_id": task_id,
                    "status": status_info["status"],
                    "log_file": str(log_file),
                    "last_update": status_info["last_update"],
                }
            )

        # 按时间排序（最新的在前）
        tasks.sort(key=lambda x: x["last_update"], reverse=True)
        return tasks


def main():
    """主函数 - 用于测试"""
    recovery_manager = RecoveryManager()

    # 示例用法
    backup_file = Path("data/backup_example.tar.gz")
    if backup_file.exists():
        success, msg = recovery_manager.restore_backup(backup_file)
        print(f"恢复结果: {success}, 消息: {msg}")
    else:
        print(f"备份文件不存在: {backup_file}")

    # 列出所有恢复任务
    tasks = recovery_manager.list_recovery_tasks()
    print(f"恢复任务列表: {tasks}")


if __name__ == "__main__":
    main()
