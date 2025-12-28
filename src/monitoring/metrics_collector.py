"""
自定义监控指标收集器
Prometheus指标定义和收集

功能：
- 定义所有业务、技术和告警指标
- 提供统一的指标收集接口
- 支持自定义指标的实时更新

作者：Claude
创建日期：2025-11-12
版本：1.0.0
"""

import logging
from typing import Dict, List, Optional, Any
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CollectorRegistry,
)

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    统一的指标收集器

    管理所有Prometheus指标的定义和收集，
    提供统一的接口用于应用程序的各个部分。
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        初始化指标收集器

        Args:
            registry: Prometheus注册表（可选，默认使用全局）
        """
        self.registry = registry or CollectorRegistry()
        self._metrics: Dict[str, Any] = {}
        self._initialize_metrics()
        logger.info("✅ MetricsCollector initialized")

    def _initialize_metrics(self):
        """初始化所有指标"""
        self._initialize_api_metrics()
        self._initialize_websocket_metrics()
        self._initialize_cache_metrics()
        self._initialize_database_metrics()
        self._initialize_business_metrics()
        self._initialize_alerting_metrics()
        logger.info("✅ Initialized %s metrics", len(self._metrics))

    # ==================== API 指标 ====================

    def _initialize_api_metrics(self):
        """初始化API相关指标"""
        self._metrics["http_requests_total"] = Counter(
            "mystocks_http_requests_total",
            "HTTP请求总数",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self._metrics["http_request_duration_seconds"] = Histogram(
            "mystocks_http_request_duration_seconds",
            "HTTP请求延迟",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        self._metrics["api_error_rate"] = Gauge(
            "mystocks_api_error_rate",
            "API错误率",
            ["endpoint", "error_type"],
            registry=self.registry,
        )

        logger.info("✅ API metrics initialized")

    # ==================== WebSocket 指标 ====================

    def _initialize_websocket_metrics(self):
        """初始化WebSocket相关指标"""
        self._metrics["websocket_connections_active"] = Gauge(
            "mystocks_websocket_connections_active",
            "活跃WebSocket连接数",
            ["namespace", "version"],
            registry=self.registry,
        )

        self._metrics["websocket_messages_sent_total"] = Counter(
            "mystocks_websocket_messages_sent_total",
            "WebSocket消息发送总数",
            ["message_type", "namespace"],
            registry=self.registry,
        )

        self._metrics["websocket_messages_received_total"] = Counter(
            "mystocks_websocket_messages_received_total",
            "WebSocket消息接收总数",
            ["message_type"],
            registry=self.registry,
        )

        self._metrics["websocket_connection_errors_total"] = Counter(
            "mystocks_websocket_connection_errors_total",
            "WebSocket连接错误总数",
            ["error_type"],
            registry=self.registry,
        )

        logger.info("✅ WebSocket metrics initialized")

    # ==================== 缓存指标 ====================

    def _initialize_cache_metrics(self):
        """初始化缓存相关指标"""
        self._metrics["cache_hits_total"] = Counter(
            "mystocks_cache_hits_total",
            "缓存命中总数",
            ["cache_type", "key_pattern"],
            registry=self.registry,
        )

        self._metrics["cache_misses_total"] = Counter(
            "mystocks_cache_misses_total",
            "缓存未命中总数",
            ["cache_type", "key_pattern"],
            registry=self.registry,
        )

        self._metrics["cache_hit_rate"] = Gauge(
            "mystocks_cache_hit_rate",
            "缓存命中率",
            ["cache_type"],
            registry=self.registry,
        )

        self._metrics["cache_evictions_total"] = Counter(
            "mystocks_cache_evictions_total",
            "缓存驱逐总数",
            ["cache_type", "reason"],
            registry=self.registry,
        )

        self._metrics["cache_memory_usage_bytes"] = Gauge(
            "mystocks_cache_memory_usage_bytes",
            "缓存内存使用量",
            ["cache_type"],
            registry=self.registry,
        )

        logger.info("✅ Cache metrics initialized")

    # ==================== 数据库指标 ====================

    def _initialize_database_metrics(self):
        """初始化数据库相关指标"""
        self._metrics["db_connections_active"] = Gauge(
            "mystocks_db_connections_active",
            "活跃数据库连接数",
            ["database", "pool_name"],
            registry=self.registry,
        )

        self._metrics["db_connections_idle"] = Gauge(
            "mystocks_db_connections_idle",
            "空闲数据库连接数",
            ["database", "pool_name"],
            registry=self.registry,
        )

        self._metrics["db_connections_total"] = Gauge(
            "mystocks_db_connections_total",
            "数据库总连接数",
            ["database"],
            registry=self.registry,
        )

        self._metrics["db_query_duration_seconds"] = Histogram(
            "mystocks_db_query_duration_seconds",
            "数据库查询延迟",
            ["database", "query_type", "table"],
            buckets=[0.001, 0.01, 0.1, 1.0, 5.0, 10.0],
            registry=self.registry,
        )

        self._metrics["db_connection_errors_total"] = Counter(
            "mystocks_db_connection_errors_total",
            "数据库连接错误总数",
            ["database", "error_type"],
            registry=self.registry,
        )

        self._metrics["db_slow_queries_total"] = Counter(
            "mystocks_db_slow_queries_total",
            "慢查询总数",
            ["database", "table"],
            registry=self.registry,
        )

        self._metrics["db_query_errors_total"] = Counter(
            "mystocks_db_query_errors_total",
            "数据库查询错误总数",
            ["database", "error_type"],
            registry=self.registry,
        )

        logger.info("✅ Database metrics initialized")

    # ==================== 业务指标 ====================

    def _initialize_business_metrics(self):
        """初始化业务相关指标"""
        # 市场数据相关指标
        self._metrics["market_data_points_processed"] = Counter(
            "mystocks_market_data_points_processed",
            "已处理的市场数据点数",
            ["datasource", "data_type"],
            registry=self.registry,
        )

        self._metrics["market_data_latency_seconds"] = Histogram(
            "mystocks_market_data_latency_seconds",
            "市场数据处理延迟",
            ["datasource", "data_type"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        self._metrics["daily_kline_update_count"] = Counter(
            "mystocks_daily_kline_update_count",
            "日线数据更新数",
            ["data_source"],
            registry=self.registry,
        )

        self._metrics["tick_data_write_rate"] = Gauge(
            "mystocks_tick_data_write_rate",
            "Tick数据写入速率",
            ["database"],
            registry=self.registry,
        )

        # 用户行为相关指标
        self._metrics["user_portfolio_updates_total"] = Counter(
            "mystocks_user_portfolio_updates_total",
            "用户组合更新总数",
            ["user_id", "action"],
            registry=self.registry,
        )

        self._metrics["user_watch_list_changes_total"] = Counter(
            "mystocks_user_watch_list_changes_total",
            "自选股列表变更总数",
            ["user_id", "action"],
            registry=self.registry,
        )

        self._metrics["user_active_sessions"] = Gauge(
            "mystocks_user_active_sessions",
            "活跃用户会话数",
            ["platform"],
            registry=self.registry,
        )

        # 交易相关指标
        self._metrics["trade_orders_total"] = Counter(
            "mystocks_trade_orders_total",
            "交易订单总数",
            ["order_type", "status"],
            registry=self.registry,
        )

        self._metrics["trade_order_latency_seconds"] = Histogram(
            "mystocks_trade_order_latency_seconds",
            "订单处理延迟",
            ["order_type"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0],
            registry=self.registry,
        )

        logger.info("✅ Business metrics initialized")

    # ==================== 告警指标 ====================

    def _initialize_alerting_metrics(self):
        """初始化告警和系统健康指标"""
        self._metrics["alerts_fired_total"] = Counter(
            "mystocks_alerts_fired_total",
            "告警触发总数",
            ["alert_name", "severity"],
            registry=self.registry,
        )

        self._metrics["alerts_active"] = Gauge(
            "mystocks_alerts_active",
            "当前活跃告警数",
            ["severity"],
            registry=self.registry,
        )

        self._metrics["alert_resolution_time_seconds"] = Histogram(
            "mystocks_alert_resolution_time_seconds",
            "告警解决时间",
            ["alert_name"],
            buckets=[60, 300, 900, 3600, 86400],
            registry=self.registry,
        )

        self._metrics["health_status"] = Gauge(
            "mystocks_health_status",
            "系统健康状态 (1=healthy, 0=unhealthy)",
            ["component", "status_type"],
            registry=self.registry,
        )

        self._metrics["dependency_availability"] = Gauge(
            "mystocks_dependency_availability",
            "依赖项可用性 (%)",
            ["dependency_name"],
            registry=self.registry,
        )

        # 系统资源指标
        self._metrics["process_memory_usage_bytes"] = Gauge(
            "mystocks_process_memory_usage_bytes",
            "进程内存使用量",
            ["component"],
            registry=self.registry,
        )

        self._metrics["process_cpu_usage_percentage"] = Gauge(
            "mystocks_process_cpu_usage_percentage",
            "进程CPU使用率",
            ["component"],
            registry=self.registry,
        )

        self._metrics["system_uptime_seconds"] = Gauge(
            "mystocks_system_uptime_seconds",
            "系统运行时间",
            ["service"],
            registry=self.registry,
        )

        # 数据质量指标
        self._metrics["data_completeness_percentage"] = Gauge(
            "mystocks_data_completeness_percentage",
            "数据完整性百分比",
            ["data_type", "source"],
            registry=self.registry,
        )

        self._metrics["data_freshness_minutes"] = Gauge(
            "mystocks_data_freshness_minutes",
            "数据新鲜度（距最后更新时间）",
            ["data_type"],
            registry=self.registry,
        )

        self._metrics["data_anomalies_detected"] = Counter(
            "mystocks_data_anomalies_detected",
            "检测到的数据异常数",
            ["data_type", "anomaly_type"],
            registry=self.registry,
        )

        logger.info("✅ Alerting metrics initialized")

    # ==================== 公共方法 ====================

    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_seconds: float,
    ):
        """记录API请求"""
        self._metrics["http_requests_total"].labels(method=method, endpoint=endpoint, status=status_code).inc()
        self._metrics["http_request_duration_seconds"].labels(method=method, endpoint=endpoint).observe(
            duration_seconds
        )

    def record_websocket_connection(self, namespace: str, version: str, count: int):
        """更新WebSocket活跃连接数"""
        self._metrics["websocket_connections_active"].labels(namespace=namespace, version=version).set(count)

    def record_websocket_message(self, message_type: str, namespace: str, sent: bool = True):
        """记录WebSocket消息"""
        metric_name = "websocket_messages_sent_total" if sent else "websocket_messages_received_total"
        if sent:
            self._metrics[metric_name].labels(message_type=message_type, namespace=namespace).inc()
        else:
            self._metrics[metric_name].labels(message_type=message_type).inc()

    def record_cache_hit(self, cache_type: str, key_pattern: str):
        """记录缓存命中"""
        self._metrics["cache_hits_total"].labels(cache_type=cache_type, key_pattern=key_pattern).inc()

    def record_cache_miss(self, cache_type: str, key_pattern: str):
        """记录缓存未命中"""
        self._metrics["cache_misses_total"].labels(cache_type=cache_type, key_pattern=key_pattern).inc()

    def update_cache_hit_rate(self, cache_type: str, hit_rate: float):
        """更新缓存命中率"""
        self._metrics["cache_hit_rate"].labels(cache_type=cache_type).set(hit_rate)

    def update_db_connections(
        self,
        database: str,
        pool_name: str,
        active: int,
        idle: int,
    ):
        """更新数据库连接状态"""
        self._metrics["db_connections_active"].labels(database=database, pool_name=pool_name).set(active)
        self._metrics["db_connections_idle"].labels(database=database, pool_name=pool_name).set(idle)
        self._metrics["db_connections_total"].labels(database=database).set(active + idle)

    def record_db_query(
        self,
        database: str,
        query_type: str,
        table: str,
        duration_seconds: float,
    ):
        """记录数据库查询"""
        self._metrics["db_query_duration_seconds"].labels(
            database=database, query_type=query_type, table=table
        ).observe(duration_seconds)

    def record_market_data(
        self,
        datasource: str,
        data_type: str,
        points: int,
        latency_seconds: float,
    ):
        """记录市场数据处理"""
        self._metrics["market_data_points_processed"].labels(datasource=datasource, data_type=data_type).inc(points)
        self._metrics["market_data_latency_seconds"].labels(datasource=datasource, data_type=data_type).observe(
            latency_seconds
        )

    def record_alert(self, alert_name: str, severity: str):
        """记录告警触发"""
        self._metrics["alerts_fired_total"].labels(alert_name=alert_name, severity=severity).inc()

    def update_health_status(
        self,
        component: str,
        status_type: str,
        is_healthy: bool,
    ):
        """更新组件健康状态"""
        status_value = 1 if is_healthy else 0
        self._metrics["health_status"].labels(component=component, status_type=status_type).set(status_value)

    def update_dependency_availability(
        self,
        dependency_name: str,
        availability_percentage: float,
    ):
        """更新依赖项可用性"""
        self._metrics["dependency_availability"].labels(dependency_name=dependency_name).set(availability_percentage)

    def get_metrics(self) -> Dict[str, Any]:
        """获取所有已定义的指标"""
        return self._metrics

    def get_metric_names(self) -> List[str]:
        """获取所有指标名称"""
        return list(self._metrics.keys())

    def get_registry(self) -> CollectorRegistry:
        """获取Prometheus注册表"""
        return self.registry


# 全局指标收集器实例（单例）
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# 便捷函数
def record_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_seconds: float,
):
    """便捷函数：记录API请求"""
    get_metrics_collector().record_api_request(method, endpoint, status_code, duration_seconds)


def record_cache_operation(
    cache_type: str,
    key_pattern: str,
    is_hit: bool,
):
    """便捷函数：记录缓存操作"""
    collector = get_metrics_collector()
    if is_hit:
        collector.record_cache_hit(cache_type, key_pattern)
    else:
        collector.record_cache_miss(cache_type, key_pattern)


def record_db_query(
    database: str,
    query_type: str,
    table: str,
    duration_seconds: float,
):
    """便捷函数：记录数据库查询"""
    get_metrics_collector().record_db_query(database, query_type, table, duration_seconds)


if __name__ == "__main__":
    """测试指标收集器"""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    collector = get_metrics_collector()
    print("\n✅ MetricsCollector initialized")
    print(f"Total metrics: {len(collector.get_metric_names())}")
    print("\nMetrics list:\n")
    for name in sorted(collector.get_metric_names()):
        print(f"  • {name}")
