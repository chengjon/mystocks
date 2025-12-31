"""
Unit Tests for Indicator Registry and Metadata
===============================================

测试指标注册表和元数据模块的功能。

Coverage:
- IndicatorMetadata 创建和验证
- IndicatorParameter 约束验证
- IndicatorRegistry 注册和查询
- 配置文件加载
- 依赖管理

Author: MyStocks Project
"""

import pytest
import numpy as np
from pathlib import Path

from app.services.indicators import (
    IndicatorCategory,
    ComplexityLevel,
    ParameterType,
    ParameterConstraint,
    IndicatorParameter,
    IndicatorMetadata,
    get_indicator_registry,
    reset_indicator_registry,
    OHLCVData,
    IndicatorResult,
    CalculationStatus,
)


class TestIndicatorParameter:
    """测试指标参数"""

    def test_create_basic_parameter(self):
        """测试创建基本参数"""
        param = IndicatorParameter(name="timeperiod", type=ParameterType.INT, default=20, description="计算周期")
        assert param.name == "timeperiod"
        assert param.type == ParameterType.INT
        assert param.default == 20
        assert param.constraints.min_value is None

    def test_parameter_with_constraints(self):
        """测试带约束的参数"""
        constraints = ParameterConstraint(min_value=2, max_value=200, step=1)
        param = IndicatorParameter(name="timeperiod", type=ParameterType.INT, default=20, constraints=constraints)
        assert param.constraints.min_value == 2
        assert param.constraints.max_value == 200

    def test_parameter_validation_valid(self):
        """测试参数验证 - 有效值"""
        param = IndicatorParameter(
            name="timeperiod",
            type=ParameterType.INT,
            default=20,
            constraints=ParameterConstraint(min_value=2, max_value=200),
        )
        is_valid, _ = param.constraints.validate(50)
        assert is_valid is True

    def test_parameter_validation_below_min(self):
        """测试参数验证 - 低于最小值"""
        param = IndicatorParameter(
            name="timeperiod",
            type=ParameterType.INT,
            default=20,
            constraints=ParameterConstraint(min_value=2, max_value=200),
        )
        is_valid, error = param.constraints.validate(1)
        assert is_valid is False
        assert "小于最小值" in error

    def test_parameter_validation_above_max(self):
        """测试参数验证 - 高于最大值"""
        param = IndicatorParameter(
            name="timeperiod",
            type=ParameterType.INT,
            default=20,
            constraints=ParameterConstraint(min_value=2, max_value=200),
        )
        is_valid, error = param.constraints.validate(300)
        assert is_valid is False
        assert "大于最大值" in error


class TestIndicatorMetadata:
    """测试指标元数据"""

    def test_create_basic_metadata(self):
        """测试创建基本元数据"""
        meta = IndicatorMetadata(
            abbreviation="SMA",
            full_name="Simple Moving Average",
            chinese_name="简单移动平均线",
            category=IndicatorCategory.TREND,
            description="简单移动平均线",
        )
        assert meta.abbreviation == "SMA"
        assert meta.category == IndicatorCategory.TREND
        assert meta.version == "1.0.0"

    def test_get_parameter(self):
        """测试获取参数"""
        param = IndicatorParameter(name="timeperiod", type=ParameterType.INT, default=20)
        meta = IndicatorMetadata(
            abbreviation="SMA",
            full_name="Simple Moving Average",
            chinese_name="简单移动平均线",
            category=IndicatorCategory.TREND,
            description="",
            parameters=[param],
        )
        found = meta.get_parameter("timeperiod")
        assert found is not None
        assert found.name == "timeperiod"

    def test_get_nonexistent_parameter(self):
        """测试获取不存在的参数"""
        meta = IndicatorMetadata(
            abbreviation="SMA",
            full_name="Simple Moving Average",
            chinese_name="简单移动平均线",
            category=IndicatorCategory.TREND,
            description="",
            parameters=[],
        )
        found = meta.get_parameter("nonexistent")
        assert found is None

    def test_get_min_data_points(self):
        """测试计算最小数据点数"""
        param = IndicatorParameter(name="timeperiod", type=ParameterType.INT, default=20)
        meta = IndicatorMetadata(
            abbreviation="SMA",
            full_name="Simple Moving Average",
            chinese_name="简单移动平均线",
            category=IndicatorCategory.TREND,
            description="",
            parameters=[param],
        )
        # 使用默认参数
        min_points = meta.get_min_data_points({})
        assert min_points == 20

        # 使用自定义参数
        min_points = meta.get_min_data_points({"timeperiod": 50})
        assert min_points == 50

    def test_validate_parameters_valid(self):
        """测试参数验证 - 有效"""
        param = IndicatorParameter(
            name="timeperiod",
            type=ParameterType.INT,
            default=20,
            constraints=ParameterConstraint(min_value=2, max_value=200),
        )
        meta = IndicatorMetadata(
            abbreviation="SMA",
            full_name="Simple Moving Average",
            chinese_name="简单移动平均线",
            category=IndicatorCategory.TREND,
            description="",
            parameters=[param],
        )
        is_valid, _ = meta.validate_parameters({"timeperiod": 50})
        assert is_valid is True

    def test_validate_parameters_invalid(self):
        """测试参数验证 - 无效"""
        param = IndicatorParameter(
            name="timeperiod",
            type=ParameterType.INT,
            default=20,
            constraints=ParameterConstraint(min_value=2, max_value=200),
        )
        meta = IndicatorMetadata(
            abbreviation="SMA",
            full_name="Simple Moving Average",
            chinese_name="简单移动平均线",
            category=IndicatorCategory.TREND,
            description="",
            parameters=[param],
        )
        is_valid, error = meta.validate_parameters({"timeperiod": 1})
        assert is_valid is False
        assert "小于最小值" in error


class TestIndicatorRegistry:
    """测试指标注册表"""

    def setup_method(self):
        """每个测试前重置注册表"""
        reset_indicator_registry()

    def test_register_indicator(self):
        """测试注册指标"""
        registry = get_indicator_registry()
        meta = IndicatorMetadata(
            abbreviation="SMA",
            full_name="Simple Moving Average",
            chinese_name="简单移动平均线",
            category=IndicatorCategory.TREND,
            description="Test indicator",
        )
        result = registry.register(meta)
        assert result is True
        assert registry.exists("SMA")

    def test_get_indicator(self):
        """测试获取指标"""
        registry = get_indicator_registry()
        meta = IndicatorMetadata(
            abbreviation="RSI",
            full_name="Relative Strength Index",
            chinese_name="相对强弱指数",
            category=IndicatorCategory.MOMENTUM,
            description="Test indicator",
        )
        registry.register(meta)

        retrieved = registry.get("RSI")
        assert retrieved is not None
        assert retrieved.abbreviation == "RSI"
        assert retrieved.category == IndicatorCategory.MOMENTUM

    def test_get_nonexistent_indicator(self):
        """测试获取不存在的指标"""
        registry = get_indicator_registry()
        result = registry.get("NONEXISTENT")
        assert result is None

    def test_unregister_indicator(self):
        """测试注销指标"""
        registry = get_indicator_registry()
        meta = IndicatorMetadata(
            abbreviation="MACD",
            full_name="Moving Average Convergence Divergence",
            chinese_name="MACD",
            category=IndicatorCategory.TREND,
            description="",
        )
        registry.register(meta)
        assert registry.exists("MACD")

        result = registry.unregister("MACD")
        assert result is True
        assert not registry.exists("MACD")

    def test_unregister_nonexistent(self):
        """测试注销不存在的指标"""
        registry = get_indicator_registry()
        result = registry.unregister("NONEXISTENT")
        assert result is False

    def test_get_by_category(self):
        """测试按分类获取指标"""
        registry = get_indicator_registry()

        # 注册不同分类的指标
        registry.register(
            IndicatorMetadata(
                abbreviation="SMA",
                full_name="Simple Moving Average",
                chinese_name="简单移动平均线",
                category=IndicatorCategory.TREND,
                description="",
            )
        )
        registry.register(
            IndicatorMetadata(
                abbreviation="RSI",
                full_name="Relative Strength Index",
                chinese_name="相对强弱指数",
                category=IndicatorCategory.MOMENTUM,
                description="",
            )
        )
        registry.register(
            IndicatorMetadata(
                abbreviation="ATR",
                full_name="Average True Range",
                chinese_name="真实波幅均值",
                category=IndicatorCategory.VOLATILITY,
                description="",
            )
        )

        trend_indicators = registry.get_by_category(IndicatorCategory.TREND)
        assert "SMA" in trend_indicators
        assert "RSI" not in trend_indicators
        assert len(trend_indicators) == 1

    def test_get_all(self):
        """测试获取所有指标"""
        reset_indicator_registry()
        registry = get_indicator_registry()

        registry.register(
            IndicatorMetadata(
                abbreviation="SMA2",
                full_name="Simple Moving Average",
                chinese_name="简单移动平均线",
                category=IndicatorCategory.TREND,
                description="",
            )
        )
        registry.register(
            IndicatorMetadata(
                abbreviation="RSI2",
                full_name="Relative Strength Index",
                chinese_name="相对强弱指数",
                category=IndicatorCategory.MOMENTUM,
                description="",
            )
        )

        all_indicators = registry.get_all()
        assert len(all_indicators) >= 2  # 至少2个，可能是更多因为有配置加载

    def test_search_indicators(self):
        """测试搜索指标"""
        reset_indicator_registry()
        registry = get_indicator_registry()

        registry.register(
            IndicatorMetadata(
                abbreviation="SMA_SEARCH",
                full_name="Simple Moving Average",
                chinese_name="简单移动平均线",
                category=IndicatorCategory.TREND,
                description="Simple moving average for price smoothing",
            )
        )
        registry.register(
            IndicatorMetadata(
                abbreviation="RSI_SEARCH",
                full_name="Relative Strength Index",
                chinese_name="相对强弱指数",
                category=IndicatorCategory.MOMENTUM,
                description="Measures overbought and oversold levels",
            )
        )

        # 搜索 "simple" - 应该在 full_name 中
        results = registry.search("simple")
        assert len(results) >= 1, f"Expected >=1 results for 'simple', got {len(results)}"

        # 搜索 "average" - 应该在 full_name 中
        results = registry.search("average")
        assert len(results) >= 1, f"Expected >=1 results for 'average', got {len(results)}"

        # 搜索 "RSI" - 应该在 abbreviation 中
        results = registry.search("RSI")
        assert len(results) >= 1, f"Expected >=1 results for 'RSI', got {len(results)}"

        # 搜索 "strength" - 应该在 full_name 中
        results = registry.search("strength")
        assert len(results) >= 1, f"Expected >=1 results for 'strength', got {len(results)}"

        # 搜索 "overbought" - 应该在 description 中
        results = registry.search("overbought")
        assert len(results) >= 1, f"Expected >=1 results for 'overbought', got {len(results)}"

    def test_validate_indicator_valid(self):
        """测试验证有效指标"""
        registry = get_indicator_registry()

        param = IndicatorParameter(
            name="timeperiod",
            type=ParameterType.INT,
            default=14,
            constraints=ParameterConstraint(min_value=2, max_value=100),
        )
        registry.register(
            IndicatorMetadata(
                abbreviation="RSI",
                full_name="Relative Strength Index",
                chinese_name="相对强弱指数",
                category=IndicatorCategory.MOMENTUM,
                description="",
                parameters=[param],
            )
        )

        is_valid, _ = registry.validate_indicator("RSI", {"timeperiod": 14})
        assert is_valid is True

    def test_validate_indicator_invalid(self):
        """测试验证无效指标"""
        registry = get_indicator_registry()

        param = IndicatorParameter(
            name="timeperiod",
            type=ParameterType.INT,
            default=14,
            constraints=ParameterConstraint(min_value=2, max_value=100),
        )
        registry.register(
            IndicatorMetadata(
                abbreviation="RSI",
                full_name="Relative Strength Index",
                chinese_name="相对强弱指数",
                category=IndicatorCategory.MOMENTUM,
                description="",
                parameters=[param],
            )
        )

        is_valid, error = registry.validate_indicator("RSI", {"timeperiod": 1})
        assert is_valid is False
        assert "小于最小值" in error

    def test_singleton_pattern(self):
        """测试单例模式"""
        registry1 = get_indicator_registry()
        registry2 = get_indicator_registry()
        assert registry1 is registry2

    def test_get_stats(self):
        """测试获取统计信息"""
        reset_indicator_registry()
        registry = get_indicator_registry()

        registry.register(
            IndicatorMetadata(
                abbreviation="SMA_STATS",
                full_name="Simple Moving Average",
                chinese_name="简单移动平均线",
                category=IndicatorCategory.TREND,
                description="",
                complexity=ComplexityLevel.LOW,
            )
        )
        registry.register(
            IndicatorMetadata(
                abbreviation="RSI_STATS",
                full_name="Relative Strength Index",
                chinese_name="相对强弱指数",
                category=IndicatorCategory.MOMENTUM,
                description="",
                complexity=ComplexityLevel.MEDIUM,
            )
        )

        stats = registry.get_stats()
        assert stats.total_indicators >= 2
        assert "trend" in stats.by_category
        assert "momentum" in stats.by_category
        assert "low" in stats.by_complexity
        assert "medium" in stats.by_complexity


class TestConfigLoading:
    """测试配置文件加载"""

    def setup_method(self):
        """每个测试前重置注册表"""
        reset_indicator_registry()

    def test_load_from_yaml(self):
        """测试从YAML加载配置"""
        registry = get_indicator_registry()

        config_path = (
            Path(__file__).parent.parent.parent.parent.parent / "config" / "indicators" / "indicator_config.yaml"
        )

        if config_path.exists():
            count = registry.load_from_config(str(config_path))
            assert count > 0

            # 验证一些关键指标
            assert registry.exists("SMA")
            assert registry.exists("RSI")
            assert registry.exists("MACD")

            # 验证MACD的依赖
            macd = registry.get("MACD")
            assert "EMA" in macd.dependencies


class TestOHLCVData:
    """测试OHLCV数据结构"""

    def test_create_ohlcv(self):
        """测试创建OHLCV数据"""
        n = 100
        data = OHLCVData(
            open=np.random.randn(n) + 10,
            high=np.random.randn(n) + 11,
            low=np.random.randn(n) + 9,
            close=np.random.randn(n) + 10,
            volume=np.random.randint(1000, 10000, n),
        )
        assert data.length == n

    def test_ohlcv_length_mismatch(self):
        """测试OHLCV长度不一致"""
        with pytest.raises(ValueError):
            OHLCVData(
                open=np.array([1, 2, 3]),
                high=np.array([1, 2, 3]),
                low=np.array([1, 2, 3]),
                close=np.array([1, 2]),  # 长度不一致
                volume=np.array([1, 2, 3]),
            )

    def test_ohlcv_slice(self):
        """测试OHLCV切片"""
        n = 100
        data = OHLCVData(
            open=np.arange(n), high=np.arange(n), low=np.arange(n), close=np.arange(n), volume=np.arange(n)
        )

        sliced = data.slice(10, 20)
        assert sliced.length == 10
        assert sliced.open[0] == 10
        assert sliced.close[-1] == 19


class TestIndicatorResult:
    """测试指标结果"""

    def test_create_success_result(self):
        """测试创建成功结果"""
        result = IndicatorResult(
            status=CalculationStatus.SUCCESS,
            abbreviation="SMA",
            parameters={"timeperiod": 20},
            values={"sma": np.array([1, 2, 3])},
            data_points=3,
        )
        assert result.success
        assert result.status == CalculationStatus.SUCCESS

    def test_get_output(self):
        """测试获取输出"""
        result = IndicatorResult(
            status=CalculationStatus.SUCCESS,
            abbreviation="MACD",
            parameters={},
            values={"macd": np.array([1, 2, 3]), "signal": np.array([0.5, 1, 1.5])},
        )
        macd = result.get_output("macd")
        assert macd is not None
        assert len(macd) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
