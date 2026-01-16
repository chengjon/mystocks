"""
Trading Signals Analyzer for MyStocks Advanced Quantitative Analysis
A股量化分析平台交易信号分析功能

This module provides multi-level trading signals system including:
- Multi-timeframe signal generation and confluence detection
- Real-time monitoring and intelligent alerts
- Signal strength assessment and filtering
- Risk-adjusted signal validation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import warnings

from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType
from src.indicators.indicator_factory import IndicatorFactory

# GPU acceleration support
try:
    import cudf
    import cuml

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Trading signals analysis will run on CPU.")


@dataclass
class TradingSignal:
    """交易信号数据结构"""

    signal_id: str
    timestamp: datetime
    symbol: str
    signal_type: str  # buy, sell, hold
    strength: float  # 信号强度 (0-1)
    confidence: float  # 置信度 (0-1)
    timeframe: str  # 时间框架
    indicators: Dict[str, Any]  # 相关指标值
    price: float  # 信号价格
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    description: str = ""
    risk_reward_ratio: Optional[float] = None
    validity_period: Optional[datetime] = None


@dataclass
class SignalConfluence:
    """信号汇合分析"""

    confluence_score: float  # 汇合得分 (0-1)
    timeframe_consensus: int  # 时间框架共识数
    indicator_consensus: int  # 指标共识数
    overall_signal: str  # 综合信号
    supporting_signals: List[TradingSignal]
    conflicting_signals: List[TradingSignal]


class TradingSignalAnalyzer(BaseAnalyzer):
    """
    交易信号分析器

    提供多层级交易信号系统，包括：
    - 多时间框架信号生成和汇合检测
    - 实时监控和智能告警
    - 信号强度评估和过滤
    - 风险调整信号验证
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # 初始化指标工厂
    self.indicator_factory = IndicatorFactory()

    # 信号生成规则配置
    self.signal_rules = {
        "rsi_signals": self._generate_rsi_signals,
        "macd_signals": self._generate_macd_signals,
        "bollinger_signals": self._generate_bollinger_signals,
        "moving_average_signals": self._generate_ma_signals,
        "volume_signals": self._generate_volume_signals,
        "support_resistance_signals": self._generate_sr_signals,
    }

    # 多时间框架配置
    self.timeframes = ["5m", "15m", "1h", "1d", "1w"]

    # 信号权重配置
    self.signal_weights = {
        "rsi_signals": 0.15,
        "macd_signals": 0.20,
        "bollinger_signals": 0.15,
        "moving_average_signals": 0.20,
        "volume_signals": 0.15,
        "support_resistance_signals": 0.15,
    }

    # 风险管理参数
    self.risk_params = {
        "max_position_size": 0.1,  # 最大仓位比例
        "stop_loss_pct": 0.05,  # 止损比例
        "take_profit_pct": 0.15,  # 止盈比例
        "min_risk_reward": 1.5,  # 最小风险收益比
    }


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行交易信号分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数
            - timeframes: 时间框架列表 (默认: ['5m', '15m', '1h', '1d'])
            - signal_types: 信号类型过滤 (默认: 所有类型)
            - min_confidence: 最小置信度 (默认: 0.6)
            - include_confluence: 是否包含汇合分析 (默认: True)
            - risk_adjusted: 是否进行风险调整 (默认: True)

    Returns:
        AnalysisResult: 分析结果
    """
    timeframes = kwargs.get("timeframes", self.timeframes)
    signal_types = kwargs.get("signal_types", None)
    min_confidence = kwargs.get("min_confidence", 0.6)
    include_confluence = kwargs.get("include_confluence", True)
    risk_adjusted = kwargs.get("risk_adjusted", True)

    try:
        # 获取多时间框架数据
        timeframe_data = {}
        for tf in timeframes:
            try:
                data = self._get_historical_data(stock_code, days=30, data_type=tf)
                if not data.empty:
                    timeframe_data[tf] = data
            except Exception as e:
                print(f"Failed to get data for timeframe {tf}: {e}")
                continue

        if not timeframe_data:
            return self._create_error_result(stock_code, "No trading data available for signal analysis")

        # 生成各时间框架的信号
        all_signals = []
        for tf, data in timeframe_data.items():
            tf_signals = self._generate_timeframe_signals(data, tf, signal_types)
            all_signals.extend(tf_signals)

        # 信号过滤和排序
        filtered_signals = [s for s in all_signals if s.confidence >= min_confidence]
        filtered_signals.sort(key=lambda x: x.strength * x.confidence, reverse=True)

        # 汇合分析
        confluence_analysis = None
        if include_confluence and len(filtered_signals) > 0:
            confluence_analysis = self._analyze_signal_confluence(filtered_signals)

        # 风险调整
        if risk_adjusted:
            filtered_signals = self._apply_risk_adjustments(filtered_signals, timeframe_data)

        # 计算综合信号强度
        signal_strength = self._calculate_overall_signal_strength(filtered_signals, confluence_analysis)

        # 生成投资建议
        recommendation = self._generate_trading_recommendation(filtered_signals, confluence_analysis)

        # 构建结果
        scores = {
            "signal_strength": signal_strength,
            "signal_count": len(filtered_signals),
            "high_confidence_signals": len([s for s in filtered_signals if s.confidence > 0.8]),
            "confluence_score": confluence_analysis.confluence_score if confluence_analysis else 0.0,
        }

        signals_list = []
        for signal in filtered_signals[:10]:  # 只返回前10个最强信号
            signals_list.append(
                {
                    "type": f"{signal.signal_type}_signal",
                    "severity": "high" if signal.strength > 0.8 else "medium" if signal.strength > 0.6 else "low",
                    "message": f"{signal.timeframe} {signal.signal_type.upper()}信号 - {signal.description}",
                    "strength": signal.strength,
                    "confidence": signal.confidence,
                    "details": {
                        "timeframe": signal.timeframe,
                        "indicators": signal.indicators,
                        "stop_loss": signal.stop_loss,
                        "take_profit": signal.take_profit,
                        "risk_reward_ratio": signal.risk_reward_ratio,
                    },
                }
            )

        recommendations = {
            "primary_signal": recommendation.get("signal", "hold"),
            "signal_strength": signal_strength,
            "recommended_action": recommendation.get("action", "观望"),
            "confidence_level": recommendation.get("confidence", "low"),
            "risk_assessment": self._assess_signal_risk(filtered_signals),
        }

        risk_assessment = {
            "signal_consistency": self._check_signal_consistency(filtered_signals),
            "timeframe_coverage": len(timeframe_data),
            "high_confidence_ratio": len([s for s in filtered_signals if s.confidence > 0.8])
            / max(len(filtered_signals), 1),
            "confluence_support": confluence_analysis.confluence_score if confluence_analysis else 0.0,
            "recommended_stop_loss": recommendation.get("stop_loss"),
            "recommended_take_profit": recommendation.get("take_profit"),
        }

        metadata = {
            "analysis_timeframes": list(timeframe_data.keys()),
            "total_signals_generated": len(all_signals),
            "signals_after_filtering": len(filtered_signals),
            "confluence_analysis": include_confluence,
            "risk_adjusted": risk_adjusted,
            "last_signal_timestamp": max([s.timestamp for s in filtered_signals]) if filtered_signals else None,
        }

        return AnalysisResult(
            analysis_type=AnalysisType.TRADING_SIGNALS,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals_list,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata=metadata,
            raw_data=timeframe_data if kwargs.get("include_raw_data", False) else None,
        )

    except Exception as e:
        return self._create_error_result(stock_code, str(e))


def _generate_timeframe_signals(
    self, data: pd.DataFrame, timeframe: str, signal_types: Optional[List[str]] = None
) -> List[TradingSignal]:
    """生成单个时间框架的信号"""
    signals = []

    # 生成各种类型的信号
    for signal_type, signal_func in self.signal_rules.items():
        if signal_types and signal_type not in signal_types:
            continue

        try:
            type_signals = signal_func(data, timeframe)
            signals.extend(type_signals)
        except Exception as e:
            print(f"Error generating {signal_type} for {timeframe}: {e}")
            continue

    return signals


def _generate_rsi_signals(self, data: pd.DataFrame, timeframe: str) -> List[TradingSignal]:
    """生成RSI信号"""
    signals = []

    try:
        # 计算RSI
        rsi_calculator = self.indicator_factory.get_calculator("RSI_14", streaming=False)
        if rsi_calculator:
            rsi_result = rsi_calculator.calculate(data)
            rsi_values = rsi_result if isinstance(rsi_result, pd.Series) else pd.Series()

            if not rsi_values.empty:
                latest_rsi = rsi_values.iloc[-1]
                prev_rsi = rsi_values.iloc[-2] if len(rsi_values) > 1 else None

                current_price = data["close"].iloc[-1]

                # 超卖信号
                if latest_rsi < 30:
                    signal = TradingSignal(
                        signal_id=f"rsi_oversold_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                        timestamp=data.index[-1].to_pydatetime(),
                        symbol="",  # 将在上级函数中设置
                        signal_type="buy",
                        strength=min((30 - latest_rsi) / 30, 1.0),
                        confidence=0.75,
                        timeframe=timeframe,
                        indicators={"rsi": latest_rsi, "rsi_prev": prev_rsi},
                        price=current_price,
                        description=f"RSI超卖({latest_rsi:.1f})，买入信号",
                    )
                    signals.append(signal)

                # 超买信号
                elif latest_rsi > 70:
                    signal = TradingSignal(
                        signal_id=f"rsi_overbought_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                        timestamp=data.index[-1].to_pydatetime(),
                        symbol="",
                        signal_type="sell",
                        strength=min((latest_rsi - 70) / 30, 1.0),
                        confidence=0.75,
                        timeframe=timeframe,
                        indicators={"rsi": latest_rsi, "rsi_prev": prev_rsi},
                        price=current_price,
                        description=f"RSI超买({latest_rsi:.1f})，卖出信号",
                    )
                    signals.append(signal)

    except Exception as e:
        print(f"Error generating RSI signals: {e}")

    return signals


def _generate_macd_signals(self, data: pd.DataFrame, timeframe: str) -> List[TradingSignal]:
    """生成MACD信号"""
    signals = []

    try:
        # 计算MACD
        macd_calculator = self.indicator_factory.get_calculator("MACD", streaming=False)
        if macd_calculator:
            macd_result = macd_calculator.calculate(data)

            if isinstance(macd_result, pd.DataFrame) and not macd_result.empty:
                # 提取MACD直方图
                hist_col = [col for col in macd_result.columns if "hist" in col.lower()]
                if hist_col:
                    hist_values = macd_result[hist_col[0]]
                    latest_hist = hist_values.iloc[-1]
                    prev_hist = hist_values.iloc[-2] if len(hist_values) > 1 else 0

                    current_price = data["close"].iloc[-1]

                    # 金叉信号
                    if latest_hist > 0 and prev_hist <= 0:
                        signal = TradingSignal(
                            signal_id=f"macd_golden_cross_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                            timestamp=data.index[-1].to_pydatetime(),
                            symbol="",
                            signal_type="buy",
                            strength=0.8,
                            confidence=0.8,
                            timeframe=timeframe,
                            indicators={"macd_hist": latest_hist, "macd_hist_prev": prev_hist},
                            price=current_price,
                            description="MACD金叉，买入信号",
                        )
                        signals.append(signal)

                    # 死叉信号
                    elif latest_hist < 0 and prev_hist >= 0:
                        signal = TradingSignal(
                            signal_id=f"macd_death_cross_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                            timestamp=data.index[-1].to_pydatetime(),
                            symbol="",
                            signal_type="sell",
                            strength=0.8,
                            confidence=0.8,
                            timeframe=timeframe,
                            indicators={"macd_hist": latest_hist, "macd_hist_prev": prev_hist},
                            price=current_price,
                            description="MACD死叉，卖出信号",
                        )
                        signals.append(signal)

    except Exception as e:
        print(f"Error generating MACD signals: {e}")

    return signals


def _generate_bollinger_signals(self, data: pd.DataFrame, timeframe: str) -> List[TradingSignal]:
    """生成布林带信号"""
    signals = []

    try:
        # 计算布林带
        bb_calculator = self.indicator_factory.get_calculator("BBANDS", streaming=False)
        if bb_calculator:
            bb_result = bb_calculator.calculate(data)

            if isinstance(bb_result, pd.DataFrame) and not bb_result.empty:
                # 提取上下轨
                upper_col = [col for col in bb_result.columns if "upper" in col.lower()]
                lower_col = [col for col in bb_result.columns if "lower" in col.lower()]

                if upper_col and lower_col:
                    upper_values = bb_result[upper_col[0]]
                    lower_values = bb_result[lower_col[0]]

                    current_price = data["close"].iloc[-1]
                    latest_upper = upper_values.iloc[-1]
                    latest_lower = lower_values.iloc[-1]

                    # 突破上轨
                    if current_price > latest_upper:
                        signal = TradingSignal(
                            signal_id=f"bb_breakout_up_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                            timestamp=data.index[-1].to_pydatetime(),
                            symbol="",
                            signal_type="sell",
                            strength=0.7,
                            confidence=0.7,
                            timeframe=timeframe,
                            indicators={"price": current_price, "upper": latest_upper, "lower": latest_lower},
                            price=current_price,
                            description=f"突破布林上轨({current_price:.2f} > {latest_upper:.2f})",
                        )
                        signals.append(signal)

                    # 跌破下轨
                    elif current_price < latest_lower:
                        signal = TradingSignal(
                            signal_id=f"bb_breakout_down_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                            timestamp=data.index[-1].to_pydatetime(),
                            symbol="",
                            signal_type="buy",
                            strength=0.7,
                            confidence=0.7,
                            timeframe=timeframe,
                            indicators={"price": current_price, "upper": latest_upper, "lower": latest_lower},
                            price=current_price,
                            description=f"跌破布林下轨({current_price:.2f} < {latest_lower:.2f})",
                        )
                        signals.append(signal)

    except Exception as e:
        print(f"Error generating Bollinger signals: {e}")

    return signals


def _generate_ma_signals(self, data: pd.DataFrame, timeframe: str) -> List[TradingSignal]:
    """生成均线信号"""
    signals = []

    try:
        # 计算多条均线
        ma_periods = [5, 10, 20, 30]
        ma_values = {}

        for period in ma_periods:
            ma_calculator = self.indicator_factory.get_calculator(f"SMA_{period}", streaming=False)
            if ma_calculator:
                ma_result = ma_calculator.calculate(data)
                if isinstance(ma_result, pd.Series):
                    ma_values[period] = ma_result

        if len(ma_values) >= 2:
            current_price = data["close"].iloc[-1]

            # 多头排列
            ma5 = ma_values[5].iloc[-1] if 5 in ma_values else None
            ma10 = ma_values[10].iloc[-1] if 10 in ma_values else None
            ma20 = ma_values[20].iloc[-1] if 20 in ma_values else None

            if ma5 and ma10 and ma20 and ma5 > ma10 > ma20:
                signal = TradingSignal(
                    signal_id=f"ma_bullish_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                    timestamp=data.index[-1].to_pydatetime(),
                    symbol="",
                    signal_type="buy",
                    strength=0.6,
                    confidence=0.65,
                    timeframe=timeframe,
                    indicators={"ma5": ma5, "ma10": ma10, "ma20": ma20, "price": current_price},
                    price=current_price,
                    description="均线多头排列，买入信号",
                )
                signals.append(signal)

            # 空头排列
            elif ma5 and ma10 and ma20 and ma5 < ma10 < ma20:
                signal = TradingSignal(
                    signal_id=f"ma_bearish_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                    timestamp=data.index[-1].to_pydatetime(),
                    symbol="",
                    signal_type="sell",
                    strength=0.6,
                    confidence=0.65,
                    timeframe=timeframe,
                    indicators={"ma5": ma5, "ma10": ma10, "ma20": ma20, "price": current_price},
                    price=current_price,
                    description="均线空头排列，卖出信号",
                )
                signals.append(signal)

    except Exception as e:
        print(f"Error generating MA signals: {e}")

    return signals


def _generate_volume_signals(self, data: pd.DataFrame, timeframe: str) -> List[TradingSignal]:
    """生成成交量信号"""
    signals = []

    try:
        if "volume" in data.columns:
            # 计算成交量均线
            volume_ma = data["volume"].rolling(window=20).mean()
            latest_volume = data["volume"].iloc[-1]
            avg_volume = volume_ma.iloc[-1]

            # 放量信号
            if latest_volume > avg_volume * 1.5:
                current_price = data["close"].iloc[-1]
                price_change = (data["close"].iloc[-1] - data["close"].iloc[-2]) / data["close"].iloc[-2]

                signal_type = "buy" if price_change > 0 else "sell"
                strength = min(latest_volume / avg_volume / 2, 1.0)

                signal = TradingSignal(
                    signal_id=f"volume_breakout_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                    timestamp=data.index[-1].to_pydatetime(),
                    symbol="",
                    signal_type=signal_type,
                    strength=strength,
                    confidence=0.6,
                    timeframe=timeframe,
                    indicators={"volume": latest_volume, "avg_volume": avg_volume, "price_change": price_change},
                    price=current_price,
                    description=f"成交量放大({latest_volume:.0f} vs {avg_volume:.0f})",
                )
                signals.append(signal)

    except Exception as e:
        print(f"Error generating volume signals: {e}")

    return signals


def _generate_sr_signals(self, data: pd.DataFrame, timeframe: str) -> List[TradingSignal]:
    """生成支撑阻力信号"""
    signals = []

    try:
        current_price = data["close"].iloc[-1]

        # 计算最近的支撑阻力位（简化的实现）
        recent_high = data["high"].rolling(window=20).max().iloc[-1]
        recent_low = data["low"].rolling(window=20).min().iloc[-1]

        # 接近阻力位
        if current_price > recent_high * 0.98 and current_price < recent_high * 1.02:
            signal = TradingSignal(
                signal_id=f"resistance_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                timestamp=data.index[-1].to_pydatetime(),
                symbol="",
                signal_type="sell",
                strength=0.65,
                confidence=0.6,
                timeframe=timeframe,
                indicators={"price": current_price, "resistance": recent_high},
                price=current_price,
                description=f"接近阻力位({recent_high:.2f})，卖出信号",
            )
            signals.append(signal)

        # 接近支撑位
        elif current_price > recent_low * 0.98 and current_price < recent_low * 1.02:
            signal = TradingSignal(
                signal_id=f"support_{timeframe}_{data.index[-1].strftime('%Y%m%d_%H%M%S')}",
                timestamp=data.index[-1].to_pydatetime(),
                symbol="",
                signal_type="buy",
                strength=0.65,
                confidence=0.6,
                timeframe=timeframe,
                indicators={"price": current_price, "support": recent_low},
                price=current_price,
                description=f"接近支撑位({recent_low:.2f})，买入信号",
            )
            signals.append(signal)

    except Exception as e:
        print(f"Error generating support/resistance signals: {e}")

    return signals


def _analyze_signal_confluence(self, signals: List[TradingSignal]) -> SignalConfluence:
    """分析信号汇合"""
    if not signals:
        return SignalConfluence(0.0, 0, 0, "hold", [], [])

    # 按时间框架分组
    timeframe_signals = {}
    for signal in signals:
        tf = signal.timeframe
        if tf not in timeframe_signals:
            timeframe_signals[tf] = []
        timeframe_signals[tf].append(signal)

    # 计算时间框架共识
    buy_signals = [s for s in signals if s.signal_type == "buy"]
    sell_signals = [s for s in signals if s.signal_type == "sell"]

    timeframe_consensus = max(len(timeframe_signals.get(tf, [])) for tf in self.timeframes)

    # 计算指标共识
    indicator_types = {}
    for signal in signals:
        for indicator_name in signal.indicators.keys():
            indicator_base = indicator_name.split("_")[0]
            if indicator_base not in indicator_types:
                indicator_types[indicator_base] = []
            indicator_types[indicator_base].append(signal)

    indicator_consensus = (
        max(len(indicator_types.get(ind, [])) for ind in indicator_types.keys()) if indicator_types else 0
    )

    # 计算综合得分
    confluence_score = min(
        (len(buy_signals) + len(sell_signals)) / max(len(signals), 1) * 0.4
        + timeframe_consensus / len(self.timeframes) * 0.3
        + indicator_consensus / max(len(signals), 1) * 0.3,
        1.0,
    )

    # 确定综合信号
    if len(buy_signals) > len(sell_signals) and confluence_score > 0.6:
        overall_signal = "buy"
        supporting_signals = buy_signals
        conflicting_signals = sell_signals
    elif len(sell_signals) > len(buy_signals) and confluence_score > 0.6:
        overall_signal = "sell"
        supporting_signals = sell_signals
        conflicting_signals = buy_signals
    else:
        overall_signal = "hold"
        supporting_signals = []
        conflicting_signals = []

    return SignalConfluence(
        confluence_score=confluence_score,
        timeframe_consensus=timeframe_consensus,
        indicator_consensus=indicator_consensus,
        overall_signal=overall_signal,
        supporting_signals=supporting_signals,
        conflicting_signals=conflicting_signals,
    )


def _apply_risk_adjustments(
    self, signals: List[TradingSignal], timeframe_data: Dict[str, pd.DataFrame]
) -> List[TradingSignal]:
    """应用风险调整"""
    adjusted_signals = []

    for signal in signals:
        try:
            # 计算止损位
            current_price = signal.price
            atr_value = self._calculate_atr(timeframe_data.get(signal.timeframe, pd.DataFrame()))

            if signal.signal_type == "buy":
                stop_loss = current_price - atr_value * 2
                take_profit = current_price + atr_value * 4
            else:
                stop_loss = current_price + atr_value * 2
                take_profit = current_price - atr_value * 4

            # 计算风险收益比
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0

            # 调整信号强度
            adjusted_strength = signal.strength
            if risk_reward_ratio < self.risk_params["min_risk_reward"]:
                adjusted_strength *= 0.7  # 风险收益比不足，降低强度

            # 更新信号
            adjusted_signal = TradingSignal(
                signal_id=signal.signal_id,
                timestamp=signal.timestamp,
                symbol=signal.symbol,
                signal_type=signal.signal_type,
                strength=adjusted_strength,
                confidence=signal.confidence,
                timeframe=signal.timeframe,
                indicators=signal.indicators,
                price=signal.price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                description=signal.description,
                risk_reward_ratio=risk_reward_ratio,
                validity_period=signal.timestamp + timedelta(hours=24),
            )
            adjusted_signals.append(adjusted_signal)

        except Exception as e:
            print(f"Error applying risk adjustment to signal {signal.signal_id}: {e}")
            adjusted_signals.append(signal)

    return adjusted_signals


def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
    """计算ATR值"""
    if data.empty or "high" not in data.columns or "low" not in data.columns or "close" not in data.columns:
        return 0.0

    try:
        high = data["high"]
        low = data["low"]
        close = data["close"].shift(1)

        tr = pd.concat([high - low, (high - close).abs(), (low - close).abs()], axis=1).max(axis=1)

        atr = tr.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.0

    except Exception:
        return 0.0


def _calculate_overall_signal_strength(
    self, signals: List[TradingSignal], confluence: Optional[SignalConfluence]
) -> float:
    """计算整体信号强度"""
    if not signals:
        return 0.0

    # 基础信号强度
    avg_strength = np.mean([s.strength * s.confidence for s in signals])

    # 汇合加成
    confluence_bonus = confluence.confluence_score * 0.2 if confluence else 0.0

    # 信号一致性加成
    buy_signals = [s for s in signals if s.signal_type == "buy"]
    sell_signals = [s for s in signals if s.signal_type == "sell"]
    consistency_ratio = max(len(buy_signals), len(sell_signals)) / len(signals)
    consistency_bonus = consistency_ratio * 0.1

    return min(avg_strength + confluence_bonus + consistency_bonus, 1.0)


def _generate_trading_recommendation(
    self, signals: List[TradingSignal], confluence: Optional[SignalConfluence]
) -> Dict[str, Any]:
    """生成交易建议"""
    if not signals:
        return {"signal": "hold", "action": "观望", "confidence": "low", "reason": "无有效信号"}

    # 计算各类型信号数量
    buy_signals = [s for s in signals if s.signal_type == "buy"]
    sell_signals = [s for s in signals if s.signal_type == "sell"]

    # 基于信号数量和强度决定建议
    buy_strength = np.mean([s.strength * s.confidence for s in buy_signals]) if buy_signals else 0
    sell_strength = np.mean([s.strength * s.confidence for s in sell_signals]) if sell_signals else 0

    # 考虑汇合分析
    if confluence and confluence.confluence_score > 0.7:
        if confluence.overall_signal == "buy" and buy_strength > sell_strength:
            signal = "buy"
            action = "强烈买入"
            confidence = "high"
            stop_loss = min([s.stop_loss for s in buy_signals if s.stop_loss] or [None])
            take_profit = max([s.take_profit for s in buy_signals if s.take_profit] or [None])
        elif confluence.overall_signal == "sell" and sell_strength > buy_strength:
            signal = "sell"
            action = "强烈卖出"
            confidence = "high"
            stop_loss = max([s.stop_loss for s in sell_signals if s.stop_loss] or [None])
            take_profit = min([s.take_profit for s in sell_signals if s.take_profit] or [None])
        else:
            signal = "hold"
            action = "观望"
            confidence = "medium"
            stop_loss = None
            take_profit = None
    else:
        if buy_strength > sell_strength and buy_strength > 0.6:
            signal = "buy"
            action = "考虑买入"
            confidence = "medium"
            stop_loss = min([s.stop_loss for s in buy_signals if s.stop_loss] or [None])
            take_profit = max([s.take_profit for s in buy_signals if s.take_profit] or [None])
        elif sell_strength > buy_strength and sell_strength > 0.6:
            signal = "sell"
            action = "考虑卖出"
            confidence = "medium"
            stop_loss = max([s.stop_loss for s in sell_signals if s.stop_loss] or [None])
            take_profit = min([s.take_profit for s in sell_signals if s.take_profit] or [None])
        else:
            signal = "hold"
            action = "观望"
            confidence = "low"
            stop_loss = None
            take_profit = None

    return {
        "signal": signal,
        "action": action,
        "confidence": confidence,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "buy_signals": len(buy_signals),
        "sell_signals": len(sell_signals),
    }


def _assess_signal_risk(self, signals: List[TradingSignal]) -> str:
    """评估信号风险水平"""
    if not signals:
        return "low"

    # 计算信号一致性
    buy_signals = [s for s in signals if s.signal_type == "buy"]
    sell_signals = [s for s in signals if s.signal_type == "sell"]

    if len(buy_signals) > 0 and len(sell_signals) > 0:
        # 信号冲突，高风险
        return "high"
    elif len(signals) >= 3:
        # 多个一致信号，中等风险
        return "medium"
    else:
        # 信号较少，低风险
        return "low"


def _check_signal_consistency(self, signals: List[TradingSignal]) -> float:
    """检查信号一致性"""
    if not signals:
        return 0.0

    buy_count = sum(1 for s in signals if s.signal_type == "buy")
    sell_count = sum(1 for s in signals if s.signal_type == "sell")

    total = len(signals)
    max_consistent = max(buy_count, sell_count)

    return max_consistent / total if total > 0 else 0.0


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.TRADING_SIGNALS,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"交易信号分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
