"""
Data Asset Registry Module

Manages metadata for all datasets, providing asset discovery,
tracking, and catalog capabilities.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import json
import logging

logger = logging.getLogger(__name__)


class AssetType(str, Enum):
    """Types of data assets"""

    DATASET = "dataset"
    TABLE = "table"
    VIEW = "view"
    API = "api"
    MODEL = "model"
    REPORT = "report"


@dataclass
class DataAsset:
    """Data asset metadata"""

    asset_id: str
    name: str
    asset_type: AssetType
    source: str
    schema: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    owner: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    quality_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["asset_type"] = self.asset_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataAsset":
        """Create from dictionary"""
        data["asset_type"] = AssetType(data["asset_type"])
        return cls(**data)


class AssetStorage:
    """
    Storage backend for asset metadata.
    Uses PostgreSQL for persistence.
    """

    def __init__(self, db_connection):
        self._db = db_connection

    async def save(self, asset: DataAsset) -> bool:
        """
        Save an asset to storage.

        Args:
            asset: DataAsset to save

        Returns:
            True if successful
        """
        try:
            async with self._db.acquire_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO data_assets
                    (asset_id, name, asset_type, source, schema, description,
                     owner, tags, created_at, updated_at, access_count,
                     quality_score, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    ON CONFLICT (asset_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        asset_type = EXCLUDED.asset_type,
                        source = EXCLUDED.source,
                        schema = EXCLUDED.schema,
                        description = EXCLUDED.description,
                        owner = EXCLUDED.owner,
                        tags = EXCLUDED.tags,
                        updated_at = EXCLUDED.updated_at,
                        access_count = EXCLUDED.access_count,
                        quality_score = EXCLUDED.quality_score,
                        metadata = EXCLUDED.metadata
                    """,
                    asset.asset_id,
                    asset.name,
                    asset.asset_type.value,
                    asset.source,
                    json.dumps(asset.schema),
                    asset.description,
                    asset.owner,
                    json.dumps(asset.tags),
                    asset.created_at,
                    asset.updated_at,
                    asset.access_count,
                    asset.quality_score,
                    json.dumps(asset.metadata),
                )
            return True
        except Exception as e:
            logger.error(f"Failed to save asset {asset.asset_id}: {e}")
            return False

    async def get(self, asset_id: str) -> Optional[DataAsset]:
        """
        Get an asset by ID.

        Args:
            asset_id: Asset identifier

        Returns:
            DataAsset or None if not found
        """
        try:
            async with self._db.acquire_connection() as conn:
                row = await conn.fetchrow("SELECT * FROM data_assets WHERE asset_id = $1", asset_id)
                if row:
                    return DataAsset(
                        asset_id=row["asset_id"],
                        name=row["name"],
                        asset_type=AssetType(row["asset_type"]),
                        source=row["source"],
                        schema=json.loads(row["schema"] or "{}"),
                        description=row["description"] or "",
                        owner=row["owner"],
                        tags=json.loads(row["tags"] or "[]"),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        last_accessed=row["last_accessed"],
                        access_count=row["access_count"] or 0,
                        quality_score=row["quality_score"],
                        metadata=json.loads(row["metadata"] or "{}"),
                    )
        except Exception as e:
            logger.error(f"Failed to get asset {asset_id}: {e}")
        return None

    async def list(
        self,
        asset_type: Optional[AssetType] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DataAsset]:
        """
        List assets with optional filters.

        Args:
            asset_type: Filter by asset type
            source: Filter by source
            tags: Filter by tags (any match)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of DataAsset objects
        """
        assets = []
        query = "SELECT * FROM data_assets WHERE 1=1"
        params = []
        param_count = 0

        if asset_type:
            param_count += 1
            query += f" AND asset_type = ${param_count}"
            params.append(asset_type.value)

        if source:
            param_count += 1
            query += f" AND source = ${param_count}"
            params.append(source)

        if tags:
            param_count += 1
            query += f" AND tags::jsonb ?| array[{param_count}]"
            params.append(tags)

        query += f" ORDER BY updated_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])

        try:
            async with self._db.acquire_connection() as conn:
                for row in await conn.fetch(query, *params):
                    assets.append(
                        DataAsset(
                            asset_id=row["asset_id"],
                            name=row["name"],
                            asset_type=AssetType(row["asset_type"]),
                            source=row["source"],
                            schema=json.loads(row["schema"] or "{}"),
                            description=row["description"] or "",
                            owner=row["owner"],
                            tags=json.loads(row["tags"] or "[]"),
                            created_at=row["created_at"],
                            updated_at=row["updated_at"],
                            last_accessed=row["last_accessed"],
                            access_count=row["access_count"] or 0,
                            quality_score=row["quality_score"],
                            metadata=json.loads(row["metadata"] or "{}"),
                        )
                    )
        except Exception as e:
            logger.error(f"Failed to list assets: {e}")

        return assets

    async def delete(self, asset_id: str) -> bool:
        """
        Delete an asset.

        Args:
            asset_id: Asset identifier

        Returns:
            True if successful
        """
        try:
            async with self._db.acquire_connection() as conn:
                await conn.execute("DELETE FROM data_assets WHERE asset_id = $1", asset_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete asset {asset_id}: {e}")
            return False


class DataAssetRegistry:
    """
    Data asset registry that manages metadata for all datasets.
    """

    def __init__(self, storage: AssetStorage):
        self._storage = storage
        self._local_cache: Dict[str, DataAsset] = {}

    async def register(
        self,
        asset_id: str,
        name: str,
        asset_type: AssetType,
        source: str,
        schema: Optional[Dict[str, Any]] = None,
        description: str = "",
        owner: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Register a new data asset.

        Args:
            asset_id: Unique identifier for the asset
            name: Display name
            asset_type: Type of asset
            source: Data source
            schema: Schema definition
            description: Description
            owner: Owner/responsible person
            tags: Tags for categorization
            metadata: Additional metadata

        Returns:
            Asset ID if successful
        """
        asset = DataAsset(
            asset_id=asset_id,
            name=name,
            asset_type=asset_type,
            source=source,
            schema=schema or {},
            description=description,
            owner=owner,
            tags=tags or [],
            metadata=metadata or {},
        )

        success = await self._storage.save(asset)
        if success:
            self._local_cache[asset_id] = asset
            logger.info(f"Registered asset: {asset_id}")
            return asset_id

        return ""

    async def get(self, asset_id: str) -> Optional[DataAsset]:
        """
        Get an asset by ID.

        Args:
            asset_id: Asset identifier

        Returns:
            DataAsset or None if not found
        """
        # Check local cache first
        if asset_id in self._local_cache:
            return self._local_cache[asset_id]

        # Fetch from storage
        asset = await self._storage.get(asset_id)
        if asset:
            self._local_cache[asset_id] = asset

        return asset

    async def list(
        self,
        asset_type: Optional[AssetType] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[DataAsset]:
        """
        List assets with optional filters.

        Args:
            asset_type: Filter by asset type
            source: Filter by source
            tags: Filter by tags
            limit: Maximum number of results

        Returns:
            List of DataAsset objects
        """
        return await self._storage.list(asset_type=asset_type, source=source, tags=tags, limit=limit)

    async def update_metadata(self, asset_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update asset metadata.

        Args:
            asset_id: Asset identifier
            updates: Fields to update

        Returns:
            True if successful
        """
        asset = await self.get(asset_id)
        if not asset:
            return False

        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)

        asset.updated_at = datetime.utcnow()
        return await self._storage.save(asset)

    async def record_access(self, asset_id: str) -> bool:
        """
        Record an access to an asset.

        Args:
            asset_id: Asset identifier

        Returns:
            True if successful
        """
        asset = await self.get(asset_id)
        if not asset:
            return False

        asset.last_accessed = datetime.utcnow()
        asset.access_count += 1

        return await self._storage.save(asset)

    async def update_quality_score(self, asset_id: str, score: float) -> bool:
        """
        Update the quality score for an asset.

        Args:
            asset_id: Asset identifier
            score: Quality score (0-100)

        Returns:
            True if successful
        """
        return await self.update_metadata(asset_id, {"quality_score": score})

    async def discover_assets(self, db_connection) -> List[str]:
        """
        Auto-discover assets by scanning database tables.

        Args:
            db_connection: Database connection

        Returns:
            List of discovered asset IDs
        """
        discovered = []

        try:
            async with db_connection.acquire_connection() as conn:
                # Get list of tables
                tables = await conn.fetch(
                    """
                    SELECT table_name, table_schema
                    FROM information_schema.tables
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                    """
                )

                for table in tables:
                    table_name = table["table_name"]
                    schema_name = table["table_schema"]

                    asset_id = f"{schema_name}.{table_name}"

                    # Check if already registered
                    existing = await self.get(asset_id)
                    if not existing:
                        # Get column information
                        columns = await conn.fetch(
                            """
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns
                            WHERE table_schema = $1 AND table_name = $2
                            """,
                            schema_name,
                            table_name,
                        )

                        schema = {
                            "table_schema": schema_name,
                            "columns": [
                                {
                                    "name": col["column_name"],
                                    "type": col["data_type"],
                                    "nullable": col["is_nullable"] == "YES",
                                }
                                for col in columns
                            ],
                        }

                        # Register the discovered table
                        await self.register(
                            asset_id=asset_id,
                            name=table_name,
                            asset_type=AssetType.TABLE,
                            source=f"{schema_name}.{table_name}",
                            schema=schema,
                            description=f"Auto-discovered table: {table_name}",
                            tags=["auto-discovered"],
                        )

                        discovered.append(asset_id)

            logger.info(f"Discovered {len(discovered)} new assets")

        except Exception as e:
            logger.error(f"Failed to discover assets: {e}")

        return discovered

    def get_access_stats(self) -> Dict[str, Any]:
        """
        Get access statistics for all assets.

        Returns:
            Dictionary with access statistics
        """
        stats = {
            "total_assets": len(self._local_cache),
            "by_type": {},
            "top_accessed": [],
        }

        for asset in self._local_cache.values():
            # Count by type
            asset_type = asset.asset_type.value
            stats["by_type"][asset_type] = stats["by_type"].get(asset_type, 0) + 1

        # Sort by access count
        sorted_assets = sorted(self._local_cache.values(), key=lambda a: a.access_count, reverse=True)
        stats["top_accessed"] = [
            {"asset_id": a.asset_id, "name": a.name, "access_count": a.access_count} for a in sorted_assets[:10]
        ]

        return stats
