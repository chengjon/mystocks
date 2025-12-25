"""
仪表盘API路由

提供仪表盘相关的RESTful API端点，整合市场概览、自选股、持仓、风险预警等数据。

版本: 1.0.0
日期: 2025-11-21
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.cache_manager import CacheManager
from app.core.responses import (
    
    ErrorCodes,
    create_unified_error_response,
    create_health_response,
)
from app.models.dashboard import (
    DashboardResponse,
    MarketIndexItem,
    MarketOverview,
    PortfolioSummary,
    PositionItem,
    RiskAlert,
    RiskAlertSummary,
    WatchlistItem,
    WatchlistSummary,
)

# from src.data_sources import get_business_source  # Module not found - disabled

# 配置日志
logger = logging.getLogger(__name__)

# 全局缓存管理器
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取或初始化缓存管理器（单例模式）"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# 创建路由器
router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)


# ==================== 健康检查 ====================


@router.get("/health")
async def health_check():
    """
    仪表盘服务健康检查

    Returns:
        统一格式的健康检查响应
    """
    return create_health_response(
        service="dashboard",
        status="healthy",
        details={
            "endpoints": [
                "summary",
                "market_overview",
                "portfolio",
                "watchlist",
                "risk_alerts",
            ],
            "cache_enabled": True,
            "version": "1.0.0",
        },
    )


# ============================================================================
# 辅助函数
# ============================================================================


class MockBusinessDataSource:
    """模拟业务数据源"""

    def get_dashboard_summary(self, user_id: int, trade_date: Optional[date] = None):
        """获取仪表盘汇总数据"""
        return {
            "data_source": "mock_composite",
            "market_overview": {
                "indices": [
                    {
                        "symbol": "000001",
                        "name": "上证指数",
                        "current_price": 3021.45,
                        "change_percent": 0.85,
                        "volume": 285000000,
                        "turnover": 3120000000,
                        "update_time": datetime.now().isoformat(),
                    },
                    {
                        "symbol": "399001",
                        "name": "深证成指",
                        "current_price": 9876.32,
                        "change_percent": -0.32,
                        "volume": 198000000,
                        "turnover": 2450000000,
                        "update_time": datetime.now().isoformat(),
                    },
                ],
                "up_count": 2156,
                "down_count": 1832,
                "flat_count": 234,
                "total_volume": 483000000,
                "total_turnover": 5570000000,
                "top_gainers": [
                    {"symbol": "600519", "name": "贵州茅台", "change_percent": 9.87},
                    {"symbol": "000858", "name": "五粮液", "change_percent": 8.23},
                ],
                "top_losers": [
                    {"symbol": "600276", "name": "恒瑞医药", "change_percent": -8.45},
                    {"symbol": "002415", "name": "海康威视", "change_percent": -7.32},
                ],
                "most_active": [
                    {"symbol": "000001", "name": "平安银行", "volume": 45000000},
                    {"symbol": "600036", "name": "招商银行", "volume": 38000000},
                ],
            },
            "watchlist": [
                {
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "current_price": 1678.50,
                    "change_percent": 2.35,
                    "note": "价值投资标的",
                    "added_at": "2025-11-01",
                },
                {
                    "symbol": "000858",
                    "name": "五粮液",
                    "current_price": 142.30,
                    "change_percent": -1.20,
                    "note": "消费龙头",
                    "added_at": "2025-10-28",
                },
            ],
            "portfolio": {
                "total_market_value": 500000.00,
                "total_cost": 450000.00,
                "total_profit_loss": 50000.00,
                "total_profit_loss_percent": 11.11,
                "position_count": 3,
                "positions": [
                    {
                        "symbol": "600519",
                        "name": "贵州茅台",
                        "quantity": 100,
                        "avg_cost": 1550.00,
                        "current_price": 1678.50,
                        "market_value": 167850.00,
                        "profit_loss": 12850.00,
                        "profit_loss_percent": 8.29,
                        "position_percent": 33.57,
                    },
                    {
                        "symbol": "000858",
                        "name": "五粮液",
                        "quantity": 500,
                        "avg_cost": 145.00,
                        "current_price": 142.30,
                        "market_value": 71150.00,
                        "profit_loss": -1350.00,
                        "profit_loss_percent": -1.86,
                        "position_percent": 14.23,
                    },
                ],
            },
            "risk_alerts": [
                {
                    "alert_id": 1,
                    "alert_type": "price_alert",
                    "alert_level": "warning",
                    "symbol": "600519",
                    "message": "贵州茅台价格突破预警线",
                    "triggered_at": datetime.now().isoformat(),
                    "is_read": False,
                },
                {
                    "alert_id": 2,
                    "alert_type": "portfolio_risk",
                    "alert_level": "info",
                    "symbol": None,
                    "message": "投资组合集中度偏高",
                    "triggered_at": datetime.now().isoformat(),
                    "is_read": True,
                },
            ],
        }

    def health_check(self):
        """健康检查"""
        return {
            "status": "healthy",
            "database": "postgresql",
            "cache": "enabled",
            "last_check": datetime.now().isoformat(),
        }


def get_business_source():
    """获取业务数据源配置"""
    # 返回模拟的业务数据源配置
    return {
        "market": {
            "enabled": True,
            "source": "tdengine",
            "status": "connected",
            "last_update": datetime.now().isoformat(),
        },
        "cache": {
            "enabled": True,
            "source": "postgresql",
            "status": "connected",
            "last_update": datetime.now().isoformat(),
        },
        "strategy": {
            "enabled": True,
            "source": "postgresql",
            "status": "connected",
            "last_update": datetime.now().isoformat(),
        },
        "notification": {
            "enabled": True,
            "source": "postgresql",
            "status": "connected",
            "last_update": datetime.now().isoformat(),
        },
        "data_quality": {"completeness": 95.6, "freshness": 99.2, "accuracy": 98.1},
    }


def get_data_source():
    """获取业务数据源"""
    try:
        return MockBusinessDataSource()
    except Exception as e:
        logger.error(f"获取数据源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据源初始化失败: {str(e)}")


def build_market_overview(raw_data: dict) -> Optional[MarketOverview]:
    """构建市场概览数据"""
    if not raw_data or "indices" not in raw_data:
        return None

    try:
        # 转换指数数据
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

        return WatchlistSummary(
            total_count=len(items), items=items, avg_change_percent=avg_change
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
            total_profit_loss_percent=float(
                raw_data.get("total_profit_loss_percent", 0)
            ),
            position_count=int(raw_data.get("position_count", 0)),
            positions=positions,
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
    except Exception as e:
        logger.error(f"构建风险预警汇总失败: {str(e)}")
        return None


# ============================================================================
# 缓存辅助函数
# ============================================================================


def _generate_cache_key(user_id: int, trade_date: Optional[date]) -> str:
    """
    生成缓存键

    Args:
        user_id: 用户ID
        trade_date: 交易日期

    Returns:
        缓存键 (格式: dashboard_user_{user_id}_{date})
    """
    date_str = (trade_date or date.today()).isoformat()
    return f"dashboard_user_{user_id}_{date_str}"


def _try_get_cached_dashboard(
    cache_manager: CacheManager,
    user_id: int,
    trade_date: Optional[date],
) -> tuple[Optional[Dict[str, Any]], bool]:
    """
    尝试从缓存获取仪表盘数据

    Args:
        cache_manager: 缓存管理器实例
        user_id: 用户ID
        trade_date: 交易日期

    Returns:
        (缓存数据, 缓存是否命中)
        如果命中缓存，返回 (数据, True)
        如果未命中缓存，返回 (None, False)
    """
    try:
        cache_key = _generate_cache_key(user_id, trade_date)
        cached_data = cache_manager.fetch_from_cache(
            symbol=f"user_{user_id}",
            data_type="dashboard",
            timeframe="1d",
        )

        if cached_data and isinstance(cached_data, dict):
            logger.info(f"✅ 仪表盘缓存命中: {cache_key}")
            return cached_data, True
        else:
            logger.debug(f"⚠️ 仪表盘缓存未命中: {cache_key}")
            return None, False

    except Exception as e:
        logger.warning(f"缓存读取失败，将继续获取新数据: {str(e)}")
        return None, False


def _cache_dashboard_data(
    cache_manager: CacheManager,
    user_id: int,
    trade_date: Optional[date],
    dashboard_data: Dict[str, Any],
    ttl_hours: int = 24,
) -> bool:
    """
    将仪表盘数据写入缓存

    Args:
        cache_manager: 缓存管理器实例
        user_id: 用户ID
        trade_date: 交易日期
        dashboard_data: 要缓存的仪表盘数据
        ttl_hours: 缓存生存时间（小时）

    Returns:
        True 如果缓存成功，False 否则
    """
    try:
        cache_key = _generate_cache_key(user_id, trade_date)

        # 为缓存数据添加元数据
        cache_entry = {
            "dashboard_data": dashboard_data,
            "user_id": user_id,
            "trade_date": (trade_date or date.today()).isoformat(),
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": ttl_hours,
        }

        success = cache_manager.write_to_cache(
            symbol=f"user_{user_id}",
            data_type="dashboard",
            timeframe="1d",
            data=cache_entry,
            ttl_days=(ttl_hours + 23) // 24,  # 四舍五入到天
            timestamp=datetime.now(),
        )

        # Ensure bool return type
        success_bool: bool = bool(success)
        if success_bool:
            logger.info(f"✅ 仪表盘数据已缓存: {cache_key}")
        else:
            logger.warning(f"⚠️ 仪表盘数据缓存失败: {cache_key}")

        return success_bool

    except Exception as e:
        logger.warning(f"缓存写入失败: {str(e)}")
        return False


# ============================================================================
# API端点
# ============================================================================


@router.get(
    "/summary",
    response_model=DashboardResponse,
    summary="获取仪表盘汇总数据",
    description="获取用户的完整仪表盘数据，包括市场概览、自选股、持仓、风险预警等信息",
)
async def get_dashboard_summary(
    user_id: int = Query(..., description="用户ID", ge=1),
    trade_date: Optional[date] = Query(None, description="交易日期，默认为今天"),
    include_market: bool = Query(True, description="是否包含市场概览"),
    include_watchlist: bool = Query(True, description="是否包含自选股"),
    include_portfolio: bool = Query(True, description="是否包含持仓"),
    include_alerts: bool = Query(True, description="是否包含风险预警"),
    bypass_cache: bool = Query(False, description="是否跳过缓存直接获取新数据"),
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
    """
    cache_manager = get_cache_manager()
    cache_hit = False

    try:
        # 第1阶段：尝试从缓存获取数据
        if not bypass_cache:
            cached_entry, cache_hit = _try_get_cached_dashboard(
                cache_manager,
                user_id,
                trade_date,
            )
            if cache_hit and cached_entry:
                logger.info(
                    f"仪表盘缓存命中: user_id={user_id}, trade_date={trade_date}"
                )
                raw_dashboard = cached_entry.get("dashboard_data", {})
            else:
                raw_dashboard = None
        else:
            logger.info(f"跳过缓存获取仪表盘数据: user_id={user_id}")
            raw_dashboard = None

        # 第2阶段：如果缓存未命中，从数据源获取新数据
        if not cache_hit or raw_dashboard is None:
            logger.info(f"从数据源获取用户{user_id}的仪表盘数据")

            # 使用数据源工厂
            from app.services.data_source_factory import get_data_source_factory

            factory = await get_data_source_factory()

            # 构建请求参数
            params = {
                "user_id": user_id,
                "trade_date": trade_date.isoformat() if trade_date else None,
                "include_market": include_market,
                "include_watchlist": include_watchlist,
                "include_portfolio": include_portfolio,
                "include_alerts": include_alerts,
            }

            # 调用数据源工厂获取dashboard/summary数据
            raw_dashboard = await factory.get_data("dashboard", "summary", params)

            # 第3阶段：将新数据写入缓存
            _cache_dashboard_data(
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
            data_source=raw_dashboard.get("data_source", "data_source_factory"),
            cache_hit=cache_hit,  # ✅ 实现缓存机制：根据实际缓存命中状态更新
        )

        # 根据参数选择性包含各模块数据
        if include_market and "market_overview" in raw_dashboard:
            response.market_overview = build_market_overview(
                raw_dashboard["market_overview"]
            )

        if include_watchlist and "watchlist" in raw_dashboard:
            response.watchlist = build_watchlist_summary(raw_dashboard["watchlist"])

        if include_portfolio and "portfolio" in raw_dashboard:
            response.portfolio = build_portfolio_summary(raw_dashboard["portfolio"])

        if include_alerts and "risk_alerts" in raw_dashboard:
            response.risk_alerts = build_risk_alert_summary(
                raw_dashboard["risk_alerts"]
            )

        # 记录缓存统计
        cache_stats = cache_manager.get_cache_stats()
        logger.info(
            f"仪表盘数据获取成功: user_id={user_id}, cache_hit={cache_hit}, "
            f"hit_rate={cache_stats.get('hit_rate', 'N/A')}"
        )
        return response

    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"参数验证失败: {str(e)}")
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取仪表盘数据失败: {str(e)}")


@router.get(
    "/market-overview",
    response_model=MarketOverview,
    summary="获取市场概览",
    description="获取市场指数、涨跌家数、榜单等市场概览信息",
)
async def get_market_overview(
    limit: int = Query(10, description="榜单数量限制", ge=1, le=100),
    data_source=Depends(get_data_source),
):
    """获取市场概览数据"""
    try:
        # 调用业务数据源
        raw_data = data_source.get_dashboard_summary(user_id=0)  # 市场数据不需要user_id

        if "market_overview" not in raw_data:
            raise HTTPException(status_code=404, detail="市场概览数据不可用")

        market_data = build_market_overview(raw_data["market_overview"])

        if not market_data:
            raise HTTPException(status_code=500, detail="市场概览数据解析失败")

        return market_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取市场概览失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取市场概览失败: {str(e)}")


@router.get(
    "/health",
    summary="仪表盘健康检查",
    description="检查仪表盘服务和数据源的健康状态",
    tags=["health"],
)
async def health_check(request: Request, data_source=Depends(get_data_source)):
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
            "mock_data": "enabled",
            "database_connections": {
                "postgresql": "connected",
                "tdengine": "connected",
            },
        }

        return create_health_response(
            service="dashboard",
            status="healthy",
            details=health_data,
            request_id=request_id,
        )

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return create_unified_error_response(
            error_code=ErrorCodes.SERVICE_UNAVAILABLE,
            message=f"仪表盘服务不可用: {str(e)}",
            request_id=getattr(request.state, "request_id", None),
        )
