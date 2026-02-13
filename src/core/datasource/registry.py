"""
Data Source Registry Module

Unified data source registry that supports dynamic registration,
deregistration, and querying of data sources.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Data source health status"""

    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


class DataSourceType(str, Enum):
    """Supported data source types"""

    AKSHARE = "akshare"
    TUSHARE = "tushare"
    TDX = "tdx"
    BAOSTOCK = "baostock"
    CUSTOM = "custom"
    API = "api"


class DataSourceConfig(BaseModel):
    """Data source configuration model"""

    source_id: str = Field(..., description="Unique identifier for the data source")
    name: str = Field(..., description="Display name for the data source")
    source_type: DataSourceType = Field(..., description="Type of data source")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    base_url: Optional[str] = Field(None, description="Base URL for API requests")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    weight: int = Field(default=100, description="Load balancing weight (1-100)")
    enabled: bool = Field(default=True, description="Whether the data source is enabled")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DataSourceInfo(BaseModel):
    """Data source information returned by registry"""

    source_id: str
    name: str
    source_type: DataSourceType
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    config: DataSourceConfig
    metrics: Dict[str, Any] = Field(default_factory=dict)


class HealthReport(BaseModel):
    """Health check report for a data source"""

    source_id: str
    status: HealthStatus
    latency_ms: float = 0.0
    last_check: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class DataSourceRegistry:
    """
    Unified data source registry that manages all data source configurations
    and health statuses.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
        self._local_cache: Dict[str, DataSourceConfig] = {}
        self._health_status: Dict[str, HealthStatus] = {}
        self._health_timestamps: Dict[str, datetime] = {}

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
            await self._redis.ping()
            logger.info("Connected to Redis for DataSourceRegistry")
        except Exception:
            logger.warning("Failed to connect to Redis: %(e)s, using local cache only")

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def register(self, config: DataSourceConfig) -> bool:
        """
        Register a new data source or update existing one.

        Args:
            config: Data source configuration

        Returns:
            True if registration successful
        """
        try:
            self._local_cache[config.source_id] = config
            self._health_status[config.source_id] = HealthStatus.UNKNOWN

            if self._redis:
                await self._redis.hset("datasource:configs", config.source_id, config.model_dump_json())
                await self._redis.hset("datasource:health", config.source_id, HealthStatus.UNKNOWN.value)

            logger.info("Registered data source: {config.source_id")
            return True
        except Exception:
            logger.error("Failed to register data source {config.source_id}: %(e)s")
            return False

    async def unregister(self, source_id: str) -> bool:
        """
        Unregister a data source.

        Args:
            source_id: Unique identifier of the data source

        Returns:
            True if deregistration successful
        """
        try:
            self._local_cache.pop(source_id, None)
            self._health_status.pop(source_id, None)
            self._health_timestamps.pop(source_id, None)

            if self._redis:
                await self._redis.hdel("datasource:configs", source_id)
                await self._redis.hdel("datasource:health", source_id)

            logger.info("Unregistered data source: %(source_id)s")
            return True
        except Exception:
            logger.error("Failed to unregister data source %(source_id)s: %(e)s")
            return False

    async def get_config(self, source_id: str) -> Optional[DataSourceConfig]:
        """
        Get configuration for a specific data source.

        Args:
            source_id: Unique identifier of the data source

        Returns:
            DataSourceConfig or None if not found
        """
        if source_id in self._local_cache:
            return self._local_cache[source_id]

        if self._redis:
            try:
                config_json = await self._redis.hget("datasource:configs", source_id)
                if config_json:
                    config = DataSourceConfig.model_validate_json(config_json)
                    self._local_cache[source_id] = config
                    return config
            except Exception:
                logger.error("Failed to get config from Redis: %(e)s")

        return None

    async def list_sources(self) -> List[DataSourceInfo]:
        """
        List all registered data sources with their status.

        Returns:
            List of DataSourceInfo objects
        """
        results = []

        for source_id, config in self._local_cache.items():
            health = self._health_status.get(source_id, HealthStatus.UNKNOWN)
            last_check = self._health_timestamps.get(source_id)

            info = DataSourceInfo(
                source_id=source_id,
                name=config.name,
                source_type=config.source_type,
                health_status=health,
                last_check=last_check,
                config=config,
            )
            results.append(info)

        return results

    async def update_health_status(self, source_id: str, report: HealthReport) -> bool:
        """
        Update health status for a data source.

        Args:
            source_id: Unique identifier of the data source
            report: Health report from health check

        Returns:
            True if update successful
        """
        try:
            self._health_status[source_id] = report.status
            self._health_timestamps[source_id] = report.last_check

            if self._redis:
                await self._redis.hset("datasource:health", source_id, report.status.value)
                await self._redis.hset("datasource:health_ts", source_id, report.last_check.isoformat())
                if report.error:
                    await self._redis.hset("datasource:health_err", source_id, report.error)

            return True
        except Exception:
            logger.error("Failed to update health status: %(e)s")
            return False

    async def get_health_status(self, source_id: str) -> Optional[HealthReport]:
        """
        Get health status for a specific data source.

        Args:
            source_id: Unique identifier of the data source

        Returns:
            HealthReport or None if not found
        """
        status = self._health_status.get(source_id, HealthStatus.UNKNOWN)
        last_check = self._health_timestamps.get(source_id)

        if self._redis and not last_check:
            try:
                ts_str = await self._redis.hget("datasource:health_ts", source_id)
                if ts_str:
                    last_check = datetime.fromisoformat(ts_str)
            except Exception:
                pass

        return HealthReport(
            source_id=source_id,
            status=status,
            last_check=last_check or datetime.now(timezone.utc),
        )

    async def load_from_redis(self) -> None:
        """Load all data source configurations from Redis"""
        if not self._redis:
            return

        try:
            configs = await self._redis.hgetall("datasource:configs")
            for source_id, config_json in configs.items():
                try:
                    config = DataSourceConfig.model_validate_json(config_json)
                    self._local_cache[source_id] = config
                except Exception:
                    logger.error("Failed to parse config for %(source_id)s: %(e)s")

            logger.info("Loaded {len(self._local_cache)} data sources from Redis")
        except Exception:
            logger.error("Failed to load from Redis: %(e)s")
