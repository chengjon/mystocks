"""
动量策略模板 (Momentum Strategy Template)

策略逻辑:
- 买入信号: 短期均线上穿长期均线 + RSI超卖
- 卖出信号: 短期均线下穿长期均线 或 RSI超买

技术指标:
- MA5, MA20: 短期和长期移动平均
- RSI14: 相对强弱指标

适用场景:
- 趋势明显的市场
- 波动较大的个股

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加父目录到路径以导入BaseStrategy
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from strategy.base_strategy import BaseStrategy
from indicators.tdx_functions import MA, CROSS, RSI


class MomentumStrategy(BaseStrategy):
    """
    动量策略 - 基于均线交叉和RSI过滤

    参数说明:
        - ma_short: 短期均线周期 (默认5)
        - ma_long: 长期均线周期 (默认20)
        - rsi_period: RSI计算周期 (默认14)
        - rsi_oversold: RSI超卖阈值 (默认30)
        - rsi_overbought: RSI超买阈值 (默认70)
    """

    def __init__(
        self,
        unified_manager=None,
        ma_short: int = 5,
        ma_long: int = 20,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
    ):
        """
        初始化动量策略

        参数:
            unified_manager: UnifiedDataManager实例
            ma_short: 短期均线周期
            ma_long: 长期均线周期
            rsi_period: RSI周期
            rsi_oversold: RSI超卖阈值
            rsi_overbought: RSI超买阈值
        """
        parameters = {
            "ma_short": ma_short,
            "ma_long": ma_long,
            "rsi_period": rsi_period,
            "rsi_oversold": rsi_oversold,
            "rsi_overbought": rsi_overbought,
        }

        super().__init__(
            name="ma_crossover_rsi_filter",
            version="1.0.0",
            parameters=parameters,
            unified_manager=unified_manager,
            description="移动平均交叉策略，结合RSI过滤超买超卖",
        )

    def validate_parameters(self) -> bool:
        """参数验证"""
        super().validate_parameters()

        # 验证均线周期
        if self.parameters["ma_short"] >= self.parameters["ma_long"]:
            raise ValueError(
                f"短期均线周期({self.parameters['ma_short']})必须小于" f"长期均线周期({self.parameters['ma_long']})"
            )

        # 验证RSI阈值
        if not (0 < self.parameters["rsi_oversold"] < self.parameters["rsi_overbought"] < 100):
            raise ValueError("RSI阈值设置不合理")

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
        signals["signal"] = None
        signals["strength"] = 0.0
        signals["entry_price"] = data["close"]
        signals["indicators"] = None

        # 提取收盘价
        close = data["close"].values

        # 计算技术指标
        ma_short = MA(close, self.parameters["ma_short"])
        ma_long = MA(close, self.parameters["ma_long"])
        rsi = RSI(close, self.parameters["rsi_period"])

        # 交叉信号
        golden_cross = CROSS(ma_short, ma_long)  # 金叉 (短期上穿长期)
        death_cross = CROSS(ma_long, ma_short)  # 死叉 (长期上穿短期)

        # 买入条件: 金叉 且 RSI超卖
        buy_condition = golden_cross & (rsi < self.parameters["rsi_oversold"])

        # 卖出条件: 死叉 或 RSI超买
        sell_condition = death_cross | (rsi > self.parameters["rsi_overbought"])

        # 计算信号强度
        # 买入强度: RSI越低强度越高
        buy_strength = np.where(buy_condition, 1.0 - (rsi / self.parameters["rsi_oversold"]), 0.0)

        # 卖出强度: RSI越高强度越高
        sell_strength = np.where(
            sell_condition,
            (rsi - self.parameters["rsi_overbought"]) / (100 - self.parameters["rsi_overbought"]),
            0.0,
        )

        # 生成信号
        signals.loc[buy_condition, "signal"] = "buy"
        signals.loc[buy_condition, "strength"] = buy_strength[buy_condition]

        signals.loc[sell_condition, "signal"] = "sell"
        signals.loc[sell_condition, "strength"] = sell_strength[sell_condition]

        # 记录指标值 (用于调试和分析)
        for idx in signals.index:
            pos = data.index.get_loc(idx)
            if signals.loc[idx, "signal"] is not None:
                signals.at[idx, "indicators"] = {
                    f"ma{self.parameters['ma_short']}": (float(ma_short[pos]) if not np.isnan(ma_short[pos]) else None),
                    f"ma{self.parameters['ma_long']}": (float(ma_long[pos]) if not np.isnan(ma_long[pos]) else None),
                    f"rsi{self.parameters['rsi_period']}": (float(rsi[pos]) if not np.isnan(rsi[pos]) else None),
                }

        return signals


if __name__ == "__main__":
    # 测试代码
    print("动量策略模板测试")
    print("=" * 60)

    # 生成测试数据
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    test_data = pd.DataFrame(
        {
            "open": np.cumsum(np.random.randn(n)) + 100,
            "high": np.cumsum(np.random.randn(n)) + 105,
            "low": np.cumsum(np.random.randn(n)) + 95,
            "close": np.cumsum(np.random.randn(n)) + 100,
            "volume": np.random.uniform(1000000, 10000000, n),
        },
        index=dates,
    )

    # 创建策略实例
    strategy = MomentumStrategy(
        unified_manager=None,
        ma_short=5,
        ma_long=20,
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70,
    )

    print(f"策略名称: {strategy.name}")
    print(f"策略版本: {strategy.version}")
    print(f"策略描述: {strategy.description}")
    print("\n策略参数:")
    for key, value in strategy.parameters.items():
        print(f"  {key}: {value}")

    # 生成信号
    signals = strategy.generate_signals(test_data)
    valid_signals = signals[signals["signal"].notna()]

    print("\n信号统计:")
    print(f"  总信号数: {len(valid_signals)}")
    print(f"  买入信号: {len(valid_signals[valid_signals['signal'] == 'buy'])}")
    print(f"  卖出信号: {len(valid_signals[valid_signals['signal'] == 'sell'])}")

    if len(valid_signals) > 0:
        print("\n最近3个信号:")
        print(valid_signals[["signal", "strength", "entry_price"]].tail(3))

    print("\n测试通过！")
