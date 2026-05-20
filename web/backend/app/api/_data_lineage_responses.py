"""Auto-extracted response constants."""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.openapi_config import COMMON_RESPONSES
from pydantic import BaseModel, Field

LINEAGE_COMMON_ERROR_RESPONSES = {
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

LINEAGE_QUERY_ERROR_RESPONSES = {
    404: COMMON_RESPONSES[404],
    **LINEAGE_COMMON_ERROR_RESPONSES,
}


def _success_response_spec(
    status_code: int,
    description: str,
    example: Dict[str, Any],
    extra_responses: Optional[Dict[int, Dict[str, Any]]] = None,
) -> Dict[int, Dict[str, Any]]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        },
        **(extra_responses or {}),
    }

LINEAGE_RECORD_REQUEST_EXAMPLE = {
    "from_node": "raw:stock:600519",
    "to_node": "feature:daily-factor:600519",
    "operation": "transform",
    "from_node_type": "dataset",
    "to_node_type": "transform",
    "metadata": {
        "market": "A-share",
        "pipeline": "daily-factor-build",
        "owner": "quant-research",
    },
}

LINEAGE_GRAPH_REQUEST_EXAMPLE = {
    "node_id": "feature:daily-factor:600519",
    "direction": "both",
    "max_depth": 3,
    "include_metadata": True,
}

LINEAGE_IMPACT_REQUEST_EXAMPLE = {
    "node_id": "feature:daily-factor:600519",
    "max_levels": 3,
    "include_indirect": True,
}

LINEAGE_RECORD_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 201,
    "message": "成功记录血缘关系: raw:stock:600519 -> feature:daily-factor:600519",
    "data": {
        "from_node": "raw:stock:600519",
        "to_node": "feature:daily-factor:600519",
        "operation": "transform",
    },
    "timestamp": "2026-04-08T03:10:00Z",
    "request_id": "req-lineage-record-001",
    "errors": None,
}

LINEAGE_UPSTREAM_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "成功查询上游血缘: 2个节点",
    "data": {
        "nodes": [
            {
                "node_id": "raw:stock:600519",
                "node_type": "dataset",
                "name": "raw:stock:600519",
                "metadata": {"market": "A-share", "source": "tdx"},
                "created_at": "2026-04-01T09:30:00Z",
                "updated_at": "2026-04-08T02:50:00Z",
            },
            {
                "node_id": "feature:daily-factor:600519",
                "node_type": "transform",
                "name": "feature:daily-factor:600519",
                "metadata": {"pipeline": "daily-factor-build"},
                "created_at": "2026-04-07T15:00:00Z",
                "updated_at": "2026-04-08T02:50:00Z",
            },
        ],
        "edges": [
            {
                "from_node": "raw:stock:600519",
                "to_node": "feature:daily-factor:600519",
                "operation": "transform",
                "timestamp": "2026-04-08T02:45:00Z",
                "metadata": {"pipeline": "daily-factor-build"},
            }
        ],
        "queried_node": "feature:daily-factor:600519",
        "depth": 3,
        "total_nodes": 2,
        "total_edges": 1,
    },
    "timestamp": "2026-04-08T03:10:00Z",
    "request_id": "req-lineage-upstream-001",
    "errors": None,
}

LINEAGE_DOWNSTREAM_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "成功查询下游血缘: 2个节点",
    "data": {
        "nodes": [
            {
                "node_id": "feature:daily-factor:600519",
                "node_type": "transform",
                "name": "feature:daily-factor:600519",
                "metadata": {"pipeline": "daily-factor-build"},
                "created_at": "2026-04-07T15:00:00Z",
                "updated_at": "2026-04-08T02:50:00Z",
            },
            {
                "node_id": "risk:model-input:if-main",
                "node_type": "dataset",
                "name": "risk:model-input:if-main",
                "metadata": {"market": "CFFEX", "instrument": "IF主连"},
                "created_at": "2026-04-08T02:40:00Z",
                "updated_at": "2026-04-08T02:55:00Z",
            },
        ],
        "edges": [
            {
                "from_node": "feature:daily-factor:600519",
                "to_node": "risk:model-input:if-main",
                "operation": "serve",
                "timestamp": "2026-04-08T02:55:00Z",
                "metadata": {"consumer": "index-futures-risk-engine"},
            }
        ],
        "queried_node": "feature:daily-factor:600519",
        "depth": 3,
        "total_nodes": 2,
        "total_edges": 1,
    },
    "timestamp": "2026-04-08T03:10:00Z",
    "request_id": "req-lineage-downstream-001",
    "errors": None,
}

LINEAGE_GRAPH_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "成功查询血缘图: 3个节点, 2条边",
    "data": {
        "nodes": [
            {
                "node_id": "raw:stock:600519",
                "node_type": "dataset",
                "name": "raw:stock:600519",
                "metadata": {"market": "A-share", "source": "tdx"},
                "created_at": "2026-04-01T09:30:00Z",
                "updated_at": "2026-04-08T02:50:00Z",
            },
            {
                "node_id": "feature:daily-factor:600519",
                "node_type": "transform",
                "name": "feature:daily-factor:600519",
                "metadata": {"pipeline": "daily-factor-build"},
                "created_at": "2026-04-07T15:00:00Z",
                "updated_at": "2026-04-08T02:50:00Z",
            },
            {
                "node_id": "risk:model-input:if-main",
                "node_type": "dataset",
                "name": "risk:model-input:if-main",
                "metadata": {"market": "CFFEX", "instrument": "IF主连"},
                "created_at": "2026-04-08T02:40:00Z",
                "updated_at": "2026-04-08T02:55:00Z",
            },
        ],
        "edges": [
            {
                "from_node": "raw:stock:600519",
                "to_node": "feature:daily-factor:600519",
                "operation": "transform",
                "timestamp": "2026-04-08T02:45:00Z",
                "metadata": {"pipeline": "daily-factor-build"},
            },
            {
                "from_node": "feature:daily-factor:600519",
                "to_node": "risk:model-input:if-main",
                "operation": "serve",
                "timestamp": "2026-04-08T02:55:00Z",
                "metadata": {"consumer": "index-futures-risk-engine"},
            },
        ],
        "queried_node": "feature:daily-factor:600519",
        "direction": "both",
        "depth": 3,
        "total_nodes": 3,
        "total_edges": 2,
    },
    "timestamp": "2026-04-08T03:10:00Z",
    "request_id": "req-lineage-graph-001",
    "errors": None,
}

LINEAGE_IMPACT_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "影响分析完成: 2个节点受影响",
    "data": {
        "node_id": "feature:daily-factor:600519",
        "impacted_nodes": [
            {
                "node_id": "risk:model-input:if-main",
                "node_type": "dataset",
                "level": 1,
                "path": ["feature:daily-factor:600519", "risk:model-input:if-main"],
                "impact_type": "direct",
            },
            {
                "node_id": "strategy:alpha-if-spread",
                "node_type": "transform",
                "level": 2,
                "path": [
                    "feature:daily-factor:600519",
                    "risk:model-input:if-main",
                    "strategy:alpha-if-spread",
                ],
                "impact_type": "indirect",
            },
        ],
        "total_impacted": 2,
        "max_level": 3,
        "analysis_timestamp": "2026-04-08T03:10:00Z",
    },
    "timestamp": "2026-04-08T03:10:00Z",
    "request_id": "req-lineage-impact-001",
    "errors": None,
}

LINEAGE_RECORD_RESPONSES = _success_response_spec(
    201,
    "血缘关系记录结果。",
    LINEAGE_RECORD_SUCCESS_EXAMPLE,
    LINEAGE_COMMON_ERROR_RESPONSES,
)

LINEAGE_UPSTREAM_RESPONSES = _success_response_spec(
    200,
    "上游血缘查询结果。",
    LINEAGE_UPSTREAM_SUCCESS_EXAMPLE,
    LINEAGE_QUERY_ERROR_RESPONSES,
)

LINEAGE_DOWNSTREAM_RESPONSES = _success_response_spec(
    200,
    "下游血缘查询结果。",
    LINEAGE_DOWNSTREAM_SUCCESS_EXAMPLE,
    LINEAGE_QUERY_ERROR_RESPONSES,
)

LINEAGE_GRAPH_RESPONSES = _success_response_spec(
    200,
    "完整血缘图查询结果。",
    LINEAGE_GRAPH_SUCCESS_EXAMPLE,
    LINEAGE_QUERY_ERROR_RESPONSES,
)

LINEAGE_IMPACT_RESPONSES = _success_response_spec(
    200,
    "血缘影响分析结果。",
    LINEAGE_IMPACT_SUCCESS_EXAMPLE,
    LINEAGE_QUERY_ERROR_RESPONSES,
)


# =============================================================================
# Pydantic Models for Request/Response
# =============================================================================


class LineageRecordRequest(BaseModel):
    """记录血缘关系的请求模型"""

    from_node: str = Field(..., description="源节点ID", min_length=1, max_length=255)
    to_node: str = Field(..., description="目标节点ID", min_length=1, max_length=255)
    operation: str = Field(
        ...,
        description="操作类型: fetch, transform, store, serve",
        pattern="^(fetch|transform|store|serve)$",
    )
    from_node_type: Optional[str] = Field(
        None,
        description="源节点类型: datasource, dataset, api, storage, transform",
        pattern="^(datasource|dataset|api|storage|transform)$",
    )
    to_node_type: Optional[str] = Field(
        None,
        description="目标节点类型: datasource, dataset, api, storage, transform",
        pattern="^(datasource|dataset|api|storage|transform)$",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据（可选）")


class LineageGraphRequest(BaseModel):
    """查询血缘图的请求模型"""

    node_id: str = Field(..., description="起始节点ID", min_length=1)
    direction: str = Field(
        default="both",
        description="查询方向: upstream, downstream, both",
        pattern="^(upstream|downstream|both)$",
    )
    max_depth: int = Field(default=3, description="最大查询深度", ge=1, le=10)
    include_metadata: bool = Field(default=True, description="是否包含节点和边的元数据")


class ImpactAnalysisRequest(BaseModel):
    """影响分析的请求模型"""

    node_id: str = Field(..., description="起始节点ID", min_length=1)
    max_levels: int = Field(default=3, description="最大影响层级", ge=1, le=10)
    include_indirect: bool = Field(default=True, description="是否包含间接影响")


class NodeInfo(BaseModel):
    """节点信息"""

    node_id: str
    node_type: str
    name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EdgeInfo(BaseModel):
    """边信息"""

    from_node: str
    to_node: str
    operation: str
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LineageGraphResponse(BaseModel):
    """血缘图响应"""

    nodes: List[NodeInfo]
    edges: List[EdgeInfo]
    queried_node: str
    depth: int
    total_nodes: int
    total_edges: int


class ImpactNode(BaseModel):
    """影响的节点"""

    node_id: str
    node_type: str
    level: int
    path: List[str] = Field(description="从源节点到该节点的路径")
    impact_type: str = Field(description="影响类型: direct, indirect")


class ImpactAnalysisResponse(BaseModel):
    """影响分析响应"""

    node_id: str
    impacted_nodes: List[ImpactNode]
    total_impacted: int
    max_level: int
    analysis_timestamp: datetime


# =============================================================================
# Helper Functions
# =============================================================================


class _AsyncpgLineageConnectionAdapter:
    """为 LineageStorage 适配 asyncpg 原生连接。"""

    def __init__(self, connection):
        self._connection = connection

    @asynccontextmanager
    async def acquire_connection(self):
        yield self._connection

    async def close(self) -> None:
        await self._connection.close()
