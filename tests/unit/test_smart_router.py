"""
单元测试: SmartRouter
"""

import pytest
from src.core.data_source.smart_router import SmartRouter


class TestSmartRouter:
    """SmartRouter 单元测试"""

    def test_performance_score_calculation(self):
        """测试性能评分计算"""
        router = SmartRouter()

        # 记录一些调用
        for i in range(10):
            router.record_call("test_endpoint", latency=0.1, success=True)
        router.record_call_complete("test_endpoint")

        # 记录一些失败调用
        for i in range(2):
            router.record_call("test_endpoint", latency=0.5, success=False)
        router.record_call_complete("test_endpoint")

        # 获取评分
        score = router._score_by_performance("test_endpoint")

        # 应该有合理的评分 (0-100)
        assert 0 <= score <= 100
        assert score > 50  # 大部分成功，应该 > 50

    def test_cost_optimization_free_source(self):
        """测试成本优化 (免费源优先)"""
        router = SmartRouter()

        # 免费数据源
        free_endpoint = {
            "endpoint_name": "free_source",
            "source_type": "akshare",
            "cost": {"is_free": True},
        }

        # 付费数据源
        paid_endpoint = {
            "endpoint_name": "paid_source",
            "source_type": "tushare",
            "cost": {"is_free": False},
        }

        # 免费源应该得到更高的成本评分
        free_score = router._adjust_by_cost(free_endpoint)
        paid_score = router._adjust_by_cost(paid_endpoint)

        assert free_score > paid_score

    def test_load_balancing(self):
        """测试负载均衡"""
        router = SmartRouter()

        # 增加负载
        for i in range(5):
            router.record_call("busy_endpoint", latency=0.1, success=True)

        # 空闲端点应该得到更高的负载评分
        busy_score = router._adjust_by_load("busy_endpoint")
        idle_score = router._adjust_by_load("idle_endpoint")

        assert idle_score > busy_score

    def test_location_awareness(self):
        """测试地域感知"""
        router = SmartRouter()

        endpoint = {
            "endpoint_name": "local_endpoint",
            "location": "beijing",
        }

        # 同地域应该得到更高的地域评分
        local_score = router._adjust_by_location(endpoint, "beijing")
        remote_score = router._adjust_by_location(endpoint, "shanghai")

        assert local_score > remote_score

    def test_multi_dimensional_routing(self):
        """测试多维度综合评分"""
        router = SmartRouter(
            performance_weight=0.4,
            cost_weight=0.3,
            load_weight=0.2,
            location_weight=0.1,
        )

        endpoints = [
            {
                "endpoint_name": "free_fast_local",
                "source_type": "akshare",
                "cost": {"is_free": True},
                "location": "beijing",
            },
            {
                "endpoint_name": "paid_slow_remote",
                "source_type": "tushare",
                "cost": {"is_free": False},
                "location": "shanghai",
            },
        ]

        # 记录性能数据
        router.record_call("free_fast_local", latency=0.05, success=True)
        router.record_call("paid_slow_remote", latency=0.5, success=True)

        # 路由决策
        selected = router.route(endpoints, "DAILY_KLINE", "beijing")

        # 应该选择免费+快速+本地的端点
        assert selected is not None
        assert selected["endpoint_name"] == "free_fast_local"

    def test_get_stats(self):
        """测试获取统计信息"""
        router = SmartRouter()

        # 记录一些调用
        for i in range(5):
            router.record_call("test_endpoint", latency=0.1 + i * 0.01, success=True)
        router.record_call_complete("test_endpoint")

        # 获取统计
        stats = router.get_stats("test_endpoint")

        assert stats["endpoint_name"] == "test_endpoint"
        assert stats["call_count"] == 5
        assert stats["avg_latency"] > 0
        assert stats["success_rate"] == 1.0

    def test_get_all_stats(self):
        """测试获取所有统计信息"""
        router = SmartRouter()

        # 记录多个端点的调用
        router.record_call("endpoint1", latency=0.1, success=True)
        router.record_call("endpoint2", latency=0.2, success=True)

        # 获取所有统计
        all_stats = router.get_all_stats()

        assert "endpoint1" in all_stats
        assert "endpoint2" in all_stats
        assert len(all_stats) == 2

    def test_reset_stats(self):
        """测试重置统计"""
        router = SmartRouter()

        # 记录调用
        router.record_call("test_endpoint", latency=0.1, success=True)

        # 重置
        router.reset_stats("test_endpoint")

        # 验证已重置
        stats = router.get_stats("test_endpoint")
        assert stats["call_count"] == 0

    def test_percentile_calculation(self):
        """测试百分位数计算"""
        router = SmartRouter()

        # 记录不同延迟的调用
        latencies = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]

        for latency in latencies:
            router.record_call("test_endpoint", latency=latency, success=True)

        # 获取统计
        stats = router.get_stats("test_endpoint")

        # 验证百分位数
        assert stats["p50_latency"] > 0
        assert stats["p95_latency"] > stats["p50_latency"]
        assert stats["p99_latency"] >= stats["p95_latency"]

    def test_empty_endpoints(self):
        """测试空端点列表"""
        router = SmartRouter()

        selected = router.route([], "DAILY_KLINE")

        assert selected is None

    def test_single_endpoint(self):
        """测试单个端点"""
        router = SmartRouter()

        endpoints = [
            {
                "endpoint_name": "only_endpoint",
                "source_type": "akshare",
            }
        ]

        selected = router.route(endpoints, "DAILY_KLINE")

        assert selected is not None
        assert selected["endpoint_name"] == "only_endpoint"

    def test_concurrent_routing(self):
        """测试并发路由决策"""
        import threading

        router = SmartRouter()
        errors = []

        def worker(worker_id):
            try:
                endpoints = [
                    {
                        "endpoint_name": f"endpoint_{worker_id}",
                        "source_type": "akshare",
                        "cost": {"is_free": True},
                    }
                ]

                selected = router.route(endpoints, "DAILY_KLINE")
                assert selected is not None

            except Exception as e:
                errors.append((worker_id, e))

        # 启动 10 个并发线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 验证没有错误
        assert len(errors) == 0
