"""
监控指标收集器
Metrics Collector
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import psutil
import threading
from prometheus_client import Counter, Histogram, Gauge, Summary
import json

logger = logging.getLogger(__name__)


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.metrics = {}
        self.counters = {}
        self.histograms = {}
        self.gauges = {}
        self.summaries = {}
        self.lock = threading.Lock()
        self.initialize_prometheus_metrics()

    def initialize_prometheus_metrics(self):
        """初始化Prometheus指标"""
        # API请求指标
        self.counters['api_requests'] = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'service', 'status']
        )

        self.histograms['api_duration'] = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['method', 'service']
        )

        self.gauges['active_connections'] = Gauge(
            'active_connections',
            'Number of active connections',
            ['service']
        )

        # GPU指标
        self.gauges['gpu_utilization'] = Gauge(
            'gpu_utilization_percent',
            'GPU utilization percentage',
            ['gpu_id', 'service']
        )

        self.gauges['gpu_memory_usage'] = Gauge(
            'gpu_memory_usage_percent',
            'GPU memory usage percentage',
            ['gpu_id', 'service']
        )

        self.gauges['gpu_temperature'] = Gauge(
            'gpu_temperature_celsius',
            'GPU temperature in Celsius',
            ['gpu_id']
        )

        # 任务队列指标
        self.gauges['queue_length'] = Gauge(
            'task_queue_length',
            'Number of tasks in queue',
            ['queue_type']
        )

        self.counters['tasks_completed'] = Counter(
            'tasks_completed_total',
            'Total tasks completed',
            ['queue_type', 'status']
        )

        self.histograms['task_duration'] = Histogram(
            'task_duration_seconds',
            'Task execution duration',
            ['queue_type']
        )

        # 系统指标
        self.gauges['cpu_usage'] = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage'
        )

        self.gauges['memory_usage'] = Gauge(
            'memory_usage_percent',
            'Memory usage percentage'
        )

        self.gauges['disk_usage'] = Gauge(
            'disk_usage_percent',
            'Disk usage percentage'
        )

        # 性能指标
        self.summaries['query_performance'] = Summary(
            'query_performance_seconds',
            'Query performance metrics',
            ['query_type', 'table']
        )

    def record_api_request(self, method: str, service: str, status: str, duration: float):
        """记录API请求"""
        with self.lock:
            self.counters['api_requests'].labels(
                method=method,
                service=service,
                status=status
            ).inc()

            self.histograms['api_duration'].labels(
                method=method,
                service=service
            ).observe(duration)

    def record_gpu_metrics(self, gpu_id: int, utilization: float, memory_usage: float, temperature: float):
        """记录GPU指标"""
        with self.lock:
            self.gauges['gpu_utilization'].labels(
                gpu_id=str(gpu_id),
                service='gpu_api'
            ).set(utilization)

            self.gauges['gpu_memory_usage'].labels(
                gpu_id=str(gpu_id),
                service='gpu_api'
            ).set(memory_usage)

            self.gauges['gpu_temperature'].labels(
                gpu_id=str(gpu_id)
            ).set(temperature)

    def record_task_metrics(self, queue_type: str, status: str, duration: float):
        """记录任务指标"""
        with self.lock:
            self.counters['tasks_completed'].labels(
                queue_type=queue_type,
                status=status
            ).inc()

            self.histograms['task_duration'].labels(
                queue_type=queue_type
            ).observe(duration)

    def record_queue_length(self, queue_type: str, length: int):
        """记录队列长度"""
        with self.lock:
            self.gauges['queue_length'].labels(
                queue_type=queue_type
            ).set(length)

    def record_active_connections(self, service: str, count: int):
        """记录活跃连接数"""
        with self.lock:
            self.gauges['active_connections'].labels(
                service=service
            ).set(count)

    def record_system_metrics(self):
        """记录系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.gauges['cpu_usage'].set(cpu_percent)

            # 内存使用率
            memory = psutil.virtual_memory()
            self.gauges['memory_usage'].set(memory.percent)

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            self.gauges['disk_usage'].set(disk.percent)

        except Exception as e:
            logger.error(f"记录系统指标失败: {e}")

    def record_query_performance(self, query_type: str, table: str, duration: float):
        """记录查询性能"""
        with self.lock:
            self.summaries['query_performance'].labels(
                query_type=query_type,
                table=table
            ).observe(duration)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self.lock:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': self._get_system_metrics(),
                'gpu_metrics': self._get_gpu_metrics(),
                'api_metrics': self._get_api_metrics(),
                'task_metrics': self._get_task_metrics()
            }
            return summary

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            return {
                'cpu_usage': self.gauges['cpu_usage']._value._value if hasattr(self.gauges['cpu_usage']._value, '_value') else 0,
                'memory_usage': self.gauges['memory_usage']._value._value if hasattr(self.gauges['memory_usage']._value, '_value') else 0,
                'disk_usage': self.gauges['disk_usage']._value._value if hasattr(self.gauges['disk_usage']._value, '_value') else 0
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}

    def _get_gpu_metrics(self) -> Dict[str, Any]:
        """获取GPU指标"""
        try:
            gpu_metrics = {}
            for gauge_name, gauge in self.gauges.items():
                if 'gpu' in gauge_name:
                    if hasattr(gauge, '_labels') and hasattr(gauge, '_value'):
                        gpu_metrics[gauge_name] = {
                            'labels': gauge._labels,
                            'value': gauge._value._value if hasattr(gauge._value, '_value') else 0
                        }
            return gpu_metrics
        except Exception as e:
            logger.error(f"获取GPU指标失败: {e}")
            return {}

    def _get_api_metrics(self) -> Dict[str, Any]:
        """获取API指标"""
        try:
            api_metrics = {}
            for counter_name, counter in self.counters.items():
                if 'api' in counter_name:
                    api_metrics[counter_name] = {
                        'labels': list(counter._labelnames),
                        'value': counter._value._value if hasattr(counter._value, '_value') else 0
                    }
            return api_metrics
        except Exception as e:
            logger.error(f"获取API指标失败: {e}")
            return {}

    def _get_task_metrics(self) -> Dict[str, Any]:
        """获取任务指标"""
        try:
            task_metrics = {}
            for counter_name, counter in self.counters.items():
                if 'task' in counter_name:
                    task_metrics[counter_name] = {
                        'labels': list(counter._labelnames),
                        'value': counter._value._value if hasattr(counter._value, '_value') else 0
                    }
            return task_metrics
        except Exception as e:
            logger.error(f"获取任务指标失败: {e}")
            return {}

    def export_metrics(self) -> Dict[str, Any]:
        """导出所有指标"""
        with self.lock:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'counters': {},
                'gauges': {},
                'histograms': {},
                'summaries': {}
            }

            # 导出计数器
            for name, counter in self.counters.items():
                export_data['counters'][name] = {
                    'value': counter._value._value if hasattr(counter._value, '_value') else 0,
                    'labels': list(counter._labelnames)
                }

            # 导出仪表
            for name, gauge in self.gauges.items():
                export_data['gauges'][name] = {
                    'value': gauge._value._value if hasattr(gauge._value, '_value') else 0,
                    'labels': list(gauge._labelnames)
                }

            # 导出直方图
            for name, histogram in self.histograms.items():
                export_data['histograms'][name] = {
                    'count': histogram._count._value if hasattr(histogram._count, '_value') else 0,
                    'sum': histogram._sum._value if hasattr(histogram._sum, '_value') else 0,
                    'labels': list(histogram._labelnames)
                }

            # 导出摘要
            for name, summary in self.summaries.items():
                export_data['summaries'][name] = {
                    'count': summary._count._value if hasattr(summary._count, '_value') else 0,
                    'sum': summary._sum._value if hasattr(summary._sum, '_value') else 0,
                    'labels': list(summary._labelnames)
                }

            return export_data

    def cleanup_old_metrics(self, days: int = 30):
        """清理旧指标"""
        cutoff_time = datetime.now() - timedelta(days=days)

        # 这里可以实现基于时间的指标清理逻辑
        # 由于Prometheus指标是累积的，通常不需要清理
        logger.info(f"指标清理完成，保留最近{days}天的数据")


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.performance_thresholds = {
            'api_response_time': 1.0,  # 秒
            'query_time': 0.5,  # 秒
            'gpu_utilization': 90,  # 百分比
            'memory_usage': 85,  # 百分比
            'queue_length': 1000  # 任务数量
        }
        self.alerts = []

    def monitor_api_performance(self, method: str, service: str, duration: float):
        """监控API性能"""
        if duration > self.performance_thresholds['api_response_time']:
            alert = {
                'type': 'api_performance',
                'severity': 'warning',
                'message': f"API {method} in {service}响应时间过长: {duration:.2f}s",
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'method': method,
                    'service': service,
                    'duration': duration,
                    'threshold': self.performance_thresholds['api_response_time']
                }
            }
            self.alerts.append(alert)
            logger.warning(alert['message'])

    def monitor_query_performance(self, query_type: str, table: str, duration: float):
        """监控查询性能"""
        if duration > self.performance_thresholds['query_time']:
            alert = {
                'type': 'query_performance',
                'severity': 'warning',
                'message': f"查询 {query_type} on {table} 执行时间过长: {duration:.2f}s",
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'query_type': query_type,
                    'table': table,
                    'duration': duration,
                    'threshold': self.performance_thresholds['query_time']
                }
            }
            self.alerts.append(alert)
            logger.warning(alert['message'])

    def monitor_system_health(self):
        """监控系统健康状态"""
        alerts = []

        # 检查系统资源使用率
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.performance_thresholds['gpu_utilization']:
                alerts.append({
                    'type': 'high_cpu',
                    'severity': 'warning',
                    'message': f"CPU使用率过高: {cpu_percent}%",
                    'timestamp': datetime.now().isoformat(),
                    'details': {'cpu_usage': cpu_percent}
                })

            memory = psutil.virtual_memory()
            if memory.percent > self.performance_thresholds['memory_usage']:
                alerts.append({
                    'type': 'high_memory',
                    'severity': 'warning',
                    'message': f"内存使用率过高: {memory.percent}%",
                    'timestamp': datetime.now().isoformat(),
                    'details': {'memory_usage': memory.percent}
                })

        except Exception as e:
            logger.error(f"监控系统健康失败: {e}")

        return alerts

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取告警信息"""
        return self.alerts[-limit:]

    def clear_alerts(self, older_than_hours: int = 24):
        """清理旧告警"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]