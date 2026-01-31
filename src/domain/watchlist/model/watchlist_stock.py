"""
Watchlist Stock Entity
自选股内股票实体

记录股票在自选股中的状态和快照信息。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.domain.watchlist.value_objects import IndicatorSnapshot, PriceData, VolatilityMetrics


@dataclass
class WatchlistStock:
    """
    自选股内股票实体

    职责：
    - 记录股票的基本信息
    - 管理入选时的快照
    - 管理观察点快照
    - 跟踪价格和指标变化
    """

    id: str
    watchlist_id: str
    stock_code: str
    stock_name: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    added_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    # 快照管理
    entry_snapshot: Optional[IndicatorSnapshot] = None
    observation_snapshots: List[IndicatorSnapshot] = field(default_factory=list)
    latest_snapshot: Optional[IndicatorSnapshot] = None

    # 监控状态
    is_active: bool = True
    alert_triggered: bool = False

    @classmethod
    def create(
        cls, watchlist_id: str, stock_code: str, stock_name: str = "", notes: str = "", tags: List[str] = None
    ) -> "WatchlistStock":
        """工厂方法：创建新的自选股股票"""
        return cls(
            id=str(uuid4()),
            watchlist_id=watchlist_id,
            stock_code=stock_code,
            stock_name=stock_name,
            notes=notes,
            tags=tags or [],
        )

    def capture_entry_snapshot(self, snapshot: IndicatorSnapshot) -> None:
        """捕获入选时的快照"""
        self.entry_snapshot = snapshot
        self.latest_snapshot = snapshot
        self.last_updated = datetime.now()

    def capture_observation_snapshot(self, snapshot: IndicatorSnapshot) -> None:
        """捕获观察点快照"""
        self.observation_snapshots.append(snapshot)
        self.latest_snapshot = snapshot
        self.last_updated = datetime.now()

    def capture_timed_snapshot(self, snapshot: IndicatorSnapshot) -> None:
        """捕获定时快照"""
        self.observation_snapshots.append(snapshot)
        self.latest_snapshot = snapshot
        self.last_updated = datetime.now()

    def get_snapshots_by_period(self, start_time: datetime, end_time: datetime = None) -> List[IndicatorSnapshot]:
        """获取指定时间范围内的快照"""
        end = end_time or datetime.now()
        snapshots = []
        for snap in self.observation_snapshots:
            if start_time <= snap.captured_at <= end:
                snapshots.append(snap)
        return snapshots

    def get_latest_price_change(self) -> float:
        """获取最新价格变化"""
        if not self.latest_snapshot or not self.entry_snapshot:
            return 0.0
        entry_close = self.entry_snapshot.price_data.get("close", 0)
        latest_close = self.latest_snapshot.price_data.get("close", 0)
        if entry_close == 0:
            return 0.0
        return ((latest_close - entry_close) / entry_close) * 100

    def get_volatility_metrics(self, period_days: int = 10) -> Optional[VolatilityMetrics]:
        """计算波动率指标"""
        snapshots = self.get_snapshots_by_period(
            datetime.now().replace(hour=0, minute=0, second=0) - datetime.timedelta(days=period_days)
        )
        if not snapshots or len(snapshots) < 2:
            return None

        prices = [s.price_data.get("close", 0) for s in snapshots]
        if len(prices) < 2:
            return None

        import math

        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices)) if prices[i - 1] != 0]
        if not returns:
            return None

        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        historical_volatility = math.sqrt(variance * 252) * 100

        intraday_volts = []
        for s in snapshots:
            high = s.price_data.get("high", 0)
            low = s.price_data.get("low", 0)
            close = s.price_data.get("close", 0)
            if close != 0:
                intraday = ((high - low) / close) * 100
                intraday_volts.append(intraday)

        return VolatilityMetrics(
            period_days=period_days,
            historical_volatility=historical_volatility,
            intraday_volatility=sum(intraday_volts) / len(intraday_volts) if intraday_volts else 0,
            max_in_period=max(prices) if prices else 0,
            min_in_period=min(prices) if prices else 0,
            atr=0.0,
        )

    def update_price_data(self, price_data: PriceData) -> None:
        """更新价格数据"""
        if self.latest_snapshot:
            self.latest_snapshot.price_data = price_data.to_dict()
        self.last_updated = datetime.now()

    def deactivate(self) -> None:
        """停用监控"""
        self.is_active = False
        self.last_updated = datetime.now()

    def activate(self) -> None:
        """启用监控"""
        self.is_active = True
        self.last_updated = datetime.now()

    def get_indicator_history(self, indicator_id: str) -> List[Dict[str, Any]]:
        """获取指定指标的历史记录"""
        history = []
        all_snapshots = [self.entry_snapshot] + self.observation_snapshots
        for snap in all_snapshots:
            if snap and indicator_id in snap.indicators:
                ind = snap.indicators[indicator_id]
                history.append(
                    {"timestamp": snap.captured_at.isoformat(), "indicator_id": ind.indicator_id, "value": ind.value}
                )
        return history

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "watchlist_id": self.watchlist_id,
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "notes": self.notes,
            "tags": self.tags,
            "added_at": self.added_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "is_active": self.is_active,
            "price_change_pct": self.get_latest_price_change(),
            "snapshot_count": len(self.observation_snapshots),
        }
