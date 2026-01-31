"""
监控逻辑解耦方案 - 基于装饰器模式和观察者模式
将横切关注点(监控、日志、性能)从业务逻辑中分离出来

设计原则:
1. 装饰器模式: 透明地为业务方法添加监控功能
2. 观察者模式: 松耦合的事件通知机制
3. 依赖注入: 通过配置控制监控功能
4. 单一职责: 监控逻辑与业务逻辑彻底分离

作者: Claude Code
版本: 3.0.0
日期: 2025-11-14
"""

import functools
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# =============================================================================
# 事件系统 - 观察者模式的实现
# =============================================================================


class MonitoringEvent(Enum):
    """监控事件类型"""

    OPERATION_START = "operation_start"
    OPERATION_END = "operation_end"
    OPERATION_ERROR = "operation_error"
    PERFORMANCE_SLOW = "performance_slow"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    ALERT_RAISED = "alert_raised"


@dataclass
class MonitoringEventData:
    """监控事件数据"""

    event_type: MonitoringEvent
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


class MonitoringEventListener(ABC):
    """监控事件监听器抽象基类"""

    @abstractmethod
    def on_event(self, event: MonitoringEventData):
        """处理监控事件"""


class EventBus:
    """事件总线 - 统一的事件分发机制"""

    def __init__(self):
        self._listeners: Dict[MonitoringEvent, List[MonitoringEventListener]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type: MonitoringEvent, listener: MonitoringEventListener):
        """订阅事件"""
        with self._lock:
            self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: MonitoringEvent, listener: MonitoringEventListener):
        """取消订阅"""
        with self._lock:
            if listener in self._listeners[event_type]:
                self._listeners[event_type].remove(listener)

    def publish(self, event: MonitoringEventData):
        """发布事件"""
        with self._lock:
            listeners = self._listeners.get(event.event_type, [])
            for listener in listeners:
                try:
                    listener.on_event(event)
                except Exception as e:
                    # 避免监听器异常影响其他监听器
                    logging.getLogger(__name__).error(f"监听器异常: {e}")


# 全局事件总线实例
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    return _event_bus


# =============================================================================
# 监控上下文管理
# =============================================================================


class MonitoringContext:
    """监控上下文 - 管理当前操作的监控信息"""

    _context: ContextVar[Dict[str, Any]] = ContextVar("monitoring_context", default={})

    @classmethod
    def get_current_context(cls) -> Dict[str, Any]:
        """获取当前监控上下文"""
        return cls._context.get()

    @classmethod
    def set_current_context(cls, context: Dict[str, Any]):
        """设置当前监控上下文"""
        cls._context.set(context)

    @classmethod
    def update_context(cls, **kwargs):
        """更新当前监控上下文"""
        current = cls.get_current_context()
        current.update(kwargs)
        cls.set_current_context(current)

    @classmethod
    def clear_context(cls):
        """清除当前监控上下文"""
        cls._context.set({})


@dataclass
class OperationContext:
    """操作上下文 - 记录操作相关信息"""

    operation_id: str
    operation_name: str
    table_name: Optional[str] = None
    database_type: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "operation_id": self.operation_id,
            "operation_name": self.operation_name,
            "table_name": self.table_name,
            "database_type": self.database_type,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "metadata": self.metadata,
        }


# =============================================================================
# 监控指标收集器
# =============================================================================


@dataclass
class PerformanceMetrics:
    """性能指标"""

    operation_name: str
    duration: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    data_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataQualityMetrics:
    """数据质量指标"""

    operation_name: str
    table_name: str
    record_count: int
    null_count: int
    duplicate_count: int
    quality_score: float
    issues: List[str]
    timestamp: datetime


# =============================================================================
# 监控监听器实现
# =============================================================================


class LoggingMonitoringListener(MonitoringEventListener):
    """日志监控监听器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def on_event(self, event: MonitoringEventData):
        """记录监控事件到日志"""
        if event.event_type == MonitoringEvent.OPERATION_START:
            self.logger.info("操作开始: {event.data.get('operation_name')} - ID: {event.data.get('operation_id')")
        elif event.event_type == MonitoringEvent.OPERATION_END:
            duration = event.data.get("duration", 0)
            self.logger.info("操作完成: %s - 耗时: %ss", event.data.get("operation_name"), duration)
        elif event.event_type == MonitoringEvent.OPERATION_ERROR:
            self.logger.error("操作失败: {event.data.get('operation_name')} - 错误: {event.data.get('error_message')")
        elif event.event_type == MonitoringEvent.PERFORMANCE_SLOW:
            duration = event.data.get("duration", 0)
            self.logger.warning("慢操作: %s - 耗时: %ss", event.data.get("operation_name"), duration)


class PerformanceMonitoringListener(MonitoringEventListener):
    """性能监控监听器"""

    def __init__(self, slow_operation_threshold: float = 5.0):
        self.slow_operation_threshold = slow_operation_threshold
        self.performance_data: List[PerformanceMetrics] = []

    def on_event(self, event: MonitoringEventData):
        """收集性能指标"""
        if event.event_type == MonitoringEvent.OPERATION_END:
            metrics = PerformanceMetrics(
                operation_name=event.data.get("operation_name", "unknown"),
                duration=event.data.get("duration", 0),
                timestamp=event.timestamp,
                success=event.data.get("success", False),
                error_message=event.data.get("error_message"),
                data_count=event.data.get("data_count", 0),
                context=event.context,
            )
            self.performance_data.append(metrics)

            # 检查是否慢操作
            if metrics.duration > self.slow_operation_threshold:
                slow_event = MonitoringEventData(
                    event_type=MonitoringEvent.PERFORMANCE_SLOW,
                    data={
                        "operation_name": metrics.operation_name,
                        "duration": metrics.duration,
                        "threshold": self.slow_operation_threshold,
                    },
                    context=metrics.context,
                )
                get_event_bus().publish(slow_event)


class DataQualityMonitoringListener(MonitoringEventListener):
    """数据质量监控监听器"""

    def __init__(self):
        self.quality_issues: List[DataQualityMetrics] = []

    def on_event(self, event: MonitoringEventData):
        """监控数据质量"""
        if event.event_type == MonitoringEvent.DATA_QUALITY_ISSUE:
            quality_metrics = DataQualityMetrics(
                operation_name=event.data.get("operation_name", "unknown"),
                table_name=event.data.get("table_name", "unknown"),
                record_count=event.data.get("record_count", 0),
                null_count=event.data.get("null_count", 0),
                duplicate_count=event.data.get("duplicate_count", 0),
                quality_score=event.data.get("quality_score", 0.0),
                issues=event.data.get("issues", []),
                timestamp=event.timestamp,
            )
            self.quality_issues.append(quality_metrics)


# =============================================================================
# 装饰器基类
# =============================================================================


class BaseMonitoringDecorator:
    """监控装饰器基类"""

    def __init__(self, enable_monitoring: bool = True):
        self.enable_monitoring = enable_monitoring
        self.event_bus = get_event_bus()

    def should_monitor(self, func: Callable, *args, **kwargs) -> bool:
        """判断是否应该监控此操作"""
        if not self.enable_monitoring:
            return False

        # 可以添加更复杂的逻辑，如基于方法名、参数等的过滤
        return True

    def extract_operation_info(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """从函数和参数中提取操作信息"""
        return {
            "operation_name": func.__name__,
            "function": func,
            "args": args,
            "kwargs": kwargs,
        }


# =============================================================================
# 具体装饰器实现
# =============================================================================


class operation_monitor(BaseMonitoringDecorator):
    """操作监控装饰器"""

    def __init__(self, operation_name: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.operation_name = operation_name

    def __call__(self, func: Callable) -> Callable:
        """装饰函数"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.should_monitor(func, *args, **kwargs):
                return func(*args, **kwargs)

            # 创建操作上下文
            operation_id = f"{func.__name__}_{int(time.time() * 1000)}"
            operation_name = self.operation_name or func.__name__

            context = OperationContext(operation_id=operation_id, operation_name=operation_name)

            # 设置监控上下文
            MonitoringContext.set_current_context(context.to_dict())

            # 发布开始事件
            self.event_bus.publish(
                MonitoringEventData(
                    event_type=MonitoringEvent.OPERATION_START,
                    data={
                        "operation_id": operation_id,
                        "operation_name": operation_name,
                        "function_name": func.__name__,
                    },
                    context=MonitoringContext.get_current_context(),
                )
            )

            start_time = time.time()
            result = None
            error_message = None

            try:
                # 执行原函数
                result = func(*args, **kwargs)

                # 计算执行时间
                duration = time.time() - start_time

                # 发布成功事件
                self.event_bus.publish(
                    MonitoringEventData(
                        event_type=MonitoringEvent.OPERATION_END,
                        data={
                            "operation_id": operation_id,
                            "operation_name": operation_name,
                            "duration": duration,
                            "success": True,
                            "data_count": len(result) if hasattr(result, "__len__") else 0,
                        },
                        context=MonitoringContext.get_current_context(),
                    )
                )

                return result

            except Exception as e:
                # 发生异常
                duration = time.time() - start_time
                error_message = str(e)

                # 发布错误事件
                self.event_bus.publish(
                    MonitoringEventData(
                        event_type=MonitoringEvent.OPERATION_ERROR,
                        data={
                            "operation_id": operation_id,
                            "operation_name": operation_name,
                            "duration": duration,
                            "success": False,
                            "error_message": error_message,
                        },
                        context=MonitoringContext.get_current_context(),
                    )
                )

                raise

            finally:
                # 清理上下文
                MonitoringContext.clear_context()

        return wrapper


class performance_monitor(BaseMonitoringDecorator):
    """性能监控装饰器"""

    def __init__(self, threshold: float = 5.0, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

    def __call__(self, func: Callable) -> Callable:
        """装饰函数"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.should_monitor(func, *args, **kwargs):
                return func(*args, **kwargs)

            start_time = time.time()
            result = None

            try:
                result = func(*args, **kwargs)
                return result

            finally:
                duration = time.time() - start_time

                if duration > self.threshold:
                    self.event_bus.publish(
                        MonitoringEventData(
                            event_type=MonitoringEvent.PERFORMANCE_SLOW,
                            data={
                                "operation_name": func.__name__,
                                "duration": duration,
                                "threshold": self.threshold,
                            },
                        )
                    )

        return wrapper


class data_quality_monitor(BaseMonitoringDecorator):
    """数据质量监控装饰器"""

    def __init__(self, table_name: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.table_name = table_name

    def __call__(self, func: Callable) -> Callable:
        """装饰函数"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.should_monitor(func, *args, **kwargs):
                return func(*args, **kwargs)

            result = func(*args, **kwargs)

            # 检查返回结果的数据质量
            if hasattr(result, "__len__") and len(result) > 0:
                self._check_data_quality(result, func.__name__, self.table_name)

            return result

        return wrapper

    def _check_data_quality(self, data: Any, operation_name: str, table_name: Optional[str]):
        """检查数据质量"""
        import pandas as pd

        if not isinstance(data, pd.DataFrame):
            return

        # 计算质量指标
        record_count = len(data)
        null_count = data.isnull().sum().sum()
        duplicate_count = data.duplicated().sum() if len(data) > 0 else 0

        # 计算质量分数 (简化版)
        null_ratio = null_count / (record_count * len(data.columns)) if record_count > 0 else 0
        duplicate_ratio = duplicate_count / record_count if record_count > 0 else 0
        quality_score = max(0, 1 - null_ratio - duplicate_ratio)

        # 识别问题
        issues = []
        if null_ratio > 0.1:
            issues.append(f"空值比例过高: {null_ratio:.2%}")
        if duplicate_ratio > 0.05:
            issues.append(f"重复数据比例过高: {duplicate_ratio:.2%}")

        # 如果有问题，发布事件
        if issues:
            self.event_bus.publish(
                MonitoringEventData(
                    event_type=MonitoringEvent.DATA_QUALITY_ISSUE,
                    data={
                        "operation_name": operation_name,
                        "table_name": table_name,
                        "record_count": record_count,
                        "null_count": null_count,
                        "duplicate_count": duplicate_count,
                        "quality_score": quality_score,
                        "issues": issues,
                    },
                )
            )


# =============================================================================
# 监控配置管理
# =============================================================================


class MonitoringConfig:
    """监控配置管理"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self._setup_listeners()

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "enable_monitoring": True,
            "enable_performance_monitoring": True,
            "enable_data_quality_monitoring": True,
            "slow_operation_threshold": 5.0,
            "listeners": {"logging": True, "performance": True, "data_quality": True},
        }

    def _setup_listeners(self):
        """设置监控监听器"""
        if self.config.get("listeners", {}).get("logging", True):
            logging_listener = LoggingMonitoringListener()
            _event_bus.subscribe(MonitoringEvent.OPERATION_START, logging_listener)
            _event_bus.subscribe(MonitoringEvent.OPERATION_END, logging_listener)
            _event_bus.subscribe(MonitoringEvent.OPERATION_ERROR, logging_listener)

        if self.config.get("listeners", {}).get("performance", True):
            perf_listener = PerformanceMonitoringListener(
                slow_operation_threshold=self.config.get("slow_operation_threshold", 5.0)
            )
            _event_bus.subscribe(MonitoringEvent.OPERATION_END, perf_listener)
            _event_bus.subscribe(MonitoringEvent.PERFORMANCE_SLOW, perf_listener)

        if self.config.get("listeners", {}).get("data_quality", True):
            quality_listener = DataQualityMonitoringListener()
            _event_bus.subscribe(MonitoringEvent.DATA_QUALITY_ISSUE, quality_listener)

    def is_enabled(self) -> bool:
        """检查监控是否启用"""
        return self.config.get("enable_monitoring", True)


# 全局监控配置实例
_monitoring_config = MonitoringConfig()


def get_monitoring_config() -> MonitoringConfig:
    """获取全局监控配置"""
    return _monitoring_config


# =============================================================================
# 便捷装饰器
# =============================================================================


def monitor_operation(operation_name: Optional[str] = None, **kwargs):
    """便捷的操作监控装饰器"""

    def decorator(func: Callable) -> Callable:
        return operation_monitor(operation_name=operation_name, **kwargs)(func)

    return decorator


def monitor_performance(threshold: float = 5.0, **kwargs):
    """便捷的性能监控装饰器"""

    def decorator(func: Callable) -> Callable:
        return performance_monitor(threshold=threshold, **kwargs)(func)

    return decorator


def monitor_data_quality(table_name: Optional[str] = None, **kwargs):
    """便捷的数据质量监控装饰器"""

    def decorator(func: Callable) -> Callable:
        return data_quality_monitor(table_name=table_name, **kwargs)(func)

    return decorator


# =============================================================================
# 监控统计和报告
# =============================================================================


class MonitoringReporter:
    """监控报告生成器"""

    def __init__(self):
        self.event_bus = get_event_bus()

    def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        # 这里应该从实际的监听器中获取数据
        # 简化实现，返回模拟数据
        return {
            "total_operations": 0,
            "average_duration": 0.0,
            "slow_operations": [],
            "success_rate": 0.0,
        }

    def get_data_quality_report(self) -> Dict[str, Any]:
        """生成数据质量报告"""
        return {
            "total_operations": 0,
            "quality_issues": [],
            "average_quality_score": 0.0,
        }

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """生成监控摘要"""
        return {
            "monitoring_enabled": get_monitoring_config().is_enabled(),
            "performance_report": self.get_performance_report(),
            "data_quality_report": self.get_data_quality_report(),
            "timestamp": datetime.now().isoformat(),
        }


# =============================================================================
# 使用示例
# =============================================================================

if __name__ == "__main__":
    # 示例1: 基本装饰器使用
    @monitor_operation("获取股票数据")
    @monitor_data_quality("stock_daily")
    def get_stock_data(symbol: str, start_date: str, end_date: str):
        """模拟获取股票数据"""
        import time

        import pandas as pd

        # 模拟耗时操作
        time.sleep(0.1)

        # 模拟返回数据
        return pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "symbol": [symbol, symbol],
                "open": [10.0, 10.5],
                "close": [10.2, 10.8],
            }
        )

    # 示例2: 性能监控
    @monitor_performance(threshold=0.05)
    def slow_operation():
        """模拟慢操作"""
        import time

        time.sleep(0.1)  # 模拟耗时操作
        return "完成"

    # 测试装饰器
    print("=== 测试监控装饰器 ===")

    # 测试操作监控
    result = get_stock_data("000001", "2024-01-01", "2024-01-02")
    print(f"获取数据结果: {len(result)}条记录")

    # 测试性能监控
    result = slow_operation()
    print(f"慢操作结果: {result}")

    # 生成报告
    reporter = MonitoringReporter()
    summary = reporter.get_monitoring_summary()
    print(f"\n监控摘要: {summary}")

    print("\n🎉 监控解耦示例完成！")
