"""
市场数据API Schemas (Pydantic模型)

用于FastAPI请求验证和响应序列化:
- FundFlow: 个股资金流向
- ETFData: ETF基金数据
- ChipRace: 竞价抢筹数据
- LongHuBang: 龙虎榜数据
- MarketOverview: 市场概览数据
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# ==================== 资金流向 (Fund Flow) ====================


class FundFlowRequest(BaseModel):
    """资金流向查询请求 (用于POST请求)"""

    symbol: str = Field(..., description="股票代码 (如: 600519.SH)", min_length=6, max_length=20)
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

    race_type: str = Field(default="open", description="抢筹类型: open(早盘) / end(尾盘)")
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


class MarketOverviewDetailedResponse(BaseModel):
    """市场概览详细响应 (包含ETF、竞价抢筹、龙虎榜)"""

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


# ==================== Market Overview ====================


class MarketOverviewRequest(BaseModel):
    """市场概览查询请求"""

    date: Optional[str] = Field(None, description="查询日期 YYYY-MM-DD (默认最新)")


class IndexQuote(BaseModel):
    """指数行情"""

    index_code: str = Field(description="指数代码 (如: 000001.SH)")
    index_name: str = Field(description="指数名称")
    current_price: float = Field(description="当前点位")
    change: float = Field(description="涨跌点数")
    change_percent: float = Field(description="涨跌幅(%)")
    volume: Optional[float] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")


class HotSector(BaseModel):
    """热门板块"""

    sector_name: str = Field(description="板块名称")
    change_percent: float = Field(description="板块涨跌幅(%)")
    leading_stock: Optional[str] = Field(None, description="领涨股票")
    stock_count: int = Field(description="成分股数量")


class MarketOverviewResponse(BaseModel):
    """市场概览响应"""

    date: str = Field(description="数据日期")
    indices: List[IndexQuote] = Field(description="主要指数行情")
    hot_sectors: List[HotSector] = Field(description="热门板块")
    market_sentiment: str = Field(description="市场情绪 (up/down/neutral)")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-12-29",
                "indices": [
                    {
                        "index_code": "000001.SH",
                        "index_name": "上证指数",
                        "current_price": 3000.5,
                        "change": 15.3,
                        "change_percent": 0.51,
                    }
                ],
                "hot_sectors": [
                    {"sector_name": "新能源", "change_percent": 3.2, "leading_stock": "600519.SH", "stock_count": 45}
                ],
                "market_sentiment": "up",
            }
        }


# ==================== Enhanced KLine Models ====================


class KLineRequestV2(BaseModel):
    """增强版K线查询请求 (符合OpenAPI模板)"""

    symbol: str = Field(
        ..., description="股票代码", examples=["000001.SZ", "600519.SH"], pattern=r"^[0-9]{6}\.[A-Z]{2}$"
    )
    interval: str = Field(..., description="K线周期", examples=["1m", "5m", "15m", "1h", "1d", "1w", "1M"])
    start_date: Optional[str] = Field(None, description="开始日期", examples=["2024-01-01"])
    end_date: Optional[str] = Field(None, description="结束日期", examples=["2024-12-29"])
    adjust: str = Field(
        default="qfq", description="复权方式 (qfq=前复权, hfq=后复权, none=不复权)", pattern="^(qfq|hfq|none)$"
    )
    limit: int = Field(default=500, ge=1, le=1000, description="返回数量限制")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v):
        """验证股票代码格式"""
        if len(v) < 6:
            raise ValueError("股票代码格式错误,至少6位")
        return v.upper()

    @field_validator("interval")
    @classmethod
    def validate_interval(cls, v):
        """验证K线周期"""
        valid_intervals = ["1m", "5m", "15m", "1h", "1d", "1w", "1M"]
        if v not in valid_intervals:
            raise ValueError(f"无效的K线周期,支持: {valid_intervals}")
        return v


class KLineCandleV2(BaseModel):
    """增强版K线蜡烛图数据 (符合OpenAPI模板)"""

    timestamp: int = Field(..., description="Unix时间戳 (毫秒)")
    open: float = Field(..., ge=0, description="开盘价")
    high: float = Field(..., ge=0, description="最高价")
    low: float = Field(..., ge=0, description="最低价")
    close: float = Field(..., ge=0, description="收盘价")
    volume: int = Field(..., ge=0, description="成交量")
    amount: Optional[float] = Field(None, ge=0, description="成交额")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 1640995200000,
                "open": 10.5,
                "high": 11.0,
                "low": 10.3,
                "close": 10.8,
                "volume": 1000000,
                "amount": 10800000.0,
            }
        }


class KLineResponseV2(BaseModel):
    """增强版K线响应 (使用统一响应格式)"""

    klines: List[KLineCandleV2] = Field(description="K线数据列表")
    total_count: int = Field(description="总记录数")
    symbol: str = Field(description="股票代码")
    interval: str = Field(description="K线周期")

    class Config:
        json_schema_extra = {
            "example": {
                "klines": [
                    {
                        "timestamp": 1640995200000,
                        "open": 10.5,
                        "high": 11.0,
                        "low": 10.3,
                        "close": 10.8,
                        "volume": 1000000,
                    }
                ],
                "total_count": 250,
                "symbol": "000001.SZ",
                "interval": "1d",
            }
        }
