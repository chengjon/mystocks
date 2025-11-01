"""
均值回归策略模板 (Mean Reversion Strategy Template)

策略逻辑:
- 买入信号: 价格触及布林带下轨 + RSI超卖
- 卖出信号: 价格触及布林带上轨 + RSI超买

技术指标:
- BOLL (20, 2): 布林带
- RSI14: 相对强弱指标

适用场景:
- 震荡市场
- 价格围绕均值波动的个股

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
from datetime import date
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from strategy.base_strategy import BaseStrategy
from indicators.tdx_functions import BOLL, RSI


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略 - 基于布林带和RSI

    参数说明:
        - boll_period: 布林带周期 (默认20)
        - boll_std_dev: 布林带标准差倍数 (默认2)
        - rsi_period: RSI计算周期 (默认14)
        - rsi_oversold: RSI超卖阈值 (默认30)
        - rsi_overbought: RSI超买阈值 (默认70)
        - price_touch_threshold: 价格触及阈值 (默认0.01, 即1%)
    """

    def __init__(self,
                 unified_manager=None,
                 boll_period: int = 20,
                 boll_std_dev: float = 2.0,
                 rsi_period: int = 14,
                 rsi_oversold: float = 30,
                 rsi_overbought: float = 70,
                 price_touch_threshold: float = 0.01):
        """
        初始化均值回归策略

        参数:
            unified_manager: UnifiedDataManager实例
            boll_period: 布林带周期
            boll_std_dev: 布林带标准差倍数
            rsi_period: RSI周期
            rsi_oversold: RSI超卖阈值
            rsi_overbought: RSI超买阈值
            price_touch_threshold: 价格触及阈值比例
        """
        parameters = {
            'boll_period': boll_period,
            'boll_std_dev': boll_std_dev,
            'rsi_period': rsi_period,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'price_touch_threshold': price_touch_threshold
        }

        super().__init__(
            name='boll_rsi_mean_reversion',
            version='1.0.0',
            parameters=parameters,
            unified_manager=unified_manager,
            description='布林带均值回归策略，结合RSI确认超买超卖'
        )

    def validate_parameters(self) -> bool:
        """参数验证"""
        super().validate_parameters()

        # 验证RSI阈值
        if not (0 < self.parameters['rsi_oversold'] < self.parameters['rsi_overbought'] < 100):
            raise ValueError("RSI阈值设置不合理")

        # 验证布林带参数
        if self.parameters['boll_std_dev'] <= 0:
            raise ValueError("布林带标准差倍数必须大于0")

        if self.parameters['price_touch_threshold'] <= 0 or self.parameters['price_touch_threshold'] > 0.1:
            raise ValueError("价格触及阈值必须在(0, 0.1]范围内")

        return True

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号

        参数:
            data: K线数据，包含 open, high, low, close, volume

        返回:
            pd.DataFrame: 信号数据
        """
        # 初始化信号DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = None
        signals['strength'] = 0.0
        signals['entry_price'] = data['close']
        signals['indicators'] = None

        # 提取收盘价
        close = data['close'].values

        # 计算技术指标
        upper, middle, lower = BOLL(
            close,
            self.parameters['boll_period'],
            self.parameters['boll_std_dev']
        )
        rsi = RSI(close, self.parameters['rsi_period'])

        # 计算价格与布林带的距离比例
        threshold = self.parameters['price_touch_threshold']

        # 下轨距离 (负值表示价格低于下轨)
        lower_distance = (close - lower) / lower

        # 上轨距离 (负值表示价格高于上轨)
        upper_distance = (upper - close) / upper

        # 买入条件: 价格触及或突破下轨 + RSI超卖
        touch_lower = lower_distance <= threshold
        buy_condition = touch_lower & (rsi < self.parameters['rsi_oversold'])

        # 卖出条件: 价格触及或突破上轨 + RSI超买
        touch_upper = upper_distance <= threshold
        sell_condition = touch_upper & (rsi > self.parameters['rsi_overbought'])

        # 计算信号强度
        # 买入强度: 价格越接近下轨、RSI越低，强度越高
        buy_strength = np.where(
            buy_condition,
            (1.0 - rsi / self.parameters['rsi_oversold']) *
            (1.0 - np.maximum(lower_distance, 0) / threshold),
            0.0
        )

        # 卖出强度: 价格越接近上轨、RSI越高，强度越高
        sell_strength = np.where(
            sell_condition,
            ((rsi - self.parameters['rsi_overbought']) / (100 - self.parameters['rsi_overbought'])) *
            (1.0 - np.maximum(upper_distance, 0) / threshold),
            0.0
        )

        # 生成信号
        signals.loc[buy_condition, 'signal'] = 'buy'
        signals.loc[buy_condition, 'strength'] = buy_strength[buy_condition]

        signals.loc[sell_condition, 'signal'] = 'sell'
        signals.loc[sell_condition, 'strength'] = sell_strength[sell_condition]

        # 记录指标值
        for idx in signals.index:
            pos = data.index.get_loc(idx)
            if signals.loc[idx, 'signal'] is not None:
                signals.at[idx, 'indicators'] = {
                    'boll_upper': float(upper[pos]) if not np.isnan(upper[pos]) else None,
                    'boll_middle': float(middle[pos]) if not np.isnan(middle[pos]) else None,
                    'boll_lower': float(lower[pos]) if not np.isnan(lower[pos]) else None,
                    f'rsi{self.parameters["rsi_period"]}': float(rsi[pos]) if not np.isnan(rsi[pos]) else None,
                    'lower_distance_pct': float(lower_distance[pos] * 100),
                    'upper_distance_pct': float(upper_distance[pos] * 100)
                }

        return signals


if __name__ == '__main__':
    # 测试代码
    print("均值回归策略模板测试")
    print("=" * 60)

    # 生成测试数据 (模拟震荡市场)
    np.random.seed(42)
    n = 100
    dates = pd.date_range('2024-01-01', periods=n, freq='D')

    # 生成震荡价格数据
    trend = 100
    noise = np.random.randn(n) * 2
    close_prices = trend + noise

    test_data = pd.DataFrame({
        'open': close_prices + np.random.randn(n) * 0.5,
        'high': close_prices + np.abs(np.random.randn(n)) * 1.5,
        'low': close_prices - np.abs(np.random.randn(n)) * 1.5,
        'close': close_prices,
        'volume': np.random.uniform(1000000, 10000000, n)
    }, index=dates)

    # 创建策略实例
    strategy = MeanReversionStrategy(
        unified_manager=None,
        boll_period=20,
        boll_std_dev=2.0,
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70,
        price_touch_threshold=0.01
    )

    print(f"策略名称: {strategy.name}")
    print(f"策略版本: {strategy.version}")
    print(f"策略描述: {strategy.description}")
    print(f"\n策略参数:")
    for key, value in strategy.parameters.items():
        print(f"  {key}: {value}")

    # 生成信号
    signals = strategy.generate_signals(test_data)
    valid_signals = signals[signals['signal'].notna()]

    print(f"\n信号统计:")
    print(f"  总信号数: {len(valid_signals)}")
    print(f"  买入信号: {len(valid_signals[valid_signals['signal'] == 'buy'])}")
    print(f"  卖出信号: {len(valid_signals[valid_signals['signal'] == 'sell'])}")

    if len(valid_signals) > 0:
        print(f"  平均信号强度: {valid_signals['strength'].mean():.3f}")
        print(f"\n最近3个信号:")
        print(valid_signals[['signal', 'strength', 'entry_price']].tail(3))

    print("\n测试通过！")
