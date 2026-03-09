"""Shared methods for `technical_signal.py`."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType
from src.advanced_analysis.technical_analyzer._technical_signal_tail import TechnicalAnalyzerTailMixin
from src.advanced_analysis.technical_analyzer.technical_signal_models import (
    MarketRegime,
    PatternResult,
    TechnicalSignal,
)
from src.indicators.indicator_factory import IndicatorFactory

logger = logging.getLogger(__name__)


class TechnicalAnalyzerMixin(TechnicalAnalyzerTailMixin):
    def __init__(self, data_manager, gpu_manager=None):
        super().__init__(data_manager, gpu_manager)

        # 初始化指标工厂
        self.indicator_factory = IndicatorFactory()

        # 自定义指标配置
        self.custom_indicators = {
            "turtle_channel": self._calculate_turtle_channel,
            "volatility_breakout": self._calculate_volatility_breakout,
            "momentum_squeeze": self._calculate_momentum_squeeze,
            "adaptive_rsi": self._calculate_adaptive_rsi,
        }

        # 形态识别配置
        self.patterns = {
            "head_shoulders": self._detect_head_shoulders,
            "double_top_bottom": self._detect_double_top_bottom,
            "triangle": self._detect_triangle,
            "wedge": self._detect_wedge,
        }

        # 信号权重配置
        self.signal_weights = {"trend": 0.25, "momentum": 0.25, "volatility": 0.20, "volume": 0.15, "custom": 0.15}


    def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
        """
        执行技术分析

        Args:
            stock_code: 股票代码
            **kwargs: 分析参数
                - timeframes: 时间框架列表 (默认: ['1d'])
                - include_patterns: 是否包含形态识别 (默认: True)
                - include_regime: 是否包含市场状态分析 (默认: True)
                - signal_threshold: 信号阈值 (默认: 0.6)

        Returns:
            AnalysisResult: 分析结果
        """
        timeframes = kwargs.get("timeframes", ["1d"])
        include_patterns = kwargs.get("include_patterns", True)
        include_regime = kwargs.get("include_regime", True)
        signal_threshold = kwargs.get("signal_threshold", 0.6)

        try:
            # 获取多时间框架数据
            timeframe_data = {}
            for tf in timeframes:
                data = self._get_historical_data(stock_code, days=365, data_type=tf)
                if not data.empty:
                    timeframe_data[tf] = data

            if not timeframe_data:
                return self._create_error_result(stock_code, "No technical data available for analysis")

            # 使用主要时间框架进行分析
            main_tf = timeframes[0]
            main_data = timeframe_data[main_tf]

            # 计算技术指标
            technical_indicators = self._calculate_technical_indicators(main_data)

            # 生成技术信号
            signals = self._generate_technical_signals(technical_indicators, main_data)

            # 形态识别
            patterns = []
            if include_patterns:
                patterns = self._analyze_patterns(main_data)

            # 市场状态分析
            market_regime = None
            if include_regime:
                market_regime = self._analyze_market_regime(main_data)

            # 计算综合信号
            composite_signal = self._calculate_composite_signal(signals, patterns, market_regime)

            # 信号过滤
            filtered_signals = self._filter_signals(signals, signal_threshold)

            # 构建结果
            scores = {
                "signal_strength": composite_signal.get("strength", 0.0),
                "signal_confidence": composite_signal.get("confidence", 0.0),
                "trend_strength": market_regime.trend_strength if market_regime else 0.0,
                "volatility_level": market_regime.volatility_level if market_regime else 0.0,
            }

            signals_list = [
                {
                    "type": s.signal_type,
                    "severity": "high" if s.strength > 0.8 else "medium" if s.strength > 0.6 else "low",
                    "message": f"{s.indicator}: {s.description}",
                    "strength": s.strength,
                    "confidence": s.confidence,
                }
                for s in filtered_signals
            ]

            recommendations = {
                "primary_signal": composite_signal.get("signal", "hold"),
                "signal_strength": composite_signal.get("strength", 0.0),
                "recommended_action": self._generate_recommendation(composite_signal, market_regime),
                "risk_level": self._assess_risk_level(signals, patterns),
            }

            risk_assessment = {
                "market_regime": market_regime.primary_regime if market_regime else "unknown",
                "volatility_regime": market_regime.volatility_regime if market_regime else "unknown",
                "signal_consistency": self._check_signal_consistency(signals),
                "pattern_signals": len(patterns),
                "divergence_warnings": self._detect_divergences(technical_indicators),
            }

            metadata = {
                "timeframes_analyzed": timeframes,
                "indicators_calculated": list(technical_indicators.keys()),
                "patterns_detected": len(patterns),
                "market_regime": market_regime.primary_regime if market_regime else "unknown",
                "analysis_timestamp": datetime.now(),
                "data_quality": self._assess_technical_data_quality(main_data),
            }

            return AnalysisResult(
                analysis_type=AnalysisType.TECHNICAL,
                stock_code=stock_code,
                timestamp=datetime.now(),
                scores=scores,
                signals=signals_list,
                recommendations=recommendations,
                risk_assessment=risk_assessment,
                metadata=metadata,
                raw_data=main_data if kwargs.get("include_raw_data", False) else None,
            )

        except Exception as e:
            return self._create_error_result(stock_code, str(e))


    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算技术指标"""
        indicators = {}

        try:
            # 标准指标
            standard_indicators = ["SMA_20", "EMA_12", "RSI_14", "MACD", "BBANDS", "ATR_14", "ADX_14"]

            for indicator_name in standard_indicators:
                try:
                    calculator = self.indicator_factory.get_calculator(indicator_name, streaming=False)
                    if calculator:
                        result = calculator.calculate(data)
                        if isinstance(result, pd.Series):
                            indicators[indicator_name.lower()] = result
                        elif isinstance(result, pd.DataFrame):
                            # 对于多输出指标，存储主要输出
                            for col in result.columns:
                                indicators[f"{indicator_name.lower()}_{col.lower()}"] = result[col]
                except Exception as e:
                    logger.error("Failed to calculate %s: %s", indicator_name, e)
                    continue

            # 自定义指标
            for custom_name, custom_func in self.custom_indicators.items():
                try:
                    custom_result = custom_func(data)
                    if isinstance(custom_result, pd.Series):
                        indicators[custom_name] = custom_result
                    elif isinstance(custom_result, dict):
                        for key, value in custom_result.items():
                            indicators[f"{custom_name}_{key}"] = value
                except Exception as e:
                    logger.error("Failed to calculate custom indicator %s: %s", custom_name, e)
                    continue

        except Exception as e:
            logger.error("Error calculating technical indicators: %s", e)

        return indicators


    def _calculate_turtle_channel(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """海龟交易通道"""
        period = 20

        high_channel = data["high"].rolling(window=period).max()
        low_channel = data["low"].rolling(window=period).min()

        # 计算突破信号
        breakout_up = data["close"] > high_channel.shift(1)
        breakout_down = data["close"] < low_channel.shift(1)

        return {
            "upper_channel": high_channel,
            "lower_channel": low_channel,
            "breakout_up": breakout_up.astype(int),
            "breakout_down": breakout_down.astype(int),
        }


    def _calculate_volatility_breakout(self, data: pd.DataFrame) -> pd.Series:
        """波动率突破指标"""
        # 计算布林带
        sma = data["close"].rolling(window=20).mean()
        std = data["close"].rolling(window=20).std()

        upper_band = sma + 2 * std
        lower_band = sma - 2 * std

        # 计算带宽
        bandwidth = (upper_band - lower_band) / sma

        # 收缩后的突破
        squeeze = bandwidth < bandwidth.rolling(window=10).mean()
        breakout = (data["close"] > upper_band) & squeeze.shift(1).fillna(False)

        return breakout.astype(int)


    def _calculate_momentum_squeeze(self, data: pd.DataFrame) -> pd.Series:
        """动量收缩指标"""
        # 计算动量指标
        momentum = data["close"] - data["close"].shift(10)

        # 计算波动率
        volatility = data["close"].pct_change().rolling(window=20).std()

        # 动量标准化
        momentum_norm = momentum / (data["close"].rolling(window=20).std() + 1e-8)

        # 波动率标准化
        volatility_norm = (volatility - volatility.rolling(window=50).mean()) / volatility.rolling(window=50).std()

        # 收缩信号：动量低迷且波动率收缩
        squeeze = (momentum_norm.abs() < 0.5) & (volatility_norm < 0)

        return squeeze.astype(int)


    def _calculate_adaptive_rsi(self, data: pd.DataFrame) -> pd.Series:
        """自适应RSI"""
        # 基于波动率的RSI周期调整
        volatility = data["close"].pct_change().rolling(window=20).std()
        volatility_norm = (volatility - volatility.min()) / (volatility.max() - volatility.min())

        # 周期从6到24动态调整
        adaptive_period = 6 + (24 - 6) * volatility_norm

        # 计算自适应RSI
        adaptive_rsi = pd.Series(index=data.index, dtype=float)

        for i in range(len(data)):
            period = int(adaptive_period.iloc[i]) if not pd.isna(adaptive_period.iloc[i]) else 14
            if i >= period:
                prices = data["close"].iloc[i - period : i + 1]
                gains = prices.diff().clip(lower=0)
                losses = -prices.diff().clip(upper=0)

                avg_gain = gains.rolling(window=period, min_periods=1).mean().iloc[-1]
                avg_loss = losses.rolling(window=period, min_periods=1).mean().iloc[-1]

                if avg_loss != 0:
                    rs = avg_gain / avg_loss
                    adaptive_rsi.iloc[i] = 100 - (100 / (1 + rs))
                else:
                    adaptive_rsi.iloc[i] = 100

        return adaptive_rsi


    def _generate_technical_signals(self, indicators: Dict[str, pd.Series], data: pd.DataFrame) -> List[TechnicalSignal]:
        """生成技术信号"""
        signals = []

        # RSI信号
        if "rsi_14" in indicators:
            rsi = indicators["rsi_14"]
            signals.extend(self._generate_rsi_signals(rsi, data))

        # MACD信号
        if any(k.startswith("macd") for k in indicators.keys()):
            signals.extend(self._generate_macd_signals(indicators, data))

        # 布林带信号
        if any(k.startswith("bbands") for k in indicators.keys()):
            signals.extend(self._generate_bbands_signals(indicators, data))

        # 自定义指标信号
        if "turtle_channel_breakout_up" in indicators:
            signals.extend(self._generate_turtle_signals(indicators, data))

        if "volatility_breakout" in indicators:
            signals.extend(self._generate_volatility_signals(indicators, data))

        return signals


    def _generate_rsi_signals(self, rsi: pd.Series, data: pd.DataFrame) -> List[TechnicalSignal]:
        """生成RSI信号"""
        signals = []

        latest_rsi = rsi.iloc[-1] if not rsi.empty else None
        if latest_rsi is None:
            return signals

        # 超卖信号
        if latest_rsi < 30:
            signals.append(
                TechnicalSignal(
                    signal_type="buy",
                    strength=min((30 - latest_rsi) / 30, 1.0),
                    confidence=0.7,
                    timeframe="1d",
                    indicator="RSI",
                    value=latest_rsi,
                    threshold=30,
                    description=f"RSI超卖 {latest_rsi:.1f}，买入信号",
                )
            )

        # 超买信号
        elif latest_rsi > 70:
            signals.append(
                TechnicalSignal(
                    signal_type="sell",
                    strength=min((latest_rsi - 70) / 30, 1.0),
                    confidence=0.7,
                    timeframe="1d",
                    indicator="RSI",
                    value=latest_rsi,
                    threshold=70,
                    description=f"RSI超买 {latest_rsi:.1f}，卖出信号",
                )
            )

        return signals


    def _generate_macd_signals(self, indicators: Dict[str, pd.Series], data: pd.DataFrame) -> List[TechnicalSignal]:
        """生成MACD信号"""
        signals = []

        macd_hist = None
        for key in indicators.keys():
            if "macd" in key and "hist" in key:
                macd_hist = indicators[key]
                break

        if macd_hist is None or macd_hist.empty:
            return signals

        latest_hist = macd_hist.iloc[-1]
        prev_hist = macd_hist.iloc[-2] if len(macd_hist) > 1 else 0

        # 金叉信号
        if latest_hist > 0 and prev_hist <= 0:
            signals.append(
                TechnicalSignal(
                    signal_type="buy",
                    strength=0.8,
                    confidence=0.75,
                    timeframe="1d",
                    indicator="MACD",
                    value=latest_hist,
                    threshold=0,
                    description="MACD金叉，买入信号",
                )
            )

        # 死叉信号
        elif latest_hist < 0 and prev_hist >= 0:
            signals.append(
                TechnicalSignal(
                    signal_type="sell",
                    strength=0.8,
                    confidence=0.75,
                    timeframe="1d",
                    indicator="MACD",
                    value=latest_hist,
                    threshold=0,
                    description="MACD死叉，卖出信号",
                )
            )

        return signals


    def _generate_bbands_signals(self, indicators: Dict[str, pd.Series], data: pd.DataFrame) -> List[TechnicalSignal]:
        """生成布林带信号"""
        signals = []

        upper_key = None
        lower_key = None
        for key in indicators.keys():
            if "bbands" in key and "upper" in key:
                upper_key = key
            elif "bbands" in key and "lower" in key:
                lower_key = key

        if not upper_key or not lower_key:
            return signals

        upper_band = indicators[upper_key]
        lower_band = indicators[lower_key]
        close_price = data["close"]

        latest_close = close_price.iloc[-1]
        latest_upper = upper_band.iloc[-1]
        latest_lower = lower_band.iloc[-1]

        # 突破上轨
        if latest_close > latest_upper:
            signals.append(
                TechnicalSignal(
                    signal_type="sell",
                    strength=0.6,
                    confidence=0.65,
                    timeframe="1d",
                    indicator="Bollinger Bands",
                    value=latest_close,
                    threshold=latest_upper,
                    description=f"突破上轨 {latest_close:.2f}，卖出信号",
                )
            )

        # 跌破下轨
        elif latest_close < latest_lower:
            signals.append(
                TechnicalSignal(
                    signal_type="buy",
                    strength=0.6,
                    confidence=0.65,
                    timeframe="1d",
                    indicator="Bollinger Bands",
                    value=latest_close,
                    threshold=latest_lower,
                    description=f"跌破下轨 {latest_close:.2f}，买入信号",
                )
            )

        return signals


    def _generate_turtle_signals(self, indicators: Dict[str, pd.Series], data: pd.DataFrame) -> List[TechnicalSignal]:
        """生成海龟交易信号"""
        signals = []

        breakout_up_key = None
        breakout_down_key = None
        for key in indicators.keys():
            if "turtle_channel_breakout_up" in key:
                breakout_up_key = key
            elif "turtle_channel_breakout_down" in key:
                breakout_down_key = key

        if breakout_up_key and indicators[breakout_up_key].iloc[-1] > 0:
            signals.append(
                TechnicalSignal(
                    signal_type="buy",
                    strength=0.9,
                    confidence=0.8,
                    timeframe="1d",
                    indicator="Turtle Channel",
                    value=indicators[breakout_up_key].iloc[-1],
                    threshold=0,
                    description="海龟通道突破买入信号",
                )
            )

        if breakout_down_key and indicators[breakout_down_key].iloc[-1] > 0:
            signals.append(
                TechnicalSignal(
                    signal_type="sell",
                    strength=0.9,
                    confidence=0.8,
                    timeframe="1d",
                    indicator="Turtle Channel",
                    value=indicators[breakout_down_key].iloc[-1],
                    threshold=0,
                    description="海龟通道突破卖出信号",
                )
            )

        return signals


    def _generate_volatility_signals(self, indicators: Dict[str, pd.Series], data: pd.DataFrame) -> List[TechnicalSignal]:
        """生成波动率信号"""
        signals = []

        breakout_key = None
        for key in indicators.keys():
            if "volatility_breakout" in key:
                breakout_key = key
                break

        if breakout_key and indicators[breakout_key].iloc[-1] > 0:
            signals.append(
                TechnicalSignal(
                    signal_type="buy",
                    strength=0.7,
                    confidence=0.6,
                    timeframe="1d",
                    indicator="Volatility Breakout",
                    value=indicators[breakout_key].iloc[-1],
                    threshold=0,
                    description="波动率突破买入信号",
                )
            )

        return signals


    def _analyze_patterns(self, data: pd.DataFrame) -> List[PatternResult]:
        """形态分析"""
        patterns = []

        for pattern_name, pattern_func in self.patterns.items():
            try:
                pattern_result = pattern_func(data)
                if pattern_result and pattern_result.confidence > 0.6:
                    patterns.append(pattern_result)
            except Exception as e:
                logger.error("Error analyzing pattern %s: %s", pattern_name, e)
                continue

        return patterns


    def _detect_head_shoulders(self, data: pd.DataFrame) -> Optional[PatternResult]:
        """检测头肩顶形态"""
        # 简化的头肩顶检测逻辑
        # 实际实现需要更复杂的形态识别算法
        return None  # 暂时返回None


    def _detect_double_top_bottom(self, data: pd.DataFrame) -> Optional[PatternResult]:
        """检测双顶/双底形态"""
        # 简化的双顶双底检测逻辑
        return None  # 暂时返回None


    def _detect_triangle(self, data: pd.DataFrame) -> Optional[PatternResult]:
        """检测三角形形态"""
        # 简化的三角形检测逻辑
        return None  # 暂时返回None


    def _detect_wedge(self, data: pd.DataFrame) -> Optional[PatternResult]:
        """检测楔形形态"""
        # 简化的楔形检测逻辑
        return None  # 暂时返回None


    def _analyze_market_regime(self, data: pd.DataFrame) -> MarketRegime:
        """分析市场状态"""
        try:
            # 计算ADX
            adx_calculator = self.indicator_factory.get_calculator("ADX_14", streaming=False)
            if adx_calculator:
                adx_result = adx_calculator.calculate(data)
                adx_value = adx_result.iloc[-1] if not adx_result.empty else 25
            else:
                adx_value = 25

            # 计算波动率
            returns = data["close"].pct_change()
            volatility = returns.rolling(window=20).std().iloc[-1] * np.sqrt(252)  # 年化波动率
            volatility_level = volatility * 100  # 转换为百分比

            # 判断趋势状态
            if adx_value > 25:
                primary_regime = "trending"
                trend_strength = min(adx_value, 100)
            else:
                primary_regime = "ranging"
                trend_strength = 100 - adx_value

            # 判断波动率状态
            if volatility_level > 30:
                volatility_regime = "high_vol"
            elif volatility_level < 15:
                volatility_regime = "low_vol"
            else:
                volatility_regime = "normal_vol"

            # 推荐策略
            if primary_regime == "trending" and volatility_regime == "high_vol":
                recommended_strategy = "trend_following"
            elif primary_regime == "ranging" and volatility_regime == "low_vol":
                recommended_strategy = "mean_reversion"
            elif volatility_regime == "high_vol":
                recommended_strategy = "volatility_breakout"
            else:
                recommended_strategy = "balanced"

            return MarketRegime(
                primary_regime=primary_regime,
                volatility_regime=volatility_regime,
                trend_strength=trend_strength,
                volatility_level=volatility_level,
                adx_value=adx_value,
                recommended_strategy=recommended_strategy,
            )

        except Exception as e:
            logger.error("Error analyzing market regime: %s", e)
            return MarketRegime(
                primary_regime="unknown",
                volatility_regime="unknown",
                trend_strength=50,
                volatility_level=20,
                adx_value=25,
                recommended_strategy="balanced",
            )
