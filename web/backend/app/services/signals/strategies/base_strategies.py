"""
Signal Engine - 信号引擎

基于技术指标和市场数据的智能交易信号生成引擎：
- 多指标融合分析
- 实时信号生成
- 策略规则引擎
- 信号质量评估

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """信号类型"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalStrength(str, Enum):
    """信号强度"""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class TradingSignal:
    """交易信号"""

    signal_id: str
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    confidence: float  # 0.0 - 1.0
    price: float
    timestamp: datetime = field(default_factory=datetime.now)
    indicators: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    validity_period: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "signal_type": self.signal_type.value,
            "strength": self.strength.value,
            "confidence": self.confidence,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
            "indicators": self.indicators,
            "reason": self.reason,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_reward_ratio": self.risk_reward_ratio,
            "validity_period": self.validity_period.isoformat() if self.validity_period else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradingSignal":
        """从字典创建信号"""
        return cls(
            signal_id=data["signal_id"],
            symbol=data["symbol"],
            signal_type=SignalType(data["signal_type"]),
            strength=SignalStrength(data["strength"]),
            confidence=data["confidence"],
            price=data["price"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            indicators=data.get("indicators", {}),
            reason=data.get("reason", ""),
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            risk_reward_ratio=data.get("risk_reward_ratio"),
            validity_period=datetime.fromisoformat(data["validity_period"]) if data.get("validity_period") else None,
        )


class SignalStrategy:
    """
    信号策略基类

    定义信号生成规则和逻辑
    """

    def __init__(self, name: str, indicators: List[str], parameters: Dict[str, Any]):
        """
        初始化信号策略

        Args:
            name: 策略名称
            indicators: 所需指标列表
            parameters: 策略参数
        """
        self.name = name
        self.indicators = indicators
        self.parameters = parameters

    def evaluate(
        self, symbol: str, indicator_data: Dict[str, Any], market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """
        评估信号

        Args:
            symbol: 股票代码
            indicator_data: 指标数据
            market_data: 市场数据

        Returns:
            交易信号，如果没有信号则返回None
        """
        raise NotImplementedError("Subclasses must implement evaluate method")

    def calculate_stop_loss(self, entry_price: float, atr_value: Optional[float] = None) -> float:
        """计算止损价"""
        if atr_value:
            # 使用ATR计算止损
            multiplier = self.parameters.get("stop_loss_atr_multiplier", 1.5)
            return entry_price - (atr_value * multiplier)
        else:
            # 使用百分比止损
            percentage = self.parameters.get("stop_loss_percentage", 0.05)
            return entry_price * (1 - percentage)

    def calculate_take_profit(self, entry_price: float, stop_loss: float) -> float:
        """计算止盈价"""
        risk_reward_ratio = self.parameters.get("risk_reward_ratio", 2.0)
        risk_amount = entry_price - stop_loss
        return entry_price + (risk_amount * risk_reward_ratio)


class RSIStrategy(SignalStrategy):
    """RSI策略"""

    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(name="rsi_strategy", indicators=["rsi"], parameters=parameters)

    def evaluate(
        self, symbol: str, indicator_data: Dict[str, Any], market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """基于RSI评估信号"""
        rsi_data = indicator_data.get("rsi", [])
        if not rsi_data or len(rsi_data) < 2:
            return None

        current_rsi = rsi_data[-1]
        previous_rsi = rsi_data[-2]

        oversold_level = self.parameters.get("oversold_level", 30)
        overbought_level = self.parameters.get("overbought_level", 70)

        current_price = market_data.get("close", [0])[-1]

        if current_rsi < oversold_level and previous_rsi >= oversold_level:
            # RSI从高位跌破超卖线，买入信号
            stop_loss = self.calculate_stop_loss(current_price)
            take_profit = self.calculate_take_profit(current_price, stop_loss)

            return TradingSignal(
                signal_id=f"rsi_oversold_{symbol}_{datetime.now().timestamp()}",
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.MODERATE,
                confidence=min(0.8, (oversold_level - current_rsi) / oversold_level),
                price=current_price,
                indicators={"rsi": current_rsi},
                reason=f"RSI超卖反弹: {current_rsi:.1f}",
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=self.parameters.get("risk_reward_ratio", 2.0),
            )

        elif current_rsi > overbought_level and previous_rsi <= overbought_level:
            # RSI从低位突破超买线，卖出信号
            stop_loss = self.calculate_stop_loss(current_price)
            take_profit = self.calculate_take_profit(current_price, stop_loss)

            return TradingSignal(
                signal_id=f"rsi_overbought_{symbol}_{datetime.now().timestamp()}",
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.MODERATE,
                confidence=min(0.8, (current_rsi - overbought_level) / (100 - overbought_level)),
                price=current_price,
                indicators={"rsi": current_rsi},
                reason=f"RSI超买回落: {current_rsi:.1f}",
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=self.parameters.get("risk_reward_ratio", 2.0),
            )

        return None


class MACDStrategy(SignalStrategy):
    """MACD策略"""

    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(name="macd_strategy", indicators=["macd"], parameters=parameters)

    def evaluate(
        self, symbol: str, indicator_data: Dict[str, Any], market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """基于MACD评估信号"""
        macd_data = indicator_data.get("macd", {})
        if not macd_data or "macd" not in macd_data or "signal" not in macd_data:
            return None

        macd_line = macd_data["macd"]
        signal_line = macd_data["signal"]

        if len(macd_line) < 3 or len(signal_line) < 3:
            return None

        # 检查金叉和死叉
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        prev_macd = macd_line[-2]
        prev_signal = signal_line[-2]

        current_price = market_data.get("close", [0])[-1]

        if prev_macd <= prev_signal and current_macd > current_signal:
            # 金叉，买入信号
            stop_loss = self.calculate_stop_loss(current_price)
            take_profit = self.calculate_take_profit(current_price, stop_loss)

            return TradingSignal(
                signal_id=f"macd_golden_cross_{symbol}_{datetime.now().timestamp()}",
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.STRONG,
                confidence=0.75,
                price=current_price,
                indicators={"macd": current_macd, "signal": current_signal},
                reason=f"MACD金叉: MACD={current_macd:.4f}, Signal={current_signal:.4f}",
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=self.parameters.get("risk_reward_ratio", 2.0),
            )

        elif prev_macd >= prev_signal and current_macd < current_signal:
            # 死叉，卖出信号
            stop_loss = self.calculate_stop_loss(current_price)
            take_profit = self.calculate_take_profit(current_price, stop_loss)

            return TradingSignal(
                signal_id=f"macd_death_cross_{symbol}_{datetime.now().timestamp()}",
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.STRONG,
                confidence=0.75,
                price=current_price,
                indicators={"macd": current_macd, "signal": current_signal},
                reason=f"MACD死叉: MACD={current_macd:.4f}, Signal={current_signal:.4f}",
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=self.parameters.get("risk_reward_ratio", 2.0),
            )

        return None


class BollingerBandsStrategy(SignalStrategy):
    """布林带策略"""

    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(name="bbands_strategy", indicators=["bbands"], parameters=parameters)

    def evaluate(
        self, symbol: str, indicator_data: Dict[str, Any], market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """基于布林带评估信号"""
        bb_data = indicator_data.get("bbands", {})
        if not bb_data or "upper" not in bb_data or "lower" not in bb_data or "middle" not in bb_data:
            return None

        upper = bb_data["upper"]
        lower = bb_data["lower"]
        middle = bb_data["middle"]

        if len(upper) < 2 or len(lower) < 2 or len(middle) < 2:
            return None

        current_price = market_data.get("close", [0])[-1]
        prev_price = market_data.get("close", [0])[-2] if len(market_data.get("close", [])) > 1 else current_price

        # 检查价格突破布林带
        if prev_price <= upper[-2] and current_price > upper[-1]:
            # 突破上轨，卖出信号
            stop_loss = self.calculate_stop_loss(current_price)
            take_profit = self.calculate_take_profit(current_price, stop_loss)

            return TradingSignal(
                signal_id=f"bb_upper_breakout_{symbol}_{datetime.now().timestamp()}",
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.MODERATE,
                confidence=0.7,
                price=current_price,
                indicators={
                    "upper": upper[-1],
                    "middle": middle[-1],
                    "lower": lower[-1],
                },
                reason=f"突破布林上轨: 价格={current_price:.2f}, 上轨={upper[-1]:.2f}",
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=self.parameters.get("risk_reward_ratio", 2.0),
            )

        elif prev_price >= lower[-2] and current_price < lower[-1]:
            # 跌破下轨，买入信号
            stop_loss = self.calculate_stop_loss(current_price)
            take_profit = self.calculate_take_profit(current_price, stop_loss)

            return TradingSignal(
                signal_id=f"bb_lower_breakout_{symbol}_{datetime.now().timestamp()}",
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.MODERATE,
                confidence=0.7,
                price=current_price,
                indicators={
                    "upper": upper[-1],
                    "middle": middle[-1],
                    "lower": lower[-1],
                },
                reason=f"跌破布林下轨: 价格={current_price:.2f}, 下轨={lower[-1]:.2f}",
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=self.parameters.get("risk_reward_ratio", 2.0),
            )

        return None
