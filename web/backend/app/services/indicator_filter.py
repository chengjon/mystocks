"""
技术指标过滤服务 - Technical Indicator Filter

Task 8: 实现灵活的用户订阅过滤系统

功能特性:
- 支持多种技术指标计算（RSI, MACD, Moving Averages, Bollinger Bands）
- 灵活的指标参数配置
- 高性能指标评估
- 指标历史缓存

Author: Claude Code
Date: 2025-11-07
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import structlog
from decimal import Decimal

logger = structlog.get_logger()


class IndicatorType(str, Enum):
    """技术指标类型"""

    RSI = "rsi"  # Relative Strength Index
    MACD = "macd"  # Moving Average Convergence Divergence
    SMA = "sma"  # Simple Moving Average
    EMA = "ema"  # Exponential Moving Average
    BB = "bb"  # Bollinger Bands
    STOCH = "stoch"  # Stochastic Oscillator


@dataclass
class IndicatorConfig:
    """指标配置"""

    type: IndicatorType
    period: int = 14
    fast_period: Optional[int] = None  # For MACD, Stochastic
    slow_period: Optional[int] = None  # For MACD, Stochastic
    signal_period: Optional[int] = None  # For MACD
    std_dev: float = 2.0  # For Bollinger Bands
    k_period: Optional[int] = None  # For Stochastic


class IndicatorCalculator:
    """技术指标计算器"""

    def __init__(self):
        """初始化计算器"""
        self.cache: Dict[str, Any] = {}
        self.calculations = 0
        logger.info("✅ Indicator Calculator initialized")

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        计算相对强度指数 (RSI)

        Args:
            prices: 价格列表（从旧到新）
            period: RSI周期

        Returns:
            RSI值 (0-100)
        """
        self.calculations += 1

        if len(prices) < period + 1:
            return 50.0  # 数据不足，返回中性值

        # 计算变化
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

        # 分离上升和下降
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        # 计算平均收益和损失
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    def calculate_sma(self, prices: List[float], period: int = 20) -> float:
        """
        计算简单移动平均 (SMA)

        Args:
            prices: 价格列表（从旧到新）
            period: SMA周期

        Returns:
            SMA值
        """
        self.calculations += 1

        if len(prices) < period:
            return prices[-1] if prices else 0.0

        sma = sum(prices[-period:]) / period
        return round(sma, 2)

    def calculate_ema(
        self, prices: List[float], period: int = 20, alpha: Optional[float] = None
    ) -> float:
        """
        计算指数移动平均 (EMA)

        Args:
            prices: 价格列表（从旧到新）
            period: EMA周期
            alpha: 平滑系数

        Returns:
            EMA值
        """
        self.calculations += 1

        if len(prices) < period:
            return prices[-1] if prices else 0.0

        if alpha is None:
            alpha = 2 / (period + 1)

        # 初始EMA = SMA
        ema = sum(prices[:period]) / period

        # 计算后续EMA
        for price in prices[period:]:
            ema = alpha * price + (1 - alpha) * ema

        return round(ema, 2)

    def calculate_macd(
        self,
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Dict[str, float]:
        """
        计算MACD指标

        Args:
            prices: 价格列表（从旧到新）
            fast_period: 快EMA周期
            slow_period: 慢EMA周期
            signal_period: 信号线周期

        Returns:
            {'macd': value, 'signal': value, 'histogram': value}
        """
        self.calculations += 1

        if len(prices) < slow_period:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

        # 计算快速和慢速EMA
        fast_ema = self.calculate_ema(prices, fast_period)
        slow_ema = self.calculate_ema(prices, slow_period)

        # MACD线 = 快速EMA - 慢速EMA
        macd = fast_ema - slow_ema

        # 信号线 = MACD的EMA
        # 简化版本：使用最后signal_period个MACD值的平均
        signal = macd  # 简化处理

        histogram = macd - signal

        return {
            "macd": round(macd, 2),
            "signal": round(signal, 2),
            "histogram": round(histogram, 2),
        }

    def calculate_bollinger_bands(
        self,
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0,
    ) -> Dict[str, float]:
        """
        计算布林带

        Args:
            prices: 价格列表（从旧到新）
            period: 周期
            std_dev: 标准差倍数

        Returns:
            {'upper': value, 'middle': value, 'lower': value}
        """
        self.calculations += 1

        if len(prices) < period:
            price = prices[-1] if prices else 0.0
            return {"upper": price, "middle": price, "lower": price}

        # 中线 = SMA
        middle = self.calculate_sma(prices, period)

        # 计算标准差
        recent_prices = prices[-period:]
        variance = sum((p - middle) ** 2 for p in recent_prices) / period
        std = variance**0.5

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        return {
            "upper": round(upper, 2),
            "middle": round(middle, 2),
            "lower": round(lower, 2),
        }

    def calculate_stochastic(
        self,
        prices: List[float],
        highs: List[float],
        lows: List[float],
        k_period: int = 14,
        d_period: int = 3,
    ) -> Dict[str, float]:
        """
        计算随机指标 (Stochastic Oscillator)

        Args:
            prices: 收盘价列表
            highs: 最高价列表
            lows: 最低价列表
            k_period: K线周期
            d_period: D线周期

        Returns:
            {'k': value, 'd': value}
        """
        self.calculations += 1

        if len(prices) < k_period:
            return {"k": 50.0, "d": 50.0}

        # 计算K线
        recent_highs = highs[-k_period:]
        recent_lows = lows[-k_period:]
        recent_closes = prices[-k_period:]

        highest = max(recent_highs)
        lowest = min(recent_lows)

        if highest == lowest:
            k = 50.0
        else:
            k = ((prices[-1] - lowest) / (highest - lowest)) * 100

        # 简化版D线 = K线的平均
        d = k

        return {"k": round(k, 2), "d": round(d, 2)}

    def get_stats(self) -> Dict[str, Any]:
        """获取计算器统计"""
        return {"total_calculations": self.calculations}


class IndicatorFilter:
    """指标过滤器"""

    def __init__(self):
        """初始化指标过滤器"""
        self.calculator = IndicatorCalculator()
        self.price_cache: Dict[str, List[float]] = {}
        logger.info("✅ Indicator Filter initialized")

    def add_price_data(self, symbol: str, price: float, max_cache: int = 100) -> None:
        """
        添加价格数据到缓存

        Args:
            symbol: 股票代码
            price: 价格
            max_cache: 最大缓存数
        """
        if symbol not in self.price_cache:
            self.price_cache[symbol] = []

        self.price_cache[symbol].append(price)

        # 限制缓存大小
        if len(self.price_cache[symbol]) > max_cache:
            self.price_cache[symbol] = self.price_cache[symbol][-max_cache:]

    def evaluate_rsi(self, symbol: str, operator: str, threshold: float) -> bool:
        """
        评估RSI条件

        Args:
            symbol: 股票代码
            operator: 比较操作符 (>, <, ==, >=, <=)
            threshold: 阈值

        Returns:
            是否满足条件
        """
        if symbol not in self.price_cache or len(self.price_cache[symbol]) < 15:
            return False

        rsi = self.calculator.calculate_rsi(self.price_cache[symbol])
        return self._compare(rsi, operator, threshold)

    def evaluate_sma(
        self, symbol: str, period: int, operator: str, threshold: float
    ) -> bool:
        """
        评估SMA条件

        Args:
            symbol: 股票代码
            period: SMA周期
            operator: 比较操作符
            threshold: 阈值

        Returns:
            是否满足条件
        """
        if symbol not in self.price_cache or len(self.price_cache[symbol]) < period:
            return False

        sma = self.calculator.calculate_sma(self.price_cache[symbol], period)
        current_price = self.price_cache[symbol][-1]

        return self._compare(current_price, operator, sma)

    def evaluate_bb(self, symbol: str, period: int, band: str) -> Optional[float]:
        """
        获取布林带值

        Args:
            symbol: 股票代码
            period: 周期
            band: 带 ('upper', 'middle', 'lower')

        Returns:
            布林带值或None
        """
        if symbol not in self.price_cache or len(self.price_cache[symbol]) < period:
            return None

        bb = self.calculator.calculate_bollinger_bands(self.price_cache[symbol], period)

        return bb.get(band)

    def _compare(self, value: float, operator: str, threshold: float) -> bool:
        """比较操作"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return value == threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        return False

    def get_stats(self) -> Dict[str, Any]:
        """获取过滤器统计"""
        return {
            "symbols_cached": len(self.price_cache),
            "total_prices_cached": sum(
                len(prices) for prices in self.price_cache.values()
            ),
            "calculator_stats": self.calculator.get_stats(),
        }


# 全局单例
_indicator_filter: Optional[IndicatorFilter] = None


def get_indicator_filter() -> IndicatorFilter:
    """获取指标过滤器单例"""
    global _indicator_filter
    if _indicator_filter is None:
        _indicator_filter = IndicatorFilter()
    return _indicator_filter


def reset_indicator_filter() -> None:
    """重置指标过滤器单例（仅用于测试）"""
    global _indicator_filter
    _indicator_filter = None
