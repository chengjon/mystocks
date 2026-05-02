from __future__ import annotations

import logging
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - optional dependency in runtime only
    GraphDatabase = None


class Neo4jLineageStore:
    """Optional persistence layer for lineage graphs."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self._driver = None
        if GraphDatabase is None or not all([uri, user, password]):
            return

        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as exc:  # pragma: no cover - defensive runtime branch
            logger.warning("Failed to initialize Neo4jLineageStore: %s", exc)
            self._driver = None

    @property
    def enabled(self) -> bool:
        return self._driver is not None

    def persist_lineage(self, graph: nx.DiGraph, data_id: str) -> None:
        if not self.enabled:
            return

        try:
            lineage_nodes = {data_id, *nx.ancestors(graph, data_id), *nx.descendants(graph, data_id)}
        except nx.NetworkXError:
            lineage_nodes = set(graph.nodes)

        subgraph = graph.subgraph(lineage_nodes)

        try:
            with self._driver.session() as session:
                for node_id, attrs in subgraph.nodes(data=True):
                    session.run(
                        """
                        MERGE (n:LineageNode {id: $id})
                        SET n.node_type = $node_type, n.name = $name
                        """,
                        id=node_id,
                        node_type=attrs.get("node_type", "unknown"),
                        name=attrs.get("name", node_id),
                    )

                for source, target in subgraph.edges():
                    session.run(
                        """
                        MATCH (a:LineageNode {id: $source_id})
                        MATCH (b:LineageNode {id: $target_id})
                        MERGE (a)-[:FLOWS_TO]->(b)
                        """,
                        source_id=source,
                        target_id=target,
                    )
        except Exception as exc:  # pragma: no cover - defensive runtime branch
            logger.warning("Failed to persist lineage graph for %s: %s", data_id, exc)

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()


class DataLineageTracker:
    """Governance-side lineage tracker backed by a NetworkX graph."""

    def __init__(
        self,
        graph: nx.DiGraph | None = None,
        neo4j_store: Neo4jLineageStore | Any | None = None,
    ) -> None:
        self.graph = graph or nx.DiGraph()
        self.neo4j_store = neo4j_store

    def record_lineage(
        self,
        data_id: str,
        source: str | dict[str, Any],
        transformations: list[str | dict[str, Any]] | None,
        destinations: list[str | dict[str, Any]] | None,
    ) -> None:
        source_node = self._normalize_node(source, default_type="source")
        data_node = self._normalize_node(
            {"id": data_id, "type": "dataset", "name": data_id},
            default_type="dataset",
        )
        transform_nodes = [
            self._normalize_node(node, default_type="transform") for node in (transformations or [])
        ]
        destination_nodes = [
            self._normalize_node(node, default_type="destination") for node in (destinations or [])
        ]

        ordered_nodes = [source_node, data_node, *transform_nodes]
        for node in ordered_nodes:
            self._upsert_node(node)

        for current, nxt in zip(ordered_nodes, ordered_nodes[1:]):
            self.graph.add_edge(current["id"], nxt["id"])

        attachment_point = ordered_nodes[-1]
        for destination in destination_nodes:
            self._upsert_node(destination)
            self.graph.add_edge(attachment_point["id"], destination["id"])

        if self.neo4j_store is not None:
            self.neo4j_store.persist_lineage(self.graph, data_id)

    def trace_lineage(self, data_id: str) -> dict[str, Any]:
        if data_id not in self.graph:
            return {
                "data_id": data_id,
                "upstream": [],
                "downstream": [],
                "full_paths": [],
                "exists": False,
            }

        upstream = sorted(
            node_id
            for node_id in nx.ancestors(self.graph, data_id)
            if self.graph.in_degree(node_id) == 0
        )
        downstream = sorted(
            node_id
            for node_id in nx.descendants(self.graph, data_id)
            if self.graph.out_degree(node_id) == 0
        )

        full_paths: list[list[str]] = []
        for source_id in upstream or [data_id]:
            for target_id in downstream or [data_id]:
                for path in nx.all_simple_paths(self.graph, source_id, target_id):
                    if data_id in path:
                        full_paths.append(path)

        full_paths.sort()

        return {
            "data_id": data_id,
            "upstream": upstream,
            "downstream": downstream,
            "full_paths": full_paths,
            "exists": True,
        }

    def _upsert_node(self, node: dict[str, Any]) -> None:
        self.graph.add_node(
            node["id"],
            node_type=node.get("type", "unknown"),
            name=node.get("name", node["id"]),
            metadata=node.get("metadata", {}),
        )

    def _normalize_node(self, node: str | dict[str, Any], default_type: str) -> dict[str, Any]:
        if isinstance(node, str):
            return {"id": node, "type": default_type, "name": node, "metadata": {}}

        normalized = dict(node)
        normalized.setdefault("id", normalized.get("name"))
        if not normalized.get("id"):
            raise ValueError("Lineage node requires an 'id' field")
        normalized.setdefault("type", default_type)
        normalized.setdefault("name", normalized["id"])
        normalized.setdefault("metadata", {})
        return normalized
