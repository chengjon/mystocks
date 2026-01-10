"""
Signal Monitoring Metrics

交易信号监控指标定义，提供信号生成、推送、质量评估的Prometheus指标。

指标列表:
1. mystocks_signal_generation_total - 信号生成计数器
2. mystocks_signal_accuracy_percentage - 信号准确度百分比
3. mystocks_signal_latency_seconds - 信号生成延迟分布
4. mystocks_active_signals_count - 活跃信号数量
5. mystocks_signal_success_rate - 信号成功率
6. mystocks_signal_profit_ratio - 盈利比率
7. mystocks_signal_push_total - 推送通知计数器
8. mystocks_signal_push_latency_seconds - 推送延迟分布
9. mystocks_strategy_health_status - 策略健康状态
"""

from prometheus_client import Counter, Gauge, Histogram

# ============================================================================
# 信号生成指标
# ============================================================================

SIGNAL_GENERATION_TOTAL = Counter(
    "mystocks_signal_generation_total",
    "Total number of signals generated",
    ["strategy_id", "signal_type", "symbol", "status"],
)

SIGNAL_LATENCY_SECONDS = Histogram(
    "mystocks_signal_latency_seconds",
    "Signal generation latency in seconds",
    ["strategy_id", "indicator_count"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

# ============================================================================
# 信号质量指标
# ============================================================================

SIGNAL_ACCURACY_PERCENTAGE = Gauge(
    "mystocks_signal_accuracy_percentage",
    "Signal accuracy percentage (0-100), calculated from executed signals",
    ["strategy_id", "signal_type"],
)

SIGNAL_SUCCESS_RATE = Gauge(
    "mystocks_signal_success_rate", "Signal execution success rate (0-100)", ["strategy_id", "signal_type"]
)

SIGNAL_PROFIT_RATIO = Gauge(
    "mystocks_signal_profit_ratio",
    "Profit ratio of executed signals (0-100)",
    ["strategy_id", "time_window"],  # time_window: 1d/1w/1m/3m
)

ACTIVE_SIGNALS_COUNT = Gauge(
    "mystocks_active_signals_count",
    "Number of currently active signals waiting for execution",
    ["strategy_id", "symbol", "signal_type"],
)

# ============================================================================
# 推送指标
# ============================================================================

SIGNAL_PUSH_TOTAL = Counter(
    "mystocks_signal_push_total",
    "Total number of signal push notifications",
    ["channel", "status"],  # channel: websocket/email/sms/app, status: success/failed/timeout
)

SIGNAL_PUSH_LATENCY_SECONDS = Histogram(
    "mystocks_signal_push_latency_seconds",
    "Signal push notification latency in seconds",
    ["channel"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# ============================================================================
# 策略健康指标
# ============================================================================

STRATEGY_HEALTH_STATUS = Gauge(
    "mystocks_strategy_health_status", "Strategy health status (1=healthy, 0=degraded, -1=unhealthy)", ["strategy_id"]
)


# ============================================================================
# 指标记录辅助函数
# ============================================================================


def record_signal_generation(strategy_id: str, signal_type: str, symbol: str, status: str = "generated") -> None:
    """
    记录信号生成

    Args:
        strategy_id: 策略ID
        signal_type: 信号类型 (BUY/SELL/HOLD)
        symbol: 标的代码
        status: 生成状态 (generated/rejected/filtered)
    """
    SIGNAL_GENERATION_TOTAL.labels(strategy_id=strategy_id, signal_type=signal_type, symbol=symbol, status=status).inc()


def record_signal_latency(strategy_id: str, latency_seconds: float, indicator_count: int = 1) -> None:
    """
    记录信号生成延迟

    Args:
        strategy_id: 策略ID
        latency_seconds: 生成延迟（秒）
        indicator_count: 计算的指标数量
    """
    SIGNAL_LATENCY_SECONDS.labels(strategy_id=strategy_id, indicator_count=str(indicator_count)).observe(
        latency_seconds
    )


def update_signal_accuracy(strategy_id: str, signal_type: str, accuracy_percentage: float) -> None:
    """
    更新信号准确率

    Args:
        strategy_id: 策略ID
        signal_type: 信号类型
        accuracy_percentage: 准确率 (0-100)
    """
    SIGNAL_ACCURACY_PERCENTAGE.labels(strategy_id=strategy_id, signal_type=signal_type).set(
        max(0, min(100, accuracy_percentage))
    )


def update_signal_success_rate(strategy_id: str, signal_type: str, success_rate: float) -> None:
    """
    更新信号成功率

    Args:
        strategy_id: 策略ID
        signal_type: 信号类型
        success_rate: 成功率 (0-100)
    """
    SIGNAL_SUCCESS_RATE.labels(strategy_id=strategy_id, signal_type=signal_type).set(max(0, min(100, success_rate)))


def update_profit_ratio(strategy_id: str, time_window: str, profit_ratio: float) -> None:
    """
    更新盈利比率

    Args:
        strategy_id: 策略ID
        time_window: 时间窗口 (1d/1w/1m/3m)
        profit_ratio: 盈利比率 (0-100)
    """
    SIGNAL_PROFIT_RATIO.labels(strategy_id=strategy_id, time_window=time_window).set(max(0, min(100, profit_ratio)))


def update_active_signals_count(strategy_id: str, symbol: str, signal_type: str, count: int) -> None:
    """
    更新活跃信号数量

    Args:
        strategy_id: 策略ID
        symbol: 标的代码
        signal_type: 信号类型
        count: 活跃信号数量
    """
    ACTIVE_SIGNALS_COUNT.labels(strategy_id=strategy_id, symbol=symbol, signal_type=signal_type).set(max(0, count))


def record_signal_push(channel: str, status: str) -> None:
    """
    记录信号推送

    Args:
        channel: 推送渠道 (websocket/email/sms/app)
        status: 推送状态 (success/failed/timeout)
    """
    SIGNAL_PUSH_TOTAL.labels(channel=channel, status=status).inc()


def record_push_latency(channel: str, latency_seconds: float) -> None:
    """
    记录推送延迟

    Args:
        channel: 推送渠道
        latency_seconds: 推送延迟（秒）
    """
    SIGNAL_PUSH_LATENCY_SECONDS.labels(channel=channel).observe(latency_seconds)


def update_strategy_health(strategy_id: str, status: int) -> None:
    """
    更新策略健康状态

    Args:
        strategy_id: 策略ID
        status: 健康状态 (1=healthy, 0=degraded, -1=unhealthy)
    """
    STRATEGY_HEALTH_STATUS.labels(strategy_id=strategy_id).set(status)


# ============================================================================
# 导出列表
# ============================================================================

__all__ = [
    # 指标定义
    "SIGNAL_GENERATION_TOTAL",
    "SIGNAL_LATENCY_SECONDS",
    "SIGNAL_ACCURACY_PERCENTAGE",
    "SIGNAL_SUCCESS_RATE",
    "SIGNAL_PROFIT_RATIO",
    "ACTIVE_SIGNALS_COUNT",
    "SIGNAL_PUSH_TOTAL",
    "SIGNAL_PUSH_LATENCY_SECONDS",
    "STRATEGY_HEALTH_STATUS",
    # 辅助函数
    "record_signal_generation",
    "record_signal_latency",
    "update_signal_accuracy",
    "update_signal_success_rate",
    "update_profit_ratio",
    "update_active_signals_count",
    "record_signal_push",
    "record_push_latency",
    "update_strategy_health",
]
