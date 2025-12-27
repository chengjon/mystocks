"""
技术指标计算器 - 从 database_service.py 拆分
职责：技术指标计算、交易信号、模式识别
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import pandas as pd
import logging
from typing import Dict, Any
from datetime import datetime

# 设置日志
logger = logging.getLogger(__name__)


class TechnicalIndicatorCalculator:
    """技术指标计算器 - 专注于技术指标和交易信号计算"""

    def __init__(self):
        """初始化技术指标计算器"""
        self.indicator_cache = {}

    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算技术指标

        Args:
            data: 价格数据DataFrame (包含close, volume列)

        Returns:
            Dict[str, Any]: 技术指标数据
        """
        try:
            if data.empty or "close" not in data.columns:
                return {}

            # 计算基础技术指标
            indicators = {}

            # 简单移动平均 (SMA)
            indicators["sma"] = self._calculate_sma(data["close"])

            # 相对强弱指标 (RSI)
            indicators["rsi"] = self._calculate_rsi(data["close"])

            # MACD指标
            indicators["macd"] = self._calculate_macd(data["close"])

            # 布林带
            indicators["bollinger"] = self._calculate_bollinger_bands(data["close"])

            return indicators

        except Exception as e:
            logger.error(f"Failed to calculate technical indicators: {str(e)}")
            return {}

    def calculate_trend_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算趋势指标

        Args:
            data: 价格数据DataFrame

        Returns:
            Dict[str, Any]: 趋势指标数据
        """
        try:
            if data.empty or "close" not in data.columns:
                return {}

            trend_indicators = {}

            # 移动平均线
            trend_indicators["ma5"] = self._calculate_sma(data["close"], period=5)
            trend_indicators["ma10"] = self._calculate_sma(data["close"], period=10)
            trend_indicators["ma20"] = self._calculate_sma(data["close"], period=20)

            # 趋势判断
            if len(trend_indicators["ma5"]) > 0 and len(trend_indicators["ma10"]) > 0:
                latest_ma5 = trend_indicators["ma5"].iloc[-1]
                latest_ma10 = trend_indicators["ma10"].iloc[-1]

                if latest_ma5 > latest_ma10:
                    trend = "UP"
                elif latest_ma5 < latest_ma10:
                    trend = "DOWN"
                else:
                    trend = "SIDEWAYS"

                trend_indicators["trend"] = trend

            return trend_indicators

        except Exception as e:
            logger.error(f"Failed to calculate trend indicators: {str(e)}")
            return {}

    def calculate_momentum_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算动量指标

        Args:
            data: 价格数据DataFrame

        Returns:
            Dict[str, Any]: 动量指标数据
        """
        try:
            if data.empty or "close" not in data.columns:
                return {}

            momentum_indicators = {}

            # RSI
            momentum_indicators["rsi"] = self._calculate_rsi(data["close"])

            # 动量指标 (当前价格相对于N天前的变化)
            momentum_indicators["momentum"] = self._calculate_momentum(data["close"])

            # 变化率
            momentum_indicators["rate_of_change"] = self._calculate_rate_of_change(data["close"])

            return momentum_indicators

        except Exception as e:
            logger.error(f"Failed to calculate momentum indicators: {str(e)}")
            return {}

    def generate_trading_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成交易信号

        Args:
            data: 价格数据DataFrame (包含close, volume列)

        Returns:
            Dict[str, Any]: 交易信号数据
        """
        try:
            if data.empty or "close" not in data.columns or len(data) < 10:
                return {"signal": "HOLD", "confidence": 0.0}

            # 计算技术指标
            indicators = self.calculate_technical_indicators(data)
            trend_indicators = self.calculate_trend_indicators(data)

            # 生成信号逻辑
            signal = "HOLD"
            confidence = 0.5

            # 基于RSI的信号
            if "rsi" in indicators and len(indicators["rsi"]) > 0:
                current_rsi = indicators["rsi"].iloc[-1]
                if current_rsi < 30:
                    signal = "BUY"
                    confidence = max(confidence, 0.7)
                elif current_rsi > 70:
                    signal = "SELL"
                    confidence = max(confidence, 0.7)

            # 基于趋势的信号
            if "trend" in trend_indicators:
                trend = trend_indicators["trend"]
                if trend == "UP" and signal != "SELL":
                    signal = "BUY"
                    confidence = max(confidence, 0.6)
                elif trend == "DOWN" and signal != "BUY":
                    signal = "SELL"
                    confidence = max(confidence, 0.6)

            return {
                "signal": signal,
                "confidence": confidence,
                "indicators_used": list(indicators.keys()),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to generate trading signals: {str(e)}")
            return {"signal": "HOLD", "confidence": 0.0}

    def _calculate_sma(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """
        计算简单移动平均

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            pd.Series: SMA序列
        """
        return prices.rolling(window=period, min_periods=1).mean()

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        计算相对强弱指标

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            pd.Series: RSI序列
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # 填充初始值为50

    def _calculate_macd(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """
        计算MACD指标

        Args:
            prices: 价格序列

        Returns:
            Dict[str, pd.Series]: MACD指标
        """
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    def _calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        计算布林带

        Args:
            prices: 价格序列
            period: 周期
            std_dev: 标准差倍数

        Returns:
            Dict[str, pd.Series]: 布林带指标
        """
        sma = self._calculate_sma(prices, period)
        rolling_std = prices.rolling(window=period, min_periods=1).std()

        upper_band = sma + (rolling_std * std_dev)
        lower_band = sma - (rolling_std * std_dev)

        return {"upper": upper_band, "middle": sma, "lower": lower_band}

    def _calculate_momentum(self, prices: pd.Series, period: int = 10) -> float:
        """
        计算动量指标

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            float: 动量值
        """
        if len(prices) < period + 1:
            return 0.0

        current_price = prices.iloc[-1]
        past_price = prices.iloc[-(period + 1)]
        momentum = (current_price - past_price) / past_price * 100

        return momentum

    def _calculate_rate_of_change(self, prices: pd.Series, period: int = 10) -> float:
        """
        计算变化率

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            float: 变化率
        """
        if len(prices) < period + 1:
            return 0.0

        current_price = prices.iloc[-1]
        past_price = prices.iloc[-(period + 1)]
        roc = ((current_price - past_price) / past_price) * 100

        return roc
