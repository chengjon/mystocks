"""
自定义策略模板 (Custom Strategy Template)

使用说明:
1. 复制此模板文件
2. 修改类名为您的策略名称
3. 在__init__中定义策略参数
4. 在generate_signals中实现信号生成逻辑
5. (可选) 在validate_parameters中添加自定义参数验证
6. (可选) 在on_before_execute和on_after_execute中添加回调逻辑

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from strategy.base_strategy import BaseStrategy

# 导入您需要的技术指标
from indicators.tdx_functions import (
    MA,
    CROSS,
    RSI,
)


class CustomStrategy(BaseStrategy):
    """
    自定义策略 - 请在此处添加策略描述

    策略逻辑:
        - 买入条件: [描述您的买入条件]
        - 卖出条件: [描述您的卖出条件]

    技术指标:
        - [列出您使用的技术指标]

    参数说明:
        - param1: [参数1说明]
        - param2: [参数2说明]
    """

    def __init__(self, unified_manager=None, param1: int = 10, param2: float = 0.5):
        """
        初始化自定义策略

        参数:
            unified_manager: UnifiedDataManager实例
            param1: [参数1说明]
            param2: [参数2说明]
        """
        # 定义策略参数
        parameters = {
            "param1": param1,
            "param2": param2,
            # 添加更多参数...
        }

        # 调用父类构造函数
        super().__init__(
            name="custom_strategy",  # 修改为您的策略名称
            version="1.0.0",  # 策略版本号
            parameters=parameters,
            unified_manager=unified_manager,
            description="自定义策略描述",  # 修改为您的策略描述
        )

    def validate_parameters(self) -> bool:
        """
        参数验证 (可选)

        在此处添加您的自定义参数验证逻辑

        返回:
            bool: 验证是否通过

        示例:
            if self.parameters['param1'] <= 0:
                raise ValueError("param1必须大于0")
        """
        # 调用父类验证
        super().validate_parameters()

        # 添加您的自定义验证逻辑
        # 例如:
        # if self.parameters['param1'] <= 0:
        #     raise ValueError("param1必须大于0")

        return True

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号 - 核心策略逻辑

        这是策略的核心方法，您需要在此实现信号生成逻辑

        参数:
            data: K线数据DataFrame，包含:
                  - index: DatetimeIndex (日期索引)
                  - columns: open, high, low, close, volume

        返回:
            pd.DataFrame: 信号DataFrame，必须包含以下列:
                - signal: 信号类型 ('buy' 或 'sell' 或 None)
                - strength: 信号强度 (0.0-1.0)
                - entry_price: 建议入场价格
                - indicators: 指标值字典 (可选，用于分析)

        示例实现:
        """
        # 1. 初始化信号DataFrame
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = None
        signals["strength"] = 0.0
        signals["entry_price"] = data["close"]
        signals["indicators"] = None

        # 2. 提取价格数据
        close = data["close"].values
        data["high"].values
        data["low"].values
        data["volume"].values

        # 3. 计算技术指标
        # 示例: 计算移动平均线
        ma_short = MA(close, 5)
        ma_long = MA(close, 20)
        rsi = RSI(close, 14)

        # 4. 定义买入/卖出条件
        # 示例: 金叉买入，死叉卖出
        buy_condition = CROSS(ma_short, ma_long) & (rsi < 30)
        sell_condition = CROSS(ma_long, ma_short) | (rsi > 70)

        # 5. 计算信号强度 (可选)
        buy_strength = np.where(buy_condition, 0.8, 0.0)
        sell_strength = np.where(sell_condition, 0.8, 0.0)

        # 6. 生成信号
        signals.loc[buy_condition, "signal"] = "buy"
        signals.loc[buy_condition, "strength"] = buy_strength[buy_condition]

        signals.loc[sell_condition, "signal"] = "sell"
        signals.loc[sell_condition, "strength"] = sell_strength[sell_condition]

        # 7. 记录指标值 (可选，便于调试和分析)
        for idx in signals.index:
            pos = data.index.get_loc(idx)
            if signals.loc[idx, "signal"] is not None:
                signals.at[idx, "indicators"] = {
                    "ma5": (float(ma_short[pos]) if not np.isnan(ma_short[pos]) else None),
                    "ma20": float(ma_long[pos]) if not np.isnan(ma_long[pos]) else None,
                    "rsi14": float(rsi[pos]) if not np.isnan(rsi[pos]) else None,
                }

        return signals

    def on_before_execute(self, symbols, start_date, end_date, **kwargs):
        """
        执行前回调 (可选)

        在策略执行前调用，可用于:
        - 打印执行信息
        - 预处理数据
        - 初始化状态

        参数:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 额外参数
        """
        # 示例: 打印执行信息
        self.logger.info("策略执行开始: %s只股票", len(symbols))
        self.logger.info("日期范围: %s 至 %s", start_date, end_date)

        # 添加您的自定义逻辑...

    def on_after_execute(self, result):
        """
        执行后回调 (可选)

        在策略执行完成后调用，可用于:
        - 打印执行结果
        - 保存额外信息
        - 发送通知

        参数:
            result: 执行结果字典
        """
        # 示例: 打印执行结果
        stats = result.get("statistics", {})
        self.logger.info("执行完成: 生成%s个信号", stats.get("total_signals", 0))

        # 添加您的自定义逻辑...


# ===================================
# 使用示例
# ===================================

if __name__ == "__main__":
    print("自定义策略模板使用示例")
    print("=" * 60)

    # 1. 创建策略实例
    strategy = CustomStrategy(
        unified_manager=None,  # 实际使用时传入UnifiedDataManager实例
        param1=10,
        param2=0.5,
    )

    print(f"策略名称: {strategy.name}")
    print(f"策略版本: {strategy.version}")
    print(f"策略描述: {strategy.description}")
    print("\n策略参数:")
    for key, value in strategy.parameters.items():
        print(f"  {key}: {value}")

    # 2. 生成测试数据
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

    # 3. 生成信号
    signals = strategy.generate_signals(test_data)
    valid_signals = signals[signals["signal"].notna()]

    print("\n信号统计:")
    print(f"  总信号数: {len(valid_signals)}")
    print(f"  买入信号: {len(valid_signals[valid_signals['signal'] == 'buy'])}")
    print(f"  卖出信号: {len(valid_signals[valid_signals['signal'] == 'sell'])}")

    if len(valid_signals) > 0:
        print("\n最近3个信号:")
        print(valid_signals[["signal", "strength", "entry_price"]].tail(3))

    print("\n" + "=" * 60)
    print("开发提示:")
    print("1. 修改类名CustomStrategy为您的策略名称")
    print("2. 在__init__中定义策略参数")
    print("3. 在generate_signals中实现核心逻辑")
    print("4. 使用TDX函数库或TA-Lib计算技术指标")
    print("5. 定义清晰的买入/卖出条件")
    print("6. 记录指标值以便后续分析")
    print("=" * 60)
