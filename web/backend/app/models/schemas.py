"""
行业概念分析API响应模型

定义行业/概念分析相关的响应数据结构
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IndustryInfo(BaseModel):
    """行业信息模型"""
    industry_code: str = Field(..., description="行业代码")
    industry_name: str = Field(..., description="行业名称")
    stock_count: Optional[int] = Field(None, description="成分股数量")
    up_count: Optional[int] = Field(None, description="上涨股票数")
    down_count: Optional[int] = Field(None, description="下跌股票数")
    leader_stock: Optional[str] = Field(None, description="领涨股")
    latest_price: Optional[float] = Field(None, description="最新价")
    change_percent: Optional[float] = Field(None, description="涨跌幅(%)")
    change_amount: Optional[float] = Field(None, description="涨跌额")
    volume: Optional[int] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    total_market_value: Optional[float] = Field(None, description="总市值")
    turnover_rate: Optional[float] = Field(None, description="换手率(%)")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ConceptInfo(BaseModel):
    """概念信息模型"""
    concept_code: str = Field(..., description="概念代码")
    concept_name: str = Field(..., description="概念名称")
    stock_count: Optional[int] = Field(None, description="成分股数量")
    up_count: Optional[int] = Field(None, description="上涨股票数")
    down_count: Optional[int] = Field(None, description="下跌股票数")
    leader_stock: Optional[str] = Field(None, description="领涨股")
    latest_price: Optional[float] = Field(None, description="最新价")
    change_percent: Optional[float] = Field(None, description="涨跌幅(%)")
    change_amount: Optional[float] = Field(None, description="涨跌额")
    volume: Optional[int] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    total_market_value: Optional[float] = Field(None, description="总市值")
    turnover_rate: Optional[float] = Field(None, description="换手率(%)")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class StockInfo(BaseModel):
    """股票信息模型"""
    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    latest_price: Optional[float] = Field(None, description="最新价")
    change_percent: Optional[float] = Field(None, description="涨跌幅(%)")
    volume: Optional[int] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")


class IndustryListResponse(BaseModel):
    """行业列表响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "industries": [
                        {
                            "industry_code": "BK0475",
                            "industry_name": "银行",
                            "stock_count": 42,
                            "up_count": 15,
                            "down_count": 27,
                            "leader_stock": "600036.SH",
                            "latest_price": 12.56,
                            "change_percent": 1.25,
                            "change_amount": 0.16,
                            "volume": 123456789,
                            "amount": 1543210000.0,
                            "total_market_value": 54321000000.0,
                            "turnover_rate": 0.85,
                            "updated_at": "2025-11-17T10:30:00"
                        }
                    ],
                    "total_count": 1
                },
                "timestamp": "2025-11-17T10:30:00"
            }
        }


class ConceptListResponse(BaseModel):
    """概念列表响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "concepts": [
                        {
                            "concept_code": "GN001",
                            "concept_name": "人工智能",
                            "stock_count": 85,
                            "up_count": 45,
                            "down_count": 40,
                            "leader_stock": "300033.SZ",
                            "latest_price": 25.68,
                            "change_percent": 3.25,
                            "change_amount": 0.81,
                            "volume": 987654321,
                            "amount": 2543210000.0,
                            "total_market_value": 123456000000.0,
                            "turnover_rate": 2.15,
                            "updated_at": "2025-11-17T10:30:00"
                        }
                    ],
                    "total_count": 1
                },
                "timestamp": "2025-11-17T10:30:00"
            }
        }


class StockListResponse(BaseModel):
    """股票列表响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "stocks": [
                        {
                            "symbol": "600036.SH",
                            "name": "招商银行",
                            "latest_price": 38.45,
                            "change_percent": 1.85,
                            "volume": 45678901,
                            "amount": 1754321000.0
                        }
                    ],
                    "total_count": 1,
                    "industry_code": "BK0475"
                },
                "timestamp": "2025-11-17T10:30:00"
            }
        }


class IndustryPerformanceResponse(BaseModel):
    """行业表现响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "industry": {
                        "industry_code": "BK0475",
                        "industry_name": "银行",
                        "stock_count": 42,
                        "up_count": 15,
                        "down_count": 27,
                        "leader_stock": "600036.SH",
                        "latest_price": 12.56,
                        "change_percent": 1.25,
                        "change_amount": 0.16,
                        "volume": 123456789,
                        "amount": 1543210000.0,
                        "total_market_value": 54321000000.0,
                        "turnover_rate": 0.85,
                        "updated_at": "2025-11-17T10:30:00"
                    },
                    "up_count": 15,
                    "down_count": 27,
                    "leader_stock": {
                        "symbol": "600036.SH",
                        "price": 38.45,
                        "change_percent": 1.85
                    },
                    "stocks_performance": [
                        {
                            "symbol": "600036.SH",
                            "latest_price": 38.45,
                            "change_percent": 1.85
                        }
                    ]
                },
                "timestamp": "2025-11-17T10:30:00"
            }
        }


class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")