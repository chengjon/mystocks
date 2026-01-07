"""
Unit tests for Data Source Registry
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.datasource import (
    DataSourceRegistry,
    DataSourceConfig,
    DataSourceInfo,
    DataSourceType,
    HealthStatus,
    HealthReport,
)


class TestDataSourceConfig:
    """Tests for DataSourceConfig model"""

    def test_create_config(self):
        """Test creating a data source config"""
        config = DataSourceConfig(
            source_id="test_source",
            name="Test Source",
            source_type=DataSourceType.AKSHARE,
            api_key="test_key",
            timeout=30,
            weight=100,
        )
        assert config.source_id == "test_source"
        assert config.name == "Test Source"
        assert config.source_type == DataSourceType.AKSHARE
        assert config.timeout == 30
        assert config.weight == 100
        assert config.enabled is True

    def test_config_defaults(self):
        """Test default values for config"""
        config = DataSourceConfig(source_id="test_source", name="Test Source", source_type=DataSourceType.TUSHARE)
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.weight == 100
        assert config.enabled is True


class TestDataSourceRegistry:
    """Tests for DataSourceRegistry"""

    @pytest.fixture
    def registry(self):
        """Create a registry instance"""
        return DataSourceRegistry()

    @pytest.fixture
    def sample_config(self):
        """Create a sample config"""
        return DataSourceConfig(
            source_id="test_akshare",
            name="Test Akshare",
            source_type=DataSourceType.AKSHARE,
            api_key="test_key",
            timeout=30,
        )

    @pytest.mark.asyncio
    async def test_register_datasource(self, registry, sample_config):
        """Test registering a data source"""
        result = await registry.register(sample_config)
        assert result is True
        assert sample_config.source_id in registry._local_cache

    @pytest.mark.asyncio
    async def test_unregister_datasource(self, registry, sample_config):
        """Test unregistering a data source"""
        await registry.register(sample_config)
        result = await registry.unregister(sample_config.source_id)
        assert result is True
        assert sample_config.source_id not in registry._local_cache

    @pytest.mark.asyncio
    async def test_get_config(self, registry, sample_config):
        """Test getting a config"""
        await registry.register(sample_config)
        config = await registry.get_config(sample_config.source_id)
        assert config is not None
        assert config.source_id == sample_config.source_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_config(self, registry):
        """Test getting a config that doesn't exist"""
        config = await registry.get_config("nonexistent")
        assert config is None

    @pytest.mark.asyncio
    async def test_list_sources(self, registry):
        """Test listing all data sources"""
        configs = [
            DataSourceConfig(source_id=f"source_{i}", name=f"Source {i}", source_type=DataSourceType.AKSHARE)
            for i in range(3)
        ]
        for config in configs:
            await registry.register(config)

        sources = await registry.list_sources()
        assert len(sources) == 3

    @pytest.mark.asyncio
    async def test_update_health_status(self, registry, sample_config):
        """Test updating health status"""
        await registry.register(sample_config)
        report = HealthReport(
            source_id=sample_config.source_id,
            status=HealthStatus.HEALTHY,
            latency_ms=10.5,
            last_check=datetime.utcnow(),
        )
        result = await registry.update_health_status(sample_config.source_id, report)
        assert result is True
        assert registry._health_status[sample_config.source_id] == HealthStatus.HEALTHY


class TestHealthReport:
    """Tests for HealthReport model"""

    def test_create_healthy_report(self):
        """Test creating a healthy report"""
        report = HealthReport(source_id="test", status=HealthStatus.HEALTHY, latency_ms=10.0)
        assert report.source_id == "test"
        assert report.status == HealthStatus.HEALTHY
        assert report.latency_ms == 10.0
        assert report.error is None

    def test_create_error_report(self):
        """Test creating an error report"""
        report = HealthReport(source_id="test", status=HealthStatus.ERROR, error="Connection failed")
        assert report.status == HealthStatus.ERROR
        assert report.error == "Connection failed"
