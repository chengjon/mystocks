"""
数据源配置CRUD API (完全符合API契约管理规范)

提供数据源配置的完整CRUD操作、版本管理和热重载功能。

核心功能:
1. 创建/更新/删除数据源配置
2. 查询配置和版本历史
3. 配置回滚到任意版本
4. 批量操作支持
5. 配置热重载

契约管理:
- ✅ 使用统一响应格式 (UnifiedResponse)
- ✅ 支持API版本管理
- ✅ 支持OpenAPI规范导出
- ✅ 符合项目API契约标准
- ✅ 完整的错误处理和日志记录
- ✅ 自动request_id追踪

Author: Claude Code (Main CLI)
Date: 2026-01-09
Version: 1.0.0
API Version: v1
Contract Version: 1.0
"""

import logging
from typing import Optional

from fastapi import Body, Depends, HTTPException, Path, Query, Request


# 导入统一响应格式
from app.api.data_source_config_schemas import (
    BatchOperationRequest,
    DataSourceCreate,
    DataSourceUpdate,
    ReloadRequest,
    RollbackRequest,
)
from app.core.config import settings
from app.core.responses import (
    BusinessCode,
    UnifiedResponse,
    create_unified_error_response,
    create_unified_success_response,
    not_found,
)

logger = logging.getLogger(__name__)

# Keep legacy module-level exports used by file-level contract tests and callers.
_COMPAT_EXPORTS = (HTTPException, settings)


from ._data_source_config_responses import (
    BATCH_OPERATION_EXAMPLES,
    DATA_SOURCE_CONFIG_BATCH_RESPONSES,
    DATA_SOURCE_CONFIG_CREATE_RESPONSES,
    DATA_SOURCE_CONFIG_DELETE_RESPONSES,
    DATA_SOURCE_CONFIG_DETAIL_RESPONSES,
    DATA_SOURCE_CONFIG_LIST_RESPONSES,
    DATA_SOURCE_CONFIG_RELOAD_RESPONSES,
    DATA_SOURCE_CONFIG_ROLLBACK_RESPONSES,
    DATA_SOURCE_CONFIG_UPDATE_RESPONSES,
    DATA_SOURCE_CONFIG_VERSIONS_RESPONSES,
    DATA_SOURCE_CREATE_EXAMPLES,
    DATA_SOURCE_UPDATE_EXAMPLES,
    RELOAD_REQUEST_EXAMPLES,
    ROLLBACK_REQUEST_EXAMPLES,
    get_config_manager,
    get_current_user,
    router,
)

def handle_config_error(error: str, request_id: Optional[str] = None) -> UnifiedResponse:
    """处理配置错误并返回统一响应"""
    if "already exists" in error:
        return create_unified_error_response(
            code=BusinessCode.CONFLICT,
            message="数据源配置已存在",
            error_code="DUPLICATE_ENDPOINT",
            request_id=request_id,
        )
    elif "not found" in error:
        return create_unified_error_response(
            code=BusinessCode.NOT_FOUND,
            message="数据源配置不存在",
            error_code="ENDPOINT_NOT_FOUND",
            request_id=request_id,
        )
    else:
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=error,
            error_code="CONFIG_ERROR",
            request_id=request_id,
        )


# ==================== API Endpoints ====================


@router.post("/", response_model=UnifiedResponse, status_code=201, responses=DATA_SOURCE_CONFIG_CREATE_RESPONSES)
async def create_data_source(
    request: Request,
    config: DataSourceCreate = Body(..., openapi_examples=DATA_SOURCE_CREATE_EXAMPLES),
    current_user: str = Depends(get_current_user),
):
    """
    创建新的数据源配置

    创建全新的数据源端点配置，自动记录版本历史（版本1）。
    验证配置有效性，保存到YAML文件和PostgreSQL数据库。

    - **endpoint_name**: 端点名称（唯一标识）
    - **source_name**: 数据源名称（如: akshare, tushare）
    - **source_type**: 数据源类型
    - **data_category**: 数据分类（DAILY_KLINE, MINUTE_KLINE等）
    - **parameters**: 参数定义（JSON格式）
    - **test_parameters**: 测试参数（JSON格式）
    - **priority**: 优先级（1-10，数字越小优先级越高）

    Returns:
        UnifiedResponse: 包含endpoint_name和version

    Raises:
        409: 端点名称已存在
        400: 配置验证失败
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info("Creating data source: {config.endpoint_name}", extra={"request_id": request_id})

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
        logger.error("Failed to create data source: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"创建数据源配置失败: {str(e)}",
            error_code="CREATE_ENDPOINT_ERROR",
            request_id=request_id,
        )


@router.put("/{endpoint_name}", response_model=UnifiedResponse, responses=DATA_SOURCE_CONFIG_UPDATE_RESPONSES)
async def update_data_source(
    request: Request,
    endpoint_name: str = Path(..., description="需要更新的数据源端点名称。"),
    updates: DataSourceUpdate = Body(..., openapi_examples=DATA_SOURCE_UPDATE_EXAMPLES),
    current_user: str = Depends(get_current_user),
):
    """
    更新数据源配置

    更新现有数据源配置的字段，自动记录版本历史。
    保存变更前后的值到元数据。

    - **priority**: 优先级（1-10）
    - **data_quality_score**: 质量评分（0-10）
    - **status**: 状态（active, maintenance, deprecated）
    - **description**: 描述信息

    Returns:
        UnifiedResponse: 包含新版本号

    Raises:
        404: 端点不存在
        400: 无有效更新字段
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info("Updating data source: {endpoint_name}", extra={"request_id": request_id})

    try:
        manager = get_config_manager()

        # 构建更新字典
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
            return create_unified_error_response(
                code=BusinessCode.BAD_REQUEST,
                message="无有效更新字段",
                error_code="NO_UPDATES",
                request_id=request_id,
            )

        result = manager.update_endpoint(endpoint_name=endpoint_name, updates=update_dict, changed_by=current_user)

        if not result.success:
            return handle_config_error(result.error, request_id)

        return create_unified_success_response(
            data={
                "endpoint_name": result.endpoint_name,
                "version": result.version,
            },
            message=f"数据源配置更新成功: {result.endpoint_name}",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to update data source {endpoint_name}: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"更新数据源配置失败: {str(e)}",
            error_code="UPDATE_ENDPOINT_ERROR",
            request_id=request_id,
        )


@router.delete("/{endpoint_name}", response_model=UnifiedResponse, responses=DATA_SOURCE_CONFIG_DELETE_RESPONSES)
async def delete_data_source(
    request: Request,
    endpoint_name: str = Path(..., description="需要删除的数据源端点名称。"),
    current_user: str = Depends(get_current_user),
):
    """
    删除数据源配置

    删除数据源配置（软删除），记录版本历史，可通过回滚恢复。

    Returns:
        UnifiedResponse: 删除结果

    Raises:
        404: 端点不存在
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info("Deleting data source: {endpoint_name}", extra={"request_id": request_id})

    try:
        manager = get_config_manager()

        result = manager.delete_endpoint(endpoint_name=endpoint_name, changed_by=current_user)

        if not result.success:
            return handle_config_error(result.error, request_id)

        return create_unified_success_response(
            data={
                "endpoint_name": result.endpoint_name,
                "version": result.version,
            },
            message=f"数据源配置删除成功: {endpoint_name}",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to delete data source {endpoint_name}: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"删除数据源配置失败: {str(e)}",
            error_code="DELETE_ENDPOINT_ERROR",
            request_id=request_id,
        )


@router.get("/{endpoint_name}", response_model=UnifiedResponse, responses=DATA_SOURCE_CONFIG_DETAIL_RESPONSES)
async def get_data_source(
    request: Request,
    endpoint_name: str = Path(..., description="需要查询详情的数据源端点名称。"),
):
    """
    获取单个数据源配置

    返回指定数据源的完整配置信息。

    - **endpoint_name**: 端点名称

    Returns:
        UnifiedResponse: 包含完整配置信息

    Raises:
        404: 端点不存在
    """
    request_id = getattr(request.state, "request_id", None)

    try:
        manager = get_config_manager()
        config = manager.get_endpoint(endpoint_name)

        if not config:
            return not_found(resource=f"数据源配置: {endpoint_name}")

        return create_unified_success_response(
            data=config,
            message="获取数据源配置成功",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to get data source {endpoint_name}: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"获取数据源配置失败: {str(e)}",
            error_code="GET_ENDPOINT_ERROR",
            request_id=request_id,
        )


@router.get("/", response_model=UnifiedResponse, responses=DATA_SOURCE_CONFIG_LIST_RESPONSES)
async def list_data_sources(
    request: Request,
    data_category: Optional[str] = Query(None, description="数据分类"),
    source_type: Optional[str] = Query(None, description="数据源类型"),
    status: Optional[str] = Query("active", description="状态（active, maintenance, deprecated）"),
):
    """
    列出数据源配置

    支持按以下条件过滤:
    - **data_category**: 数据分类
    - **source_type**: 数据源类型
    - **status**: 状态（默认: active）

    结果按优先级排序。

    Returns:
        UnifiedResponse: 包含数据源配置列表
    """
    request_id = getattr(request.state, "request_id", None)

    try:
        manager = get_config_manager()
        endpoints = manager.list_endpoints(data_category=data_category, source_type=source_type, status=status)

        return create_unified_success_response(
            data={
                "endpoints": endpoints,
                "total": len(endpoints),
            },
            message=f"获取数据源列表成功，共 {len(endpoints)} 个",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to list data sources: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"列出数据源配置失败: {str(e)}",
            error_code="LIST_ENDPOINTS_ERROR",
            request_id=request_id,
        )


@router.post("/batch", response_model=UnifiedResponse, responses=DATA_SOURCE_CONFIG_BATCH_RESPONSES)
async def batch_operations(
    request: Request,
    batch_request: BatchOperationRequest = Body(..., openapi_examples=BATCH_OPERATION_EXAMPLES),
    current_user: str = Depends(get_current_user),
):
    """
    批量操作数据源配置

    支持批量创建、更新、删除操作，每次最多50个操作。

    Returns:
        UnifiedResponse: 包含批量操作结果统计

    Raises:
        400: 操作列表无效或超过50个
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info("Batch operations: {len(batch_request.operations)} items", extra={"request_id": request_id})

    try:
        manager = get_config_manager()

        results = []
        succeeded = 0
        failed = 0

        for op in batch_request.operations:
            action = op.action

            try:
                if action == "create":
                    if not op.config:
                        raise ValueError("config is required for create action")
                    result = manager.create_endpoint(
                        endpoint_name=op.config.endpoint_name,
                        source_name=op.config.source_name,
                        source_type=op.config.source_type,
                        data_category=op.config.data_category,
                        parameters=op.config.parameters,
                        test_parameters=op.config.test_parameters,
                        priority=op.config.priority,
                        description=op.config.description,
                        changed_by=current_user,
                    )

                elif action == "update":
                    if not op.endpoint_name:
                        raise ValueError("endpoint_name is required for update action")
                    updates_dict = {}
                    if op.updates:
                        if op.updates.priority is not None:
                            updates_dict["priority"] = op.updates.priority
                        if op.updates.data_quality_score is not None:
                            updates_dict["data_quality_score"] = op.updates.data_quality_score
                        if op.updates.status is not None:
                            updates_dict["status"] = op.updates.status
                        if op.updates.description is not None:
                            updates_dict["description"] = op.updates.description
                    result = manager.update_endpoint(
                        endpoint_name=op.endpoint_name, updates=updates_dict, changed_by=current_user
                    )

                elif action == "delete":
                    if not op.endpoint_name:
                        raise ValueError("endpoint_name is required for delete action")
                    result = manager.delete_endpoint(endpoint_name=op.endpoint_name, changed_by=current_user)

                else:
                    result = type("obj", (object,), {"success": False, "error": f"Unknown action: {action}"})()

                if result.success:
                    succeeded += 1
                else:
                    failed += 1

                results.append(
                    {
                        "action": action,
                        "success": result.success,
                        "endpoint_name": getattr(result, "endpoint_name", None),
                        "version": getattr(result, "version", None),
                        "error": None if result.success else result.error,
                    }
                )

            except Exception as e:
                failed += 1
                results.append({"action": action, "success": False, "error": str(e)})

        return create_unified_success_response(
            data={
                "total": len(batch_request.operations),
                "succeeded": succeeded,
                "failed": failed,
                "results": results,
            },
            message=f"批量操作完成: 成功 {succeeded}/{len(batch_request.operations)}",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to execute batch operations: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"批量操作失败: {str(e)}",
            error_code="BATCH_OPERATION_ERROR",
            request_id=request_id,
        )


@router.get("/{endpoint_name}/versions", response_model=UnifiedResponse, responses=DATA_SOURCE_CONFIG_VERSIONS_RESPONSES)
async def get_version_history(
    request: Request,
    endpoint_name: str = Path(..., description="需要查询版本历史的数据源端点名称。"),
    limit: int = Query(10, description="返回数量限制", ge=1, le=100),
):
    """
    获取数据源配置的版本历史

    返回指定数据源的所有版本历史，按版本号倒序排列。

    - **endpoint_name**: 端点名称
    - **limit**: 返回数量限制（默认10，最多100）

    Returns:
        UnifiedResponse: 包含版本历史列表

    Raises:
        404: 端点不存在或无版本历史
    """
    request_id = getattr(request.state, "request_id", None)

    try:
        manager = get_config_manager()
        versions = manager.get_version_history(endpoint_name=endpoint_name, limit=limit)

        if not versions:
            return not_found(resource=f"端点或版本历史: {endpoint_name}")

        # 转换为字典格式
        versions_list = [
            {
                "endpoint_name": v.endpoint_name,
                "version": v.version,
                "change_type": v.change_type,
                "changed_by": v.changed_by,
                "changed_at": v.changed_at.isoformat(),
                "change_summary": v.change_summary,
                "metadata": v.metadata,
            }
            for v in versions
        ]

        return create_unified_success_response(
            data={
                "endpoint_name": endpoint_name,
                "versions": versions_list,
                "total": len(versions_list),
            },
            message=f"获取版本历史成功，共 {len(versions_list)} 个版本",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to get version history for {endpoint_name}: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"获取版本历史失败: {str(e)}",
            error_code="GET_VERSIONS_ERROR",
            request_id=request_id,
        )


@router.post(
    "/{endpoint_name}/rollback/{version}",
    response_model=UnifiedResponse,
    responses=DATA_SOURCE_CONFIG_ROLLBACK_RESPONSES,
)
async def rollback_to_version(
    request: Request,
    endpoint_name: str = Path(..., description="需要回滚的数据源端点名称。"),
    version: int = Path(..., description="目标回滚版本号。", ge=1),
    rollback_req: RollbackRequest = Body(..., openapi_examples=ROLLBACK_REQUEST_EXAMPLES),
    current_user: str = Depends(get_current_user),
):
    """
    回滚数据源配置到指定版本

    将配置恢复到指定版本的快照，自动创建新的版本记录（restore类型）。

    - **endpoint_name**: 端点名称
    - **version**: 目标版本号

    Returns:
        UnifiedResponse: 回滚结果

    Raises:
        404: 端点或版本不存在
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info("Rolling back {endpoint_name} to version {version}", extra={"request_id": request_id})

    try:
        manager = get_config_manager()
        result = manager.rollback_to_version(
            endpoint_name=endpoint_name, target_version=version, changed_by=current_user
        )

        if not result.success:
            return handle_config_error(result.error, request_id)

        return create_unified_success_response(
            data={
                "endpoint_name": result.endpoint_name,
                "version": result.version,
                "restored_from_version": version,
            },
            message=f"回滚成功: {endpoint_name} → 版本 {version}",
            request_id=request_id,
        )

    except Exception as e:
        logger.error(
            f"Failed to rollback {endpoint_name} to version {version}: {str(e)}", extra={"request_id": request_id}
        )
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"回滚配置失败: {str(e)}",
            error_code="ROLLBACK_ERROR",
            request_id=request_id,
        )


@router.post("/reload", response_model=UnifiedResponse, responses=DATA_SOURCE_CONFIG_RELOAD_RESPONSES)
async def reload_config(
    request: Request,
    reload_req: ReloadRequest = Body(..., openapi_examples=RELOAD_REQUEST_EXAMPLES),
    current_user: str = Depends(get_current_user),
):
    """
    触发配置热重载

    从YAML文件重新加载配置，通知所有注册的回调函数。

    Returns:
        UnifiedResponse: 重载结果统计
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info("Reloading data source configurations", extra={"request_id": request_id})

    try:
        manager = get_config_manager()
        result = manager.reload_config(changed_by=current_user)

        return create_unified_success_response(
            data={
                "old_count": result["old_count"],
                "new_count": result["new_count"],
                "duration": result["duration"],
                "reloaded_at": result["reloaded_at"],
            },
            message=f"配置热重载成功: {result['old_count']} → {result['new_count']} 个端点",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to reload config: {str(e)}", extra={"request_id": request_id})
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=f"配置热重载失败: {str(e)}",
            error_code="RELOAD_ERROR",
            request_id=request_id,
        )


# ==================== Lifecycle Events ====================


@router.on_event("startup")
async def startup_event():
    """API启动事件"""
    logger.info("✅ 数据源配置CRUD API已启动 (符合契约管理规范)")


@router.on_event("shutdown")
async def shutdown_event():
    """API关闭事件"""
    logger.info("👋 数据源配置CRUD API已关闭")
