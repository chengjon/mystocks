"""
Unit Tests for Dependency Graph and Smart Scheduler
====================================================

测试依赖管理和智能调度模块的功能。

Coverage:
- Dependency Graph Construction
- Cycle Detection
- Topological Sort
- Smart Scheduler
- Parameter Validation

Author: MyStocks Project
"""

import pytest
import numpy as np
import time

from app.services.indicators import (
    IndicatorDependencyGraph,
    DependencyNode,
    NodeState,
    DependencyValidator,
    IncrementalCalculator,
    SmartScheduler,
    ScheduleResult,
    CalculationMode,
    OHLCVData,
    IndicatorResult,
    CalculationStatus,
    reset_indicator_registry,
)


class TestDependencyNode:
    """测试依赖图节点"""

    def test_create_node(self):
        """测试创建节点"""
        node = DependencyNode(abbreviation="SMA", params={"timeperiod": 20})
        assert node.abbreviation == "SMA"
        assert node.params == {"timeperiod": 20}
        assert node.state == NodeState.PENDING

    def test_node_id(self):
        """测试节点ID生成"""
        node = DependencyNode(abbreviation="SMA", params={"timeperiod": 20})
        assert node.node_id == "SMA[timeperiod-20]"

    def test_node_id_no_params(self):
        """测试无参数节点ID"""
        node = DependencyNode(abbreviation="RSI")
        assert node.node_id == "RSI"

    def test_add_dependency(self):
        """测试添加依赖"""
        node = DependencyNode(abbreviation="MACD")
        node.add_dependency("EMA")
        node.add_dependency("EMA")  # 重复添加
        assert len(node.dependencies) == 1
        assert "EMA" in node.dependencies


class TestIndicatorDependencyGraph:
    """测试依赖图"""

    def setup_method(self):
        """每个测试前创建新图"""
        self.graph = IndicatorDependencyGraph()

    def test_add_indicator(self):
        """测试添加指标"""
        node_id = self.graph.add_indicator(abbreviation="SMA", params={"timeperiod": 20})
        assert node_id == "SMA[timeperiod-20]"

    def test_add_indicator_with_dependencies(self):
        """测试添加带依赖的指标"""
        # 先添加依赖的指标
        self.graph.add_indicator(abbreviation="EMA", params={})

        # 添加依赖EMA的指标
        node_id = self.graph.add_indicator(
            abbreviation="MACD", params={"fastperiod": 12, "slowperiod": 26}, dependencies=["EMA"]
        )

        # 格式: key1-value1_key2-value2
        assert node_id == "MACD[fastperiod-12_slowperiod-26]"

        # 验证边已创建
        assert self.graph._graph.has_edge("EMA", node_id)

    def test_detect_no_cycle(self):
        """测试无循环情况"""
        # 添加独立指标
        self.graph.add_indicator(abbreviation="SMA", params={})
        self.graph.add_indicator(abbreviation="RSI", params={})

        cycles = self.graph.detect_cycles()
        assert cycles is None
        assert not self.graph.has_cycle()

    def test_detect_cycle(self):
        """测试检测循环"""
        # 添加 A 依赖 B
        self.graph.add_indicator(abbreviation="A", params={})
        self.graph.add_indicator(abbreviation="B", params={})
        self.graph.add_dependency_edge("B", "A")

        # 添加 B 依赖 A（形成循环）
        self.graph.add_dependency_edge("A", "B")

        cycles = self.graph.detect_cycles()
        assert cycles is not None
        assert len(cycles) > 0

    def test_get_ready_nodes(self):
        """测试获取就绪节点"""
        self.graph.add_indicator(abbreviation="SMA", params={})
        self.graph.add_indicator(abbreviation="RSI", params={})

        ready = self.graph.get_ready_nodes()
        assert len(ready) == 2

    def test_topological_sort(self):
        """测试拓扑排序"""
        # A 依赖 B
        self.graph.add_indicator(abbreviation="A", params={})
        self.graph.add_indicator(abbreviation="B", params={})
        self.graph.add_dependency_edge("B", "A")

        order = self.graph.topological_sort_kahn()
        assert order is not None
        # B 应该在 A 前面
        assert order.index("B") < order.index("A")

    def test_complex_topological_sort(self):
        """测试复杂拓扑排序"""
        # MACD 依赖 EMA
        self.graph.add_indicator(abbreviation="EMA", params={})
        self.graph.add_indicator(abbreviation="MACD", params={"fastperiod": 12}, dependencies=["EMA"])

        # SMA 和 RSI 独立
        self.graph.add_indicator(abbreviation="SMA", params={})
        self.graph.add_indicator(abbreviation="RSI", params={})

        order = self.graph.topological_sort_kahn()
        assert order is not None
        assert "EMA" in order
        # MACD 的完整节点ID是 "MACD[fastperiod_12]"
        macd_node_id = "MACD[fastperiod-12]"
        assert macd_node_id in order
        # EMA 应该在 MACD 前面
        assert order.index("EMA") < order.index(macd_node_id)

    def test_get_calculation_order(self):
        """测试获取计算顺序"""
        indicators = [
            {"abbreviation": "SMA", "params": {"timeperiod": 20}},
            {"abbreviation": "EMA", "params": {"timeperiod": 20}},
            {"abbreviation": "MACD", "params": {"fastperiod": 12}, "dependencies": ["EMA"]},
        ]

        order = self.graph.get_calculation_order(indicators)

        assert len(order) == 3
        # EMA 应该在 MACD 前面
        ema_ind = next(i for i in order if i["abbreviation"] == "EMA")
        macd_ind = next(i for i in order if i["abbreviation"] == "MACD")
        assert order.index(ema_ind) < order.index(macd_ind)

    def test_mark_computed(self):
        """测试标记计算完成"""
        self.graph.add_indicator(abbreviation="SMA", params={})
        node_id = "SMA"

        self.graph.mark_computed(node_id, [1, 2, 3], 10.5, False)

        node = self.graph.get_node(node_id)
        assert node.state == NodeState.COMPLETED
        assert node.result == [1, 2, 3]
        assert node.computation_time_ms == 10.5

    def test_mark_failed(self):
        """测试标记计算失败"""
        self.graph.add_indicator(abbreviation="SMA", params={})
        node_id = "SMA"

        self.graph.mark_failed(node_id, "计算错误")

        node = self.graph.get_node(node_id)
        assert node.state == NodeState.FAILED
        assert node.error == "计算错误"

    def test_reset(self):
        """测试重置"""
        self.graph.add_indicator(abbreviation="SMA", params={})
        self.graph.mark_computed("SMA", [1, 2, 3], 10, False)

        self.graph.reset()

        node = self.graph.get_node("SMA")
        assert node.state == NodeState.PENDING
        assert node.result is None

    def test_get_stats(self):
        """测试获取统计"""
        self.graph.add_indicator(abbreviation="SMA", params={})
        self.graph.add_indicator(abbreviation="RSI", params={})
        self.graph.add_dependency_edge("SMA", "RSI")

        stats = self.graph.get_stats()

        assert stats["total_nodes"] == 2
        assert stats["total_edges"] == 1
        assert stats["has_cycle"] is False
        assert stats["ready_nodes"] == 1


class TestDependencyValidator:
    """测试依赖验证器"""

    def test_validate_macd_valid(self):
        """测试有效MACD参数"""
        is_valid, error = DependencyValidator.validate_macd_params({"fastperiod": 12, "slowperiod": 26})
        assert is_valid is True
        assert error == ""

    def test_validate_macd_invalid(self):
        """测试无效MACD参数"""
        is_valid, error = DependencyValidator.validate_macd_params({"fastperiod": 30, "slowperiod": 26})
        assert is_valid is False
        assert "快线周期" in error

    def test_validate_kdj_valid(self):
        """测试有效KDJ参数"""
        is_valid, error = DependencyValidator.validate_kdj_params({"k_period": 9, "d_period": 3})
        assert is_valid is True

    def test_validate_kdj_invalid(self):
        """测试无效KDJ参数"""
        is_valid, error = DependencyValidator.validate_kdj_params({"k_period": 3, "d_period": 5})
        assert is_valid is False
        assert "K周期" in error

    def test_validate_indicator_params(self):
        """测试通用参数验证"""
        is_valid, error = DependencyValidator.validate_indicator_params("MACD", {"fastperiod": 12, "slowperiod": 26})
        assert is_valid is True


class TestIncrementalCalculator:
    """测试增量计算器"""

    def setup_method(self):
        """每个测试前创建"""
        self.graph = IndicatorDependencyGraph()
        self.calculator = IncrementalCalculator(self.graph)

    def test_set_and_get_cache(self):
        """测试缓存设置和获取"""
        self.calculator.set_cache("SMA", [1, 2, 3])
        result = self.calculator.get_cached_result("SMA")

        assert result == [1, 2, 3]

    def test_get_nonexistent_cache(self):
        """测试获取不存在的缓存"""
        result = self.calculator.get_cached_result("NONEXISTENT")
        assert result is None

    def test_clear_cache(self):
        """测试清空缓存"""
        self.calculator.set_cache("SMA", [1, 2, 3])
        self.calculator.clear_cache()

        result = self.calculator.get_cached_result("SMA")
        assert result is None


class TestSmartScheduler:
    """测试智能调度器"""

    def setup_method(self):
        """每个测试前创建"""
        reset_indicator_registry()
        self.scheduler = SmartScheduler(max_workers=2, mode=CalculationMode.SYNC, enable_cache=True)

    def test_create_scheduler(self):
        """测试创建调度器"""
        scheduler = SmartScheduler(max_workers=4)
        assert scheduler.max_workers == 4
        assert scheduler.mode == CalculationMode.ASYNC_PARALLEL

    def test_set_calculation_function(self):
        """测试设置计算函数"""

        def dummy_calc(abbr, ohlcv, params):
            return IndicatorResult(status=CalculationStatus.SUCCESS, abbreviation=abbr, parameters=params, values={})

        self.scheduler.set_calculation_function(dummy_calc)
        assert self.scheduler._calculation_func is not None

    def test_calculate_without_function(self):
        """测试未设置计算函数时抛出异常"""
        with pytest.raises(ValueError, match="未设置计算函数"):
            self.scheduler.calculate(
                [{"abbreviation": "SMA"}],
                OHLCVData(
                    open=np.array([1, 2, 3]),
                    high=np.array([2, 3, 4]),
                    low=np.array([0.5, 1.5, 2.5]),
                    close=np.array([1, 2, 3]),
                    volume=np.array([100, 200, 300]),
                ),
            )

    def test_sync_calculation(self):
        """测试同步计算"""

        def dummy_calc(abbr, ohlcv, params):
            return IndicatorResult(
                status=CalculationStatus.SUCCESS,
                abbreviation=abbr,
                parameters=params,
                values={"result": np.array([1, 2, 3])},
                calculation_time_ms=5.0,
            )

        self.scheduler.set_calculation_function(dummy_calc)
        self.scheduler.mode = CalculationMode.SYNC

        ohlcv = OHLCVData(
            open=np.array([1, 2, 3]),
            high=np.array([2, 3, 4]),
            low=np.array([0.5, 1.5, 2.5]),
            close=np.array([1, 2, 3]),
            volume=np.array([100, 200, 300]),
        )

        indicators = [
            {"abbreviation": "SMA", "params": {"timeperiod": 20}},
            {"abbreviation": "RSI", "params": {"timeperiod": 14}},
        ]

        results = self.scheduler.calculate(indicators, ohlcv)

        assert len(results) == 2
        assert all(isinstance(r, ScheduleResult) for r in results)

    def test_cache_functionality(self):
        """测试缓存功能"""
        call_count = 0

        def counting_calc(abbr, ohlcv, params):
            nonlocal call_count
            call_count += 1
            return IndicatorResult(
                status=CalculationStatus.SUCCESS,
                abbreviation=abbr,
                parameters=params,
                values={"result": np.array([1, 2, 3])},
                calculation_time_ms=5.0,
            )

        self.scheduler.set_calculation_function(counting_calc)
        self.scheduler.enable_cache = True

        ohlcv = OHLCVData(
            open=np.array([1, 2, 3]),
            high=np.array([2, 3, 4]),
            low=np.array([0.5, 1.5, 2.5]),
            close=np.array([1, 2, 3]),
            volume=np.array([100, 200, 300]),
        )

        indicators = [{"abbreviation": "SMA", "params": {"timeperiod": 20}}]

        # 第一次计算
        self.scheduler.calculate(indicators, ohlcv)
        assert call_count == 1

        # 第二次计算应该命中缓存（使用缓存时直接返回）
        self.scheduler.calculate(indicators, ohlcv)
        # 由于缓存生效，第二次不会调用计算函数
        assert call_count == 1, f"Expected 1 call (cache hit), but got {call_count}"

    def test_parallel_calculation(self):
        """测试并行计算"""
        execution_times = []

        def slow_calc(abbr, ohlcv, params):
            start = time.time()
            time.sleep(0.05)  # 50ms
            execution_times.append((abbr, time.time() - start))
            return IndicatorResult(
                status=CalculationStatus.SUCCESS,
                abbreviation=abbr,
                parameters=params,
                values={"result": np.array([1, 2, 3])},
                calculation_time_ms=50.0,
            )

        self.scheduler.set_calculation_function(slow_calc)
        self.scheduler.mode = CalculationMode.ASYNC_PARALLEL
        self.scheduler.max_workers = 4

        ohlcv = OHLCVData(
            open=np.array([1, 2, 3]),
            high=np.array([2, 3, 4]),
            low=np.array([0.5, 1.5, 2.5]),
            close=np.array([1, 2, 3]),
            volume=np.array([100, 200, 300]),
        )

        indicators = [
            {"abbreviation": "SMA", "params": {"timeperiod": 20}},
            {"abbreviation": "RSI", "params": {"timeperiod": 14}},
            {"abbreviation": "MACD", "params": {"fastperiod": 12}},
            {"abbreviation": "KDJ", "params": {"k_period": 9}},
        ]

        start = time.time()
        results = self.scheduler.calculate(indicators, ohlcv)
        total_time = time.time() - start

        # 并行应该比串行快（串行需要4*50ms=200ms）
        assert len(results) == 4
        assert total_time < 0.15  # 应该远小于150ms

    def test_empty_indicators(self):
        """测试空指标列表"""
        results = self.scheduler.calculate(
            [],
            OHLCVData(open=np.array([]), high=np.array([]), low=np.array([]), close=np.array([]), volume=np.array([])),
        )
        assert results == []

    def test_clear_cache(self):
        """测试清空缓存"""

        def dummy_calc(abbr, ohlcv, params):
            return IndicatorResult(status=CalculationStatus.SUCCESS, abbreviation=abbr, parameters=params, values={})

        self.scheduler.set_calculation_function(dummy_calc)
        self.scheduler._cache["test"] = "value"

        self.scheduler.clear_cache()

        assert len(self.scheduler._cache) == 0

    def test_reset(self):
        """测试重置调度器"""

        def dummy_calc(abbr, ohlcv, params):
            return IndicatorResult(status=CalculationStatus.SUCCESS, abbreviation=abbr, parameters=params, values={})

        self.scheduler.set_calculation_function(dummy_calc)
        self.scheduler._cache["test"] = "value"

        self.scheduler.reset()

        assert len(self.scheduler._cache) == 0


class TestIntegration:
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        graph = IndicatorDependencyGraph()
        scheduler = SmartScheduler(max_workers=2)

        # 设置计算函数
        def calc_func(abbr, ohlcv, params):
            return IndicatorResult(
                status=CalculationStatus.SUCCESS,
                abbreviation=abbr,
                parameters=params,
                values={"value": np.array([1.0, 2.0, 3.0])},
                calculation_time_ms=10.0,
            )

        scheduler.set_calculation_function(calc_func)

        # 准备数据
        ohlcv = OHLCVData(
            open=np.array([1, 2, 3, 4, 5]),
            high=np.array([2, 3, 4, 5, 6]),
            low=np.array([0.5, 1.5, 2.5, 3.5, 4.5]),
            close=np.array([1, 2, 3, 4, 5]),
            volume=np.array([100, 200, 300, 400, 500]),
        )

        # 定义指标（包含依赖）
        indicators = [
            {"abbreviation": "SMA", "params": {"timeperiod": 5}},
            {"abbreviation": "EMA", "params": {"timeperiod": 5}},
            {"abbreviation": "MACD", "params": {"fastperiod": 12}, "dependencies": ["EMA"]},
        ]

        # 执行计算
        results = scheduler.calculate(indicators, ohlcv)

        # 验证结果
        assert len(results) == 3

        # 验证EMA在MACD之前计算
        ema_result = next((r for r in results if r.abbreviation == "EMA"), None)
        macd_result = next((r for r in results if r.abbreviation == "MACD"), None)

        assert ema_result is not None
        assert macd_result is not None
        assert results.index(ema_result) < results.index(macd_result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
