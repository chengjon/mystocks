"""
Unit tests for Data Asset Registry Module
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data_governance.asset import (
    DataAssetRegistry,
    AssetStorage,
    DataAsset,
    AssetType,
)


class TestAssetType:
    """Test cases for AssetType enum"""

    def test_all_asset_types(self):
        """Test all asset type values"""
        assert AssetType.DATASET.value == "dataset"
        assert AssetType.TABLE.value == "table"
        assert AssetType.VIEW.value == "view"
        assert AssetType.API.value == "api"
        assert AssetType.MODEL.value == "model"
        assert AssetType.REPORT.value == "report"


class TestDataAsset:
    """Test cases for DataAsset dataclass"""

    def test_create_dataset_asset(self):
        """Test creating a dataset asset"""
        asset = DataAsset(
            asset_id="daily_kline_000001",
            name="Daily Kline - 上证指数",
            asset_type=AssetType.DATASET,
            source="akshare",
            description="Daily k-line data for SSE index",
        )
        assert asset.asset_id == "daily_kline_000001"
        assert asset.asset_type == AssetType.DATASET
        assert asset.source == "akshare"
        assert asset.access_count == 0

    def test_create_table_asset(self):
        """Test creating a table asset"""
        asset = DataAsset(
            asset_id="public.stock_prices",
            name="Stock Prices Table",
            asset_type=AssetType.TABLE,
            source="postgresql",
            schema={"columns": [{"name": "code", "type": "varchar"}]},
            owner="data-team",
            tags=[" equities", " pricing"],
        )
        assert asset.asset_type == AssetType.TABLE
        assert asset.schema["columns"][0]["name"] == "code"
        assert "pricing" in asset.tags

    def test_to_dict(self):
        """Test converting asset to dictionary"""
        asset = DataAsset(
            asset_id="test_asset",
            name="Test Asset",
            asset_type=AssetType.DATASET,
            source="test",
        )
        data = asset.to_dict()
        assert data["asset_id"] == "test_asset"
        assert data["asset_type"] == "dataset"
        assert isinstance(data["created_at"], datetime)

    def test_from_dict(self):
        """Test creating asset from dictionary"""
        data = {
            "asset_id": "test_asset",
            "name": "Test Asset",
            "asset_type": "dataset",
            "source": "test",
            "schema": {},
            "description": "",
            "owner": None,
            "tags": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_accessed": None,
            "access_count": 0,
            "quality_score": None,
            "metadata": {},
        }
        asset = DataAsset.from_dict(data)
        assert asset.asset_id == "test_asset"
        assert asset.asset_type == AssetType.DATASET


class TestAssetStorage:
    """Test cases for AssetStorage class"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection"""
        db = MagicMock()
        db.acquire_connection = AsyncMock()
        return db

    @pytest.fixture
    def storage(self, mock_db):
        """Create an AssetStorage instance with mock db"""
        return AssetStorage(mock_db)

    @pytest.fixture
    def sample_asset(self):
        """Create a sample asset for testing"""
        return DataAsset(
            asset_id="test_asset",
            name="Test Asset",
            asset_type=AssetType.DATASET,
            source="test",
        )

    @pytest.mark.asyncio
    async def test_save_asset(self, storage, mock_db, sample_asset):
        """Test saving an asset"""
        mock_conn = AsyncMock()
        mock_db.acquire_connection.return_value.__aenter__.return_value = mock_conn

        result = await storage.save(sample_asset)

        assert result is True
        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_asset(self, storage, mock_db, sample_asset):
        """Test getting an asset by ID"""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={
                "asset_id": "test_asset",
                "name": "Test Asset",
                "asset_type": "dataset",
                "source": "test",
                "schema": "{}",
                "description": "",
                "owner": None,
                "tags": "[]",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_accessed": None,
                "access_count": 0,
                "quality_score": None,
                "metadata": "{}",
            }
        )
        mock_db.acquire_connection.return_value.__aenter__.return_value = mock_conn

        asset = await storage.get("test_asset")

        assert asset is not None
        assert asset.asset_id == "test_asset"

    @pytest.mark.asyncio
    async def test_get_asset_not_found(self, storage, mock_db):
        """Test getting a non-existent asset"""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_db.acquire_connection.return_value.__aenter__.return_value = mock_conn

        asset = await storage.get("nonexistent")

        assert asset is None

    @pytest.mark.asyncio
    async def test_list_assets(self, storage, mock_db):
        """Test listing assets"""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "asset_id": "asset1",
                    "name": "Asset 1",
                    "asset_type": "dataset",
                    "source": "test",
                    "schema": "{}",
                    "description": "",
                    "owner": None,
                    "tags": "[]",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "last_accessed": None,
                    "access_count": 0,
                    "quality_score": None,
                    "metadata": "{}",
                }
            ]
        )
        mock_db.acquire_connection.return_value.__aenter__.return_value = mock_conn

        assets = await storage.list(limit=10)

        assert len(assets) == 1
        assert assets[0].asset_id == "asset1"

    @pytest.mark.asyncio
    async def test_delete_asset(self, storage, mock_db):
        """Test deleting an asset"""
        mock_conn = AsyncMock()
        mock_db.acquire_connection.return_value.__aenter__.return_value = mock_conn

        result = await storage.delete("test_asset")

        assert result is True
        mock_conn.execute.assert_called_once()


class TestDataAssetRegistry:
    """Test cases for DataAssetRegistry class"""

    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage"""
        storage = MagicMock(spec=AssetStorage)
        storage.save = AsyncMock(return_value=True)
        storage.get = AsyncMock(return_value=None)
        storage.list = AsyncMock(return_value=[])
        return storage

    @pytest.fixture
    def registry(self, mock_storage):
        """Create a DataAssetRegistry instance"""
        return DataAssetRegistry(mock_storage)

    @pytest.mark.asyncio
    async def test_register_asset(self, registry, mock_storage):
        """Test registering a new asset"""
        result = await registry.register(
            asset_id="new_asset",
            name="New Asset",
            asset_type=AssetType.DATASET,
            source="test",
        )

        assert result == "new_asset"
        mock_storage.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_fails(self, registry, mock_storage):
        """Test that registering a duplicate asset fails"""
        existing_asset = DataAsset(
            asset_id="existing",
            name="Existing",
            asset_type=AssetType.DATASET,
            source="test",
        )
        mock_storage.get.return_value = existing_asset

        result = await registry.register(
            asset_id="existing",
            name="Existing",
            asset_type=AssetType.DATASET,
            source="test",
        )

        assert result == ""
        mock_storage.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_asset(self, registry, mock_storage):
        """Test getting an asset"""
        asset = DataAsset(
            asset_id="test_asset",
            name="Test Asset",
            asset_type=AssetType.DATASET,
            source="test",
        )
        mock_storage.get.return_value = asset

        result = await registry.get("test_asset")

        assert result is not None
        assert result.asset_id == "test_asset"

    @pytest.mark.asyncio
    async def test_get_asset_from_cache(self, registry, mock_storage):
        """Test getting an asset from local cache"""
        cached_asset = DataAsset(
            asset_id="cached",
            name="Cached",
            asset_type=AssetType.DATASET,
            source="test",
        )
        registry._local_cache["cached"] = cached_asset

        result = await registry.get("cached")

        assert result is not None
        assert result.asset_id == "cached"
        mock_storage.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_assets(self, registry, mock_storage):
        """Test listing assets with filters"""
        await registry.list(
            asset_type=AssetType.DATASET,
            source="test",
            limit=10,
        )

        mock_storage.list.assert_called_once_with(
            asset_type=AssetType.DATASET,
            source="test",
            tags=None,
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_update_metadata(self, registry, mock_storage):
        """Test updating asset metadata"""
        asset = DataAsset(
            asset_id="test_asset",
            name="Test Asset",
            asset_type=AssetType.DATASET,
            source="test",
        )
        mock_storage.get.return_value = asset

        result = await registry.update_metadata("test_asset", {"description": "Updated"})

        assert result is True
        mock_storage.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_access(self, registry, mock_storage):
        """Test recording an asset access"""
        asset = DataAsset(
            asset_id="test_asset",
            name="Test Asset",
            asset_type=AssetType.DATASET,
            source="test",
            access_count=5,
        )
        mock_storage.get.return_value = asset

        result = await registry.record_access("test_asset")

        assert result is True
        assert asset.access_count == 6

    @pytest.mark.asyncio
    async def test_update_quality_score(self, registry, mock_storage):
        """Test updating quality score"""
        asset = DataAsset(
            asset_id="test_asset",
            name="Test Asset",
            asset_type=AssetType.DATASET,
            source="test",
        )
        mock_storage.get.return_value = asset

        result = await registry.update_quality_score("test_asset", 85.5)

        assert result is True

    def test_get_access_stats(self, registry):
        """Test getting access statistics"""
        registry._local_cache = {
            "asset1": DataAsset(
                asset_id="asset1", name="Asset 1", asset_type=AssetType.DATASET, source="test", access_count=100
            ),
            "asset2": DataAsset(
                asset_id="asset2", name="Asset 2", asset_type=AssetType.TABLE, source="test", access_count=50
            ),
            "asset3": DataAsset(
                asset_id="asset3", name="Asset 3", asset_type=AssetType.DATASET, source="test", access_count=200
            ),
        }

        stats = registry.get_access_stats()

        assert stats["total_assets"] == 3
        assert stats["by_type"]["dataset"] == 2
        assert stats["by_type"]["table"] == 1
        assert len(stats["top_accessed"]) == 3
        assert stats["top_accessed"][0]["asset_id"] == "asset3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
