"""
备份管理器 - 支持 TDengine 和 PostgreSQL 的完整备份

策略:
- TDengine: 日全量备份 + 小时增量备份
- PostgreSQL: 日全量备份 + WAL 归档
"""

import os
import gzip
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from src.storage.database import DatabaseConnectionManager
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess


logger = logging.getLogger(__name__)


@dataclass
class BackupMetadata:
    """备份元数据"""

    backup_id: str
    backup_type: str  # 'full' or 'incremental'
    database: str  # 'tdengine' or 'postgresql'
    start_time: str
    end_time: str
    duration_seconds: float
    tables_backed_up: List[str]
    total_rows: int
    backup_size_bytes: int
    compression_ratio: float
    status: str  # 'success' or 'failed'
    error_message: Optional[str] = None
    checksum: Optional[str] = None


class BackupManager:
    """备份管理器"""

    def __init__(
        self,
        backup_base_path: str = "./backups",
        compression: bool = True,
        retention_days: int = 30,
    ):
        """
        初始化备份管理器

        Args:
            backup_base_path: 备份根目录
            compression: 是否压缩备份
            retention_days: 备份保留天数
        """
        self.backup_base_path = Path(backup_base_path)
        self.backup_base_path.mkdir(parents=True, exist_ok=True)

        self.compression = compression
        self.retention_days = retention_days

        # 创建数据库访问层
        self.conn_manager = DatabaseConnectionManager()
        self.tdengine_access = TDengineDataAccess()
        self.postgresql_access = PostgreSQLDataAccess()

        # 备份目录结构
        self.tdengine_backup_dir = self.backup_base_path / "tdengine"
        self.postgresql_backup_dir = self.backup_base_path / "postgresql"
        self.metadata_dir = self.backup_base_path / "metadata"

        for d in [
            self.tdengine_backup_dir,
            self.postgresql_backup_dir,
            self.metadata_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def backup_tdengine_full(self) -> BackupMetadata:
        """
        TDengine 全量备份

        Returns:
            BackupMetadata: 备份元数据
        """
        start_time = datetime.now()
        backup_id = f"tdengine_full_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(f"Starting TDengine full backup: {backup_id}")

            # 获取所有表
            tables = self._get_tdengine_tables()
            backup_dir = self.tdengine_backup_dir / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            total_rows = 0
            backup_files = []

            # 备份每个表
            for table in tables:
                logger.info(f"Backing up TDengine table: {table}")

                # 查询表数据
                df = self.tdengine_access.query_all(table)

                if df is not None and len(df) > 0:
                    total_rows += len(df)

                    # 保存为 Parquet 格式（压缩效率更好）
                    table_file = backup_dir / f"{table}.parquet"
                    df.to_parquet(table_file, compression="snappy")
                    backup_files.append(table_file)

                    logger.info(f"  Backed up {len(df)} rows from {table}")

            # 计算备份大小和压缩率
            original_size = sum(f.stat().st_size for f in backup_files)

            # 如果启用压缩，打包整个备份目录
            compressed_file = None
            if self.compression:
                compressed_file = self.tdengine_backup_dir / f"{backup_id}.tar.gz"
                with gzip.open(compressed_file, "wb") as tar:
                    for file in backup_files:
                        tar.write(file, arcname=file.name)

                compressed_size = compressed_file.stat().st_size
                compression_ratio = (
                    original_size / compressed_size if compressed_size > 0 else 0
                )

                # 删除未压缩的文件
                shutil.rmtree(backup_dir)
                backup_size = compressed_size
            else:
                backup_size = original_size
                compression_ratio = 1.0

            # 创建元数据
            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type="full",
                database="tdengine",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                tables_backed_up=tables,
                total_rows=total_rows,
                backup_size_bytes=backup_size,
                compression_ratio=compression_ratio,
                status="success",
            )

            # 保存元数据
            self._save_metadata(metadata)

            logger.info(
                f"TDengine full backup completed: {backup_id}, "
                f"rows={total_rows}, size={backup_size/1024/1024:.2f}MB, "
                f"ratio={compression_ratio:.2f}x"
            )

            return metadata

        except Exception as e:
            logger.error(f"TDengine full backup failed: {e}")

            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type="full",
                database="tdengine",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                tables_backed_up=[],
                total_rows=0,
                backup_size_bytes=0,
                compression_ratio=0.0,
                status="failed",
                error_message=str(e),
            )

            self._save_metadata(metadata)
            return metadata

    def backup_tdengine_incremental(self, since_backup_id: str) -> BackupMetadata:
        """
        TDengine 增量备份（基于时间戳）

        Args:
            since_backup_id: 上次备份的 ID

        Returns:
            BackupMetadata: 备份元数据
        """
        start_time = datetime.now()
        backup_id = f"tdengine_incr_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(f"Starting TDengine incremental backup: {backup_id}")

            # 获取上次备份的时间戳
            since_metadata = self._load_metadata(since_backup_id)
            if not since_metadata:
                logger.warning(
                    f"Previous backup {since_backup_id} not found, doing full backup instead"
                )
                return self.backup_tdengine_full()

            since_time = datetime.fromisoformat(since_metadata["end_time"])

            # 获取所有表
            tables = self._get_tdengine_tables()
            backup_dir = self.tdengine_backup_dir / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            total_rows = 0
            backup_files = []

            # 备份每个表的增量数据
            for table in tables:
                logger.info(f"Backing up TDengine incremental data from {table}")

                # 查询增量数据
                df = self.tdengine_access.query_by_time_range(
                    table, since_time, datetime.now()
                )

                if df is not None and len(df) > 0:
                    total_rows += len(df)

                    # 保存为 Parquet 格式
                    table_file = backup_dir / f"{table}.parquet"
                    df.to_parquet(table_file, compression="snappy")
                    backup_files.append(table_file)

                    logger.info(f"  Backed up {len(df)} incremental rows from {table}")

            # 计算备份大小
            original_size = sum(f.stat().st_size for f in backup_files)

            # 如果启用压缩
            compressed_file = None
            if self.compression:
                compressed_file = self.tdengine_backup_dir / f"{backup_id}.tar.gz"
                with gzip.open(compressed_file, "wb") as tar:
                    for file in backup_files:
                        tar.write(file, arcname=file.name)

                compressed_size = compressed_file.stat().st_size
                compression_ratio = (
                    original_size / compressed_size if compressed_size > 0 else 0
                )

                shutil.rmtree(backup_dir)
                backup_size = compressed_size
            else:
                backup_size = original_size
                compression_ratio = 1.0

            # 创建元数据
            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type="incremental",
                database="tdengine",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                tables_backed_up=tables,
                total_rows=total_rows,
                backup_size_bytes=backup_size,
                compression_ratio=compression_ratio,
                status="success",
            )

            self._save_metadata(metadata)

            logger.info(
                f"TDengine incremental backup completed: {backup_id}, "
                f"rows={total_rows}, size={backup_size/1024/1024:.2f}MB"
            )

            return metadata

        except Exception as e:
            logger.error(f"TDengine incremental backup failed: {e}")

            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type="incremental",
                database="tdengine",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                tables_backed_up=[],
                total_rows=0,
                backup_size_bytes=0,
                compression_ratio=0.0,
                status="failed",
                error_message=str(e),
            )

            self._save_metadata(metadata)
            return metadata

    def backup_postgresql_full(self) -> BackupMetadata:
        """
        PostgreSQL 全量备份（使用 pg_dump）

        Returns:
            BackupMetadata: 备份元数据
        """
        start_time = datetime.now()
        backup_id = f"postgresql_full_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(f"Starting PostgreSQL full backup: {backup_id}")

            # 获取数据库连接信息
            pg_conn = self.conn_manager.get_postgresql_connection()

            # 使用 pg_dump 进行备份
            backup_file = self.postgresql_backup_dir / f"{backup_id}.sql"

            # 构建 pg_dump 命令
            pg_dump_cmd = (
                f"pg_dump "
                f"--host {os.getenv('POSTGRESQL_HOST', 'localhost')} "
                f"--port {os.getenv('POSTGRESQL_PORT', '5432')} "
                f"--username {os.getenv('POSTGRESQL_USER', 'postgres')} "
                f"--format plain "
                f"--file {backup_file} "
                f"{os.getenv('POSTGRESQL_DATABASE', 'mystocks')}"
            )

            # 执行备份
            result = os.system(
                f"PGPASSWORD={os.getenv('POSTGRESQL_PASSWORD')} {pg_dump_cmd}"
            )

            if result != 0:
                raise Exception(f"pg_dump failed with exit code {result}")

            # 获取备份大小
            original_size = backup_file.stat().st_size

            # 如果启用压缩
            if self.compression:
                compressed_file = self.postgresql_backup_dir / f"{backup_id}.sql.gz"
                with open(backup_file, "rb") as f_in:
                    with gzip.open(compressed_file, "wb") as f_out:
                        f_out.writelines(f_in)

                compressed_size = compressed_file.stat().st_size
                compression_ratio = (
                    original_size / compressed_size if compressed_size > 0 else 0
                )

                # 删除未压缩的文件
                backup_file.unlink()
                backup_size = compressed_size
            else:
                backup_size = original_size
                compression_ratio = 1.0

            # 获取表数和行数
            tables = self._get_postgresql_tables()
            total_rows = self._count_postgresql_rows()

            # 创建元数据
            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type="full",
                database="postgresql",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                tables_backed_up=tables,
                total_rows=total_rows,
                backup_size_bytes=backup_size,
                compression_ratio=compression_ratio,
                status="success",
            )

            self._save_metadata(metadata)

            logger.info(
                f"PostgreSQL full backup completed: {backup_id}, "
                f"rows={total_rows}, size={backup_size/1024/1024:.2f}MB, "
                f"ratio={compression_ratio:.2f}x"
            )

            return metadata

        except Exception as e:
            logger.error(f"PostgreSQL full backup failed: {e}")

            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type="full",
                database="postgresql",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                tables_backed_up=[],
                total_rows=0,
                backup_size_bytes=0,
                compression_ratio=0.0,
                status="failed",
                error_message=str(e),
            )

            self._save_metadata(metadata)
            return metadata

    def cleanup_old_backups(self):
        """清理过期备份（基于保留天数）"""
        cutoff_date = datetime.now().timestamp() - (self.retention_days * 86400)

        for backup_dir in [self.tdengine_backup_dir, self.postgresql_backup_dir]:
            for backup_file in backup_dir.iterdir():
                if backup_file.is_file():
                    if backup_file.stat().st_mtime < cutoff_date:
                        logger.info(f"Deleting old backup: {backup_file}")
                        backup_file.unlink()

    # ==================== 私有方法 ====================

    def _get_tdengine_tables(self) -> List[str]:
        """获取所有 TDengine 表"""
        try:
            # 从配置中获取超表列表
            tables = [
                "tick_data",
                "minute_kline",
                "order_book_depth",
                "level2_snapshot",
                "index_intraday_quotes",
            ]
            return tables
        except Exception as e:
            logger.error(f"Failed to get TDengine tables: {e}")
            return []

    def _get_postgresql_tables(self) -> List[str]:
        """获取所有 PostgreSQL 表"""
        try:
            # 从数据库查询表列表
            conn = self.conn_manager.get_postgresql_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            )

            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()

            return tables
        except Exception as e:
            logger.error(f"Failed to get PostgreSQL tables: {e}")
            return []

    def _count_postgresql_rows(self) -> int:
        """统计 PostgreSQL 总行数"""
        try:
            conn = self.conn_manager.get_postgresql_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT SUM(n_live_tup)
                FROM pg_stat_user_tables
            """
            )

            result = cursor.fetchone()
            total_rows = result[0] if result and result[0] else 0
            cursor.close()

            return total_rows
        except Exception as e:
            logger.error(f"Failed to count PostgreSQL rows: {e}")
            return 0

    def _save_metadata(self, metadata: BackupMetadata):
        """保存备份元数据"""
        metadata_file = self.metadata_dir / f"{metadata.backup_id}.json"

        with open(metadata_file, "w") as f:
            json.dump(asdict(metadata), f, indent=2)

        logger.info(f"Metadata saved: {metadata_file}")

    def _load_metadata(self, backup_id: str) -> Optional[dict]:
        """加载备份元数据"""
        metadata_file = self.metadata_dir / f"{backup_id}.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, "r") as f:
            return json.load(f)

    def get_backup_list(self) -> List[BackupMetadata]:
        """获取所有备份列表"""
        backups = []

        for metadata_file in self.metadata_dir.glob("*.json"):
            with open(metadata_file, "r") as f:
                metadata_dict = json.load(f)
                backups.append(BackupMetadata(**metadata_dict))

        return sorted(backups, key=lambda x: x.start_time, reverse=True)

    def get_latest_backup(
        self, database: str, backup_type: str = "full"
    ) -> Optional[BackupMetadata]:
        """获取最新的备份"""
        backups = self.get_backup_list()

        for backup in backups:
            if (
                backup.database == database
                and backup.backup_type == backup_type
                and backup.status == "success"
            ):
                return backup

        return None
