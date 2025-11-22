"""
SAR Strategy

SAR抛物线转向策略 - 趋势跟踪与止损合一
Parabolic Stop And Reverse
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class SARStrategy(BaseStrategy):
    """
    SAR抛物线转向策略

    核心逻辑:
    - SAR(n) = SAR(n-1) + AF × (EP - SAR(n-1))
    - AF: 加速因子 (0.02起始，每次新高/新低增加0.02，最大0.20)
    - EP: 极值点 (上升趋势中的最高价/下降趋势中的最低价)

    交易信号:
    - 价格 > SAR: 上升趋势，持有或买入
    - 价格 < SAR: 下降趋势，卖出或做空
    - 价格穿越SAR: 趋势反转，反向操作

    特点:
    - 天然的移动止损线
    - 简单明确的入场退出信号
    - 适合趋势明确的市场
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "SAR抛物线转向策略 - 趋势跟踪 + 动态止损"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 缓存SAR状态
        self.sar_values = {}  # {symbol: sar}
        self.af_values = {}   # {symbol: af}
        self.ep_values = {}   # {symbol: ep}
        self.is_uptrend = {}  # {symbol: True/False}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            # SAR参数
            'initial_af': 0.02,        # 初始加速因子
            'af_increment': 0.02,      # AF增量
            'max_af': 0.20,            # 最大AF

            # 信号确认
            'confirm_bars': 1,         # 确认K线数
            'require_volume': False,   # 要求成交量确认
            'volume_ratio': 1.2,       # 成交量倍数

            # 入场过滤
            'use_trend_filter': False,  # 使用趋势过滤
            'trend_ma_period': 50,      # 趋势均线周期
            'min_trend_days': 3,        # 最小趋势持续天数

            # 退出规则
            'exit_on_reversal': True,   # 反转时退出
            'use_trailing_sar': True,   # 使用SAR作为移动止损

            # 仓位管理
            'position_sizing': 'fixed',  # fixed/dynamic
            'base_position_size': 0.3,   # 基础仓位

            # 回看周期
            'lookback_period': 5,        # 初始化回看周期
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {'name': 'initial_af', 'type': 'float', 'min': 0.01, 'max': 0.05, 'label': '初始AF'},
            {'name': 'af_increment', 'type': 'float', 'min': 0.01, 'max': 0.05, 'label': 'AF增量'},
            {'name': 'max_af', 'type': 'float', 'min': 0.10, 'max': 0.30, 'label': '最大AF'},
            {'name': 'lookback_period', 'type': 'int', 'min': 3, 'max': 10, 'label': '回看周期'},
        ]

    def _initialize_sar(self, history: List[Dict[str, Any]], symbol: str):
        """初始化SAR值"""
        lookback = self.parameters['lookback_period']

        if len(history) < lookback:
            return

        recent = history[-lookback:]
        highs = [d['high'] for d in recent]
        lows = [d['low'] for d in recent]

        highest = max(highs)
        lowest = min(lows)

        # 判断初始趋势方向
        first_close = recent[0]['close']
        last_close = recent[-1]['close']

        if last_close > first_close:
            # 上升趋势
            self.is_uptrend[symbol] = True
            self.sar_values[symbol] = lowest  # SAR在价格下方
            self.ep_values[symbol] = highest
        else:
            # 下降趋势
            self.is_uptrend[symbol] = False
            self.sar_values[symbol] = highest  # SAR在价格上方
            self.ep_values[symbol] = lowest

        self.af_values[symbol] = self.parameters['initial_af']

    def _calculate_sar(self, current_data: Dict[str, Any], symbol: str) -> Optional[float]:
        """
        计算下一个SAR值

        Returns:
            当前SAR值
        """
        if symbol not in self.sar_values:
            return None

        sar = self.sar_values[symbol]
        af = self.af_values[symbol]
        ep = self.ep_values[symbol]
        uptrend = self.is_uptrend[symbol]

        current_high = current_data['high']
        current_low = current_data['low']
        current_close = current_data['close']

        initial_af = self.parameters['initial_af']
        af_increment = self.parameters['af_increment']
        max_af = self.parameters['max_af']

        # 检查是否需要反转
        if uptrend:
            # 上升趋势中，价格跌破SAR -> 反转为下降趋势
            if current_low < sar:
                self.is_uptrend[symbol] = False
                self.sar_values[symbol] = ep  # 新SAR为之前的极值点
                self.ep_values[symbol] = current_low
                self.af_values[symbol] = initial_af
                return self.sar_values[symbol]

            # 继续上升趋势
            # 更新极值点
            if current_high > ep:
                self.ep_values[symbol] = current_high
                # 增加AF
                if af < max_af:
                    self.af_values[symbol] = min(af + af_increment, max_af)

            # 计算新SAR
            new_sar = sar + af * (ep - sar)

            # SAR不能高于前两天的最低价
            history = self.price_history.get(symbol, [])
            if len(history) >= 2:
                prev_low = history[-2]['low']
                prev_prev_low = history[-3]['low'] if len(history) >= 3 else prev_low
                new_sar = min(new_sar, prev_low, prev_prev_low)

            self.sar_values[symbol] = new_sar

        else:
            # 下降趋势中，价格突破SAR -> 反转为上升趋势
            if current_high > sar:
                self.is_uptrend[symbol] = True
                self.sar_values[symbol] = ep  # 新SAR为之前的极值点
                self.ep_values[symbol] = current_high
                self.af_values[symbol] = initial_af
                return self.sar_values[symbol]

            # 继续下降趋势
            # 更新极值点
            if current_low < ep:
                self.ep_values[symbol] = current_low
                # 增加AF
                if af < max_af:
                    self.af_values[symbol] = min(af + af_increment, max_af)

            # 计算新SAR
            new_sar = sar - af * (sar - ep)

            # SAR不能低于前两天的最高价
            history = self.price_history.get(symbol, [])
            if len(history) >= 2:
                prev_high = history[-2]['high']
                prev_prev_high = history[-3]['high'] if len(history) >= 3 else prev_high
                new_sar = max(new_sar, prev_high, prev_prev_high)

            self.sar_values[symbol] = new_sar

        return self.sar_values[symbol]

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        history = self.price_history.get(symbol, [])
        lookback = self.parameters['lookback_period']

        if len(history) < lookback + 1:
            return None

        # 初始化SAR (如果尚未初始化)
        if symbol not in self.sar_values:
            self._initialize_sar(history[:-1], symbol)
            if symbol not in self.sar_values:
                return None

        # 记录当前趋势状态
        prev_uptrend = self.is_uptrend.get(symbol)

        # 计算当前SAR
        sar = self._calculate_sar(current_data, symbol)

        if sar is None:
            return None

        current_price = float(current_data['close'])
        current_uptrend = self.is_uptrend[symbol]
        has_position = position and position.get('quantity', 0) > 0

        # 检测趋势反转
        trend_reversed = prev_uptrend != current_uptrend

        # 趋势过滤
        trend_aligned = True
        if self.parameters.get('use_trend_filter'):
            closes = self.get_closes(symbol)
            trend_period = self.parameters['trend_ma_period']
            if len(closes) >= trend_period:
                trend_ma = self.sma(closes, trend_period)
                if trend_ma:
                    # 只在价格高于趋势均线时做多
                    trend_aligned = current_price > trend_ma

        # 成交量确认
        volume_confirmed = True
        if self.parameters.get('require_volume'):
            volumes = self.get_volumes(symbol)
            if len(volumes) >= 20:
                avg_volume = sum(volumes[-20:]) / 20
                current_volume = int(current_data.get('volume', 0))
                volume_confirmed = current_volume >= avg_volume * self.parameters['volume_ratio']

        # === 买入信号 ===
        if not has_position:
            # 上升趋势 (价格 > SAR)
            if current_uptrend:
                # 如果是刚反转到上升趋势
                if trend_reversed and trend_aligned and volume_confirmed:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=0.8,
                        reason=f"SAR反转向上: 价格{current_price:.2f} > SAR{sar:.2f}",
                        stop_loss=Decimal(str(sar)),  # SAR作为止损
                        metadata={
                            'sar': sar,
                            'af': self.af_values[symbol],
                            'ep': self.ep_values[symbol],
                            'trend': 'up',
                            'reversal': True
                        }
                    )

                # 持续上升趋势中的入场
                elif trend_aligned:
                    # 计算SAR与价格的距离百分比
                    distance_pct = (current_price - sar) / current_price

                    # 只在SAR距离适中时入场 (避免追高)
                    if 0.01 <= distance_pct <= 0.05:
                        return StrategySignal(
                            symbol=symbol,
                            signal_type=SignalType.LONG,
                            strength=0.5,
                            reason=f"SAR上升趋势: 价格{current_price:.2f}, SAR{sar:.2f} (距离{distance_pct*100:.1f}%)",
                            stop_loss=Decimal(str(sar)),
                            metadata={
                                'sar': sar,
                                'af': self.af_values[symbol],
                                'trend': 'up'
                            }
                        )

        # === 卖出信号 ===
        if has_position:
            # 反转到下降趋势
            if self.parameters.get('exit_on_reversal'):
                if not current_uptrend and trend_reversed:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"SAR反转向下: 价格{current_price:.2f} < SAR{sar:.2f}",
                        metadata={
                            'sar': sar,
                            'trend': 'down',
                            'reversal': True
                        }
                    )

            # SAR移动止损触发
            if self.parameters.get('use_trailing_sar'):
                if current_uptrend and current_price <= sar:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"SAR止损触发: 价格{current_price:.2f} <= SAR{sar:.2f}",
                        metadata={'sar': sar, 'triggered': 'stop_loss'}
                    )

            # 下降趋势中持有
            if not current_uptrend:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=0.7,
                    reason=f"下降趋势: 价格{current_price:.2f}, SAR{sar:.2f}",
                    metadata={'sar': sar, 'trend': 'down'}
                )

        return None

    def get_current_sar(self, symbol: str) -> Optional[float]:
        """获取当前SAR值 (供外部调用)"""
        return self.sar_values.get(symbol)

    def get_current_trend(self, symbol: str) -> Optional[str]:
        """获取当前趋势 (供外部调用)"""
        if symbol in self.is_uptrend:
            return 'up' if self.is_uptrend[symbol] else 'down'
        return None
