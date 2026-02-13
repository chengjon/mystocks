"""
市场数据聚合服务 - Market Data Aggregation Service

Task 7: 实现实时OHLCV柱线聚合与多时间周期支持

功能特性:
- 实时OHLCV柱线构建（1m, 5m, 15m, 1h, 1d）
- 高效的内存缓冲状态管理
- 数据质量验证和异常检测
- PostgreSQL TimescaleDB存储集成
- 与Task 6流服务的集成用于实时分发
- 支持多股票代码同时聚合

Author: Claude Code
Date: 2025-11-07
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger()


class Timeframe(str, Enum):
    """时间周期枚举"""

    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"


# 时间周期到秒数的映射
TIMEFRAME_SECONDS = {
    Timeframe.ONE_MINUTE: 60,
    Timeframe.FIVE_MINUTES: 300,
    Timeframe.FIFTEEN_MINUTES: 900,
    Timeframe.ONE_HOUR: 3600,
    Timeframe.ONE_DAY: 86400,
}


@dataclass
class Tick:
    """单个交易tick数据"""

    symbol: str
    timestamp: int  # Unix毫秒时间戳
    price: Decimal
    volume: int
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None


@dataclass
class OHLCV:
    """OHLCV柱线数据"""

    symbol: str
    timeframe: Timeframe
    timestamp: int  # 柱线开始的Unix毫秒时间戳
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    tick_count: int = 1
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe.value,
            "timestamp": self.timestamp,
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "volume": self.volume,
            "tick_count": self.tick_count,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class TimeframeBuffer:
    """单个时间周期的缓冲区管理器"""

    symbol: str
    timeframe: Timeframe
    current_bar: Optional[OHLCV] = None
    last_bar_timestamp: int = 0

    def _get_bar_start_time(self, timestamp: int) -> int:
        """获取给定timestamp所属的柱线起始时间"""
        timeframe_seconds = TIMEFRAME_SECONDS[self.timeframe]
        # 向下取整到最近的时间周期
        return (timestamp // (timeframe_seconds * 1000)) * (timeframe_seconds * 1000)

    def add_tick(self, tick: Tick) -> Optional[OHLCV]:
        """
        添加tick并更新柱线状态

        返回已完成的柱线（如果跨越了时间边界），否则返回None
        """
        bar_start_time = self._get_bar_start_time(tick.timestamp)

        # 如果是新的柱线周期
        if self.current_bar is None or bar_start_time > self.current_bar.timestamp:
            completed_bar = self.current_bar
            if completed_bar is not None:
                completed_bar.completed = True
                self.last_bar_timestamp = completed_bar.timestamp

            # 创建新柱线
            self.current_bar = OHLCV(
                symbol=tick.symbol,
                timeframe=self.timeframe,
                timestamp=bar_start_time,
                open=tick.price,
                high=tick.price,
                low=tick.price,
                close=tick.price,
                volume=tick.volume,
                tick_count=1,
            )

            return completed_bar

        # 更新当前柱线
        self.current_bar.high = max(self.current_bar.high, tick.price)
        self.current_bar.low = min(self.current_bar.low, tick.price)
        self.current_bar.close = tick.price
        self.current_bar.volume += tick.volume
        self.current_bar.tick_count += 1

        return None

    def get_open_bar(self) -> Optional[OHLCV]:
        """获取当前开放的柱线（未完成）"""
        return self.current_bar

    def force_complete_bar(self) -> Optional[OHLCV]:
        """强制完成当前柱线（用于EOD或强制完成）"""
        if self.current_bar is not None:
            self.current_bar.completed = True
            self.last_bar_timestamp = self.current_bar.timestamp
            completed = self.current_bar
            self.current_bar = None
            return completed
        return None


class BarValidator:
    """OHLCV柱线验证器"""

    def __init__(
        self,
        max_price_spike: float = 0.5,  # 最大价格涨跌幅（50%）
        min_volume: int = 0,  # 最小成交量
        max_volume: Optional[int] = None,  # 最大成交量
    ):
        """
        初始化验证器

        Args:
            max_price_spike: 最大价格涨跌幅（作为之前收盘价的百分比）
            min_volume: 最小成交量
            max_volume: 最大成交量
        """
        self.max_price_spike = max_price_spike
        self.min_volume = min_volume
        self.max_volume = max_volume

    def validate_ohlcv(self, bar: OHLCV, prev_close: Optional[Decimal] = None) -> Tuple[bool, Optional[str]]:
        """
        验证OHLCV柱线

        返回 (is_valid, error_message)
        """
        # 验证OHLC关系
        if not (bar.open > 0 and bar.high > 0 and bar.low > 0 and bar.close > 0):
            return False, "Invalid price values (must be > 0)"

        if not (bar.low <= bar.open and bar.low <= bar.close):
            return False, "Low price higher than Open or Close"

        if not (bar.high >= bar.open and bar.high >= bar.close):
            return False, "High price lower than Open or Close"

        if bar.low > bar.high:
            return False, "Low price higher than High"

        # 验证成交量
        if bar.volume < self.min_volume:
            return (
                False,
                f"Volume {bar.volume} below minimum {self.min_volume}",
            )

        if self.max_volume is not None and bar.volume > self.max_volume:
            return (
                False,
                f"Volume {bar.volume} exceeds maximum {self.max_volume}",
            )

        # 验证价格涨跌幅
        if prev_close is not None and prev_close > 0:
            max_allowed_price = prev_close * (Decimal(1) + Decimal(self.max_price_spike))
            min_allowed_price = prev_close * (Decimal(1) - Decimal(self.max_price_spike))

            if bar.high > max_allowed_price or bar.low < min_allowed_price:
                return (
                    False,
                    f"Price spike exceeds {self.max_price_spike * 100}%",
                )

        return True, None

    def detect_anomalies(self, bar: OHLCV) -> List[str]:
        """
        检测柱线异常

        返回异常列表
        """
        anomalies = []

        # 检测无成交量
        if bar.volume == 0:
            anomalies.append("Zero volume")

        # 检测十字星（价格没有变化）
        if bar.open == bar.high and bar.high == bar.low and bar.low == bar.close:
            anomalies.append("Doji candle (no price movement)")

        # 检测长影线
        if bar.high > 0 and bar.low > 0:
            body = abs(bar.close - bar.open)
            upper_shadow = bar.high - max(bar.close, bar.open)
            lower_shadow = min(bar.close, bar.open) - bar.low

            if body > 0:
                upper_ratio = upper_shadow / body
                lower_ratio = lower_shadow / body

                if upper_ratio > 3:
                    anomalies.append("Long upper shadow")
                if lower_ratio > 3:
                    anomalies.append("Long lower shadow")

        return anomalies


class AggregationEngine:
    """实时OHLCV聚合引擎"""

    def __init__(self, validator: Optional[BarValidator] = None):
        """
        初始化聚合引擎

        Args:
            validator: OHLCV验证器实例
        """
        self.buffers: Dict[Tuple[str, Timeframe], TimeframeBuffer] = {}
        self.validator = validator or BarValidator()
        self.completed_bars: List[OHLCV] = []
        self.last_price: Dict[str, Decimal] = {}  # symbol -> last close price

        # 指标
        self.ticks_processed = 0
        self.bars_completed = 0
        self.validation_errors = 0
        self.last_update_time = datetime.now(timezone.utc)

        logger.info("✅ Aggregation Engine initialized")

    def add_tick(self, tick: Tick) -> List[OHLCV]:
        """
        处理单个tick并返回所有完成的柱线

        Args:
            tick: Tick对象

        Returns:
            已完成的OHLCV柱线列表
        """
        self.ticks_processed += 1
        self.last_update_time = datetime.now(timezone.utc)
        completed_bars = []

        # 处理所有时间周期
        for timeframe in Timeframe:
            key = (tick.symbol, timeframe)

            # 获取或创建缓冲区
            if key not in self.buffers:
                self.buffers[key] = TimeframeBuffer(symbol=tick.symbol, timeframe=timeframe)

            buffer = self.buffers[key]
            completed_bar = buffer.add_tick(tick)

            # 如果产生了完成的柱线，进行验证
            if completed_bar is not None:
                prev_close = self.last_price.get(tick.symbol)
                is_valid, error_msg = self.validator.validate_ohlcv(completed_bar, prev_close)

                if is_valid:
                    self.bars_completed += 1
                    completed_bars.append(completed_bar)
                    logger.debug(
                        "📊 Bar completed",
                        symbol=tick.symbol,
                        timeframe=timeframe.value,
                        close=float(completed_bar.close),
                    )
                else:
                    self.validation_errors += 1
                    logger.warning(
                        "⚠️ Validation failed for completed bar",
                        symbol=tick.symbol,
                        timeframe=timeframe.value,
                        error=error_msg,
                    )

        # 更新最后价格
        self.last_price[tick.symbol] = tick.price

        return completed_bars

    def get_open_bar(self, symbol: str, timeframe: Timeframe) -> Optional[OHLCV]:
        """获取开放的柱线（未完成）"""
        key = (symbol, timeframe)
        if key in self.buffers:
            return self.buffers[key].get_open_bar()
        return None

    def force_complete_bars(self, symbol: str) -> List[OHLCV]:
        """
        强制完成给定symbol的所有开放柱线

        用于EOD或市场暂停
        """
        completed = []
        for timeframe in Timeframe:
            key = (symbol, timeframe)
            if key in self.buffers:
                bar = self.buffers[key].force_complete_bar()
                if bar is not None:
                    completed.append(bar)
                    self.bars_completed += 1

        logger.info(
            "🔒 Forced completion of bars",
            symbol=symbol,
            count=len(completed),
        )

        return completed

    def get_stats(self) -> Dict[str, Any]:
        """获取聚合引擎统计信息"""
        active_buffers = sum(1 for buf in self.buffers.values() if buf.get_open_bar() is not None)

        return {
            "ticks_processed": self.ticks_processed,
            "bars_completed": self.bars_completed,
            "validation_errors": self.validation_errors,
            "active_buffers": active_buffers,
            "total_symbols": len(set(buf.symbol for buf in self.buffers.values())),
            "uptime_seconds": (datetime.now(timezone.utc) - self.last_update_time).total_seconds(),
            "last_update": self.last_update_time.isoformat(),
        }


# 全局单例
_aggregation_engine: Optional[AggregationEngine] = None


def get_aggregation_engine() -> AggregationEngine:
    """获取聚合引擎单例"""
    global _aggregation_engine
    if _aggregation_engine is None:
        _aggregation_engine = AggregationEngine()
    return _aggregation_engine


def reset_aggregation_engine() -> None:
    """重置聚合引擎（仅用于测试）"""
    global _aggregation_engine
    _aggregation_engine = None
