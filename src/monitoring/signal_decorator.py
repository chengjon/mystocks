"""
Signal Monitoring Decorator

信号监控装饰器 - 复用现有StrategyExecutor，添加信号生成和推送监控。

功能：
- 记录信号生成统计（数量、类型、延迟）
- 记录推送结果（成功率、延迟）
- 更新策略健康状态
- 兼容现有GPU加速逻辑

使用方式：
```python
# 包装现有的StrategyExecutor
from src.ml_strategy.strategy import StrategyExecutor
from src.monitoring.signal_decorator import monitored_strategy

executor = StrategyExecutor(strategy, signal_manager)
monitored_executor = monitored_strategy(executor)

# 正常使用，不改变原有逻辑
result = monitored_executor.execute(symbols)
```

作者: MyStocks量化交易团队
创建时间: 2026-01-08
版本: 1.0.0
"""

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from src.monitoring.signal_metrics import (
        record_push_latency,
        record_signal_generation,
        record_signal_latency,
        record_signal_push,
        update_active_signals_count,
        update_profit_ratio,
        update_signal_accuracy,
        update_signal_success_rate,
        update_strategy_health,
    )
except ImportError:
    logger.warning("Signal metrics module not available, monitoring disabled")
    record_signal_generation = None
    record_signal_latency = None
    record_signal_push = None
    record_push_latency = None
    update_signal_accuracy = None
    update_signal_success_rate = None
    update_profit_ratio = None
    update_active_signals_count = None
    update_strategy_health = None


class SignalMonitoringContext:
    """
    信号监控上下文 - 跟踪单次策略执行的监控数据
    """

    def __init__(self, strategy_id: str):
        self.strategy_id = strategy_id
        self.start_time = time.time()
        self.signals_generated: Dict[str, int] = {"BUY": 0, "SELL": 0, "HOLD": 0}
        self.signals_by_symbol: Dict[str, Dict[str, int]] = {}
        self.push_results: Dict[str, Dict[str, int]] = {}
        self.errors: List[str] = []
        self._gpu_used = False
        self._gpu_latency_ms = 0.0

    def record_signal(self, signal_type: str, symbol: str) -> None:
        """记录信号生成"""
        self.signals_generated[signal_type] = self.signals_generated.get(signal_type, 0) + 1

        if symbol not in self.signals_by_symbol:
            self.signals_by_symbol[symbol] = {"BUY": 0, "SELL": 0, "HOLD": 0}
        self.signals_by_symbol[symbol][signal_type] = self.signals_by_symbol[symbol].get(signal_type, 0) + 1

        if record_signal_generation:
            record_signal_generation(
                strategy_id=self.strategy_id, signal_type=signal_type, symbol=symbol, status="generated"
            )

    def record_push(self, channel: str, success: bool, latency_ms: float) -> None:
        """记录推送结果"""
        status = "success" if success else "failed"
        if channel not in self.push_results:
            self.push_results[channel] = {"success": 0, "failed": 0, "total_latency_ms": 0.0}

        if success:
            self.push_results[channel]["success"] += 1
        else:
            self.push_results[channel]["failed"] += 1
        self.push_results[channel]["total_latency_ms"] += latency_ms

        if record_signal_push and record_push_latency:
            record_signal_push(channel=channel, status=status)
            record_push_latency(channel=channel, latency_seconds=latency_ms / 1000)

    def record_gpu_usage(self, latency_ms: float) -> None:
        """记录GPU使用情况"""
        self._gpu_used = True
        self._gpu_latency_ms = latency_ms

    def get_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        elapsed_ms = (time.time() - self.start_time) * 1000
        total_signals = sum(self.signals_generated.values())

        return {
            "strategy_id": self.strategy_id,
            "elapsed_ms": round(elapsed_ms, 2),
            "gpu_used": self._gpu_used,
            "gpu_latency_ms": round(self._gpu_latency_ms, 2) if self._gpu_used else None,
            "total_signals": total_signals,
            "signals_by_type": self.signals_generated,
            "unique_symbols": len(self.signals_by_symbol),
            "push_results": self.push_results,
            "errors_count": len(self.errors),
        }

    def update_gauges(self) -> None:
        """更新Prometheus Gauge指标"""
        if not update_strategy_health:
            return

        total_signals = sum(self.signals_generated.values())

        health_status = 1 if len(self.errors) == 0 else 0
        update_strategy_health(self.strategy_id, health_status)

        for symbol, counts in self.signals_by_symbol.items():
            for signal_type, count in counts.items():
                if count > 0:
                    update_active_signals_count(
                        strategy_id=self.strategy_id, symbol=symbol, signal_type=signal_type, count=count
                    )


class MonitoredStrategyExecutor:
    """
    监控包装器 - 复用原有执行器所有功能
    """

    def __init__(self, original_executor: Any, strategy_id: str = "default"):
        self._executor = original_executor
        self._strategy_id = strategy_id
        self._monitoring_context: Optional[SignalMonitoringContext] = None

        for attr_name in dir(original_executor):
            if not attr_name.startswith("_") and attr_name != "execute":
                try:
                    attr = getattr(original_executor, attr_name)
                    if not callable(attr):
                        setattr(self, attr_name, attr)
                except (AttributeError, TypeError):
                    pass

    def __getattr__(self, name: str):
        return getattr(self._executor, name)

    def execute(
        self, symbols: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        self._monitoring_context = SignalMonitoringContext(self._strategy_id)
        start_time = time.time()

        try:
            result = self._executor.execute(symbols=symbols, start_date=start_date, end_date=end_date, **kwargs)

            elapsed_ms = (time.time() - start_time) * 1000

            if hasattr(result, "signals"):
                signals = result.signals if isinstance(result.signals, list) else []
                for signal in signals:
                    signal_type = getattr(signal, "side", None)
                    if signal_type:
                        symbol = getattr(signal, "symbol", "unknown")
                        signal_val = getattr(signal_type, "value", str(signal_type))
                        self._monitoring_context.record_signal(signal_val, symbol)

            if hasattr(self._executor, "_gpu_used") and self._executor._gpu_used:
                self._monitoring_context.record_gpu_usage(elapsed_ms)

            self._monitoring_context.update_gauges()

            if isinstance(result, dict):
                result["_monitoring"] = self._monitoring_context.get_summary()
            elif hasattr(result, "_monitoring"):
                result._monitoring = self._monitoring_context.get_summary()

            logger.info(
                f"策略执行监控: strategy={self._strategy_id}, "
                f"信号数={self._monitoring_context.signals_generated}, "
                f"耗时={elapsed_ms:.2f}ms"
            )

            return result

        except Exception as e:
            self._monitoring_context.errors.append(str(e))
            self._monitoring_context.update_gauges()
            logger.error("策略执行监控错误: %(e)s")
            raise

    def execute_symbol(self, symbol: str, data: Any = None, **kwargs) -> Any:
        start_time = time.time()
        context = SignalMonitoringContext(self._strategy_id)

        try:
            result = self._executor.execute_symbol(symbol, data, **kwargs)

            if hasattr(result, "signals"):
                for signal in result.signals:
                    signal_type = getattr(signal, "side", "HOLD")
                    symbol_name = getattr(signal, "symbol", symbol)
                    context.record_signal(getattr(signal_type, "value", str(signal_type)), symbol_name)

            latency_ms = (time.time() - start_time) * 1000
            if record_signal_latency:
                record_signal_latency(
                    strategy_id=self._strategy_id, latency_seconds=latency_ms / 1000, indicator_count=1
                )

            context.update_gauges()

            return result

        except Exception as e:
            context.errors.append(str(e))
            logger.error("单标的执行监控错误: %(e)s")
            raise

    def get_monitoring_summary(self) -> Dict[str, Any]:
        if self._monitoring_context:
            return self._monitoring_context.get_summary()
        return {"status": "no_execution", "strategy_id": self._strategy_id}

    def record_push_result(self, channel: str, success: bool, latency_ms: float) -> None:
        if self._monitoring_context:
            self._monitoring_context.record_push(channel, success, latency_ms)


def monitored_strategy(executor: Any) -> MonitoredStrategyExecutor:
    """
    策略执行器监控装饰器

    包装现有的StrategyExecutor，添加信号监控功能。

    Args:
        executor: 现有的StrategyExecutor实例

    Returns:
        包装后的执行器（保留原所有方法）
    """
    return MonitoredStrategyExecutor(executor)


def record_signal_result(
    strategy_id: str,
    signal_id: str,
    executed: bool,
    profit_loss: Optional[float] = None,
    execution_time_ms: Optional[float] = None,
) -> None:
    """
    记录信号执行结果

    用于更新信号准确率、成功率等指标。

    Args:
        strategy_id: 策略ID
        signal_id: 信号ID
        executed: 是否成功执行
        profit_loss: 盈亏金额（可选）
        execution_time_ms: 执行时间（毫秒，可选）
    """
    if update_signal_success_rate:
        status = "success" if executed else "failed"

        if executed:
            update_signal_success_rate(strategy_id, "BUY", 100.0 if profit_loss and profit_loss > 0 else 80.0)
        else:
            update_signal_success_rate(strategy_id, "BUY", 0.0)

    if profit_loss is not None and update_profit_ratio:
        profit_percent = 100.0 if profit_loss > 0 else 0.0
        update_profit_ratio(strategy_id, "1d", profit_percent)

    logger.debug("信号结果记录: strategy=%(strategy_id)s, signal=%(signal_id)s, executed=%(executed)s, profit=%(profit_loss)s")
