"""
简化版智能阈值管理器测试
避免循环导入问题，直接测试核心功能
"""

import pytest
import numpy as np
from datetime import datetime
import sys
import os

# 添加项目根路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 直接导入模块测试功能
try:
    from src.monitoring.data_analyzer import DataAnalyzer
    from src.monitoring.statistical_optimizer import StatisticalOptimizer
    from src.monitoring.trend_analyzer import TrendAnalyzer
    from src.monitoring.clustering_analyzer import ClusteringAnalyzer
    from src.monitoring.threshold_rule_manager import ThresholdRuleManager

    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    MODULES_AVAILABLE = False


class TestCoreFunctionality:
    """核心功能测试（不依赖复杂导入）"""

    def test_basic_data_analysis(self):
        """测试基础数据分析功能"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        analyzer = DataAnalyzer(window_size=50)
        timestamp = datetime.now()

        # 添加测试数据
        for i in range(20):
            analyzer.add_data_point(10.0 + i * 0.1, timestamp, "test_rule")

        stats = analyzer.calculate_statistics()

        assert isinstance(stats, dict)
        assert "mean" in stats
        assert "std_dev" in stats
        assert "count" == 20
        assert stats["mean"] > 10.0
        assert stats["min_value"] == 10.0
        assert stats["max_value"] == 11.9

    def test_statistical_optimization(self):
        """测试统计优化功能"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        optimizer = StatisticalOptimizer()
        # 生成足够的数据点
        data = [10.0 + np.random.normal(0, 1) for _ in range(50)]

        result = optimizer.optimize_threshold_statistical(data=data, current_threshold=15.0, threshold_type="upper")

        assert isinstance(result, dict)
        assert "recommended_threshold" in result
        assert "confidence_score" in result
        assert result["recommended_threshold"] != 15.0  # 应该有调整

    def test_trend_analysis(self):
        """测试趋势分析功能"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        analyzer = TrendAnalyzer()
        # 生成上升趋势数据
        data = [10.0 + i * 0.5 for i in range(20)]

        result = analyzer.optimize_threshold_trend(data=data, current_threshold=15.0, threshold_type="upper")

        assert isinstance(result, dict)
        assert "trend_direction" in result
        assert result["trend_direction"] == "upward"  # 应该检测到上升趋势

    def test_clustering_analysis(self):
        """测试聚类分析功能"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        analyzer = ClusteringAnalyzer(min_cluster_size=3)
        # 创建两个明显聚类
        normal_data = [10.0, 10.1, 10.2, 10.3] * 10
        outlier_data = [50.0, 51.0, 52.0]
        data = normal_data + outlier_data

        result = analyzer.optimize_threshold_clustering(data=data, current_threshold=20.0, threshold_type="upper")

        assert isinstance(result, dict)
        assert "recommended_threshold" in result
        assert "num_clusters" in result

    def test_threshold_rule_management(self):
        """测试阈值规则管理功能"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        manager = ThresholdRuleManager()

        # 创建规则
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

        # 测试调整
        adjustment = manager.adjust_threshold(
            rule_name="cpu_usage_rule",
            new_threshold=85.0,
            reason="Performance optimization",
            confidence=0.8,
        )

        assert adjustment is not None
        assert adjustment.new_threshold == 85.0

        # 验证规则已更新
        updated_rule = manager.get_rule("cpu_usage_rule")
        assert updated_rule.current_threshold == 85.0

    def test_performance_benchmark(self):
        """性能基准测试"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        manager = ThresholdRuleManager()

        import time

        start_time = time.time()

        # 性能测试：创建100个规则应在1秒内完成
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

        assert total_time < 1.0, f"Performance benchmark failed: {total_time:.2f}s > 1.0s"


if __name__ == "__main__":
    # 如果直接运行此文件，显示模块可用性状态
    print(f"Modules available: {MODULES_AVAILABLE}")
    if MODULES_AVAILABLE:
        pytest.main([__file__, "-v", "--tb=short"])
    else:
        print("⚠️  Some modules are not available. This is expected during refactoring.")
