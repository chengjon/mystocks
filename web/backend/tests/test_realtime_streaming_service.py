"""
实时流媒体服务单元测试

Test Real-Time Streaming Service - Market data streaming via WebSocket

Task 6: 实时市场数据流传输测试

Author: Claude Code
Date: 2025-11-06
"""

from app.services.realtime_streaming_service import (
    RealtimeStreamingService,
    MarketDataStream,
    StreamSubscriber,
    StreamData,
    StreamStatus,
    StreamEventType,
    get_streaming_service,
    reset_streaming_service,
)


class TestStreamSubscriber:
    """测试流订阅者"""

    def test_subscriber_creation(self):
        """测试订阅者创建"""
        subscriber = StreamSubscriber("sid_001", user_id="user_001")

        assert subscriber.sid == "sid_001"
        assert subscriber.user_id == "user_001"
        assert subscriber.messages_received == 0
        assert "price" in subscriber.fields

    def test_subscriber_fields(self):
        """测试订阅者字段"""
        fields = {"price", "volume"}
        subscriber = StreamSubscriber("sid_001", fields=fields)

        assert subscriber.fields == fields

    def test_subscriber_update_activity(self):
        """测试更新活动时间"""
        subscriber = StreamSubscriber("sid_001")
        old_time = subscriber.subscribed_at

        subscriber.update_activity()

        assert subscriber.subscribed_at >= old_time


class TestStreamData:
    """测试流数据"""

    def test_stream_data_creation(self):
        """测试流数据创建"""
        data = StreamData(
            message_id="msg_001",
            symbol="600519",
            timestamp=1699000000000,
            data={"price": 100.5, "volume": 1000},
        )

        assert data.message_id == "msg_001"
        assert data.symbol == "600519"
        assert data.version == 1

    def test_stream_data_to_dict(self):
        """测试流数据转换"""
        data = StreamData(
            message_id="msg_001",
            symbol="600519",
            timestamp=1699000000000,
            data={"price": 100.5},
        )

        result = data.to_dict()

        assert result["message_id"] == "msg_001"
        assert result["symbol"] == "600519"
        assert "created_at" in result


class TestMarketDataStream:
    """测试市场数据流"""

    def test_stream_creation(self):
        """测试流创建"""
        stream = MarketDataStream("600519")

        assert stream.symbol == "600519"
        assert stream.status == StreamStatus.INACTIVE
        assert len(stream.subscribers) == 0

    def test_add_subscriber(self):
        """测试添加订阅者"""
        stream = MarketDataStream("600519")
        subscriber = stream.add_subscriber("sid_001", user_id="user_001")

        assert stream.has_subscribers()
        assert subscriber.sid == "sid_001"
        assert len(stream.subscribers) == 1

    def test_remove_subscriber(self):
        """测试移除订阅者"""
        stream = MarketDataStream("600519")
        stream.add_subscriber("sid_001")
        removed = stream.remove_subscriber("sid_001")

        assert removed.sid == "sid_001"
        assert not stream.has_subscribers()

    def test_buffer_data(self):
        """测试数据缓冲"""
        stream = MarketDataStream("600519")
        data = StreamData(
            message_id="msg_001",
            symbol="600519",
            timestamp=1699000000000,
            data={"price": 100.5},
        )

        success = stream.buffer_data(data)

        assert success
        assert len(stream.data_buffer) == 1

    def test_buffer_data_deduplication(self):
        """测试重复数据去重"""
        stream = MarketDataStream("600519")
        data = StreamData(
            message_id="msg_001",
            symbol="600519",
            timestamp=1699000000000,
            data={"price": 100.5},
        )

        # 第一次缓冲应该成功
        assert stream.buffer_data(data)

        # 重复缓冲应该失败
        assert not stream.buffer_data(data)
        assert len(stream.data_buffer) == 1

    def test_buffer_overflow(self):
        """测试缓冲区溢出"""
        stream = MarketDataStream("600519", buffer_size=3)

        for i in range(5):
            data = StreamData(
                message_id=f"msg_{i}",
                symbol="600519",
                timestamp=1699000000000 + i,
                data={"price": 100.5 + i},
            )
            stream.buffer_data(data)

        assert len(stream.data_buffer) == 3

    def test_get_buffered_data(self):
        """测试获取缓冲数据"""
        stream = MarketDataStream("600519")

        for i in range(3):
            data = StreamData(
                message_id=f"msg_{i}",
                symbol="600519",
                timestamp=1699000000000 + i,
                data={"price": 100.5 + i},
            )
            stream.buffer_data(data)

        buffered = stream.get_buffered_data()

        assert len(buffered) == 3

    def test_get_stats(self):
        """测试统计信息"""
        stream = MarketDataStream("600519")
        stream.add_subscriber("sid_001")

        stats = stream.get_stats()

        assert stats["symbol"] == "600519"
        assert stats["subscriber_count"] == 1
        assert "uptime_seconds" in stats


class TestRealtimeStreamingService:
    """测试实时流服务"""

    def setup_method(self):
        """测试前初始化"""
        reset_streaming_service()
        self.service = RealtimeStreamingService()

    def test_service_initialization(self):
        """测试服务初始化"""
        assert len(self.service.streams) == 0
        assert self.service.peak_subscribers == 0

    def test_start_stream(self):
        """测试启动流"""
        stream = self.service.start_stream("600519")

        assert stream.symbol == "600519"
        assert stream.status == StreamStatus.ACTIVE
        assert "600519" in self.service.streams

    def test_stop_stream(self):
        """测试停止流"""
        self.service.start_stream("600519")
        success = self.service.stop_stream("600519")

        assert success
        assert "600519" not in self.service.streams

    def test_subscribe(self):
        """测试订阅"""
        success = self.service.subscribe("sid_001", "600519", user_id="user_001")

        assert success
        assert "600519" in self.service.streams
        assert self.service.subscriber_to_stream["sid_001"] == "600519"

    def test_unsubscribe(self):
        """测试取消订阅"""
        self.service.subscribe("sid_001", "600519")
        success = self.service.unsubscribe("sid_001", "600519")

        assert success
        assert "sid_001" not in self.service.subscriber_to_stream

    def test_unsubscribe_stops_stream(self):
        """测试无订阅者时自动停止流"""
        self.service.subscribe("sid_001", "600519")
        self.service.unsubscribe("sid_001", "600519")

        assert "600519" not in self.service.streams

    def test_broadcast_data(self):
        """测试广播数据"""
        self.service.subscribe("sid_001", "600519")
        success = self.service.broadcast_data(
            "600519", {"price": 100.5, "volume": 1000}
        )

        assert success
        stream = self.service.get_stream("600519")
        assert len(stream.data_buffer) == 1

    def test_filter_data(self):
        """测试数据过滤"""
        data = {"price": 100.5, "volume": 1000, "timestamp": 1699000000000}
        fields = {"price", "volume"}

        filtered = self.service.filter_data(data, fields)

        assert "price" in filtered
        assert "volume" in filtered
        assert "timestamp" not in filtered

    def test_get_active_symbols(self):
        """测试获取活跃代码"""
        self.service.subscribe("sid_001", "600519")
        self.service.subscribe("sid_002", "000001")

        symbols = self.service.get_active_symbols()

        assert "600519" in symbols
        assert "000001" in symbols

    def test_get_stats(self):
        """测试全局统计"""
        self.service.subscribe("sid_001", "600519")
        self.service.subscribe("sid_002", "600519")
        self.service.subscribe("sid_003", "000001")

        stats = self.service.get_stats()

        assert stats["active_streams"] == 2
        assert stats["total_subscribers"] == 3
        assert "600519" in stats["streams"]

    def test_multiple_symbols(self):
        """测试多个股票代码"""
        symbols = ["600519", "000001", "600000"]

        for symbol in symbols:
            self.service.subscribe("sid_001", symbol)
            # 第一个订阅激活流
            assert symbol in self.service.streams

    def test_peak_subscribers_tracking(self):
        """测试峰值订阅者跟踪"""
        for i in range(5):
            self.service.subscribe(f"sid_{i}", "600519")

        assert self.service.peak_subscribers >= 5


class TestStreamingEventHandlers:
    """测试流事件处理"""

    def setup_method(self):
        """测试前初始化"""
        reset_streaming_service()
        self.service = RealtimeStreamingService()
        self.events = []

    def event_handler(self, data):
        """事件处理器"""
        self.events.append(data)

    def test_register_event_handler(self):
        """测试注册事件处理器"""
        self.service.register_event_handler(
            StreamEventType.STREAM_STARTED, self.event_handler
        )

        assert len(self.service.event_callbacks[StreamEventType.STREAM_STARTED]) > 0

    def test_stream_started_event(self):
        """测试流启动事件"""
        self.service.register_event_handler(
            StreamEventType.STREAM_STARTED, self.event_handler
        )

        self.service.start_stream("600519")

        assert len(self.events) == 1
        assert self.events[0]["symbol"] == "600519"

    def test_stream_stopped_event(self):
        """测试流停止事件"""
        self.service.start_stream("600519")
        self.service.register_event_handler(
            StreamEventType.STREAM_STOPPED, self.event_handler
        )

        self.service.stop_stream("600519")

        assert len(self.events) == 1
        assert self.events[0]["symbol"] == "600519"


class TestStreamingSingleton:
    """测试流服务单例"""

    def test_get_singleton_service(self):
        """测试获取单例"""
        reset_streaming_service()

        service1 = get_streaming_service()
        service2 = get_streaming_service()

        assert service1 is service2

    def test_reset_singleton(self):
        """测试重置单例"""
        reset_streaming_service()
        service1 = get_streaming_service()

        reset_streaming_service()
        service2 = get_streaming_service()

        assert service1 is not service2


class TestStreamingConcurrency:
    """测试并发场景"""

    def setup_method(self):
        """测试前初始化"""
        reset_streaming_service()
        self.service = RealtimeStreamingService()

    def test_multiple_subscribers_same_symbol(self):
        """测试同一个股票的多个订阅者"""
        for i in range(10):
            self.service.subscribe(f"sid_{i}", "600519")

        stream = self.service.get_stream("600519")

        assert len(stream.subscribers) == 10

    def test_single_subscriber_multiple_subscriptions(self):
        """测试单个订阅者多次订阅"""
        self.service.subscribe("sid_001", "600519")
        self.service.subscribe("sid_001", "000001")

        # 应该替换为最新的订阅
        assert self.service.subscriber_to_stream["sid_001"] == "000001"

    def test_rapid_subscribe_unsubscribe(self):
        """测试快速订阅/取消订阅"""
        for i in range(5):
            self.service.subscribe(f"sid_{i}", "600519")

        for i in range(5):
            self.service.unsubscribe(f"sid_{i}", "600519")

        assert len(self.service.streams) == 0

    def test_high_frequency_data_broadcast(self):
        """测试高频数据广播"""
        self.service.subscribe("sid_001", "600519")

        for i in range(100):
            self.service.broadcast_data("600519", {"price": 100.5 + i, "tick": i})

        stream = self.service.get_stream("600519")

        assert stream.messages_sent == 100

    def test_data_buffer_capacity_stress(self):
        """测试缓冲区容量压力"""
        self.service.subscribe("sid_001", "600519")
        stream = self.service.get_stream("600519")

        # 广播超过缓冲区容量的数据
        for i in range(150):
            self.service.broadcast_data("600519", {"price": 100.5 + i})

        # 缓冲区应该保持最大大小
        assert len(stream.data_buffer) == stream.buffer_size


class TestStreamingPerformance:
    """测试流性能"""

    def setup_method(self):
        """测试前初始化"""
        reset_streaming_service()
        self.service = RealtimeStreamingService()

    def test_subscribe_latency(self):
        """测试订阅延迟"""
        import time

        start = time.time()
        for i in range(100):
            self.service.subscribe(f"sid_{i}", f"stock_{i % 10}")
        elapsed = time.time() - start

        # 应该在100ms内完成100个订阅
        assert elapsed < 0.1

    def test_broadcast_latency(self):
        """测试广播延迟"""
        import time

        self.service.subscribe("sid_001", "600519")

        start = time.time()
        for i in range(1000):
            self.service.broadcast_data("600519", {"price": 100.5 + i})
        elapsed = time.time() - start

        # 应该在500ms内完成1000个广播
        assert elapsed < 0.5

    def test_filter_data_performance(self):
        """测试数据过滤性能"""
        import time

        data = {f"field_{i}": i for i in range(50)}
        fields = {f"field_{i}" for i in range(0, 50, 2)}

        start = time.time()
        for _ in range(1000):
            self.service.filter_data(data, fields)
        elapsed = time.time() - start

        # 应该在100ms内完成1000次过滤
        assert elapsed < 0.1


class TestStreamingEdgeCases:
    """测试边界情况"""

    def setup_method(self):
        """测试前初始化"""
        reset_streaming_service()
        self.service = RealtimeStreamingService()

    def test_unsubscribe_nonexistent_subscriber(self):
        """测试取消不存在订阅者的订阅"""
        success = self.service.unsubscribe("nonexistent_sid")

        assert not success

    def test_broadcast_to_nonexistent_stream(self):
        """测试广播到不存在的流"""
        success = self.service.broadcast_data("nonexistent_symbol", {"price": 100})

        assert not success

    def test_empty_field_filter(self):
        """测试空字段过滤"""
        data = {"price": 100.5, "volume": 1000}
        filtered = self.service.filter_data(data, set())

        assert len(filtered) == 0

    def test_empty_data_broadcast(self):
        """测试空数据广播"""
        self.service.subscribe("sid_001", "600519")
        success = self.service.broadcast_data("600519", {})

        assert success

    def test_special_characters_in_symbol(self):
        """测试特殊字符股票代码"""
        symbols = ["600519.SH", "000001.SZ", "BTC-USDT"]

        for symbol in symbols:
            success = self.service.subscribe("sid_001", symbol)
            assert success
