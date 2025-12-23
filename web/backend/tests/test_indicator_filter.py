"""
技术指标过滤测试

Tests for Technical Indicator Filter

Task 8: 实现灵活的用户订阅过滤系统

Author: Claude Code
Date: 2025-11-07
"""

from app.services.indicator_filter import (
    IndicatorType,
    IndicatorConfig,
    IndicatorCalculator,
    IndicatorFilter,
    get_indicator_filter,
    reset_indicator_filter,
)


class TestIndicatorConfig:
    """Test indicator configuration"""

    def test_rsi_config(self):
        """Test RSI configuration"""
        config = IndicatorConfig(type=IndicatorType.RSI, period=14)
        assert config.type == IndicatorType.RSI
        assert config.period == 14

    def test_macd_config(self):
        """Test MACD configuration"""
        config = IndicatorConfig(
            type=IndicatorType.MACD,
            fast_period=12,
            slow_period=26,
            signal_period=9,
        )
        assert config.type == IndicatorType.MACD
        assert config.fast_period == 12
        assert config.slow_period == 26
        assert config.signal_period == 9

    def test_bb_config(self):
        """Test Bollinger Bands configuration"""
        config = IndicatorConfig(type=IndicatorType.BB, period=20, std_dev=2.0)
        assert config.type == IndicatorType.BB
        assert config.period == 20
        assert config.std_dev == 2.0


class TestIndicatorCalculator:
    """Test indicator calculator"""

    def test_calculator_initialization(self):
        """Test calculator initialization"""
        calc = IndicatorCalculator()
        assert calc.calculations == 0

    def test_calculate_rsi_insufficient_data(self):
        """Test RSI with insufficient data"""
        calc = IndicatorCalculator()
        prices = [100.0, 101.0, 102.0]
        rsi = calc.calculate_rsi(prices, period=14)
        assert rsi == 50.0  # Neutral value when data insufficient

    def test_calculate_rsi_normal(self):
        """Test RSI with normal data"""
        calc = IndicatorCalculator()
        # Create uptrend data
        prices = [100.0 + i * 0.5 for i in range(20)]
        rsi = calc.calculate_rsi(prices, period=14)
        assert 0 <= rsi <= 100
        assert rsi > 50  # Uptrend should have high RSI

    def test_calculate_rsi_downtrend(self):
        """Test RSI with downtrend data"""
        calc = IndicatorCalculator()
        # Create downtrend data
        prices = [100.0 - i * 0.5 for i in range(20)]
        rsi = calc.calculate_rsi(prices, period=14)
        assert 0 <= rsi <= 100
        assert rsi < 50  # Downtrend should have low RSI

    def test_calculate_sma(self):
        """Test SMA calculation"""
        calc = IndicatorCalculator()
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        sma = calc.calculate_sma(prices, period=3)
        expected = (102.0 + 103.0 + 104.0) / 3
        assert sma == round(expected, 2)

    def test_calculate_sma_insufficient_data(self):
        """Test SMA with insufficient data"""
        calc = IndicatorCalculator()
        prices = [100.0, 101.0]
        sma = calc.calculate_sma(prices, period=5)
        assert sma == prices[-1]  # Returns last price

    def test_calculate_ema(self):
        """Test EMA calculation"""
        calc = IndicatorCalculator()
        prices = [100.0 + i for i in range(30)]
        ema = calc.calculate_ema(prices, period=10)
        assert isinstance(ema, float)
        assert 100 < ema < 130  # Should be in range of prices

    def test_calculate_macd(self):
        """Test MACD calculation"""
        calc = IndicatorCalculator()
        prices = [100.0 + i * 0.1 for i in range(50)]
        macd_result = calc.calculate_macd(prices)
        assert "macd" in macd_result
        assert "signal" in macd_result
        assert "histogram" in macd_result
        assert isinstance(macd_result["macd"], float)

    def test_calculate_macd_insufficient_data(self):
        """Test MACD with insufficient data"""
        calc = IndicatorCalculator()
        prices = [100.0, 101.0, 102.0]
        macd_result = calc.calculate_macd(prices)
        assert macd_result["macd"] == 0.0
        assert macd_result["signal"] == 0.0

    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        calc = IndicatorCalculator()
        prices = [100.0 + i * 0.1 for i in range(30)]
        bb = calc.calculate_bollinger_bands(prices, period=20, std_dev=2.0)
        assert "upper" in bb
        assert "middle" in bb
        assert "lower" in bb
        assert bb["upper"] > bb["middle"]
        assert bb["middle"] > bb["lower"]

    def test_calculate_bollinger_bands_insufficient_data(self):
        """Test Bollinger Bands with insufficient data"""
        calc = IndicatorCalculator()
        prices = [100.0, 101.0, 102.0]
        bb = calc.calculate_bollinger_bands(prices, period=20)
        assert bb["upper"] == prices[-1]
        assert bb["middle"] == prices[-1]
        assert bb["lower"] == prices[-1]

    def test_calculate_stochastic(self):
        """Test Stochastic Oscillator calculation"""
        calc = IndicatorCalculator()
        closes = [100.0 + i for i in range(20)]
        highs = [101.0 + i for i in range(20)]
        lows = [99.0 + i for i in range(20)]
        stoch = calc.calculate_stochastic(closes, highs, lows)
        assert "k" in stoch
        assert "d" in stoch
        assert 0 <= stoch["k"] <= 100
        assert 0 <= stoch["d"] <= 100

    def test_calculator_stats(self):
        """Test calculator statistics"""
        calc = IndicatorCalculator()
        prices = [100.0 + i for i in range(30)]
        calc.calculate_rsi(prices)
        calc.calculate_sma(prices)
        stats = calc.get_stats()
        assert stats["total_calculations"] == 2


class TestIndicatorFilter:
    """Test indicator filter"""

    def test_filter_initialization(self):
        """Test filter initialization"""
        filter = IndicatorFilter()
        assert len(filter.price_cache) == 0

    def test_add_price_data(self):
        """Test adding price data"""
        filter = IndicatorFilter()
        filter.add_price_data("600519", 100.0)
        filter.add_price_data("600519", 101.0)
        assert len(filter.price_cache["600519"]) == 2
        assert filter.price_cache["600519"] == [100.0, 101.0]

    def test_price_cache_limit(self):
        """Test price cache size limit"""
        filter = IndicatorFilter()
        for i in range(150):
            filter.add_price_data("600519", 100.0 + i, max_cache=100)
        assert len(filter.price_cache["600519"]) <= 100

    def test_evaluate_rsi(self):
        """Test RSI evaluation"""
        filter = IndicatorFilter()
        prices = [100.0 + i * 0.5 for i in range(20)]
        for price in prices:
            filter.add_price_data("600519", price)

        # Uptrend should have high RSI
        result = filter.evaluate_rsi("600519", ">", 50)
        assert result is True

        # Should not have low RSI
        result = filter.evaluate_rsi("600519", "<", 30)
        assert result is False

    def test_evaluate_rsi_insufficient_data(self):
        """Test RSI evaluation with insufficient data"""
        filter = IndicatorFilter()
        filter.add_price_data("600519", 100.0)
        result = filter.evaluate_rsi("600519", ">", 50)
        assert result is False

    def test_evaluate_sma(self):
        """Test SMA evaluation"""
        filter = IndicatorFilter()
        prices = [100.0 + i for i in range(30)]
        for price in prices:
            filter.add_price_data("600519", price)

        # Current price above SMA
        result = filter.evaluate_sma("600519", 10, ">", 100.0)
        assert result is True

    def test_evaluate_sma_insufficient_data(self):
        """Test SMA evaluation with insufficient data"""
        filter = IndicatorFilter()
        filter.add_price_data("600519", 100.0)
        result = filter.evaluate_sma("600519", 20, ">", 100.0)
        assert result is False

    def test_evaluate_bb(self):
        """Test Bollinger Bands evaluation"""
        filter = IndicatorFilter()
        prices = [100.0 + i * 0.1 for i in range(30)]
        for price in prices:
            filter.add_price_data("600519", price)

        upper = filter.evaluate_bb("600519", 20, "upper")
        middle = filter.evaluate_bb("600519", 20, "middle")
        lower = filter.evaluate_bb("600519", 20, "lower")

        assert upper is not None
        assert middle is not None
        assert lower is not None
        assert upper > middle > lower

    def test_evaluate_bb_insufficient_data(self):
        """Test Bollinger Bands with insufficient data"""
        filter = IndicatorFilter()
        filter.add_price_data("600519", 100.0)
        result = filter.evaluate_bb("600519", 20, "upper")
        assert result is None

    def test_compare_operators(self):
        """Test comparison operators"""
        filter = IndicatorFilter()
        # Using internal compare method through RSI evaluation
        assert filter._compare(75.0, ">", 50.0) is True
        assert filter._compare(75.0, "<", 50.0) is False
        assert filter._compare(75.0, ">=", 75.0) is True
        assert filter._compare(75.0, "<=", 75.0) is True
        assert filter._compare(75.0, "==", 75.0) is True

    def test_multiple_symbols(self):
        """Test handling multiple symbols"""
        filter = IndicatorFilter()

        # Add data for two symbols
        for i in range(20):
            filter.add_price_data("600519", 100.0 + i * 0.5)
            filter.add_price_data("000001", 50.0 + i * 0.3)

        assert len(filter.price_cache) == 2
        stats = filter.get_stats()
        assert stats["symbols_cached"] == 2
        assert stats["total_prices_cached"] == 40

    def test_filter_stats(self):
        """Test filter statistics"""
        filter = IndicatorFilter()
        for i in range(30):
            filter.add_price_data("600519", 100.0 + i * 0.1)

        stats = filter.get_stats()
        assert stats["symbols_cached"] == 1
        assert stats["total_prices_cached"] == 30


class TestIndicatorFilterSingleton:
    """Test singleton pattern"""

    def test_get_indicator_filter(self):
        """Test getting indicator filter singleton"""
        reset_indicator_filter()
        filter1 = get_indicator_filter()
        filter2 = get_indicator_filter()
        assert filter1 is filter2

    def test_reset_indicator_filter(self):
        """Test resetting indicator filter"""
        reset_indicator_filter()
        filter1 = get_indicator_filter()
        reset_indicator_filter()
        filter2 = get_indicator_filter()
        assert filter1 is not filter2


class TestIndicatorIntegration:
    """Test integration scenarios"""

    def test_full_indicator_workflow(self):
        """Test complete workflow with multiple indicators"""
        filter = IndicatorFilter()

        # Generate realistic price data with uptrend
        prices = []
        price = 100.0
        for i in range(50):
            price += 0.2 if i % 2 == 0 else 0.1
            filter.add_price_data("600519", price)
            prices.append(price)

        # Test multiple indicators
        rsi_high = filter.evaluate_rsi("600519", ">", 50)
        sma_above = filter.evaluate_sma("600519", 20, ">", 100.0)
        bb_upper = filter.evaluate_bb("600519", 20, "upper")

        assert rsi_high is True
        assert sma_above is True
        assert bb_upper is not None

    def test_downtrend_detection(self):
        """Test downtrend detection"""
        filter = IndicatorFilter()

        # Generate downtrend
        price = 110.0
        for i in range(25):
            filter.add_price_data("600519", price)
            price -= 0.3

        rsi_low = filter.evaluate_rsi("600519", "<", 50)
        assert rsi_low is True

    def test_volatile_price_movement(self):
        """Test handling volatile price movement"""
        filter = IndicatorFilter()

        # Generate volatile data
        price = 100.0
        for i in range(30):
            if i % 2 == 0:
                price += 1.0
            else:
                price -= 0.8
            filter.add_price_data("600519", price)

        # Should still calculate indicators
        upper = filter.evaluate_bb("600519", 20, "upper")
        lower = filter.evaluate_bb("600519", 20, "lower")

        assert upper is not None
        assert lower is not None
        # Volatile prices should have wider BB
        assert (upper - lower) > 1.0
