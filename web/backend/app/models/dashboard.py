"""
仪表盘数据模型

定义仪表盘相关的Pydantic模型，用于API请求和响应的数据验证。

版本: 1.0.0
日期: 2025-11-21
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# 请求模型
# ============================================================================


class DashboardRequest(BaseModel):
    """仪表盘请求模型"""

    user_id: int = Field(..., description="用户ID", ge=1)
    trade_date: Optional[date] = Field(None, description="交易日期，默认为今天")
    include_market_overview: bool = Field(True, description="是否包含市场概览")
    include_watchlist: bool = Field(True, description="是否包含自选股数据")
    include_portfolio: bool = Field(True, description="是否包含持仓数据")
    include_risk_alerts: bool = Field(True, description="是否包含风险预警")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1001,
                "trade_date": "2025-11-21",
                "include_market_overview": True,
                "include_watchlist": True,
                "include_portfolio": True,
                "include_risk_alerts": True,
            }
        }


# ============================================================================
# 响应模型 - 市场概览
# ============================================================================


class MarketIndexItem(BaseModel):
    """市场指数项"""

    symbol: str = Field(..., description="指数代码")
    name: str = Field(..., description="指数名称")
    current_price: float = Field(..., description="当前价格")
    change_percent: float = Field(..., description="涨跌幅(%)")
    volume: Optional[float] = Field(None, description="成交量")
    turnover: Optional[float] = Field(None, description="成交额")
    update_time: Optional[datetime] = Field(None, description="更新时间")


class MarketOverview(BaseModel):
    """市场概览"""

    indices: List[MarketIndexItem] = Field(default_factory=list, description="市场指数列表")
    up_count: int = Field(0, description="上涨家数")
    down_count: int = Field(0, description="下跌家数")
    flat_count: int = Field(0, description="平盘家数")
    total_volume: Optional[float] = Field(None, description="总成交量")
    total_turnover: Optional[float] = Field(None, description="总成交额")
    top_gainers: List[Dict[str, Any]] = Field(default_factory=list, description="涨幅榜")
    top_losers: List[Dict[str, Any]] = Field(default_factory=list, description="跌幅榜")
    most_active: List[Dict[str, Any]] = Field(default_factory=list, description="成交额榜")


# ============================================================================
# 响应模型 - 自选股
# ============================================================================


class WatchlistItem(BaseModel):
    """自选股项"""

    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    current_price: Optional[float] = Field(None, description="当前价格")
    change_percent: Optional[float] = Field(None, description="涨跌幅(%)")
    note: Optional[str] = Field(None, description="备注")
    added_at: Optional[datetime] = Field(None, description="添加时间")


class WatchlistSummary(BaseModel):
    """自选股汇总"""

    total_count: int = Field(0, description="自选股总数")
    items: List[WatchlistItem] = Field(default_factory=list, description="自选股列表")
    avg_change_percent: Optional[float] = Field(None, description="平均涨跌幅")


# ============================================================================
# 响应模型 - 持仓
# ============================================================================


class PositionItem(BaseModel):
    """持仓项"""

    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    quantity: float = Field(..., description="持仓数量", ge=0)
    avg_cost: float = Field(..., description="平均成本", ge=0)
    current_price: Optional[float] = Field(None, description="当前价格")
    market_value: Optional[float] = Field(None, description="市值")
    profit_loss: Optional[float] = Field(None, description="盈亏金额")
    profit_loss_percent: Optional[float] = Field(None, description="盈亏比例(%)")
    position_percent: Optional[float] = Field(None, description="持仓占比(%)")


class PortfolioSummary(BaseModel):
    """持仓汇总"""

    total_market_value: float = Field(0, description="总市值")
    total_cost: float = Field(0, description="总成本")
    total_profit_loss: float = Field(0, description="总盈亏")
    total_profit_loss_percent: float = Field(0, description="总盈亏比例(%)")
    position_count: int = Field(0, description="持仓股票数")
    positions: List[PositionItem] = Field(default_factory=list, description="持仓列表")


# ============================================================================
# 响应模型 - 风险预警
# ============================================================================


class RiskAlert(BaseModel):
    """风险预警项"""

    alert_id: int = Field(..., description="预警ID")
    alert_type: str = Field(..., description="预警类型")
    alert_level: str = Field(..., description="预警级别: info/warning/critical")
    symbol: Optional[str] = Field(None, description="相关股票代码")
    message: str = Field(..., description="预警消息")
    triggered_at: datetime = Field(..., description="触发时间")
    is_read: bool = Field(False, description="是否已读")


class RiskAlertSummary(BaseModel):
    """风险预警汇总"""

    total_count: int = Field(0, description="预警总数")
    unread_count: int = Field(0, description="未读预警数")
    critical_count: int = Field(0, description="严重预警数")
    alerts: List[RiskAlert] = Field(default_factory=list, description="预警列表")


# ============================================================================
# 响应模型 - 仪表盘汇总
# ============================================================================


class DashboardResponse(BaseModel):
    """仪表盘响应模型"""

    user_id: int = Field(..., description="用户ID")
    trade_date: date = Field(..., description="交易日期")
    generated_at: datetime = Field(..., description="生成时间")

    # 各模块数据
    market_overview: Optional[MarketOverview] = Field(None, description="市场概览")
    watchlist: Optional[WatchlistSummary] = Field(None, description="自选股汇总")
    portfolio: Optional[PortfolioSummary] = Field(None, description="持仓汇总")
    risk_alerts: Optional[RiskAlertSummary] = Field(None, description="风险预警汇总")

    # 元数据
    data_source: str = Field("composite", description="数据源类型")
    cache_hit: bool = Field(False, description="是否命中缓存")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1001,
                "trade_date": "2025-11-21",
                "generated_at": "2025-11-21T10:30:00",
                "market_overview": {
                    "indices": [
                        {
                            "symbol": "000001",
                            "name": "上证指数",
                            "current_price": 3100.50,
                            "change_percent": 1.2,
                        }
                    ],
                    "up_count": 2500,
                    "down_count": 1500,
                    "flat_count": 100,
                },
                "watchlist": {
                    "total_count": 10,
                    "items": [],
                    "avg_change_percent": 0.5,
                },
                "portfolio": {
                    "total_market_value": 100000.0,
                    "total_cost": 95000.0,
                    "total_profit_loss": 5000.0,
                    "total_profit_loss_percent": 5.26,
                    "position_count": 5,
                    "positions": [],
                },
                "risk_alerts": {
                    "total_count": 3,
                    "unread_count": 2,
                    "critical_count": 1,
                    "alerts": [],
                },
                "data_source": "composite",
                "cache_hit": False,
            }
        }


# ============================================================================
# 错误响应模型
# ============================================================================


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_USER_ID",
                "error_message": "用户ID无效",
                "details": {"user_id": -1},
                "timestamp": "2025-11-21T10:30:00",
            }
        }
