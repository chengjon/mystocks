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

CONTRACT_IMPACT_EXAMPLES = {
    "breaking_endpoint_change": {
        "summary": "Analyze consumer impact between two published contract versions",
        "description": "Compare a source contract version with a target contract version before release.",
        "value": {
            "from_version_id": 101,
            "to_version_id": 108,
        },
    }
}

CONTRACT_IMPACT_RESPONSES = {
    200: {
        "description": "契约影响分析结果。",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "code": 200,
                    "message": "契约影响分析完成",
                    "data": {
                        "from_version": "2.1.0",
                        "to_version": "2.2.0",
                        "risk_level": "medium",
                        "summary": {
                            "total_impacts": 2,
                            "breaking_impacts": 1,
                            "non_breaking_impacts": 1,
                            "by_category": {"endpoint": 1, "schema": 1},
                        },
                        "impacts": [
                            {
                                "category": "endpoint",
                                "name": "POST /api/trading/orders",
                                "path": "paths./api/trading/orders.post.requestBody",
                                "change_type": "modified",
                                "severity": "high",
                                "is_breaking": True,
                                "reason": "Required request field changed for order submission.",
                            }
                        ],
                        "affected_endpoints": ["/api/trading/orders"],
                        "affected_schemas": ["OrderRequest"],
                        "affected_clients": ["trading-terminal", "strategy-engine"],
                        "recommendations": [
                            "Publish a migration notice before activating the target contract.",
                        ],
                        "migration_effort": {
                            "level": "medium",
                            "score": 55,
                            "estimated_hours_min": 4,
                            "estimated_hours_max": 12,
                            "drivers": ["breaking endpoint request change"],
                        },
                        "notifications": [
                            {
                                "kind": "breaking_contract_change",
                                "priority": "high",
                                "title": "Breaking contract impact detected",
                                "message": "1 breaking impact affects trading consumers.",
                                "targets": ["trading-terminal", "strategy-engine"],
                                "action_required": True,
                                "action_url": "/api/contracts/impact",
                                "metadata": {"breaking_impacts": 1},
                            }
                        ],
                    },
                }
            }
        },
    },
    404: {
        "description": "源契约版本或目标契约版本不存在。",
        "content": {"application/json": {"example": {"detail": "源版本不存在"}}},
    },
    500: {
        "description": "契约影响分析失败，通常由契约仓库、数据库或影响分析链路异常导致。",
        "content": {"application/json": {"example": {"detail": "contract impact analysis unavailable"}}},
    },
}


@router.post(
    "/impact",
    response_model=UnifiedResponse[ContractImpactAnalysisResponse],
    summary="分析契约变更影响",
    description="基于两个契约版本的 OpenAPI 规范分析 endpoint、schema、client 域和迁移工作量影响。",
    responses=CONTRACT_IMPACT_RESPONSES,
)
async def analyze_contract_impact(
    request: ContractImpactRequest = Body(..., openapi_examples=CONTRACT_IMPACT_EXAMPLES),
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
    notification_service = ContractImpactNotificationService()
    notifications = notification_service.build_notifications(analysis)
    await notification_service.dispatch_notifications(notifications)
    response = ContractImpactAnalysisResponse(
        **asdict(analysis),
        notifications=[asdict(notification) for notification in notifications],
    )
    return UnifiedResponse[ContractImpactAnalysisResponse](data=response, message="契约影响分析完成")
