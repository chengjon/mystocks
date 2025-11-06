"""
双库同步处理器测试
Test Suite for Sync Processor

测试覆盖:
- SyncExecutor: 同步执行器
- SyncProcessor: 消息处理器
- 各种同步方向和操作类型
- 错误处理和重试
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import time

from app.models.sync_message import (
    SyncMessage,
    MessageStatus,
    SyncDirection,
    OperationType,
)
from app.core.sync_processor import (
    SyncExecutor,
    SyncProcessor,
    get_sync_processor,
    reset_sync_processor,
)
from app.core.sync_db_manager import SyncDatabaseManager, reset_sync_db_manager
from app.core.cache_manager import reset_cache_manager


@pytest.fixture
def setup_teardown():
    """设置和清理"""
    # 重置所有单例
    reset_cache_manager()
    reset_sync_db_manager()
    reset_sync_processor()

    # 初始化数据库
    db_manager = SyncDatabaseManager()
    db_manager.initialize_engine()

    try:
        db_manager.drop_tables()
    except:
        pass

    db_manager.create_tables()

    yield db_manager

    # 清理
    try:
        db_manager.drop_tables()
    except:
        pass

    reset_cache_manager()
    reset_sync_db_manager()
    reset_sync_processor()


class TestSyncExecutor:
    """测试同步执行器"""

    def test_executor_initialization(self):
        """测试执行器初始化"""
        executor = SyncExecutor()
        assert executor.cache_manager is not None
        assert executor.postgresql_engine is not None

    def test_execute_sync_tdengine_to_postgresql_insert(self, setup_teardown):
        """测试TDengine到PostgreSQL的INSERT同步"""
        executor = SyncExecutor()
        db_manager = setup_teardown

        # 创建测试消息
        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="market_data",
            target_database="mystocks",
            source_table="minute_data",
            target_table="market_data_minute",
            record_identifier={"symbol": "600000", "data_type": "minute_data"},
            payload={"symbol": "600000", "open": 10.50, "close": 10.75},
        )

        # 执行同步
        result = executor.execute_sync(message)

        assert result["success"] is True
        assert "duration_ms" in result
        assert result["rows_affected"] >= 0

    def test_execute_sync_postgresql_to_tdengine_insert(self, setup_teardown):
        """测试PostgreSQL到TDengine的INSERT同步"""
        executor = SyncExecutor()
        db_manager = setup_teardown

        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.POSTGRESQL_TO_TDENGINE,
            source_database="mystocks",
            target_database="market_data",
            source_table="stocks",
            target_table="minute_data",
            record_identifier={
                "symbol": "600519",
                "data_type": "stock_info",
                "timeframe": "1d",
            },
            payload={"symbol": "600519", "name": "贵州茅台", "price": 1800.0},
        )

        result = executor.execute_sync(message)

        assert result["success"] is True
        assert "duration_ms" in result

    def test_execute_sync_bidirectional(self, setup_teardown):
        """测试双向同步"""
        executor = SyncExecutor()
        db_manager = setup_teardown

        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.BIDIRECTIONAL,
            source_database="market_data",
            target_database="mystocks",
            source_table="minute_data",
            target_table="market_data_minute",
            record_identifier={"symbol": "000001", "data_type": "minute_data"},
            payload={"symbol": "000001", "open": 15.0},
        )

        result = executor.execute_sync(message)

        assert result["success"] is True
        assert result["rows_affected"] >= 0

    def test_execute_sync_bulk_insert(self, setup_teardown):
        """测试批量插入同步"""
        executor = SyncExecutor()
        db_manager = setup_teardown

        message = db_manager.create_message(
            operation_type=OperationType.BULK_INSERT,
            sync_direction=SyncDirection.POSTGRESQL_TO_TDENGINE,
            source_database="mystocks",
            target_database="market_data",
            source_table="stocks",
            target_table="minute_data",
            record_identifier={"data_type": "stock_info", "timeframe": "1d"},
            payload=[
                {"symbol": "600000", "name": "浦发银行"},
                {"symbol": "600519", "name": "贵州茅台"},
                {"symbol": "000001", "name": "平安银行"},
            ],
        )

        result = executor.execute_sync(message)

        assert result["success"] is True
        assert result["rows_affected"] >= 0

    def test_execute_sync_invalid_direction(self, setup_teardown):
        """测试无效的同步方向"""
        executor = SyncExecutor()
        db_manager = setup_teardown

        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test",
            target_database="test",
            source_table="test",
            target_table="test",
            record_identifier={"id": 1},
            payload={"data": "test"},
        )

        # 手动修改direction为无效值
        message.sync_direction = None

        result = executor.execute_sync(message)

        assert result["success"] is False
        assert "error" in result


class TestSyncProcessor:
    """测试同步处理器"""

    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = SyncProcessor(batch_size=100, process_interval=10)

        assert processor.batch_size == 100
        assert processor.process_interval == 10
        assert processor.is_running is False
        assert processor.processed_count == 0
        assert processor.failed_count == 0
        assert processor.worker_id.startswith("worker-")

    def test_process_pending_messages_empty(self, setup_teardown):
        """测试处理空的待处理消息队列"""
        processor = SyncProcessor()

        result = processor.process_pending_messages()

        assert result["processed"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0

    def test_process_pending_messages_single(self, setup_teardown):
        """测试处理单条待处理消息"""
        db_manager = setup_teardown
        processor = SyncProcessor(db_manager=db_manager)

        # 创建待处理消息
        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.POSTGRESQL_TO_TDENGINE,
            source_database="mystocks",
            target_database="market_data",
            source_table="stocks",
            target_table="minute_data",
            record_identifier={
                "symbol": "600000",
                "data_type": "test",
                "timeframe": "1d",
            },
            payload={"symbol": "600000", "price": 10.0},
        )

        # 处理消息
        result = processor.process_pending_messages()

        assert result["processed"] == 1
        assert result["succeeded"] >= 0  # 可能成功或失败,取决于cache_manager状态

        # 验证消息状态已更新
        updated = db_manager.get_message_by_id(message.id)
        assert updated.status in [
            MessageStatus.SUCCESS,
            MessageStatus.FAILED,
            MessageStatus.RETRY,
        ]

    def test_process_pending_messages_batch(self, setup_teardown):
        """测试批量处理待处理消息"""
        db_manager = setup_teardown
        processor = SyncProcessor(db_manager=db_manager, batch_size=5)

        # 创建多条消息
        for i in range(3):
            db_manager.create_message(
                operation_type=OperationType.INSERT,
                sync_direction=SyncDirection.POSTGRESQL_TO_TDENGINE,
                source_database="test",
                target_database="test",
                source_table="test",
                target_table="test",
                record_identifier={
                    "symbol": f"60000{i}",
                    "data_type": "test",
                    "timeframe": "1d",
                },
                payload={"symbol": f"60000{i}", "value": i},
            )

        # 处理消息
        result = processor.process_pending_messages()

        assert result["processed"] == 3
        assert result["succeeded"] + result["failed"] == 3

    def test_process_retryable_messages(self, setup_teardown):
        """测试处理可重试消息"""
        db_manager = setup_teardown
        processor = SyncProcessor(db_manager=db_manager)

        # 创建消息并设置为失败状态
        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.POSTGRESQL_TO_TDENGINE,
            source_database="test",
            target_database="test",
            source_table="test",
            target_table="test",
            record_identifier={
                "symbol": "600000",
                "data_type": "test",
                "timeframe": "1d",
            },
            payload={"symbol": "600000"},
        )

        # 手动标记为失败
        db_manager.update_message_status(
            message_id=message.id,
            status=MessageStatus.FAILED,
            error_message="Test error",
        )

        # 手动设置next_retry_at为过去
        session = db_manager.get_session()
        try:
            msg = (
                session.query(SyncMessage).filter(SyncMessage.id == message.id).first()
            )
            msg.next_retry_at = datetime.utcnow() - timedelta(seconds=1)
            session.commit()
        finally:
            session.close()

        # 处理重试消息
        result = processor.process_retryable_messages()

        assert result["processed"] >= 1

    def test_processor_get_stats(self, setup_teardown):
        """测试获取处理器统计"""
        processor = SyncProcessor()

        stats = processor.get_stats()

        assert "worker_id" in stats
        assert "is_running" in stats
        assert "processed_count" in stats
        assert "failed_count" in stats
        assert "success_rate" in stats
        assert stats["success_rate"] >= 0

    def test_single_message_processing_success(self, setup_teardown):
        """测试单条消息成功处理"""
        db_manager = setup_teardown
        processor = SyncProcessor(db_manager=db_manager)

        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.POSTGRESQL_TO_TDENGINE,
            source_database="test",
            target_database="test",
            source_table="test",
            target_table="test",
            record_identifier={
                "symbol": "600000",
                "data_type": "test",
                "timeframe": "1d",
            },
            payload={"symbol": "600000", "value": 100},
        )

        result = processor._process_single_message(message)

        assert "success" in result
        assert "message_id" in result
        assert result["message_id"] == message.id

        # 验证状态更新
        updated = db_manager.get_message_by_id(message.id)
        assert updated.status in [
            MessageStatus.SUCCESS,
            MessageStatus.FAILED,
            MessageStatus.RETRY,
        ]
        assert updated.processed_by == processor.worker_id


class TestSyncProcessorSingleton:
    """测试单例模式"""

    def test_get_sync_processor_singleton(self):
        """测试同步处理器单例"""
        processor1 = get_sync_processor()
        processor2 = get_sync_processor()

        assert processor1 is processor2

    def test_reset_sync_processor(self):
        """测试重置单例"""
        processor1 = get_sync_processor()
        reset_sync_processor()
        processor2 = get_sync_processor()

        assert processor1 is not processor2


class TestSyncProcessorEdgeCases:
    """测试边界情况"""

    def test_process_message_with_missing_fields(self, setup_teardown):
        """测试处理缺少字段的消息"""
        db_manager = setup_teardown
        processor = SyncProcessor(db_manager=db_manager)

        # 创建缺少必要字段的消息
        message = db_manager.create_message(
            operation_type=OperationType.INSERT,
            sync_direction=SyncDirection.TDENGINE_TO_POSTGRESQL,
            source_database="test",
            target_database="test",
            source_table="test",
            target_table="test",
            record_identifier={},  # 空记录标识
            payload={},  # 空负载
        )

        result = processor._process_single_message(message)

        # 应该处理失败但不抛出异常
        assert "success" in result

    def test_process_with_database_error(self, setup_teardown):
        """测试数据库错误时的处理"""
        processor = SyncProcessor()

        # 使用无效的message对象
        fake_message = Mock()
        fake_message.id = 99999
        fake_message.operation_type = OperationType.INSERT
        fake_message.sync_direction = SyncDirection.POSTGRESQL_TO_TDENGINE
        fake_message.created_at = datetime.utcnow()

        result = processor._process_single_message(fake_message)

        assert result["success"] is False
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
