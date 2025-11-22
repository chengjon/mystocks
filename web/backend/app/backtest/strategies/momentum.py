"""
Momentum Strategy

动量策略模板 - 追涨杀跌
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class MomentumStrategy(BaseStrategy):
    """
    动量策略

    核心逻辑：
    - 价格突破均线一定比例时买入
    - 价格跌破均线一定比例时卖出
    - 结合RSI过滤超买超卖
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "动量策略 - 追踪价格趋势，突破均线买入，跌破均线卖出"

        # 默认参数
        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            'ma_period': 20,           # 均线周期
            'breakout_pct': 0.02,      # 突破百分比 (2%)
            'breakdown_pct': 0.02,     # 跌破百分比 (2%)
            'rsi_period': 14,          # RSI周期
            'rsi_overbought': 70,      # RSI超买阈值
            'rsi_oversold': 30,        # RSI超卖阈值
            'use_rsi_filter': True,    # 是否使用RSI过滤
            'volume_confirm': True,    # 是否需要成交量确认
            'volume_ratio': 1.5        # 成交量倍数
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {'name': 'ma_period', 'type': 'int', 'min': 5, 'max': 200, 'label': '均线周期'},
            {'name': 'breakout_pct', 'type': 'float', 'min': 0.01, 'max': 0.10, 'label': '突破百分比'},
            {'name': 'breakdown_pct', 'type': 'float', 'min': 0.01, 'max': 0.10, 'label': '跌破百分比'},
            {'name': 'rsi_period', 'type': 'int', 'min': 5, 'max': 50, 'label': 'RSI周期'},
            {'name': 'rsi_overbought', 'type': 'int', 'min': 60, 'max': 90, 'label': 'RSI超买'},
            {'name': 'rsi_oversold', 'type': 'int', 'min': 10, 'max': 40, 'label': 'RSI超卖'},
        ]

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        # 更新历史数据
        self.update_history(symbol, current_data)

        # 获取参数
        ma_period = self.parameters['ma_period']
        breakout_pct = self.parameters['breakout_pct']
        breakdown_pct = self.parameters['breakdown_pct']

        # 获取价格序列
        closes = self.get_closes(symbol)
        if len(closes) < ma_period:
            return None

        # 计算均线
        ma = self.sma(closes, ma_period)
        if ma is None:
            return None

        current_price = float(current_data['close'])
        has_position = position and position.get('quantity', 0) > 0

        # 计算RSI（可选）
        rsi_value = None
        if self.parameters.get('use_rsi_filter'):
            rsi_value = self.rsi(closes, self.parameters['rsi_period'])

        # 成交量确认（可选）
        volume_confirmed = True
        if self.parameters.get('volume_confirm'):
            volumes = self.get_volumes(symbol)
            if len(volumes) >= ma_period:
                avg_volume = sum(volumes[-ma_period:]) / ma_period
                current_volume = int(current_data.get('volume', 0))
                volume_confirmed = current_volume > avg_volume * self.parameters['volume_ratio']

        # 买入信号
        if not has_position:
            breakout_price = ma * (1 + breakout_pct)

            if current_price > breakout_price:
                # RSI过滤
                if rsi_value and rsi_value > self.parameters['rsi_overbought']:
                    return None  # RSI超买，不买入

                # 成交量确认
                if not volume_confirmed:
                    return None

                strength = min(1.0, (current_price - breakout_price) / breakout_price / 0.05)

                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.LONG,
                    strength=strength,
                    reason=f"价格{current_price:.2f}突破MA{ma_period}({ma:.2f})的{breakout_pct*100}%"
                )

        # 卖出信号
        if has_position:
            breakdown_price = ma * (1 - breakdown_pct)

            if current_price < breakdown_price:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"价格{current_price:.2f}跌破MA{ma_period}({ma:.2f})的{breakdown_pct*100}%"
                )

            # RSI超卖可以考虑减仓
            if rsi_value and rsi_value < self.parameters['rsi_oversold']:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=0.5,
                    reason=f"RSI={rsi_value:.1f}进入超卖区域"
                )

        return None
