"""
ADX Strategy

ADX平均趋向指标策略 - 判断趋势强度和方向
Average Directional Index
"""

from typing import Dict, Any, Optional, List

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class ADXStrategy(BaseStrategy):
    """
    ADX平均趋向指标策略

    核心逻辑:
    - +DI: 正向动向指标 (上涨趋势)
    - -DI: 负向动向指标 (下跌趋势)
    - ADX: 趋势强度 (不分方向)

    计算方法:
    - TR = max(H-L, |H-Cp|, |L-Cp|)
    - +DM = H - Hp (if > Lp - L else 0)
    - -DM = Lp - L (if > H - Hp else 0)
    - +DI = Smoothed(+DM) / ATR × 100
    - -DI = Smoothed(-DM) / ATR × 100
    - DX = |+DI - -DI| / (+DI + -DI) × 100
    - ADX = Smoothed(DX)

    交易信号:
    - ADX > 25: 强趋势市场
    - ADX < 20: 震荡市场
    - +DI > -DI: 多头趋势
    - -DI > +DI: 空头趋势
    - 买入: +DI上穿-DI，且ADX>25且上升
    - 卖出: +DI下穿-DI
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "ADX趋势强度策略 - +DI/-DI方向判断 + ADX强度过滤"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 缓存平滑值
        self.smoothed_plus_dm = {}
        self.smoothed_minus_dm = {}
        self.smoothed_tr = {}
        self.adx_values = {}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            # ADX参数
            "adx_period": 14,  # ADX周期 (默认14)
            "smoothing_period": 14,  # 平滑周期
            # 趋势强度阈值
            "strong_trend": 25,  # 强趋势阈值
            "weak_trend": 20,  # 弱趋势阈值
            "very_strong_trend": 40,  # 极强趋势阈值
            # 交易规则
            "require_strong_adx": True,  # 要求强ADX
            "require_adx_rising": True,  # 要求ADX上升
            "use_di_crossover": True,  # 使用DI交叉
            # 过滤参数
            "min_adx_for_entry": 20,  # 入场最小ADX
            "max_adx_for_entry": 50,  # 入场最大ADX (避免追高)
            "di_gap_threshold": 5,  # DI差距阈值
            # 退出规则
            "exit_on_adx_decline": True,  # ADX下降时退出
            "exit_on_di_crossover": True,  # DI交叉时退出
            # 止损
            "use_atr_stop": True,  # ATR止损
            "atr_multiplier": 2.0,  # ATR倍数
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "adx_period",
                "type": "int",
                "min": 7,
                "max": 21,
                "label": "ADX周期",
            },
            {
                "name": "strong_trend",
                "type": "int",
                "min": 20,
                "max": 30,
                "label": "强趋势阈值",
            },
            {
                "name": "weak_trend",
                "type": "int",
                "min": 15,
                "max": 25,
                "label": "弱趋势阈值",
            },
            {
                "name": "min_adx_for_entry",
                "type": "int",
                "min": 15,
                "max": 30,
                "label": "入场最小ADX",
            },
        ]

    def _calculate_adx(
        self, history: List[Dict[str, Any]], symbol: str
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        计算ADX指标

        Returns:
            (ADX, +DI, -DI)
        """
        period = self.parameters["adx_period"]

        if len(history) < period + 1:
            return None, None, None

        # 初始化或获取缓存的平滑值
        if symbol not in self.smoothed_plus_dm:
            # 首次计算，需要初始化
            plus_dm_list = []
            minus_dm_list = []
            tr_list = []

            for i in range(1, len(history)):
                curr = history[i]
                prev = history[i - 1]

                # True Range
                tr = max(
                    curr["high"] - curr["low"],
                    abs(curr["high"] - prev["close"]),
                    abs(curr["low"] - prev["close"]),
                )
                tr_list.append(tr)

                # +DM and -DM
                up_move = curr["high"] - prev["high"]
                down_move = prev["low"] - curr["low"]

                plus_dm = up_move if (up_move > down_move and up_move > 0) else 0
                minus_dm = down_move if (down_move > up_move and down_move > 0) else 0

                plus_dm_list.append(plus_dm)
                minus_dm_list.append(minus_dm)

            if len(tr_list) < period:
                return None, None, None

            # 初始平滑值 (第一个period的总和)
            self.smoothed_tr[symbol] = sum(tr_list[:period])
            self.smoothed_plus_dm[symbol] = sum(plus_dm_list[:period])
            self.smoothed_minus_dm[symbol] = sum(minus_dm_list[:period])

            # 继续平滑后续值
            for i in range(period, len(tr_list)):
                self.smoothed_tr[symbol] = self.smoothed_tr[symbol] - (self.smoothed_tr[symbol] / period) + tr_list[i]
                self.smoothed_plus_dm[symbol] = (
                    self.smoothed_plus_dm[symbol] - (self.smoothed_plus_dm[symbol] / period) + plus_dm_list[i]
                )
                self.smoothed_minus_dm[symbol] = (
                    self.smoothed_minus_dm[symbol] - (self.smoothed_minus_dm[symbol] / period) + minus_dm_list[i]
                )

            # 计算DI
            atr = self.smoothed_tr[symbol] / period
            if atr == 0:
                return None, None, None

            plus_di = (self.smoothed_plus_dm[symbol] / self.smoothed_tr[symbol]) * 100
            minus_di = (self.smoothed_minus_dm[symbol] / self.smoothed_tr[symbol]) * 100

            # 计算DX和ADX
            di_sum = plus_di + minus_di
            if di_sum == 0:
                dx = 0
            else:
                dx = abs(plus_di - minus_di) / di_sum * 100

            # 简化: 使用DX作为ADX (实际应该对DX再做一次平滑)
            adx = dx
            self.adx_values[symbol] = adx

            return adx, plus_di, minus_di

        else:
            # 使用最新数据更新
            curr = history[-1]
            prev = history[-2]

            # True Range
            tr = max(
                curr["high"] - curr["low"],
                abs(curr["high"] - prev["close"]),
                abs(curr["low"] - prev["close"]),
            )

            # +DM and -DM
            up_move = curr["high"] - prev["high"]
            down_move = prev["low"] - curr["low"]

            plus_dm = up_move if (up_move > down_move and up_move > 0) else 0
            minus_dm = down_move if (down_move > up_move and down_move > 0) else 0

            # 更新平滑值
            self.smoothed_tr[symbol] = self.smoothed_tr[symbol] - (self.smoothed_tr[symbol] / period) + tr
            self.smoothed_plus_dm[symbol] = (
                self.smoothed_plus_dm[symbol] - (self.smoothed_plus_dm[symbol] / period) + plus_dm
            )
            self.smoothed_minus_dm[symbol] = (
                self.smoothed_minus_dm[symbol] - (self.smoothed_minus_dm[symbol] / period) + minus_dm
            )

            # 计算DI
            if self.smoothed_tr[symbol] == 0:
                return None, None, None

            plus_di = (self.smoothed_plus_dm[symbol] / self.smoothed_tr[symbol]) * 100
            minus_di = (self.smoothed_minus_dm[symbol] / self.smoothed_tr[symbol]) * 100

            # 计算DX
            di_sum = plus_di + minus_di
            if di_sum == 0:
                dx = 0
            else:
                dx = abs(plus_di - minus_di) / di_sum * 100

            # 更新ADX (简化的平滑)
            prev_adx = self.adx_values.get(symbol, dx)
            adx = prev_adx + (dx - prev_adx) / period
            self.adx_values[symbol] = adx

            return adx, plus_di, minus_di

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        history = self.price_history.get(symbol, [])
        period = self.parameters["adx_period"]

        if len(history) < period + 2:
            return None

        # 计算当前ADX
        adx, plus_di, minus_di = self._calculate_adx(history, symbol)

        if adx is None or plus_di is None or minus_di is None:
            return None

        # 计算前一天的ADX (重置缓存后计算)
        # 保存当前缓存
        temp_tr = self.smoothed_tr.get(symbol)
        temp_plus = self.smoothed_plus_dm.get(symbol)
        temp_minus = self.smoothed_minus_dm.get(symbol)
        temp_adx = self.adx_values.get(symbol)

        # 清除缓存重新计算
        self.smoothed_tr.pop(symbol, None)
        self.smoothed_plus_dm.pop(symbol, None)
        self.smoothed_minus_dm.pop(symbol, None)
        self.adx_values.pop(symbol, None)

        prev_adx, prev_plus_di, prev_minus_di = self._calculate_adx(history[:-1], symbol)

        # 恢复缓存
        if temp_tr is not None:
            self.smoothed_tr[symbol] = temp_tr
            self.smoothed_plus_dm[symbol] = temp_plus
            self.smoothed_minus_dm[symbol] = temp_minus
            self.adx_values[symbol] = temp_adx

        if prev_adx is None:
            return None

        float(current_data["close"])
        has_position = position and position.get("quantity", 0) > 0

        strong_trend = self.parameters["strong_trend"]
        min_adx = self.parameters["min_adx_for_entry"]
        max_adx = self.parameters["max_adx_for_entry"]

        # ADX趋势判断
        adx_rising = adx > prev_adx
        is_strong_trend = adx >= strong_trend
        is_tradeable = min_adx <= adx <= max_adx

        # DI交叉判断
        di_golden_cross = plus_di > minus_di and prev_plus_di <= prev_minus_di
        di_death_cross = plus_di < minus_di and prev_plus_di >= prev_minus_di
        di_gap = abs(plus_di - minus_di)

        # === 买入信号 ===
        if not has_position:
            # DI金叉 + ADX确认
            if self.parameters.get("use_di_crossover") and di_golden_cross:
                # 检查ADX条件
                adx_ok = True
                if self.parameters.get("require_strong_adx"):
                    adx_ok = is_tradeable
                if self.parameters.get("require_adx_rising"):
                    adx_ok = adx_ok and adx_rising

                if adx_ok:
                    # 计算信号强度 (基于ADX和DI差距)
                    strength = min(1.0, (adx / 50) * (di_gap / 20))
                    strength = max(0.3, strength)

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"DI金叉: +DI({plus_di:.2f})上穿-DI({minus_di:.2f}), ADX={adx:.2f}",
                        metadata={
                            "adx": adx,
                            "plus_di": plus_di,
                            "minus_di": minus_di,
                            "adx_rising": adx_rising,
                            "trend_strength": "strong" if is_strong_trend else "moderate",
                        },
                    )

            # 强趋势持续 (ADX高位，+DI领先)
            if plus_di > minus_di and is_strong_trend and adx_rising:
                if di_gap >= self.parameters["di_gap_threshold"]:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=0.5,  # 中等强度，因为不是交叉信号
                        reason=f"强趋势持续: ADX={adx:.2f}, +DI={plus_di:.2f} > -DI={minus_di:.2f}",
                        metadata={
                            "adx": adx,
                            "plus_di": plus_di,
                            "minus_di": minus_di,
                            "trend_strength": "strong",
                        },
                    )

        # === 卖出信号 ===
        if has_position:
            # DI死叉
            if self.parameters.get("exit_on_di_crossover") and di_death_cross:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"DI死叉: +DI({plus_di:.2f})下穿-DI({minus_di:.2f})",
                    metadata={"adx": adx, "plus_di": plus_di, "minus_di": minus_di},
                )

            # ADX下降 (趋势减弱)
            if self.parameters.get("exit_on_adx_decline"):
                if not adx_rising and adx < strong_trend:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=0.5,  # 部分退出
                        reason=f"趋势减弱: ADX({adx:.2f})下降且<{strong_trend}",
                        metadata={"adx": adx, "prev_adx": prev_adx},
                    )

            # -DI领先且差距扩大
            if minus_di > plus_di and di_gap > self.parameters["di_gap_threshold"]:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=0.7,
                    reason=f"空头趋势明确: -DI({minus_di:.2f}) > +DI({plus_di:.2f})",
                    metadata={"adx": adx, "plus_di": plus_di, "minus_di": minus_di},
                )

        return None
