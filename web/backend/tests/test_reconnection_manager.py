"""
客户端重连机制单元测试

Test Reconnection Manager - Auto-reconnect with message buffering

Task 4.4: 客户端重连测试

Author: Claude Code
Date: 2025-11-06
"""

from app.core.reconnection_manager import (
    ReconnectionManager,
    ReconnectionState,
    MessageBuffer,
    OfflineMessage,
    get_reconnection_manager,
    reset_reconnection_manager,
)


class TestOfflineMessage:
    """测试离线消息"""

    def test_offline_message_creation(self):
        """测试离线消息创建"""
        msg = OfflineMessage("update", {"data": "test"}, "room_001")

        assert msg.event == "update"
        assert msg.data == {"data": "test"}
        assert msg.room == "room_001"
        assert msg.id is not None
        assert msg.retry_count == 0
        assert msg.created_at is not None

    def test_offline_message_to_dict(self):
        """测试离线消息转换为字典"""
        msg = OfflineMessage("update", {"value": 100}, "room_001")
        data = msg.to_dict()

        assert data["id"] == msg.id
        assert data["event"] == "update"
        assert data["data"] == {"value": 100}
        assert data["room"] == "room_001"
        assert data["retry_count"] == 0
        assert "created_at" in data


class TestMessageBuffer:
    """测试消息缓冲区"""

    def test_buffer_creation(self):
        """测试缓冲区创建"""
        buffer = MessageBuffer(max_size=50)

        assert buffer.max_size == 50
        assert len(buffer.messages) == 0
        assert len(buffer.sent_message_ids) == 0

    def test_add_message(self):
        """测试添加消息"""
        buffer = MessageBuffer()
        buffer.add_message("update", {"data": "test"}, "room_001")

        assert len(buffer.messages) == 1
        assert buffer.messages[0].event == "update"

    def test_add_multiple_messages(self):
        """测试添加多个消息"""
        buffer = MessageBuffer()
        for i in range(5):
            buffer.add_message(f"event_{i}", {"index": i}, f"room_{i}")

        assert len(buffer.messages) == 5

    def test_buffer_max_size_overflow(self):
        """测试缓冲区溢出处理"""
        buffer = MessageBuffer(max_size=3)
        for i in range(5):
            buffer.add_message(f"event_{i}", {"index": i})

        assert len(buffer.messages) == 3
        # 最早的两个消息应该被移除
        assert buffer.messages[0].data["index"] == 2

    def test_get_unsent_messages(self):
        """测试获取未发送消息"""
        buffer = MessageBuffer()
        msg1 = buffer.add_message("event_1", {"data": 1})
        msg2 = buffer.add_message("event_2", {"data": 2})
        msg3 = buffer.add_message("event_3", {"data": 3})

        unsent = buffer.get_unsent_messages()
        assert len(unsent) == 3

    def test_mark_sent(self):
        """测试标记消息已发送"""
        buffer = MessageBuffer()
        buffer.add_message("event_1", {"data": 1})
        buffer.add_message("event_2", {"data": 2})

        msg_id = buffer.messages[0].id
        buffer.mark_sent(msg_id)

        unsent = buffer.get_unsent_messages()
        assert len(unsent) == 1
        assert unsent[0].id == buffer.messages[1].id

    def test_mark_all_sent(self):
        """测试标记所有消息已发送"""
        buffer = MessageBuffer()
        buffer.add_message("event_1", {"data": 1})
        buffer.add_message("event_2", {"data": 2})
        buffer.add_message("event_3", {"data": 3})

        buffer.mark_all_sent()

        unsent = buffer.get_unsent_messages()
        assert len(unsent) == 0

    def test_clear_buffer(self):
        """测试清空缓冲区"""
        buffer = MessageBuffer()
        buffer.add_message("event_1", {"data": 1})
        buffer.add_message("event_2", {"data": 2})

        buffer.clear()

        assert len(buffer.messages) == 0
        assert len(buffer.sent_message_ids) == 0

    def test_buffer_stats(self):
        """测试缓冲区统计"""
        buffer = MessageBuffer(max_size=10)
        buffer.add_message("event_1", {"data": 1})
        buffer.add_message("event_2", {"data": 2})
        buffer.mark_sent(buffer.messages[0].id)

        stats = buffer.get_stats()

        assert stats["total_messages"] == 2
        assert stats["unsent_messages"] == 1
        assert stats["sent_messages"] == 1
        assert stats["max_size"] == 10
        assert stats["buffer_usage_percent"] == 20.0


class TestReconnectionManager:
    """测试重连管理器"""

    def setup_method(self):
        """测试前初始化"""
        reset_reconnection_manager()
        self.manager = ReconnectionManager()

    def test_register_connection(self):
        """测试注册连接"""
        self.manager.register_connection("sid_001", user_id="user_001")

        assert "sid_001" in self.manager.reconnection_states
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.CONNECTED
        assert self.manager.reconnection_attempts["sid_001"] == 0

    def test_mark_disconnected(self):
        """测试标记断开连接"""
        self.manager.register_connection("sid_001")
        self.manager.mark_disconnected("sid_001")

        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.DISCONNECTED
        assert self.manager.reconnection_attempts["sid_001"] == 0

    def test_buffer_message(self):
        """测试缓冲消息"""
        self.manager.register_connection("sid_001")
        self.manager.buffer_message("sid_001", "update", {"data": "test"}, "room_001")

        messages = self.manager.get_buffered_messages("sid_001")
        assert len(messages) == 1
        assert messages[0].event == "update"

    def test_should_attempt_reconnect_true(self):
        """测试应该尝试重连"""
        self.manager.register_connection("sid_001")
        self.manager.mark_disconnected("sid_001")

        assert self.manager.should_attempt_reconnect("sid_001")

    def test_should_attempt_reconnect_false_when_connected(self):
        """测试已连接时不重连"""
        self.manager.register_connection("sid_001")

        assert not self.manager.should_attempt_reconnect("sid_001")

    def test_should_attempt_reconnect_false_when_max_retries(self):
        """测试超过最大重试次数不重连"""
        self.manager.register_connection("sid_001")
        self.manager.mark_disconnected("sid_001")

        # 模拟达到最大重试次数
        for _ in range(self.manager.max_retries):
            self.manager.record_reconnect_attempt("sid_001")

        assert not self.manager.should_attempt_reconnect("sid_001")
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.RECONNECT_FAILED

    def test_get_next_reconnect_interval_exponential_backoff(self):
        """测试指数退避计算"""
        self.manager.register_connection("sid_001")
        self.manager.mark_disconnected("sid_001")

        # 第一次尝试：base_interval * 2^0 = 3
        interval_0 = self.manager.get_next_reconnect_interval("sid_001")
        assert interval_0 == 3.0

        # 第一次重试：base_interval * 2^1 = 6
        self.manager.record_reconnect_attempt("sid_001")
        interval_1 = self.manager.get_next_reconnect_interval("sid_001")
        assert interval_1 == 6.0

        # 第二次重试：base_interval * 2^2 = 12
        self.manager.record_reconnect_attempt("sid_001")
        interval_2 = self.manager.get_next_reconnect_interval("sid_001")
        assert interval_2 == 12.0

    def test_get_next_reconnect_interval_max_cap(self):
        """测试重连间隔上限"""
        manager = ReconnectionManager(base_interval=3.0, max_interval=15.0)
        manager.register_connection("sid_001")
        manager.mark_disconnected("sid_001")

        # 多次重试超过最大间隔
        for _ in range(10):
            manager.record_reconnect_attempt("sid_001")

        interval = manager.get_next_reconnect_interval("sid_001")
        assert interval <= 15.0

    def test_record_reconnect_attempt(self):
        """测试记录重连尝试"""
        self.manager.register_connection("sid_001")
        self.manager.mark_disconnected("sid_001")

        self.manager.record_reconnect_attempt("sid_001")

        assert self.manager.reconnection_attempts["sid_001"] == 1
        # 状态保持DISCONNECTED，直到成功重连或达到最大重试次数
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.DISCONNECTED

    def test_mark_reconnected(self):
        """测试标记已重连"""
        self.manager.register_connection("sid_001")
        self.manager.mark_disconnected("sid_001")
        self.manager.record_reconnect_attempt("sid_001")

        self.manager.mark_reconnected("sid_001")

        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.CONNECTED
        assert self.manager.reconnection_attempts["sid_001"] == 0

    def test_get_buffered_messages(self):
        """测试获取缓冲消息"""
        self.manager.register_connection("sid_001")
        self.manager.buffer_message("sid_001", "event_1", {"data": 1})
        self.manager.buffer_message("sid_001", "event_2", {"data": 2})

        messages = self.manager.get_buffered_messages("sid_001")

        assert len(messages) == 2

    def test_mark_message_sent(self):
        """测试标记消息已发送"""
        self.manager.register_connection("sid_001")
        self.manager.buffer_message("sid_001", "event_1", {"data": 1})

        msg_id = self.manager.message_buffers["sid_001"].messages[0].id
        self.manager.mark_message_sent("sid_001", msg_id)

        messages = self.manager.get_buffered_messages("sid_001")
        assert len(messages) == 0

    def test_mark_all_messages_sent(self):
        """测试标记所有消息已发送"""
        self.manager.register_connection("sid_001")
        self.manager.buffer_message("sid_001", "event_1", {"data": 1})
        self.manager.buffer_message("sid_001", "event_2", {"data": 2})

        self.manager.mark_all_messages_sent("sid_001")

        messages = self.manager.get_buffered_messages("sid_001")
        assert len(messages) == 0

    def test_clear_buffer(self):
        """测试清空缓冲区"""
        self.manager.register_connection("sid_001")
        self.manager.buffer_message("sid_001", "event_1", {"data": 1})
        self.manager.buffer_message("sid_001", "event_2", {"data": 2})

        self.manager.clear_buffer("sid_001")

        messages = self.manager.get_buffered_messages("sid_001")
        assert len(messages) == 0

    def test_get_reconnection_state(self):
        """测试获取重连状态"""
        self.manager.register_connection("sid_001")

        state = self.manager.get_reconnection_state("sid_001")

        assert state == ReconnectionState.CONNECTED

    def test_get_stats_single_connection(self):
        """测试获取单个连接统计"""
        self.manager.register_connection("sid_001")
        self.manager.buffer_message("sid_001", "event_1", {"data": 1})

        stats = self.manager.get_stats("sid_001")

        assert stats["sid"] == "sid_001"
        assert stats["state"] == ReconnectionState.CONNECTED
        assert stats["attempts"] == 0
        assert stats["max_retries"] == 5
        assert "message_buffer" in stats

    def test_get_all_stats(self):
        """测试获取所有连接统计"""
        self.manager.register_connection("sid_001")
        self.manager.register_connection("sid_002")
        self.manager.mark_disconnected("sid_002")

        stats = self.manager.get_all_stats()

        assert stats["total_connections"] == 2
        assert stats["connected"] == 1
        assert stats["disconnected"] == 1
        assert "timestamp" in stats

    def test_unregister_connection(self):
        """测试注销连接"""
        self.manager.register_connection("sid_001")
        self.manager.unregister_connection("sid_001")

        assert "sid_001" not in self.manager.reconnection_states

    def test_reconnection_workflow(self):
        """测试完整重连工作流"""
        # 1. 注册连接
        self.manager.register_connection("sid_001", user_id="user_001")
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.CONNECTED

        # 2. 缓冲消息（模拟离线状态）
        self.manager.mark_disconnected("sid_001")
        self.manager.buffer_message("sid_001", "update", {"stock": "600519"})
        self.manager.buffer_message("sid_001", "update", {"stock": "600000"})

        # 3. 检查是否需要重连
        assert self.manager.should_attempt_reconnect("sid_001")

        # 4. 记录重连尝试
        self.manager.record_reconnect_attempt("sid_001")
        # 状态保持DISCONNECTED，直到成功重连或达到最大重试次数
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.DISCONNECTED

        # 5. 标记重连成功
        self.manager.mark_reconnected("sid_001")
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.CONNECTED

        # 6. 获取缓冲消息进行补发
        buffered = self.manager.get_buffered_messages("sid_001")
        assert len(buffered) == 2

        # 7. 标记消息已发送
        self.manager.mark_all_messages_sent("sid_001")
        buffered_after = self.manager.get_buffered_messages("sid_001")
        assert len(buffered_after) == 0

    def test_multiple_connections_management(self):
        """测试多连接管理"""
        for i in range(5):
            self.manager.register_connection(f"sid_{i:03d}", user_id=f"user_{i}")

        self.manager.mark_disconnected("sid_001")
        self.manager.mark_disconnected("sid_003")

        stats = self.manager.get_all_stats()

        assert stats["total_connections"] == 5
        assert stats["connected"] == 3
        assert stats["disconnected"] == 2


class TestSingletonPattern:
    """测试单例模式"""

    def test_get_singleton_manager(self):
        """测试获取单例管理器"""
        reset_reconnection_manager()

        manager1 = get_reconnection_manager()
        manager2 = get_reconnection_manager()

        assert manager1 is manager2

    def test_reset_singleton_manager(self):
        """测试重置单例管理器"""
        reset_reconnection_manager()
        manager1 = get_reconnection_manager()

        reset_reconnection_manager()
        manager2 = get_reconnection_manager()

        assert manager1 is not manager2


class TestReconnectionScenarios:
    """测试重连场景"""

    def setup_method(self):
        """测试前初始化"""
        reset_reconnection_manager()
        self.manager = ReconnectionManager(
            base_interval=0.1,
            max_interval=0.5,
            max_retries=3,
        )

    def test_rapid_disconnect_reconnect(self):
        """测试快速断开和重连"""
        self.manager.register_connection("sid_001")
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.CONNECTED

        # 断开
        self.manager.mark_disconnected("sid_001")
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.DISCONNECTED

        # 重连
        self.manager.mark_reconnected("sid_001")
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.CONNECTED

    def test_message_buffering_across_reconnect(self):
        """测试跨重连的消息缓冲"""
        self.manager.register_connection("sid_001")

        # 断开连接
        self.manager.mark_disconnected("sid_001")

        # 缓冲多条消息
        for i in range(10):
            self.manager.buffer_message("sid_001", f"event_{i}", {"index": i})

        # 重连
        self.manager.record_reconnect_attempt("sid_001")
        self.manager.mark_reconnected("sid_001")

        # 获取缓冲消息
        buffered = self.manager.get_buffered_messages("sid_001")
        assert len(buffered) == 10

    def test_failed_reconnection_max_retries(self):
        """测试重连失败达到最大次数"""
        self.manager.register_connection("sid_001")
        self.manager.mark_disconnected("sid_001")

        for attempt in range(self.manager.max_retries):
            assert self.manager.should_attempt_reconnect("sid_001")
            self.manager.record_reconnect_attempt("sid_001")

        # 达到最大重试次数
        assert not self.manager.should_attempt_reconnect("sid_001")
        assert self.manager.reconnection_states["sid_001"] == ReconnectionState.RECONNECT_FAILED
