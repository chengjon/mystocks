"""
仪表盘聚合结果构建辅助函数
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from app.models.dashboard import (
    MarketIndexItem,
    MarketOverview,
    PortfolioSummary,
    PositionItem,
    RiskAlert,
    RiskAlertSummary,
    WatchlistItem,
    WatchlistSummary,
)

logger = logging.getLogger(__name__)


def build_market_overview(raw_data: dict) -> Optional[MarketOverview]:
    """构建市场概览数据"""
    if not raw_data or "indices" not in raw_data:
        return None

    try:
        indices = []
        for idx in raw_data.get("indices", []):
            indices.append(
                MarketIndexItem(
                    symbol=idx.get("symbol", ""),
                    name=idx.get("name", ""),
                    current_price=float(idx.get("current_price", 0)),
                    change_percent=float(idx.get("change_percent", 0)),
                    volume=idx.get("volume"),
                    turnover=idx.get("turnover"),
                    update_time=idx.get("update_time"),
                )
            )

        return MarketOverview(
            indices=indices,
            up_count=raw_data.get("up_count", 0),
            down_count=raw_data.get("down_count", 0),
            flat_count=raw_data.get("flat_count", 0),
            total_volume=raw_data.get("total_volume"),
            total_turnover=raw_data.get("total_turnover"),
            top_gainers=raw_data.get("top_gainers", []),
            top_losers=raw_data.get("top_losers", []),
            most_active=raw_data.get("most_active", []),
        )
    except Exception as error:
        logger.error("构建市场概览失败: %s", error)
        return None


def build_watchlist_summary(raw_data: list) -> Optional[WatchlistSummary]:
    """构建自选股汇总数据"""
    if not raw_data:
        return WatchlistSummary(total_count=0, items=[], avg_change_percent=None)

    try:
        items = []
        total_change = 0.0
        count_with_price = 0

        for item in raw_data:
            watchlist_item = WatchlistItem(
                symbol=item.get("symbol", ""),
                name=item.get("name"),
                current_price=item.get("current_price"),
                change_percent=item.get("change_percent"),
                note=item.get("note"),
                added_at=item.get("added_at"),
            )
            items.append(watchlist_item)

            if item.get("change_percent") is not None:
                total_change += float(item["change_percent"])
                count_with_price += 1

        avg_change = total_change / count_with_price if count_with_price > 0 else None
        return WatchlistSummary(total_count=len(items), items=items, avg_change_percent=avg_change)
    except Exception as error:
        logger.error("构建自选股汇总失败: %s", error)
        return None


def build_portfolio_summary(raw_data: dict) -> Optional[PortfolioSummary]:
    """构建持仓汇总数据"""
    if not raw_data:
        return PortfolioSummary()

    try:
        positions = []
        for pos in raw_data.get("positions", []):
            positions.append(
                PositionItem(
                    symbol=pos.get("symbol", ""),
                    name=pos.get("name"),
                    quantity=float(pos.get("quantity", 0)),
                    avg_cost=float(pos.get("avg_cost", 0)),
                    current_price=pos.get("current_price"),
                    market_value=pos.get("market_value"),
                    profit_loss=pos.get("profit_loss"),
                    profit_loss_percent=pos.get("profit_loss_percent"),
                    position_percent=pos.get("position_percent"),
                )
            )

        return PortfolioSummary(
            total_market_value=float(raw_data.get("total_market_value", 0)),
            total_cost=float(raw_data.get("total_cost", 0)),
            total_profit_loss=float(raw_data.get("total_profit_loss", 0)),
            total_profit_loss_percent=float(raw_data.get("total_profit_loss_percent", 0)),
            position_count=int(raw_data.get("position_count", 0)),
            positions=positions,
        )
    except Exception as error:
        logger.error("构建持仓汇总失败: %s", error)
        return None


def build_risk_alert_summary(raw_data: list) -> Optional[RiskAlertSummary]:
    """构建风险预警汇总数据"""
    if not raw_data:
        return RiskAlertSummary()

    try:
        alerts = []
        unread_count = 0
        critical_count = 0

        for alert in raw_data:
            risk_alert = RiskAlert(
                alert_id=int(alert.get("alert_id", 0)),
                alert_type=alert.get("alert_type", ""),
                alert_level=alert.get("alert_level", "info"),
                symbol=alert.get("symbol"),
                message=alert.get("message", ""),
                triggered_at=alert.get("triggered_at", datetime.now()),
                is_read=bool(alert.get("is_read", False)),
            )
            alerts.append(risk_alert)

            if not risk_alert.is_read:
                unread_count += 1
            if risk_alert.alert_level == "critical":
                critical_count += 1

        return RiskAlertSummary(
            total_count=len(alerts),
            unread_count=unread_count,
            critical_count=critical_count,
            alerts=alerts,
        )
    except Exception as error:
        logger.error("构建风险预警汇总失败: %s", error)
        return None
