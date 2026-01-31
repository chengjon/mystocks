"""
Data Governance API

RESTful API endpoints for data quality metrics, lineage tracking,
and asset management.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.data_governance import (
    AssetType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/governance", tags=["Data Governance"])


class QualityScoreResponse(BaseModel):
    """Response model for quality score"""

    dataset_id: str
    overall_score: float
    dimension_scores: Dict[str, float]
    measured_at: datetime


class QualityTrendResponse(BaseModel):
    """Response model for quality trend"""

    dataset_id: str
    trends: List[Dict[str, Any]]


class AnomalyResponse(BaseModel):
    """Response model for quality anomaly"""

    dimension: str
    severity: str
    message: str


class LineageNodeResponse(BaseModel):
    """Response model for lineage node"""

    node_id: str
    node_type: str
    name: str
    metadata: Dict[str, Any] = {}


class LineageEdgeResponse(BaseModel):
    """Response model for lineage edge"""

    from_node: str
    to_node: str
    operation: str
    timestamp: datetime


class LineageGraphResponse(BaseModel):
    """Response model for lineage graph"""

    nodes: List[LineageNodeResponse]
    edges: List[LineageEdgeResponse]
    queried_at: datetime


class ImpactAnalysisResponse(BaseModel):
    """Response model for impact analysis"""

    node_id: str
    impacted_nodes: List[str]
    levels_traversed: int


class AssetResponse(BaseModel):
    """Response model for data asset"""

    asset_id: str
    name: str
    asset_type: str
    source: str
    description: str = ""
    owner: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    quality_score: Optional[float] = None


class AssetCreateRequest(BaseModel):
    """Request model for creating an asset"""

    asset_id: str = Field(..., description="Unique identifier for the asset")
    name: str = Field(..., description="Display name")
    asset_type: str = Field(..., description="Type of asset (dataset, table, view, api)")
    source: str = Field(..., description="Data source")
    description: str = ""
    owner: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class AssetUpdateRequest(BaseModel):
    """Request model for updating an asset"""

    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DataAssetCatalogResponse(BaseModel):
    """Response model for asset catalog"""

    total: int
    assets: List[AssetResponse]


# Quality API endpoints


@router.get("/quality/{asset_id}", response_model=QualityScoreResponse)
async def get_quality_score(asset_id: str) -> QualityScoreResponse:
    """Get quality score for a dataset"""
    from src.data_governance.quality import DataQualityChecker

    checker = DataQualityChecker()

    # Check all dimensions
    report = await checker.check_all_dimensions(asset_id)

    return QualityScoreResponse(
        dataset_id=report.dataset_id,
        overall_score=report.overall_score,
        dimension_scores={s.dimension.value: s.score for s in report.dimension_scores},
        measured_at=report.measured_at,
    )


@router.get("/quality/{asset_id}/trend", response_model=QualityTrendResponse)
async def get_quality_trend(
    asset_id: str, period: str = Query("7d", description="Time period: 1d, 7d, 30d")
) -> QualityTrendResponse:
    """Get quality score trend over time"""
    from src.data_governance.quality import DataQualityChecker

    checker = DataQualityChecker()

    history = await checker.get_quality_trend(asset_id)

    return QualityTrendResponse(
        dataset_id=asset_id,
        trends=[{"overall_score": r.overall_score, "measured_at": r.measured_at.isoformat()} for r in history],
    )


@router.get("/quality/anomalies", response_model=List[AnomalyResponse])
async def get_quality_anomalies(
    severity: str = Query("all", description="Filter by severity: high, medium, all"),
) -> List[AnomalyResponse]:
    """Get all quality anomalies"""
    # This would query the quality checker for anomalies
    # For now, return placeholder data
    return []


# Lineage API endpoints


@router.get("/lineage/{node_id}", response_model=LineageGraphResponse)
async def get_lineage_graph(
    node_id: str,
    direction: str = Query("both", description="Direction: upstream, downstream, both"),
) -> LineageGraphResponse:
    """Get lineage graph for a node"""

    # This would query the lineage tracker
    # For now, return placeholder data
    return LineageGraphResponse(nodes=[], edges=[], queried_at=datetime.utcnow())


@router.get("/lineage/{node_id}/impact", response_model=ImpactAnalysisResponse)
async def get_impact_analysis(
    node_id: str,
    levels: int = Query(3, ge=1, le=10, description="Maximum levels to traverse"),
) -> ImpactAnalysisResponse:
    """Get downstream impact analysis for a node"""
    # This would query the lineage tracker
    return ImpactAnalysisResponse(node_id=node_id, impacted_nodes=[], levels_traversed=levels)


# Asset API endpoints


@router.get("/assets", response_model=DataAssetCatalogResponse)
async def list_assets(
    asset_type: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> DataAssetCatalogResponse:
    """Get asset catalog with optional filters"""
    # This would query the asset registry
    # For now, return placeholder data
    return DataAssetCatalogResponse(total=0, assets=[])


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str) -> AssetResponse:
    """Get details of a specific asset"""
    # This would query the asset registry
    raise HTTPException(status_code=404, detail="Asset not found")


@router.post("/assets", response_model=AssetResponse, status_code=201)
async def create_asset(request: AssetCreateRequest) -> AssetResponse:
    """Register a new data asset"""
    try:
        AssetType(request.asset_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset type")

    return AssetResponse(
        asset_id=request.asset_id,
        name=request.name,
        asset_type=request.asset_type,
        source=request.source,
        description=request.description,
        owner=request.owner,
        tags=request.tags,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: str, request: AssetUpdateRequest) -> AssetResponse:
    """Update an asset"""
    # This would update the asset in the registry
    raise HTTPException(status_code=404, detail="Asset not found")


@router.delete("/assets/{asset_id}", status_code=204)
async def delete_asset(asset_id: str):
    """Delete an asset"""
    # This would delete the asset from the registry


@router.post("/assets/{asset_id}/access", response_model=Dict[str, str])
async def record_asset_access(asset_id: str) -> Dict[str, str]:
    """Record an access to an asset"""
    # This would record the access in the registry
    return {"status": "recorded"}


@router.get("/assets/stats/summary")
async def get_asset_stats() -> Dict[str, Any]:
    """Get asset statistics summary"""
    # This would get stats from the registry
    return {"total_assets": 0, "by_type": {}, "top_accessed": []}
