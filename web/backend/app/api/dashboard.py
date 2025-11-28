"""
仪表盘API路由

提供仪表盘相关的RESTful API端点，整合市场概览、自选股、持仓、风险预警等数据。

版本: 1.0.0
日期: 2025-11-21
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import date, datetime
import logging

from app.models.dashboard import (
    DashboardRequest,
    DashboardResponse,
    MarketOverview,
    MarketIndexItem,
    WatchlistSummary,
    WatchlistItem,
    PortfolioSummary,
    PositionItem,
    RiskAlertSummary,
    RiskAlert,
    ErrorResponse
)
# from src.data_sources import get_business_source  # Module not found - disabled

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}}
)


# ============================================================================
# 辅助函数
# ============================================================================

def get_data_source():
    """获取业务数据源"""
    try:
        return get_business_source()
    except Exception as e:
        logger.error(f"获取数据源失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"数据源初始化失败: {str(e)}"
        )


def build_market_overview(raw_data: dict) -> Optional[MarketOverview]:
    """构建市场概览数据"""
    if not raw_data or 'indices' not in raw_data:
        return None

    try:
        # 转换指数数据
        indices = []
        for idx in raw_data.get('indices', []):
            indices.append(MarketIndexItem(
                symbol=idx.get('symbol', ''),
                name=idx.get('name', ''),
                current_price=float(idx.get('current_price', 0)),
                change_percent=float(idx.get('change_percent', 0)),
                volume=idx.get('volume'),
                turnover=idx.get('turnover'),
                update_time=idx.get('update_time')
            ))

        return MarketOverview(
            indices=indices,
            up_count=raw_data.get('up_count', 0),
            down_count=raw_data.get('down_count', 0),
            flat_count=raw_data.get('flat_count', 0),
            total_volume=raw_data.get('total_volume'),
            total_turnover=raw_data.get('total_turnover'),
            top_gainers=raw_data.get('top_gainers', []),
            top_losers=raw_data.get('top_losers', []),
            most_active=raw_data.get('most_active', [])
        )
    except Exception as e:
        logger.error(f"构建市场概览失败: {str(e)}")
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
                symbol=item.get('symbol', ''),
                name=item.get('name'),
                current_price=item.get('current_price'),
                change_percent=item.get('change_percent'),
                note=item.get('note'),
                added_at=item.get('added_at')
            )
            items.append(watchlist_item)

            if item.get('change_percent') is not None:
                total_change += float(item['change_percent'])
                count_with_price += 1

        avg_change = total_change / count_with_price if count_with_price > 0 else None

        return WatchlistSummary(
            total_count=len(items),
            items=items,
            avg_change_percent=avg_change
        )
    except Exception as e:
        logger.error(f"构建自选股汇总失败: {str(e)}")
        return None


def build_portfolio_summary(raw_data: dict) -> Optional[PortfolioSummary]:
    """构建持仓汇总数据"""
    if not raw_data:
        return PortfolioSummary()

    try:
        positions = []
        for pos in raw_data.get('positions', []):
            positions.append(PositionItem(
                symbol=pos.get('symbol', ''),
                name=pos.get('name'),
                quantity=float(pos.get('quantity', 0)),
                avg_cost=float(pos.get('avg_cost', 0)),
                current_price=pos.get('current_price'),
                market_value=pos.get('market_value'),
                profit_loss=pos.get('profit_loss'),
                profit_loss_percent=pos.get('profit_loss_percent'),
                position_percent=pos.get('position_percent')
            ))

        return PortfolioSummary(
            total_market_value=float(raw_data.get('total_market_value', 0)),
            total_cost=float(raw_data.get('total_cost', 0)),
            total_profit_loss=float(raw_data.get('total_profit_loss', 0)),
            total_profit_loss_percent=float(raw_data.get('total_profit_loss_percent', 0)),
            position_count=int(raw_data.get('position_count', 0)),
            positions=positions
        )
    except Exception as e:
        logger.error(f"构建持仓汇总失败: {str(e)}")
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
                alert_id=int(alert.get('alert_id', 0)),
                alert_type=alert.get('alert_type', ''),
                alert_level=alert.get('alert_level', 'info'),
                symbol=alert.get('symbol'),
                message=alert.get('message', ''),
                triggered_at=alert.get('triggered_at', datetime.now()),
                is_read=bool(alert.get('is_read', False))
            )
            alerts.append(risk_alert)

            if not risk_alert.is_read:
                unread_count += 1
            if risk_alert.alert_level == 'critical':
                critical_count += 1

        return RiskAlertSummary(
            total_count=len(alerts),
            unread_count=unread_count,
            critical_count=critical_count,
            alerts=alerts
        )
    except Exception as e:
        logger.error(f"构建风险预警汇总失败: {str(e)}")
        return None


# ============================================================================
# API端点
# ============================================================================

@router.get(
    "/summary",
    response_model=DashboardResponse,
    summary="获取仪表盘汇总数据",
    description="获取用户的完整仪表盘数据，包括市场概览、自选股、持仓、风险预警等信息"
)
async def get_dashboard_summary(
    user_id: int = Query(..., description="用户ID", ge=1),
    trade_date: Optional[date] = Query(None, description="交易日期，默认为今天"),
    include_market: bool = Query(True, description="是否包含市场概览"),
    include_watchlist: bool = Query(True, description="是否包含自选股"),
    include_portfolio: bool = Query(True, description="是否包含持仓"),
    include_alerts: bool = Query(True, description="是否包含风险预警"),
    data_source = Depends(get_data_source)
):
    """
    获取仪表盘汇总数据

    **参数说明**:
    - user_id: 用户ID（必须）
    - trade_date: 交易日期（可选，默认今天）
    - include_market: 是否包含市场概览（默认true）
    - include_watchlist: 是否包含自选股（默认true）
    - include_portfolio: 是否包含持仓（默认true）
    - include_alerts: 是否包含风险预警（默认true）

    **返回数据**:
    - 市场概览: 指数数据、涨跌家数、榜单等
    - 自选股: 自选股列表、平均涨跌幅等
    - 持仓: 持仓列表、总盈亏等
    - 风险预警: 预警列表、未读数量等
    """
    try:
        # 调用业务数据源获取仪表盘数据
        logger.info(f"获取用户{user_id}的仪表盘数据")

        # 兼容Mock和Real数据源（Mock不支持trade_date参数）
        try:
            raw_dashboard = data_source.get_dashboard_summary(
                user_id=user_id,
                trade_date=trade_date
            )
        except TypeError:
            # Mock数据源不支持trade_date参数，降级为只传user_id
            raw_dashboard = data_source.get_dashboard_summary(user_id=user_id)

        # 构建响应数据
        response = DashboardResponse(
            user_id=user_id,
            trade_date=trade_date or date.today(),
            generated_at=datetime.now(),
            data_source=raw_dashboard.get('data_source', 'composite'),
            cache_hit=False  # TODO: 实现缓存机制后更新
        )

        # 根据参数选择性包含各模块数据
        if include_market and 'market_overview' in raw_dashboard:
            response.market_overview = build_market_overview(
                raw_dashboard['market_overview']
            )

        if include_watchlist and 'watchlist' in raw_dashboard:
            response.watchlist = build_watchlist_summary(
                raw_dashboard['watchlist']
            )

        if include_portfolio and 'portfolio' in raw_dashboard:
            response.portfolio = build_portfolio_summary(
                raw_dashboard['portfolio']
            )

        if include_alerts and 'risk_alerts' in raw_dashboard:
            response.risk_alerts = build_risk_alert_summary(
                raw_dashboard['risk_alerts']
            )

        logger.info(f"仪表盘数据获取成功: user_id={user_id}")
        return response

    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"参数验证失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取仪表盘数据失败: {str(e)}"
        )


@router.get(
    "/market-overview",
    response_model=MarketOverview,
    summary="获取市场概览",
    description="获取市场指数、涨跌家数、榜单等市场概览信息"
)
async def get_market_overview(
    limit: int = Query(10, description="榜单数量限制", ge=1, le=100),
    data_source = Depends(get_data_source)
):
    """获取市场概览数据"""
    try:
        # 调用业务数据源
        raw_data = data_source.get_dashboard_summary(user_id=0)  # 市场数据不需要user_id

        if 'market_overview' not in raw_data:
            raise HTTPException(
                status_code=404,
                detail="市场概览数据不可用"
            )

        market_data = build_market_overview(raw_data['market_overview'])

        if not market_data:
            raise HTTPException(
                status_code=500,
                detail="市场概览数据解析失败"
            )

        return market_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取市场概览失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取市场概览失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查仪表盘服务和数据源的健康状态"
)
async def health_check(data_source = Depends(get_data_source)):
    """健康检查端点"""
    try:
        health = data_source.health_check()
        return {
            "status": "healthy",
            "service": "dashboard",
            "data_source": health,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "dashboard",
            "error": str(e),
            "timestamp": datetime.now()
        }
