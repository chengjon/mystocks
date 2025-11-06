"""
双库数据一致性 - 本地消息表模型
Local Message Table for Dual-Database Eventual Consistency

实现本地消息表模式,确保TDengine和PostgreSQL之间的数据最终一致性。

Architecture:
- SyncMessage: 主消息表,记录所有跨库同步操作
- MessageStatus: 消息状态枚举
- SyncDirection: 同步方向枚举

Features:
- 操作类型: INSERT, UPDATE, DELETE
- 状态跟踪: PENDING -> IN_PROGRESS -> SUCCESS/FAILED
- 重试机制: 最多3次重试,失败后进入死信队列
- 监控指标: 同步延迟、失败率、死信数量
"""

from datetime import datetime
from typing import Optional, Dict, Any
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    DECIMAL,
    Index,
    CheckConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MessageStatus(enum.Enum):
    """
    消息状态枚举

    状态流转:
    PENDING -> IN_PROGRESS -> SUCCESS
                           -> FAILED -> RETRY (最多3次)
                                    -> DEAD_LETTER (重试耗尽)
    """

    PENDING = "pending"  # 等待处理
    IN_PROGRESS = "in_progress"  # 处理中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    RETRY = "retry"  # 重试中
    DEAD_LETTER = "dead_letter"  # 死信队列 (超过最大重试次数)


class SyncDirection(enum.Enum):
    """同步方向枚举"""

    TDENGINE_TO_POSTGRESQL = "tdengine_to_postgresql"  # TDengine -> PostgreSQL
    POSTGRESQL_TO_TDENGINE = "postgresql_to_tdengine"  # PostgreSQL -> TDengine
    BIDIRECTIONAL = "bidirectional"  # 双向同步


class OperationType(enum.Enum):
    """操作类型枚举"""

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    BULK_INSERT = "bulk_insert"  # 批量插入


class SyncMessage(Base):
    """
    本地消息表 - 跨库同步消息

    用途:
    1. 记录所有需要跨库同步的操作
    2. 追踪消息处理状态和重试次数
    3. 提供消息持久化和恢复能力
    4. 支持监控和告警

    Example:
        # 创建同步消息
        message = SyncMessage(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="market_data",
            target_database="mystocks",
            source_table="minute_data",
            target_table="market_data_minute",
            record_identifier={"symbol": "600000", "timestamp": "2025-11-06T10:30:00"},
            payload={
                "symbol": "600000",
                "timestamp": "2025-11-06T10:30:00",
                "open": 10.50,
                "high": 10.80,
                "low": 10.45,
                "close": 10.75,
                "volume": 1000000
            },
            priority=1
        )
    """

    __tablename__ = "sync_message"

    # ==================== 主键 ====================
    id = Column(Integer, primary_key=True, autoincrement=True, comment="消息ID")

    # ==================== 操作信息 ====================
    operation_type = Column(
        SQLEnum(OperationType),
        nullable=False,
        index=True,
        comment="操作类型: insert/update/delete/bulk_insert",
    )

    sync_direction = Column(
        SQLEnum(SyncDirection),
        nullable=False,
        index=True,
        comment="同步方向: tdengine_to_postgresql/postgresql_to_tdengine/bidirectional",
    )

    # ==================== 数据库和表信息 ====================
    source_database = Column(String(100), nullable=False, comment="源数据库名称")
    target_database = Column(String(100), nullable=False, comment="目标数据库名称")
    source_table = Column(String(100), nullable=False, index=True, comment="源表名称")
    target_table = Column(String(100), nullable=False, index=True, comment="目标表名称")

    # ==================== 记录标识 ====================
    record_identifier = Column(
        JSONB,
        nullable=False,
        comment="记录唯一标识 (如: {symbol: '600000', timestamp: '2025-11-06T10:30:00'})",
    )

    # ==================== 数据负载 ====================
    payload = Column(JSONB, nullable=False, comment="完整数据负载,用于同步操作")

    # ==================== 状态管理 ====================
    status = Column(
        SQLEnum(MessageStatus),
        nullable=False,
        default=MessageStatus.PENDING,
        index=True,
        comment="消息状态",
    )

    priority = Column(
        Integer,
        nullable=False,
        default=1,
        index=True,
        comment="优先级 (1-10, 数字越大优先级越高)",
    )

    # ==================== 重试机制 ====================
    retry_count = Column(Integer, nullable=False, default=0, comment="已重试次数")

    max_retries = Column(Integer, nullable=False, default=3, comment="最大重试次数")

    next_retry_at = Column(
        DateTime, nullable=True, index=True, comment="下次重试时间 (指数退避策略)"
    )

    # ==================== 错误信息 ====================
    error_message = Column(Text, nullable=True, comment="错误消息")

    error_details = Column(
        JSONB, nullable=True, comment="错误详情 (堆栈跟踪、上下文等)"
    )

    # ==================== 时间戳 ====================
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="创建时间",
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    started_at = Column(DateTime, nullable=True, comment="开始处理时间")

    completed_at = Column(DateTime, nullable=True, index=True, comment="完成时间")

    # ==================== 监控和审计 ====================
    sync_latency_ms = Column(
        DECIMAL(10, 2),
        nullable=True,
        comment="同步延迟(毫秒): completed_at - created_at",
    )

    processing_duration_ms = Column(
        DECIMAL(10, 2),
        nullable=True,
        comment="处理耗时(毫秒): completed_at - started_at",
    )

    processed_by = Column(
        String(100), nullable=True, comment="处理者 (worker ID或进程ID)"
    )

    # ==================== 额外元数据 ====================
    extra_metadata = Column(
        JSONB, nullable=True, comment="额外元数据 (请求ID、用户ID、业务上下文等)"
    )

    # ==================== 表约束 ====================
    __table_args__ = (
        # 优先级约束
        CheckConstraint(
            "priority >= 1 AND priority <= 10", name="check_priority_range"
        ),
        # 重试次数约束
        CheckConstraint("retry_count >= 0", name="check_retry_count_non_negative"),
        CheckConstraint("max_retries >= 0", name="check_max_retries_non_negative"),
        CheckConstraint("retry_count <= max_retries", name="check_retry_count_le_max"),
        # 复合索引 - 用于查询待处理消息
        Index("idx_status_priority_created", "status", "priority", "created_at"),
        # 复合索引 - 用于查询重试消息
        Index("idx_status_retry_next_retry", "status", "retry_count", "next_retry_at"),
        # 复合索引 - 用于监控同步延迟
        Index("idx_created_completed", "created_at", "completed_at"),
        # 复合索引 - 用于表级统计
        Index("idx_source_target_status", "source_table", "target_table", "status"),
        # 注释
        {"comment": "双库同步消息表 - 支持TDengine和PostgreSQL之间的最终一致性"},
    )

    def __repr__(self):
        return (
            f"<SyncMessage(id={self.id}, "
            f"operation={self.operation_type.value}, "
            f"direction={self.sync_direction.value}, "
            f"status={self.status.value}, "
            f"retry={self.retry_count}/{self.max_retries})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "operation_type": self.operation_type.value,
            "sync_direction": self.sync_direction.value,
            "source_database": self.source_database,
            "target_database": self.target_database,
            "source_table": self.source_table,
            "target_table": self.target_table,
            "record_identifier": self.record_identifier,
            "payload": self.payload,
            "status": self.status.value,
            "priority": self.priority,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "next_retry_at": (
                self.next_retry_at.isoformat() if self.next_retry_at else None
            ),
            "error_message": self.error_message,
            "error_details": self.error_details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "sync_latency_ms": (
                float(self.sync_latency_ms) if self.sync_latency_ms else None
            ),
            "processing_duration_ms": (
                float(self.processing_duration_ms)
                if self.processing_duration_ms
                else None
            ),
            "processed_by": self.processed_by,
            "extra_metadata": self.extra_metadata,
        }

    @property
    def is_retryable(self) -> bool:
        """判断是否可以重试"""
        return (
            self.status in [MessageStatus.FAILED, MessageStatus.RETRY]
            and self.retry_count < self.max_retries
        )

    @property
    def should_move_to_dead_letter(self) -> bool:
        """判断是否应该移动到死信队列"""
        return (
            self.status == MessageStatus.FAILED and self.retry_count >= self.max_retries
        )


class SyncStatistics(Base):
    """
    同步统计表 - 按时间窗口汇总统计数据

    用途:
    1. 监控同步性能指标
    2. 告警阈值判断
    3. 运维Dashboard展示
    """

    __tablename__ = "sync_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ==================== 时间窗口 ====================
    window_start = Column(
        DateTime, nullable=False, index=True, comment="统计窗口开始时间"
    )
    window_end = Column(
        DateTime, nullable=False, index=True, comment="统计窗口结束时间"
    )
    window_size_minutes = Column(
        Integer, nullable=False, default=5, comment="窗口大小(分钟)"
    )

    # ==================== 表级维度 ====================
    source_table = Column(
        String(100), nullable=True, index=True, comment="源表名称 (NULL表示全局统计)"
    )
    target_table = Column(String(100), nullable=True, index=True, comment="目标表名称")

    # ==================== 消息计数 ====================
    total_messages = Column(Integer, nullable=False, default=0, comment="总消息数")
    success_count = Column(Integer, nullable=False, default=0, comment="成功数")
    failed_count = Column(Integer, nullable=False, default=0, comment="失败数")
    retry_count = Column(Integer, nullable=False, default=0, comment="重试数")
    dead_letter_count = Column(Integer, nullable=False, default=0, comment="死信数")

    # ==================== 性能指标 ====================
    avg_sync_latency_ms = Column(
        DECIMAL(10, 2), nullable=True, comment="平均同步延迟(毫秒)"
    )
    p50_sync_latency_ms = Column(
        DECIMAL(10, 2), nullable=True, comment="P50同步延迟(毫秒)"
    )
    p95_sync_latency_ms = Column(
        DECIMAL(10, 2), nullable=True, comment="P95同步延迟(毫秒)"
    )
    p99_sync_latency_ms = Column(
        DECIMAL(10, 2), nullable=True, comment="P99同步延迟(毫秒)"
    )
    max_sync_latency_ms = Column(
        DECIMAL(10, 2), nullable=True, comment="最大同步延迟(毫秒)"
    )

    avg_processing_duration_ms = Column(
        DECIMAL(10, 2), nullable=True, comment="平均处理耗时(毫秒)"
    )

    # ==================== 成功率 ====================
    success_rate = Column(DECIMAL(5, 2), nullable=True, comment="成功率 (%)")
    failure_rate = Column(DECIMAL(5, 2), nullable=True, comment="失败率 (%)")

    # ==================== 时间戳 ====================
    calculated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, comment="计算时间"
    )

    # ==================== 表约束 ====================
    __table_args__ = (
        Index(
            "idx_window_table",
            "window_start",
            "window_end",
            "source_table",
            "target_table",
        ),
        Index("idx_window_calculated", "window_start", "calculated_at"),
        {"comment": "双库同步统计表 - 按时间窗口汇总监控指标"},
    )

    def __repr__(self):
        return (
            f"<SyncStatistics("
            f"window={self.window_start.strftime('%Y-%m-%d %H:%M')}, "
            f"total={self.total_messages}, "
            f"success_rate={self.success_rate}%)>"
        )
