"""
Watchlist Value Objects
自选股领域值对象

定义自选股系统中不可变的值对象。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class WatchlistType(Enum):
    """自选股类型"""

    TECHNICAL = "technical"  # 技术关注
    FUNDAMENTAL = "fundamental"  # 基本面关注
    EVENT_DRIVEN = "event"  # 事件驱动
    HOLDING = "holding"  # 持仓股
    TEMPORARY = "temporary"  # 临时观察


@dataclass(frozen=True)
class StockCode:
    """股票代码值对象"""

    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("股票代码不能为空")
        if len(self.value) > 10:
            raise ValueError("股票代码长度不能超过10位")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class StockName:
    """股票名称值对象"""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) > 50:
            raise ValueError("股票名称长度必须在1-50之间")


@dataclass(frozen=True)
class SnapshotTime:
    """快照时间值对象"""

    timestamp: datetime

    @classmethod
    def now(cls) -> "SnapshotTime":
        return cls(timestamp=datetime.now())

    def to_strftime(self, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return self.timestamp.strftime(fmt)


@dataclass
class IndicatorValue:
    """技术指标值对象"""

    indicator_id: str
    value: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class IndicatorSnapshot:
    """指标快照值对象"""

    snapshot_id: str
    stock_code: str
    captured_at: datetime
    indicators: Dict[str, IndicatorValue]
    price_data: Dict[str, float]
    reference_time: datetime = None
    reference_indicators: Dict[str, IndicatorValue] = None

    def get_indicator(self, indicator_id: str) -> Optional[IndicatorValue]:
        return self.indicators.get(indicator_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "stock_code": self.stock_code,
            "captured_at": self.captured_at.isoformat(),
            "indicators": {k: {"id": v.indicator_id, "value": v.value} for k, v in self.indicators.items()},
            "price_data": self.price_data,
            "reference_time": self.reference_time.isoformat() if self.reference_time else None,
        }


@dataclass
class PriceData:
    """价格数据值对象"""

    open: float
    high: float
    low: float
    close: float
    volume: int
    change_pct: float = 0.0
    turnover: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "change_pct": self.change_pct,
            "turnover": self.turnover,
        }


@dataclass
class VolatilityMetrics:
    """波动率指标值对象"""

    period_days: int
    historical_volatility: float  # 历史波幅
    intraday_volatility: float  # 日内波幅
    max_in_period: float  # 周期内最高价
    min_in_period: float  # 周期内最低价
    atr: float = 0.0  # 真实波幅均值

    def to_dict(self) -> Dict[str, float]:
        return {
            "period_days": self.period_days,
            "historical_volatility": self.historical_volatility,
            "intraday_volatility": self.intraday_volatility,
            "max_in_period": self.max_in_period,
            "min_in_period": self.min_in_period,
            "atr": self.atr,
        }


@dataclass
class PredictionResult:
    """预测结果值对象"""

    prediction_type: str
    target_symbol: str
    predicted_value: float
    confidence: float
    prediction_horizon: str
    model_used: str
    created_at: datetime
    prediction_basis: Dict[str, Any] = None

    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.8

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_type": self.prediction_type,
            "target_symbol": self.target_symbol,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "prediction_horizon": self.prediction_horizon,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat(),
            "prediction_basis": self.prediction_basis,
        }


@dataclass
class AlertCondition:
    """预警条件值对象"""

    condition_type: str  # price_change, indicator_threshold, volatility
    threshold: float
    direction: str = "above"  # above, below
    enabled: bool = True

    def matches(self, current_value: float) -> bool:
        if self.direction == "above":
            return current_value >= self.threshold
        else:
            return current_value <= self.threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition_type": self.condition_type,
            "threshold": self.threshold,
            "direction": self.direction,
            "enabled": self.enabled,
        }


@dataclass
class WatchlistConfig:
    """自选股配置值对象"""

    auto_refresh: bool = True
    refresh_interval_seconds: int = 60
    alert_enabled: bool = True
    snapshot_retention_days: int = 30
    max_stocks_per_watchlist: int = 500

    def to_dict(self) -> Dict[str, Any]:
        return {
            "auto_refresh": self.auto_refresh,
            "refresh_interval_seconds": self.refresh_interval_seconds,
            "alert_enabled": self.alert_enabled,
            "snapshot_retention_days": self.snapshot_retention_days,
            "max_stocks_per_watchlist": self.max_stocks_per_watchlist,
        }
