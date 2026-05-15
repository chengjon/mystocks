"""Contract impact analysis API routes."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.contract.schemas import ContractImpactAnalysisResponse, ContractImpactRequest
from app.api.contract.services.impact_analyzer import ContractImpactAnalyzer
from app.api.contract.services.impact_notifications import ContractImpactNotificationService
from app.api.contract.services.version_manager import VersionManager
from app.core.database import get_db
from app.core.responses import UnifiedResponse

router = APIRouter(prefix="/api/contracts", tags=["contract-management"])


@router.post(
    "/impact",
    response_model=UnifiedResponse[ContractImpactAnalysisResponse],
    summary="分析契约变更影响",
    description="基于两个契约版本的 OpenAPI 规范分析 endpoint、schema、client 域和迁移工作量影响。",
)
async def analyze_contract_impact(
    request: ContractImpactRequest = Body(...),
    db: Session = Depends(get_db),
) -> UnifiedResponse[ContractImpactAnalysisResponse]:
    """分析两个契约版本之间的消费者影响与迁移工作量。"""
    from_version = VersionManager.get_version(db, request.from_version_id)
    to_version = VersionManager.get_version(db, request.to_version_id)

    if not from_version:
        raise HTTPException(status_code=404, detail="源版本不存在")
    if not to_version:
        raise HTTPException(status_code=404, detail="目标版本不存在")

    analysis = ContractImpactAnalyzer().analyze_specs(
        from_spec=from_version.spec,
        to_spec=to_version.spec,
        from_version=from_version.version,
        to_version=to_version.version,
    )
    notifications = ContractImpactNotificationService().build_notifications(analysis)
    response = ContractImpactAnalysisResponse(
        **asdict(analysis),
        notifications=[asdict(notification) for notification in notifications],
    )
    return UnifiedResponse[ContractImpactAnalysisResponse](data=response, message="契约影响分析完成")
