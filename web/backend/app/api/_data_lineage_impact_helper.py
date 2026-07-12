"""Helpers for data lineage impact analysis."""

from __future__ import annotations

from typing import Any


def _find_path(request_node_id: str, node_id: str, edges: list[Any]) -> list[str]:
    path = [request_node_id]
    queue: list[tuple[str, list[str]]] = [(request_node_id, [])]
    found_path = None

    while queue and not found_path:
        current, current_path = queue.pop(0)
        if current == node_id:
            found_path = current_path
            break

        for edge in edges:
            if edge.from_node == current:
                queue.append((edge.to_node, current_path + [edge.to_node]))

    return path


def _find_level(request_node_id: str, node_id: str, edges: list[Any]) -> int:
    for edge in edges:
        if edge.from_node == request_node_id and edge.to_node == node_id:
            return 1

    level_queue: list[tuple[str, int]] = [(request_node_id, 0)]
    visited_level = {request_node_id}

    while level_queue:
        current, current_level = level_queue.pop(0)
        if current == node_id:
            return current_level

        for edge in edges:
            if edge.from_node == current and edge.to_node not in visited_level:
                visited_level.add(edge.to_node)
                level_queue.append((edge.to_node, current_level + 1))

    return 0


async def build_impacted_nodes(
    tracker: Any, request_node_id: str, impacted_node_ids: list[str]
) -> list[dict[str, Any]]:
    impacted_nodes: list[dict[str, Any]] = []

    for node_id in impacted_node_ids:
        nodes, edges = await tracker._storage.get_lineage(node_id)
        if not nodes:
            continue

        node = nodes[0]
        level = _find_level(request_node_id, node_id, edges)
        impacted_nodes.append(
            {
                "node_id": node.node_id,
                "node_type": node.node_type.value,
                "level": level,
                "path": _find_path(request_node_id, node_id, edges),
                "impact_type": "direct" if level == 1 else "indirect",
            },
        )

    return impacted_nodes
