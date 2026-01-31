"""
Data Lineage Tracking Module

Tracks the complete data flow from sources to storage,
supporting problem troubleshooting and impact analysis.
"""

import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    """Types of lineage nodes"""

    DATASOURCE = "datasource"
    DATASET = "dataset"
    API = "api"
    STORAGE = "storage"
    TRANSFORM = "transform"


class OperationType(str, Enum):
    """Types of operations in lineage"""

    FETCH = "fetch"
    TRANSFORM = "transform"
    STORE = "store"
    SERVE = "serve"


@dataclass
class LineageNode:
    """A node in the lineage graph"""

    node_id: str
    node_type: NodeType
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LineageEdge:
    """An edge connecting two nodes in the lineage graph"""

    from_node: str
    to_node: str
    operation: OperationType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageGraph:
    """Complete lineage graph for a dataset"""

    nodes: List[LineageNode]
    edges: List[LineageEdge]
    queried_at: datetime = field(default_factory=datetime.utcnow)


class LineageStorage:
    """
    Storage backend for lineage data.
    Uses PostgreSQL for persistence.
    """

    def __init__(self, db_connection):
        self._db = db_connection

    async def init_tables(self) -> None:
        """Initialize database tables for lineage storage"""
        # Tables are created separately via migration scripts

    async def save_node(self, node: LineageNode) -> None:
        """Save a lineage node to storage"""
        try:
            async with self._db.acquire_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO data_lineage_nodes
                    (node_id, node_type, name, metadata, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (node_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        metadata = EXCLUDED.metadata,
                        updated_at = EXCLUDED.updated_at
                    """,
                    node.node_id,
                    node.node_type.value,
                    node.name,
                    json.dumps(node.metadata),
                    node.created_at,
                    node.updated_at,
                )
        except Exception as e:
            logger.error("Failed to save node {node.node_id}: %(e)s")

    async def save_edge(self, edge: LineageEdge) -> None:
        """Save a lineage edge to storage"""
        try:
            async with self._db.acquire_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO data_lineage_edges
                    (from_node, to_node, operation, timestamp, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    edge.from_node,
                    edge.to_node,
                    edge.operation.value,
                    edge.timestamp,
                    json.dumps(edge.metadata),
                )
        except Exception as e:
            logger.error("Failed to save edge: %(e)s")

    async def get_lineage(self, node_id: str) -> Tuple[List[LineageNode], List[LineageEdge]]:
        """
        Get complete lineage graph for a node.

        Returns:
            Tuple of (nodes, edges)
        """
        nodes = []
        edges = []

        try:
            async with self._db.acquire_connection() as conn:
                # Get the starting node
                node_rows = await conn.fetch("SELECT * FROM data_lineage_nodes WHERE node_id = $1", node_id)
                for row in node_rows:
                    nodes.append(
                        LineageNode(
                            node_id=row["node_id"],
                            node_type=NodeType(row["node_type"]),
                            name=row["name"],
                            metadata=json.loads(row["metadata"] or "{}"),
                            created_at=row["created_at"],
                            updated_at=row["updated_at"],
                        )
                    )

                # Get downstream edges and nodes
                downstream = await conn.fetch(
                    """
                    SELECT e.*, n.node_type, n.name, n.metadata
                    FROM data_lineage_edges e
                    LEFT JOIN data_lineage_nodes n ON e.to_node = n.node_id
                    WHERE e.from_node = $1
                    """,
                    node_id,
                )
                for row in downstream:
                    edges.append(
                        LineageEdge(
                            from_node=row["from_node"],
                            to_node=row["to_node"],
                            operation=OperationType(row["operation"]),
                            timestamp=row["timestamp"],
                            metadata=json.loads(row["metadata"] or "{}"),
                        )
                    )
                    if row["node_type"]:
                        nodes.append(
                            LineageNode(
                                node_id=row["to_node"],
                                node_type=NodeType(row["node_type"]),
                                name=row["name"],
                                metadata=json.loads(row["metadata"] or "{}"),
                            )
                        )

                # Get upstream edges
                upstream = await conn.fetch(
                    """
                    SELECT e.*, n.node_type, n.name, n.metadata
                    FROM data_lineage_edges e
                    LEFT JOIN data_lineage_nodes n ON e.from_node = n.node_id
                    WHERE e.to_node = $1
                    """,
                    node_id,
                )
                for row in upstream:
                    edges.append(
                        LineageEdge(
                            from_node=row["from_node"],
                            to_node=row["to_node"],
                            operation=OperationType(row["operation"]),
                            timestamp=row["timestamp"],
                            metadata=json.loads(row["metadata"] or "{}"),
                        )
                    )
                    if row["node_type"]:
                        nodes.append(
                            LineageNode(
                                node_id=row["from_node"],
                                node_type=NodeType(row["node_type"]),
                                name=row["name"],
                                metadata=json.loads(row["metadata"] or "{}"),
                            )
                        )

        except Exception as e:
            logger.error("Failed to get lineage: %(e)s")

        return nodes, edges


class LineageTracker:
    """
    Data lineage tracker that records data flow through the system.
    """

    def __init__(self, storage: LineageStorage):
        self._storage = storage
        self._current_chain: List[LineageNode] = []
        self._context_id: Optional[str] = None

    @contextmanager
    def trace(self, source_id: str, source_type: NodeType = NodeType.DATASOURCE):
        """
        Context manager for tracing data flow.

        Usage:
            async with tracker.trace("akshare") as t:
                t.record_fetch("market_data")
                t.record_transform("processed_data")
                t.record_store("tdengine")
        """
        self._context_id = f"context_{datetime.utcnow().timestamp()}"
        self._current_chain = [LineageNode(node_id=source_id, node_type=source_type, name=source_id)]

        try:
            yield self
        finally:
            self._current_chain.clear()
            self._context_id = None

    def record_fetch(self, target_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a data fetch operation.

        Args:
            target_id: ID of the fetched dataset
            metadata: Additional metadata
        """
        self._record_operation(OperationType.FETCH, target_id, NodeType.DATASET, metadata)

    def record_transform(
        self,
        target_id: str,
        transform_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a data transformation operation.

        Args:
            target_id: ID of the transformed dataset
            transform_type: Type of transformation
            metadata: Additional metadata
        """
        op_metadata = {"transform_type": transform_type}
        if metadata:
            op_metadata.update(metadata)
        self._record_operation(OperationType.TRANSFORM, target_id, NodeType.DATASET, op_metadata)

    def record_store(
        self,
        target_id: str,
        storage_type: str = "database",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a data storage operation.

        Args:
            target_id: ID of the storage location
            storage_type: Type of storage
            metadata: Additional metadata
        """
        op_metadata = {"storage_type": storage_type}
        if metadata:
            op_metadata.update(metadata)
        self._record_operation(OperationType.STORE, target_id, NodeType.STORAGE, op_metadata)

    def record_serve(self, target_id: str, endpoint: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a data serving operation.

        Args:
            target_id: ID of the served data
            endpoint: API endpoint or service name
            metadata: Additional metadata
        """
        op_metadata = {"endpoint": endpoint}
        if metadata:
            op_metadata.update(metadata)
        self._record_operation(OperationType.SERVE, target_id, NodeType.API, op_metadata)

    def _record_operation(
        self,
        operation: OperationType,
        target: str,
        target_type: NodeType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Internal method to record an operation in the lineage chain.
        """
        if not self._current_chain:
            logger.warning("No active trace context, operation not recorded")
            return

        from_node = self._current_chain[-1].node_id
        new_node = LineageNode(node_id=target, node_type=target_type, name=target, metadata=metadata or {})
        edge = LineageEdge(
            from_node=from_node,
            to_node=target,
            operation=operation,
            metadata=metadata or {},
        )

        self._current_chain.append(new_node)

        # Save to storage
        import asyncio

        asyncio.create_task(self._storage.save_node(new_node))
        asyncio.create_task(self._storage.save_edge(edge))

    def get_current_chain(self) -> List[LineageNode]:
        """
        Get the current lineage chain.

        Returns:
            List of nodes in the current trace
        """
        return self._current_chain.copy()

    async def get_lineage(self, node_id: str) -> LineageGraph:
        """
        Get complete lineage graph for a node.

        Args:
            node_id: ID of the node to query

        Returns:
            LineageGraph with all connected nodes and edges
        """
        nodes, edges = await self._storage.get_lineage(node_id)
        return LineageGraph(nodes=nodes, edges=edges)

    async def get_downstream_impact(self, node_id: str, max_levels: int = 3) -> List[str]:
        """
        Get all downstream nodes impacted by a change.

        Args:
            node_id: Starting node ID
            max_levels: Maximum number of levels to traverse

        Returns:
            List of impacted node IDs
        """
        impacted: List[str] = []
        visited = set()
        queue = [(node_id, 0)]

        while queue:
            current_id, level = queue.pop(0)
            if current_id in visited or level >= max_levels:
                continue
            visited.add(current_id)

            nodes, edges = await self._storage.get_lineage(current_id)
            for edge in edges:
                if edge.from_node == current_id and edge.to_node not in visited:
                    impacted.append(edge.to_node)
                    queue.append((edge.to_node, level + 1))

        return impacted
