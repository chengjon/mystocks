"""数据源注册表管理 API 路由。"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Header, Path, Query

from app.core.config import settings
from app.core.exceptions import BusinessException
from app.core.responses import ErrorCodes, UnifiedResponse, create_error_response, create_unified_success_response
from app.core.security import verify_token
from app.api.data_source_registry_contracts import (
    DATA_SOURCE_CATEGORY_STATS_RESPONSES,
    DATA_SOURCE_DETAIL_RESPONSES,
    DATA_SOURCE_HEALTH_CHECK_ALL_RESPONSES,
    DATA_SOURCE_HEALTH_CHECK_RESPONSES,
    DATA_SOURCE_REGISTRY_RESPONSES,
    DATA_SOURCE_SEARCH_RESPONSES,
    DATA_SOURCE_TEST_EXAMPLES,
    DATA_SOURCE_TEST_RESPONSES,
    DATA_SOURCE_UPDATE_EXAMPLES,
    DATA_SOURCE_UPDATE_RESPONSES,
    CategoryStatsResponse,
    DataSourceSearchResponse,
    DataSourceUpdate,
    TestRequest,
    TestResponse,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/data-sources",
    tags=["数据源管理"],
    responses=DATA_SOURCE_REGISTRY_RESPONSES,
)


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
        raise BusinessException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "缺少或无效的认证凭据",
            ).dict(),
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token or verify_token(token) is None:
        raise BusinessException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "认证失败或令牌已过期",
            ).dict(),
        )


# ==================== API Endpoints ====================


@router.get("/", response_model=UnifiedResponse[DataSourceSearchResponse], responses=DATA_SOURCE_SEARCH_RESPONSES)
async def search_data_sources(
    data_category: Optional[str] = Query(None, description="5层数据分类（如: DAILY_KLINE）"),
    classification_level: Optional[int] = Query(None, description="分类层级（1-5）"),
    source_type: Optional[str] = Query(None, description="数据源类型（如: akshare, tushare）"),
    only_healthy: Optional[bool] = Query(False, description="仅返回健康的数据源"),
    keyword: Optional[str] = Query(None, description="模糊搜索关键词"),
    status: str = Query("active", description="数据源状态（active/maintenance/deprecated）"),
) -> UnifiedResponse[DataSourceSearchResponse]:
    """搜索和筛选数据源接口。"""
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

        return create_unified_success_response(
            data=DataSourceSearchResponse(total=len(endpoints), data_sources=endpoints),
            message="数据源搜索成功",
        )

    except Exception as e:
        raise BusinessException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get(
    "/categories",
    response_model=UnifiedResponse[List[CategoryStatsResponse]],
    description="汇总所有五层数据分类的接口规模、健康状态、平均质量评分和平均响应时间。",
    responses=DATA_SOURCE_CATEGORY_STATS_RESPONSES,
)
async def get_category_stats() -> UnifiedResponse[List[CategoryStatsResponse]]:
    """获取所有 5 层数据分类的统计信息。"""
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

        return create_unified_success_response(data=result, message="数据源分类统计获取成功")

    except Exception as e:
        raise BusinessException(status_code=500, detail=f"获取分类统计失败: {str(e)}")


@router.get(
    "/{endpoint_name}",
    response_model=UnifiedResponse[Dict[str, Any]],
    description="获取单个数据源接口的完整配置、调用计数和最近一次调用信息。",
    responses=DATA_SOURCE_DETAIL_RESPONSES,
)
async def get_data_source(
    endpoint_name: str = Path(..., description="需要查询详情的数据源接口名称。"),
) -> UnifiedResponse[Dict[str, Any]]:
    """获取单个数据源的详细信息。"""
    try:
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise BusinessException(status_code=404, detail=f"接口不存在: {endpoint_name}")

        source_data = manager.registry[endpoint_name]
        config = source_data.get("config", {})

        # 添加额外信息
        config["endpoint_name"] = endpoint_name
        config["last_call"] = source_data.get("last_call")
        config["call_count"] = source_data.get("call_count", 0)

        return create_unified_success_response(data=config, message="数据源详情获取成功")

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"获取数据源失败: {str(e)}")


@router.put(
    "/{endpoint_name}",
    response_model=UnifiedResponse[Dict[str, Any]],
    description="更新指定数据源的优先级、质量评分、状态或补充描述信息。",
    responses=DATA_SOURCE_UPDATE_RESPONSES,
)
async def update_data_source(
    endpoint_name: str = Path(..., description="需要更新配置的数据源接口名称。"),
    update: DataSourceUpdate = Body(..., openapi_examples=DATA_SOURCE_UPDATE_EXAMPLES),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer Token。非测试环境下写操作必须提供有效认证凭据。",
    ),
) -> UnifiedResponse[Dict[str, Any]]:
    """更新数据源配置。"""
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise BusinessException(status_code=404, detail=f"接口不存在: {endpoint_name}")

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
            raise BusinessException(status_code=400, detail="无更新内容")

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

        return create_unified_success_response(
            data={"endpoint_name": endpoint_name, "updated_fields": list(updates.keys())},
            message="配置已更新",
        )

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post(
    "/{endpoint_name}/test",
    response_model=UnifiedResponse[TestResponse],
    description="对指定数据源执行一次手动测试，返回耗时、数据预览和质量检查结果。",
    responses=DATA_SOURCE_TEST_RESPONSES,
)
async def test_data_source(
    endpoint_name: str = Path(..., description="需要执行测试的数据源接口名称。"),
    request: TestRequest = Body(..., openapi_examples=DATA_SOURCE_TEST_EXAMPLES),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer Token。非测试环境下手动测试操作必须提供有效认证凭据。",
    ),
) -> UnifiedResponse[TestResponse]:
    """手动测试数据源。"""
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise BusinessException(status_code=404, detail=f"接口不存在: {endpoint_name}")

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

        return create_unified_success_response(data=TestResponse(**result), message="数据源手动测试完成")

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"测试失败: {str(e)}")


@router.post(
    "/{endpoint_name}/health-check",
    response_model=UnifiedResponse[Dict[str, Any]],
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
) -> UnifiedResponse[Dict[str, Any]]:
    """健康检查单个数据源。"""
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        if endpoint_name not in manager.registry:
            raise BusinessException(status_code=404, detail=f"接口不存在: {endpoint_name}")

        # 获取预设的测试参数
        config = manager.registry[endpoint_name]["config"]
        test_params = config.get("test_parameters", {})

        if not test_params:
            return create_unified_success_response(
                data={
                    "endpoint_name": endpoint_name,
                    "status": "skipped",
                    "timestamp": datetime.now().isoformat(),
                },
                message="无预设测试参数",
            )

        # 执行健康检查
        health_result = manager.health_check(endpoint_name=endpoint_name)
        return create_unified_success_response(data=health_result, message="数据源健康检查完成")

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.post(
    "/health-check/all",
    response_model=UnifiedResponse[Dict[str, Any]],
    description="批量执行所有数据源的健康检查，并返回带时间戳的汇总结果。",
    responses=DATA_SOURCE_HEALTH_CHECK_ALL_RESPONSES,
)
async def health_check_all_data_sources(
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer Token。非测试环境下批量健康检查必须提供有效认证凭据。",
    ),
) -> UnifiedResponse[Dict[str, Any]]:
    """健康检查所有数据源。"""
    try:
        _require_write_auth(authorization)
        manager = get_manager()

        health_result = manager.health_check()

        # 添加时间戳
        health_result["timestamp"] = datetime.now().isoformat()

        return create_unified_success_response(data=health_result, message="全部数据源健康检查完成")

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"健康检查失败: {str(e)}")


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
