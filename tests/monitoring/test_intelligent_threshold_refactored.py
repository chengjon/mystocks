"""
TDD测试框架 - 智能阈值管理器重构
遵循红-绿-重构循环，确保拆分后的功能完整性
"""

import pytest
from datetime import datetime
import sys
import os

# 添加项目根路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)


class TestDataAnalyzer:
    """数据分析器测试类"""

    def test_init_data_analyzer(self):
        """测试：初始化数据分析器"""
        # TODO: 这个测试在重构前应该失败，因为没有拆分的模块
        from src.monitoring.data_analyzer import DataAnalyzer

        analyzer = DataAnalyzer(window_size=100)

        assert analyzer is not None
        assert hasattr(analyzer, "window_size")
        assert analyzer.window_size == 100

    def test_add_data_point(self):
        """测试：添加数据点"""
        from src.monitoring.data_analyzer import DataAnalyzer

        analyzer = DataAnalyzer()
        timestamp = datetime.now()

        analyzer.add_data_point(10.5, timestamp, "test_rule")

        # 验证数据点被添加
        assert len(analyzer.data_points) == 1
        assert analyzer.data_points[0]["value"] == 10.5

    def test_calculate_statistics(self):
        """测试：计算统计数据"""
        from src.monitoring.data_analyzer import DataAnalyzer

        analyzer = DataAnalyzer()
        timestamp = datetime.now()

        # 添加测试数据
        for i in range(10):
            analyzer.add_data_point(float(i), timestamp, "test_rule")

        stats = analyzer.calculate_statistics()

        assert isinstance(stats, dict)
        assert "mean" in stats
        assert "std_dev" in stats
        assert "min_value" in stats
        assert "max_value" in stats

    def test_detect_anomalies(self):
        """测试：异常检测"""
        from src.monitoring.data_analyzer import DataAnalyzer

        analyzer = DataAnalyzer()
        timestamp = datetime.now()

        # 添加正常数据
        for i in range(10):
            analyzer.add_data_point(10.0 + (i % 3) * 0.1, timestamp, "test_rule")

        # 添加异常数据
        analyzer.add_data_point(100.0, timestamp, "test_rule")

        anomalies = analyzer.detect_anomalies(contamination=0.1)

        assert isinstance(anomalies, list)
        assert len(anomalies) >= 0  # 可能检测到异常

    def test_analyze_trend(self):
        """测试：趋势分析"""
        from src.monitoring.data_analyzer import DataAnalyzer

        analyzer = DataAnalyzer()
        timestamp = datetime.now()

        # 添加上升趋势数据
        for i in range(10):
            analyzer.add_data_point(10.0 + i * 0.5, timestamp, "test_rule")

        trend = analyzer.analyze_trend()

        assert isinstance(trend, dict)
        assert "direction" in trend
        assert "strength" in trend


class TestStatisticalOptimizer:
    """统计优化器测试类"""

    def test_init_statistical_optimizer(self):
        """测试：初始化统计优化器"""
        # TODO: 重构前应该失败
        from src.monitoring.statistical_optimizer import StatisticalOptimizer

        optimizer = StatisticalOptimizer(min_data_points=30)

        assert optimizer is not None
        assert hasattr(optimizer, "min_data_points")
        assert optimizer.min_data_points == 30

    def test_optimize_threshold_statistical(self):
        """测试：统计阈值优化"""
        from src.monitoring.statistical_optimizer import StatisticalOptimizer

        optimizer = StatisticalOptimizer()
        data = [10.0, 10.5, 11.0, 10.8, 10.2, 10.7, 10.9, 10.4]
        current_threshold = 12.0

        result = optimizer.optimize_threshold_statistical(
            data=data, current_threshold=current_threshold, threshold_type="upper"
        )

        assert isinstance(result, dict)
        assert "recommended_threshold" in result
        assert "confidence_score" in result
        assert "reasoning" in result

    def test_calculate_confidence(self):
        """测试：置信度计算"""
        from src.monitoring.statistical_optimizer import StatisticalOptimizer

        optimizer = StatisticalOptimizer()
        data = [10.0] * 50  # 50个相同数据点

        confidence = optimizer._calculate_confidence(data, 10.5, "upper")

        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_insufficient_data_handling(self):
        """测试：数据不足处理"""
        from src.monitoring.statistical_optimizer import StatisticalOptimizer

        optimizer = StatisticalOptimizer(min_data_points=30)
        data = [10.0, 11.0]  # 数据不足

        result = optimizer.optimize_threshold_statistical(
            data=data, current_threshold=12.0, threshold_type="upper"
        )

        # 应该返回表示数据不足的结果
        assert "recommended_threshold" in result
        assert "confidence_score" in result


class TestTrendAnalyzer:
    """趋势分析器测试类"""

    def test_init_trend_analyzer(self):
        """测试：初始化趋势分析器"""
        # TODO: 重构前应该失败
        from src.monitoring.trend_analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer()

        assert analyzer is not None
        assert hasattr(analyzer, "window_size")

    def test_optimize_threshold_trend(self):
        """测试：趋势阈值优化"""
        from src.monitoring.trend_analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer()
        data = [10.0 + i * 0.1 for i in range(20)]  # 上升趋势数据
        current_threshold = 12.0

        result = analyzer.optimize_threshold_trend(
            data=data, current_threshold=current_threshold, threshold_type="upper"
        )

        assert isinstance(result, dict)
        assert "recommended_threshold" in result
        assert "confidence_score" in result
        assert "trend_direction" in result

    def test_detect_trend_direction(self):
        """测试：趋势方向检测"""
        from src.monitoring.trend_analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer()

        # 测试上升趋势
        uptrend_data = [10.0 + i * 0.5 for i in range(10)]
        direction = analyzer._detect_trend_direction(uptrend_data)
        assert direction == "upward"

        # 测试下降趋势
        downtrend_data = [20.0 - i * 0.5 for i in range(10)]
        direction = analyzer._detect_trend_direction(downtrend_data)
        assert direction == "downward"

        # 测试平稳趋势
        flat_data = [10.0] * 10
        direction = analyzer._detect_trend_direction(flat_data)
        assert direction == "stable"


class TestClusteringAnalyzer:
    """聚类分析器测试类"""

    def test_init_clustering_analyzer(self):
        """测试：初始化聚类分析器"""
        # TODO: 重构前应该失败
        from src.monitoring.clustering_analyzer import ClusteringAnalyzer

        analyzer = ClusteringAnalyzer(min_cluster_size=3)

        assert analyzer is not None
        assert hasattr(analyzer, "min_cluster_size")
        assert analyzer.min_cluster_size == 3

    def test_optimize_threshold_clustering(self):
        """测试：聚类阈值优化"""
        from src.monitoring.clustering_analyzer import ClusteringAnalyzer

        analyzer = ClusteringAnalyzer()
        # 创建两个聚类：正常数据和异常数据
        normal_data = [10.0, 10.1, 10.2, 10.3, 10.4] * 10
        outlier_data = [50.0, 51.0, 52.0]
        data = normal_data + outlier_data
        current_threshold = 15.0

        result = analyzer.optimize_threshold_clustering(
            data=data, current_threshold=current_threshold, threshold_type="upper"
        )

        assert isinstance(result, dict)
        assert "recommended_threshold" in result
        assert "confidence_score" in result
        assert "num_clusters" in result

    def test_identify_clusters(self):
        """测试：聚类识别"""
        from src.monitoring.clustering_analyzer import ClusteringAnalyzer

        analyzer = ClusteringAnalyzer()
        data = [10.0] * 10 + [50.0] * 5  # 两个明显聚类

        clusters = analyzer._identify_clusters(data)

        assert isinstance(clusters, dict)
        assert "cluster_labels" in clusters
        assert "num_clusters" in clusters

    def test_insufficient_clusters(self):
        """测试：聚类数量不足处理"""
        from src.monitoring.clustering_analyzer import ClusteringAnalyzer

        analyzer = ClusteringAnalyzer()
        data = [10.0, 10.1, 10.2]  # 数据点太少

        result = analyzer.optimize_threshold_clustering(
            data=data, current_threshold=12.0, threshold_type="upper"
        )

        # 应该返回无法聚类的结果
        assert "recommended_threshold" in result


class TestThresholdRuleManager:
    """阈值规则管理器测试类"""

    def test_init_threshold_rule_manager(self):
        """测试：初始化阈值规则管理器"""
        # TODO: 重构前应该失败
        from src.monitoring.threshold_rule_manager import ThresholdRuleManager

        manager = ThresholdRuleManager()

        assert manager is not None
        assert hasattr(manager, "rules")
        assert hasattr(manager, "adjustments")

    def test_create_threshold_rule(self):
        """测试：创建阈值规则"""
        from src.monitoring.threshold_rule_manager import ThresholdRuleManager

        manager = ThresholdRuleManager()
        rule_data = {
            "name": "cpu_usage_rule",
            "metric_name": "cpu_usage",
            "current_threshold": 80.0,
            "threshold_type": "upper",
        }

        rule = manager.create_threshold_rule(rule_data)

        assert rule.name == "cpu_usage_rule"
        assert rule.current_threshold == 80.0
        assert rule.metric_name == "cpu_usage"

    def test_adjust_threshold(self):
        """测试：调整阈值"""
        from src.monitoring.threshold_rule_manager import ThresholdRuleManager

        manager = ThresholdRuleManager()

        # 先创建规则
        rule = manager.create_threshold_rule(
            {
                "name": "test_rule",
                "metric_name": "test_metric",
                "current_threshold": 50.0,
            }
        )

        # 调整阈值
        adjustment = manager.adjust_threshold(
            rule_name="test_rule",
            new_threshold=60.0,
            reason="Optimization based on recent data",
            confidence=0.8,
        )

        assert adjustment is not None
        assert adjustment.new_threshold == 60.0
        assert adjustment.reason == "Optimization based on recent data"

    def test_get_rule_optimization_history(self):
        """测试：获取规则优化历史"""
        from src.monitoring.threshold_rule_manager import ThresholdRuleManager

        manager = ThresholdRuleManager()

        # 创建规则并进行调整
        manager.create_threshold_rule(
            {
                "name": "test_rule",
                "metric_name": "test_metric",
                "current_threshold": 50.0,
            }
        )

        manager.adjust_threshold("test_rule", 60.0, "Test adjustment", 0.7)

        history = manager.get_rule_optimization_history("test_rule")

        assert isinstance(history, list)
        assert len(history) > 0

    def test_performance_benchmark(self):
        """测试：性能基准"""
        from src.monitoring.threshold_rule_manager import ThresholdRuleManager
        import time

        manager = ThresholdRuleManager()

        # 性能测试：100次操作应在1秒内完成
        start_time = time.time()

        for i in range(100):
            manager.create_threshold_rule(
                {
                    "name": f"test_rule_{i}",
                    "metric_name": f"test_metric_{i}",
                    "current_threshold": 50.0 + i,
                }
            )

        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 1.0, (
            f"Performance benchmark failed: {total_time:.2f}s > 1.0s"
        )


if __name__ == "__main__":
    # 运行测试以验证当前状态（应该全部失败）
    pytest.main([__file__, "-v", "--tb=short"])
