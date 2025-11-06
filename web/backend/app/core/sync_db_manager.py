"""
双库同步数据库管理器
Sync Database Manager for Dual-Database Consistency

负责:
1. 创建同步消息表和统计表
2. 提供消息CRUD操作
3. 提供消息查询和统计接口
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_, or_, func, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import structlog

from app.core.config import get_postgresql_connection_string
from app.models.sync_message import (
    Base,
    SyncMessage,
    SyncStatistics,
    MessageStatus,
    SyncDirection,
    OperationType,
)

logger = structlog.get_logger()


class SyncDatabaseManager:
    """
    同步数据库管理器

    Features:
    - 表初始化和验证
    - 消息CRUD操作
    - 批量查询和更新
    - 统计数据聚合
    """

    def __init__(self):
        """初始化同步数据库管理器"""
        self.connection_string = get_postgresql_connection_string()
        self.engine = None
        self.SessionLocal = None

    def initialize_engine(self):
        """初始化数据库引擎"""
        if self.engine is None:
            self.engine = create_engine(
                self.connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            logger.info("✅ Sync database engine initialized")

    def create_tables(self):
        """
        创建同步消息表和统计表

        Creates:
        - sync_message: 主消息表
        - sync_statistics: 统计表
        """
        try:
            self.initialize_engine()

            # 创建所有表
            Base.metadata.create_all(bind=self.engine, checkfirst=True)

            logger.info(
                "✅ Sync tables created successfully",
                tables=["sync_message", "sync_statistics"],
            )

        except SQLAlchemyError as e:
            logger.error("❌ Failed to create sync tables", error=str(e))
            raise

    def drop_tables(self):
        """删除所有同步表 (仅用于测试)"""
        try:
            self.initialize_engine()
            Base.metadata.drop_all(bind=self.engine)
            logger.warning(
                "⚠️ Sync tables dropped", tables=["sync_message", "sync_statistics"]
            )

        except SQLAlchemyError as e:
            logger.error("❌ Failed to drop sync tables", error=str(e))
            raise

    def get_session(self) -> Session:
        """获取数据库会话"""
        self.initialize_engine()
        return self.SessionLocal()

    # ==================== 消息创建 ====================

    def create_message(
        self,
        operation_type: OperationType,
        sync_direction: SyncDirection,
        source_database: str,
        target_database: str,
        source_table: str,
        target_table: str,
        record_identifier: Dict[str, Any],
        payload: Dict[str, Any],
        priority: int = 1,
        max_retries: int = 3,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> SyncMessage:
        """
        创建同步消息

        Args:
            operation_type: 操作类型
            sync_direction: 同步方向
            source_database: 源数据库
            target_database: 目标数据库
            source_table: 源表
            target_table: 目标表
            record_identifier: 记录标识
            payload: 数据负载
            priority: 优先级 (1-10)
            max_retries: 最大重试次数
            extra_metadata: 额外元数据

        Returns:
            创建的消息对象
        """
        session = self.get_session()

        try:
            message = SyncMessage(
                operation_type=operation_type,
                sync_direction=sync_direction,
                source_database=source_database,
                target_database=target_database,
                source_table=source_table,
                target_table=target_table,
                record_identifier=record_identifier,
                payload=payload,
                status=MessageStatus.PENDING,
                priority=priority,
                max_retries=max_retries,
                extra_metadata=extra_metadata,
            )

            session.add(message)
            session.commit()
            session.refresh(message)

            logger.info(
                "✅ Sync message created",
                message_id=message.id,
                operation=operation_type.value,
                direction=sync_direction.value,
            )

            return message

        except SQLAlchemyError as e:
            session.rollback()
            logger.error("❌ Failed to create sync message", error=str(e))
            raise

        finally:
            session.close()

    def create_messages_batch(self, messages: List[Dict[str, Any]]) -> List[int]:
        """
        批量创建同步消息

        Args:
            messages: 消息列表，每个元素包含create_message的参数

        Returns:
            创建的消息ID列表
        """
        session = self.get_session()

        try:
            message_objects = []

            for msg_data in messages:
                message = SyncMessage(
                    operation_type=msg_data["operation_type"],
                    sync_direction=msg_data["sync_direction"],
                    source_database=msg_data["source_database"],
                    target_database=msg_data["target_database"],
                    source_table=msg_data["source_table"],
                    target_table=msg_data["target_table"],
                    record_identifier=msg_data["record_identifier"],
                    payload=msg_data["payload"],
                    status=MessageStatus.PENDING,
                    priority=msg_data.get("priority", 1),
                    max_retries=msg_data.get("max_retries", 3),
                    extra_metadata=msg_data.get("extra_metadata"),
                )
                message_objects.append(message)

            session.add_all(message_objects)
            session.commit()

            message_ids = [msg.id for msg in message_objects]

            logger.info("✅ Batch messages created", count=len(message_ids))

            return message_ids

        except SQLAlchemyError as e:
            session.rollback()
            logger.error("❌ Failed to create batch messages", error=str(e))
            raise

        finally:
            session.close()

    # ==================== 消息查询 ====================

    def get_message_by_id(self, message_id: int) -> Optional[SyncMessage]:
        """根据ID查询消息"""
        session = self.get_session()

        try:
            message = (
                session.query(SyncMessage).filter(SyncMessage.id == message_id).first()
            )
            return message

        finally:
            session.close()

    def get_pending_messages(
        self, limit: int = 100, priority_threshold: int = 1
    ) -> List[SyncMessage]:
        """
        查询待处理消息 (按优先级和创建时间排序)

        Args:
            limit: 最大返回数量
            priority_threshold: 优先级阈值

        Returns:
            待处理消息列表
        """
        session = self.get_session()

        try:
            messages = (
                session.query(SyncMessage)
                .filter(
                    and_(
                        SyncMessage.status == MessageStatus.PENDING,
                        SyncMessage.priority >= priority_threshold,
                    )
                )
                .order_by(desc(SyncMessage.priority), SyncMessage.created_at)
                .limit(limit)
                .all()
            )

            return messages

        finally:
            session.close()

    def get_retryable_messages(self, limit: int = 50) -> List[SyncMessage]:
        """
        查询可重试消息

        Returns:
            可重试消息列表 (retry_count < max_retries 且 next_retry_at <= now)
        """
        session = self.get_session()

        try:
            now = datetime.utcnow()

            messages = (
                session.query(SyncMessage)
                .filter(
                    and_(
                        or_(
                            SyncMessage.status == MessageStatus.FAILED,
                            SyncMessage.status == MessageStatus.RETRY,
                        ),
                        SyncMessage.retry_count < SyncMessage.max_retries,
                        or_(
                            SyncMessage.next_retry_at.is_(None),
                            SyncMessage.next_retry_at <= now,
                        ),
                    )
                )
                .order_by(desc(SyncMessage.priority), SyncMessage.next_retry_at)
                .limit(limit)
                .all()
            )

            return messages

        finally:
            session.close()

    def get_dead_letter_messages(
        self, limit: int = 100, offset: int = 0
    ) -> List[SyncMessage]:
        """查询死信队列消息"""
        session = self.get_session()

        try:
            messages = (
                session.query(SyncMessage)
                .filter(SyncMessage.status == MessageStatus.DEAD_LETTER)
                .order_by(desc(SyncMessage.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            return messages

        finally:
            session.close()

    # ==================== 消息更新 ====================

    def update_message_status(
        self,
        message_id: int,
        status: MessageStatus,
        error_message: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        sync_latency_ms: Optional[float] = None,
        processing_duration_ms: Optional[float] = None,
        processed_by: Optional[str] = None,
    ) -> bool:
        """
        更新消息状态

        Args:
            message_id: 消息ID
            status: 新状态
            error_message: 错误消息 (状态为FAILED时)
            error_details: 错误详情
            sync_latency_ms: 同步延迟
            processing_duration_ms: 处理耗时
            processed_by: 处理者

        Returns:
            是否更新成功
        """
        session = self.get_session()

        try:
            message = (
                session.query(SyncMessage).filter(SyncMessage.id == message_id).first()
            )

            if not message:
                logger.warning("⚠️ Message not found", message_id=message_id)
                return False

            # 更新状态
            message.status = status
            message.updated_at = datetime.utcnow()

            # 根据状态更新时间戳
            if status == MessageStatus.IN_PROGRESS:
                message.started_at = datetime.utcnow()

            elif status == MessageStatus.SUCCESS:
                message.completed_at = datetime.utcnow()
                if sync_latency_ms:
                    message.sync_latency_ms = sync_latency_ms
                if processing_duration_ms:
                    message.processing_duration_ms = processing_duration_ms

            elif status == MessageStatus.FAILED:
                message.error_message = error_message
                message.error_details = error_details

                # 增加重试次数
                message.retry_count += 1

                # 判断是否进入死信队列
                if message.should_move_to_dead_letter:
                    message.status = MessageStatus.DEAD_LETTER
                else:
                    # 计算下次重试时间 (指数退避)
                    retry_delay = 2**message.retry_count  # 2, 4, 8 秒
                    message.next_retry_at = datetime.utcnow() + timedelta(
                        seconds=retry_delay
                    )
                    message.status = MessageStatus.RETRY

            if processed_by:
                message.processed_by = processed_by

            session.commit()

            logger.info(
                "✅ Message status updated",
                message_id=message_id,
                status=status.value,
                retry_count=message.retry_count,
            )

            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error("❌ Failed to update message status", error=str(e))
            return False

        finally:
            session.close()

    # ==================== 统计查询 ====================

    def get_message_counts_by_status(self) -> Dict[str, int]:
        """查询各状态消息数量"""
        session = self.get_session()

        try:
            counts = (
                session.query(SyncMessage.status, func.count(SyncMessage.id))
                .group_by(SyncMessage.status)
                .all()
            )

            return {status.value: count for status, count in counts}

        finally:
            session.close()

    def get_sync_statistics(
        self, window_minutes: int = 5, table_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取同步统计数据

        Args:
            window_minutes: 统计窗口(分钟)
            table_name: 表名过滤

        Returns:
            统计数据字典
        """
        session = self.get_session()

        try:
            window_start = datetime.utcnow() - timedelta(minutes=window_minutes)

            query = session.query(
                func.count(SyncMessage.id).label("total_messages"),
                func.count(
                    func.nullif(SyncMessage.status == MessageStatus.SUCCESS, False)
                ).label("success_count"),
                func.count(
                    func.nullif(SyncMessage.status == MessageStatus.FAILED, False)
                ).label("failed_count"),
                func.count(
                    func.nullif(SyncMessage.status == MessageStatus.DEAD_LETTER, False)
                ).label("dead_letter_count"),
                func.avg(SyncMessage.sync_latency_ms).label("avg_sync_latency_ms"),
                func.max(SyncMessage.sync_latency_ms).label("max_sync_latency_ms"),
                func.avg(SyncMessage.processing_duration_ms).label(
                    "avg_processing_duration_ms"
                ),
            ).filter(SyncMessage.created_at >= window_start)

            if table_name:
                query = query.filter(SyncMessage.source_table == table_name)

            result = query.first()

            total = result.total_messages or 0
            success = result.success_count or 0

            return {
                "window_minutes": window_minutes,
                "window_start": window_start.isoformat(),
                "total_messages": total,
                "success_count": success,
                "failed_count": result.failed_count or 0,
                "dead_letter_count": result.dead_letter_count or 0,
                "success_rate": (success / total * 100) if total > 0 else 0,
                "avg_sync_latency_ms": float(result.avg_sync_latency_ms or 0),
                "max_sync_latency_ms": float(result.max_sync_latency_ms or 0),
                "avg_processing_duration_ms": float(
                    result.avg_processing_duration_ms or 0
                ),
            }

        finally:
            session.close()

    # ==================== 清理操作 ====================

    def cleanup_old_success_messages(self, days: int = 7) -> int:
        """
        清理旧的成功消息

        Args:
            days: 保留天数

        Returns:
            删除的消息数量
        """
        session = self.get_session()

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            deleted_count = (
                session.query(SyncMessage)
                .filter(
                    and_(
                        SyncMessage.status == MessageStatus.SUCCESS,
                        SyncMessage.completed_at < cutoff_date,
                    )
                )
                .delete(synchronize_session=False)
            )

            session.commit()

            logger.info(
                "✅ Old success messages cleaned",
                deleted_count=deleted_count,
                days=days,
            )

            return deleted_count

        except SQLAlchemyError as e:
            session.rollback()
            logger.error("❌ Failed to cleanup old messages", error=str(e))
            return 0

        finally:
            session.close()


# ==================== 全局实例 ====================

_sync_db_manager: Optional[SyncDatabaseManager] = None


def get_sync_db_manager() -> SyncDatabaseManager:
    """
    获取同步数据库管理器单例

    Returns:
        SyncDatabaseManager实例
    """
    global _sync_db_manager

    if _sync_db_manager is None:
        _sync_db_manager = SyncDatabaseManager()

    return _sync_db_manager


def reset_sync_db_manager() -> None:
    """重置同步数据库管理器 (用于测试)"""
    global _sync_db_manager
    if _sync_db_manager:
        _sync_db_manager = None
