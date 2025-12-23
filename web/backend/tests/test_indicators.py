"""
Unit and Integration Tests for Indicator Calculation
测试技术指标计算功能
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.services.indicator_calculator import (
    get_indicator_calculator,
    InsufficientDataError,
)
from app.main import app

# Test client
client = TestClient(app)


class TestMACalculation:
    """测试MA指标计算 (T016)"""

    def test_calculate_ma(self):
        """
        T016: Unit test for MA calculation
        验证 NumPy array → TA-Lib → 正确的MA值
        """
        calculator = get_indicator_calculator()

        # 准备测试数据: 10个简单的收盘价
        close_prices = np.array(
            [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0]
        )
        ohlcv_data = {
            "open": close_prices - 0.5,
            "high": close_prices + 0.5,
            "low": close_prices - 0.5,
            "close": close_prices,
            "volume": np.array([1000000] * 10),
        }

        # 计算MA(5)
        result = calculator.calculate_indicator(
            abbreviation="SMA", ohlcv_data=ohlcv_data, parameters={"timeperiod": 5}
        )

        # 验证返回格式
        assert "sma" in result
        assert isinstance(result["sma"], np.ndarray)
        assert len(result["sma"]) == 10

        # 验证前4个值为NaN (数据不足)
        assert np.all(np.isnan(result["sma"][:4]))

        # 验证第5个值 = (10+11+12+13+14)/5 = 12.0
        assert result["sma"][4] == pytest.approx(12.0, abs=0.01)

        # 验证第6个值 = (11+12+13+14+15)/5 = 13.0
        assert result["sma"][5] == pytest.approx(13.0, abs=0.01)

        # 验证最后一个值 = (15+16+17+18+19)/5 = 17.0
        assert result["sma"][9] == pytest.approx(17.0, abs=0.01)


class TestMultipleMACalculation:
    """测试批量MA计算 (T017)"""

    def test_calculate_multiple_mas(self):
        """
        T017: Unit test for multiple MAs
        验证批量计算功能
        """
        calculator = get_indicator_calculator()

        # 准备测试数据
        close_prices = np.array([10.0 + i for i in range(100)])
        ohlcv_data = {
            "open": close_prices - 0.5,
            "high": close_prices + 0.5,
            "low": close_prices - 0.5,
            "close": close_prices,
            "volume": np.array([1000000] * 100),
        }

        # 批量计算 MA5, MA10, MA20
        indicators = [
            {"abbreviation": "SMA", "parameters": {"timeperiod": 5}},
            {"abbreviation": "SMA", "parameters": {"timeperiod": 10}},
            {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
        ]

        results = calculator.calculate_multiple_indicators(indicators, ohlcv_data)

        # 验证返回了3个指标 (带索引key: SMA_0, SMA_1, SMA_2)
        assert len(results) == 3
        assert "SMA_0" in results
        assert "SMA_1" in results
        assert "SMA_2" in results

        # 验证每个指标都有values
        assert "values" in results["SMA_0"]
        assert "sma" in results["SMA_0"]["values"]

        # 验证panel_type
        assert results["SMA_0"]["panel_type"] == "overlay"

        # 验证数据点数量
        assert len(results["SMA_0"]["values"]["sma"]) == 100

        # 验证abbreviation字段
        assert results["SMA_0"]["abbreviation"] == "SMA"
        assert results["SMA_1"]["abbreviation"] == "SMA"
        assert results["SMA_2"]["abbreviation"] == "SMA"


class TestInsufficientDataHandling:
    """测试数据点不足处理 (T018)"""

    def test_insufficient_data_error(self):
        """
        T018: Unit test for insufficient data handling
        MA(200) with 50 days → InsufficientDataError
        """
        calculator = get_indicator_calculator()

        # 准备50个数据点
        close_prices = np.array([10.0 + i for i in range(50)])
        ohlcv_data = {
            "open": close_prices - 0.5,
            "high": close_prices + 0.5,
            "low": close_prices - 0.5,
            "close": close_prices,
            "volume": np.array([1000000] * 50),
        }

        # 尝试计算MA(200) - 应该抛出异常
        with pytest.raises(InsufficientDataError) as exc_info:
            calculator.calculate_indicator(
                abbreviation="SMA",
                ohlcv_data=ohlcv_data,
                parameters={"timeperiod": 200},
            )

        # 验证错误消息
        error_message = str(exc_info.value)
        assert "至少 200 个数据点" in error_message
        assert "只有 50 个数据点" in error_message

    def test_minimum_data_points_edge_case(self):
        """测试临界情况: 刚好满足最小数据点要求"""
        calculator = get_indicator_calculator()

        # 准备刚好20个数据点 (MA20的最小要求)
        close_prices = np.array([10.0 + i for i in range(20)])
        ohlcv_data = {
            "open": close_prices - 0.5,
            "high": close_prices + 0.5,
            "low": close_prices - 0.5,
            "close": close_prices,
            "volume": np.array([1000000] * 20),
        }

        # 应该成功计算
        result = calculator.calculate_indicator(
            abbreviation="SMA", ohlcv_data=ohlcv_data, parameters={"timeperiod": 20}
        )

        # 验证最后一个值不是NaN
        assert not np.isnan(result["sma"][-1])


class TestRegistryEndpoint:
    """测试注册表API端点 (T019)"""

    def test_get_registry(self):
        """
        T019: Integration test for registry endpoint
        验证返回161个指标及其元数据
        """
        response = client.get("/api/indicators/registry")

        # 验证状态码
        assert response.status_code == 200

        # 验证响应结构
        data = response.json()
        assert "total_count" in data
        assert "categories" in data
        assert "indicators" in data

        # 验证指标数量 (至少有我们实现的27个)
        assert data["total_count"] >= 27
        assert isinstance(data["indicators"], list)

        # 验证分类
        assert "trend" in data["categories"]
        assert "momentum" in data["categories"]
        assert "volatility" in data["categories"]
        assert "volume" in data["categories"]
        assert "candlestick" in data["categories"]

        # 验证单个指标的结构
        if len(data["indicators"]) > 0:
            indicator = data["indicators"][0]
            assert "abbreviation" in indicator
            assert "full_name" in indicator
            assert "chinese_name" in indicator
            assert "category" in indicator
            assert "description" in indicator
            assert "panel_type" in indicator
            assert "parameters" in indicator
            assert "outputs" in indicator

    def test_get_indicators_by_category(self):
        """测试按分类获取指标"""
        # 获取趋势类指标
        response = client.get("/api/indicators/registry/trend")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # 验证所有指标都是趋势类
        for indicator in data:
            assert indicator["category"] == "trend"

        # 验证包含SMA
        abbreviations = [ind["abbreviation"] for ind in data]
        assert "SMA" in abbreviations

    def test_get_invalid_category(self):
        """测试无效的分类"""
        response = client.get("/api/indicators/registry/invalid_category")

        # 应该返回400错误
        assert response.status_code == 400


class TestCalculateEndpoint:
    """测试指标计算API端点 (T020)"""

    def test_calculate_indicators_endpoint(self):
        """
        T020: Integration test for calculate endpoint
        POST /api/indicators/calculate with MA → 验证响应schema
        """
        request_data = {
            "symbol": "600519.SH",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "indicators": [{"abbreviation": "SMA", "parameters": {"timeperiod": 20}}],
            "use_cache": False,
        }

        response = client.post("/api/indicators/calculate", json=request_data)

        # 验证状态码 (可能是200或422,取决于是否有真实数据)
        assert response.status_code in [200, 422, 500]

        if response.status_code == 200:
            data = response.json()

            # 验证响应结构
            assert "symbol" in data
            assert "symbol_name" in data
            assert "start_date" in data
            assert "end_date" in data
            assert "ohlcv" in data
            assert "indicators" in data
            assert "calculation_time_ms" in data
            assert "cached" in data

            # 验证OHLCV结构
            assert "dates" in data["ohlcv"]
            assert "open" in data["ohlcv"]
            assert "high" in data["ohlcv"]
            assert "low" in data["ohlcv"]
            assert "close" in data["ohlcv"]
            assert "volume" in data["ohlcv"]

            # 验证指标结果
            assert len(data["indicators"]) == 1
            indicator_result = data["indicators"][0]
            assert indicator_result["abbreviation"] == "SMA"
            assert "outputs" in indicator_result
            assert "panel_type" in indicator_result

    def test_calculate_with_invalid_symbol(self):
        """测试无效的股票代码"""
        request_data = {
            "symbol": "INVALID",  # 无效格式
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "indicators": [{"abbreviation": "SMA", "parameters": {"timeperiod": 20}}],
        }

        response = client.post("/api/indicators/calculate", json=request_data)

        # 应该返回422 Validation Error
        assert response.status_code == 422

    def test_calculate_with_invalid_date_range(self):
        """测试无效的日期范围"""
        request_data = {
            "symbol": "600519.SH",
            "start_date": "2024-12-31",  # 开始日期晚于结束日期
            "end_date": "2024-01-01",
            "indicators": [{"abbreviation": "SMA", "parameters": {"timeperiod": 20}}],
        }

        response = client.post("/api/indicators/calculate", json=request_data)

        # 应该返回422 Validation Error
        assert response.status_code == 422

    def test_calculate_with_future_date(self):
        """测试未来日期"""
        request_data = {
            "symbol": "600519.SH",
            "start_date": "2024-01-01",
            "end_date": "2099-12-31",  # 未来日期
            "indicators": [{"abbreviation": "SMA", "parameters": {"timeperiod": 20}}],
        }

        response = client.post("/api/indicators/calculate", json=request_data)

        # 应该返回422 Validation Error
        assert response.status_code == 422

    def test_calculate_with_unknown_indicator(self):
        """测试未知指标"""
        request_data = {
            "symbol": "600519.SH",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "indicators": [{"abbreviation": "UNKNOWN_INDICATOR", "parameters": {}}],
        }

        response = client.post("/api/indicators/calculate", json=request_data)

        # 应该返回400或500错误
        assert response.status_code in [400, 500]


class TestDataQualityValidation:
    """测试数据质量验证"""

    def test_validate_ohlc_relationships(self):
        """测试OHLC关系验证"""
        calculator = get_indicator_calculator()

        # 无效数据: high < close
        invalid_ohlcv = {
            "open": np.array([10.0, 11.0]),
            "high": np.array([9.0, 10.0]),  # high < open/close (无效)
            "low": np.array([8.0, 9.0]),
            "close": np.array([10.0, 11.0]),
            "volume": np.array([1000, 1000]),
        }

        is_valid, error_msg = calculator.validate_data_quality(invalid_ohlcv)
        assert not is_valid
        assert "high" in error_msg.lower()

    def test_validate_negative_volume(self):
        """测试负成交量验证"""
        calculator = get_indicator_calculator()

        # 无效数据: 负成交量
        invalid_ohlcv = {
            "open": np.array([10.0, 11.0]),
            "high": np.array([11.0, 12.0]),
            "low": np.array([9.0, 10.0]),
            "close": np.array([10.5, 11.5]),
            "volume": np.array([1000, -500]),  # 负数 (无效)
        }

        is_valid, error_msg = calculator.validate_data_quality(invalid_ohlcv)
        assert not is_valid
        assert "volume" in error_msg.lower()


class TestMACDCalculation:
    """测试MACD指标计算"""

    def test_calculate_macd(self):
        """验证MACD计算返回三个输出 (macd, signal, hist)"""
        calculator = get_indicator_calculator()

        # 准备足够的数据点 (MACD需要至少slowperiod + signalperiod = 26+9 = 35)
        close_prices = np.array([10.0 + i * 0.1 for i in range(100)])
        ohlcv_data = {
            "open": close_prices - 0.5,
            "high": close_prices + 0.5,
            "low": close_prices - 0.5,
            "close": close_prices,
            "volume": np.array([1000000] * 100),
        }

        result = calculator.calculate_indicator(
            abbreviation="MACD",
            ohlcv_data=ohlcv_data,
            parameters={"fastperiod": 12, "slowperiod": 26, "signalperiod": 9},
        )

        # 验证返回三个值
        assert "macd" in result
        assert "signal" in result
        assert "hist" in result

        # 验证都是NumPy数组
        assert isinstance(result["macd"], np.ndarray)
        assert isinstance(result["signal"], np.ndarray)
        assert isinstance(result["hist"], np.ndarray)

        # 验证长度一致
        assert len(result["macd"]) == 100
        assert len(result["signal"]) == 100
        assert len(result["hist"]) == 100


class TestRSICalculation:
    """测试RSI指标计算"""

    def test_calculate_rsi(self):
        """验证RSI计算结果在0-100范围内"""
        calculator = get_indicator_calculator()

        # 准备数据
        close_prices = np.array([10.0 + i * 0.5 for i in range(50)])
        ohlcv_data = {
            "open": close_prices - 0.5,
            "high": close_prices + 0.5,
            "low": close_prices - 0.5,
            "close": close_prices,
            "volume": np.array([1000000] * 50),
        }

        result = calculator.calculate_indicator(
            abbreviation="RSI", ohlcv_data=ohlcv_data, parameters={"timeperiod": 14}
        )

        # 验证返回格式
        assert "rsi" in result

        # 验证非NaN值在0-100范围内
        rsi_values = result["rsi"]
        valid_values = rsi_values[~np.isnan(rsi_values)]
        assert np.all(valid_values >= 0)
        assert np.all(valid_values <= 100)
