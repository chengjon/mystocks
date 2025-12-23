"""
策略基类 (Base Strategy Class)

功能说明:
- 提供策略开发的基础框架
- 定义策略必须实现的接口方法
- 提供常用的工具方法和指标计算
- 集成UnifiedDataManager进行数据访问
- 支持参数验证和回测兼容

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import date, datetime
import logging

# 导入技术指标库
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.tdx_functions import (
    MA,
    CROSS,
    RSI,
)


class BaseStrategy(ABC):
    """
    策略基类 - 所有自定义策略必须继承此类

    子类必须实现:
        - generate_signals(): 核心信号生成逻辑

    子类可选重写:
        - validate_parameters(): 自定义参数验证
        - on_before_execute(): 执行前回调
        - on_after_execute(): 执行后回调
    """

    def __init__(
        self,
        name: str,
        version: str,
        parameters: Dict,
        unified_manager=None,
        description: str = "",
    ):
        """
        初始化策略

        参数:
            name: 策略名称 (字母数字+连字符/下划线)
            version: 策略版本 (语义化版本号 X.Y.Z)
            parameters: 策略参数字典
            unified_manager: UnifiedDataManager实例 (用于数据访问)
            description: 策略描述
        """
        self.name = name
        self.version = version
        self.parameters = parameters
        self.unified_manager = unified_manager
        self.description = description

        # 策略元数据
        self.strategy_id = None  # 数据库中的策略ID
        self.created_at = datetime.now()
        self.is_active = True

        # 日志配置
        self.logger = logging.getLogger(f"Strategy.{self.name}")
        self.logger.setLevel(logging.INFO)

        # 执行统计
        self.stats = {
            "total_executions": 0,
            "total_signals": 0,
            "buy_signals": 0,
            "sell_signals": 0,
            "execution_time_seconds": 0,
        }

        # 验证参数
        self.validate_parameters()

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        核心信号生成方法 - 子类必须实现

        参数:
            data: K线数据DataFrame，必须包含:
                  - index: DatetimeIndex
                  - columns: open, high, low, close, volume

        返回:
            pd.DataFrame: 信号DataFrame，包含:
                - index: DatetimeIndex (与输入data相同)
                - signal: 信号类型 ('buy', 'sell', None)
                - strength: 信号强度 (0.0-1.0)
                - entry_price: 建议入场价格
                - indicators: 指标值字典 (可选)

        示例:
            >>> def generate_signals(self, data):
            ...     signals = pd.DataFrame(index=data.index)
            ...     signals['signal'] = None
            ...     signals['strength'] = 0.0
            ...     signals['entry_price'] = data['close']
            ...
            ...     # 计算指标
            ...     ma5 = MA(data['close'], 5)
            ...     ma20 = MA(data['close'], 20)
            ...
            ...     # 生成买入信号
            ...     buy_condition = CROSS(ma5, ma20)
            ...     signals.loc[buy_condition, 'signal'] = 'buy'
            ...     signals.loc[buy_condition, 'strength'] = 0.8
            ...
            ...     return signals
        """
        pass

    def validate_parameters(self) -> bool:
        """
        参数验证方法 - 子类可重写以添加自定义验证

        返回:
            bool: 验证是否通过

        异常:
            ValueError: 参数验证失败时抛出
        """
        if not isinstance(self.parameters, dict):
            raise ValueError("策略参数必须是字典类型")

        # 基础验证: 确保所有参数值为数字或字符串
        for key, value in self.parameters.items():
            if not isinstance(value, (int, float, str, bool)):
                raise ValueError(
                    f"参数 '{key}' 的值必须是数字、字符串或布尔类型，当前类型: {type(value)}"
                )

        return True

    def calculate_code_hash(self) -> str:
        """
        计算策略代码的SHA-256哈希值

        用于版本控制和变更追踪

        返回:
            str: 64位十六进制哈希字符串
        """
        # 获取generate_signals方法的源代码
        import inspect

        source_code = inspect.getsource(self.generate_signals)

        # 结合参数生成唯一哈希
        hash_input = f"{source_code}:{json.dumps(self.parameters, sort_keys=True)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def get_market_data(
        self, symbol: str, start_date: date, end_date: date, frequency: str = "daily"
    ) -> pd.DataFrame:
        """
        获取市场数据

        参数:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率 ('daily', 'minute', 'tick')

        返回:
            pd.DataFrame: K线数据

        异常:
            ValueError: 如果unified_manager未初始化
        """
        if self.unified_manager is None:
            raise ValueError("UnifiedDataManager未初始化，无法获取数据")

        self.logger.info(
            f"获取市场数据: {symbol}, {start_date} 至 {end_date}, 频率: {frequency}"
        )

        # 通过UnifiedDataManager获取数据
        # 注意: 实际实现需要根据UnifiedDataManager的具体接口调整
        data = self.unified_manager.load_data_by_classification(
            classification="market_data",
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
        )

        return data

    def execute(
        self, symbols: List[str], start_date: date, end_date: date, **kwargs
    ) -> Dict:
        """
        执行策略对股票池进行筛选

        参数:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 额外参数

        返回:
            dict: 执行结果
                - signals: 生成的信号列表
                - statistics: 执行统计信息
                - errors: 错误列表

        示例:
            >>> strategy = MyStrategy(...)
            >>> result = strategy.execute(
            ...     symbols=['000001', '000002'],
            ...     start_date=date(2024, 1, 1),
            ...     end_date=date(2024, 12, 31)
            ... )
            >>> print(f"生成了 {len(result['signals'])} 个信号")
        """
        self.logger.info(f"开始执行策略: {self.name} v{self.version}")
        self.logger.info(f"股票池大小: {len(symbols)}")
        self.logger.info(f"日期范围: {start_date} 至 {end_date}")

        # 执行前回调
        self.on_before_execute(symbols, start_date, end_date, **kwargs)

        all_signals = []
        errors = []
        start_time = datetime.now()

        for i, symbol in enumerate(symbols):
            try:
                self.logger.debug(f"处理股票 [{i + 1}/{len(symbols)}]: {symbol}")

                # 获取市场数据
                data = self.get_market_data(symbol, start_date, end_date)

                if data.empty:
                    self.logger.warning(f"股票 {symbol} 数据为空，跳过")
                    continue

                # 生成信号
                signals = self.generate_signals(data)

                # 过滤有效信号
                valid_signals = signals[signals["signal"].notna()]

                if len(valid_signals) > 0:
                    # 添加股票代码
                    valid_signals["symbol"] = symbol
                    valid_signals["strategy_id"] = self.strategy_id
                    all_signals.append(valid_signals)

                    self.logger.info(f"股票 {symbol} 生成 {len(valid_signals)} 个信号")

            except Exception as e:
                error_msg = f"处理股票 {symbol} 时出错: {str(e)}"
                self.logger.error(error_msg)
                errors.append(
                    {"symbol": symbol, "error": str(e), "timestamp": datetime.now()}
                )

        # 合并所有信号
        if all_signals:
            signals_df = pd.concat(all_signals, ignore_index=True)
        else:
            signals_df = pd.DataFrame()

        # 执行统计
        execution_time = (datetime.now() - start_time).total_seconds()
        self.stats["total_executions"] += 1
        self.stats["total_signals"] += len(signals_df)
        self.stats["buy_signals"] += len(signals_df[signals_df["signal"] == "buy"])
        self.stats["sell_signals"] += len(signals_df[signals_df["signal"] == "sell"])
        self.stats["execution_time_seconds"] += execution_time

        result = {
            "signals": signals_df,
            "statistics": {
                "total_symbols": len(symbols),
                "processed_symbols": len(symbols) - len(errors),
                "failed_symbols": len(errors),
                "total_signals": len(signals_df),
                "buy_signals": len(signals_df[signals_df["signal"] == "buy"]),
                "sell_signals": len(signals_df[signals_df["signal"] == "sell"]),
                "execution_time_seconds": execution_time,
            },
            "errors": errors,
        }

        # 执行后回调
        self.on_after_execute(result)

        self.logger.info(
            f"策略执行完成: 生成 {len(signals_df)} 个信号，耗时 {execution_time:.2f}秒"
        )

        return result

    def on_before_execute(
        self, symbols: List[str], start_date: date, end_date: date, **kwargs
    ):
        """
        执行前回调 - 子类可重写

        参数:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 额外参数
        """
        pass

    def on_after_execute(self, result: Dict):
        """
        执行后回调 - 子类可重写

        参数:
            result: 执行结果字典
        """
        pass

    def to_dict(self) -> Dict:
        """
        将策略转换为字典格式 (用于数据库存储)

        返回:
            dict: 策略信息字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "parameters": self.parameters,
            "code_hash": self.calculate_code_hash(),
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "stats": self.stats,
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}')>"
        )


# ===================================
# 示例策略实现
# ===================================


class MomentumStrategy(BaseStrategy):
    """
    动量策略示例 - MA交叉 + RSI过滤

    策略逻辑:
        - 买入信号: MA5上穿MA20 且 RSI < 30 (超卖)
        - 卖出信号: MA5下穿MA20 或 RSI > 70 (超买)
    """

    def __init__(self, unified_manager=None):
        parameters = {
            "ma_short": 5,
            "ma_long": 20,
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
        }

        super().__init__(
            name="ma_crossover_rsi_filter",
            version="1.0.0",
            parameters=parameters,
            unified_manager=unified_manager,
            description="移动平均交叉策略，结合RSI过滤",
        )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """实现信号生成逻辑"""
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = None
        signals["strength"] = 0.0
        signals["entry_price"] = data["close"]
        signals["indicators"] = None

        # 计算技术指标
        close = data["close"].values
        ma_short = MA(close, self.parameters["ma_short"])
        ma_long = MA(close, self.parameters["ma_long"])
        rsi = RSI(close, self.parameters["rsi_period"])

        # 交叉信号
        cross_up = CROSS(ma_short, ma_long)  # 金叉
        cross_down = CROSS(ma_long, ma_short)  # 死叉

        # 买入条件: 金叉 + RSI超卖
        buy_condition = cross_up & (rsi < self.parameters["rsi_oversold"])

        # 卖出条件: 死叉 或 RSI超买
        sell_condition = cross_down | (rsi > self.parameters["rsi_overbought"])

        # 生成信号
        signals.loc[buy_condition, "signal"] = "buy"
        signals.loc[buy_condition, "strength"] = 0.8

        signals.loc[sell_condition, "signal"] = "sell"
        signals.loc[sell_condition, "strength"] = 0.8

        # 记录指标值
        for idx in signals.index:
            if signals.loc[idx, "signal"] is not None:
                signals.at[idx, "indicators"] = {
                    "ma5": float(ma_short[data.index.get_loc(idx)]),
                    "ma20": float(ma_long[data.index.get_loc(idx)]),
                    "rsi14": float(rsi[data.index.get_loc(idx)]),
                }

        return signals


if __name__ == "__main__":
    # 测试代码
    print("策略基类测试")
    print("=" * 50)

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

    # 测试动量策略
    print("\n测试动量策略")
    strategy = MomentumStrategy()
    print(f"策略名称: {strategy.name}")
    print(f"策略版本: {strategy.version}")
    print(f"策略参数: {strategy.parameters}")
    print(f"代码哈希: {strategy.calculate_code_hash()[:16]}...")

    # 生成信号
    signals = strategy.generate_signals(test_data)
    valid_signals = signals[signals["signal"].notna()]

    print(f"\n生成信号数量: {len(valid_signals)}")
    print(f"买入信号: {len(valid_signals[valid_signals['signal'] == 'buy'])}")
    print(f"卖出信号: {len(valid_signals[valid_signals['signal'] == 'sell'])}")

    if len(valid_signals) > 0:
        print("\n前3个信号:")
        print(valid_signals.head(3))

    print("\n策略信息:")
    print(json.dumps(strategy.to_dict(), indent=2, ensure_ascii=False, default=str))

    print("\n所有测试通过！")
