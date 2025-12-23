"""
TA-Lib 技术指标包装器

功能说明:
- 封装TA-Lib库的常用技术指标函数
- 提供统一的错误处理和参数验证
- 支持pandas Series和numpy array输入
- 自动处理NaN值和数据长度校验

依赖:
- TA-Lib 0.6.7+ (使用binary wheels安装)

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

from typing import Dict, Tuple, Union

import numpy as np
import pandas as pd
import talib


class TALibIndicators:
    """
    TA-Lib技术指标包装类

    提供常用技术指标的便捷访问接口，自动处理输入数据格式和异常情况
    """

    @staticmethod
    def _to_numpy(data: Union[np.ndarray, pd.Series]) -> np.ndarray:
        """
        将输入数据转换为numpy array

        参数:
            data: 输入数据 (numpy array或pandas Series)

        返回:
            np.ndarray: 转换后的numpy数组
        """
        if isinstance(data, pd.Series):
            return data.values
        return np.array(data, dtype=float)

    @staticmethod
    def _validate_length(data: np.ndarray, min_length: int, name: str = "数据"):
        """
        验证数据长度

        参数:
            data: 输入数据
            min_length: 最小数据长度
            name: 数据名称(用于错误提示)

        异常:
            ValueError: 数据长度不足
        """
        if len(data) < min_length:
            raise ValueError(
                f"{name}长度不足: 需要至少{min_length}个数据点，当前仅有{len(data)}个"
            )

    # ===================================
    # 趋势指标 (Trend Indicators)
    # ===================================

    @classmethod
    def calculate_sma(
        cls, close: Union[np.ndarray, pd.Series], period: int = 20
    ) -> np.ndarray:
        """
        简单移动平均 (Simple Moving Average)

        参数:
            close: 收盘价序列
            period: 移动平均周期

        返回:
            np.ndarray: SMA值序列
        """
        close_arr = cls._to_numpy(close)
        cls._validate_length(close_arr, period, "收盘价")
        return talib.SMA(close_arr, timeperiod=period)

    @classmethod
    def calculate_ema(
        cls, close: Union[np.ndarray, pd.Series], period: int = 20
    ) -> np.ndarray:
        """
        指数移动平均 (Exponential Moving Average)

        参数:
            close: 收盘价序列
            period: EMA周期

        返回:
            np.ndarray: EMA值序列
        """
        close_arr = cls._to_numpy(close)
        cls._validate_length(close_arr, period, "收盘价")
        return talib.EMA(close_arr, timeperiod=period)

    @classmethod
    def calculate_wma(
        cls, close: Union[np.ndarray, pd.Series], period: int = 20
    ) -> np.ndarray:
        """
        加权移动平均 (Weighted Moving Average)

        参数:
            close: 收盘价序列
            period: WMA周期

        返回:
            np.ndarray: WMA值序列
        """
        close_arr = cls._to_numpy(close)
        cls._validate_length(close_arr, period, "收盘价")
        return talib.WMA(close_arr, timeperiod=period)

    @classmethod
    def calculate_macd(
        cls,
        close: Union[np.ndarray, pd.Series],
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        MACD指标 (Moving Average Convergence Divergence)

        参数:
            close: 收盘价序列
            fastperiod: 快速EMA周期
            slowperiod: 慢速EMA周期
            signalperiod: 信号线周期

        返回:
            tuple: (MACD线, 信号线, MACD柱)
        """
        close_arr = cls._to_numpy(close)
        cls._validate_length(close_arr, slowperiod + signalperiod, "收盘价")
        macd, signal, hist = talib.MACD(
            close_arr,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            signalperiod=signalperiod,
        )
        return macd, signal, hist

    # ===================================
    # 动量指标 (Momentum Indicators)
    # ===================================

    @classmethod
    def calculate_rsi(
        cls, close: Union[np.ndarray, pd.Series], period: int = 14
    ) -> np.ndarray:
        """
        相对强弱指标 (Relative Strength Index)

        参数:
            close: 收盘价序列
            period: RSI周期

        返回:
            np.ndarray: RSI值序列 (0-100)
        """
        close_arr = cls._to_numpy(close)
        cls._validate_length(close_arr, period + 1, "收盘价")
        return talib.RSI(close_arr, timeperiod=period)

    @classmethod
    def calculate_stoch(
        cls,
        high: Union[np.ndarray, pd.Series],
        low: Union[np.ndarray, pd.Series],
        close: Union[np.ndarray, pd.Series],
        fastk_period: int = 5,
        slowk_period: int = 3,
        slowd_period: int = 3,
    ) -> Tuple[np.ndarray, np.ndarray]:
        # pylint: disable=too-many-positional-arguments
        """
        随机指标 (Stochastic Oscillator)

        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            fastk_period: FastK周期
            slowk_period: SlowK周期
            slowd_period: SlowD周期

        返回:
            tuple: (SlowK, SlowD)
        """
        high_arr = cls._to_numpy(high)
        low_arr = cls._to_numpy(low)
        close_arr = cls._to_numpy(close)

        min_length = fastk_period + slowk_period + slowd_period
        cls._validate_length(high_arr, min_length, "最高价")

        slowk, slowd = talib.STOCH(
            high_arr,
            low_arr,
            close_arr,
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowk_matype=0,
            slowd_period=slowd_period,
            slowd_matype=0,
        )
        return slowk, slowd

    @classmethod
    def calculate_cci(
        cls,
        high: Union[np.ndarray, pd.Series],
        low: Union[np.ndarray, pd.Series],
        close: Union[np.ndarray, pd.Series],
        period: int = 14,
    ) -> np.ndarray:
        """
        顺势指标 (Commodity Channel Index)

        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: CCI周期

        返回:
            np.ndarray: CCI值序列
        """
        high_arr = cls._to_numpy(high)
        low_arr = cls._to_numpy(low)
        close_arr = cls._to_numpy(close)

        cls._validate_length(high_arr, period, "最高价")
        return talib.CCI(high_arr, low_arr, close_arr, timeperiod=period)

    @classmethod
    def calculate_mom(
        cls, close: Union[np.ndarray, pd.Series], period: int = 10
    ) -> np.ndarray:
        """
        动量指标 (Momentum)

        参数:
            close: 收盘价序列
            period: 动量周期

        返回:
            np.ndarray: 动量值序列
        """
        close_arr = cls._to_numpy(close)
        cls._validate_length(close_arr, period, "收盘价")
        return talib.MOM(close_arr, timeperiod=period)

    # ===================================
    # 波动率指标 (Volatility Indicators)
    # ===================================

    @classmethod
    def calculate_bbands(
        cls,
        close: Union[np.ndarray, pd.Series],
        period: int = 20,
        nbdevup: float = 2,
        nbdevdn: float = 2,
        matype: int = 0,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # pylint: disable=too-many-positional-arguments
        """
        计算布林带 (Bollinger Bands)

        参数:
            close: 收盘价序列
            period: 移动平均周期
            nbdevup: 上轨标准差倍数
            nbdevdn: 下轨标准差倍数

        返回:
            tuple: (上轨, 中轨, 下轨)
        """
        close_arr = cls._to_numpy(close)
        cls._validate_length(close_arr, period, "收盘价")

        upper, middle, lower = talib.BBANDS(
            close_arr, timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0
        )
        return upper, middle, lower

    @classmethod
    def calculate_atr(
        cls,
        high: Union[np.ndarray, pd.Series],
        low: Union[np.ndarray, pd.Series],
        close: Union[np.ndarray, pd.Series],
        period: int = 14,
    ) -> np.ndarray:
        """
        平均真实波幅 (Average True Range)

        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: ATR周期

        返回:
            np.ndarray: ATR值序列
        """
        high_arr = cls._to_numpy(high)
        low_arr = cls._to_numpy(low)
        close_arr = cls._to_numpy(close)

        cls._validate_length(high_arr, period, "最高价")
        return talib.ATR(high_arr, low_arr, close_arr, timeperiod=period)

    # ===================================
    # 成交量指标 (Volume Indicators)
    # ===================================

    @classmethod
    def calculate_obv(
        cls, close: Union[np.ndarray, pd.Series], volume: Union[np.ndarray, pd.Series]
    ) -> np.ndarray:
        """
        能量潮 (On Balance Volume)

        参数:
            close: 收盘价序列
            volume: 成交量序列

        返回:
            np.ndarray: OBV值序列
        """
        close_arr = cls._to_numpy(close)
        volume_arr = cls._to_numpy(volume).astype(float)  # 确保成交量为float类型

        cls._validate_length(close_arr, 2, "收盘价")
        return talib.OBV(close_arr, volume_arr)

    @classmethod
    def calculate_ad(
        cls,
        high: Union[np.ndarray, pd.Series],
        low: Union[np.ndarray, pd.Series],
        close: Union[np.ndarray, pd.Series],
        volume: Union[np.ndarray, pd.Series],
    ) -> np.ndarray:
        """
        累积/派发线 (Accumulation/Distribution Line)

        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列

        返回:
            np.ndarray: A/D线值序列
        """
        high_arr = cls._to_numpy(high)
        low_arr = cls._to_numpy(low)
        close_arr = cls._to_numpy(close)
        volume_arr = cls._to_numpy(volume).astype(float)  # 确保成交量为float类型

        cls._validate_length(high_arr, 1, "最高价")
        return talib.AD(high_arr, low_arr, close_arr, volume_arr)

    # ===================================
    # 形态识别 (Pattern Recognition)
    # ===================================

    @classmethod
    def detect_doji(
        cls,
        open_: Union[np.ndarray, pd.Series],
        high: Union[np.ndarray, pd.Series],
        low: Union[np.ndarray, pd.Series],
        close: Union[np.ndarray, pd.Series],
    ) -> np.ndarray:
        """
        十字星形态识别 (Doji)

        参数:
            open_: 开盘价序列
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列

        返回:
            np.ndarray: 形态标识 (100=看涨, -100=看跌, 0=无形态)
        """
        open_arr = cls._to_numpy(open_)
        high_arr = cls._to_numpy(high)
        low_arr = cls._to_numpy(low)
        close_arr = cls._to_numpy(close)

        return talib.CDLDOJI(open_arr, high_arr, low_arr, close_arr)

    @classmethod
    def detect_hammer(
        cls,
        open_: Union[np.ndarray, pd.Series],
        high: Union[np.ndarray, pd.Series],
        low: Union[np.ndarray, pd.Series],
        close: Union[np.ndarray, pd.Series],
    ) -> np.ndarray:
        """
        锤子线形态识别 (Hammer)

        参数:
            open_: 开盘价序列
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列

        返回:
            np.ndarray: 形态标识 (100=看涨锤子线, 0=无形态)
        """
        open_arr = cls._to_numpy(open_)
        high_arr = cls._to_numpy(high)
        low_arr = cls._to_numpy(low)
        close_arr = cls._to_numpy(close)

        return talib.CDLHAMMER(open_arr, high_arr, low_arr, close_arr)

    @classmethod
    def detect_engulfing(
        cls,
        open_: Union[np.ndarray, pd.Series],
        high: Union[np.ndarray, pd.Series],
        low: Union[np.ndarray, pd.Series],
        close: Union[np.ndarray, pd.Series],
    ) -> np.ndarray:
        """
        吞没形态识别 (Engulfing)

        参数:
            open_: 开盘价序列
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列

        返回:
            np.ndarray: 形态标识 (100=看涨吞没, -100=看跌吞没, 0=无形态)
        """
        open_arr = cls._to_numpy(open_)
        high_arr = cls._to_numpy(high)
        low_arr = cls._to_numpy(low)
        close_arr = cls._to_numpy(close)

        return talib.CDLENGULFING(open_arr, high_arr, low_arr, close_arr)

    # ===================================
    # 批量计算
    # ===================================

    @classmethod
    def calculate_all_indicators(cls, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        批量计算所有常用指标

        参数:
            df: K线数据DataFrame，需包含 open, high, low, close, volume 列

        返回:
            dict: 指标名称到值序列的映射

        示例:
            >>> indicators = TALibIndicators.calculate_all_indicators(df)
            >>> print(indicators.keys())
            dict_keys(['ma5', 'ma20', 'ema12', 'ema26', 'rsi14', ...])
        """
        required_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"数据缺少必需列: {missing_cols}")

        indicators = {}

        # 移动平均
        indicators["ma5"] = cls.calculate_sma(df["close"], 5)
        indicators["ma10"] = cls.calculate_sma(df["close"], 10)
        indicators["ma20"] = cls.calculate_sma(df["close"], 20)
        indicators["ma60"] = cls.calculate_sma(df["close"], 60)

        # EMA
        indicators["ema12"] = cls.calculate_ema(df["close"], 12)
        indicators["ema26"] = cls.calculate_ema(df["close"], 26)

        # MACD
        macd, signal, hist = cls.calculate_macd(df["close"])
        indicators["macd"] = macd
        indicators["macd_signal"] = signal
        indicators["macd_hist"] = hist

        # RSI
        indicators["rsi6"] = cls.calculate_rsi(df["close"], 6)
        indicators["rsi14"] = cls.calculate_rsi(df["close"], 14)

        # 布林带
        upper, middle, lower = cls.calculate_bbands(df["close"], 20, 2, 2)
        indicators["boll_upper"] = upper
        indicators["boll_middle"] = middle
        indicators["boll_lower"] = lower

        # ATR
        indicators["atr14"] = cls.calculate_atr(df["high"], df["low"], df["close"], 14)

        # OBV
        indicators["obv"] = cls.calculate_obv(df["close"], df["volume"])

        return indicators


if __name__ == "__main__":
    # 测试代码
    print("TA-Lib包装器测试")
    print("=" * 50)
    print(f"TA-Lib版本: {talib.__version__}")
    print(f"可用函数数量: {len(talib.get_functions())}")
    print()

    # 生成测试数据
    np.random.seed(42)
    test_n = 100
    test_df = pd.DataFrame(
        {
            "open": np.cumsum(np.random.randn(test_n)) + 100,
            "high": np.cumsum(np.random.randn(test_n)) + 105,
            "low": np.cumsum(np.random.randn(test_n)) + 95,
            "close": np.cumsum(np.random.randn(test_n)) + 100,
            "volume": np.random.uniform(1000000, 10000000, test_n),  # 使用float类型
        }
    )

    # 测试单个指标
    print("1. 测试SMA")
    test_sma20 = TALibIndicators.calculate_sma(test_df["close"], 20)
    print(f"   最后5个值: {test_sma20[-5:]}")

    print("\n2. 测试RSI")
    test_rsi14 = TALibIndicators.calculate_rsi(test_df["close"], 14)
    print(f"   最后5个值: {test_rsi14[-5:]}")

    print("\n3. 测试MACD")
    test_macd, test_signal, test_hist = TALibIndicators.calculate_macd(test_df["close"])
    print(f"   MACD最后值: {test_macd[-1]:.4f}")
    print(f"   信号线最后值: {test_signal[-1]:.4f}")
    print(f"   柱状图最后值: {test_hist[-1]:.4f}")

    print("\n4. 测试布林带")
    test_upper, test_middle, test_lower = TALibIndicators.calculate_bbands(
        test_df["close"], 20, 2, 2
    )
    print(f"   上轨最后值: {test_upper[-1]:.2f}")
    print(f"   中轨最后值: {test_middle[-1]:.2f}")
    print(f"   下轨最后值: {test_lower[-1]:.2f}")

    print("\n5. 测试批量计算")
    test_all_indicators = TALibIndicators.calculate_all_indicators(test_df)
    print(f"   计算了 {len(test_all_indicators)} 个指标")
    print(f"   指标列表: {list(test_all_indicators.keys())}")

    print("\n所有测试通过！")
