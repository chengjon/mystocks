"""OpenAPI contracts and DTOs for data source registry routes."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.openapi_config import COMMON_RESPONSES


def _success_response_spec(description: str, example: Any) -> Dict[int, Dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


DATA_SOURCE_REGISTRY_RESPONSES = {
    400: COMMON_RESPONSES[400],
    401: COMMON_RESPONSES[401],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

DATA_SOURCE_SEARCH_RESPONSES = _success_response_spec(
    "数据源搜索结果",
    {
        "total": 1,
        "data_sources": [
            {
                "endpoint_name": "akshare.stock_zh_a_hist",
                "source_name": "akshare",
                "source_type": "http",
                "data_category": "DAILY_KLINE",
                "status": "active",
                "priority": 3,
                "description": "A股日线历史行情数据源",
            }
        ],
    },
)

DATA_SOURCE_CATEGORY_STATS_RESPONSES = _success_response_spec(
    "数据源分类统计结果",
    [
        {
            "category": "DAILY_KLINE",
            "display_name": "日线K线数据",
            "total": 12,
            "healthy": 10,
            "unhealthy": 2,
            "avg_quality_score": 8.73,
            "avg_response_time": 0.512,
        }
    ],
)

DATA_SOURCE_DETAIL_RESPONSES = _success_response_spec(
    "数据源详情",
    {
        "endpoint_name": "akshare.stock_zh_a_hist",
        "source_name": "akshare",
        "source_type": "http",
        "data_category": "DAILY_KLINE",
        "status": "active",
        "priority": 3,
        "description": "A股日线历史行情数据源",
        "last_call": "2026-04-06T15:30:00",
        "call_count": 128,
    },
)

DATA_SOURCE_HEALTH_CHECK_RESPONSES = _success_response_spec(
    "单个数据源健康检查结果",
    {
        "endpoint_name": "akshare.stock_zh_a_hist",
        "status": "healthy",
        "message": "健康检查通过",
        "duration": 0.432,
        "timestamp": "2026-04-06T15:30:00",
    },
)

DATA_SOURCE_HEALTH_CHECK_ALL_RESPONSES = _success_response_spec(
    "全部数据源健康检查汇总",
    {
        "summary": {
            "total": 3,
            "healthy": 2,
            "unhealthy": 1,
        },
        "results": {
            "akshare.stock_zh_a_hist": {"status": "healthy", "duration": 0.432},
            "tushare.daily_basic": {"status": "healthy", "duration": 0.518},
            "legacy.market_feed": {"status": "unhealthy", "error": "timeout"},
        },
        "timestamp": "2026-04-06T15:30:00",
    },
)

DATA_SOURCE_UPDATE_RESPONSES = _success_response_spec(
    "数据源配置更新结果",
    {
        "success": True,
        "message": "配置已更新",
        "endpoint_name": "akshare.stock_zh_a_hist",
        "updated_fields": ["priority", "data_quality_score", "status", "description"],
    },
)

DATA_SOURCE_TEST_RESPONSES = _success_response_spec(
    "数据源手动测试结果",
    {
        "success": True,
        "endpoint_name": "akshare.stock_zh_a_hist",
        "test_params": {
            "symbol": "000001",
            "start_date": "20240101",
            "end_date": "20240131",
        },
        "duration": 0.318,
        "row_count": 22,
        "data_preview": [
            {
                "date": "2024-01-02",
                "open": 12.34,
                "close": 12.56,
            }
        ],
        "quality_checks": {
            "has_data": True,
            "is_empty": False,
            "column_completeness": {},
            "data_range": {
                "open": {
                    "min": 12.01,
                    "max": 12.88,
                    "mean": 12.43,
                    "null_count": 0,
                    "null_rate": 0.0,
                }
            },
            "duplicate_check": {
                "duplicate_count": 0,
                "duplicate_rate": 0.0,
            },
            "type_consistency": {},
        },
        "error": None,
    },
)


class DataSourceSearchResponse(BaseModel):
    """数据源搜索响应"""

    total: int = Field(..., description="满足筛选条件的数据源总数。")
    data_sources: List[Dict[str, Any]] = Field(..., description="符合条件的数据源配置与状态列表。")


class CategoryStatsResponse(BaseModel):
    """分类统计响应"""

    category: str = Field(..., description="数据分类编码。")
    display_name: str = Field(..., description="数据分类的中文展示名称。")
    total: int = Field(..., description="该分类下注册的数据源总数。")
    healthy: int = Field(..., description="该分类下当前健康的数据源数量。")
    unhealthy: int = Field(..., description="该分类下当前异常或不健康的数据源数量。")
    avg_quality_score: float = Field(..., description="该分类数据源的平均质量评分。")
    avg_response_time: float = Field(..., description="该分类数据源的平均响应时间，单位秒。")


class DataSourceUpdate(BaseModel):
    """数据源更新请求"""

    priority: Optional[int] = Field(None, description="新的优先级，数值越小优先级越高。")
    data_quality_score: Optional[float] = Field(None, description="新的数据质量评分。")
    status: Optional[str] = Field(None, description="新的状态，如 active、maintenance、deprecated。")
    description: Optional[str] = Field(None, description="新的补充说明或治理备注。")


class TestRequest(BaseModel):
    """测试请求"""

    test_params: Dict[str, Any] = Field(..., description="发送给目标数据源处理器的测试参数。")


class TestResponse(BaseModel):
    """测试响应"""

    success: bool = Field(..., description="本次测试是否执行成功。")
    endpoint_name: str = Field(..., description="被测试的数据源接口名称。")
    test_params: Dict[str, Any] = Field(..., description="用于本次测试的数据源参数。")
    duration: Optional[float] = Field(None, description="测试执行耗时，单位秒。")
    row_count: Optional[int] = Field(None, description="测试返回的数据行数。")
    data_preview: Optional[List[Dict]] = Field(None, description="返回数据的预览内容，通常为前几行。")
    quality_checks: Optional[Dict[str, Any]] = Field(None, description="测试后生成的数据质量检查结果。")
    error: Optional[str] = Field(None, description="测试失败时的错误信息。")


DATA_SOURCE_UPDATE_EXAMPLES = {
    "adjust_priority_and_status": {
        "summary": "更新数据源配置",
        "description": "调整数据源优先级、质量评分和状态，常用于治理登记或切换维护状态。",
        "value": {
            "priority": 1,
            "data_quality_score": 9.5,
            "status": "active",
            "description": "主数据源，优先使用。",
        },
    }
}

DATA_SOURCE_TEST_EXAMPLES = {
    "test_daily_kline_endpoint": {
        "summary": "测试日线数据接口",
        "description": "对指定 AKShare 日线接口发起一次样例测试，验证连通性和数据质量。",
        "value": {
            "test_params": {
                "symbol": "000001",
                "start_date": "20240101",
                "end_date": "20240131",
            }
        },
    }
}
