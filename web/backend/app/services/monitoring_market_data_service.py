"""Monitoring market-data use-case service."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional, Protocol

from app.models.monitoring import DragonTigerListResponse, RealtimeMonitoringResponse


class MonitoringMarketDataSource(Protocol):
    def get_session(self) -> Any:
        """Return a database session for monitoring data queries."""

    def fetch_realtime_data(self, symbols: list[str]) -> Any:
        """Fetch realtime monitoring data for symbols."""

    def save_realtime_data(self, df: Any) -> int:
        """Persist fetched realtime monitoring data."""

    def evaluate_alert_rules(self, df: Any) -> list[Any]:
        """Evaluate alert rules for fetched realtime monitoring data."""

    def fetch_dragon_tiger_list(self, trade_date: date) -> Any:
        """Fetch dragon-tiger list data for a trade date."""

    def save_dragon_tiger_data(self, df: Any, trade_date: date) -> int:
        """Persist fetched dragon-tiger list data."""


class MonitoringMarketDataService:
    """Coordinate realtime and dragon-tiger monitoring market data operations."""

    def __init__(self, monitoring_service: MonitoringMarketDataSource) -> None:
        self._monitoring_service = monitoring_service

    def get_realtime_monitoring(self, symbol: str) -> Optional[RealtimeMonitoringResponse]:
        session = self._monitoring_service.get_session()
        try:
            from app.models.monitoring import RealtimeMonitoring

            record = (
                session.query(RealtimeMonitoring)
                .filter(RealtimeMonitoring.symbol == symbol)
                .order_by(RealtimeMonitoring.timestamp.desc())
                .first()
            )
            if not record:
                return None

            return RealtimeMonitoringResponse.model_validate(record, from_attributes=True)
        finally:
            session.close()

    def list_realtime_monitoring(
        self,
        *,
        symbols: Optional[str],
        limit: int,
        is_limit_up: Optional[bool],
        is_limit_down: Optional[bool],
    ) -> list[RealtimeMonitoringResponse]:
        session = self._monitoring_service.get_session()
        try:
            from app.models.monitoring import RealtimeMonitoring

            query = session.query(RealtimeMonitoring).filter(RealtimeMonitoring.trade_date == date.today())

            if symbols:
                symbol_list = [s.strip() for s in symbols.split(",")]
                query = query.filter(RealtimeMonitoring.symbol.in_(symbol_list))

            if is_limit_up is not None:
                query = query.filter(RealtimeMonitoring.is_limit_up == is_limit_up)
            if is_limit_down is not None:
                query = query.filter(RealtimeMonitoring.is_limit_down == is_limit_down)

            records = query.order_by(RealtimeMonitoring.timestamp.desc()).limit(limit).all()
            return [RealtimeMonitoringResponse.model_validate(record, from_attributes=True) for record in records]
        finally:
            session.close()

    def fetch_realtime_data(self, symbols: list[str]) -> Optional[dict[str, int]]:
        df = self._monitoring_service.fetch_realtime_data(symbols)
        if df.empty:
            return None

        count = self._monitoring_service.save_realtime_data(df)
        alerts = self._monitoring_service.evaluate_alert_rules(df)
        return {
            "stocks_count": len(df),
            "saved_count": count,
            "alerts_triggered": len(alerts),
        }

    def list_dragon_tiger(
        self,
        *,
        trade_date: Optional[date],
        symbol: Optional[str],
        min_net_amount: Optional[float],
        limit: int,
    ) -> list[DragonTigerListResponse]:
        session = self._monitoring_service.get_session()
        try:
            from app.models.monitoring import DragonTigerList

            query_trade_date = trade_date or date.today()
            query = session.query(DragonTigerList).filter(DragonTigerList.trade_date == query_trade_date)

            if symbol:
                query = query.filter(DragonTigerList.symbol == symbol)
            if min_net_amount is not None:
                query = query.filter(DragonTigerList.net_amount >= min_net_amount)

            records = query.order_by(DragonTigerList.net_amount.desc()).limit(limit).all()
            return [DragonTigerListResponse.model_validate(record, from_attributes=True) for record in records]
        finally:
            session.close()

    def fetch_dragon_tiger_data(self, trade_date: date) -> Optional[dict[str, str | int]]:
        df = self._monitoring_service.fetch_dragon_tiger_list(trade_date)
        if df.empty:
            return None

        count = self._monitoring_service.save_dragon_tiger_data(df, trade_date)
        return {"trade_date": trade_date.isoformat(), "count": count}
