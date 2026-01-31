"""
TDX数据API的Pydantic模型定义
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class RealTimeQuoteResponse(BaseModel):
    """实时行情响应模型"""

    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(..., description="最新价")
    pre_close: float = Field(..., description="昨收价")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    volume: int = Field(..., description="成交量(手)")
    amount: float = Field(..., description="成交额(元)")
    bid1: float = Field(..., description="买一价")
    bid1_volume: int = Field(..., description="买一量")
    ask1: float = Field(..., description="卖一价")
    ask1_volume: int = Field(..., description="卖一量")
    timestamp: str = Field(..., description="查询时间戳")

    # 计算字段
    change: Optional[float] = Field(None, description="涨跌额")
    change_pct: Optional[float] = Field(None, description="涨跌幅(%)")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "600519",
                "name": "贵州茅台",
                "price": 1850.50,
                "pre_close": 1845.00,
                "open": 1846.00,
                "high": 1852.00,
                "low": 1844.00,
                "volume": 123456,
                "amount": 228000000.00,
                "bid1": 1850.00,
                "bid1_volume": 100,
                "ask1": 1851.00,
                "ask1_volume": 150,
                "timestamp": "2025-10-15 14:30:00",
                "change": 5.50,
                "change_pct": 0.30,
            }
        }


class KlineDataPoint(BaseModel):
    """K线数据点模型"""

    date: str = Field(..., description="日期时间")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-10-15 09:30:00",
                "open": 1845.00,
                "high": 1850.00,
                "low": 1844.00,
                "close": 1848.50,
                "volume": 12345,
                "amount": 22800000.00,
            }
        }


class KlineResponse(BaseModel):
    """K线数据响应模型"""

    code: str = Field(..., description="股票/指数代码")
    period: str = Field(..., description="K线周期")
    data: List[KlineDataPoint] = Field(..., description="K线数据列表")
    count: int = Field(..., description="数据条数")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "600519",
                "period": "5m",
                "data": [
                    {
                        "date": "2025-10-15 09:30:00",
                        "open": 1845.00,
                        "high": 1850.00,
                        "low": 1844.00,
                        "close": 1848.50,
                        "volume": 12345,
                        "amount": 22800000.00,
                    }
                ],
                "count": 1,
            }
        }


class IndexQuoteResponse(BaseModel):
    """指数行情响应模型"""

    code: str = Field(..., description="指数代码")
    name: str = Field(..., description="指数名称")
    price: float = Field(..., description="当前点位")
    pre_close: float = Field(..., description="昨收点位")
    open: float = Field(..., description="开盘点位")
    high: float = Field(..., description="最高点位")
    low: float = Field(..., description="最低点位")
    volume: int = Field(..., description="成交量")
    amount: float = Field(..., description="成交额")
    change: Optional[float] = Field(None, description="涨跌点数")
    change_pct: Optional[float] = Field(None, description="涨跌幅(%)")
    timestamp: str = Field(..., description="查询时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "000001",
                "name": "上证指数",
                "price": 3250.50,
                "pre_close": 3245.00,
                "open": 3246.00,
                "high": 3252.00,
                "low": 3244.00,
                "volume": 1234567890,
                "amount": 450000000000.00,
                "change": 5.50,
                "change_pct": 0.17,
                "timestamp": "2025-10-15 14:30:00",
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="详细信息")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "InvalidParameter",
                "message": "无效的股票代码",
                "detail": "股票代码必须为6位数字",
            }
        }


class TdxHealthResponse(BaseModel):
    """TDX服务健康检查响应"""

    status: str = Field(..., description="服务状态")
    tdx_connected: bool = Field(..., description="TDX服务器连接状态")
    timestamp: str = Field(..., description="检查时间")
    server_info: Optional[dict] = Field(None, description="服务器信息")
