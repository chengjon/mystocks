#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财API请求/响应Schema

定义问财功能的Pydantic数据模型，用于API请求验证和响应序列化

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============================================================================
# 请求Schema
# ============================================================================


class WencaiQueryRequest(BaseModel):
    """
    执行问财查询请求

    用于POST /api/market/wencai/query
    """

    query_name: str = Field(
        ...,
        description="查询名称，如qs_1, qs_2, ..., qs_9",
        example="qs_9",
        min_length=4,
        max_length=20,
    )
    pages: int = Field(default=1, description="获取页数", ge=1, le=10, example=1)

    @validator("query_name")
    def validate_query_name(cls, v):
        """验证查询名称格式 - 只允许 qs_1 到 qs_9"""
        if not re.match(r"^qs_[1-9]$", v):
            raise ValueError(f"query_name must be in format 'qs_N' where N is 1-9. Got: {v}")
        return v

    class Config:
        schema_extra = {"example": {"query_name": "qs_9", "pages": 1}}


class WencaiCustomQueryRequest(BaseModel):
    """
    自定义查询请求

    用于POST /api/market/wencai/custom-query
    """

    query_text: str = Field(
        ...,
        description="自定义查询语句（自然语言）",
        example="请列出今天涨幅超过5%的股票",
        min_length=5,
        max_length=500,
    )
    pages: int = Field(default=1, description="获取页数", ge=1, le=5, example=1)

    class Config:
        schema_extra = {"example": {"query_text": "请列出今天涨幅超过5%的股票", "pages": 1}}


class WencaiRefreshRequest(BaseModel):
    """
    刷新查询数据请求（可选参数）

    用于POST /api/market/wencai/refresh/{query_name}
    """

    pages: int = Field(default=1, description="获取页数", ge=1, le=10)
    force: bool = Field(default=False, description="是否强制刷新（忽略缓存）")


# ============================================================================
# 响应Schema
# ============================================================================


class WencaiQueryInfo(BaseModel):
    """
    查询信息

    用于GET /api/market/wencai/queries
    """

    id: int = Field(..., description="查询ID")
    query_name: str = Field(..., description="查询名称", example="qs_1")
    query_text: str = Field(..., description="查询语句", example="请列出...")
    description: Optional[str] = Field(None, description="查询说明")
    is_active: bool = Field(..., description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "query_name": "qs_1",
                "query_text": "请列举出20天内出现过涨停...",
                "description": "涨停板筛选",
                "is_active": True,
                "created_at": "2025-10-17T09:00:00",
                "updated_at": "2025-10-17T09:00:00",
            }
        }


class WencaiQueryListResponse(BaseModel):
    """
    查询列表响应

    用于GET /api/market/wencai/queries
    """

    queries: List[WencaiQueryInfo] = Field(..., description="查询列表")
    total: int = Field(..., description="总数量")

    class Config:
        schema_extra = {
            "example": {
                "queries": [
                    {
                        "id": 1,
                        "query_name": "qs_1",
                        "query_text": "请列举出20天内出现过涨停...",
                        "description": "涨停板筛选",
                        "is_active": True,
                        "created_at": "2025-10-17T09:00:00",
                        "updated_at": "2025-10-17T09:00:00",
                    }
                ],
                "total": 9,
            }
        }


class WencaiQueryResponse(BaseModel):
    """
    查询执行响应

    用于POST /api/market/wencai/query
    """

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    query_name: str = Field(..., description="查询名称")
    total_records: int = Field(..., description="获取的总记录数", ge=0)
    new_records: int = Field(..., description="新增记录数", ge=0)
    duplicate_records: int = Field(..., description="重复记录数", ge=0)
    table_name: str = Field(..., description="结果表名")
    fetch_time: datetime = Field(..., description="数据获取时间")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "查询执行成功",
                "data": {
                    "table_name": "wencai_qs_9",
                    "columns": ["股票代码", "股票简称", "..."],
                },
                "total_records": 45,
                "new_records": 12,
                "duplicate_records": 33,
                "query_name": "qs_9",
                "fetch_time": "2025-10-17T09:00:00",
            }
        }


class WencaiCustomQueryResponse(BaseModel):
    """
    自定义查询响应

    用于POST /api/market/wencai/custom-query
    """

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    query_text: str = Field(..., description="查询语句")
    total_records: int = Field(..., description="获取的总记录数", ge=0)
    results: List[Dict[str, Any]] = Field(..., description="查询结果列表")
    columns: List[str] = Field(..., description="列名列表")
    fetch_time: datetime = Field(..., description="数据获取时间")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "查询执行成功",
                "query_text": "请列出今天涨幅超过5%的股票",
                "total_records": 25,
                "results": [{"股票代码": "000001", "股票简称": "平安银行", "涨跌幅": "6.5%"}],
                "columns": ["股票代码", "股票简称", "涨跌幅"],
                "fetch_time": "2025-10-18T10:00:00",
            }
        }


class WencaiResultItem(BaseModel):
    """
    单条查询结果

    注意：由于不同查询返回的字段不同，这里使用动态字典
    """

    data: Dict[str, Any] = Field(..., description="结果数据（动态字段）")
    fetch_time: datetime = Field(..., description="数据获取时间")

    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "股票代码": "000001",
                    "股票简称": "平安银行",
                    "涨跌幅": "2.5%",
                    "换手率": "3.2%",
                },
                "fetch_time": "2025-10-17T09:00:00",
            }
        }


class WencaiResultsResponse(BaseModel):
    """
    查询结果列表响应

    用于GET /api/market/wencai/results/{query_name}
    """

    query_name: str = Field(..., description="查询名称")
    total: int = Field(..., description="总记录数", ge=0)
    results: List[Dict[str, Any]] = Field(..., description="结果列表")
    columns: List[str] = Field(..., description="列名列表")
    latest_fetch_time: Optional[datetime] = Field(None, description="最新数据时间")

    class Config:
        schema_extra = {
            "example": {
                "query_name": "qs_9",
                "total": 45,
                "results": [
                    {
                        "股票代码": "000001",
                        "股票简称": "平安银行",
                        "fetch_time": "2025-10-17T09:00:00",
                    }
                ],
                "columns": ["股票代码", "股票简称", "fetch_time"],
                "latest_fetch_time": "2025-10-17T09:00:00",
            }
        }


class WencaiRefreshResponse(BaseModel):
    """
    刷新任务响应

    用于POST /api/market/wencai/refresh/{query_name}
    """

    status: str = Field(..., description="任务状态", example="refreshing")
    message: str = Field(..., description="消息")
    task_id: Optional[str] = Field(None, description="后台任务ID")
    query_name: str = Field(..., description="查询名称")

    class Config:
        schema_extra = {
            "example": {
                "status": "refreshing",
                "message": "后台任务已启动",
                "task_id": "abc123-def456-ghi789",
                "query_name": "qs_9",
            }
        }


class WencaiHistoryItem(BaseModel):
    """
    历史数据项
    """

    date: str = Field(..., description="日期", example="2025-10-17")
    total_records: int = Field(..., description="记录数", ge=0)
    fetch_count: int = Field(..., description="获取次数", ge=0)

    class Config:
        schema_extra = {"example": {"date": "2025-10-17", "total_records": 45, "fetch_count": 3}}


class WencaiHistoryResponse(BaseModel):
    """
    历史数据响应

    用于GET /api/market/wencai/history/{query_name}
    """

    query_name: str = Field(..., description="查询名称")
    date_range: List[str] = Field(..., description="日期范围")
    history: List[WencaiHistoryItem] = Field(..., description="历史数据")
    total_days: int = Field(..., description="总天数", ge=0)

    class Config:
        schema_extra = {
            "example": {
                "query_name": "qs_9",
                "date_range": ["2025-10-10", "2025-10-17"],
                "history": [{"date": "2025-10-17", "total_records": 45, "fetch_count": 3}],
                "total_days": 7,
            }
        }


# ============================================================================
# 错误响应Schema
# ============================================================================


class WencaiErrorResponse(BaseModel):
    """
    错误响应

    统一的错误格式
    """

    success: bool = Field(False, description="是否成功")
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "query_name must start with 'qs_'",
                "details": {"field": "query_name", "value": "invalid_name"},
            }
        }


# ============================================================================
# 统计响应Schema
# ============================================================================


class WencaiStatsResponse(BaseModel):
    """
    统计信息响应（可选，用于监控面板）
    """

    total_queries: int = Field(..., description="总查询数", ge=0)
    active_queries: int = Field(..., description="启用的查询数", ge=0)
    total_records: int = Field(..., description="总记录数", ge=0)
    last_refresh_time: Optional[datetime] = Field(None, description="最后刷新时间")

    class Config:
        schema_extra = {
            "example": {
                "total_queries": 9,
                "active_queries": 9,
                "total_records": 350,
                "last_refresh_time": "2025-10-17T09:00:00",
            }
        }
