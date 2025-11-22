"""
Strategy Base Class

策略基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class SignalType(str, Enum):
    """信号类型"""
    LONG = "LONG"       # 做多
    SHORT = "SHORT"     # 做空
    EXIT = "EXIT"       # 平仓
    HOLD = "HOLD"       # 持有


@dataclass
class StrategySignal:
    """策略信号"""
    symbol: str
    signal_type: SignalType
    strength: float = 1.0  # 信号强度 0-1
    reason: str = ""
    target_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None  # 额外元数据


class BaseStrategy(ABC):
    """
    策略基类

    所有策略模板必须继承此类
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """
        初始化策略

        Args:
            parameters: 策略参数字典
        """
        self.parameters = parameters or {}
        self.name = self.__class__.__name__
        self.description = ""
        self.version = "1.0.0"

        # 历史数据缓存
        self.price_history: Dict[str, List[Dict]] = {}  # symbol -> [OHLCV data]
        self.indicator_cache: Dict[str, Dict] = {}  # symbol -> {indicator: values}

        # 初始化参数
        self._init_parameters()

    @abstractmethod
    def _init_parameters(self):
        """初始化策略参数（子类实现）"""
        pass

    @abstractmethod
    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """
        生成交易信号

        Args:
            symbol: 股票代码
            current_data: 当前市场数据
            position: 当前持仓信息

        Returns:
            交易信号或None
        """
        pass

    def update_history(self, symbol: str, data: Dict[str, Any]):
        """
        更新历史数据

        Args:
            symbol: 股票代码
            data: OHLCV数据
        """
        if symbol not in self.price_history:
            self.price_history[symbol] = []

        self.price_history[symbol].append(data)

        # 限制历史数据长度
        max_history = self.parameters.get('max_history', 500)
        if len(self.price_history[symbol]) > max_history:
            self.price_history[symbol] = self.price_history[symbol][-max_history:]

    def get_closes(self, symbol: str, n: int = None) -> List[float]:
        """获取收盘价序列"""
        history = self.price_history.get(symbol, [])
        closes = [float(h.get('close', 0)) for h in history]
        return closes[-n:] if n else closes

    def get_volumes(self, symbol: str, n: int = None) -> List[int]:
        """获取成交量序列"""
        history = self.price_history.get(symbol, [])
        volumes = [int(h.get('volume', 0)) for h in history]
        return volumes[-n:] if n else volumes

    # 技术指标计算方法
    def sma(self, prices: List[float], period: int) -> Optional[float]:
        """简单移动平均"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def ema(self, prices: List[float], period: int) -> Optional[float]:
        """指数移动平均"""
        if len(prices) < period:
            return None

        multiplier = 2 / (period + 1)
        ema_value = prices[0]

        for price in prices[1:]:
            ema_value = (price - ema_value) * multiplier + ema_value

        return ema_value

    def rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """相对强弱指标"""
        if len(prices) < period + 1:
            return None

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def bollinger_bands(
        self, prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Optional[tuple]:
        """布林带"""
        if len(prices) < period:
            return None

        import numpy as np
        recent = prices[-period:]
        middle = np.mean(recent)
        std = np.std(recent)

        upper = middle + std_dev * std
        lower = middle - std_dev * std

        return (upper, middle, lower)

    def atr(self, history: List[Dict], period: int = 14) -> Optional[float]:
        """平均真实波幅"""
        if len(history) < period + 1:
            return None

        true_ranges = []
        for i in range(1, len(history)):
            high = float(history[i]['high'])
            low = float(history[i]['low'])
            prev_close = float(history[i - 1]['close'])

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        return sum(true_ranges[-period:]) / period

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        """获取默认参数"""
        return {}

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        """获取参数schema（用于UI）"""
        return []

    def get_info(self) -> Dict[str, Any]:
        """获取策略信息"""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'parameters': self.parameters,
            'default_parameters': self.get_default_parameters(),
            'parameter_schema': self.get_parameter_schema()
        }
