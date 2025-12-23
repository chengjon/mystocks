"""
市场数据API Schemas (Pydantic模型)

用于FastAPI请求验证和响应序列化:
- FundFlow: 个股资金流向
- ETFData: ETF基金数据
- ChipRace: 竞价抢筹数据
- LongHuBang: 龙虎榜数据
- MarketOverview: 市场概览数据
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime


# ==================== 资金流向 (Fund Flow) ====================


class FundFlowRequest(BaseModel):
    """资金流向查询请求 (用于POST请求)"""

    symbol: str = Field(
        ..., description="股票代码 (如: 600519.SH)", min_length=6, max_length=20
    )
    timeframe: str = Field(default="1", description="时间维度: 1/3/5/10天")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, v):
        if v not in ["1", "3", "5", "10"]:
            raise ValueError("timeframe必须为: 1, 3, 5, 10")
        return v


class FundFlowItem(BaseModel):
    """资金流向单项数据"""

    trade_date: str = Field(description="交易日期 YYYY-MM-DD")
    main_net_inflow: float = Field(description="主力净流入额(元)")
    main_net_inflow_rate: float = Field(default=0, description="主力净流入占比(%)")
    super_large_net_inflow: float = Field(description="超大单净流入(元)")
    large_net_inflow: float = Field(description="大单净流入(元)")
    medium_net_inflow: float = Field(description="中单净流入(元)")
    small_net_inflow: float = Field(description="小单净流入(元)")


class FundFlowDataResponse(BaseModel):
    """资金流向数据响应"""

    fund_flow: List[FundFlowItem] = Field(description="资金流向数据列表")
    total: int = Field(description="总记录数")
    symbol: Optional[str] = Field(None, description="股票代码")
    timeframe: Optional[str] = Field(None, description="时间维度")


class FundFlowResponse(BaseModel):
    """资金流向响应 (数据库模型)"""

    id: int
    symbol: str
    trade_date: date
    timeframe: str
    main_net_inflow: float = Field(description="主力净流入额(元)")
    main_net_inflow_rate: float = Field(description="主力净流入占比(%)")
    super_large_net_inflow: float = Field(description="超大单净流入(元)")
    large_net_inflow: float = Field(description="大单净流入(元)")
    medium_net_inflow: float = Field(description="中单净流入(元)")
    small_net_inflow: float = Field(description="小单净流入(元)")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== ETF数据 (ETF Spot) ====================


class ETFDataRequest(BaseModel):
    """ETF数据查询请求"""

    symbol: Optional[str] = Field(None, description="ETF代码 (如: 510300)")
    keyword: Optional[str] = Field(None, description="关键词搜索(名称/代码)")
    limit: int = Field(default=50, ge=1, le=500, description="返回数量限制")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v):
        if v and len(v) < 6:
            raise ValueError("ETF代码长度至少6位")
        return v


class ETFDataResponse(BaseModel):
    """ETF数据响应"""

    id: int
    symbol: str
    name: str
    trade_date: date
    latest_price: float = Field(description="最新价")
    change_percent: float = Field(description="涨跌幅(%)")
    change_amount: float = Field(description="涨跌额")
    volume: int = Field(description="成交量")
    amount: float = Field(description="成交额")
    open_price: float
    high_price: float
    low_price: float
    prev_close: float = Field(description="昨收价")
    turnover_rate: float = Field(description="换手率(%)")
    total_market_cap: float = Field(description="总市值")
    circulating_market_cap: float = Field(description="流通市值")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 竞价抢筹 (Chip Race) ====================


class ChipRaceRequest(BaseModel):
    """竞价抢筹查询请求"""

    race_type: str = Field(
        default="open", description="抢筹类型: open(早盘) / end(尾盘)"
    )
    trade_date: Optional[date] = Field(None, description="交易日期")
    min_race_amount: Optional[float] = Field(None, ge=0, description="最小抢筹金额(元)")
    limit: int = Field(default=100, ge=1, le=500)

    @field_validator("race_type")
    @classmethod
    def validate_race_type(cls, v):
        if v not in ["open", "end"]:
            raise ValueError("race_type必须为: open 或 end")
        return v


class ChipRaceResponse(BaseModel):
    """竞价抢筹响应"""

    id: int
    symbol: str
    name: str
    trade_date: date
    race_type: str = Field(description="抢筹类型: open/end")
    latest_price: float
    change_percent: float = Field(description="涨跌幅(%)")
    prev_close: float
    open_price: float
    race_amount: float = Field(description="抢筹金额(元)")
    race_amplitude: float = Field(description="抢筹幅度(%)")
    race_commission: float = Field(description="抢筹委托金额")
    race_transaction: float = Field(description="抢筹成交金额")
    race_ratio: float = Field(description="抢筹占比(%)")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 龙虎榜 (Long Hu Bang) ====================


class LongHuBangRequest(BaseModel):
    """龙虎榜查询请求"""

    symbol: Optional[str] = Field(None, description="股票代码")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    min_net_amount: Optional[float] = Field(None, description="最小净买入额(元)")
    limit: int = Field(default=100, ge=1, le=500)


class LongHuBangResponse(BaseModel):
    """龙虎榜响应"""

    id: int
    symbol: str
    name: str
    trade_date: date
    reason: Optional[str] = Field(description="上榜原因")
    buy_amount: float = Field(description="买入总额(元)")
    sell_amount: float = Field(description="卖出总额(元)")
    net_amount: float = Field(description="净买入额(元)")
    turnover_rate: float = Field(description="换手率(%)")
    institution_buy: Optional[float] = Field(description="机构买入额")
    institution_sell: Optional[float] = Field(description="机构卖出额")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 通用响应模型 ====================


class PaginatedResponse(BaseModel):
    """分页响应"""

    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    data: List[dict] = Field(description="数据列表")


class MessageResponse(BaseModel):
    """通用消息响应"""

    success: bool
    message: str
    data: Optional[dict] = None


# ==================== 市场概览 (Market Overview) ====================


class MarketOverviewStats(BaseModel):
    """市场统计数据"""

    total_stocks: int = Field(description="总股票数")
    rising_stocks: int = Field(description="上涨股票数")
    falling_stocks: int = Field(description="下跌股票数")
    avg_change_percent: float = Field(description="平均涨跌幅(%)")


class TopETFItem(BaseModel):
    """热门ETF概览项"""

    symbol: str = Field(description="ETF代码")
    name: str = Field(description="ETF名称")
    latest_price: float = Field(description="最新价")
    change_percent: float = Field(description="涨跌幅(%)")
    volume: int = Field(description="成交量")


class ChipRaceItem(BaseModel):
    """竞价抢筹概览项"""

    symbol: str = Field(description="股票代码")
    name: str = Field(description="股票名称")
    race_amount: float = Field(description="抢筹金额(元)")
    change_percent: float = Field(description="涨跌幅(%)")


class LongHuBangItem(BaseModel):
    """龙虎榜概览项"""

    symbol: str = Field(description="股票代码")
    name: str = Field(description="股票名称")
    net_amount: float = Field(description="净买入额(元)")
    reason: Optional[str] = Field(None, description="上榜原因")


class MarketOverviewResponse(BaseModel):
    """市场概览响应"""

    market_stats: MarketOverviewStats = Field(description="市场统计")
    top_etfs: List[TopETFItem] = Field(default_factory=list, description="热门ETF列表")
    chip_races: List[ChipRaceItem] = Field(default_factory=list, description="竞价抢筹列表")
    long_hu_bang: List[LongHuBangItem] = Field(default_factory=list, description="龙虎榜列表")
    timestamp: str = Field(description="数据时间戳(ISO格式)")


# ==================== K线数据 (Kline) ====================


class KlineCandle(BaseModel):
    """K线蜡烛图数据"""

    datetime: str = Field(description="时间")
    open: float = Field(description="开盘价")
    high: float = Field(description="最高价")
    low: float = Field(description="最低价")
    close: float = Field(description="收盘价")
    volume: float = Field(description="成交量")
    amount: Optional[float] = Field(None, description="成交额")


class KlineRequest(BaseModel):
    """K线查询请求"""

    symbol: str = Field(..., description="股票代码(6位数字)")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    period: str = Field(default="1d", description="K线周期: 1m/5m/15m/30m/1h/1d")

    @field_validator("period")
    @classmethod
    def validate_period(cls, v):
        valid_periods = ["1m", "5m", "15m", "30m", "1h", "1d"]
        if v not in valid_periods:
            raise ValueError(f"period必须为: {', '.join(valid_periods)}")
        return v


class KlineResponse(BaseModel):
    """K线数据响应"""

    symbol: str = Field(description="股票代码")
    period: str = Field(description="K线周期")
    data: List[KlineCandle] = Field(description="K线数据列表")
    count: int = Field(description="数据条数")


# ==================== 热力图数据 (Heatmap) ====================


class HeatmapStock(BaseModel):
    """热力图股票数据"""

    symbol: str = Field(description="股票代码")
    name: str = Field(description="股票名称")
    change_percent: float = Field(description="涨跌幅(%)")
    market_cap: Optional[float] = Field(None, description="市值(元)")


class HeatmapResponse(BaseModel):
    """热力图响应"""

    sector: str = Field(description="板块名称")
    stocks: List[HeatmapStock] = Field(description="股票列表")
    avg_change: float = Field(description="板块平均涨跌幅(%)")
