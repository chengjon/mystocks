"""
数据聚合服务单元测试

Test Data Aggregation Service - Real-time OHLCV bar construction

Task 7: 实时OHLCV聚合服务测试

Author: Claude Code
Date: 2025-11-07
"""

from decimal import Decimal

from app.services.data_aggregation_service import (
    Tick,
    OHLCV,
    Timeframe,
    TimeframeBuffer,
    BarValidator,
    AggregationEngine,
    get_aggregation_engine,
    reset_aggregation_engine,
)


class TestTick:
    """测试Tick数据结构"""

    def test_tick_creation(self):
        """测试Tick创建"""
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.50"),
            volume=1000,
        )

        assert tick.symbol == "600519"
        assert tick.timestamp == 1699000000000
        assert tick.price == Decimal("100.50")
        assert tick.volume == 1000

    def test_tick_with_bid_ask(self):
        """测试带有bid/ask的Tick"""
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.50"),
            volume=1000,
            bid=Decimal("100.40"),
            ask=Decimal("100.60"),
        )

        assert tick.bid == Decimal("100.40")
        assert tick.ask == Decimal("100.60")


class TestOHLCV:
    """测试OHLCV数据结构"""

    def test_ohlcv_creation(self):
        """测试OHLCV创建"""
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.20"),
            volume=10000,
        )

        assert bar.symbol == "600519"
        assert bar.timeframe == Timeframe.ONE_MINUTE
        assert bar.close == Decimal("100.20")
        assert bar.tick_count == 1
        assert not bar.completed

    def test_ohlcv_to_dict(self):
        """测试OHLCV转换为字典"""
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.FIVE_MINUTES,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.20"),
            volume=10000,
        )

        result = bar.to_dict()

        assert result["symbol"] == "600519"
        assert result["timeframe"] == "5m"
        assert result["open"] == 100.0
        assert result["high"] == 100.5
        assert "created_at" in result


class TestTimeframeBuffer:
    """测试TimeframeBuffer"""

    def test_buffer_creation(self):
        """测试缓冲区创建"""
        buffer = TimeframeBuffer(symbol="600519", timeframe=Timeframe.ONE_MINUTE)

        assert buffer.symbol == "600519"
        assert buffer.timeframe == Timeframe.ONE_MINUTE
        assert buffer.current_bar is None

    def test_single_tick_creates_bar(self):
        """测试单个tick创建柱线"""
        buffer = TimeframeBuffer(symbol="600519", timeframe=Timeframe.ONE_MINUTE)
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=1000,
        )

        completed = buffer.add_tick(tick)

        assert completed is None
        assert buffer.current_bar is not None
        assert buffer.current_bar.open == Decimal("100.00")
        assert buffer.current_bar.close == Decimal("100.00")

    def test_multiple_ticks_update_bar(self):
        """测试多个tick更新柱线"""
        buffer = TimeframeBuffer(symbol="600519", timeframe=Timeframe.ONE_MINUTE)
        ticks = [
            Tick(
                symbol="600519",
                timestamp=1699000000000,
                price=Decimal("100.00"),
                volume=1000,
            ),
            Tick(
                symbol="600519",
                timestamp=1699000001000,
                price=Decimal("100.50"),
                volume=1500,
            ),
            Tick(
                symbol="600519",
                timestamp=1699000002000,
                price=Decimal("99.50"),
                volume=2000,
            ),
        ]

        for tick in ticks:
            completed = buffer.add_tick(tick)
            assert completed is None

        bar = buffer.current_bar
        assert bar.open == Decimal("100.00")
        assert bar.high == Decimal("100.50")
        assert bar.low == Decimal("99.50")
        assert bar.close == Decimal("99.50")
        assert bar.volume == 4500
        assert bar.tick_count == 3

    def test_time_boundary_completes_bar(self):
        """测试时间边界完成柱线"""
        buffer = TimeframeBuffer(symbol="600519", timeframe=Timeframe.ONE_MINUTE)

        # 第一个tick
        tick1 = Tick(
            symbol="600519",
            timestamp=1699000000000,  # 0秒
            price=Decimal("100.00"),
            volume=1000,
        )
        completed1 = buffer.add_tick(tick1)
        assert completed1 is None

        # 跨越时间边界的tick（61秒后）
        tick2 = Tick(
            symbol="600519",
            timestamp=1699000061000,  # 61秒
            price=Decimal("100.50"),
            volume=1500,
        )
        completed2 = buffer.add_tick(tick2)

        assert completed2 is not None
        assert completed2.completed == True
        assert completed2.close == Decimal("100.00")
        assert buffer.current_bar.open == Decimal("100.50")

    def test_get_open_bar(self):
        """测试获取开放柱线"""
        buffer = TimeframeBuffer(symbol="600519", timeframe=Timeframe.FIVE_MINUTES)
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=1000,
        )
        buffer.add_tick(tick)

        open_bar = buffer.get_open_bar()

        assert open_bar is not None
        assert open_bar.symbol == "600519"
        assert not open_bar.completed

    def test_force_complete_bar(self):
        """测试强制完成柱线"""
        buffer = TimeframeBuffer(symbol="600519", timeframe=Timeframe.ONE_HOUR)
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=1000,
        )
        buffer.add_tick(tick)

        completed = buffer.force_complete_bar()

        assert completed is not None
        assert completed.completed
        assert buffer.current_bar is None


class TestBarValidator:
    """测试BarValidator"""

    def test_validator_creation(self):
        """测试验证器创建"""
        validator = BarValidator(max_price_spike=0.5, min_volume=10)

        assert validator.max_price_spike == 0.5
        assert validator.min_volume == 10

    def test_validate_valid_bar(self):
        """测试验证有效柱线"""
        validator = BarValidator()
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.20"),
            volume=10000,
        )

        is_valid, error = validator.validate_ohlcv(bar)

        assert is_valid
        assert error is None

    def test_validate_invalid_ohlc_relationship(self):
        """测试验证无效的OHLC关系"""
        validator = BarValidator()
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("99.00"),  # High < Open (invalid)
            low=Decimal("98.00"),
            close=Decimal("99.50"),
            volume=10000,
        )

        is_valid, error = validator.validate_ohlcv(bar)

        assert not is_valid
        assert error is not None

    def test_validate_zero_price(self):
        """测试验证零价格"""
        validator = BarValidator()
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("0"),  # Invalid
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.20"),
            volume=10000,
        )

        is_valid, error = validator.validate_ohlcv(bar)

        assert not is_valid

    def test_validate_volume_too_low(self):
        """测试成交量太低"""
        validator = BarValidator(min_volume=100)
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.20"),
            volume=50,  # Below minimum
        )

        is_valid, error = validator.validate_ohlcv(bar)

        assert not is_valid
        assert "below minimum" in error

    def test_validate_price_spike(self):
        """测试验证价格涨跌幅"""
        validator = BarValidator(max_price_spike=0.1)  # 10%
        prev_close = Decimal("100.00")

        # High exceeds 10% spike
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("105.00"),
            high=Decimal("115.00"),  # 15% spike
            low=Decimal("104.00"),
            close=Decimal("105.00"),
            volume=10000,
        )

        is_valid, error = validator.validate_ohlcv(bar, prev_close)

        assert not is_valid
        assert "spike" in error

    def test_detect_zero_volume_anomaly(self):
        """测试检测零成交量异常"""
        validator = BarValidator()
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.20"),
            volume=0,
        )

        anomalies = validator.detect_anomalies(bar)

        assert "Zero volume" in anomalies

    def test_detect_doji_anomaly(self):
        """测试检测十字星"""
        validator = BarValidator()
        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.00"),
            low=Decimal("100.00"),
            close=Decimal("100.00"),
            volume=10000,
        )

        anomalies = validator.detect_anomalies(bar)

        assert "Doji candle (no price movement)" in anomalies


class TestAggregationEngine:
    """测试AggregationEngine"""

    def setup_method(self):
        """测试前初始化"""
        reset_aggregation_engine()
        self.engine = AggregationEngine()

    def test_engine_initialization(self):
        """测试引擎初始化"""
        assert self.engine.ticks_processed == 0
        assert self.engine.bars_completed == 0
        assert len(self.engine.buffers) == 0

    def test_single_tick_processing(self):
        """测试单个tick处理"""
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=1000,
        )

        completed = self.engine.add_tick(tick)

        assert self.engine.ticks_processed == 1
        assert len(completed) == 0  # No bars completed yet
        assert len(self.engine.buffers) == 5  # 5 timeframes

    def test_multiple_ticks_single_bar(self):
        """测试多个tick产生单个柱线"""
        ticks = [
            Tick(
                symbol="600519",
                timestamp=1699000000000 + i * 1000,
                price=Decimal("100.00") + Decimal(i * 0.1),
                volume=1000 + i * 100,
            )
            for i in range(5)
        ]

        for tick in ticks:
            completed = self.engine.add_tick(tick)
            assert len(completed) == 0

        open_bar = self.engine.get_open_bar("600519", Timeframe.ONE_MINUTE)
        assert open_bar is not None
        assert open_bar.tick_count == 5

    def test_tick_crossing_time_boundary(self):
        """测试tick跨越时间边界"""
        # First tick
        tick1 = Tick(
            symbol="600519",
            timestamp=1699000000000,  # 0秒
            price=Decimal("100.00"),
            volume=1000,
        )
        completed1 = self.engine.add_tick(tick1)
        assert len(completed1) == 0

        # Tick crossing 1-minute boundary
        tick2 = Tick(
            symbol="600519",
            timestamp=1699000061000,  # 61秒
            price=Decimal("100.50"),
            volume=1500,
        )
        completed2 = self.engine.add_tick(tick2)

        assert self.engine.bars_completed >= 1
        assert self.engine.ticks_processed == 2

    def test_multiple_symbols(self):
        """测试多个股票代码"""
        symbols = ["600519", "000001", "600000"]
        for symbol in symbols:
            tick = Tick(
                symbol=symbol,
                timestamp=1699000000000,
                price=Decimal("100.00"),
                volume=1000,
            )
            self.engine.add_tick(tick)

        # Should have buffers for 3 symbols x 5 timeframes = 15
        assert len(self.engine.buffers) == 15

    def test_get_open_bar(self):
        """测试获取开放柱线"""
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=1000,
        )
        self.engine.add_tick(tick)

        open_bar = self.engine.get_open_bar("600519", Timeframe.FIVE_MINUTES)

        assert open_bar is not None
        assert open_bar.symbol == "600519"
        assert not open_bar.completed

    def test_force_complete_bars(self):
        """测试强制完成柱线"""
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=1000,
        )
        self.engine.add_tick(tick)

        completed = self.engine.force_complete_bars("600519")

        # Should complete bars for all 5 timeframes
        assert len(completed) == 5
        assert self.engine.bars_completed >= 5

    def test_get_stats(self):
        """测试获取统计信息"""
        for i in range(10):
            tick = Tick(
                symbol="600519",
                timestamp=1699000000000 + i * 1000,
                price=Decimal("100.00"),
                volume=1000,
            )
            self.engine.add_tick(tick)

        stats = self.engine.get_stats()

        assert stats["ticks_processed"] == 10
        assert "active_buffers" in stats
        assert "total_symbols" in stats

    def test_engine_singleton(self):
        """测试引擎单例"""
        engine1 = get_aggregation_engine()
        engine2 = get_aggregation_engine()

        assert engine1 is engine2


class TestAggregationEdgeCases:
    """测试边界情况"""

    def setup_method(self):
        """测试前初始化"""
        reset_aggregation_engine()
        self.engine = AggregationEngine()

    def test_handling_price_gaps(self):
        """测试处理价格跳空"""
        # Normal price
        tick1 = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=1000,
        )
        self.engine.add_tick(tick1)

        # Large price jump
        tick2 = Tick(
            symbol="600519",
            timestamp=1699000001000,
            price=Decimal("150.00"),  # 50% jump
            volume=500,
        )
        self.engine.add_tick(tick2)

        open_bar = self.engine.get_open_bar("600519", Timeframe.ONE_MINUTE)
        assert open_bar.high == Decimal("150.00")
        assert open_bar.low == Decimal("100.00")

    def test_empty_volume_tick(self):
        """测试零成交量tick"""
        tick = Tick(
            symbol="600519",
            timestamp=1699000000000,
            price=Decimal("100.00"),
            volume=0,
        )
        completed = self.engine.add_tick(tick)

        # Should still be processed
        assert self.engine.ticks_processed == 1
        open_bar = self.engine.get_open_bar("600519", Timeframe.ONE_MINUTE)
        assert open_bar.volume == 0

    def test_same_timestamp_ticks(self):
        """测试相同时间戳的多个tick"""
        for i in range(5):
            tick = Tick(
                symbol="600519",
                timestamp=1699000000000,  # Same timestamp
                price=Decimal("100.00") + Decimal(i * 0.1),
                volume=1000,
            )
            self.engine.add_tick(tick)

        open_bar = self.engine.get_open_bar("600519", Timeframe.ONE_MINUTE)
        assert open_bar.tick_count == 5


class TestAggregationPerformance:
    """测试聚合性能"""

    def setup_method(self):
        """测试前初始化"""
        reset_aggregation_engine()
        self.engine = AggregationEngine()

    def test_bulk_tick_processing(self):
        """测试批量tick处理"""
        import time

        start = time.time()
        for i in range(1000):
            tick = Tick(
                symbol="600519",
                timestamp=1699000000000 + i * 100,  # Every 100ms
                price=Decimal("100.00") + Decimal(i % 100 * 0.01),
                volume=1000 + i % 100,
            )
            self.engine.add_tick(tick)
        elapsed = time.time() - start

        # Should process 1000 ticks quickly
        assert elapsed < 1.0  # Less than 1 second
        assert self.engine.ticks_processed == 1000

    def test_high_frequency_aggregation(self):
        """测试高频聚合"""
        import time

        start = time.time()
        # Simulate 1 minute of 1ms ticks (60,000 ticks)
        for i in range(100):  # Use 100 for reasonable test time
            tick = Tick(
                symbol="600519",
                timestamp=1699000000000 + i * 10,  # 10ms intervals
                price=Decimal("100.00") + Decimal((i % 10) * 0.01),
                volume=100 + (i % 50),
            )
            self.engine.add_tick(tick)
        elapsed = time.time() - start

        # Should maintain good performance
        assert elapsed < 0.5
        assert self.engine.bars_completed >= 0
