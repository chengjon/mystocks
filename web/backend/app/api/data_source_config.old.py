"""数据源配置CRUD API (符合API契约管理规范)

提供数据源配置的完整CRUD操作、版本管理和热重载功能。

核心功能:
1. 创建/更新/删除数据源配置
2. 查询配置和版本历史
3. 配置回滚到任意版本
4. 批量操作支持
5. 配置热重载

契约管理:
- 使用统一响应格式 (UnifiedResponse)
- 支持API版本管理
- 支持OpenAPI规范导出
- 符合项目API契约标准

Author: Claude Code (Main CLI)
Date: 2026-01-09
Version: 1.0.0
API Version: v1
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, validator

from app.api._data_source_config_old_reload import (
    get_current_user_impl,
    handle_config_error_impl,
    reload_config_impl,
    shutdown_event_impl,
    startup_event_impl,
)

# 导入统一响应格式
from app.core.responses import (
    BusinessCode,
    UnifiedResponse,
    create_unified_error_response,
    create_unified_success_response,
)


router = APIRouter(prefix="/api/v1/data-sources/config", tags=["数据源配置管理"])


# ==================== Pydantic Models ====================


class DataSourceCreate(BaseModel):
    """创建数据源配置请求"""

    endpoint_name: str = Field(..., description="端点名称（唯一标识）", min_length=1, max_length=255)
    source_name: str = Field(..., description="数据源名称（如: akshare, tushare）", min_length=1, max_length=100)
    source_type: str = Field(..., description="数据源类型", min_length=1, max_length=50)
    data_category: str = Field(
        ...,
        description="数据分类（DAILY_KLINE, MINUTE_KLINE, REALTIME_QUOTE, FINANCIAL_DATA, REFERENCE_DATA）",
        min_length=1,
        max_length=50,
    )
    parameters: Dict[str, Any] = Field(..., description="参数定义")
    test_parameters: Dict[str, Any] = Field(..., description="测试参数")
    priority: int = Field(default=5, description="优先级（1-10，数字越小优先级越高）", ge=1, le=10)
    description: str = Field(default="", description="描述信息")

    @validator("data_category")
    def validate_data_category(cls, v):
        """验证数据分类"""
        valid_categories = ["DAILY_KLINE", "MINUTE_KLINE", "REALTIME_QUOTE", "FINANCIAL_DATA", "REFERENCE_DATA"]
        if v not in valid_categories:
            raise ValueError(f"Invalid data_category. Must be one of: {', '.join(valid_categories)}")
        return v


class DataSourceUpdate(BaseModel):
    """更新数据源配置请求"""

    priority: Optional[int] = Field(None, description="优先级（1-10）", ge=1, le=10)
    data_quality_score: Optional[float] = Field(None, description="质量评分（0-10）", ge=0, le=10)
    status: Optional[str] = Field(None, description="状态（active, maintenance, deprecated）")
    description: Optional[str] = Field(None, description="描述信息")
    parameters: Optional[Dict[str, Any]] = Field(None, description="参数定义")
    test_parameters: Optional[Dict[str, Any]] = Field(None, "测试参数")


class DataSourceResponse(BaseModel):
    """数据源配置响应"""

    endpoint_name: str
    source_name: str
    source_type: str
    data_category: str
    parameters: Dict[str, Any]
    test_parameters: Dict[str, Any]
    priority: int
    description: str
    status: str
    data_quality_score: Optional[float] = None
    created_at: str
    updated_at: str


class VersionInfo(BaseModel):
    """版本信息"""

    endpoint_name: str
    version: int
    change_type: str
    changed_by: str
    changed_at: str
    change_summary: str
    metadata: Dict[str, Any]


class BatchOperationRequest(BaseModel):
    """批量操作请求"""

    operations: List[Dict[str, Any]] = Field(..., description="操作列表（最多50个）", min_items=1, max_items=50)

    @validator("operations")
    def validate_operations(cls, v):
        """验证操作列表"""
        if not v:
            raise ValueError("Operations list cannot be empty")
        if len(v) > 50:
            raise ValueError("Maximum 50 operations allowed in a single batch")
        return v


class BatchOperationResponse(BaseModel):
    """批量操作响应"""

    total: int
    succeeded: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[str]


class RollbackRequest(BaseModel):
    """回滚请求"""

    changed_by: str = Field(default="system", description="变更人")


class ReloadRequest(BaseModel):
    """热重载请求"""

    changed_by: str = Field(default="system", description="变更人")


# ==================== Unified Response Models ====================


class ConfigChangeResponse(BaseModel):
    """配置变更响应（统一格式）"""

    success: bool
    endpoint_name: str
    version: Optional[int] = None
    message: str
    error: Optional[str] = None


# ==================== Helper Functions ====================


def get_config_manager():
    """获取ConfigManager实例"""
    from src.core.data_source.config_manager import ConfigManager

    # 初始化配置管理器
    yaml_config_path = "config/data_sources_registry.yaml"

    # 可选：传入PostgreSQL连接
    postgresql_access = None
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgresql_access = get_postgres_async()
    except Exception:
        pass

    return ConfigManager(yaml_config_path=yaml_config_path, postgresql_access=postgresql_access)


def get_current_user() -> str:
    """获取当前用户（从JWT token或其他认证机制）"""
    return get_current_user_impl()


def handle_config_error(error: str, request_id: Optional[str] = None) -> UnifiedResponse:
    """处理配置错误并返回统一响应格式"""
    return handle_config_error_impl(error, request_id)


# ==================== API Endpoints ====================


@router.post("/", response_model=UnifiedResponse, status_code=201)
async def create_data_source(config: DataSourceCreate, request: Request, current_user: str = Depends(get_current_user)):
    """创建新的数据源配置

    功能:
    - 创建全新的数据源端点配置
    - 自动记录版本历史（版本1）
    - 验证配置有效性
    - 保存到YAML文件和PostgreSQL数据库

    Args:
        config: 数据源配置信息
        request: FastAPI请求对象
        current_user: 当前用户（自动注入）

    Returns:
        UnifiedResponse: 创建结果，包含版本号

    Raises:
        400: 配置验证失败
        409: 端点名称已存在

    Example:
        POST /api/v1/data-sources/config
        {
            "endpoint_name": "new_source",
            "source_name": "akshare",
            "source_type": "http",
            "data_category": "DAILY_KLINE",
            "parameters": {...},
            "test_parameters": {...},
            "priority": 5,
            "description": "新数据源"
        }

    """
    request_id = getattr(request.state, "request_id", None)

    try:
        manager = get_config_manager()

        result = manager.create_endpoint(
            endpoint_name=config.endpoint_name,
            source_name=config.source_name,
            source_type=config.source_type,
            data_category=config.data_category,
            parameters=config.parameters,
            test_parameters=config.test_parameters,
            priority=config.priority,
            description=config.description,
            changed_by=current_user,
        )

        if not result.success:
            return handle_config_error(result.error, request_id)

        # 返回统一格式的成功响应
        return create_unified_success_response(
            data={
                "endpoint_name": result.endpoint_name,
                "version": result.version,
            },
            message=f"数据源配置创建成功: {result.endpoint_name}",
            code=BusinessCode.CREATED,
            request_id=request_id,
        )

    except Exception as e:
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"创建数据源配置失败: {e!s}",
            error_code="CREATE_ENDPOINT_ERROR",
            request_id=request_id,
        )


@router.put("/{endpoint_name}", response_model=ConfigChangeResponse)
async def update_data_source(
    endpoint_name: str, updates: DataSourceUpdate, current_user: str = Depends(get_current_user),
):
    """更新数据源配置

    功能:
    - 更新现有数据源配置的字段
    - 自动记录版本历史
    - 保存变更前后的值到元数据

    Args:
        endpoint_name: 端点名称
        updates: 要更新的字段
        current_user: 当前用户

    Returns:
        ConfigChangeResponse: 更新结果，包含新版本号

    Raises:
        404: 端点不存在
        400: 无有效更新字段

    Example:
        PUT /api/v1/data-sources/config/new_source
        {
            "priority": 1,
            "data_quality_score": 9.5
        }

    """
    try:
        manager = get_config_manager()

        # 构建更新字典（仅包含非None字段）
        update_dict = {}
        if updates.priority is not None:
            update_dict["priority"] = updates.priority
        if updates.data_quality_score is not None:
            update_dict["data_quality_score"] = updates.data_quality_score
        if updates.status is not None:
            update_dict["status"] = updates.status
        if updates.description is not None:
            update_dict["description"] = updates.description
        if updates.parameters is not None:
            update_dict["parameters"] = updates.parameters
        if updates.test_parameters is not None:
            update_dict["test_parameters"] = updates.test_parameters

        if not update_dict:
            raise HTTPException(status_code=400, detail="无有效更新字段")

        result = manager.update_endpoint(endpoint_name=endpoint_name, updates=update_dict, changed_by=current_user)

        if not result.success:
            if "not found" in result.error:
                raise HTTPException(status_code=404, detail=result.error)
            raise HTTPException(status_code=400, detail=result.error)

        return ConfigChangeResponse(
            success=result.success, endpoint_name=result.endpoint_name, version=result.version, message=result.message,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新数据源配置失败: {e!s}")


@router.delete("/{endpoint_name}", response_model=ConfigChangeResponse)
async def delete_data_source(endpoint_name: str, current_user: str = Depends(get_current_user)):
    """删除数据源配置

    功能:
    - 删除数据源配置（软删除）
    - 记录版本历史
    - 可通过回滚恢复

    Args:
        endpoint_name: 端点名称
        current_user: 当前用户

    Returns:
        ConfigChangeResponse: 删除结果

    Raises:
        404: 端点不存在

    Example:
        DELETE /api/v1/data-sources/config/new_source

    """
    try:
        manager = get_config_manager()

        result = manager.delete_endpoint(endpoint_name=endpoint_name, changed_by=current_user)

        if not result.success:
            if "not found" in result.error:
                raise HTTPException(status_code=404, detail=result.error)
            raise HTTPException(status_code=400, detail=result.error)

        return ConfigChangeResponse(
            success=result.success, endpoint_name=result.endpoint_name, version=result.version, message=result.message,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除数据源配置失败: {e!s}")


@router.get("/{endpoint_name}", response_model=DataSourceResponse)
async def get_data_source(endpoint_name: str):
    """获取单个数据源配置

    Args:
        endpoint_name: 端点名称

    Returns:
        DataSourceResponse: 数据源配置详情

    Raises:
        404: 端点不存在

    Example:
        GET /api/v1/data-sources/config/akshare.stock_zh_a_hist

    """
    try:
        manager = get_config_manager()

        config = manager.get_endpoint(endpoint_name)

        if not config:
            raise HTTPException(status_code=404, detail=f"端点不存在: {endpoint_name}")

        return DataSourceResponse(**config)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据源配置失败: {e!s}")


@router.get("/", response_model=List[DataSourceResponse])
async def list_data_sources(
    data_category: Optional[str] = Query(None, description="数据分类"),
    source_type: Optional[str] = Query(None, description="数据源类型"),
    status: Optional[str] = Query("active", description="状态（active, maintenance, deprecated）"),
):
    """列出数据源配置

    支持按以下条件过滤:
    - data_category: 数据分类
    - source_type: 数据源类型
    - status: 状态（默认: active）

    结果按优先级排序。

    Args:
        data_category: 数据分类
        source_type: 数据源类型
        status: 状态

    Returns:
        List[DataSourceResponse]: 数据源配置列表

    Example:
        GET /api/v1/data-sources/config?data_category=DAILY_KLINE&status=active

    """
    try:
        manager = get_config_manager()

        endpoints = manager.list_endpoints(data_category=data_category, source_type=source_type, status=status)

        return [DataSourceResponse(**ep) for ep in endpoints]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出数据源配置失败: {e!s}")


@router.post("/batch", response_model=BatchOperationResponse)
async def batch_operations(batch_request: BatchOperationRequest, current_user: str = Depends(get_current_user)):
    """批量操作数据源配置

    支持:
    - 批量创建
    - 批量更新
    - 批量删除

    每次最多50个操作。

    Args:
        batch_request: 批量操作请求
        current_user: 当前用户

    Returns:
        BatchOperationResponse: 批量操作结果

    Raises:
        400: 操作列表无效或超过50个

    Example:
        POST /api/v1/data-sources/config/batch
        {
            "operations": [
                {"action": "create", "config": {...}},
                {"action": "update", "endpoint_name": "xxx", "updates": {...}},
                {"action": "delete", "endpoint_name": "yyy"}
            ]
        }

    """
    try:
        manager = get_config_manager()

        results = []
        errors = []
        succeeded = 0
        failed = 0

        for op in batch_request.operations:
            action = op.get("action")

            try:
                if action == "create":
                    config = op.get("config", {})
                    result = manager.create_endpoint(
                        endpoint_name=config.get("endpoint_name"),
                        source_name=config.get("source_name"),
                        source_type=config.get("source_type"),
                        data_category=config.get("data_category"),
                        parameters=config.get("parameters", {}),
                        test_parameters=config.get("test_parameters", {}),
                        priority=config.get("priority", 5),
                        description=config.get("description", ""),
                        changed_by=current_user,
                    )

                elif action == "update":
                    endpoint_name = op.get("endpoint_name")
                    updates = op.get("updates", {})
                    result = manager.update_endpoint(
                        endpoint_name=endpoint_name, updates=updates, changed_by=current_user,
                    )

                elif action == "delete":
                    endpoint_name = op.get("endpoint_name")
                    result = manager.delete_endpoint(endpoint_name=endpoint_name, changed_by=current_user)

                else:
                    result = type("obj", (object,), {"success": False, "error": f"未知操作: {action}"})()

                if result.success:
                    succeeded += 1
                else:
                    failed += 1
                    errors.append(result.error)

                results.append(
                    {
                        "action": action,
                        "success": result.success,
                        "endpoint_name": getattr(result, "endpoint_name", None),
                        "error": result.error if not result.success else None,
                    },
                )

            except Exception as e:
                failed += 1
                errors.append(str(e))
                results.append({"action": action, "success": False, "error": str(e)})

        return BatchOperationResponse(
            total=len(batch_request.operations), succeeded=succeeded, failed=failed, results=results, errors=errors,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量操作失败: {e!s}")


@router.get("/{endpoint_name}/versions", response_model=List[VersionInfo])
async def get_version_history(endpoint_name: str, limit: int = Query(10, description="返回数量限制", ge=1, le=100)):
    """获取数据源配置的版本历史

    Args:
        endpoint_name: 端点名称
        limit: 返回数量限制（默认10，最多100）

    Returns:
        List[VersionInfo]: 版本历史列表（倒序）

    Raises:
        404: 端点不存在

    Example:
        GET /api/v1/data-sources/config/akshare.stock_zh_a_hist/versions?limit=20

    """
    try:
        manager = get_config_manager()

        versions = manager.get_version_history(endpoint_name=endpoint_name, limit=limit)

        if not versions:
            raise HTTPException(status_code=404, detail=f"端点不存在或无版本历史: {endpoint_name}")

        return [
            VersionInfo(
                endpoint_name=v.endpoint_name,
                version=v.version,
                change_type=v.change_type,
                changed_by=v.changed_by,
                changed_at=v.changed_at.isoformat(),
                change_summary=v.change_summary,
                metadata=v.metadata,
            )
            for v in versions
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取版本历史失败: {e!s}")


@router.post("/{endpoint_name}/rollback/{version}", response_model=ConfigChangeResponse)
async def rollback_to_version(
    endpoint_name: str, version: int, request: RollbackRequest, current_user: str = Depends(get_current_user),
):
    """回滚数据源配置到指定版本

    功能:
    - 将配置恢复到指定版本的快照
    - 自动创建新的版本记录（restore类型）
    - 保存回滚操作审计日志

    Args:
        endpoint_name: 端点名称
        version: 目标版本号
        request: 回滚请求
        current_user: 当前用户

    Returns:
        ConfigChangeResponse: 回滚结果

    Raises:
        404: 端点或版本不存在

    Example:
        POST /api/v1/data-sources/config/akshare.stock_zh_a_hist/rollback/1

    """
    try:
        manager = get_config_manager()

        result = manager.rollback_to_version(
            endpoint_name=endpoint_name, target_version=version, changed_by=current_user,
        )

        if not result.success:
            if "not found" in result.error:
                raise HTTPException(status_code=404, detail=result.error)
            raise HTTPException(status_code=400, detail=result.error)

        return ConfigChangeResponse(
            success=result.success, endpoint_name=result.endpoint_name, version=result.version, message=result.message,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回滚配置失败: {e!s}")


@router.post("/reload")
async def reload_config(request: ReloadRequest, current_user: str = Depends(get_current_user)):
    """触发配置热重载

    功能:
    - 从YAML文件重新加载配置
    - 通知所有注册的回调函数
    - 记录重载操作审计日志

    Args:
        request: 热重载请求
        current_user: 当前用户

    Returns:
        重载结果统计

    Example:
        POST /api/v1/data-sources/config/reload

    """
    return await reload_config_impl(current_user, get_config_manager)


# ==================== Startup/Shutdown Events ====================


@router.on_event("startup")
async def startup_event():
    """API启动事件"""
    await startup_event_impl()


@router.on_event("shutdown")
async def shutdown_event():
    """API关闭事件"""
    await shutdown_event_impl()
