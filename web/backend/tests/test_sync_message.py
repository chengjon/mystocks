"""
双库同步消息表测试
Test Suite for Sync Message Table and Database Manager

测试覆盖:
- SyncMessage模型
- SyncDatabaseManager CRUD操作
- 消息状态流转
- 重试机制
- 统计查询
"""

import pytest
from datetime import datetime, timedelta

from app.models.sync_message import (
    SyncMessage,
    MessageStatus,
    SyncDirection,
    OperationType,
)
from app.core.sync_db_manager import (
    SyncDatabaseManager,
    get_sync_db_manager,
    reset_sync_db_manager,
)


@pytest.fixture
def setup_teardown():
    """设置和清理"""
    manager = SyncDatabaseManager()
    manager.initialize_engine()

    # 清理旧表
    try:
        manager.drop_tables()
    except:
        pass

    # 创建新表
    manager.create_tables()

    yield manager

    # 清理
    try:
        manager.drop_tables()
    except:
        pass

    reset_sync_db_manager()


class TestSyncMessageModel:
    """测试SyncMessage模型"""

    def test_sync_message_creation(self):
        """测试消息对象创建"""
        message = SyncMessage(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="market_data",
            target_database="mystocks",
            source_table="minute_data",
            target_table="market_data_minute",
            record_identifier={"symbol": "600000", "timestamp": "2025-11-06T10:30:00"},
            payload={"symbol": "600000", "open": 10.50},
            priority=5,
            max_retries=3,
            status=MessageStatus.PENDING,  # 手动设置默认状态
            retry_count=0,  # 手动设置默认值
        )

        assert message.operation_type == OperationType.INSERT
        assert message.sync_direction == SyncDirection.TDENGINE_TO_POSTGRESQL
        assert message.status == MessageStatus.PENDING
        assert message.priority == 5
        assert message.max_retries == 3
        assert message.retry_count == 0

    def test_message_is_retryable(self):
        """测试消息可重试判断"""
        message = SyncMessage(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
            status=MessageStatus.FAILED,
            retry_count=1,
            max_retries=3,
        )

        assert message.is_retryable is True

        message.retry_count = 3
        assert message.is_retryable is False

    def test_message_should_move_to_dead_letter(self):
        """测试死信队列判断"""
        message = SyncMessage(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
            status=MessageStatus.FAILED,
            retry_count=3,
            max_retries=3,
        )

        assert message.should_move_to_dead_letter is True

    def test_message_to_dict(self):
        """测试消息转换为字典"""
        message = SyncMessage(
            operation_type=OperationType.UPDATE,
            sync_direction=SyncDirection.POSTGRESQL_TO_TDENGINE,
            source_database="mystocks",
            target_database="market_data",
            source_table="stocks",
            target_table="stock_info",
            record_identifier={"symbol": "600519"},
            payload={"symbol": "600519", "name": "贵州茅台"},
            priority=1,
            status=MessageStatus.PENDING,
        )

        data = message.to_dict()

        assert data["operation_type"] == "update"
        assert data["sync_direction"] == "postgresql_to_tdengine"
        assert data["status"] == "pending"
        assert data["priority"] == 1
        assert data["record_identifier"] == {"symbol": "600519"}


class TestSyncDatabaseManager:
    """测试SyncDatabaseManager"""

    def test_manager_initialization(self, setup_teardown):
        """测试管理器初始化"""
        manager = setup_teardown

        assert manager.engine is not None
        assert manager.SessionLocal is not None

    def test_create_single_message(self, setup_teardown):
        """测试创建单条消息"""
        manager = setup_teardown

        message = manager.create_message(
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
                "volume": 1000000,
            },
            priority=5,
        )

        assert message.id is not None
        assert message.status == MessageStatus.PENDING
        assert message.priority == 5

    def test_create_messages_batch(self, setup_teardown):
        """测试批量创建消息"""
        manager = setup_teardown

        messages = [
            {
                "operation_type": OperationType.INSERT,
                "sync_direction": SyncDirection.TDENGINE_TO_POSTGRESQL,
                "source_database": "market_data",
                "target_database": "mystocks",
                "source_table": "minute_data",
                "target_table": "market_data_minute",
                "record_identifier": {
                    "symbol": f"60000{i}",
                    "timestamp": "2025-11-06T10:30:00",
                },
                "payload": {"symbol": f"60000{i}", "open": 10.0 + i},
                "priority": 1,
            }
            for i in range(5)
        ]

        message_ids = manager.create_messages_batch(messages)

        assert len(message_ids) == 5
        assert all(msg_id is not None for msg_id in message_ids)

    def test_get_message_by_id(self, setup_teardown):
        """测试根据ID查询消息"""
        manager = setup_teardown

        # 创建消息
        message = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
        )

        # 查询消息
        retrieved = manager.get_message_by_id(message.id)

        assert retrieved is not None
        assert retrieved.id == message.id
        assert retrieved.operation_type == OperationType.INSERT

    def test_get_pending_messages(self, setup_teardown):
        """测试查询待处理消息"""
        manager = setup_teardown

        # 创建多条消息
        for i in range(5):
            manager.create_message(
                operation_type=OperationType.INSERT,
                sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
                source_database="test_db",
                target_database="test_db",
                source_table="test_table",
                target_table="test_table",
                record_identifier={"id": i},
                payload={"data": f"test_{i}"},
                priority=i + 1,
            )

        # 查询待处理消息
        pending = manager.get_pending_messages(limit=10)

        assert len(pending) == 5
        assert all(msg.status == MessageStatus.PENDING for msg in pending)
        # 验证按优先级降序排序
        assert pending[0].priority >= pending[-1].priority

    def test_update_message_status_to_in_progress(self, setup_teardown):
        """测试更新消息状态为处理中"""
        manager = setup_teardown

        # 创建消息
        message = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
        )

        # 更新状态
        success = manager.update_message_status(
            message_id=message.id,
            status=MessageStatus.IN_PROGRESS,
            processed_by="worker-1",
        )

        assert success is True

        # 验证状态
        updated = manager.get_message_by_id(message.id)
        assert updated.status == MessageStatus.IN_PROGRESS
        assert updated.started_at is not None
        assert updated.processed_by == "worker-1"

    def test_update_message_status_to_success(self, setup_teardown):
        """测试更新消息状态为成功"""
        manager = setup_teardown

        # 创建消息
        message = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
        )

        # 更新为处理中
        manager.update_message_status(message.id, MessageStatus.IN_PROGRESS)

        # 更新为成功
        success = manager.update_message_status(
            message_id=message.id,
            status=MessageStatus.SUCCESS,
            sync_latency_ms=50.0,
            processing_duration_ms=25.0,
            processed_by="worker-1",
        )

        assert success is True

        # 验证状态
        updated = manager.get_message_by_id(message.id)
        assert updated.status == MessageStatus.SUCCESS
        assert updated.completed_at is not None
        assert float(updated.sync_latency_ms) == 50.0
        assert float(updated.processing_duration_ms) == 25.0

    def test_update_message_status_to_failed_with_retry(self, setup_teardown):
        """测试更新消息状态为失败并重试"""
        manager = setup_teardown

        # 创建消息
        message = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
            max_retries=3,
        )

        # 第一次失败
        manager.update_message_status(
            message_id=message.id,
            status=MessageStatus.FAILED,
            error_message="Connection timeout",
            error_details={"code": "TIMEOUT", "reason": "Network error"},
        )

        # 验证状态
        updated = manager.get_message_by_id(message.id)
        assert updated.status == MessageStatus.RETRY
        assert updated.retry_count == 1
        assert updated.error_message == "Connection timeout"
        assert updated.next_retry_at is not None

    def test_update_message_to_dead_letter(self, setup_teardown):
        """测试消息进入死信队列"""
        manager = setup_teardown

        # 创建消息
        message = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
            max_retries=3,
        )

        # 模拟3次失败
        for _ in range(3):
            manager.update_message_status(
                message_id=message.id,
                status=MessageStatus.FAILED,
                error_message="Persistent error",
            )

        # 验证进入死信队列
        updated = manager.get_message_by_id(message.id)
        assert updated.status == MessageStatus.DEAD_LETTER
        assert updated.retry_count == 3

    def test_get_retryable_messages(self, setup_teardown):
        """测试查询可重试消息"""
        manager = setup_teardown

        # 创建可重试消息
        message1 = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test1"},
        )

        # 设置为失败状态
        manager.update_message_status(
            message_id=message1.id,
            status=MessageStatus.FAILED,
            error_message="Error",
        )

        # 验证消息进入RETRY状态
        updated = manager.get_message_by_id(message1.id)
        assert updated.status == MessageStatus.RETRY
        assert updated.retry_count == 1
        assert updated.next_retry_at is not None

        # 创建成功消息(不应该被查询到)
        message2 = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 2},
            payload={"data": "test2"},
        )
        manager.update_message_status(
            message_id=message2.id, status=MessageStatus.SUCCESS
        )

        # 手动将next_retry_at设置为过去，使其立即可重试
        session = manager.get_session()
        try:
            msg = (
                session.query(SyncMessage).filter(SyncMessage.id == message1.id).first()
            )
            msg.next_retry_at = datetime.utcnow() - timedelta(seconds=1)
            session.commit()
        finally:
            session.close()

        # 查询可重试消息
        retryable = manager.get_retryable_messages(limit=10)

        assert len(retryable) >= 1
        assert all(
            msg.status in [MessageStatus.RETRY, MessageStatus.FAILED]
            for msg in retryable
        )

    def test_get_dead_letter_messages(self, setup_teardown):
        """测试查询死信队列消息"""
        manager = setup_teardown

        # 创建消息并进入死信队列
        message = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
            max_retries=1,
        )

        # 失败2次进入死信队列
        manager.update_message_status(
            message.id, MessageStatus.FAILED, error_message="Error"
        )
        manager.update_message_status(
            message.id, MessageStatus.FAILED, error_message="Error"
        )

        # 查询死信消息
        dead_letters = manager.get_dead_letter_messages(limit=10)

        assert len(dead_letters) >= 1
        assert all(msg.status == MessageStatus.DEAD_LETTER for msg in dead_letters)

    def test_get_message_counts_by_status(self, setup_teardown):
        """测试按状态统计消息数量"""
        manager = setup_teardown

        # 创建不同状态的消息
        for i in range(3):
            manager.create_message(
                operation_type=OperationType.INSERT,
                sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
                source_database="test_db",
                target_database="test_db",
                source_table="test_table",
                target_table="test_table",
                record_identifier={"id": i},
                payload={"data": f"test_{i}"},
            )

        # 更新部分消息状态
        messages = manager.get_pending_messages(limit=10)
        if len(messages) >= 2:
            manager.update_message_status(messages[0].id, MessageStatus.SUCCESS)
            manager.update_message_status(
                messages[1].id, MessageStatus.FAILED, error_message="Error"
            )

        # 查询统计
        counts = manager.get_message_counts_by_status()

        assert "pending" in counts or "retry" in counts or "success" in counts
        assert sum(counts.values()) >= 3

    def test_get_sync_statistics(self, setup_teardown):
        """测试获取同步统计数据"""
        manager = setup_teardown

        # 创建消息
        for i in range(5):
            message = manager.create_message(
                operation_type=OperationType.INSERT,
                sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
                source_database="test_db",
                target_database="test_db",
                source_table="test_table",
                target_table="test_table",
                record_identifier={"id": i},
                payload={"data": f"test_{i}"},
            )

            if i < 3:
                manager.update_message_status(
                    message.id,
                    MessageStatus.SUCCESS,
                    sync_latency_ms=float(10 + i),
                    processing_duration_ms=float(5 + i),
                )

        # 查询统计
        stats = manager.get_sync_statistics(window_minutes=5)

        assert stats["total_messages"] >= 5
        assert stats["success_count"] >= 3
        assert stats["success_rate"] > 0

    def test_cleanup_old_success_messages(self, setup_teardown):
        """测试清理旧的成功消息"""
        manager = setup_teardown

        # 创建成功消息
        message = manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test_db",
            target_database="test_db",
            source_table="test_table",
            target_table="test_table",
            record_identifier={"id": 1},
            payload={"data": "test"},
        )

        manager.update_message_status(message.id, MessageStatus.SUCCESS)

        # 手动修改完成时间为8天前
        session = manager.get_session()
        try:
            msg = (
                session.query(SyncMessage).filter(SyncMessage.id == message.id).first()
            )
            msg.completed_at = datetime.utcnow() - timedelta(days=8)
            session.commit()
        finally:
            session.close()

        # 清理7天前的消息
        deleted_count = manager.cleanup_old_success_messages(days=7)

        assert deleted_count >= 1


class TestSyncDatabaseManagerSingleton:
    """测试单例模式"""

    def test_get_sync_db_manager_singleton(self):
        """测试单例"""
        manager1 = get_sync_db_manager()
        manager2 = get_sync_db_manager()

        assert manager1 is manager2

    def test_reset_sync_db_manager(self):
        """测试重置单例"""
        manager1 = get_sync_db_manager()
        reset_sync_db_manager()
        manager2 = get_sync_db_manager()

        assert manager1 is not manager2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
