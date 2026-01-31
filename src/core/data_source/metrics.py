"""
Prometheus 监控指标模块

为数据源管理提供 Prometheus 指标采集和暴露。
"""

import logging
import time
from functools import wraps
from typing import Optional

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not available, metrics disabled")

logger = logging.getLogger(__name__)


class DataSourceMetrics:
    """
    数据源 Prometheus 指标收集器

    指标:
    - datasource_api_latency_seconds: API 调用延迟 (Histogram)
    - datasource_api_calls_total: API 调用总数 (Counter)
    - datasource_data_quality: 数据质量评分 (Gauge)
    - datasource_cache_hits_total: 缓存命中次数 (Counter)
    - datasource_cache_misses_total: 缓存未命中次数 (Counter)
    - datasource_circuit_breaker_state: 熔断器状态 (Gauge)
    - datasource_api_cost_estimated: 估算的 API 成本 (Gauge)
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        初始化指标收集器

        Args:
            registry: Prometheus Registry，None 使用全局 registry
        """
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus metrics disabled (prometheus_client not installed)")
            self.enabled = False
            return

        self.enabled = True
        self.registry = registry or CollectorRegistry()

        # 定义指标
        self._setup_metrics()

        logger.info("DataSourceMetrics initialized (Prometheus enabled)")

    def _setup_metrics(self):
        """设置所有 Prometheus 指标"""

        # 1. API 调用延迟 (Histogram)
        self.api_latency = Histogram(
            "datasource_api_latency_seconds",
            "Data source API call latency in seconds",
            ["endpoint", "data_category"],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        # 2. API 调用总数 (Counter)
        self.api_calls_total = Counter(
            "datasource_api_calls_total",
            "Total number of data source API calls",
            ["endpoint", "data_category", "status"],  # status: success/failure
            registry=self.registry,
        )

        # 3. 数据质量评分 (Gauge)
        self.data_quality = Gauge(
            "datasource_data_quality",
            "Data quality score (0-100)",
            ["endpoint", "check_type"],  # check_type: logic/business/statistical/cross_source
            registry=self.registry,
        )

        # 4. 缓存命中次数 (Counter)
        self.cache_hits_total = Counter(
            "datasource_cache_hits_total",
            "Total number of cache hits",
            ["endpoint"],
            registry=self.registry,
        )

        # 5. 缓存未命中次数 (Counter)
        self.cache_misses_total = Counter(
            "datasource_cache_misses_total",
            "Total number of cache misses",
            ["endpoint"],
            registry=self.registry,
        )

        # 6. 熔断器状态 (Gauge)
        self.circuit_breaker_state = Gauge(
            "datasource_circuit_breaker_state",
            "Circuit breaker state (0=CLOSED, 1=OPEN, 2=HALF_OPEN)",
            ["endpoint"],
            registry=self.registry,
        )

        # 7. 估算的 API 成本 (Gauge)
        self.api_cost_estimated = Gauge(
            "datasource_api_cost_estimated",
            "Estimated API cost in CNY",
            ["endpoint"],
            registry=self.registry,
        )

    def record_api_call(
        self,
        endpoint: str,
        data_category: str,
        latency: float,
        success: bool,
        cost: float = 0.0,
    ):
        """
        记录 API 调用

        Args:
            endpoint: 数据源端点名称
            data_category: 数据分类
            latency: 调用延迟 (秒)
            success: 是否成功
            cost: 估算的成本 (元)
        """
        if not self.enabled:
            return

        status = "success" if success else "failure"

        # 记录延迟
        self.api_latency.labels(endpoint=endpoint, data_category=data_category).observe(latency)

        # 记录调用数
        self.api_calls_total.labels(endpoint=endpoint, data_category=data_category, status=status).inc()

        # 记录成本
        if cost > 0:
            self.api_cost_estimated.labels(endpoint=endpoint).set(cost)

        logger.debug("Recorded API call: {endpoint}, latency={latency:.3f}s, " f"status={status}, cost={cost:.4f}")

    def record_cache_hit(self, endpoint: str):
        """
        记录缓存命中

        Args:
            endpoint: 数据源端点名称
        """
        if not self.enabled:
            return

        self.cache_hits_total.labels(endpoint=endpoint).inc()
        logger.debug("Recorded cache hit: %(endpoint)s")

    def record_cache_miss(self, endpoint: str):
        """
        记录缓存未命中

        Args:
            endpoint: 数据源端点名称
        """
        if not self.enabled:
            return

        self.cache_misses_total.labels(endpoint=endpoint).inc()
        logger.debug("Recorded cache miss: %(endpoint)s")

    def record_data_quality(self, endpoint: str, check_type: str, quality_score: float):
        """
        记录数据质量评分

        Args:
            endpoint: 数据源端点名称
            check_type: 检查类型 (logic/business/statistical/cross_source)
            quality_score: 质量评分 (0-100)
        """
        if not self.enabled:
            return

        self.data_quality.labels(endpoint=endpoint, check_type=check_type).set(quality_score)
        logger.debug("Recorded data quality: %(endpoint)s, %(check_type)s=%(quality_score)s")

    def record_circuit_breaker_state(self, endpoint: str, state: int):
        """
        记录熔断器状态

        Args:
            endpoint: 数据源端点名称
            state: 状态 (0=CLOSED, 1=OPEN, 2=HALF_OPEN)
        """
        if not self.enabled:
            return

        self.circuit_breaker_state.labels(endpoint=endpoint).set(state)
        logger.debug("Recorded circuit breaker state: %(endpoint)s=%(state)s")

    def get_cache_hit_rate(self, endpoint: str) -> float:
        """
        计算缓存命中率

        Args:
            endpoint: 数据源端点名称

        Returns:
            缓存命中率 (0.0-1.0)
        """
        if not self.enabled:
            return 0.0

        hits = self.cache_hits_total.labels(endpoint=endpoint)._value.get()
        misses = self.cache_misses_total.labels(endpoint=endpoint)._value.get()

        total = hits + misses
        if total == 0:
            return 0.0

        return hits / total

    def get_api_success_rate(self, endpoint: str, data_category: str) -> float:
        """
        计算 API 成功率

        Args:
            endpoint: 数据源端点名称
            data_category: 数据分类

        Returns:
            成功率 (0.0-1.0)
        """
        if not self.enabled:
            return 0.0

        success_calls = (
            self.api_calls_total.labels(endpoint=endpoint, data_category=data_category, status="success")._value.get()
            or 0
        )
        failure_calls = (
            self.api_calls_total.labels(endpoint=endpoint, data_category=data_category, status="failure")._value.get()
            or 0
        )

        total = success_calls + failure_calls
        if total == 0:
            return 0.0

        return success_calls / total

    def get_avg_latency(self, endpoint: str, data_category: str) -> float:
        """
        获取平均延迟

        Args:
            endpoint: 数据源端点名称
            data_category: 数据分类

        Returns:
            平均延迟 (秒)
        """
        if not self.enabled:
            return 0.0

        # 从 Histogram 获取样本数和总和
        histogram = self.api_latency.labels(endpoint=endpoint, data_category=data_category)
        samples = histogram._value.get()

        if not samples or samples.sum == 0:
            return 0.0

        return samples.sum / samples.count

    def generate_metrics(self) -> bytes:
        """
        生成 Prometheus 指标文本格式

        Returns:
            Prometheus exposition format bytes
        """
        if not self.enabled:
            return b""

        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """
        获取指标内容类型

        Returns:
            Content-Type header value
        """
        return CONTENT_TYPE_LATEST

    def reset_metrics(self):
        """重置所有指标"""
        if not self.enabled:
            return

        # 清空所有指标
        for metric in [
            self.api_calls_total,
            self.cache_hits_total,
            self.cache_misses_total,
        ]:
            metric.clear()

        logger.info("All metrics reset")


# 全局指标实例
_global_metrics: Optional[DataSourceMetrics] = None


def get_metrics() -> DataSourceMetrics:
    """
    获取全局指标实例

    Returns:
        DataSourceMetrics 实例
    """
    global _global_metrics

    if _global_metrics is None:
        _global_metrics = DataSourceMetrics()

    return _global_metrics


def track_api_call(metrics: Optional[DataSourceMetrics] = None):
    """
    装饰器: 自动跟踪 API 调用

    Args:
        metrics: DataSourceMetrics 实例，None 使用全局实例

    使用示例:
        @track_api_call()
        def fetch_data(endpoint, data_category):
            # ... 调用逻辑
            return data

        # 返回值必须是包含以下字段的字典:
        # {
        #     "endpoint": "endpoint_name",
        #     "data_category": "DAILY_KLINE",
        #     "latency": 0.123,
        #     "success": True,
        #     "cost": 0.01,
        # }
    """

    if metrics is None:
        metrics = get_metrics()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not metrics.enabled:
                return func(*args, **kwargs)

            start_time = time.time()
            endpoint = kwargs.get("endpoint", "unknown")
            data_category = kwargs.get("data_category", "unknown")

            try:
                result = func(*args, **kwargs)

                # 计算延迟
                latency = time.time() - start_time

                # 记录成功调用
                success = True
                cost = result.get("cost", 0.0) if isinstance(result, dict) else 0.0

                metrics.record_api_call(
                    endpoint=endpoint,
                    data_category=data_category,
                    latency=latency,
                    success=success,
                    cost=cost,
                )

                return result

            except Exception as e:
                # 计算延迟
                latency = time.time() - start_time

                # 记录失败调用
                metrics.record_api_call(
                    endpoint=endpoint,
                    data_category=data_category,
                    latency=latency,
                    success=False,
                )

                raise e

        return wrapper

    return decorator
