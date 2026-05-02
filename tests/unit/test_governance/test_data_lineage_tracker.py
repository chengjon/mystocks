from __future__ import annotations

from unittest.mock import MagicMock

from src.governance.lineage.tracker import DataLineageTracker, Neo4jLineageStore


def test_record_lineage_builds_networkx_path():
    tracker = DataLineageTracker()

    tracker.record_lineage(
        data_id="dataset.daily.000001",
        source={"id": "source.akshare", "type": "source", "name": "AkShare"},
        transformations=[
            {"id": "transform.normalize", "type": "transform", "name": "Normalize"},
            {"id": "transform.factorize", "type": "transform", "name": "Factorize"},
        ],
        destinations=["storage.postgresql.daily_kline", "api.market.daily_kline"],
    )

    trace = tracker.trace_lineage("dataset.daily.000001")

    assert trace["data_id"] == "dataset.daily.000001"
    assert trace["upstream"] == ["source.akshare"]
    assert sorted(trace["downstream"]) == ["api.market.daily_kline", "storage.postgresql.daily_kline"]
    assert ["source.akshare", "dataset.daily.000001", "transform.normalize", "transform.factorize", "storage.postgresql.daily_kline"] in trace["full_paths"]


def test_record_lineage_accepts_destination_metadata_dicts():
    tracker = DataLineageTracker()

    tracker.record_lineage(
        data_id="dataset.minute.000001",
        source={"id": "source.tdx", "type": "source", "name": "TDX"},
        transformations=[],
        destinations=[
            {"id": "storage.tdengine.minute", "type": "storage", "name": "TDengine"},
        ],
    )

    trace = tracker.trace_lineage("dataset.minute.000001")

    assert trace["downstream"] == ["storage.tdengine.minute"]
    assert tracker.graph.nodes["storage.tdengine.minute"]["node_type"] == "storage"


def test_trace_lineage_for_unknown_data_id_is_empty():
    tracker = DataLineageTracker()

    trace = tracker.trace_lineage("missing.dataset")

    assert trace == {
        "data_id": "missing.dataset",
        "upstream": [],
        "downstream": [],
        "full_paths": [],
        "exists": False,
    }


def test_neo4j_store_is_optional_and_non_blocking():
    tracker = DataLineageTracker(neo4j_store=Neo4jLineageStore())

    tracker.record_lineage(
        data_id="dataset.factor.000001",
        source={"id": "source.baostock", "type": "source", "name": "BaoStock"},
        transformations=[{"id": "transform.signal", "type": "transform", "name": "Signal"}],
        destinations=["storage.cache.factor"],
    )

    assert tracker.trace_lineage("dataset.factor.000001")["exists"] is True


def test_record_lineage_persists_to_optional_neo4j_store():
    mock_store = MagicMock()
    tracker = DataLineageTracker(neo4j_store=mock_store)

    tracker.record_lineage(
        data_id="dataset.factor.000300",
        source={"id": "source.tushare", "type": "source", "name": "Tushare"},
        transformations=[{"id": "transform.rank", "type": "transform", "name": "Rank"}],
        destinations=["storage.postgresql.factor_rank"],
    )

    mock_store.persist_lineage.assert_called_once()
