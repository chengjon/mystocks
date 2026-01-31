"""
API契约管理 API路由
提供契约版本管理、差异检测、验证和同步功能
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.contract.schemas import (
    ContractDiffRequest,
    ContractDiffResponse,
    ContractListResponse,
    ContractSyncRequest,
    ContractValidateRequest,
    ContractValidateResponse,
    ContractVersionCreate,
    ContractVersionResponse,
    ContractVersionUpdate,
)
from app.api.contract.services.diff_engine import DiffEngine
from app.api.contract.services.validator import ContractValidator
from app.api.contract.services.version_manager import VersionManager
from app.core.database import get_db

router = APIRouter(prefix="/api/contracts", tags=["contract-management"])


# ==================== 契约版本管理 ====================


@router.post("/versions", response_model=ContractVersionResponse)
async def create_version(version_data: ContractVersionCreate, db: Session = Depends(get_db)):
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
    return VersionManager.create_version(db, version_data)


@router.get("/versions/{version_id}", response_model=ContractVersionResponse)
async def get_version(version_id: int, db: Session = Depends(get_db)):
    """获取指定契约版本"""
    version = VersionManager.get_version(db, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="契约版本不存在")
    return version


@router.get("/versions/{name}/active", response_model=ContractVersionResponse)
async def get_active_version(name: str, db: Session = Depends(get_db)):
    """获取契约的当前激活版本"""
    version = VersionManager.get_active_version(db, name)
    if not version:
        raise HTTPException(status_code=404, detail="契约不存在或无激活版本")
    return version


@router.get("/versions", response_model=List[ContractVersionResponse])
async def list_versions(name: str = None, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """列出版本"""
    return VersionManager.list_versions(db, name, limit, offset)


@router.put("/versions/{version_id}", response_model=ContractVersionResponse)
async def update_version(version_id: int, update_data: ContractVersionUpdate, db: Session = Depends(get_db)):
    """更新契约版本"""
    version = VersionManager.update_version(db, version_id, update_data)
    if not version:
        raise HTTPException(status_code=404, detail="契约版本不存在")
    return version


@router.post("/versions/{version_id}/activate")
async def activate_version(version_id: int, db: Session = Depends(get_db)):
    """激活指定版本"""
    success = VersionManager.activate_version(db, version_id)
    if not success:
        raise HTTPException(status_code=404, detail="契约版本不存在")
    return {"success": True, "message": "版本已激活"}


@router.delete("/versions/{version_id}")
async def delete_version(version_id: int, db: Session = Depends(get_db)):
    """删除契约版本"""
    success = VersionManager.delete_version(db, version_id)
    if not success:
        raise HTTPException(status_code=404, detail="契约版本不存在")
    return {"success": True, "message": "版本已删除"}


# ==================== 契约列表 ====================


@router.get("/contracts", response_model=ContractListResponse)
async def list_contracts(db: Session = Depends(get_db)):
    """列出所有契约及其元数据"""
    contracts = VersionManager.list_contracts(db)
    return ContractListResponse(
        contracts=contracts,
        total=len(contracts),
    )


# ==================== 契约差异检测 ====================


@router.post("/diff", response_model=ContractDiffResponse)
async def compare_versions(request: ContractDiffRequest, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=404, detail="源版本不存在")
    if not to_version:
        raise HTTPException(status_code=404, detail="目标版本不存在")

    # 对比差异
    diff_result = DiffEngine.compare_versions(
        from_spec=from_version.spec,
        to_spec=to_version.spec,
        from_version=from_version.version,
        to_version=to_version.version,
    )

    return diff_result


# ==================== 契约验证 ====================


@router.post("/validate", response_model=ContractValidateResponse)
async def validate_contract(request: ContractValidateRequest):
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

    return validation_result


# ==================== 契约同步 ====================


@router.post("/sync")
async def sync_contract(request: ContractSyncRequest, db: Session = Depends(get_db)):
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

    return result


@router.get("/sync/report")
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

    return report
