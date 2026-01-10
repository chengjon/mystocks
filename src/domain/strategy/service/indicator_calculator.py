"""
Indicator Calculator Interface
指标计算器接口

定义技术指标计算的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd


class IIndicatorCalculator(ABC):
    """
    指标计算器接口

    职责：
    - 定义技术指标计算的抽象接口
    - 支持多种指标类型的计算
    - 隔离具体实现（CPU/GPU）

    实现方式：
    - CPU实现：使用 Pandas/TA-Lib
    - GPU实现：使用 cuDF/cuML（Infrastructure层）
    """

    @abstractmethod
    def calculate_rsi(
        self, data: pd.DataFrame, period: int = 14
    ) -> pd.Series:
        """
        计算RSI指标

        Args:
            data: 价格数据（必须包含 'close' 列）
            period: RSI周期

        Returns:
            RSI值序列
        """
        pass

    @abstractmethod
    def calculate_macd(
        self,
        data: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Dict[str, pd.Series]:
        """
        计算MACD指标

        Args:
            data: 价格数据（必须包含 'close' 列）
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期

        Returns:
            包含 'macd', 'signal', 'histogram' 的字典
        """
        pass

    @abstractmethod
    def calculate_ma(
        self, data: pd.DataFrame, period: int = 20, ma_type: str = "SMA"
    ) -> pd.Series:
        """
        计算移动平均线

        Args:
            data: 价格数据（必须包含 'close' 列）
            period: 周期
            ma_type: 类型（SMA, EMA, etc.）

        Returns:
            MA值序列
        """
        pass

    @abstractmethod
    def calculate_bollinger_bands(
        self, data: pd.DataFrame, period: int = 20, std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        计算布林带

        Args:
            data: 价格数据（必须包含 'close' 列）
            period: 周期
            std_dev: 标准差倍数

        Returns:
            包含 'upper', 'middle', 'lower' 的字典
        """
        pass

    @abstractmethod
    def calculate_atr(
        self, data: pd.DataFrame, period: int = 14
    ) -> pd.Series:
        """
        计算ATR（Average True Range）

        Args:
            data: 价格数据（必须包含 'high', 'low', 'close' 列）
            period: 周期

        Returns:
            ATR值序列
        """
        pass

    @abstractmethod
    def calculate_stochastic(
        self,
        data: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3,
    ) -> Dict[str, pd.Series]:
        """
        计算随机指标（KD/Stochastic Oscillator）

        Args:
            data: 价格数据（必须包含 'high', 'low', 'close' 列）
            k_period: K线周期
            d_period: D线周期

        Returns:
            包含 'k', 'd' 的字典
        """
        pass

    @abstractmethod
    def batch_calculate(
        self, data: pd.DataFrame, indicators: List[Dict[str, Any]]
    ) -> Dict[str, pd.Series]:
        """
        批量计算多个指标

        Args:
            data: 价格数据
            indicators: 指标配置列表，每个配置包含：
                - name: 指标名称
                - params: 指标参数
                - type: 指标类型（rsi, macd, ma, etc.）

        Returns:
            指标值字典 {indicator_name: pd.Series}
        """
        pass
