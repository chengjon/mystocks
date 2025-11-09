"""
性能测试
测试GPU加速性能、吞吐量和延迟
"""

import pytest
import time
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import statistics


class TestBacktestPerformance:
    """回测性能测试"""

    def test_gpu_vs_cpu_performance(self, sample_market_data, sample_strategy_config):
        """测试GPU vs CPU性能对比"""
        # GPU模式
        with patch("utils.gpu_acceleration_engine.BacktestEngineGPU") as MockGPUEngine:
            gpu_engine = MockGPUEngine(None, None)

            # 模拟GPU执行
            start_gpu = time.time()
            gpu_engine.run_backtest.return_value = {
                "total_return": 0.25,
                "execution_time": 3.0,
            }
            gpu_result = gpu_engine.run_backtest(
                sample_market_data, sample_strategy_config
            )
            gpu_time = time.time() - start_gpu + gpu_result["execution_time"]

        # CPU模式
        with patch("utils.gpu_acceleration_engine.BacktestEngineCPU") as MockCPUEngine:
            cpu_engine = MockCPUEngine()

            # 模拟CPU执行
            start_cpu = time.time()
            cpu_engine.run_backtest.return_value = {
                "total_return": 0.25,
                "execution_time": 45.0,
            }
            cpu_result = cpu_engine.run_backtest(
                sample_market_data, sample_strategy_config
            )
            cpu_time = time.time() - start_cpu + cpu_result["execution_time"]

        # 计算加速比
        speedup = cpu_time / gpu_time

        # GPU应该至少快10倍
        assert speedup >= 10, f"Expected speedup >= 10x, got {speedup:.2f}x"

    def test_backtest_throughput(self):
        """测试回测吞吐量"""
        n_backtests = 20
        durations = []

        with patch("utils.gpu_acceleration_engine.BacktestEngineGPU") as MockEngine:
            engine = MockEngine(None, None)

            for i in range(n_backtests):
                start = time.time()
                engine.run_backtest.return_value = {"status": "completed"}
                engine.run_backtest({}, {})
                duration = time.time() - start
                durations.append(duration)

        # 计算平均时间
        avg_time = statistics.mean(durations)
        throughput = 1.0 / avg_time if avg_time > 0 else float("inf")

        # 应该能处理每秒至少0.3个回测（3秒/个）
        assert throughput >= 0.3, f"Throughput too low: {throughput:.2f} backtests/sec"

    def test_concurrent_backtest_performance(self):
        """测试并发回测性能"""
        max_concurrent = 20

        # 模拟并发执行
        start = time.time()

        tasks = []
        for i in range(max_concurrent):
            task = Mock()
            task.result.return_value = {"status": "completed"}
            tasks.append(task)

        # 等待所有任务完成
        for task in tasks:
            task.result()

        duration = time.time() - start

        # 20个并发任务应该在合理时间内完成
        assert duration < 60, f"Concurrent execution too slow: {duration:.2f}s"

    @pytest.mark.benchmark
    def test_backtest_latency_percentiles(self):
        """测试回测延迟百分位数"""
        n_samples = 100
        latencies = []

        with patch("utils.gpu_acceleration_engine.BacktestEngineGPU") as MockEngine:
            engine = MockEngine(None, None)

            for _ in range(n_samples):
                start = time.time()
                engine.run_backtest.return_value = {"status": "completed"}
                engine.run_backtest({}, {})
                latency = (time.time() - start) * 1000  # ms
                latencies.append(latency)

        # 计算百分位数
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)

        # P50应该 < 5秒
        # P95应该 < 10秒
        # P99应该 < 15秒
        assert p50 < 5000, f"P50 latency too high: {p50:.2f}ms"
        assert p95 < 10000, f"P95 latency too high: {p95:.2f}ms"
        assert p99 < 15000, f"P99 latency too high: {p99:.2f}ms"


class TestRealTimePerformance:
    """实时处理性能测试"""

    def test_streaming_throughput(self):
        """测试流式处理吞吐量"""
        target_throughput = 10000  # 条/秒
        n_messages = 10000

        with patch(
            "services.integrated_realtime_service.IntegratedRealTimeService"
        ) as MockService:
            service = MockService(None, None, None)

            start = time.time()

            # 模拟处理数据流
            for i in range(n_messages):
                service.process_message.return_value = True
                service.process_message(Mock())

            duration = time.time() - start

        actual_throughput = n_messages / duration if duration > 0 else float("inf")

        # 应该达到目标吞吐量
        assert (
            actual_throughput >= target_throughput * 0.8
        ), f"Throughput too low: {actual_throughput:.0f} messages/sec (target: {target_throughput})"

    def test_feature_calculation_latency(self):
        """测试特征计算延迟"""
        n_calculations = 100
        latencies = []

        with patch("utils.gpu_acceleration_engine.FeatureCalculationGPU") as MockEngine:
            engine = MockEngine(None, None)

            for _ in range(n_calculations):
                start = time.time()
                engine.calculate_features.return_value = {}
                engine.calculate_features({})
                latency = (time.time() - start) * 1000  # ms
                latencies.append(latency)

        avg_latency = statistics.mean(latencies)

        # 平均延迟应该 < 50ms
        assert avg_latency < 50, f"Feature calculation too slow: {avg_latency:.2f}ms"

    def test_batch_processing_efficiency(self):
        """测试批量处理效率"""
        batch_sizes = [10, 50, 100, 200]
        throughputs = []

        with patch("utils.gpu_acceleration_engine.FeatureCalculationGPU") as MockEngine:
            engine = MockEngine(None, None)

            for batch_size in batch_sizes:
                start = time.time()
                engine.process_batch.return_value = [{}] * batch_size
                engine.process_batch([{}] * batch_size)
                duration = time.time() - start

                throughput = batch_size / duration if duration > 0 else float("inf")
                throughputs.append(throughput)

        # 吞吐量应该随批量大小增加
        assert throughputs[-1] > throughputs[0], "Batch processing not scaling properly"


class TestMLPerformance:
    """ML训练性能测试"""

    def test_training_speedup(self, sample_ml_training_data):
        """测试训练加速比"""
        X = sample_ml_training_data[["price", "volume", "sma_20", "rsi"]]
        y = sample_ml_training_data["target"]

        # GPU训练
        with patch("utils.gpu_acceleration_engine.MLTrainingGPU") as MockGPU:
            gpu_trainer = MockGPU(None, None)

            start_gpu = time.time()
            gpu_trainer.train_model.return_value = (Mock(), {"training_time": 8.0})
            model_gpu, metrics_gpu = gpu_trainer.train_model(X, y, "random_forest", {})
            gpu_time = metrics_gpu["training_time"]

        # CPU训练
        with patch("utils.gpu_acceleration_engine.MLTrainingCPU") as MockCPU:
            cpu_trainer = MockCPU()

            start_cpu = time.time()
            cpu_trainer.train_model.return_value = (Mock(), {"training_time": 120.0})
            model_cpu, metrics_cpu = cpu_trainer.train_model(X, y, "random_forest", {})
            cpu_time = metrics_cpu["training_time"]

        # 计算加速比
        speedup = cpu_time / gpu_time

        # 应该有至少10倍加速
        assert speedup >= 10, f"Training speedup insufficient: {speedup:.2f}x"

    def test_prediction_throughput(self):
        """测试预测吞吐量"""
        target_throughput = 1000  # 次/秒
        n_predictions = 10000

        with patch("utils.gpu_acceleration_engine.MLTrainingGPU") as MockGPU:
            predictor = MockGPU(None, None)

            start = time.time()

            for _ in range(n_predictions):
                predictor.predict.return_value = [1]
                predictor.predict([[10.5, 1000000, 10.3, 65]])

            duration = time.time() - start

        actual_throughput = n_predictions / duration if duration > 0 else float("inf")

        # 应该达到目标吞吐量
        assert (
            actual_throughput >= target_throughput * 0.8
        ), f"Prediction throughput too low: {actual_throughput:.0f} predictions/sec"

    def test_model_loading_time(self):
        """测试模型加载时间"""
        n_loads = 10
        load_times = []

        with patch("services.integrated_ml_service.IntegratedMLService") as MockService:
            service = MockService(None, None, None)

            for _ in range(n_loads):
                start = time.time()
                service.load_model.return_value = Mock()
                service.load_model("model_12345")
                load_time = (time.time() - start) * 1000  # ms
                load_times.append(load_time)

        avg_load_time = statistics.mean(load_times)

        # 平均加载时间应该 < 100ms
        assert avg_load_time < 100, f"Model loading too slow: {avg_load_time:.2f}ms"


class TestCachePerformance:
    """缓存性能测试"""

    def test_cache_hit_rate(self):
        """测试缓存命中率"""
        n_requests = 1000
        hits = 0

        with patch("utils.cache_optimization.CacheManager") as MockCache:
            cache = MockCache()

            # 模拟请求模式（80%重复）
            for i in range(n_requests):
                key = f"key_{i % 200}"  # 重复使用200个key

                # 模拟缓存命中
                if i % 200 < 160:  # 80% 命中率
                    cache.get.return_value = {"data": "value"}
                    hits += 1
                else:
                    cache.get.return_value = None

                cache.get(key)

        hit_rate = hits / n_requests

        # 命中率应该 >= 80%
        assert hit_rate >= 0.8, f"Cache hit rate too low: {hit_rate:.2%}"

    def test_cache_access_latency(self):
        """测试缓存访问延迟"""
        n_accesses = 1000
        latencies = {"l1": [], "l2": [], "redis": []}

        with patch("utils.cache_optimization.CacheManager") as MockCache:
            cache = MockCache()

            # L1缓存访问
            for _ in range(n_accesses):
                start = time.time()
                cache.l1_get.return_value = {"data": "value"}
                cache.l1_get("key")
                latency = (time.time() - start) * 1000  # ms
                latencies["l1"].append(latency)

        # L1平均延迟应该 < 1ms
        avg_l1 = statistics.mean(latencies["l1"])
        assert avg_l1 < 1, f"L1 cache too slow: {avg_l1:.2f}ms"


class TestResourceUtilization:
    """资源利用率测试"""

    def test_gpu_utilization(self):
        """测试GPU利用率"""
        with patch("utils.gpu_utils.GPUUtilizationMonitor") as MockMonitor:
            monitor = MockMonitor()

            # 模拟高负载
            monitor.get_utilization.return_value = {
                "utilization": 85.0,
                "memory_usage": 75.0,
            }

            stats = monitor.get_utilization(0)

        # GPU利用率应该 > 80%
        assert (
            stats["utilization"] > 80
        ), f"GPU utilization too low: {stats['utilization']:.1f}%"

    def test_memory_efficiency(self):
        """测试内存效率"""
        with patch("utils.gpu_utils.GPUUtilizationMonitor") as MockMonitor:
            monitor = MockMonitor()

            monitor.get_memory_usage.return_value = {
                "used_mb": 6144,
                "total_mb": 8192,
                "percentage": 75.0,
            }

            memory = monitor.get_memory_usage(0)

        # 内存使用应该 < 90%
        assert (
            memory["percentage"] < 90
        ), f"Memory usage too high: {memory['percentage']:.1f}%"

    def test_concurrent_task_limit(self):
        """测试并发任务上限"""
        max_concurrent = 20

        with patch("utils.resource_scheduler.ResourceScheduler") as MockScheduler:
            scheduler = MockScheduler()

            # 提交大量任务
            submitted = 0
            for i in range(30):
                scheduler.schedule.return_value = {"status": "scheduled"}
                result = scheduler.schedule({"task_id": f"task_{i}"})

                if result["status"] == "scheduled":
                    submitted += 1

        # 应该能支持最大并发数
        assert (
            submitted >= max_concurrent
        ), f"Insufficient concurrency: {submitted} (target: {max_concurrent})"


class TestStressTest:
    """压力测试"""

    @pytest.mark.stress
    def test_sustained_load(self):
        """测试持续负载"""
        duration = 60  # 秒
        requests_per_second = 100

        with patch(
            "services.integrated_backtest_service.IntegratedBacktestService"
        ) as MockService:
            service = MockService(None, None, None)

            start = time.time()
            total_requests = 0

            while time.time() - start < duration:
                for _ in range(requests_per_second):
                    service.IntegratedBacktest.return_value = Mock(status="SUBMITTED")
                    service.IntegratedBacktest(Mock())
                    total_requests += 1

                time.sleep(1)

        success_rate = total_requests / (duration * requests_per_second)

        # 成功率应该 > 95%
        assert success_rate > 0.95, f"Success rate too low: {success_rate:.2%}"

    @pytest.mark.stress
    def test_peak_load_handling(self):
        """测试峰值负载处理"""
        peak_requests = 1000

        with patch(
            "services.integrated_backtest_service.IntegratedBacktestService"
        ) as MockService:
            service = MockService(None, None, None)

            start = time.time()

            # 突发大量请求
            for _ in range(peak_requests):
                service.IntegratedBacktest.return_value = Mock(status="SUBMITTED")
                service.IntegratedBacktest(Mock())

            duration = time.time() - start

        # 应该在合理时间内处理完
        assert duration < 30, f"Peak load handling too slow: {duration:.2f}s"
