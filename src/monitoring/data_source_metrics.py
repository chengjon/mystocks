"""
数据源监控指标导出器（Prometheus）

功能：
1. 定义数据源相关的Prometheus metrics
2. 提供metrics更新接口
3. 暴露/metrics端点给Prometheus抓取

使用方法：
    # 在FastAPI主应用中集成
    from prometheus_client import start_http_server
    from src.monitoring.data_source_metrics import (
        init_metrics, update_call_metrics, update_health_metrics
    )

    # 启动metrics服务器
    start_http_server(8001)  # 暴露在8001端口

    # 在代码中记录metrics
    update_call_metrics("akshare.stock_zh_a_hist", "akshare",
                       success=True, response_time=0.5, record_count=1000)

作者：Claude Code
版本：v2.0
创建时间：2026-01-02
"""

import logging

from prometheus_client import Counter, Gauge, Histogram, Info, start_http_server

logger = logging.getLogger(__name__)

# ============================================================================
# 定义数据源监控指标
# ============================================================================

# 1. 数据源可用性指标
data_source_up = Gauge(
    "data_source_up", "数据源是否可用（1=可用，0=不可用）", ["endpoint_name", "source_name", "data_category"]
)

# 2. 数据源响应时间分布
data_source_response_time = Histogram(
    "data_source_response_time_seconds",
    "数据源响应时间（秒）",
    ["endpoint_name", "source_name"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],  # p50, p95, p99分位数
)

# 3. 数据源调用总次数（按状态分类）
data_source_calls_total = Counter(
    "data_source_calls_total", "数据源调用总次数", ["endpoint_name", "source_name", "status"]  # status=success/failure
)

# 4. 数据源返回记录数
data_source_record_count = Histogram(
    "data_source_record_count",
    "数据源返回记录数",
    ["endpoint_name", "source_name"],
    buckets=[1, 10, 100, 1000, 10000, 100000],
)

# 5. 数据源成功率
data_source_success_rate = Gauge("data_source_success_rate", "数据源成功率（百分比）", ["endpoint_name", "source_name"])

# 6. 数据源健康状态
data_source_health_status = Gauge(
    "data_source_health_status",
    "数据源健康状态（3=healthy，2=degraded，1=failed，0=unknown）",
    ["endpoint_name", "source_name"],
)

# 7. 数据源质量评分
data_source_quality_score = Gauge(
    "data_source_quality_score", "数据源质量评分（0-10）", ["endpoint_name", "source_name"]
)

# 8. 数据源连续失败次数
data_source_consecutive_failures = Gauge(
    "data_source_consecutive_failures", "数据源连续失败次数", ["endpoint_name", "source_name"]
)

# 9. 数据源总调用次数
data_source_total_calls = Gauge("data_source_total_calls", "数据源总调用次数", ["endpoint_name", "source_name"])

# 10. 数据源信息（元数据）
data_source_info = Info("data_source_info", "数据源信息（元数据）", ["endpoint_name", "source_name"])

# ============================================================================
# Metrics更新接口
# ============================================================================


class DataSourceMetricsExporter:
    """数据源监控指标导出器（单例模式）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """初始化导出器"""
        self.initialized_sources = set()
        logger.info("DataSourceMetricsExporter 初始化")

    def init_source_metrics(self, endpoint_name: str, source_name: str, data_category: str, **metadata):
        """
        初始化数据源的metrics和info

        Args:
            endpoint_name: 端点名称
            source_name: 数据源名称
            data_category: 数据分类
            **metadata: 其他元数据
        """
        if endpoint_name in self.initialized_sources:
            return

        # 初始化info（元数据）
        info_data = {
            "data_category": data_category,
            "source_type": metadata.get("source_type", ""),
            "classification_level": str(metadata.get("classification_level", "")),
            "target_db": metadata.get("target_db", ""),
            "table_name": metadata.get("table_name", ""),
            "description": metadata.get("description", ""),
            "version": metadata.get("version", "1.0"),
            "priority": str(metadata.get("priority", "")),
            "status": metadata.get("status", "unknown"),
        }

        data_source_info.labels(endpoint_name=endpoint_name, source_name=source_name).info(info_data)

        # 初始化其他gauge为默认值
        data_source_up.labels(endpoint_name=endpoint_name, source_name=source_name, data_category=data_category).set(
            1
        )  # 初始设为可用

        data_source_health_status.labels(endpoint_name=endpoint_name, source_name=source_name).set(0)  # unknown

        data_source_consecutive_failures.labels(endpoint_name=endpoint_name, source_name=source_name).set(0)

        data_source_total_calls.labels(endpoint_name=endpoint_name, source_name=source_name).set(0)

        self.initialized_sources.add(endpoint_name)
        logger.info("初始化metrics: %(endpoint_name)s")

    def update_call_metrics(
        self,
        endpoint_name: str,
        source_name: str,
        data_category: str,
        success: bool,
        response_time: float,
        record_count: int = None,
        error_msg: str = None,
    ):
        """
        更新调用相关的metrics

        Args:
            endpoint_name: 端点名称
            source_name: 数据源名称
            data_category: 数据分类
            success: 是否成功
            response_time: 响应时间（秒）
            record_count: 返回记录数
            error_msg: 错误信息
        """
        # 确保已初始化
        if endpoint_name not in self.initialized_sources:
            self.init_source_metrics(endpoint_name, source_name, data_category)

        # 更新调用次数
        status = "success" if success else "failure"
        data_source_calls_total.labels(endpoint_name=endpoint_name, source_name=source_name, status=status).inc()

        # 更新响应时间
        if response_time is not None:
            data_source_response_time.labels(endpoint_name=endpoint_name, source_name=source_name).observe(
                response_time
            )

        # 更新记录数
        if record_count is not None and success:
            data_source_record_count.labels(endpoint_name=endpoint_name, source_name=source_name).observe(record_count)

        # 更新可用性
        if success:
            data_source_up.labels(
                endpoint_name=endpoint_name, source_name=source_name, data_category=data_category
            ).set(1)
        else:
            data_source_up.labels(
                endpoint_name=endpoint_name, source_name=source_name, data_category=data_category
            ).set(0)

            logger.error("数据源调用失败: %(endpoint_name)s, 错误: %(error_msg)s")

    def update_health_metrics(
        self,
        endpoint_name: str,
        source_name: str,
        data_category: str,
        health_status: str,
        quality_score: float,
        success_rate: float,
        consecutive_failures: int,
        total_calls: int,
    ):
        """
        更新健康状态相关的metrics

        Args:
            endpoint_name: 端点名称
            source_name: 数据源名称
            data_category: 数据分类
            health_status: 健康状态（healthy/degraded/failed/unknown）
            quality_score: 质量评分
            success_rate: 成功率
            consecutive_failures: 连续失败次数
            total_calls: 总调用次数
        """
        # 确保已初始化
        if endpoint_name not in self.initialized_sources:
            self.init_source_metrics(endpoint_name, source_name, data_category)

        # 更新健康状态（映射为数字）
        status_map = {"healthy": 3, "degraded": 2, "failed": 1, "unknown": 0}
        status_value = status_map.get(health_status, 0)

        data_source_health_status.labels(endpoint_name=endpoint_name, source_name=source_name).set(status_value)

        # 更新质量评分
        data_source_quality_score.labels(endpoint_name=endpoint_name, source_name=source_name).set(quality_score)

        # 更新成功率
        data_source_success_rate.labels(endpoint_name=endpoint_name, source_name=source_name).set(success_rate)

        # 更新连续失败次数
        data_source_consecutive_failures.labels(endpoint_name=endpoint_name, source_name=source_name).set(
            consecutive_failures
        )

        # 更新总调用次数
        data_source_total_calls.labels(endpoint_name=endpoint_name, source_name=source_name).set(total_calls)

        # 根据健康状态更新可用性
        is_up = 1 if health_status != "failed" else 0
        data_source_up.labels(endpoint_name=endpoint_name, source_name=source_name, data_category=data_category).set(
            is_up
        )

    def update_all_from_registry(self, registry_dict: dict):
        """
        从注册表批量更新所有metrics

        Args:
            registry_dict: 注册表字典（{endpoint_name: config, ...}）
        """
        for endpoint_name, source_data in registry_dict.items():
            config = source_data.get("config", {})

            # 更新健康metrics
            self.update_health_metrics(
                endpoint_name=endpoint_name,
                source_name=config.get("source_name", ""),
                data_category=config.get("data_category", ""),
                health_status=config.get("health_status", "unknown"),
                quality_score=config.get("data_quality_score", 0),
                success_rate=config.get("success_rate", 100),
                consecutive_failures=config.get("consecutive_failures", 0),
                total_calls=config.get("total_calls", 0),
            )


# ============================================================================
# 便捷函数
# ============================================================================

# 全局导出器实例
_metrics_exporter = DataSourceMetricsExporter.get_instance()


def init_source_metrics(endpoint_name: str, source_name: str, data_category: str, **metadata):
    """初始化数据源metrics（便捷函数）"""
    _metrics_exporter.init_source_metrics(endpoint_name, source_name, data_category, **metadata)


def update_call_metrics(
    endpoint_name: str,
    source_name: str,
    data_category: str,
    success: bool,
    response_time: float,
    record_count: int = None,
    error_msg: str = None,
):
    """更新调用metrics（便捷函数）"""
    _metrics_exporter.update_call_metrics(
        endpoint_name, source_name, data_category, success, response_time, record_count, error_msg
    )


def update_health_metrics(
    endpoint_name: str,
    source_name: str,
    data_category: str,
    health_status: str,
    quality_score: float,
    success_rate: float,
    consecutive_failures: int,
    total_calls: int,
):
    """更新健康metrics（便捷函数）"""
    _metrics_exporter.update_health_metrics(
        endpoint_name,
        source_name,
        data_category,
        health_status,
        quality_score,
        success_rate,
        consecutive_failures,
        total_calls,
    )


def update_all_from_registry(registry_dict: dict):
    """从注册表批量更新metrics（便捷函数）"""
    _metrics_exporter.update_all_from_registry(registry_dict)


# ============================================================================
# 启动metrics服务器
# ============================================================================


def start_metrics_server(port: int = 8001):
    """
    启动Prometheus metrics HTTP服务器

    Args:
        port: 监听端口（默认8001）

    注意：
    - 此函数会阻塞，应该在单独线程中调用
    - Prometheus将从此端点抓取metrics
    - 默认暴露地址: http://localhost:8001/metrics
    """
    try:
        start_http_server(port)
        logger.info("Prometheus metrics服务器已启动: http://localhost:%(port)s/metrics")
    except Exception:
        logger.error("启动metrics服务器失败: %(e)s")
        raise


if __name__ == "__main__":
    # 测试metrics服务器
    print("启动Prometheus metrics测试服务器...")
    start_metrics_server(8001)
