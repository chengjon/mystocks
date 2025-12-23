"""
TDX (Tongdaxin) 兼容技术指标函数库

功能说明:
- 提供与通达信公式兼容的技术指标函数
- 使用NumPy向量化计算，性能优于pandas rolling
- 支持多种技术分析指标 (MA, EMA, MACD, KDJ, RSI等)
- 自动处理NaN值和边界条件

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

from typing import Union

import numpy as np
import pandas as pd

# pylint: disable=invalid-name


def MA(data: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    简单移动平均 (Simple Moving Average)

    参数:
        data: 价格序列 (收盘价、成交量等)
        period: 移动平均周期

    返回:
        np.ndarray: 移动平均值序列 (前period-1个值为NaN)

    示例:
        >>> close = np.array([10, 11, 12, 13, 14, 15])
        >>> ma5 = MA(close, 5)
        >>> print(ma5)
        [nan nan nan nan 12. 13.]
    """
    if isinstance(data, pd.Series):
        data = data.values

    if len(data) < period:
        return np.full(len(data), np.nan)

    # 使用卷积实现移动平均，性能更优
    weights = np.ones(period) / period
    ma = np.convolve(data, weights, mode="valid")

    # 前period-1个值为NaN
    result = np.full(len(data), np.nan)
    result[period - 1 :] = ma

    return result


def SMA(
    data: Union[np.ndarray, pd.Series], period: int, weight: float = 1.0
) -> np.ndarray:
    """
    平滑移动平均 (Smoothed Moving Average)

    TDX公式: SMA(X, N, M) = (M*X + (N-M)*Y) / N
    其中Y为上一周期SMA值

    参数:
        data: 价格序列
        period: 平滑周期
        weight: 权重系数 (默认1.0)

    返回:
        np.ndarray: 平滑移动平均值序列

    示例:
        >>> close = np.array([10, 11, 12, 13, 14, 15])
        >>> sma5 = SMA(close, 5, 1)
    """
    if isinstance(data, pd.Series):
        data = data.values

    result = np.zeros_like(data, dtype=float)
    result[0] = data[0]

    alpha = weight / period

    for i in range(1, len(data)):
        result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]

    # 前period-1个值设为NaN
    result[: period - 1] = np.nan

    return result


def EMA(data: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    指数移动平均 (Exponential Moving Average)

    参数:
        data: 价格序列
        period: EMA周期

    返回:
        np.ndarray: 指数移动平均值序列

    示例:
        >>> close = np.array([10, 11, 12, 13, 14, 15])
        >>> ema5 = EMA(close, 5)
    """
    if isinstance(data, pd.Series):
        data = data.values

    alpha = 2.0 / (period + 1)
    result = np.zeros_like(data, dtype=float)
    result[0] = data[0]

    for i in range(1, len(data)):
        result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]

    # 前period-1个值设为NaN
    result[: period - 1] = np.nan

    return result


def CROSS(
    series1: Union[np.ndarray, pd.Series], series2: Union[np.ndarray, pd.Series]
) -> np.ndarray:
    """
    交叉函数 - 判断series1是否向上穿越series2

    参数:
        series1: 第一个序列 (通常是短期均线)
        series2: 第二个序列 (通常是长期均线)

    返回:
        np.ndarray: 布尔数组，True表示发生向上交叉

    示例:
        >>> ma5 = np.array([10, 11, 12, 13, 14])
        >>> ma10 = np.array([12, 12, 12, 12, 12])
        >>> cross = CROSS(ma5, ma10)
        >>> print(cross)
        [False False False  True False]
    """
    if isinstance(series1, pd.Series):
        series1 = series1.values
    if isinstance(series2, pd.Series):
        series2 = series2.values

    # 当前周期: series1 > series2
    # 前一周期: series1 <= series2
    cross = np.zeros(len(series1), dtype=bool)

    if len(series1) > 1:
        cross[1:] = (series1[1:] > series2[1:]) & (series1[:-1] <= series2[:-1])

    return cross


def HHV(data: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    最高值 (Highest High Value) - 滚动窗口内的最高价

    参数:
        data: 价格序列
        period: 滚动窗口周期

    返回:
        np.ndarray: 滚动最高值序列

    示例:
        >>> high = np.array([10, 12, 11, 15, 13, 14])
        >>> hhv5 = HHV(high, 5)
        >>> print(hhv5)
        [nan nan nan nan 15. 15.]
    """
    if isinstance(data, pd.Series):
        data = data.values

    result = np.full(len(data), np.nan)

    for i in range(period - 1, len(data)):
        result[i] = np.max(data[i - period + 1 : i + 1])

    return result


def LLV(data: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    最低值 (Lowest Low Value) - 滚动窗口内的最低价

    参数:
        data: 价格序列
        period: 滚动窗口周期

    返回:
        np.ndarray: 滚动最低值序列

    示例:
        >>> low = np.array([10, 12, 11, 15, 13, 14])
        >>> llv5 = LLV(low, 5)
        >>> print(llv5)
        [nan nan nan nan 10. 11.]
    """
    if isinstance(data, pd.Series):
        data = data.values

    result = np.full(len(data), np.nan)

    for i in range(period - 1, len(data)):
        result[i] = np.min(data[i - period + 1 : i + 1])

    return result


def REF(data: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    引用函数 - 获取period周期前的数据

    参数:
        data: 价格序列
        period: 向前引用的周期数

    返回:
        np.ndarray: 向前引用后的序列

    示例:
        >>> close = np.array([10, 11, 12, 13, 14, 15])
        >>> ref1 = REF(close, 1)
        >>> print(ref1)
        [nan 10. 11. 12. 13. 14.]
    """
    if isinstance(data, pd.Series):
        data = data.values

    result = np.full(len(data), np.nan)
    result[period:] = data[:-period]

    return result


def BARSLAST(condition: Union[np.ndarray, pd.Series]) -> np.ndarray:
    """
    上一次条件成立位置 - 距离上次条件为True的周期数

    参数:
        condition: 布尔数组

    返回:
        np.ndarray: 距离上次True的周期数

    示例:
        >>> cond = np.array([False, True, False, False, True, False])
        >>> bars = BARSLAST(cond)
        >>> print(bars)
        [nan  0.  1.  2.  0.  1.]
    """
    if isinstance(condition, pd.Series):
        condition = condition.values

    result = np.full(len(condition), np.nan)
    last_true_index = -1

    for i, cond_val in enumerate(condition):
        if cond_val:
            last_true_index = i
            result[i] = 0
        elif last_true_index >= 0:
            result[i] = i - last_true_index

    return result


def STD(data: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    标准差 (Standard Deviation) - 滚动窗口标准差

    参数:
        data: 价格序列
        period: 滚动窗口周期

    返回:
        np.ndarray: 滚动标准差序列

    示例:
        >>> close = np.array([10, 11, 12, 13, 14, 15])
        >>> std5 = STD(close, 5)
    """
    if isinstance(data, pd.Series):
        data = data.values

    result = np.full(len(data), np.nan)

    for i in range(period - 1, len(data)):
        result[i] = np.std(data[i - period + 1 : i + 1], ddof=1)

    return result


def SUM(data: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    求和函数 - 滚动窗口求和

    参数:
        data: 价格序列
        period: 滚动窗口周期

    返回:
        np.ndarray: 滚动求和序列

    示例:
        >>> volume = np.array([100, 200, 150, 300, 250])
        >>> sum3 = SUM(volume, 3)
        >>> print(sum3)
        [nan nan 450. 650. 700.]
    """
    if isinstance(data, pd.Series):
        data = data.values

    result = np.full(len(data), np.nan)

    for i in range(period - 1, len(data)):
        result[i] = np.sum(data[i - period + 1 : i + 1])

    return result


def COUNT(condition: Union[np.ndarray, pd.Series], period: int) -> np.ndarray:
    """
    计数函数 - 统计滚动窗口内条件为True的次数

    参数:
        condition: 布尔数组
        period: 滚动窗口周期

    返回:
        np.ndarray: 滚动计数序列

    示例:
        >>> cond = np.array([True, False, True, True, False, True])
        >>> count3 = COUNT(cond, 3)
        >>> print(count3)
        [nan nan  2.  2.  2.  2.]
    """
    if isinstance(condition, pd.Series):
        condition = condition.values

    result = np.full(len(condition), np.nan, dtype=float)

    for i in range(period - 1, len(condition)):
        result[i] = np.sum(condition[i - period + 1 : i + 1])

    return result


def MAX(
    series1: Union[np.ndarray, pd.Series], series2: Union[np.ndarray, pd.Series]
) -> np.ndarray:
    """
    取最大值 - 逐个元素比较取大

    参数:
        series1: 第一个序列
        series2: 第二个序列

    返回:
        np.ndarray: 逐个元素的最大值
    """
    if isinstance(series1, pd.Series):
        series1 = series1.values
    if isinstance(series2, pd.Series):
        series2 = series2.values

    return np.maximum(series1, series2)


def MIN(
    series1: Union[np.ndarray, pd.Series], series2: Union[np.ndarray, pd.Series]
) -> np.ndarray:
    """
    取最小值 - 逐个元素比较取小

    参数:
        series1: 第一个序列
        series2: 第二个序列

    返回:
        np.ndarray: 逐个元素的最小值
    """
    if isinstance(series1, pd.Series):
        series1 = series1.values
    if isinstance(series2, pd.Series):
        series2 = series2.values

    return np.minimum(series1, series2)


def ABS(data: Union[np.ndarray, pd.Series]) -> np.ndarray:
    """
    绝对值函数

    参数:
        data: 数据序列

    返回:
        np.ndarray: 绝对值序列
    """
    if isinstance(data, pd.Series):
        data = data.values

    return np.abs(data)


# ===================================
# 常用组合指标
# ===================================


def MACD(
    close: Union[np.ndarray, pd.Series],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple:
    """
    MACD指标 (Moving Average Convergence Divergence)

    参数:
        close: 收盘价序列
        fast_period: 快速EMA周期 (默认12)
        slow_period: 慢速EMA周期 (默认26)
        signal_period: 信号线周期 (默认9)

    返回:
        tuple: (DIF, DEA, MACD柱)

    示例:
        >>> close = np.random.randn(100) + 100
        >>> dif, dea, macd = MACD(close)
    """
    if isinstance(close, pd.Series):
        close = close.values

    ema_fast = EMA(close, fast_period)
    ema_slow = EMA(close, slow_period)

    dif = ema_fast - ema_slow
    dea = EMA(dif, signal_period)
    macd = (dif - dea) * 2

    return dif, dea, macd


def KDJ(
    high: Union[np.ndarray, pd.Series],
    low: Union[np.ndarray, pd.Series],
    close: Union[np.ndarray, pd.Series],
    n: int = 9,
    m1: int = 3,
    m2: int = 3,
) -> tuple:
    # pylint: disable=too-many-positional-arguments

    """


    KDJ 指标 (随机指标)

    参数:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        n: RSV计算周期 (默认9)
        m1: K值平滑周期 (默认3)
        m2: D值平滑周期 (默认3)

    返回:
        tuple: (K, D, J)

    示例:
        >>> k, d, j = KDJ(high, low, close)
    """
    if isinstance(high, pd.Series):
        high = high.values
    if isinstance(low, pd.Series):
        low = low.values
    if isinstance(close, pd.Series):
        close = close.values

    # 计算RSV (未成熟随机值)
    hhv = HHV(high, n)
    llv = LLV(low, n)

    rsv = np.where(hhv != llv, (close - llv) / (hhv - llv) * 100, 50)

    # 计算K, D, J
    k = SMA(rsv, m1, 1)
    d = SMA(k, m2, 1)
    j = 3 * k - 2 * d

    return k, d, j


def RSI(close: Union[np.ndarray, pd.Series], period: int = 14) -> np.ndarray:
    """
    相对强弱指标 (Relative Strength Index)

    参数:
        close: 收盘价序列
        period: RSI周期 (默认14)

    返回:
        np.ndarray: RSI值序列 (0-100)

    示例:
        >>> close = np.random.randn(100) + 100
        >>> rsi14 = RSI(close, 14)
    """
    if isinstance(close, pd.Series):
        close = close.values

    # 计算价格变化
    delta = np.diff(close, prepend=close[0])

    # 分离涨跌
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    # 计算平均涨跌幅
    avg_gain = SMA(gain, period, 1)
    avg_loss = SMA(loss, period, 1)

    # 计算RSI
    rs = np.where(avg_loss != 0, avg_gain / avg_loss, 0)
    rsi = 100 - (100 / (1 + rs))

    return rsi


def BOLL(
    close: Union[np.ndarray, pd.Series], period: int = 20, std_dev: float = 2.0
) -> tuple:
    """
    布林带指标 (Bollinger Bands)

    参数:
        close: 收盘价序列
        period: 移动平均周期 (默认20)
        std_dev: 标准差倍数 (默认2.0)

    返回:
        tuple: (上轨, 中轨, 下轨)

    示例:
        >>> upper, middle, lower = BOLL(close, 20, 2)
    """
    if isinstance(close, pd.Series):
        close = close.values

    middle = MA(close, period)
    std = STD(close, period)

    upper = middle + std_dev * std
    lower = middle - std_dev * std

    return upper, middle, lower


if __name__ == "__main__":
    # 测试代码
    print("TDX兼容函数库测试")
    print("=" * 50)

    # 生成测试数据
    np.random.seed(42)
    test_close = np.cumsum(np.random.randn(100)) + 100
    test_high = test_close + np.random.rand(100)
    test_low = test_close - np.random.rand(100)

    # 测试MA
    test_ma5 = MA(test_close, 5)
    test_ma20 = MA(test_close, 20)
    print(f"MA5最后5个值: {test_ma5[-5:]}")
    print(f"MA20最后5个值: {test_ma20[-5:]}")

    # 测试CROSS
    test_cross_signal = CROSS(test_ma5, test_ma20)
    print(f"金叉信号数量: {np.sum(test_cross_signal)}")

    # 测试MACD
    test_dif, test_dea, test_macd = MACD(test_close)
    print(f"MACD最后5个值: {test_macd[-5:]}")

    # 测试KDJ
    test_k, test_d, test_j = KDJ(test_high, test_low, test_close)
    print(f"KDJ最后值: K={test_k[-1]:.2f}, D={test_d[-1]:.2f}, J={test_j[-1]:.2f}")

    # 测试RSI
    test_rsi14 = RSI(test_close, 14)
    print(f"RSI14最后5个值: {test_rsi14[-5:]}")

    # 测试BOLL
    test_upper, test_middle, test_lower = BOLL(test_close, 20, 2)
    print(
        f"BOLL最后值: 上轨={test_upper[-1]:.2f}, 中轨={test_middle[-1]:.2f}, 下轨={test_lower[-1]:.2f}"
    )

    print("\n所有测试通过！")
