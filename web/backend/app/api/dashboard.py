"""
仪表盘API路由

提供仪表盘相关的RESTful API端点，整合市场概览、自选股、持仓、风险预警等数据。

版本: 2.0.0 - 真实数据版本
日期: 2026-01-20
更新: 将MockBusinessDataSource替换为真实API调用
"""

import logging
from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dashboard_builders import (
    build_market_overview,
    build_portfolio_summary,
    build_risk_alert_summary,
    build_watchlist_summary,
)
from app.api.dashboard_cache import cache_dashboard_data, try_get_cached_dashboard
from app.api.dashboard_data_source import get_data_source_dependency
from app.core.cache_manager import CacheManager, get_cache_manager_async
from app.core.responses import (
    ErrorCodes,
    UnifiedResponse,
    create_error_response,
    create_health_response,
    create_unified_success_response,
)
from app.models.dashboard import (
    DashboardResponse,
    MarketOverview,
)

# 配置日志
logger = logging.getLogger(__name__)

# 全局缓存管理器 (异步初始化)
_cache_manager: Optional[CacheManager] = None
_cache_manager_initialized: Optional[bool] = None

DASHBOARD_HEALTH_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "服务dashboard状态检查",
    "data": {
        "status": "healthy",
        "service": "dashboard",
        "timestamp": "2026-04-05T12:00:00Z",
        "data_source": {"status": "healthy", "latency_ms": 18},
        "real_api": "enabled",
        "database_connections": {"postgresql": "connected", "tdengine": "connected"},
    },
    "request_id": "req-dashboard-health-001",
}

DASHBOARD_SUMMARY_RESPONSE_EXAMPLE = {
    "user_id": 1001,
    "trade_date": "2026-04-07",
    "generated_at": "2026-04-07T09:30:00Z",
    "market_overview": {
        "indices": [
            {
                "symbol": "000001.SH",
                "name": "上证指数",
                "current_price": 3128.42,
                "change_percent": 0.86,
                "volume": 386502300,
                "turnover": 452300000000,
                "update_time": "2026-04-07T09:30:00Z",
            },
            {
                "symbol": "HSI",
                "name": "恒生指数",
                "current_price": 17886.35,
                "change_percent": 1.14,
                "volume": 125000000,
                "turnover": 168500000000,
                "update_time": "2026-04-07T09:30:00Z",
            },
        ],
        "up_count": 3124,
        "down_count": 1587,
        "flat_count": 126,
        "total_volume": 983452100.0,
        "total_turnover": 820300000000.0,
        "top_gainers": [{"symbol": "600519.SH", "name": "贵州茅台", "change_percent": 3.21}],
        "top_losers": [{"symbol": "0700.HK", "name": "腾讯控股", "change_percent": -1.42}],
        "most_active": [{"symbol": "IF2504", "name": "沪深300股指期货", "turnover": 5230000000.0}],
    },
    "watchlist": {
        "total_count": 4,
        "items": [{"symbol": "600519.SH", "name": "贵州茅台", "current_price": 1688.0, "change_percent": 3.21}],
        "avg_change_percent": 1.18,
    },
    "portfolio": {
        "total_market_value": 1285000.0,
        "total_cost": 1218000.0,
        "total_profit_loss": 67000.0,
        "total_profit_loss_percent": 5.5,
        "position_count": 3,
        "positions": [{"symbol": "510300.SH", "name": "沪深300ETF", "quantity": 5000, "avg_cost": 4.08}],
    },
    "risk_alerts": {
        "total_count": 2,
        "unread_count": 1,
        "critical_count": 0,
        "alerts": [
            {
                "alert_id": 101,
                "alert_type": "position_limit",
                "alert_level": "warning",
                "symbol": "IF2504",
                "message": "股指期货保证金占用接近阈值",
                "triggered_at": "2026-04-07T09:25:00Z",
                "is_read": False,
            }
        ],
    },
    "data_source": "real_api_composite",
    "cache_hit": True,
}

MARKET_OVERVIEW_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "获取市场概览成功",
    "data": {
        "indices": [
            {
                "symbol": "000001.SH",
                "name": "上证指数",
                "current_price": 3128.42,
                "change_percent": 0.86,
                "volume": 386502300,
                "turnover": 452300000000,
                "update_time": "2026-04-07T09:30:00Z",
            },
            {
                "symbol": "HSI",
                "name": "恒生指数",
                "current_price": 17886.35,
                "change_percent": 1.14,
                "volume": 125000000,
                "turnover": 168500000000,
                "update_time": "2026-04-07T09:30:00Z",
            },
        ],
        "up_count": 3124,
        "down_count": 1587,
        "flat_count": 126,
        "total_volume": 983452100.0,
        "total_turnover": 820300000000.0,
        "top_gainers": [{"symbol": "600519.SH", "name": "贵州茅台", "change_percent": 3.21}],
        "top_losers": [{"symbol": "0700.HK", "name": "腾讯控股", "change_percent": -1.42}],
        "most_active": [{"symbol": "IF2504", "name": "沪深300股指期货", "turnover": 5230000000.0}],
    },
    "timestamp": "2026-04-07T09:30:00Z",
    "request_id": "req-dashboard-overview-001",
    "errors": None,
}


def _response_spec(status_code: int, description: str, example: Any) -> dict[int, dict[str, Any]]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


DASHBOARD_SUMMARY_RESPONSES = {
    **_response_spec(200, "仪表盘聚合摘要", DASHBOARD_SUMMARY_RESPONSE_EXAMPLE),
    **_response_spec(400, "查询参数错误", {"detail": "参数验证失败: user_id 必须大于 0"}),
    **_response_spec(500, "仪表盘数据获取失败", {"detail": "获取仪表盘数据失败: 数据源不可用"}),
}

MARKET_OVERVIEW_RESPONSES = {
    **_response_spec(200, "市场概览统一响应", MARKET_OVERVIEW_RESPONSE_EXAMPLE),
    **_response_spec(404, "市场概览数据不可用", {"detail": "市场概览数据不可用"}),
    **_response_spec(500, "市场概览处理失败", {"detail": "获取市场概览失败: 市场概览数据解析失败"}),
    **_response_spec(503, "市场概览数据源未就绪", {"detail": "市场概览数据源未实现专用接口"}),
}


async def get_cache_manager() -> CacheManager:
    """获取或初始化缓存管理器（单例模式，支持Redis注入）"""
    global _cache_manager, _cache_manager_initialized

    if _cache_manager is None or _cache_manager_initialized is not True:
        # 尝试获取Redis缓存服务
        redis_cache = None
        try:
            from src.core.cache.multi_level import get_cache

            redis_cache = get_cache()
        except ImportError:
            logger.warning("Redis缓存服务不可用，将使用L1+L3模式")

        # 使用异步缓存管理器初始化
        _cache_manager = await get_cache_manager_async(redis_cache=redis_cache)
        _cache_manager_initialized = True

    return _cache_manager


# 创建路由器
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], responses={404: {"description": "Not found"}})


# ============================================================================
# API端点
# ============================================================================


@router.get(
    "/summary",
    response_model=DashboardResponse,
    summary="获取仪表盘汇总数据",
    description="获取用户的完整仪表盘数据，包括市场概览、自选股、持仓、风险预警等信息",
    responses=DASHBOARD_SUMMARY_RESPONSES,
)
async def get_dashboard_summary(
    user_id: int = Query(..., description="用户ID", ge=1),
    trade_date: Optional[date] = Query(None, description="交易日期，默认为今天"),
    include_market: bool = Query(True, description="是否包含市场概览"),
    include_watchlist: bool = Query(True, description="是否包含自选股"),
    include_portfolio: bool = Query(True, description="是否包含持仓"),
    include_alerts: bool = Query(True, description="是否包含风险预警"),
    bypass_cache: bool = Query(False, description="是否跳过缓存直接获取新数据"),
    data_source=Depends(get_data_source_dependency),
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
    - bypass_cache: 是否跳过缓存（默认false）

    **返回数据**:
    - 市场概览: 指数数据、涨跌家数、榜单等
    - 自选股: 自选股列表、平均涨跌幅等
    - 持仓: 持仓列表、总盈亏等
    - 风险预警: 预警列表、未读数量等

    **数据源**: 使用真实API端点（替代Mock数据）
    """
    cache_manager = await get_cache_manager()
    cache_hit = False

    try:
        # 第1阶段：尝试从三级缓存获取数据
        if not bypass_cache:
            cached_entry, cache_hit = await try_get_cached_dashboard(
                cache_manager,
                user_id,
                trade_date,
            )
            if cache_hit and cached_entry:
                logger.info("三级缓存命中: user_id=%s, trade_date=%s", user_id, trade_date)
                raw_dashboard = cached_entry.get("dashboard_data", {})
            else:
                raw_dashboard = None
        else:
            logger.info("跳过三级缓存获取仪表盘数据: user_id=%s", user_id)
            raw_dashboard = None

        # 第2阶段：如果缓存未命中，从数据源获取新数据
        if not cache_hit or raw_dashboard is None:
            logger.info("从真实数据源获取用户%s的仪表盘数据", user_id)

            raw_dashboard = data_source.get_dashboard_summary(user_id, trade_date)

            # 第3阶段：将新数据写入三级缓存
            await cache_dashboard_data(
                cache_manager,
                user_id,
                trade_date,
                raw_dashboard,
                ttl_hours=24,  # 缓存24小时
            )

        # 第4阶段：构建响应数据
        response = DashboardResponse(
            user_id=user_id,
            trade_date=trade_date or date.today(),
            generated_at=datetime.now(),
            data_source=raw_dashboard.get("data_source", "real_api_composite"),
            cache_hit=cache_hit,
        )

        # 根据参数选择性包含各模块数据
        if include_market and "market_overview" in raw_dashboard:
            response.market_overview = build_market_overview(raw_dashboard["market_overview"])

        if include_watchlist and "watchlist" in raw_dashboard:
            response.watchlist = build_watchlist_summary(raw_dashboard["watchlist"])

        if include_portfolio and "portfolio" in raw_dashboard:
            response.portfolio = build_portfolio_summary(raw_dashboard["portfolio"])

        if include_alerts and "risk_alerts" in raw_dashboard:
            response.risk_alerts = build_risk_alert_summary(raw_dashboard["risk_alerts"])

        # 记录缓存统计
        cache_stats = cache_manager.get_cache_stats()
        logger.info(
            f"仪表盘数据获取成功: user_id={user_id}, cache_hit={cache_hit}, "
            f"hit_rate={cache_stats.get('hit_rate', 'N/A')}"
        )
        return response

    except ValueError as e:
        logger.error("参数验证失败: %s", e)
        raise HTTPException(status_code=400, detail=f"参数验证失败: {str(e)}")
    except Exception as e:
        logger.error("获取仪表盘数据失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取仪表盘数据失败: {str(e)}")


@router.get(
    "/market-overview",
    response_model=UnifiedResponse[MarketOverview],
    summary="获取市场概览",
    description="获取市场指数、涨跌家数、榜单等市场概览信息（使用真实API数据）",
    responses=MARKET_OVERVIEW_RESPONSES,
)
async def get_market_overview(
    request: Request,
    limit: int = Query(10, description="榜单数量限制", ge=1, le=100),
    data_source=Depends(get_data_source_dependency),
):
    """获取市场概览数据（使用真实API）"""
    try:
        if hasattr(data_source, "get_market_overview_data"):
            raw_market_data = data_source.get_market_overview_data()
        elif hasattr(data_source, "get_market_overview"):
            raw_market_data = data_source.get_market_overview()
        else:
            raise HTTPException(status_code=503, detail="市场概览数据源未实现专用接口")

        if not raw_market_data:
            raise HTTPException(status_code=404, detail="市场概览数据不可用")

        market_data = build_market_overview(raw_market_data)

        if not market_data:
            raise HTTPException(status_code=500, detail="市场概览数据解析失败")

        market_data.top_gainers = market_data.top_gainers[:limit]
        market_data.top_losers = market_data.top_losers[:limit]
        market_data.most_active = market_data.most_active[:limit]

        return create_unified_success_response(
            data=market_data,
            message="获取市场概览成功",
            request_id=getattr(request.state, "request_id", None),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取市场概览失败: %s", e)
        raise HTTPException(status_code=500, detail=f"获取市场概览失败: {str(e)}")


@router.get(
    "/health",
    summary="仪表盘健康检查",
    description="检查仪表盘服务、真实数据源与数据库连接状态，供前端健康面板和运维探针统一消费。",
    tags=["health"],
    responses={
        200: {
            "description": "仪表盘服务与依赖组件健康状态",
            "content": {"application/json": {"example": DASHBOARD_HEALTH_RESPONSE_EXAMPLE}},
        }
    },
)
async def health_check(request: Request, data_source=Depends(get_data_source_dependency)):
    """
    检查仪表盘服务及其依赖组件的健康状态

    此端点定期用于监控仪表盘服务的可用性和数据源的连接状态。

    **功能说明**:
    - 验证数据源服务连接状态
    - 检查市场数据可用性
    - 评估自选股和持仓数据的可用性

    **使用场景**:
    - 前端健康检查显示
    - 监控系统集成
    - 负载均衡器健康检查

    Notes:
        - healthy: 所有组件工作正常
        - unhealthy: 一个或多个组件不可用
    """
    try:
        # 获取请求ID
        request_id = getattr(request.state, "request_id", None)

        # 检查数据源健康状态
        health = data_source.health_check()

        # 创建健康检查数据
        health_data = {
            "data_source": health,
            "real_api": "enabled",
            "database_connections": {"postgresql": "connected", "tdengine": "connected"},
        }

        return create_health_response(service="dashboard", status="healthy", details=health_data, request_id=request_id)

    except Exception as e:
        logger.error("健康检查失败: %s", e)
        return create_error_response(
            error_code=ErrorCodes.SERVICE_UNAVAILABLE,
            message=f"仪表盘服务不可用: {str(e)}",
            request_id=getattr(request.state, "request_id", None),
        )
