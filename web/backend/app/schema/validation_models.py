"""
Pydantic V2 数据验证模型
用于所有API端点的输入和输出验证

遵循P0改进计划 Task 2: 数据验证增强
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StockSymbolModel(BaseModel):
    """股票代码验证模型"""

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        pattern=r"^[A-Za-z0-9_\-]+$",
        description="股票代码（A股: 000001, 600001, 美股: AAPL等）",
    )

    model_config = ConfigDict(json_schema_extra={"example": {"symbol": "000001"}})

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证股票代码格式"""
        v = v.upper().strip()
        if not v:
            raise ValueError("股票代码不能为空")
        if len(v) > 20:
            raise ValueError("股票代码长度不能超过20")
        return v


class DateRangeModel(BaseModel):
    """日期范围验证模型"""

    start_date: datetime = Field(..., description="开始日期，格式: 2025-12-01或2025-12-01T00:00:00")
    end_date: datetime = Field(..., description="结束日期，格式: 2025-12-31或2025-12-31T23:59:59")

    model_config = ConfigDict(json_schema_extra={"example": {"start_date": "2025-01-01", "end_date": "2025-12-31"}})

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: datetime, info) -> datetime:
        """验证日期范围的有效性"""
        if "start_date" in info.data:
            if v <= info.data["start_date"]:
                raise ValueError("结束日期必须晚于开始日期")
            # 检查日期范围是否合理（不超过2年）
            days_diff = (v - info.data["start_date"]).days
            if days_diff > 730:
                raise ValueError("日期范围不能超过2年")
        return v


class MarketDataQueryModel(BaseModel):
    """市场数据查询模型"""

    symbol: str = Field(..., min_length=1, max_length=20, description="股票代码")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    interval: Optional[str] = Field(
        default="daily",
        pattern=r"^(1m|5m|15m|30m|hourly|daily|weekly|monthly)$",
        description="时间间隔: 1m(1分钟), 5m(5分钟), 15m(15分钟), 30m(30分钟), hourly(小时), daily(日), weekly(周), monthly(月)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "000001",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "interval": "daily",
            }
        }
    )


class TechnicalIndicatorQueryModel(BaseModel):
    """技术指标查询模型"""

    symbol: str = Field(..., min_length=1, max_length=20, description="股票代码")
    indicators: List[str] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="技术指标列表（如: MA, RSI, MACD等）",
    )
    period: Optional[int] = Field(default=20, ge=1, le=500, description="周期长度")
    start_date: Optional[datetime] = Field(default=None, description="开始日期（可选）")
    end_date: Optional[datetime] = Field(default=None, description="结束日期（可选）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "000001",
                "indicators": ["MA", "RSI", "MACD"],
                "period": 20,
            }
        }
    )


class PaginationModel(BaseModel):
    """分页参数模型"""

    page: int = Field(default=1, ge=1, le=10000, description="页码（从1开始）")
    page_size: int = Field(default=20, ge=1, le=500, description="每页数量（1-500）")

    model_config = ConfigDict(json_schema_extra={"example": {"page": 1, "page_size": 20}})


class StockListQueryModel(PaginationModel):
    """股票列表查询模型"""

    query: Optional[str] = Field(default=None, max_length=100, description="搜索关键词（可选）")
    sort_by: Optional[str] = Field(
        default="symbol",
        pattern=r"^(symbol|name|price|change|volume)$",
        description="排序字段",
    )
    sort_order: Optional[str] = Field(default="asc", pattern=r"^(asc|desc)$", description="排序顺序")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "page_size": 20,
                "query": "招商银行",
                "sort_by": "symbol",
                "sort_order": "asc",
            }
        }
    )


class TradeOrderModel(BaseModel):
    """交易订单模型"""

    symbol: str = Field(..., min_length=1, max_length=20, description="股票代码")
    order_type: str = Field(..., pattern=r"^(buy|sell)$", description="订单类型（buy/sell）")
    price: float = Field(..., gt=0, le=1000000, description="价格（大于0，不超过100万）")
    quantity: int = Field(..., gt=0, le=10000000, description="数量（大于0，不超过1000万）")
    order_validity: Optional[str] = Field(
        default="gtc",
        pattern=r"^(gtc|gtd|ioc|fok)$",
        description="订单有效期：gtc(持续有效), gtd(指定日期), ioc(立即或取消), fok(全部成交或全部取消)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "000001",
                "order_type": "buy",
                "price": 10.5,
                "quantity": 100,
                "order_validity": "gtc",
            }
        }
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """验证价格合理性"""
        if v <= 0:
            raise ValueError("价格必须大于0")
        if v > 1000000:
            raise ValueError("价格不能超过100万")
        return round(v, 4)

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """验证数量合理性"""
        if v <= 0:
            raise ValueError("数量必须大于0")
        if v > 10000000:
            raise ValueError("数量不能超过1000万")
        return v


class ResponseModel(BaseModel):
    """标准响应模型"""

    code: str = Field(..., description="响应代码")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="时间戳")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "SUCCESS",
                "message": "操作成功",
                "data": {},
                "timestamp": 1733318400.123,
            }
        }
    )


class ErrorResponseModel(BaseModel):
    """错误响应模型"""

    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Any] = Field(default=None, description="错误详情")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="时间戳")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "验证失败",
                "details": {"field": "symbol", "error": "Invalid symbol"},
                "timestamp": 1733318400.123,
            }
        }
    )


# ==================== 应用导出 ====================

__all__ = [
    "StockSymbolModel",
    "DateRangeModel",
    "MarketDataQueryModel",
    "TechnicalIndicatorQueryModel",
    "PaginationModel",
    "StockListQueryModel",
    "TradeOrderModel",
    "ResponseModel",
    "ErrorResponseModel",
]
