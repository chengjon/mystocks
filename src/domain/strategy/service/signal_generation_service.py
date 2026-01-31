"""
Signal Generation Service
信号生成领域服务

协调指标计算和规则匹配，生成交易信号。
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd

from src.monitoring.signal_metrics import (
    record_signal_generation,
    record_signal_latency,
    update_active_signals_count,
)
from src.monitoring.signal_recorder import get_signal_recorder

from ..model.rule import Rule
from ..model.signal import Signal
from ..value_objects.strategy_id import StrategyId
from .indicator_calculator import IIndicatorCalculator


@dataclass
class SignalGenerationService:
    """
    信号生成领域服务

    职责：
    - 协调指标计算
    - 执行规则匹配
    - 生成交易信号

    依赖：
    - IIndicatorCalculator: 指标计算器（可CPU/GPU实现）
    """

    indicator_calculator: IIndicatorCalculator

    def generate_signals(
        self,
        strategy_id: StrategyId,
        data: pd.DataFrame,
        rules: List[Rule],
        symbol: str,
    ) -> List[Signal]:
        """
        生成交易信号

        Args:
            strategy_id: 策略ID
            data: 市场数据（OHLCV）
            rules: 规则列表
            symbol: 标的代码

        Returns:
            生成的信号列表
        """
        start_time = time.time()
        indicator_count = len(set(r.indicator_name for r in rules))

        # 1. 计算所有需要的指标
        indicators = self._calculate_indicators(data, rules)

        # 2. 匹配规则
        signals = []
        for rule in rules:
            if rule.matches(indicators):
                signal = self._create_signal(
                    strategy_id=strategy_id,
                    rule=rule,
                    indicators=indicators,
                    symbol=symbol,
                )
                signals.append(signal)

        # 3. 记录指标
        latency_ms = (time.time() - start_time) * 1000
        record_signal_latency(
            strategy_id=strategy_id.id, latency_seconds=latency_ms / 1000, indicator_count=indicator_count
        )

        # 4. 记录到数据库（异步，不阻塞主流程）
        recorder = get_signal_recorder()
        for signal in signals:
            # Prometheus 指标
            record_signal_generation(
                strategy_id=strategy_id.id, signal_type=signal.side.value, symbol=symbol, status="generated"
            )

            # 数据库记录
            try:
                import asyncio

                # 创建异步任务（非阻塞）
                asyncio.create_task(
                    recorder.record_signal(
                        strategy_id=strategy_id.id,
                        symbol=symbol,
                        signal_type=signal.side.value,
                        indicator_count=indicator_count,
                        execution_time_ms=latency_ms,
                        metadata={
                            "confidence": signal.confidence,
                            "reason": signal.reason,
                            "price": signal.price,
                        },
                    )
                )
            except Exception as e:
                # 不影响主流程，只记录错误
                import warnings

                warnings.warn(f"数据库记录失败（非关键）: {e}")

        update_active_signals_count(strategy_id=strategy_id.id, symbol=symbol, signal_type="total", count=len(signals))

        return signals

    def _calculate_indicators(self, data: pd.DataFrame, rules: List[Rule]) -> Dict[str, Any]:
        """
        计算所有需要的指标

        Args:
            data: 市场数据
            rules: 规则列表

        Returns:
            指标值字典
        """
        # 收集所有需要的指标
        indicator_configs = []
        for rule in rules:
            indicator_config = {
                "name": rule.indicator_name,
                "params": {},
            }
            if indicator_config not in indicator_configs:
                indicator_configs.append(indicator_config)

        # 批量计算指标
        indicators = {}
        for config in indicator_configs:
            indicator_name = config["name"]
            if indicator_name == "RSI":
                result = self.indicator_calculator.calculate_rsi(data)
                indicators[indicator_name] = result.iloc[-1]  # 最新值
            elif indicator_name == "MACD":
                result = self.indicator_calculator.calculate_macd(data)
                indicators["MACD"] = result["macd"].iloc[-1]
                indicators["MACD_Signal"] = result["signal"].iloc[-1]
                indicators["MACD_Histogram"] = result["histogram"].iloc[-1]
            elif indicator_name.startswith("MA"):
                # MA_5, MA_10, MA_20, etc.
                period = int(indicator_name.split("_")[1])
                result = self.indicator_calculator.calculate_ma(data, period=period)
                indicators[indicator_name] = result.iloc[-1]
            # ... 其他指标

        return indicators

    def _create_signal(
        self,
        strategy_id: StrategyId,
        rule: Rule,
        indicators: Dict[str, Any],
        symbol: str,
    ) -> Signal:
        """
        从规则创建信号

        Args:
            strategy_id: 策略ID
            rule: 匹配的规则
            indicators: 指标值
            symbol: 标的代码

        Returns:
            交易信号
        """
        # 获取当前价格
        current_price = indicators.get("close", 0.0)

        # 生成信号原因
        reason = self._generate_reason(rule, indicators)

        # 创建信号
        signal = Signal(
            signal_id=f"{strategy_id.id}_{symbol}_{rule.indicator_name}",
            strategy_id=strategy_id,
            symbol=symbol,
            side=rule.action,
            price=current_price,
            quantity=100,  # 默认数量，应该由策略配置决定
            confidence=0.8,  # 默认置信度，可以基于规则强度计算
            reason=reason,
        )

        return signal

    def _generate_reason(self, rule: Rule, indicators: Dict[str, Any]) -> str:
        """
        生成信号原因

        Args:
            rule: 触发的规则
            indicators: 指标值

        Returns:
            原因描述
        """
        value = indicators.get(rule.indicator_name, "N/A")

        return f"{rule.indicator_name} ({value}) {rule.operator} {rule.threshold} -> {rule.action}"
