"""
KDJ Strategy

KDJ随机指标策略 - 超买超卖与金叉死叉结合
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class KDJStrategy(BaseStrategy):
    """
    KDJ随机指标策略

    核心逻辑:
    - KDJ指标是随机指标的改进版本
    - RSV = (C - Ln) / (Hn - Ln) × 100
    - K = EMA(RSV, 3)
    - D = EMA(K, 3)
    - J = 3K - 2D

    交易信号:
    - 金叉买入: K上穿D，且处于超卖区
    - 死叉卖出: K下穿D，且处于超买区
    - 超买: K>80, D>80, J>100
    - 超卖: K<20, D<20, J<0

    适用场景:
    - 震荡市场
    - 短线交易
    - 与趋势指标配合使用
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "KDJ随机指标策略 - 超买超卖判断 + 金叉死叉信号"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 缓存KDJ值
        self.k_values = {}
        self.d_values = {}
        self.j_values = {}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            # KDJ参数
            'n_period': 9,            # RSV周期 (默认9)
            'k_period': 3,            # K值平滑周期
            'd_period': 3,            # D值平滑周期

            # 超买超卖阈值
            'overbought_k': 80,       # K超买阈值
            'oversold_k': 20,         # K超卖阈值
            'overbought_d': 80,       # D超买阈值
            'oversold_d': 20,         # D超卖阈值
            'overbought_j': 100,      # J超买阈值
            'oversold_j': 0,          # J超卖阈值

            # 信号确认
            'require_extreme_area': True,  # 要求在极值区域
            'use_j_filter': True,          # 使用J值过滤
            'crossover_confirm': 1,        # 交叉确认天数

            # 钝化处理
            'handle_divergence': True,     # 处理背离
            'max_overbought_days': 5,      # 超买区最大天数

            # 趋势过滤
            'use_trend_filter': False,     # 使用趋势过滤
            'trend_ma_period': 30,         # 趋势均线周期
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {'name': 'n_period', 'type': 'int', 'min': 5, 'max': 20, 'label': 'RSV周期'},
            {'name': 'k_period', 'type': 'int', 'min': 2, 'max': 5, 'label': 'K平滑'},
            {'name': 'd_period', 'type': 'int', 'min': 2, 'max': 5, 'label': 'D平滑'},
            {'name': 'overbought_k', 'type': 'int', 'min': 70, 'max': 90, 'label': 'K超买'},
            {'name': 'oversold_k', 'type': 'int', 'min': 10, 'max': 30, 'label': 'K超卖'},
        ]

    def _calculate_kdj(self, history: List[Dict[str, Any]]) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        计算KDJ指标

        Returns:
            (K值, D值, J值)
        """
        n_period = self.parameters['n_period']

        if len(history) < n_period:
            return None, None, None

        # 1. 计算RSV (Raw Stochastic Value)
        recent_data = history[-n_period:]
        highs = [d['high'] for d in recent_data]
        lows = [d['low'] for d in recent_data]
        close = history[-1]['close']

        highest = max(highs)
        lowest = min(lows)

        if highest == lowest:
            rsv = 50  # 避免除零
        else:
            rsv = (close - lowest) / (highest - lowest) * 100

        # 2. 计算K值 (RSV的EMA)
        # K = 2/3 × 前K + 1/3 × RSV
        symbol = history[-1].get('symbol', 'unknown')
        prev_k = self.k_values.get(symbol, 50)  # 初始K=50

        k_smoothing = 2.0 / (self.parameters['k_period'] + 1)
        k_value = prev_k * (1 - k_smoothing) + rsv * k_smoothing

        # 3. 计算D值 (K的EMA)
        # D = 2/3 × 前D + 1/3 × K
        prev_d = self.d_values.get(symbol, 50)  # 初始D=50

        d_smoothing = 2.0 / (self.parameters['d_period'] + 1)
        d_value = prev_d * (1 - d_smoothing) + k_value * d_smoothing

        # 4. 计算J值
        # J = 3K - 2D
        j_value = 3 * k_value - 2 * d_value

        # 缓存当前值
        self.k_values[symbol] = k_value
        self.d_values[symbol] = d_value
        self.j_values[symbol] = j_value

        return k_value, d_value, j_value

    def _check_golden_cross(self, k: float, d: float, prev_k: float, prev_d: float) -> bool:
        """检测金叉: K上穿D"""
        return k > d and prev_k <= prev_d

    def _check_death_cross(self, k: float, d: float, prev_k: float, prev_d: float) -> bool:
        """检测死叉: K下穿D"""
        return k < d and prev_k >= prev_d

    def _is_oversold(self, k: float, d: float, j: float) -> bool:
        """判断是否超卖"""
        k_oversold = k < self.parameters['oversold_k']
        d_oversold = d < self.parameters['oversold_d']

        if self.parameters.get('use_j_filter'):
            j_oversold = j < self.parameters['oversold_j']
            return k_oversold and d_oversold and j_oversold

        return k_oversold and d_oversold

    def _is_overbought(self, k: float, d: float, j: float) -> bool:
        """判断是否超买"""
        k_overbought = k > self.parameters['overbought_k']
        d_overbought = d > self.parameters['overbought_d']

        if self.parameters.get('use_j_filter'):
            j_overbought = j > self.parameters['overbought_j']
            return k_overbought and d_overbought and j_overbought

        return k_overbought and d_overbought

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        history = self.price_history.get(symbol, [])
        n_period = self.parameters['n_period']

        if len(history) < n_period + 1:
            return None

        # 计算当前KDJ
        k, d, j = self._calculate_kdj(history)

        if k is None or d is None or j is None:
            return None

        # 计算前一天的KDJ (用于检测交叉)
        # 临时保存当前值
        temp_k = self.k_values.get(symbol)
        temp_d = self.d_values.get(symbol)
        temp_j = self.j_values.get(symbol)

        prev_k, prev_d, prev_j = self._calculate_kdj(history[:-1])

        # 恢复当前值
        if temp_k is not None:
            self.k_values[symbol] = temp_k
            self.d_values[symbol] = temp_d
            self.j_values[symbol] = temp_j

        if prev_k is None or prev_d is None:
            return None

        current_price = float(current_data['close'])
        has_position = position and position.get('quantity', 0) > 0

        # 趋势过滤
        if self.parameters.get('use_trend_filter'):
            closes = self.get_closes(symbol)
            trend_period = self.parameters['trend_ma_period']
            if len(closes) >= trend_period:
                trend_ma = self.sma(closes, trend_period)
                # 只在价格高于趋势均线时做多
                if not has_position and trend_ma and current_price < trend_ma:
                    return None

        # === 买入信号 (金叉 + 超卖) ===
        if not has_position:
            if self._check_golden_cross(k, d, prev_k, prev_d):
                # 是否要求在超卖区域
                if self.parameters.get('require_extreme_area'):
                    # 至少有一个在超卖区
                    if not (prev_k < self.parameters['oversold_k'] or
                           prev_d < self.parameters['oversold_d']):
                        return None

                # 计算信号强度 (基于超卖程度)
                oversold_degree = 0
                if k < self.parameters['oversold_k']:
                    oversold_degree += (self.parameters['oversold_k'] - k) / self.parameters['oversold_k']
                if d < self.parameters['oversold_d']:
                    oversold_degree += (self.parameters['oversold_d'] - d) / self.parameters['oversold_d']

                strength = min(1.0, 0.5 + oversold_degree / 2)

                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.LONG,
                    strength=strength,
                    reason=f"KDJ金叉: K({k:.2f}) 上穿 D({d:.2f}), J={j:.2f}",
                    metadata={
                        'k': k,
                        'd': d,
                        'j': j,
                        'oversold': self._is_oversold(k, d, j)
                    }
                )

        # === 卖出信号 (死叉 + 超买) ===
        if has_position:
            if self._check_death_cross(k, d, prev_k, prev_d):
                # 是否要求在超买区域
                if self.parameters.get('require_extreme_area'):
                    # 至少有一个在超买区
                    if not (prev_k > self.parameters['overbought_k'] or
                           prev_d > self.parameters['overbought_d']):
                        return None

                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"KDJ死叉: K({k:.2f}) 下穿 D({d:.2f}), J={j:.2f}",
                    metadata={
                        'k': k,
                        'd': d,
                        'j': j,
                        'overbought': self._is_overbought(k, d, j)
                    }
                )

            # J值极端超买卖出
            if self.parameters.get('use_j_filter'):
                if j > 120:  # J值严重超买
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=0.5,  # 部分退出
                        reason=f"J值严重超买: J={j:.2f} > 120",
                        metadata={'k': k, 'd': d, 'j': j}
                    )

        return None
