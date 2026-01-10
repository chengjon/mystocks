"""
Unit tests for Data Lineage Tracking Module
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data_governance.lineage import (
    LineageTracker,
    LineageStorage,
    LineageNode,
    LineageEdge,
    LineageGraph,
    NodeType,
    OperationType,
)


class TestLineageNode:
    """Test cases for LineageNode dataclass"""

    def test_create_datasource_node(self):
        """Test creating a datasource node"""
        node = LineageNode(
            node_id="akshare_market",
            node_type=NodeType.DATASOURCE,
            name="Akshare Market Data",
        )
        assert node.node_id == "akshare_market"
        assert node.node_type == NodeType.DATASOURCE
        assert node.name == "Akshare Market Data"
        assert node.metadata == {}

    def test_create_dataset_node(self):
        """Test creating a dataset node"""
        node = LineageNode(
            node_id="daily_kline_000001",
            node_type=NodeType.DATASET,
            name="Daily Kline - 上证指数",
            metadata={"records": 1000, "date_range": "2024-01-01 to 2024-12-31"},
        )
        assert node.node_type == NodeType.DATASET
        assert node.metadata["records"] == 1000

    def test_node_timestamps(self):
        """Test node timestamp fields"""
        now = datetime.utcnow()
        node = LineageNode(
            node_id="test_node",
            node_type=NodeType.DATASET,
            name="Test Node",
        )
        assert node.created_at is not None
        assert node.updated_at is not None


class TestLineageEdge:
    """Test cases for LineageEdge dataclass"""

    def test_create_fetch_edge(self):
        """Test creating a fetch operation edge"""
        edge = LineageEdge(
            from_node="akshare_market",
            to_node="daily_kline_000001",
            operation=OperationType.FETCH,
        )
        assert edge.from_node == "akshare_market"
        assert edge.to_node == "daily_kline_000001"
        assert edge.operation == OperationType.FETCH

    def test_create_transform_edge(self):
        """Test creating a transform operation edge"""
        edge = LineageEdge(
            from_node="raw_data",
            to_node="processed_data",
            operation=OperationType.TRANSFORM,
            metadata={"transform_type": "ma_calculation"},
        )
        assert edge.operation == OperationType.TRANSFORM
        assert edge.metadata["transform_type"] == "ma_calculation"


class TestLineageStorage:
    """Test cases for LineageStorage class"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection"""
        db = MagicMock()
        db.acquire_connection = AsyncMock()
        return db

    @pytest.fixture
    def storage(self, mock_db):
        """Create a LineageStorage instance with mock db"""
        return LineageStorage(mock_db)

    @pytest.mark.asyncio
    async def test_save_node(self, storage, mock_db):
        """Test saving a lineage node"""
        node = LineageNode(
            node_id="test_node",
            node_type=NodeType.DATASET,
            name="Test Node",
        )
        mock_conn = AsyncMock()
        mock_db.acquire_connection.return_value.__aenter__.return_value = mock_conn

        await storage.save_node(node)

        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_edge(self, storage, mock_db):
        """Test saving a lineage edge"""
        edge = LineageEdge(
            from_node="source",
            to_node="target",
            operation=OperationType.FETCH,
        )
        mock_conn = AsyncMock()
        mock_db.acquire_connection.return_value.__aenter__.return_value = mock_conn

        await storage.save_edge(edge)

        mock_conn.execute.assert_called_once()


class TestLineageTracker:
    """Test cases for LineageTracker class"""

    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage"""
        storage = MagicMock(spec=LineageStorage)
        storage.save_node = AsyncMock()
        storage.save_edge = AsyncMock()
        storage.get_lineage = AsyncMock()
        return storage

    @pytest.fixture
    def tracker(self, mock_storage):
        """Create a LineageTracker instance"""
        return LineageTracker(mock_storage)

    def test_initial_state(self, tracker):
        """Test tracker initial state"""
        assert tracker._current_chain == []
        assert tracker._context_id is None

    def test_record_fetch(self, tracker):
        """Test recording a fetch operation"""
        tracker._current_chain = [LineageNode(node_id="source", node_type=NodeType.DATASOURCE, name="Source")]

        tracker.record_fetch("target_dataset")

        assert len(tracker._current_chain) == 2
        assert tracker._current_chain[-1].node_id == "target_dataset"
        assert tracker._current_chain[-1].node_type == NodeType.DATASET

    def test_record_transform(self, tracker):
        """Test recording a transform operation"""
        tracker._current_chain = [LineageNode(node_id="raw", node_type=NodeType.DATASET, name="Raw Data")]

        tracker.record_transform("processed", transform_type="ma_5")

        assert len(tracker._current_chain) == 2
        assert tracker._current_chain[-1].metadata["transform_type"] == "ma_5"

    def test_record_store(self, tracker):
        """Test recording a store operation"""
        tracker._current_chain = [LineageNode(node_id="data", node_type=NodeType.DATASET, name="Data")]

        tracker.record_store("tdengine", storage_type="tdengine")

        assert len(tracker._current_chain) == 2
        assert tracker._current_chain[-1].node_type == NodeType.STORAGE

    def test_record_serve(self, tracker):
        """Test recording a serve operation"""
        tracker._current_chain = [LineageNode(node_id="data", node_type=NodeType.DATASET, name="Data")]

        tracker.record_serve("api_response", endpoint="/api/market/kline")

        assert len(tracker._current_chain) == 2
        assert tracker._current_chain[-1].node_type == NodeType.API

    def test_get_current_chain(self, tracker):
        """Test getting the current lineage chain"""
        tracker._current_chain = [
            LineageNode(node_id="node1", node_type=NodeType.DATASOURCE, name="Node 1"),
            LineageNode(node_id="node2", node_type=NodeType.DATASET, name="Node 2"),
        ]

        chain = tracker.get_current_chain()

        assert len(chain) == 2
        assert chain[0].node_id == "node1"

    @pytest.mark.asyncio
    async def test_get_lineage(self, tracker, mock_storage):
        """Test getting lineage graph"""
        mock_storage.get_lineage.return_value = (
            [LineageNode(node_id="n1", node_type=NodeType.DATASET, name="N1")],
            [LineageEdge(from_node="n1", to_node="n2", operation=OperationType.FETCH)],
        )

        graph = await tracker.get_lineage("n1")

        assert isinstance(graph, LineageGraph)
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 1

    @pytest.mark.asyncio
    async def test_get_downstream_impact(self, tracker, mock_storage):
        """Test downstream impact analysis"""
        mock_storage.get_lineage.return_value = (
            [],
            [
                LineageEdge(from_node="n1", to_node="n2", operation=OperationType.FETCH),
                LineageEdge(from_node="n2", to_node="n3", operation=OperationType.TRANSFORM),
            ],
        )

        impacted = await tracker.get_downstream_impact("n1", max_levels=3)

        assert "n2" in impacted
        assert "n3" in impacted


class TestNodeType:
    """Test cases for NodeType enum"""

    def test_all_node_types(self):
        """Test all node type values"""
        assert NodeType.DATASOURCE.value == "datasource"
        assert NodeType.DATASET.value == "dataset"
        assert NodeType.API.value == "api"
        assert NodeType.STORAGE.value == "storage"
        assert NodeType.TRANSFORM.value == "transform"


class TestOperationType:
    """Test cases for OperationType enum"""

    def test_all_operation_types(self):
        """Test all operation type values"""
        assert OperationType.FETCH.value == "fetch"
        assert OperationType.TRANSFORM.value == "transform"
        assert OperationType.STORE.value == "store"
        assert OperationType.SERVE.value == "serve"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
