"""
API监控和指标收集模块
支持请求追踪、性能监控、错误统计和数据质量指标
"""

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class APIMetric:
    """API请求指标"""

    endpoint: str
    method: str
    status_code: int
    response_time: float  # 毫秒
    timestamp: datetime
    error_message: Optional[str] = None
    data_quality_score: Optional[float] = None
    record_count: int = 0


@dataclass
class EndpointStats:
    """端点统计信息"""

    endpoint: str
    total_requests: int = 0
    success_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    error_rate: float = 0.0
    avg_data_quality_score: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None


class APIMonitor:
    """API监控器 - 跟踪API性能和数据质量"""

    def __init__(self, history_limit: int = 10000):
        """初始化监控器

        Args:
            history_limit: 保存的历史指标数量限制
        """
        self.history_limit = history_limit
        self.metrics: List[APIMetric] = []
        self.endpoint_stats: Dict[str, EndpointStats] = {}
        self.lock = threading.RLock()  # 线程安全

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        error_message: Optional[str] = None,
        data_quality_score: Optional[float] = None,
        record_count: int = 0,
    ) -> None:
        """记录API请求"""
        with self.lock:
            metric = APIMetric(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=error_message,
                data_quality_score=data_quality_score,
                record_count=record_count,
            )

            # 添加到历史
            self.metrics.append(metric)

            # 限制历史记录大小
            if len(self.metrics) > self.history_limit:
                self.metrics = self.metrics[-self.history_limit :]

            # 更新统计
            self._update_stats(metric)

            # 日志记录
            log_level = "error" if status_code >= 400 else "info"
            log_func = logger.error if status_code >= 400 else logger.info

            log_func(
                f"{method} {endpoint}",
                status_code=status_code,
                response_time_ms=response_time,
                data_quality_score=data_quality_score,
                record_count=record_count,
                error=error_message,
            )

    def _update_stats(self, metric: APIMetric) -> None:
        """更新端点统计"""
        endpoint = f"{metric.method} {metric.endpoint}"

        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = EndpointStats(endpoint=endpoint)

        stats = self.endpoint_stats[endpoint]
        stats.total_requests += 1

        if metric.status_code < 400:
            stats.success_count += 1
        else:
            stats.error_count += 1
            stats.last_error = metric.error_message
            stats.last_error_time = metric.timestamp

        # 更新响应时间统计
        stats.max_response_time = max(stats.max_response_time, metric.response_time)
        stats.min_response_time = min(stats.min_response_time, metric.response_time)

        # 重新计算平均响应时间
        total_time = sum(m.response_time for m in self.metrics if f"{m.method} {m.endpoint}" == endpoint)
        count = sum(1 for m in self.metrics if f"{m.method} {m.endpoint}" == endpoint)
        stats.avg_response_time = total_time / count if count > 0 else 0

        # 计算错误率
        stats.error_rate = stats.error_count / stats.total_requests if stats.total_requests > 0 else 0

        # 更新数据质量评分
        quality_scores = [
            m.data_quality_score
            for m in self.metrics
            if f"{m.method} {m.endpoint}" == endpoint and m.data_quality_score is not None
        ]
        if quality_scores:
            stats.avg_data_quality_score = sum(quality_scores) / len(quality_scores)

    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, EndpointStats]:
        """获取端点统计"""
        with self.lock:
            if endpoint:
                return {endpoint: self.endpoint_stats.get(endpoint)}
            return dict(self.endpoint_stats)

    def get_metrics(self, endpoint: Optional[str] = None, limit: int = 100) -> List[APIMetric]:
        """获取最近的指标记录"""
        with self.lock:
            if endpoint:
                filtered = [m for m in self.metrics if m.endpoint == endpoint]
            else:
                filtered = self.metrics

            return filtered[-limit:] if filtered else []

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控仪表板数据"""
        with self.lock:
            if not self.metrics:
                return {
                    "total_requests": 0,
                    "success_rate": 0.0,
                    "avg_response_time": 0.0,
                    "endpoints": {},
                    "recent_errors": [],
                    "timestamp": datetime.now().isoformat(),
                }

            # 计算汇总统计
            total_requests = len(self.metrics)
            success_count = sum(1 for m in self.metrics if m.status_code < 400)
            success_rate = success_count / total_requests if total_requests > 0 else 0

            avg_response_time = sum(m.response_time for m in self.metrics) / total_requests

            # 获取最近的错误
            recent_errors = [
                {
                    "endpoint": m.endpoint,
                    "error": m.error_message,
                    "timestamp": m.timestamp.isoformat(),
                    "response_time": m.response_time,
                }
                for m in self.metrics
                if m.status_code >= 400
            ][
                -10:
            ]  # 最多10条

            # 构建端点统计
            endpoint_data = {}
            for endpoint, stats in self.endpoint_stats.items():
                endpoint_data[endpoint] = {
                    "total_requests": stats.total_requests,
                    "success_count": stats.success_count,
                    "error_count": stats.error_count,
                    "error_rate": f"{stats.error_rate:.2%}",
                    "avg_response_time_ms": round(stats.avg_response_time, 2),
                    "min_response_time_ms": round(stats.min_response_time, 2),
                    "max_response_time_ms": round(stats.max_response_time, 2),
                    "avg_data_quality_score": round(stats.avg_data_quality_score, 2),
                    "last_error": stats.last_error,
                    "last_error_time": stats.last_error_time.isoformat() if stats.last_error_time else None,
                }

            return {
                "total_requests": total_requests,
                "success_rate": f"{success_rate:.2%}",
                "avg_response_time_ms": round(avg_response_time, 2),
                "endpoints": endpoint_data,
                "recent_errors": recent_errors,
                "timestamp": datetime.now().isoformat(),
            }

    def get_health_check(self) -> Dict[str, Any]:
        """获取健康检查报告"""
        with self.lock:
            if not self.metrics:
                return {
                    "status": "healthy",
                    "message": "未收集到指标数据",
                    "timestamp": datetime.now().isoformat(),
                }

            # 检查最近1小时的错误率
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_metrics = [m for m in self.metrics if m.timestamp >= one_hour_ago]

            if not recent_metrics:
                return {
                    "status": "healthy",
                    "message": "过去1小时无请求",
                    "timestamp": datetime.now().isoformat(),
                }

            recent_errors = sum(1 for m in recent_metrics if m.status_code >= 400)
            recent_error_rate = recent_errors / len(recent_metrics)

            # 检查响应时间
            avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)

            issues = []

            if recent_error_rate > 0.1:  # 错误率超过10%
                issues.append(f"高错误率: {recent_error_rate:.2%}")

            if avg_response_time > 1000:  # 响应时间超过1秒
                issues.append(f"响应缓慢: {avg_response_time:.0f}ms")

            # 检查数据质量
            quality_scores = [m.data_quality_score for m in recent_metrics if m.data_quality_score is not None]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                if avg_quality < 70:
                    issues.append(f"数据质量低: {avg_quality:.1f}/100")

            status = "unhealthy" if len(issues) > 1 else ("warning" if issues else "healthy")
            message = "; ".join(issues) if issues else "系统运行正常"

            return {
                "status": status,
                "message": message,
                "error_rate": f"{recent_error_rate:.2%}",
                "avg_response_time_ms": round(avg_response_time, 2),
                "timestamp": datetime.now().isoformat(),
            }

    def clear_old_data(self, older_than_hours: int = 24) -> int:
        """清理旧数据"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            original_len = len(self.metrics)
            self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
            removed_count = original_len - len(self.metrics)
            if removed_count > 0:
                logger.info(f"Cleared {removed_count} old metrics")
            return removed_count


# 全局监控器实例
global_monitor = APIMonitor()


def get_monitor() -> APIMonitor:
    """获取全局监控器实例"""
    return global_monitor
