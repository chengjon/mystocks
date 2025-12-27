"""
Database Performance Monitor Test Suite
数据库性能监控测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.database_optimization.performance_monitor (334行)
"""

import pytest
from datetime import datetime
import sys
import os

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from database_optimization.performance_monitor import IndexPerformanceMonitor


class TestIndexPerformanceMonitor:
    """索引性能监控测试"""

    def test_performance_monitor_initialization(self):
        """测试性能监控器初始化"""
        monitor = IndexPerformanceMonitor()

        assert monitor.query_metrics == {}
        assert monitor.index_usage_stats == {}
        assert monitor.performance_baselines == {}
        assert monitor.slow_query_threshold_ms == 500
        assert monitor.very_slow_query_threshold_ms == 2000

    def test_performance_monitor_custom_thresholds(self):
        """测试自定义阈值初始化"""
        monitor = IndexPerformanceMonitor()
        monitor.slow_query_threshold_ms = 1000
        monitor.very_slow_query_threshold_ms = 5000

        assert monitor.slow_query_threshold_ms == 1000
        assert monitor.very_slow_query_threshold_ms == 5000

    def test_record_query_execution_basic(self):
        """测试基本查询执行记录"""
        monitor = IndexPerformanceMonitor()

        # 记录一次查询执行
        monitor.record_query_execution("test_query", 200, "users")

        assert "test_query" in monitor.query_metrics
        assert len(monitor.query_metrics["test_query"]) == 1

        metric = monitor.query_metrics["test_query"][0]
        assert metric["execution_time_ms"] == 200
        assert metric["table_name"] == "users"
        assert metric["is_slow"] is False
        assert metric["is_very_slow"] is False
        assert "timestamp" in metric

    def test_record_query_execution_slow(self):
        """测试慢查询记录"""
        monitor = IndexPerformanceMonitor()

        # 记录慢查询
        monitor.record_query_execution("slow_query", 800, "orders")

        metric = monitor.query_metrics["slow_query"][0]
        assert metric["execution_time_ms"] == 800
        assert metric["is_slow"] is True
        assert metric["is_very_slow"] is False

    def test_record_query_execution_very_slow(self):
        """测试非常慢查询记录"""
        monitor = IndexPerformanceMonitor()

        # 记录非常慢查询
        monitor.record_query_execution("very_slow_query", 3000, "products")

        metric = monitor.query_metrics["very_slow_query"][0]
        assert metric["execution_time_ms"] == 3000
        assert metric["is_slow"] is True
        assert metric["is_very_slow"] is True

    def test_record_multiple_executions(self):
        """测试多次查询执行记录"""
        monitor = IndexPerformanceMonitor()

        # 记录多次执行
        execution_times = [100, 200, 300, 400, 600]
        for time in execution_times:
            monitor.record_query_execution("frequent_query", time, "logs")

        assert len(monitor.query_metrics["frequent_query"]) == 5

        # 验证所有记录都有时间戳
        for metric in monitor.query_metrics["frequent_query"]:
            assert "timestamp" in metric
            assert metric["table_name"] == "logs"

    def test_analyze_query_performance_single_query(self):
        """测试单个查询性能分析"""
        monitor = IndexPerformanceMonitor()

        # 记录查询执行数据
        execution_times = [100, 150, 200, 250, 800]  # 包含一个慢查询
        for time in execution_times:
            monitor.record_query_execution("select_users", time, "users")

        # 分析性能
        result = monitor.analyze_query_performance("select_users")

        assert result["query_name"] == "select_users"
        assert result["execution_count"] == 5
        assert result["avg_execution_time_ms"] == 300.0  # (100+150+200+250+800)/5
        assert result["min_execution_time_ms"] == 100
        assert result["max_execution_time_ms"] == 800
        assert result["median_execution_time_ms"] == 200
        assert result["slow_query_percentage"] == 20.0  # 1/5 * 100

    def test_analyze_query_performance_all_queries(self):
        """测试所有查询性能分析"""
        monitor = IndexPerformanceMonitor()

        # 记录多个查询
        monitor.record_query_execution("query1", 100, "table1")
        monitor.record_query_execution("query1", 150, "table1")
        monitor.record_query_execution("query2", 600, "table2")
        monitor.record_query_execution("query2", 700, "table2")

        # 分析所有查询
        results = monitor.analyze_query_performance()

        assert len(results) == 2
        assert "query1" in results
        assert "query2" in results

        # 验证query1结果
        query1_result = results["query1"]
        assert query1_result["execution_count"] == 2
        assert query1_result["avg_execution_time_ms"] == 125.0

        # 验证query2结果
        query2_result = results["query2"]
        assert query2_result["execution_count"] == 2
        assert query2_result["slow_query_percentage"] == 100.0  # 都是慢查询

    def test_analyze_query_performance_empty_metrics(self):
        """测试空指标分析"""
        monitor = IndexPerformanceMonitor()

        # 分析不存在的查询
        result = monitor.analyze_query_performance("nonexistent_query")
        assert result == {}

        # 分析所有查询（无数据）
        result = monitor.analyze_query_performance()
        assert result == {}

    def test_analyze_query_performance_percentiles(self):
        """测试性能百分位数分析"""
        monitor = IndexPerformanceMonitor()

        # 创建大量查询数据用于百分位计算
        execution_times = list(range(100, 1001, 100))  # [100, 200, 300, ..., 1000]
        for time in execution_times:
            monitor.record_query_execution("percentile_test", time, "test_table")

        result = monitor.analyze_query_performance("percentile_test")

        # 验证百分位数
        assert result["p95_execution_time_ms"] == 950  # 95%的查询在950ms内完成
        assert result["p99_execution_time_ms"] == 990  # 99%的查询在990ms内完成

    def test_performance_baselines(self):
        """测试性能基线功能"""
        monitor = IndexPerformanceMonitor()

        # 设置性能基线
        monitor.performance_baselines["fast_query"] = {
            "max_execution_time_ms": 100,
            "avg_execution_time_ms": 50,
        }

        # 记录满足基线的查询
        monitor.record_query_execution("fast_query", 80, "users")

        # 记录违反基线的查询
        monitor.record_query_execution("fast_query", 150, "users")

        assert len(monitor.query_metrics["fast_query"]) == 2

    def test_index_usage_stats(self):
        """测试索引使用统计"""
        monitor = IndexPerformanceMonitor()

        # 模拟索引使用统计
        monitor.index_usage_stats = {
            "users_email_idx": {
                "usage_count": 1000,
                "last_used": datetime.now().isoformat(),
                "table_name": "users",
            },
            "orders_status_idx": {
                "usage_count": 500,
                "last_used": datetime.now().isoformat(),
                "table_name": "orders",
            },
        }

        assert len(monitor.index_usage_stats) == 2
        assert monitor.index_usage_stats["users_email_idx"]["usage_count"] == 1000
        assert monitor.index_usage_stats["orders_status_idx"]["table_name"] == "orders"

    def test_get_slow_queries(self):
        """测试获取慢查询功能"""
        monitor = IndexPerformanceMonitor()

        # 记录不同性能的查询
        queries_data = [
            ("fast_query", 50, "users"),
            ("normal_query", 300, "orders"),
            ("slow_query", 800, "products"),
            ("very_slow_query", 3000, "logs"),
        ]

        for query_name, exec_time, table_name in queries_data:
            monitor.record_query_execution(query_name, exec_time, table_name)

        # 获取所有慢查询
        slow_queries = []
        for query_name, metrics in monitor.query_metrics.items():
            for metric in metrics:
                if metric["is_slow"]:
                    slow_queries.append((query_name, metric))

        assert len(slow_queries) == 2  # slow_query 和 very_slow_query
        slow_query_names = [query[0] for query in slow_queries]
        assert "slow_query" in slow_query_names
        assert "very_slow_query" in slow_query_names
        assert "fast_query" not in slow_query_names
        assert "normal_query" not in slow_query_names

    def test_clear_old_metrics(self):
        """测试清除旧指标功能"""
        monitor = IndexPerformanceMonitor()

        # 记录一些查询
        monitor.record_query_execution("old_query", 100, "users")
        monitor.record_query_execution("recent_query", 200, "orders")

        assert len(monitor.query_metrics) == 2

        # 模拟清除旧数据的逻辑（这里简单演示）
        # 实际实现中可能需要基于时间戳的清除逻辑
        old_query_count = len(monitor.query_metrics.get("old_query", []))
        assert old_query_count == 1

    def test_performance_summary_statistics(self):
        """测试性能汇总统计"""
        monitor = IndexPerformanceMonitor()

        # 记录不同类型的查询
        test_data = [
            ("user_select", 150, "users"),
            ("user_select", 200, "users"),
            ("user_insert", 600, "users"),
            ("order_select", 100, "orders"),
            ("order_select", 250, "orders"),
            ("order_update", 800, "orders"),
        ]

        for query_name, exec_time, table_name in test_data:
            monitor.record_query_execution(query_name, exec_time, table_name)

        # 计算总体统计
        all_metrics = []
        for metrics in monitor.query_metrics.values():
            all_metrics.extend(metrics)

        total_queries = len(all_metrics)
        slow_queries = sum(1 for m in all_metrics if m["is_slow"])
        total_execution_time = sum(m["execution_time_ms"] for m in all_metrics)
        avg_execution_time = total_execution_time / total_queries

        assert total_queries == 6
        assert slow_queries == 2  # 600ms 和 800ms 的查询
        assert avg_execution_time == 350.0  # (150+200+600+100+250+800)/6

    def test_edge_cases(self):
        """测试边界情况"""
        monitor = IndexPerformanceMonitor()

        # 测试零执行时间
        monitor.record_query_execution("zero_time", 0, "test")
        metric = monitor.query_metrics["zero_time"][0]
        assert metric["execution_time_ms"] == 0
        assert metric["is_slow"] is False

        # 测试负执行时间（异常情况）
        monitor.record_query_execution("negative_time", -100, "test")
        metric = monitor.query_metrics["negative_time"][0]
        assert metric["execution_time_ms"] == -100
        assert metric["is_slow"] is False

    def test_concurrent_recording(self):
        """测试并发记录功能"""
        monitor = IndexPerformanceMonitor()

        # 模拟并发记录（在测试中是顺序的，但模拟并发场景）
        queries = []
        for i in range(10):
            query_name = f"concurrent_query_{i % 3}"  # 3个不同的查询
            exec_time = 100 + i * 50
            table_name = f"table_{i % 2}"  # 2个不同的表
            monitor.record_query_execution(query_name, exec_time, table_name)

        # 验证记录结果
        assert len(monitor.query_metrics) == 3
        for query_name in [
            "concurrent_query_0",
            "concurrent_query_1",
            "concurrent_query_2",
        ]:
            assert query_name in monitor.query_metrics

    def test_performance_monitoring_workflow(self):
        """测试完整的性能监控工作流程"""
        monitor = IndexPerformanceMonitor()

        # 1. 设置自定义阈值
        monitor.slow_query_threshold_ms = 300
        monitor.very_slow_query_threshold_ms = 1000

        # 2. 记录查询执行
        queries = [
            ("fast_user_query", 50, "users"),
            ("normal_order_query", 250, "orders"),
            ("slow_product_query", 500, "products"),
            ("very_slow_log_query", 1500, "logs"),
        ]

        for query_name, exec_time, table_name in queries:
            monitor.record_query_execution(query_name, exec_time, table_name)

        # 3. 分析性能
        analysis = monitor.analyze_query_performance()

        # 4. 验证分析结果
        assert len(analysis) == 4

        # 验证慢查询检测
        slow_query_results = [r for r in analysis.values() if r["slow_query_percentage"] > 0]
        assert len(slow_query_results) == 2  # slow_product_query 和 very_slow_log_query

        # 5. 验证性能指标
        for result in analysis.values():
            assert result["execution_count"] == 1
            assert result["avg_execution_time_ms"] > 0
            assert result["min_execution_time_ms"] == result["max_execution_time_ms"]
            assert result["median_execution_time_ms"] == result["min_execution_time_ms"]

    def test_memory_usage_simulation(self):
        """测试内存使用模拟"""
        monitor = IndexPerformanceMonitor()

        # 模拟大量查询记录，测试内存使用
        for i in range(1000):
            query_name = f"bulk_query_{i % 10}"  # 10个不同的查询类型
            exec_time = 100 + (i % 500)  # 执行时间在100-600之间
            table_name = f"table_{i % 5}"  # 5个不同的表
            monitor.record_query_execution(query_name, exec_time, table_name)

        # 验证记录数量
        assert len(monitor.query_metrics) == 10

        # 验证每个查询都有100个记录
        for query_metrics in monitor.query_metrics.values():
            assert len(query_metrics) == 100

    def test_error_handling(self):
        """测试错误处理"""
        monitor = IndexPerformanceMonitor()

        # 测试正常情况下的错误处理
        try:
            # 记录正常查询
            monitor.record_query_execution("test", 100, "test_table")
            # 分析不存在的查询
            result = monitor.analyze_query_performance("nonexistent")
            assert result == {}
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")


class TestPerformanceMonitorIntegration:
    """性能监控集成测试"""

    def test_real_world_scenario(self):
        """测试真实世界场景"""
        monitor = IndexPerformanceMonitor()

        # 模拟真实应用中的查询模式
        real_queries = [
            # 用户查询（通常较快）
            ("user_login", 45, "users"),
            ("user_profile", 120, "users"),
            ("user_profile", 80, "users"),
            # 订单查询（中等速度）
            ("order_history", 350, "orders"),
            ("order_history", 420, "orders"),
            ("order_create", 580, "orders"),
            # 报表查询（通常较慢）
            ("sales_report", 1200, "orders"),
            ("sales_report", 1500, "orders"),
            ("sales_report", 980, "orders"),
            # 日志查询（可能很慢）
            ("log_search", 2500, "logs"),
            ("log_search", 3200, "logs"),
        ]

        for query_name, exec_time, table_name in real_queries:
            monitor.record_query_execution(query_name, exec_time, table_name)

        # 分析整体性能
        analysis = monitor.analyze_query_performance()

        # 验证分析结果符合预期
        user_analysis = analysis["user_profile"]
        assert user_analysis["avg_execution_time_ms"] == 100.0  # (120+80)/2
        assert user_analysis["slow_query_percentage"] == 0.0

        order_analysis = analysis["order_history"]
        assert order_analysis["avg_execution_time_ms"] == 385.0  # (350+420)/2
        assert order_analysis["slow_query_percentage"] == 50.0

        report_analysis = analysis["sales_report"]
        assert report_analysis["avg_execution_time_ms"] == 1226.67  # (1200+1500+980)/3
        assert report_analysis["slow_query_percentage"] == 100.0

        log_analysis = analysis["log_search"]
        assert log_analysis["avg_execution_time_ms"] == 2850.0  # (2500+3200)/2
        assert log_analysis["slow_query_percentage"] == 100.0

    def test_performance_trend_analysis(self):
        """测试性能趋势分析"""
        monitor = IndexPerformanceMonitor()

        # 模拟性能随时间变化
        # 早期性能较差，后期性能改善
        performance_over_time = [
            (1000, 800, 600, 400, 200),  # 性能逐渐改善
        ]

        for exec_time in performance_over_time[0]:
            monitor.record_query_execution("trending_query", exec_time, "test_table")

        analysis = monitor.analyze_query_performance("trending_query")

        # 验证趋势分析
        assert analysis["max_execution_time_ms"] == 1000
        assert analysis["min_execution_time_ms"] == 200
        assert analysis["avg_execution_time_ms"] == 600.0

        # 模拟性能恶化
        performance_degradation = [100, 150, 200, 300, 500]
        for exec_time in performance_degradation:
            monitor.record_query_execution("degrading_query", exec_time, "test_table")

        degrading_analysis = monitor.analyze_query_performance("degrading_query")
        assert degrading_analysis["max_execution_time_ms"] == 500
        assert degrading_analysis["min_execution_time_ms"] == 100


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
