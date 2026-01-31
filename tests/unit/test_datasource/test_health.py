"""
Unit tests for Data Source Health Monitor
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.datasource import (
    DataSourceConfig,
    DataSourceHealthMonitor,
    DataSourceRegistry,
    DataSourceType,
    HealthReport,
    HealthStatus,
)


class TestDataSourceHealthMonitor:
    """Tests for DataSourceHealthMonitor"""

    @pytest.fixture
    def registry(self):
        """Create a mock registry"""
        reg = MagicMock(spec=DataSourceRegistry)
        reg.get_config = AsyncMock()
        reg.update_health_status = AsyncMock(return_value=True)
        return reg

    @pytest.fixture
    def monitor(self, registry):
        """Create a health monitor instance"""
        return DataSourceHealthMonitor(registry)

    @pytest.fixture
    def healthy_config(self):
        """Create a config for a healthy source"""
        return DataSourceConfig(
            source_id="healthy_source", name="Healthy Source", source_type=DataSourceType.AKSHARE, enabled=True
        )

    @pytest.fixture
    def unhealthy_config(self):
        """Create a config for an unhealthy source"""
        return DataSourceConfig(
            source_id="unhealthy_source", name="Unhealthy Source", source_type=DataSourceType.AKSHARE, enabled=True
        )

    @pytest.mark.asyncio
    async def test_check_health_healthy_source(self, monitor, registry, healthy_config):
        """Test health check for a healthy source"""
        registry.get_config.return_value = healthy_config

        # Register a health check function that returns True
        async def always_healthy(config):
            return True

        monitor.register_health_check("akshare", always_healthy)

        report = await monitor.check_health(healthy_config.source_id)

        assert report.status == HealthStatus.HEALTHY
        assert report.error is None
        assert report.latency_ms > 0

    @pytest.mark.asyncio
    async def test_check_health_unhealthy_source(self, monitor, registry, unhealthy_config):
        """Test health check for an unhealthy source"""
        registry.get_config.return_value = unhealthy_config

        # Register a health check function that returns False
        async def always_unhealthy(config):
            return False

        monitor.register_health_check("akshare", always_unhealthy)

        report = await monitor.check_health(unhealthy_config.source_id)

        assert report.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_check_health_with_exception(self, monitor, registry, healthy_config):
        """Test health check when an exception is raised"""
        registry.get_config.return_value = healthy_config

        async def raise_error(config):
            raise ConnectionError("Connection failed")

        monitor.register_health_check("akshare", raise_error)

        report = await monitor.check_health(healthy_config.source_id)

        assert report.status == HealthStatus.ERROR
        assert report.error == "Connection failed"

    @pytest.mark.asyncio
    async def test_check_health_disabled_source(self, monitor, registry, healthy_config):
        """Test health check for a disabled source"""
        healthy_config.enabled = False
        registry.get_config.return_value = healthy_config

        report = await monitor.check_health(healthy_config.source_id)

        assert report.status == HealthStatus.UNKNOWN
        assert "disabled" in report.error.lower()

    @pytest.mark.asyncio
    async def test_check_health_not_found(self, monitor, registry):
        """Test health check for a non-existent source"""
        registry.get_config.return_value = None

        report = await monitor.check_health("nonexistent")

        assert report.status == HealthStatus.UNKNOWN
        assert "not found" in report.error.lower()

    @pytest.mark.asyncio
    async def test_check_all_sources(self, monitor, registry):
        """Test checking all sources"""
        configs = [
            DataSourceConfig(
                source_id=f"source_{i}", name=f"Source {i}", source_type=DataSourceType.AKSHARE, enabled=True
            )
            for i in range(3)
        ]

        for config in configs:
            registry.get_config.return_value = config

            async def healthy(config):
                return True

            monitor.register_health_check("akshare", healthy)

        # Mock list_sources to return our test sources
        from src.core.datasource import DataSourceInfo

        registry.list_sources = AsyncMock(
            return_value=[
                DataSourceInfo(
                    source_id=config.source_id, name=config.name, source_type=config.source_type, config=config
                )
                for config in configs
            ]
        )

        results = await monitor.check_all_sources()

        assert len(results) == 3
        for source_id in results:
            assert results[source_id].status == HealthStatus.HEALTHY


class TestPrometheusMetrics:
    """Tests for Prometheus metrics integration"""

    def test_metrics_are_defined(self):
        """Test that Prometheus metrics are properly defined"""
        from src.core.datasource import (
            DATASOURCE_HEALTH_STATUS,
            DATASOURCE_LATENCY_MS,
            DATASOURCE_LATENCY_SECONDS,
            DATASOURCE_REQUESTS_TOTAL,
        )

        assert DATASOURCE_REQUESTS_TOTAL is not None
        assert DATASOURCE_LATENCY_SECONDS is not None
        assert DATASOURCE_HEALTH_STATUS is not None
        assert DATASOURCE_LATENCY_MS is not None

    def test_metrics_have_correct_labels(self):
        """Test that metrics have correct label names"""
        from src.core.datasource import DATASOURCE_LATENCY_SECONDS, DATASOURCE_REQUESTS_TOTAL

        # Check label names
        assert "source_id" in DATASOURCE_REQUESTS_TOTAL._labelnames
        assert "status" in DATASOURCE_REQUESTS_TOTAL._labelnames
        assert "operation" in DATASOURCE_REQUESTS_TOTAL._labelnames

        assert "source_id" in DATASOURCE_LATENCY_SECONDS._labelnames
        assert "operation" in DATASOURCE_LATENCY_SECONDS._labelnames
