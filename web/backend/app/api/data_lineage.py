"""
数据血缘追踪 API 端点

提供数据血缘关系的记录、查询和影响分析功能。

核心端点:
1. POST /api/v1/lineage/record - 记录血缘关系
2. GET /api/v1/lineage/{node_id}/upstream - 查询上游血缘
3. GET /api/v1/lineage/{node_id}/downstream - 查询下游血缘
4. POST /api/v1/lineage/graph - 查询完整血缘图
5. POST /api/v1/lineage/impact - 影响分析

Author: Claude Code (Main CLI)
Date: 2026-01-09
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.responses import (
    BusinessCode,
    UnifiedResponse,
    create_unified_error_response,
    create_unified_success_response,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/lineage",
    tags=["Data Lineage"],
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


def handle_lineage_error(error: str, request_id: Optional[str] = None) -> UnifiedResponse:
    """
    处理血缘错误并返回统一响应

    Args:
        error: 错误消息
        request_id: 请求ID

    Returns:
        UnifiedResponse: 错误响应
    """
    if "not found" in error.lower() or "does not exist" in error.lower():
        return create_unified_error_response(
            code=BusinessCode.NOT_FOUND,
            message="节点不存在",
            error_code="NODE_NOT_FOUND",
            request_id=request_id,
        )
    elif "invalid" in error.lower():
        return create_unified_error_response(
            code=BusinessCode.VALIDATION_ERROR,
            message="请求参数无效",
            error_code="INVALID_PARAMETER",
            request_id=request_id,
        )
    else:
        return create_unified_error_response(
            code=BusinessCode.INTERNAL_ERROR,
            message=error,
            error_code="LINEAGE_ERROR",
            request_id=request_id,
        )


async def get_lineage_tracker():
    """
    获取LineageTracker实例

    Returns:
        LineageTracker实例
    """
    # TODO: 从依赖注入容器获取LineageTracker实例
    # 这里先创建一个简单的占位符实现
    import asyncpg

    from src.data_governance.lineage import LineageStorage, LineageTracker

    try:
        conn = await asyncpg.connect(
            host=settings.postgresql_host,
            port=settings.postgresql_port,
            user=settings.postgresql_user,
            password=settings.postgresql_password,
            database=settings.postgresql_database,
        )
        storage = LineageStorage(conn)
        tracker = LineageTracker(storage)
        return tracker, conn
    except Exception as e:
        logger.error("Failed to create lineage tracker: {str(e)}"")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize lineage tracker: {str(e)}",
        )


# =============================================================================
# API Endpoints
# =============================================================================


@router.post("/record", response_model=UnifiedResponse, status_code=201)
async def record_lineage(
    request: LineageRecordRequest,
    http_request: Request,
):
    """
    记录血缘关系

    记录两个节点之间的数据流转关系（边），自动创建不存在的节点。

    Args:
        request: 血缘记录请求
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 包含记录结果的统一响应
    """
    request_id = getattr(http_request.state, "request_id", None)
    logger.info("Recording lineage: {request.from_node} -> {request.to_node}", extra={"request_id": request_id})

    try:
        tracker, conn = await get_lineage_tracker()

        # 使用tracker记录血缘关系
        from src.data_governance.lineage import LineageEdge, LineageNode, NodeType, OperationType

        # 创建源节点
        from_node = LineageNode(
            node_id=request.from_node,
            node_type=NodeType(request.from_node_type) if request.from_node_type else NodeType.DATASET,
            name=request.from_node,
        )

        # 创建目标节点
        to_node = LineageNode(
            node_id=request.to_node,
            node_type=NodeType(request.to_node_type) if request.to_node_type else NodeType.DATASET,
            name=request.to_node,
        )

        # 创建边
        edge = LineageEdge(
            from_node=request.from_node,
            to_node=request.to_node,
            operation=OperationType(request.operation),
            metadata=request.metadata,
        )

        # 保存到数据库
        await tracker._storage.save_node(from_node)
        await tracker._storage.save_node(to_node)
        await tracker._storage.save_edge(edge)

        await conn.close()

        logger.info(
            f"Successfully recorded lineage: {request.from_node} -> {request.to_node}", extra={"request_id": request_id}
        )

        return create_unified_success_response(
            data={
                "from_node": request.from_node,
                "to_node": request.to_node,
                "operation": request.operation,
            },
            message=f"成功记录血缘关系: {request.from_node} -> {request.to_node}",
            code=BusinessCode.CREATED,
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to record lineage: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_lineage_error(str(e), request_id)


@router.get("/{node_id}/upstream", response_model=UnifiedResponse)
async def get_upstream_lineage(
    node_id: str,
    max_depth: int = 3,
    http_request: Request = None,
):
    """
    查询上游血缘

    查询指定节点的所有上游数据源和变换操作。

    Args:
        node_id: 节点ID
        max_depth: 最大查询深度（默认3层）
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 包含上游血缘的统一响应
    """
    request_id = getattr(http_request.state, "request_id", None) if http_request else None
    logger.info("Querying upstream lineage for node: {node_id}", extra={"request_id": request_id})

    try:
        tracker, conn = await get_lineage_tracker()

        # 使用BFS迭代查询上游血缘（避免递归和异步嵌套）
        visited = set()
        upstream_nodes = []  # 存储Node对象
        upstream_node_ids = set()  # 用于去重
        edges_to_include = []

        # 初始查询
        graph = await tracker.get_lineage(node_id)

        # 使用队列进行BFS遍历
        from collections import deque

        queue = deque([(node_id, 0)])  # (node_id, depth)

        while queue:
            current_id, depth = queue.popleft()

            # 超过最大深度或已访问则跳过
            if depth > max_depth or current_id in visited:
                continue
            visited.add(current_id)

            # 查询该节点的血缘
            nodes, edges = await tracker._storage.get_lineage(current_id)

            # 筛选指向当前节点的上游边
            for edge in edges:
                if edge.to_node == current_id and edge.from_node not in visited:
                    edges_to_include.append(edge)

                    # 添加上游节点
                    for node in nodes:
                        if node.node_id == edge.from_node and node.node_id not in upstream_node_ids:
                            upstream_nodes.append(node)
                            upstream_node_ids.add(node.node_id)

                    # 将上游节点加入队列继续遍历
                    queue.append((edge.from_node, depth + 1))

        await conn.close()

        # 构建响应数据
        nodes_response = [
            NodeInfo(
                node_id=n.node_id,
                node_type=n.node_type.value,
                name=n.name,
                metadata=n.metadata,
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
            for n in upstream_nodes
        ]

        edges_response = [
            EdgeInfo(
                from_node=e.from_node,
                to_node=e.to_node,
                operation=e.operation.value,
                timestamp=e.timestamp,
                metadata=e.metadata,
            )
            for e in edges_to_include
        ]

        logger.info("Found {len(nodes_response)} upstream nodes for {node_id}", extra={"request_id": request_id})

        return create_unified_success_response(
            data={
                "nodes": [n.dict() for n in nodes_response],
                "edges": [e.dict() for e in edges_response],
                "queried_node": node_id,
                "depth": max_depth,
                "total_nodes": len(nodes_response),
                "total_edges": len(edges_response),
            },
            message=f"成功查询上游血缘: {len(nodes_response)}个节点",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to query upstream lineage: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_lineage_error(str(e), request_id)


@router.get("/{node_id}/downstream", response_model=UnifiedResponse)
async def get_downstream_lineage(
    node_id: str,
    max_depth: int = 3,
    http_request: Request = None,
):
    """
    查询下游血缘

    查询指定节点的所有下游依赖和影响范围。

    Args:
        node_id: 节点ID
        max_depth: 最大查询深度（默认3层）
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 包含下游血缘的统一响应
    """
    request_id = getattr(http_request.state, "request_id", None) if http_request else None
    logger.info("Querying downstream lineage for node: {node_id}", extra={"request_id": request_id})

    try:
        tracker, conn = await get_lineage_tracker()

        # 获取下游血缘
        impacted_nodes = await tracker.get_downstream_impact(node_id, max_levels=max_depth)

        # 获取所有相关的节点和边
        all_nodes = []
        all_edges = []

        for impacted_id in impacted_nodes:
            nodes, edges = await tracker._storage.get_lineage(impacted_id)
            all_nodes.extend(nodes)
            all_edges.extend(edges)

        await conn.close()

        # 去重
        unique_nodes = {n.node_id: n for n in all_nodes}
        unique_edges = {(e.from_node, e.to_node): e for e in all_edges}

        # 构建响应数据
        nodes_response = [
            NodeInfo(
                node_id=n.node_id,
                node_type=n.node_type.value,
                name=n.name,
                metadata=n.metadata,
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
            for n in unique_nodes.values()
        ]

        edges_response = [
            EdgeInfo(
                from_node=e.from_node,
                to_node=e.to_node,
                operation=e.operation.value,
                timestamp=e.timestamp,
                metadata=e.metadata,
            )
            for e in unique_edges.values()
        ]

        logger.info("Found {len(nodes_response)} downstream nodes for {node_id}", extra={"request_id": request_id})

        return create_unified_success_response(
            data={
                "nodes": [n.dict() for n in nodes_response],
                "edges": [e.dict() for e in edges_response],
                "queried_node": node_id,
                "depth": max_depth,
                "total_nodes": len(nodes_response),
                "total_edges": len(edges_response),
            },
            message=f"成功查询下游血缘: {len(nodes_response)}个节点",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to query downstream lineage: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_lineage_error(str(e), request_id)


@router.post("/graph", response_model=UnifiedResponse)
async def get_lineage_graph(
    request: LineageGraphRequest,
    http_request: Request,
):
    """
    查询完整血缘图

    查询指定节点的完整血缘关系图（包括上游和下游）。

    Args:
        request: 血缘图查询请求
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 包含完整血缘图的统一响应
    """
    request_id = getattr(http_request.state, "request_id", None)
    logger.info(
        f"Querying lineage graph for node: {request.node_id}, direction: {request.direction}",
        extra={"request_id": request_id},
    )

    try:
        tracker, conn = await get_lineage_tracker()

        # 获取完整血缘图
        graph = await tracker.get_lineage(request.node_id)

        # 根据方向筛选
        if request.direction == "upstream":
            edges = [e for e in graph.edges if e.to_node == request.node_id]
        elif request.direction == "downstream":
            edges = [e for e in graph.edges if e.from_node == request.node_id]
        else:  # both
            edges = graph.edges

        # 限制深度
        visited = {request.node_id}
        nodes_at_depth = {request.node_id}
        included_edges = []

        for _ in range(request.max_depth):
            next_level = set()
            for edge in edges:
                if edge.from_node in nodes_at_depth and edge.to_node not in visited:
                    next_level.add(edge.to_node)
                    visited.add(edge.to_node)
                    included_edges.append(edge)
                elif edge.to_node in nodes_at_depth and edge.from_node not in visited:
                    next_level.add(edge.from_node)
                    visited.add(edge.from_node)
                    included_edges.append(edge)

            if not next_level:
                break
            nodes_at_depth = next_level

        # 收集所有相关节点
        node_ids = set()
        for edge in included_edges:
            node_ids.add(edge.from_node)
            node_ids.add(edge.to_node)

        included_nodes = [n for n in graph.nodes if n.node_id in node_ids]

        await conn.close()

        # 构建响应数据
        nodes_response = [
            NodeInfo(
                node_id=n.node_id,
                node_type=n.node_type.value,
                name=n.name,
                metadata=n.metadata if request.include_metadata else {},
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
            for n in included_nodes
        ]

        edges_response = [
            EdgeInfo(
                from_node=e.from_node,
                to_node=e.to_node,
                operation=e.operation.value,
                timestamp=e.timestamp,
                metadata=e.metadata if request.include_metadata else {},
            )
            for e in included_edges
        ]

        logger.info(
            f"Retrieved lineage graph: {len(nodes_response)} nodes, {len(edges_response)} edges",
            extra={"request_id": request_id},
        )

        return create_unified_success_response(
            data={
                "nodes": [n.dict() for n in nodes_response],
                "edges": [e.dict() for e in edges_response],
                "queried_node": request.node_id,
                "direction": request.direction,
                "depth": request.max_depth,
                "total_nodes": len(nodes_response),
                "total_edges": len(edges_response),
            },
            message=f"成功查询血缘图: {len(nodes_response)}个节点, {len(edges_response)}条边",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to query lineage graph: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_lineage_error(str(e), request_id)


@router.post("/impact", response_model=UnifiedResponse)
async def analyze_impact(
    request: ImpactAnalysisRequest,
    http_request_obj: Request,
):
    """
    影响分析

    分析指定节点变更后对所有下游节点的影响范围。

    Args:
        request: 影响分析请求
        http_request_obj: HTTP请求对象

    Returns:
        UnifiedResponse: 包含影响分析结果的统一响应
    """
    request_id = getattr(http_request_obj.state, "request_id", None)
    logger.info(
        f"Analyzing impact for node: {request.node_id}, max_levels: {request.max_levels}",
        extra={"request_id": request_id},
    )

    try:
        tracker, conn = await get_lineage_tracker()

        # 获取受影响的节点
        impacted_node_ids = await tracker.get_downstream_impact(request.node_id, max_levels=request.max_levels)

        # 构建影响节点列表（包含路径信息）
        impacted_nodes = []

        for node_id in impacted_node_ids:
            # 查询该节点的信息
            nodes, edges = await tracker._storage.get_lineage(node_id)

            if nodes:
                node = nodes[0]

                # 查找从源节点到该节点的路径
                path = [request.node_id]
                current = request.node_id

                # 简单的路径查找（BFS）
                queue = [(current, [])]
                found_path = None

                while queue and not found_path:
                    curr, curr_path = queue.pop(0)
                    if curr == node_id:
                        found_path = curr_path
                        break

                    # 查找下游边
                    for edge in edges:
                        if edge.from_node == curr:
                            queue.append((edge.to_node, curr_path + [edge.to_node]))

                # 确定影响层级
                level = 0
                for edge in edges:
                    if edge.from_node == request.node_id and edge.to_node == node_id:
                        level = 1
                        break

                # 如果不是直接连接，尝试通过其他节点查找
                if level == 0:
                    # 使用BFS查找层级
                    level_queue = [(request.node_id, 0)]
                    visited_level = {request.node_id}

                    while level_queue:
                        curr, curr_level = level_queue.pop(0)
                        if curr == node_id:
                            level = curr_level
                            break

                        for edge in edges:
                            if edge.from_node == curr and edge.to_node not in visited_level:
                                visited_level.add(edge.to_node)
                                level_queue.append((edge.to_node, curr_level + 1))

                impact_type = "direct" if level == 1 else "indirect"

                impacted_nodes.append(
                    ImpactNode(
                        node_id=node.node_id,
                        node_type=node.node_type.value,
                        level=level,
                        path=path,
                        impact_type=impact_type,
                    )
                )

        await conn.close()

        logger.info(
            f"Impact analysis complete: {len(impacted_nodes)} nodes impacted",
            extra={"request_id": request_id},
        )

        return create_unified_success_response(
            data={
                "node_id": request.node_id,
                "impacted_nodes": [n.dict() for n in impacted_nodes],
                "total_impacted": len(impacted_nodes),
                "max_level": request.max_levels,
                "analysis_timestamp": datetime.now().isoformat(),
            },
            message=f"影响分析完成: {len(impacted_nodes)}个节点受影响",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to analyze impact: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_lineage_error(str(e), request_id)
