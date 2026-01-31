"""
CCI Strategy

CCI顺势指标策略 - 捕捉趋势拐点
Commodity Channel Index
"""

from typing import Any, Dict, List, Optional

from app.backtest.strategies.base import BaseStrategy, SignalType, StrategySignal


class CCIStrategy(BaseStrategy):
    """
    CCI顺势指标策略

    核心逻辑:
    - CCI = (TP - MA(TP)) / (0.015 × MD)
    - TP (典型价格) = (High + Low + Close) / 3
    - MD = 平均绝对偏差

    交易信号:
    - 超买区: CCI > 100 (强势上涨)
    - 超卖区: CCI < -100 (强势下跌)
    - 买入: CCI从超卖区回升穿过-100
    - 卖出: CCI从超买区回落穿过100

    特点:
    - 领先指标，比价格更早反应
    - 对趋势敏感
    - 可用于判断趋势强度
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "CCI顺势指标策略 - 超买超卖回归 + 零轴穿越"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 缓存CCI值
        self.cci_cache = {}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            # CCI参数
            "cci_period": 14,  # CCI周期 (默认14)
            "constant": 0.015,  # 常数因子
            # 超买超卖阈值
            "overbought": 100,  # 超买阈值
            "oversold": -100,  # 超卖阈值
            "extreme_overbought": 200,  # 极度超买
            "extreme_oversold": -200,  # 极度超卖
            # 交易模式
            "trade_mode": "reversal",  # reversal(回归) / trend(趋势)
            # 回归模式参数
            "entry_on_pullback": True,  # 回归时入场
            "exit_at_zero": True,  # 回到零轴附近退出
            # 趋势模式参数
            "entry_on_breakout": False,  # 突破时入场
            "follow_strong_trend": True,  # 跟随强趋势
            # 确认参数
            "confirm_bars": 1,  # 确认K线数
            "use_price_confirm": True,  # 价格确认
            # 止损止盈
            "stop_loss_pct": 0.05,  # 止损%
            "take_profit_pct": 0.10,  # 止盈%
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "cci_period",
                "type": "int",
                "min": 10,
                "max": 30,
                "label": "CCI周期",
            },
            {
                "name": "overbought",
                "type": "int",
                "min": 80,
                "max": 150,
                "label": "超买阈值",
            },
            {
                "name": "oversold",
                "type": "int",
                "min": -150,
                "max": -80,
                "label": "超卖阈值",
            },
            {
                "name": "trade_mode",
                "type": "select",
                "options": ["reversal", "trend"],
                "label": "交易模式",
            },
        ]

    def _calculate_cci(self, history: List[Dict[str, Any]]) -> Optional[float]:
        """
        计算CCI指标

        CCI = (TP - SMA(TP)) / (0.015 × MD)
        """
        cci_period = self.parameters["cci_period"]

        if len(history) < cci_period:
            return None

        recent = history[-cci_period:]

        # 1. 计算典型价格 (TP)
        typical_prices = []
        for bar in recent:
            tp = (bar["high"] + bar["low"] + bar["close"]) / 3
            typical_prices.append(tp)

        # 2. 计算TP的简单移动平均
        tp_sma = sum(typical_prices) / cci_period

        # 3. 计算平均绝对偏差 (MD)
        deviations = [abs(tp - tp_sma) for tp in typical_prices]
        md = sum(deviations) / cci_period

        # 4. 计算CCI
        if md == 0:
            return 0  # 避免除零

        constant = self.parameters["constant"]
        current_tp = typical_prices[-1]
        cci = (current_tp - tp_sma) / (constant * md)

        return cci

    def _check_oversold_exit(self, cci: float, prev_cci: float) -> bool:
        """检测从超卖区回升穿过阈值"""
        oversold = self.parameters["oversold"]
        return cci > oversold and prev_cci <= oversold

    def _check_overbought_exit(self, cci: float, prev_cci: float) -> bool:
        """检测从超买区回落穿过阈值"""
        overbought = self.parameters["overbought"]
        return cci < overbought and prev_cci >= overbought

    def _check_zero_cross_up(self, cci: float, prev_cci: float) -> bool:
        """检测向上穿越零轴"""
        return cci > 0 and prev_cci <= 0

    def _check_zero_cross_down(self, cci: float, prev_cci: float) -> bool:
        """检测向下穿越零轴"""
        return cci < 0 and prev_cci >= 0

    def _check_breakout_up(self, cci: float, prev_cci: float) -> bool:
        """检测向上突破超买线（趋势模式）"""
        overbought = self.parameters["overbought"]
        return cci > overbought and prev_cci <= overbought

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        history = self.price_history.get(symbol, [])
        cci_period = self.parameters["cci_period"]

        if len(history) < cci_period + 1:
            return None

        # 计算当前和前一天的CCI
        cci = self._calculate_cci(history)
        prev_cci = self._calculate_cci(history[:-1])

        if cci is None or prev_cci is None:
            return None

        float(current_data["close"])
        has_position = position and position.get("quantity", 0) > 0
        trade_mode = self.parameters["trade_mode"]

        overbought = self.parameters["overbought"]
        oversold = self.parameters["oversold"]
        self.parameters["extreme_overbought"]
        extreme_oversold = self.parameters["extreme_oversold"]

        # === 回归模式 (Reversal) ===
        if trade_mode == "reversal":
            # 买入信号: 从超卖区回升
            if not has_position:
                if self._check_oversold_exit(cci, prev_cci):
                    # 计算信号强度 (越超卖强度越高)
                    strength = min(1.0, abs(prev_cci) / abs(extreme_oversold))

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"CCI超卖回升: {prev_cci:.2f} → {cci:.2f} (穿越{oversold})",
                        metadata={
                            "cci": cci,
                            "prev_cci": prev_cci,
                            "mode": "reversal_entry",
                        },
                    )

            # 卖出信号
            if has_position:
                # 从超买区回落
                if self._check_overbought_exit(cci, prev_cci):
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"CCI超买回落: {prev_cci:.2f} → {cci:.2f} (穿越{overbought})",
                        metadata={"cci": cci, "prev_cci": prev_cci},
                    )

                # 或者回到零轴附近
                if self.parameters.get("exit_at_zero"):
                    if self._check_zero_cross_down(cci, prev_cci):
                        return StrategySignal(
                            symbol=symbol,
                            signal_type=SignalType.EXIT,
                            strength=0.5,  # 部分退出
                            reason=f"CCI零轴死叉: {prev_cci:.2f} → {cci:.2f}",
                            metadata={"cci": cci, "prev_cci": prev_cci},
                        )

        # === 趋势模式 (Trend) ===
        elif trade_mode == "trend":
            # 买入信号: 向上突破超买线（强势）
            if not has_position:
                if self.parameters.get("entry_on_breakout"):
                    if self._check_breakout_up(cci, prev_cci):
                        return StrategySignal(
                            symbol=symbol,
                            signal_type=SignalType.LONG,
                            strength=0.7,
                            reason=f"CCI强势突破: {prev_cci:.2f} → {cci:.2f} (突破{overbought})",
                            metadata={"cci": cci, "mode": "trend_entry"},
                        )

                # 或者零轴金叉
                if self._check_zero_cross_up(cci, prev_cci):
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=0.5,
                        reason=f"CCI零轴金叉: {prev_cci:.2f} → {cci:.2f}",
                        metadata={"cci": cci, "mode": "zero_cross"},
                    )

            # 卖出信号
            if has_position:
                # 跌破超买线
                if cci < overbought and prev_cci >= overbought:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=0.5,
                        reason=f"CCI跌破超买线: {prev_cci:.2f} → {cci:.2f}",
                        metadata={"cci": cci},
                    )

                # 或者进入超卖区
                if cci < oversold:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"CCI进入超卖区: {cci:.2f} < {oversold}",
                        metadata={"cci": cci},
                    )

        # 通用止损: 极度超卖止损
        if has_position and cci < extreme_oversold:
            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.EXIT,
                strength=1.0,
                reason=f"CCI极度超卖止损: {cci:.2f} < {extreme_oversold}",
                metadata={"cci": cci},
            )

        return None
