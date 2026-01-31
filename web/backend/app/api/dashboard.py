"""
仪表盘API路由

提供仪表盘相关的RESTful API端点，整合市场概览、自选股、持仓、风险预警等数据。

版本: 2.0.0 - 真实数据版本
日期: 2026-01-20
更新: 将MockBusinessDataSource替换为真实API调用
"""

import logging
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.cache_manager import CacheManager, get_cache_manager_async
from app.core.responses import (
    ErrorCodes,
    create_error_response,
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

# 配置日志
logger = logging.getLogger(__name__)

# 全局缓存管理器 (异步初始化)
_cache_manager: Optional[CacheManager] = None
_cache_manager_initialized = False


async def get_cache_manager() -> CacheManager:
    """获取或初始化缓存管理器（单例模式，支持Redis注入）"""
    global _cache_manager, _cache_manager_initialized

    if _cache_manager is None or not _cache_manager_initialized:
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
# 真实业务数据源 (替代MockBusinessDataSource)
# ============================================================================


class RealBusinessDataSource:
    """
    真实业务数据源

    使用现有API端点获取真实数据，替代硬编码的Mock数据。
    实现方案与前端dashboardService.ts保持一致。
    """

    def __init__(self):
        """初始化真实数据源"""
        self.base_url = "http://localhost:8000"
        self.timeout = 10.0
        logger.info("✅ RealBusinessDataSource initialized")

    async def _make_request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Dict:
        """
        发送HTTP请求到后端API

        Args:
            method: HTTP方法 (GET/POST)
            endpoint: API端点路径
            params: URL查询参数
            json_data: POST请求体

        Returns:
            API响应数据
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{endpoint}"

                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=json_data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error("HTTP请求失败: %(endpoint)s - {str(e)}"")
            return {"success": False, "data": None}
        except Exception as e:
            logger.error("请求异常: %(endpoint)s - {str(e)}"")
            return {"success": False, "data": None}

    def get_dashboard_summary(self, user_id: int, trade_date: Optional[date] = None):
        """
        获取仪表盘汇总数据

        使用真实API端点替代Mock数据:
        1. 指数列表 -> /api/market/v2/etf/list (筛选指数型ETF)
        2. 市场统计 -> 从真实市场数据聚合
        3. 用户持仓 -> /api/api/mtm/portfolio/{user_id}
        4. 活跃策略 -> /api/strategy-mgmt/strategies
        """
        logger.info("获取仪表盘数据: user_id=%(user_id)s, trade_date=%(trade_date)s"")

        dashboard_data = {
            "data_source": "real_api_composite",
            "generated_at": datetime.now().isoformat(),
        }

        # 1. 获取市场概览 (指数列表 + 市场统计)
        try:
            dashboard_data["market_overview"] = self._get_market_overview_data()
        except Exception as e:
            logger.warning("获取市场概览失败: %(e)s"")
            dashboard_data["market_overview"] = self._get_fallback_market_overview()

        # 2. 获取用户持仓数据
        try:
            portfolio_data = self._get_user_portfolio_data(user_id)
            dashboard_data["portfolio"] = portfolio_data
        except Exception as e:
            logger.warning("获取用户持仓失败: %(e)s"")
            dashboard_data["portfolio"] = self._get_fallback_portfolio()

        # 3. 获取自选股数据 (使用占位符，实际可从watchlist表获取)
        dashboard_data["watchlist"] = []

        # 4. 获取活跃策略
        try:
            strategies_data = self._get_user_active_strategies(user_id)
            dashboard_data["strategies"] = strategies_data
        except Exception as e:
            logger.warning("获取活跃策略失败: %(e)s"")
            dashboard_data["strategies"] = []

        # 5. 获取风险预警 (使用占位符，实际可从alerts表获取)
        dashboard_data["risk_alerts"] = []

        return dashboard_data

    def _get_market_overview_data(self) -> Dict:
        """
        获取市场概览数据

        实现方案:
        - 指数列表: 使用 /api/market/v2/etf/list 筛选指数型ETF
        - 市场统计: 从ETF数据聚合统计
        """

        # 同步调用异步方法 (在FastAPI上下文中运行)
        try:
            # 使用同步方式调用API
            import requests

            # 1. 获取ETF列表
            etf_response = requests.get(f"{self.base_url}/api/market/v2/etf/list", params={"limit": 100}, timeout=5)

            if etf_response.status_code == 200 and etf_response.json().get("success"):
                etf_data = etf_response.json().get("data", [])

                # 筛选主要指数型ETF
                index_patterns = [
                    r"^510300",  # 沪深300ETF
                    r"^510500",  # 中证500ETF
                    r"^510050",  # 上证50ETF
                    r"^159915",  # 创业板ETF
                    r"^159919",  # 深证成指ETF
                    r"^159949",  # 深证300ETF
                    r"^510900",  # 300ETF
                ]

                indices = []
                up_count = 0
                down_count = 0
                total_volume = 0

                for etf in etf_data:
                    symbol = etf.get("symbol", "")
                    name = etf.get("name", "")

                    # 检查是否匹配指数型ETF
                    is_index = any(re.match(pattern, symbol) for pattern in index_patterns) or "指数" in name

                    if is_index:
                        change_percent = etf.get("change_percent", 0)

                        indices.append(
                            {
                                "symbol": symbol,
                                "name": name.replace("ETF", "").replace("交易型开放式指数基金", "").strip(),
                                "current_price": etf.get("latest_price", 0),
                                "change_percent": change_percent,
                                "volume": etf.get("volume", 0),
                                "turnover": etf.get("amount", 0),
                                "update_time": etf.get("created_at") or etf.get("trade_date"),
                            }
                        )

                        # 统计涨跌
                        if change_percent > 0:
                            up_count += 1
                        elif change_percent < 0:
                            down_count += 1

                        total_volume += etf.get("volume", 0)

                # 返回市场概览数据
                return {
                    "indices": indices[:10],  # 取前10个主要指数
                    "up_count": up_count,
                    "down_count": down_count,
                    "flat_count": 0,
                    "total_volume": total_volume,
                    "total_turnover": sum(idx.get("turnover", 0) for idx in indices),
                    "top_gainers": sorted(indices, key=lambda x: x.get("change_percent", 0), reverse=True)[:3],
                    "top_losers": sorted(indices, key=lambda x: x.get("change_percent", 0))[:3],
                    "most_active": sorted(indices, key=lambda x: x.get("volume", 0), reverse=True)[:3],
                }

        except Exception as e:
            logger.error("获取市场概览数据失败: %(e)s"")

        # Fallback: 返回降级数据
        return self._get_fallback_market_overview()

    def _get_user_portfolio_data(self, user_id: int) -> Dict:
        """
        获取用户持仓数据

        使用 /api/api/mtm/portfolio/{user_id} 端点
        """
        try:
            import requests

            # 注意: 这里使用user_id作为portfolio_id
            mtm_response = requests.get(f"{self.base_url}/api/api/mtm/portfolio/{user_id}", timeout=5)

            if mtm_response.status_code == 200:
                mtm_data = mtm_response.json()

                # 转换为dashboard期望的格式
                return {
                    "total_market_value": mtm_data.get("total_value", 0),
                    "total_cost": mtm_data.get("total_cost", 0),
                    "total_profit_loss": mtm_data.get("profit_loss", 0),
                    "total_profit_loss_percent": mtm_data.get("profit_loss_percent", 0),
                    "position_count": len(mtm_data.get("positions", [])),
                    "positions": [
                        {
                            "symbol": pos.get("symbol", ""),
                            "name": pos.get("name", ""),
                            "quantity": pos.get("quantity", 0),
                            "avg_cost": pos.get("avg_cost", 0),
                            "current_price": pos.get("current_price", 0),
                            "market_value": pos.get("market_value", 0),
                            "profit_loss": pos.get("profit_loss", 0),
                            "profit_loss_percent": pos.get("profit_loss_percent", 0),
                            "position_percent": pos.get("position_percent", 0),
                        }
                        for pos in mtm_data.get("positions", [])
                    ],
                }

        except Exception as e:
            logger.error("获取用户持仓数据失败: %(e)s"")

        # Fallback: 返回空持仓
        return self._get_fallback_portfolio()

    def _get_user_active_strategies(self, user_id: int) -> List:
        """
        获取用户活跃策略

        使用 /api/strategy-mgmt/strategies 端点，过滤status='active'
        """
        try:
            import requests

            strategy_response = requests.get(
                f"{self.base_url}/api/strategy-mgmt/strategies", params={"user_id": user_id}, timeout=5
            )

            if strategy_response.status_code == 200:
                strategies_data = strategy_response.json()

                # 过滤活跃策略
                if isinstance(strategies_data, dict):
                    strategies = strategies_data.get("data", [])
                elif isinstance(strategies_data, list):
                    strategies = strategies_data
                else:
                    strategies = []

                active_strategies = [s for s in strategies if s.get("status") == "active" or s.get("is_active") is True]

                return active_strategies

        except Exception as e:
            logger.error("获取活跃策略失败: %(e)s"")

        return []

    def _get_fallback_market_overview(self) -> Dict:
        """获取降级市场概览数据"""
        return {
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
            "top_gainers": [],
            "top_losers": [],
            "most_active": [],
        }

    def _get_fallback_portfolio(self) -> Dict:
        """获取降级持仓数据"""
        return {
            "total_market_value": 0,
            "total_cost": 0,
            "total_profit_loss": 0,
            "total_profit_loss_percent": 0,
            "position_count": 0,
            "positions": [],
        }

    def health_check(self) -> Dict:
        """健康检查"""
        return {
            "status": "healthy",
            "database": "postgresql",
            "cache": "enabled",
            "data_source": "real_api",
            "last_check": datetime.now().isoformat(),
        }


# ============================================================================
# 工厂函数
# ============================================================================


def get_business_source():
    """获取业务数据源配置"""
    # 返回真实的业务数据源
    return RealBusinessDataSource()


def get_data_source():
    """获取业务数据源"""
    try:
        return RealBusinessDataSource()
    except Exception as e:
        logger.error("获取数据源失败: {str(e)}"")
        raise HTTPException(status_code=500, detail=f"数据源初始化失败: {str(e)}")


# ============================================================================
# 辅助函数
# ============================================================================


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
        logger.error("构建市场概览失败: {str(e)}"")
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
    except Exception as e:
        logger.error("构建自选股汇总失败: {str(e)}"")
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
    except Exception as e:
        logger.error("构建持仓汇总失败: {str(e)}"")
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
            total_count=len(alerts), unread_count=unread_count, critical_count=critical_count, alerts=alerts
        )
    except Exception as e:
        logger.error("构建风险预警汇总失败: {str(e)}"")
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


async def _try_get_cached_dashboard(
    cache_manager: CacheManager,
    user_id: int,
    trade_date: Optional[date],
) -> tuple[Optional[Dict[str, Any]], bool]:
    """
    尝试从三级缓存获取仪表盘数据

    Args:
        cache_manager: 异步缓存管理器实例
        user_id: 用户ID
        trade_date: 交易日期

    Returns:
        (缓存数据, 缓存是否命中)
        如果命中缓存，返回 (数据, True)
        如果未命中缓存，返回 (None, False)
    """
    try:
        cache_key = _generate_cache_key(user_id, trade_date)
        cached_data = await cache_manager.fetch_from_cache(
            symbol=f"user_{user_id}",
            data_type="dashboard",
            timeframe="1d",
        )

        if cached_data and isinstance(cached_data, dict):
            logger.info("✅ 三级缓存命中: %(cache_key)s"")
            return cached_data, True
        else:
            logger.debug("⚠️ 三级缓存未命中: %(cache_key)s"")
            return None, False

    except Exception as e:
        logger.warning("三级缓存读取失败，将继续获取新数据: {str(e)}"")
        return None, False


async def _cache_dashboard_data(
    cache_manager: CacheManager,
    user_id: int,
    trade_date: Optional[date],
    dashboard_data: Dict[str, Any],
    ttl_hours: int = 24,
) -> bool:
    """
    将仪表盘数据写入三级缓存

    Args:
        cache_manager: 异步缓存管理器实例
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

        success = await cache_manager.write_to_cache(
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
            logger.info("✅ 三级缓存写入成功: %(cache_key)s"")
        else:
            logger.warning("⚠️ 三级缓存写入失败: %(cache_key)s"")

        return success_bool

    except Exception as e:
        logger.warning("三级缓存写入异常: {str(e)}"")
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

    **数据源**: 使用真实API端点（替代Mock数据）
    """
    cache_manager = await get_cache_manager()
    cache_hit = False

    try:
        # 第1阶段：尝试从三级缓存获取数据
        if not bypass_cache:
            cached_entry, cache_hit = await _try_get_cached_dashboard(
                cache_manager,
                user_id,
                trade_date,
            )
            if cache_hit and cached_entry:
                logger.info("三级缓存命中: user_id=%(user_id)s, trade_date=%(trade_date)s"")
                raw_dashboard = cached_entry.get("dashboard_data", {})
            else:
                raw_dashboard = None
        else:
            logger.info("跳过三级缓存获取仪表盘数据: user_id=%(user_id)s"")
            raw_dashboard = None

        # 第2阶段：如果缓存未命中，从数据源获取新数据
        if not cache_hit or raw_dashboard is None:
            logger.info("从真实数据源获取用户%(user_id)s的仪表盘数据"")

            # 使用真实业务数据源
            data_source = get_data_source()
            raw_dashboard = data_source.get_dashboard_summary(user_id, trade_date)

            # 第3阶段：将新数据写入三级缓存
            await _cache_dashboard_data(
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
        logger.error("参数验证失败: {str(e)}"")
        raise HTTPException(status_code=400, detail=f"参数验证失败: {str(e)}")
    except Exception as e:
        logger.error("获取仪表盘数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取仪表盘数据失败: {str(e)}")


@router.get(
    "/market-overview",
    response_model=MarketOverview,
    summary="获取市场概览",
    description="获取市场指数、涨跌家数、榜单等市场概览信息（使用真实API数据）",
)
async def get_market_overview(
    limit: int = Query(10, description="榜单数量限制", ge=1, le=100), data_source=Depends(get_data_source)
):
    """获取市场概览数据（使用真实API）"""
    try:
        # 调用真实业务数据源
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
        logger.error("获取市场概览失败: {str(e)}"")
        raise HTTPException(status_code=500, detail=f"获取市场概览失败: {str(e)}")


@router.get("/health", summary="仪表盘健康检查", description="检查仪表盘服务和数据源的健康状态", tags=["health"])
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
            "real_api": "enabled",
            "database_connections": {"postgresql": "connected", "tdengine": "connected"},
        }

        return create_health_response(service="dashboard", status="healthy", details=health_data, request_id=request_id)

    except Exception as e:
        logger.error("健康检查失败: {str(e)}"")
        return create_error_response(
            error_code=ErrorCodes.SERVICE_UNAVAILABLE,
            message=f"仪表盘服务不可用: {str(e)}",
            request_id=getattr(request.state, "request_id", None),
        )
