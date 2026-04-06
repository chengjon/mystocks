"""
数据源注册表管理API

提供数据源的查询、更新、测试等功能。

功能:
1. 搜索和筛选数据源接口
2. 获取分类统计信息
3. 更新数据源配置
4. 手动测试数据源
5. 健康检查

作者: Claude Code
版本: v1.0
创建时间: 2026-01-02
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Header, Path, Query
from pydantic import BaseModel, Field

from app.core.config import settings
from app.openapi_config import COMMON_RESPONSES
from app.core.responses import ErrorCodes, create_error_response
from app.core.security import verify_token

logger = logging.getLogger(__name__)


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

router = APIRouter(
    prefix="/api/v1/data-sources",
    tags=["数据源管理"],
    responses=DATA_SOURCE_REGISTRY_RESPONSES,
)


# ==================== Pydantic Models ====================


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


# ==================== Helper Functions ====================


def get_db_connection():
    """获取数据库连接"""
    import psycopg2
    from dotenv import load_dotenv

    load_dotenv()

    return psycopg2.connect(
        host=os.getenv("POSTGRESQL_HOST"),
        port=int(os.getenv("POSTGRESQL_PORT", "5438")),
        user=os.getenv("POSTGRESQL_USER", "postgres"),
        password=os.getenv("POSTGRESQL_PASSWORD"),
        database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
    )


def get_manager():
    """获取数据源管理器实例"""
    from src.core.data_source import DataSourceManagerV2

    return DataSourceManagerV2()


def _require_write_auth(authorization: Optional[str]) -> None:
    """写操作鉴权：测试环境放行，非测试环境要求有效Bearer Token。"""
    if settings.testing:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "缺少或无效的认证凭据",
            ).dict(),
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token or verify_token(token) is None:
        raise HTTPException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "认证失败或令牌已过期",
            ).dict(),
        )


# ==================== API Endpoints ====================


@router.get("/", response_model=DataSourceSearchResponse, responses=DATA_SOURCE_SEARCH_RESPONSES)
async def search_data_sources(
    data_category: Optional[str] = Query(None, description="5层数据分类（如: DAILY_KLINE）"),
    classification_level: Optional[int] = Query(None, description="分类层级（1-5）"),
    source_type: Optional[str] = Query(None, description="数据源类型（如: akshare, tushare）"),
    only_healthy: Optional[bool] = Query(False, description="仅返回健康的数据源"),
    keyword: Optional[str] = Query(None, description="模糊搜索关键词"),
    status: str = Query("active", description="数据源状态（active/maintenance/deprecated）"),
):
    """
    搜索和筛选数据源接口

    支持的筛选条件:
    - data_category: 按5层数据分类筛选
    - classification_level: 按分类层级筛选
    - source_type: 按数据源类型筛选
    - only_healthy: 仅返回健康的数据源
    - keyword: 模糊搜索接口名称或描述
    - status: 按状态筛选（默认: active）

    返回:
        符合条件的数据源列表

    示例:
        # 搜索所有日线数据接口
        GET /api/v1/data-sources/?data_category=DAILY_KLINE

        # 搜索akshare数据源
        GET /api/v1/data-sources/?source_type=akshare

        # 搜索包含"日线"关键词的接口
        GET /api/v1/data-sources/?keyword=日线

        # 仅搜索健康的接口
        GET /api/v1/data-sources/?only_healthy=true
    """
    try:
        manager = get_manager()

        # 使用V2管理器的查询功能
        endpoints = manager.find_endpoints(
            data_category=data_category,
            classification_level=classification_level,
            source_type=source_type,
            only_healthy=only_healthy,
        )

        # 状态筛选
        if status:
            endpoints = [ep for ep in endpoints if ep.get("status") == status]

        # 关键词搜索
        if keyword:
            keyword_lower = keyword.lower()
            endpoints = [
                ep
                for ep in endpoints
                if keyword_lower in ep.get("endpoint_name", "").lower()
                or keyword_lower in ep.get("description", "").lower()
                or keyword_lower in ep.get("source_name", "").lower()
            ]

        return DataSourceSearchResponse(total=len(endpoints), data_sources=endpoints)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get(
    "/categories",
    response_model=List[CategoryStatsResponse],
    description="汇总所有五层数据分类的接口规模、健康状态、平均质量评分和平均响应时间。",
    responses=DATA_SOURCE_CATEGORY_STATS_RESPONSES,
)
async def get_category_stats():
    """
    获取所有5层数据分类的统计信息

    返回:
        分类统计列表，包含每个分类的:
        - 总接口数
        - 健康接口数
        - 异常接口数
        - 平均质量评分
        - 平均响应时间

    示例:
        GET /api/v1/data-sources/categories
    """
    try:
        manager = get_manager()

        # 按分类分组统计
        categories = {}

        for endpoint_name, source_data in manager.registry.items():
            config = source_data.get("config", {})
            category = config.get("data_category", "UNKNOWN")

            if category not in categories:
                categories[category] = {
                    "category": category,
                    "display_name": _get_category_display_name(category),
                    "total": 0,
                    "healthy": 0,
                    "unhealthy": 0,
                    "quality_scores": [],
                    "response_times": [],
                }

            stats = categories[category]
            stats["total"] += 1

            # 健康状态统计
            health_status = config.get("health_status", "unknown")
            if health_status == "healthy":
                stats["healthy"] += 1
            else:
                stats["unhealthy"] += 1

            # 收集质量指标
            quality_score = config.get("data_quality_score")
            if quality_score is not None:
                stats["quality_scores"].append(quality_score)

            response_time = config.get("avg_response_time")
            if response_time is not None:
                stats["response_times"].append(response_time)

        # 计算平均值
        result = []
        for category, stats in categories.items():
            avg_quality = sum(stats["quality_scores"]) / len(stats["quality_scores"]) if stats["quality_scores"] else 0
            avg_response = sum(stats["response_times"]) / len(stats["response_times"]) if stats["response_times"] else 0

            result.append(
                CategoryStatsResponse(
                    category=stats["category"],
                    display_name=stats["display_name"],
                    total=stats["total"],
                    healthy=stats["healthy"],
                    unhealthy=stats["unhealthy"],
                    avg_quality_score=round(avg_quality, 2),
                    avg_response_time=round(avg_response, 3),
                )
            )

        # 按分类名称排序
        result.sort(key=lambda x: x.category)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类统计失败: {str(e)}")


@router.get(
    "/{endpoint_name}",
    description="获取单个数据源接口的完整配置、调用计数和最近一次调用信息。",
    responses=DATA_SOURCE_DETAIL_RESPONSES,
)
async def get_data_source(endpoint_name: str = Path(..., description="需要查询详情的数据源接口名称。")):
    """
    获取单个数据源的详细信息

    Args:
        endpoint_name: 接口名称

    返回:
        数据源完整配置信息

    示例:
        GET /api/v1/data-sources/akshare.stock_zh_a_hist
    """
    try:
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise HTTPException(status_code=404, detail=f"接口不存在: {endpoint_name}")

        source_data = manager.registry[endpoint_name]
        config = source_data.get("config", {})

        # 添加额外信息
        config["endpoint_name"] = endpoint_name
        config["last_call"] = source_data.get("last_call")
        config["call_count"] = source_data.get("call_count", 0)

        return config

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据源失败: {str(e)}")


@router.put(
    "/{endpoint_name}",
    description="更新指定数据源的优先级、质量评分、状态或补充描述信息。",
)
async def update_data_source(
    endpoint_name: str = Path(..., description="需要更新配置的数据源接口名称。"),
    update: DataSourceUpdate = Body(..., openapi_examples=DATA_SOURCE_UPDATE_EXAMPLES),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer Token。非测试环境下写操作必须提供有效认证凭据。",
    ),
):
    """
    更新数据源配置

    支持更新的字段:
    - priority: 优先级（1-10，数字越小优先级越高）
    - data_quality_score: 质量评分（0-10）
    - status: 状态（active/maintenance/deprecated）
    - description: 描述信息

    Args:
        endpoint_name: 接口名称
        update: 更新内容

    返回:
        更新成功确认

    示例:
        PUT /api/v1/data-sources/akshare.stock_zh_a_hist
        {
            "priority": 1,
            "data_quality_score": 9.5
        }
    """
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise HTTPException(status_code=404, detail=f"接口不存在: {endpoint_name}")

        # 构建更新SQL
        updates = {}
        if update.priority is not None:
            updates["priority"] = update.priority
        if update.data_quality_score is not None:
            updates["data_quality_score"] = update.data_quality_score
        if update.status is not None:
            updates["status"] = update.status
        if update.description is not None:
            updates["description"] = update.description

        if not updates:
            raise HTTPException(status_code=400, detail="无更新内容")

        # 更新数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        set_clause = ", ".join([f"{k} = %({k})s" for k in updates.keys()])
        updates["updated_at"] = "NOW()"

        sql = f"""
            UPDATE data_source_registry
            SET {set_clause}
            WHERE endpoint_name = %(endpoint_name)s
        """

        cursor.execute(sql, {**updates, "endpoint_name": endpoint_name})
        conn.commit()
        cursor.close()
        conn.close()

        # 重新加载注册表
        manager._load_registry()

        return {
            "success": True,
            "message": "配置已更新",
            "endpoint_name": endpoint_name,
            "updated_fields": list(updates.keys()),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post(
    "/{endpoint_name}/test",
    response_model=TestResponse,
    description="对指定数据源执行一次手动测试，返回耗时、数据预览和质量检查结果。",
)
async def test_data_source(
    endpoint_name: str = Path(..., description="需要执行测试的数据源接口名称。"),
    request: TestRequest = Body(..., openapi_examples=DATA_SOURCE_TEST_EXAMPLES),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer Token。非测试环境下手动测试操作必须提供有效认证凭据。",
    ),
):
    """
    手动测试数据源

    发送测试请求到数据源接口，验证其可用性和数据质量

    Args:
        endpoint_name: 接口名称
        request: 测试参数

    返回:
        测试结果，包含:
        - 是否成功
        - 响应时间
        - 返回数据量
        - 数据预览
        - 质量检查结果
        - 错误信息（如果失败）

    示例:
        POST /api/v1/data-sources/akshare.stock_zh_a_hist/test
        {
            "test_params": {
                "symbol": "000001",
                "start_date": "20240101",
                "end_date": "20240131"
            }
        }
    """
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise HTTPException(status_code=404, detail=f"接口不存在: {endpoint_name}")

        test_params = request.test_params
        result = {
            "endpoint_name": endpoint_name,
            "test_params": test_params,
            "success": False,
            "duration": None,
            "row_count": 0,
            "data_preview": None,
            "quality_checks": None,
            "error": None,
        }

        # 执行测试
        start_time = datetime.now()

        try:
            # 调用数据源
            from src.core.data_source_handlers_v2 import get_handler

            handler = get_handler(endpoint_name, manager.registry[endpoint_name]["config"])
            data = handler.fetch(**test_params)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result["duration"] = round(duration, 3)

            # 处理返回数据
            if data is not None:
                if hasattr(data, "__len__"):
                    result["row_count"] = len(data)

                    # 数据预览（前3行）
                    if hasattr(data, "head") and result["row_count"] > 0:
                        preview_df = data.head(3)
                        if hasattr(preview_df, "to_dict"):
                            result["data_preview"] = preview_df.to_dict(orient="records")

                    # 数据质量检查
                    quality_checks = _check_data_quality(data, manager.registry[endpoint_name]["config"])
                    result["quality_checks"] = quality_checks

            result["success"] = True

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result["duration"] = round(duration, 3)
            result["error"] = str(e)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.post(
    "/{endpoint_name}/health-check",
    description="使用预设测试参数对单个数据源执行健康检查，快速判断接口可用性。",
    responses=DATA_SOURCE_HEALTH_CHECK_RESPONSES,
)
async def health_check_data_source(
    endpoint_name: str = Path(..., description="需要执行健康检查的数据源接口名称。"),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer Token。非测试环境下健康检查操作必须提供有效认证凭据。",
    ),
):
    """
    健康检查单个数据源

    使用预设的测试参数进行健康检查，验证数据源是否可用

    Args:
        endpoint_name: 接口名称

    返回:
        健康检查结果

    示例:
        POST /api/v1/data-sources/akshare.stock_zh_a_hist/health-check
    """
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise HTTPException(status_code=404, detail=f"接口不存在: {endpoint_name}")

        # 获取预设的测试参数
        config = manager.registry[endpoint_name]["config"]
        test_params = config.get("test_parameters", {})

        if not test_params:
            return {
                "endpoint_name": endpoint_name,
                "status": "skipped",
                "message": "无预设测试参数",
                "timestamp": datetime.now().isoformat(),
            }

        # 执行健康检查
        health_result = manager.health_check(endpoint_name=endpoint_name)
        return health_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.post(
    "/health-check/all",
    description="批量执行所有数据源的健康检查，并返回带时间戳的汇总结果。",
    responses=DATA_SOURCE_HEALTH_CHECK_ALL_RESPONSES,
)
async def health_check_all_data_sources(
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer Token。非测试环境下批量健康检查必须提供有效认证凭据。",
    ),
):
    """
    健康检查所有数据源

    遍历所有数据源，使用预设参数进行健康检查

    返回:
        所有数据源的健康检查结果汇总

    示例:
        POST /api/v1/data-sources/health-check/all
    """
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        health_result = manager.health_check()

        # 添加时间戳
        health_result["timestamp"] = datetime.now().isoformat()

        return health_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


# ==================== Helper Functions ====================


def _get_category_display_name(category: str) -> str:
    """获取分类的显示名称"""
    display_names = {
        "DAILY_KLINE": "日线K线数据",
        "MINUTE_KLINE": "分钟K线数据",
        "TICK_DATA": "Tick逐笔数据",
        "REALTIME_QUOTES": "实时行情",
        "REFERENCE_DATA": "参考数据",
        "FINANCIAL_DATA": "财务数据",
        "INDEX_DATA": "指数数据",
        "SECTOR_DATA": "板块数据",
        # 添加更多分类...
    }
    return display_names.get(category, category)


def _check_data_quality(data: Any, config: Dict) -> Dict[str, Any]:
    """
    数据质量检查

    检查项:
    - 数据完整性（列缺失检查）
    - 数据范围（最小值、最大值、空值率）
    - 重复数据检查
    - 数据类型一致性

    Args:
        data: 返回的数据
        config: 数据源配置

    Returns:
        质量检查结果
    """
    checks = {
        "has_data": data is not None,
        "is_empty": False,
        "column_completeness": {},
        "data_range": {},
        "duplicate_check": None,
        "type_consistency": {},
    }

    if data is None:
        return checks

    # 检查是否为空
    if hasattr(data, "empty"):
        checks["is_empty"] = data.empty
    elif hasattr(data, "__len__"):
        checks["is_empty"] = len(data) == 0

    if checks["is_empty"]:
        return checks

    # DataFrame类型检查
    if hasattr(data, "columns"):
        import pandas as pd

        # 1. 列完整性检查
        expected_params = config.get("parameters", {})
        actual_cols = data.columns.tolist()

        for param_name, param_config in expected_params.items():
            is_present = param_name in actual_cols
            checks["column_completeness"][param_name] = {
                "present": is_present,
                "status": "exists" if is_present else "missing",
            }

        # 2. 数据范围检查（仅检查前5个数值列）
        numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()[:5]

        for col in numeric_cols:
            if pd.api.types.is_numeric_dtype(data[col]):
                checks["data_range"][col] = {
                    "min": float(data[col].min()),
                    "max": float(data[col].max()),
                    "mean": float(data[col].mean()),
                    "null_count": int(data[col].isna().sum()),
                    "null_rate": float(data[col].isna().sum() / len(data)),
                }

        # 3. 重复数据检查
        if hasattr(data, "duplicated"):
            dup_count = int(data.duplicated().sum())
            checks["duplicate_check"] = {
                "duplicate_count": dup_count,
                "duplicate_rate": dup_count / len(data) if len(data) > 0 else 0,
            }

    return checks


# ==================== Startup/Shutdown Events ====================


@router.on_event("startup")
async def startup_event():
    """API启动事件"""
    logger.info("数据源管理API已启动")


@router.on_event("shutdown")
async def shutdown_event():
    """API关闭事件"""
    logger.info("数据源管理API已关闭")
