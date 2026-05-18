"""
API契约管理 API路由
提供契约版本管理、差异检测、验证和同步功能
"""

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Path, Query
from app.core.exceptions import BusinessException
from sqlalchemy.orm import Session

from app.api.contract.schemas import (
    ContractDiffRequest,
    ContractDiffResponse,
    ContractDriftIncidentListResponse,
    ContractDriftIncidentResponse,
    ContractListResponse,
    ContractSyncRequest,
    ContractValidateRequest,
    ContractValidateResponse,
    ContractVersionCreate,
    ContractVersionResponse,
    ContractVersionUpdate,
    SyncResult,
)
from app.api.contract.services.diff_engine import DiffEngine
from app.api.contract.services.drift_incidents import list_contract_drift_incidents as list_tracked_contract_drift_incidents
from app.api.contract.services.validation_alerts import ContractValidationAlertService
from app.api.contract.services.validator import ContractValidator
from app.api.contract.services.version_manager import VersionManager
from app.core.database import get_db
from app.core.responses import UnifiedResponse, create_unified_success_response

router = APIRouter(prefix="/api/contracts", tags=["contract-management"])


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


CONTRACT_OPERATION_ERROR_RESPONSES = {
    404: {
        "description": "指定的契约版本、契约名称或对比目标不存在。",
        "content": {"application/json": {"example": {"detail": "契约版本不存在"}}},
    },
    500: {
        "description": "契约管理操作失败，通常由契约仓库、数据库或 OpenAPI 处理链路异常导致。",
        "content": {"application/json": {"example": {"detail": "contract registry unavailable"}}},
    },
}


CONTRACT_VERSION_CREATE_EXAMPLES = {
    "market_api_version": {
        "summary": "Create a new market API contract version",
        "value": {
            "name": "market-api",
            "version": "1.2.0",
            "spec": {
                "openapi": "3.1.0",
                "info": {"title": "Market API", "version": "1.2.0"},
                "paths": {"/api/v1/market/quotes": {"get": {"summary": "List quotes", "responses": {"200": {}}}}},
            },
            "commit_hash": "abc123def456",
            "author": "codex",
            "description": "Add quote aggregation endpoint",
            "tags": ["market", "v1"],
        },
    }
}

CONTRACT_DIFF_EXAMPLES = {
    "compare_neighbor_versions": {
        "summary": "Compare two contract versions",
        "value": {
            "from_version_id": 12,
            "to_version_id": 13,
        },
    }
}

CONTRACT_VALIDATE_EXAMPLES = {
    "validate_openapi_spec": {
        "summary": "Validate an OpenAPI specification",
        "value": {
            "spec": {
                "openapi": "3.1.0",
                "info": {"title": "Trading API", "version": "2.0.0"},
                "paths": {"/api/v1/trades": {"get": {"summary": "List trades", "responses": {"200": {}}}}},
            },
            "check_breaking_changes": True,
            "compare_to_version_id": 11,
        },
    }
}

CONTRACT_SYNC_EXAMPLES = {
    "sync_code_to_db": {
        "summary": "Sync generated code contract into the registry",
        "value": {
            "name": "trading-runtime",
            "direction": "code_to_db",
            "commit_hash": "fedcba654321",
            "author": "codex",
            "description": "Sync the latest trading runtime OpenAPI contract",
        },
    }
}

CONTRACT_SYNC_ERROR_RESPONSE = {
    500: {
        "description": "Contract sync report generation failed because the OpenAPI scanner or registry backend is unavailable.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "failed to scan FastAPI application routes",
                }
            }
        },
    }
}

CONTRACT_VERSION_UPDATE_EXAMPLES = {
    "annotate_version": {
        "summary": "Update version metadata",
        "value": {
            "description": "Mark this version as the baseline for mobile clients.",
            "tags": ["baseline", "mobile"],
        },
    }
}

CONTRACT_LIST_ERROR_RESPONSE = {
    500: {
        "description": "Contract list retrieval failed because the contract registry database is unavailable.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "failed to read contract registry",
                }
            }
        },
    }
}

CONTRACT_VERSION_DETAIL_RESPONSES = _success_response_spec(
    "契约版本详情",
    {
        "id": 13,
        "name": "market-api",
        "version": "1.2.0",
        "spec": {
            "openapi": "3.1.0",
            "info": {"title": "Market API", "version": "1.2.0"},
            "paths": {"/api/v1/market/quotes": {"get": {"summary": "List quotes", "responses": {"200": {}}}}},
        },
        "commit_hash": "abc123def456",
        "author": "codex",
        "description": "Add quote aggregation endpoint",
        "tags": ["market", "v1"],
        "created_at": "2026-04-06T15:30:00",
        "is_active": True,
    },
)

CONTRACT_VERSION_LIST_RESPONSES = _success_response_spec(
    "契约版本列表",
    [
        {
            "id": 13,
            "name": "market-api",
            "version": "1.2.0",
            "spec": {
                "openapi": "3.1.0",
                "info": {"title": "Market API", "version": "1.2.0"},
                "paths": {"/api/v1/market/quotes": {"get": {"summary": "List quotes", "responses": {"200": {}}}}},
            },
            "commit_hash": "abc123def456",
            "author": "codex",
            "description": "Add quote aggregation endpoint",
            "tags": ["market", "v1"],
            "created_at": "2026-04-06T15:30:00",
            "is_active": True,
        }
    ],
)

CONTRACT_VERSION_ACTIVATE_RESPONSES = _success_response_spec(
    "契约版本激活结果",
    {
        "success": True,
        "message": "版本已激活",
    },
)

CONTRACT_VERSION_DELETE_RESPONSES = _success_response_spec(
    "契约版本删除结果",
    {
        "success": True,
        "message": "版本已删除",
    },
)

CONTRACT_LIST_RESPONSES = {
    **CONTRACT_LIST_ERROR_RESPONSE,
    **_success_response_spec(
        "契约列表",
        {
            "contracts": [
                {
                    "name": "market-api",
                    "latest_version": "1.2.0",
                    "total_versions": 3,
                    "last_updated": "2026-04-06T15:30:00",
                    "description": "市场数据对外契约",
                    "tags": ["market", "public"],
                }
            ],
            "total": 1,
        },
    ),
}

CONTRACT_SYNC_REPORT_RESPONSES = {
    **CONTRACT_SYNC_ERROR_RESPONSE,
    **_success_response_spec(
        "契约同步报告",
        {
            "contracts": [
                {
                    "name": "trading-runtime",
                    "detected_endpoints": 12,
                    "last_synced_version": "2.1.0",
                }
            ],
            "generated_at": "2026-04-06T15:30:00",
        },
    ),
}

CONTRACT_VERSION_CREATE_RESPONSES = {
    **CONTRACT_OPERATION_ERROR_RESPONSES,
    **_success_response_spec(
        "创建契约版本成功。",
        {
            "id": 14,
            "name": "trading-runtime",
            "version": "2.2.0",
            "spec": {
                "openapi": "3.1.0",
                "info": {"title": "Trading Runtime API", "version": "2.2.0"},
                "paths": {"/api/trading/status": {"get": {"summary": "Get trading runtime status", "responses": {"200": {}}}}},
            },
            "commit_hash": "fedcba65",
            "author": "codex",
            "description": "Add runtime control examples",
            "tags": ["runtime", "v2"],
            "created_at": "2026-04-08T11:30:00",
            "is_active": False,
        },
    ),
}

CONTRACT_VERSION_UPDATE_RESPONSES = {
    **CONTRACT_OPERATION_ERROR_RESPONSES,
    **_success_response_spec(
        "更新契约版本元数据成功。",
        {
            "id": 14,
            "name": "trading-runtime",
            "version": "2.2.0",
            "spec": {
                "openapi": "3.1.0",
                "info": {"title": "Trading Runtime API", "version": "2.2.0"},
                "paths": {"/api/trading/status": {"get": {"summary": "Get trading runtime status", "responses": {"200": {}}}}},
            },
            "commit_hash": "fedcba65",
            "author": "codex",
            "description": "Mark runtime contract as reviewed baseline.",
            "tags": ["baseline", "runtime"],
            "created_at": "2026-04-08T11:30:00",
            "is_active": False,
        },
    ),
}

CONTRACT_DIFF_RESPONSES = {
    **CONTRACT_OPERATION_ERROR_RESPONSES,
    **_success_response_spec(
        "契约版本差异比较结果。",
        {
            "from_version": "2.1.0",
            "to_version": "2.2.0",
            "total_changes": 2,
            "breaking_changes": 0,
            "non_breaking_changes": 2,
            "diffs": [
                {
                    "change_type": "added",
                    "path": "paths./api/trading/start.post.responses.200",
                    "old_value": None,
                    "new_value": {"description": "交易运行时会话启动结果"},
                    "is_breaking": False,
                    "description": "Added success example for trading runtime start endpoint",
                }
            ],
            "summary": "2 non-breaking changes detected between 2.1.0 and 2.2.0",
        },
    ),
}

CONTRACT_VALIDATE_RESPONSES = {
    **CONTRACT_OPERATION_ERROR_RESPONSES,
    **_success_response_spec(
        "OpenAPI 契约验证结果。",
        {
            "valid": True,
            "error_count": 0,
            "warning_count": 1,
            "results": [
                {
                    "valid": True,
                    "category": "warning",
                    "path": "paths./api/v1/trades.get.responses.200",
                    "message": "Response example is recommended for stable consumer integration",
                    "suggestion": "Add a concrete 200 response example before release",
                }
            ],
        },
    ),
}

CONTRACT_DRIFT_INCIDENT_RESPONSES = {
    **CONTRACT_OPERATION_ERROR_RESPONSES,
    **_success_response_spec(
        "契约漂移事件列表。",
        {"success": True, "code": 200, "message": "契约漂移事件获取成功", "data": {"incidents": [], "total": 0, "open_count": 0}},
    ),
}

CONTRACT_SYNC_RESPONSES = {
    **CONTRACT_OPERATION_ERROR_RESPONSES,
    **_success_response_spec(
        "契约同步执行结果。",
        {
            "success": True,
            "version_id": 14,
            "version": "2026.04.08.1130",
            "direction": "code_to_db",
            "changes": {
                "endpoints_added": 12,
                "sync_direction": "code_to_db",
                "generated_from": "FastAPI routes",
            },
            "message": "Successfully synced 12 endpoints from code to database",
        },
    ),
}


# ==================== 契约版本管理 ====================


@router.post(
    "/versions",
    response_model=UnifiedResponse[ContractVersionResponse],
    summary="创建契约版本",
    description="创建新的契约版本记录，并把 OpenAPI 规范、作者、提交号和标签一起写入版本仓库。",
    responses=CONTRACT_VERSION_CREATE_RESPONSES,
)
async def create_version(
    version_data: ContractVersionCreate = Body(..., openapi_examples=CONTRACT_VERSION_CREATE_EXAMPLES),
    db: Session = Depends(get_db),
):
    """
    创建新的契约版本

    - **name**: 契约名称 (如: market-api, trade-api)
    - **version**: 版本号 (如: 1.0.0)
    - **spec**: OpenAPI规范内容
    - **commit_hash**: Git commit hash (可选)
    - **author**: 作者 (可选)
    - **description**: 版本描述 (可选)
    - **tags**: 版本标签 (可选)
    """
    return create_unified_success_response(data=VersionManager.create_version(db, version_data), message="契约版本创建成功")


@router.get(
    "/versions/{version_id}",
    response_model=UnifiedResponse[ContractVersionResponse],
    responses=CONTRACT_VERSION_DETAIL_RESPONSES,
)
async def get_version(
    version_id: int = Path(..., description="Unique identifier of the contract version to retrieve."),
    db: Session = Depends(get_db),
):
    """获取指定契约版本及其当前持久化的 OpenAPI 规范详情。"""
    version = VersionManager.get_version(db, version_id)
    if not version:
        raise BusinessException(status_code=404, detail="契约版本不存在")
    return create_unified_success_response(data=version, message="契约版本获取成功")


@router.get(
    "/versions/{name}/active",
    response_model=UnifiedResponse[ContractVersionResponse],
    responses=CONTRACT_VERSION_DETAIL_RESPONSES,
)
async def get_active_version(
    name: str = Path(..., description="Contract name whose active version should be returned."),
    db: Session = Depends(get_db),
):
    """获取指定契约名称当前处于激活状态的版本元数据。"""
    version = VersionManager.get_active_version(db, name)
    if not version:
        raise BusinessException(status_code=404, detail="契约不存在或无激活版本")
    return create_unified_success_response(data=version, message="激活契约版本获取成功")


@router.get(
    "/versions",
    response_model=UnifiedResponse[list[ContractVersionResponse]],
    responses=CONTRACT_VERSION_LIST_RESPONSES,
)
async def list_versions(
    name: str = Query(None, description="Optional contract name filter used to scope the version list."),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of contract versions returned in one page."),
    offset: int = Query(0, ge=0, description="Zero-based offset for paginating the version list."),
    db: Session = Depends(get_db),
):
    """按契约名称和分页条件列出当前可查询的契约版本集合。"""
    return create_unified_success_response(data=VersionManager.list_versions(db, name, limit, offset), message="契约版本列表获取成功")


@router.put(
    "/versions/{version_id}",
    response_model=UnifiedResponse[ContractVersionResponse],
    summary="更新契约版本元数据",
    description="更新指定契约版本的描述、标签等元数据，不修改该版本对应的 OpenAPI 规范正文。",
    responses=CONTRACT_VERSION_UPDATE_RESPONSES,
)
async def update_version(
    version_id: int = Path(..., description="Unique identifier of the contract version to update."),
    update_data: ContractVersionUpdate = Body(..., openapi_examples=CONTRACT_VERSION_UPDATE_EXAMPLES),
    db: Session = Depends(get_db),
):
    """更新契约版本的描述、标签和其他补充元数据信息。"""
    version = VersionManager.update_version(db, version_id, update_data)
    if not version:
        raise BusinessException(status_code=404, detail="契约版本不存在")
    return create_unified_success_response(data=version, message="契约版本更新成功")


@router.post(
    "/versions/{version_id}/activate",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=CONTRACT_VERSION_ACTIVATE_RESPONSES,
)
async def activate_version(
    version_id: int = Path(..., description="Unique identifier of the contract version that should become active."),
    db: Session = Depends(get_db),
):
    """将指定契约版本设置为当前对外生效的激活版本。"""
    success = VersionManager.activate_version(db, version_id)
    if not success:
        raise BusinessException(status_code=404, detail="契约版本不存在")
    return create_unified_success_response(data={"success": True, "version_id": version_id}, message="版本已激活")


@router.delete(
    "/versions/{version_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=CONTRACT_VERSION_DELETE_RESPONSES,
)
async def delete_version(
    version_id: int = Path(..., description="Unique identifier of the contract version to delete."),
    db: Session = Depends(get_db),
):
    """删除指定的契约版本及其关联的版本记录与元数据。"""
    success = VersionManager.delete_version(db, version_id)
    if not success:
        raise BusinessException(status_code=404, detail="契约版本不存在")
    return create_unified_success_response(data={"success": True, "version_id": version_id}, message="版本已删除")


# ==================== 契约列表 ====================


@router.get("/contracts", response_model=UnifiedResponse[ContractListResponse], responses=CONTRACT_LIST_RESPONSES)
async def list_contracts(db: Session = Depends(get_db)):
    """列出所有已登记契约及其最新版本和元数据信息。"""
    contracts = VersionManager.list_contracts(db)
    response = ContractListResponse(contracts=contracts, total=len(contracts))
    return create_unified_success_response(data=response, message="契约列表获取成功")


# ==================== 契约差异检测 ====================


@router.post(
    "/diff",
    response_model=UnifiedResponse[ContractDiffResponse],
    summary="比较契约版本差异",
    description="比较两个契约版本的差异，输出总变更数、破坏性变更数以及逐项 diff 明细。",
    responses=CONTRACT_DIFF_RESPONSES,
)
async def compare_versions(
    request: ContractDiffRequest = Body(..., openapi_examples=CONTRACT_DIFF_EXAMPLES),
    db: Session = Depends(get_db),
):
    """
    对比两个契约版本的差异

    - **from_version_id**: 源版本ID
    - **to_version_id**: 目标版本ID

    返回差异详情，包括：
    - 总变更数
    - 破坏性变更数
    - 非破坏性变更数
    - 详细差异列表
    """
    # 获取两个版本
    from_version = VersionManager.get_version(db, request.from_version_id)
    to_version = VersionManager.get_version(db, request.to_version_id)

    if not from_version:
        raise BusinessException(status_code=404, detail="源版本不存在")
    if not to_version:
        raise BusinessException(status_code=404, detail="目标版本不存在")

    # 对比差异
    diff_result = DiffEngine.compare_versions(
        from_spec=from_version.spec,
        to_spec=to_version.spec,
        from_version=from_version.version,
        to_version=to_version.version,
    )

    return create_unified_success_response(data=diff_result, message="契约差异比较完成")


# ==================== 契约验证 ====================


@router.post(
    "/validate",
    response_model=UnifiedResponse[ContractValidateResponse],
    summary="验证契约规范",
    description="验证待检查的 OpenAPI 规范，并在需要时与指定历史版本比较破坏性变更。",
    responses=CONTRACT_VALIDATE_RESPONSES,
)
async def validate_contract(request: ContractValidateRequest = Body(..., openapi_examples=CONTRACT_VALIDATE_EXAMPLES)):
    """
    验证OpenAPI规范

    - **spec**: 待验证的OpenAPI规范
    - **check_breaking_changes**: 是否检查破坏性变更
    - **compare_to_version_id**: 对比的版本ID (可选)

    返回验证结果，包括：
    - 是否通过验证
    - 错误数
    - 警告数
    - 详细验证结果
    """
    compare_to_spec = None

    # 如果需要对比破坏性变更
    if request.check_breaking_changes and request.compare_to_version_id:
        from app.api.contract.services.version_manager import VersionManager
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            old_version = VersionManager.get_version(db, request.compare_to_version_id)
            if old_version:
                compare_to_spec = old_version.spec
        finally:
            db.close()

    # 验证契约
    validation_result = ContractValidator.validate(
        spec=request.spec,
        check_breaking_changes=request.check_breaking_changes,
        compare_to_spec=compare_to_spec,
    )
    alert_service = ContractValidationAlertService()
    await alert_service.dispatch_alerts(alert_service.build_alerts(validation_result))

    return create_unified_success_response(data=validation_result, message="契约验证完成")


@router.get(
    "/drift/incidents",
    response_model=UnifiedResponse[ContractDriftIncidentListResponse],
    summary="查询契约漂移事件",
    description="返回当前进程内由契约验证记录的 drift incident，用于治理看板和后续告警接线。",
    responses=CONTRACT_DRIFT_INCIDENT_RESPONSES,
)
async def list_contract_drift_incidents(
    limit: int = Query(default=50, ge=1, le=200, description="Maximum number of drift incidents to return"),
):
    """查询契约验证期间记录的漂移事件。"""
    incidents = list_tracked_contract_drift_incidents(limit=limit)
    incident_responses = [
        ContractDriftIncidentResponse(
            incident_id=f"contract-drift-{uuid.uuid5(uuid.NAMESPACE_URL, f'{incident.kind}:{incident.path}:{incident.message}:{incident.recorded_at.isoformat()}').hex}",
            detected_at=incident.recorded_at,
            kind=incident.kind,
            severity=incident.severity,
            path=incident.path,
            message=incident.message,
            suggestion=incident.suggestion,
            status=str(incident.metadata.get("status", "open")),
            metadata=incident.metadata,
        )
        for incident in incidents
    ]
    response = ContractDriftIncidentListResponse(
        incidents=incident_responses,
        total=len(incident_responses),
        open_count=sum(1 for incident in incident_responses if incident.status == "open"),
    )
    return create_unified_success_response(data=response, message="契约漂移事件获取成功")


# ==================== 契约同步 ====================


@router.post(
    "/sync",
    response_model=UnifiedResponse[SyncResult],
    summary="同步契约",
    description="在代码与契约仓库之间同步指定契约，可选择 code_to_db 或 db_to_code 方向。",
    responses=CONTRACT_SYNC_RESPONSES,
)
async def sync_contract(
    request: ContractSyncRequest = Body(..., openapi_examples=CONTRACT_SYNC_EXAMPLES),
    db: Session = Depends(get_db),
):
    """
    同步契约

    - **name**: 契约名称
    - **direction**: 同步方向 (code_to_db | db_to_code)
    - **commit_hash**: Git commit hash (可选)
    - **author**: 作者 (可选)
    - **description**: 版本描述 (可选)

    返回同步结果

    Code-to-DB: 从 FastAPI 代码生成 OpenAPI Spec 并保存到数据库
    DB-to-Code: 从数据库导出 OpenAPI Spec 到文件
    """

    result = VersionManager.sync(
        db=db,
        contract_name=request.name,
        direction=request.direction,
        commit_hash=request.commit_hash,
        author=request.author,
        description=request.description,
    )

    return create_unified_success_response(data=result, message="契约同步完成")


@router.get(
    "/sync/report",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=CONTRACT_SYNC_REPORT_RESPONSES,
)
async def get_sync_report(db: Session = Depends(get_db)):
    """
    获取同步报告

    返回当前可以同步的端点信息
    """
    from app.api.contract.services.openapi_generator import OpenAPIGenerator
    from app.main import app as fastapi_app

    generator = OpenAPIGenerator()
    generator.scan_app(fastapi_app)
    report = generator.get_sync_report()

    return create_unified_success_response(data=report, message="契约同步报告获取成功")
