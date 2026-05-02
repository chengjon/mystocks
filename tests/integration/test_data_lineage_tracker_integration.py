from __future__ import annotations

from src.governance.lineage.tracker import DataLineageTracker


class RecordingStore:
    def __init__(self) -> None:
        self.calls: list[tuple[set[str], str]] = []

    def persist_lineage(self, graph, data_id: str) -> None:
        self.calls.append((set(graph.nodes), data_id))


def test_tracker_persists_complete_subgraph_to_optional_store():
    store = RecordingStore()
    tracker = DataLineageTracker(neo4j_store=store)

    tracker.record_lineage(
        data_id="dataset.daily.600000",
        source={"id": "source.akshare", "type": "source", "name": "AkShare"},
        transformations=[
            {"id": "transform.normalize", "type": "transform", "name": "Normalize"},
            {"id": "transform.aggregate", "type": "transform", "name": "Aggregate"},
        ],
        destinations=[
            {"id": "storage.postgresql.daily_kline", "type": "storage", "name": "PostgreSQL"},
            {"id": "api.market.daily_kline", "type": "api", "name": "Market API"},
        ],
    )

    trace = tracker.trace_lineage("dataset.daily.600000")

    assert store.calls == [
        (
            {
                "source.akshare",
                "dataset.daily.600000",
                "transform.normalize",
                "transform.aggregate",
                "storage.postgresql.daily_kline",
                "api.market.daily_kline",
            },
            "dataset.daily.600000",
        )
    ]
    assert trace["exists"] is True
    assert sorted(trace["downstream"]) == ["api.market.daily_kline", "storage.postgresql.daily_kline"]


def test_tracker_accumulates_multiple_datasets_without_cross_linking():
    tracker = DataLineageTracker()

    tracker.record_lineage(
        data_id="dataset.minute.000001",
        source="source.tdx",
        transformations=[],
        destinations=["storage.tdengine.minute"],
    )
    tracker.record_lineage(
        data_id="dataset.minute.000002",
        source="source.tdx",
        transformations=[],
        destinations=["storage.tdengine.minute"],
    )

    first_trace = tracker.trace_lineage("dataset.minute.000001")
    second_trace = tracker.trace_lineage("dataset.minute.000002")

    assert first_trace["full_paths"] == [["source.tdx", "dataset.minute.000001", "storage.tdengine.minute"]]
    assert second_trace["full_paths"] == [["source.tdx", "dataset.minute.000002", "storage.tdengine.minute"]]
