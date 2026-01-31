"""
数据库迁移服务

管理数据库schema变更、版本控制和迁移历史
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from contextlib import contextmanager

from .connection_service import ConnectionService


logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """迁移状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationRecord:
    def __init__(self):
        self.version: str = ""
        self.name: str = ""
        self.description: str = ""
        self.applied_at: Optional[datetime] = None
        self.status: MigrationStatus = MigrationStatus.PENDING
        self.sql_content: str = ""
        self.duration_seconds: float = 0.0
        self.rows_affected: int = 0
        self.error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "rows_affected": self.rows_affected,
            "error_message": self.error_message,
        }


class MigrationService:
    def __init__(self, connection_service: ConnectionService):
        self.connection_service = connection_service
        self.migration_history: List[MigrationRecord] = []

        logger.info("MigrationService initialized")

    def get_pending_migrations(self) -> List[MigrationRecord]:
        """获取待执行的迁移"""
        try:
            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT version, name, description, sql_content
                    FROM schema_migrations
                    WHERE status = 'pending'
                    ORDER BY applied_at
                    """
                )

                migrations = []
                for row in cursor.fetchall():
                    record = MigrationRecord()
                    record.version = row[0]
                    record.name = row[1]
                    record.description = row[2]
                    record.sql_content = row[3]
                    record.status = MigrationStatus.PENDING
                    migrations.append(record)

                logger.info(f"找到{len(migrations)}个待执行迁移")
                return migrations
        except Exception as e:
            logger.error(f"获取待执行迁移失败: {e}")
            raise

    def apply_migration(self, migration: MigrationRecord) -> MigrationRecord:
        """应用数据库迁移"""
        try:
            migration.status = MigrationStatus.RUNNING
            migration.applied_at = datetime.now()

            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                start_time = datetime.now()

                cursor.execute(migration.sql_content)
                migration.rows_affected = cursor.rowcount
                conn.commit()

                end_time = datetime.now()
                migration.duration_seconds = (end_time - start_time).total_seconds()
                migration.status = MigrationStatus.SUCCESS

                logger.info(f"迁移成功: {migration.name} (版本 {migration.version})")

                self.migration_history.append(migration)
                self._save_migration_record(migration)

                return migration
        except Exception as e:
            migration.status = MigrationStatus.FAILED
            migration.error_message = str(e)

            logger.error(f"迁移失败: {migration.name} - {e}")

            self.migration_history.append(migration)
            self._save_migration_record(migration)

            raise

    def rollback_migration(self, migration: MigrationRecord) -> bool:
        """回滚迁移"""
        try:
            if migration.status != MigrationStatus.SUCCESS:
                logger.warning(f"迁移{migration.name}未成功执行，无法回滚")
                return False

            logger.info(f"尝试回滚迁移: {migration.name} (版本 {migration.version})")

            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                if migration.rows_affected > 0:
                    cursor.execute("ROLLBACK")
                    logger.info(f"已回滚{migration.rows_affected}行数据")

                migration.status = MigrationStatus.ROLLED_BACK

                self.migration_history.append(migration)
                self._save_migration_record(migration)

                logger.info(f"回滚成功: {migration.name}")
                return True
        except Exception as e:
            logger.error(f"回滚失败: {migration.name} - {e}")
            return False

    def _save_migration_record(self, migration: MigrationRecord):
        """保存迁移记录"""
        try:
            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO migration_history
                    (version, name, description, status, applied_at, duration_seconds, rows_affected, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        migration.version,
                        migration.name,
                        migration.description,
                        migration.status.value,
                        migration.applied_at,
                        migration.duration_seconds,
                        migration.rows_affected,
                        migration.error_message,
                    ),
                )

                conn.commit()
                logger.debug(f"迁移记录已保存: {migration.version} - {migration.name}")
        except Exception as e:
            logger.error(f"保存迁移记录失败: {e}")

    def get_migration_history(self, limit: int = 50) -> List[Dict]:
        """获取迁移历史"""
        try:
            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT version, name, description, status, applied_at, duration_seconds, rows_affected
                    FROM migration_history
                    ORDER BY applied_at DESC
                    LIMIT %s
                """,
                    (limit,),
                )

                history = []
                for row in cursor.fetchall():
                    history.append(
                        {
                            "version": row[0],
                            "name": row[1],
                            "description": row[2],
                            "status": row[3],
                            "applied_at": row[4],
                            "duration_seconds": row[5],
                            "rows_affected": row[6],
                        }
                    )

                return history
        except Exception as e:
            logger.error(f"获取迁移历史失败: {e}")
            raise

    def check_migration_status(self, version: str) -> Dict:
        """检查迁移状态"""
        try:
            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT status, applied_at
                    FROM migration_history
                    WHERE version = %s
                    ORDER BY applied_at DESC
                    LIMIT 1
                """,
                    (version,),
                )

                result = cursor.fetchone()

                if not result:
                    return {"version": version, "status": "not_applied", "last_applied_at": None}

                return {"version": version, "status": result[0], "last_applied_at": result[1]}
        except Exception as e:
            logger.error(f"检查迁移状态失败: {e}")
            raise

    @contextmanager
    def safe_migration_context(self):
        """安全的迁移上下文管理器"""
        try:
            with self.connection_service.get_connection() as conn:
                conn.autocommit = False
                yield conn
                conn.commit()
        except Exception as e:
            logger.error(f"迁移上下文出错: {e}")
            conn.rollback()
            raise
