"""数据源工厂模式单元测试 - 数据源与模式切换部分
"""

import os
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from ._test_data_source_factory_support import (
    DataSourceConfig,
    DataSourceMode,
    HealthStatus,
    HealthStatusEnum,
    HybridDataSource,
    MockDataSource,
    RealDataSource,
)


BACKEND_PORT = os.getenv("BACKEND_PORT", "8020")
API_BASE_URL = f"http://localhost:{BACKEND_PORT}/api"


class _AsyncResponseContext:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class TestDataSourceConfig:
    """测试DataSourceConfig"""

    def test_data_source_config_creation(self):
        """测试数据源配置创建"""
        config = DataSourceConfig(name="Test Source", type="market", mode=DataSourceMode.MOCK, timeout=15.0)

        assert config.name == "Test Source"
        assert config.type == "market"
        assert config.mode == DataSourceMode.MOCK
        assert config.timeout == 15.0
        assert config.enabled is True
        assert config.fallback_enabled is True

    def test_data_source_config_defaults(self):
        """测试数据源配置默认值"""
        config = DataSourceConfig(name="Test", type="test")

        assert config.mode == DataSourceMode.MOCK
        assert config.timeout == 30.0
        assert config.retry_count == 3
        assert config.retry_delay == 1.0
        assert config.health_check_interval == 60.0
        assert config.fallback_enabled is True
        assert config.cache_enabled is True
        assert config.cache_ttl == 300


class TestMockDataSource:
    """测试MockDataSource"""

    @pytest.fixture
    def mock_config(self):
        """Mock配置fixture"""
        return DataSourceConfig(name="Mock Test", type="test", mode=DataSourceMode.MOCK)

    @pytest.mark.asyncio
    async def test_mock_data_source_initialize(self, mock_config):
        """测试Mock数据源初始化"""
        source = MockDataSource(mock_config)
        await source.initialize()

        assert source._session is not None
        assert source.metrics.total_requests == 0

        await source.cleanup()
        assert source._session is None

    @pytest.mark.asyncio
    async def test_mock_data_source_get_data_market(self, mock_config):
        """测试Mock数据源获取市场数据"""
        source = MockDataSource(mock_config)
        async with source:
            data = await source.get_data("market/overview")

            assert "indices" in data
            assert "up_count" in data
            assert "down_count" in data
            assert "total_volume" in data
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_mock_data_source_get_data_portfolio(self, mock_config):
        """测试Mock数据源获取投资组合数据"""
        source = MockDataSource(mock_config)
        async with source:
            data = await source.get_data("portfolio/summary")

            assert "total_value" in data
            assert "daily_pnl" in data
            assert "total_pnl" in data
            assert "positions" in data

    @pytest.mark.asyncio
    async def test_mock_data_source_metrics_update(self, mock_config):
        """测试Mock数据源指标更新"""
        source = MockDataSource(mock_config)
        async with source:
            await source.get_data("market/overview")
            assert source.metrics.total_requests == 1
            assert source.metrics.success_rate == 100.0
            assert source.metrics.error_count == 0

            with patch.object(source, "_mock_data", {"data": None}), pytest.raises(Exception):
                await source.get_data("market/overview")

            assert source.metrics.total_requests == 2
            assert source.metrics.error_count == 1
            assert source.metrics.success_rate == 50.0

    @pytest.mark.asyncio
    async def test_mock_data_source_health_check(self, mock_config):
        """测试Mock数据源健康检查"""
        source = MockDataSource(mock_config)
        async with source:
            health = await source.health_check()

            assert health.status == HealthStatusEnum.HEALTHY
            assert health.response_time > 0
            assert "Mock data source is healthy" in health.message
            assert isinstance(health.timestamp, datetime)


class TestRealDataSource:
    """测试RealDataSource"""

    @pytest.fixture
    def real_config(self):
        """Real数据源配置fixture"""
        return DataSourceConfig(
            name="Real Test",
            type="market",
            mode=DataSourceMode.REAL,
            base_url=API_BASE_URL,
        )

    @pytest.mark.asyncio
    async def test_real_data_source_missing_base_url(self):
        """测试缺少base_url的Real数据源"""
        config = DataSourceConfig(name="Test", type="test", mode=DataSourceMode.REAL)

        with pytest.raises(ValueError, match="Real data source.*requires base_url"):
            RealDataSource(config)

    @pytest.mark.asyncio
    async def test_real_data_source_get_data_success(self, real_config):
        """测试Real数据源成功获取数据"""
        source = RealDataSource(real_config)

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "success", "data": {"test": "value"}})

        async with source:
            with patch.object(source._session, "get", return_value=_AsyncResponseContext(mock_response)):
                data = await source.get_data("market/data")

            assert data["status"] == "success"
            assert data["data"]["test"] == "value"
            assert source.metrics.total_requests == 1
            assert source.metrics.success_rate == 100.0

    @pytest.mark.asyncio
    async def test_real_data_source_get_data_with_retry(self, real_config):
        """测试Real数据源重试机制"""
        source = RealDataSource(real_config)

        mock_fail_response = Mock()
        mock_fail_response.status = 500
        mock_fail_response.text = AsyncMock(return_value="Server Error")

        mock_success_response = Mock()
        mock_success_response.status = 200
        mock_success_response.json = AsyncMock(return_value={"status": "success"})

        async with source:
            with (
                patch.object(
                    source._session,
                    "get",
                    side_effect=[
                        _AsyncResponseContext(mock_fail_response),
                        _AsyncResponseContext(mock_fail_response),
                        _AsyncResponseContext(mock_success_response),
                    ],
                ),
                patch("asyncio.sleep"),
            ):
                data = await source.get_data("market/data")

            assert data["status"] == "success"
            assert source.metrics.total_requests == 1
            assert source.metrics.success_rate == 100.0

    @pytest.mark.asyncio
    async def test_real_data_source_get_data_all_retries_failed(self, real_config):
        """测试Real数据源所有重试都失败"""
        source = RealDataSource(real_config)

        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Server Error")

        async with source:
            with (
                patch.object(source._session, "get", return_value=_AsyncResponseContext(mock_response)),
                patch("asyncio.sleep"),pytest.raises(Exception),
            ):
                await source.get_data("market/data")

            assert source.metrics.total_requests == 1
            assert source.metrics.error_count == 1
            assert source.metrics.success_rate == 0.0

    @pytest.mark.asyncio
    async def test_real_data_source_health_check_success(self, real_config):
        """测试Real数据源健康检查成功"""
        source = RealDataSource(real_config)

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "healthy", "version": "1.0"})

        async with source:
            with patch.object(source._session, "get", return_value=_AsyncResponseContext(mock_response)):
                health = await source.health_check()

            assert health.status == HealthStatusEnum.HEALTHY
            assert "Real data source is healthy" in health.message

    @pytest.mark.asyncio
    async def test_real_data_source_health_check_failure(self, real_config):
        """测试Real数据源健康检查失败"""
        source = RealDataSource(real_config)

        async with source:
            with patch.object(source._session, "get", side_effect=aiohttp.ClientError("Connection failed")):
                health = await source.health_check()

            assert health.status == HealthStatusEnum.FAILED
            assert "Health check error" in health.message


class TestHybridDataSource:
    """测试HybridDataSource"""

    @pytest.fixture
    def hybrid_config(self):
        """Hybrid配置fixture"""
        return DataSourceConfig(
            name="Hybrid Test",
            type="market",
            mode=DataSourceMode.HYBRID,
            fallback_enabled=True,
        )

    @pytest.fixture
    def hybrid_source(self, hybrid_config):
        """Hybrid数据源fixture"""
        real_config = hybrid_config.model_copy(deep=True)
        real_config.mode = DataSourceMode.REAL
        real_config.base_url = API_BASE_URL
        real_source = RealDataSource(real_config)

        mock_config = hybrid_config.model_copy(deep=True)
        mock_config.mode = DataSourceMode.MOCK
        mock_source = MockDataSource(mock_config)

        return HybridDataSource(hybrid_config, real_source, mock_source)

    @pytest.mark.asyncio
    async def test_hybrid_data_source_real_success(self, hybrid_source):
        """测试Hybrid数据源Real成功"""
        with patch.object(hybrid_source.real_source, "get_data", new_callable=AsyncMock) as mock_real_get:
            mock_real_get.return_value = {
                "status": "success",
                "data": {"source": "real"},
            }

            data = await hybrid_source.get_data("market/data")

            assert data["status"] == "success"
            assert data["_source"] == "real"
            assert hybrid_source._fallback_count == 0
            mock_real_get.assert_called_once_with("market/data", None)

    @pytest.mark.asyncio
    async def test_hybrid_data_source_fallback_to_mock(self, hybrid_source):
        """测试Hybrid数据源fallback到Mock"""
        with (
            patch.object(hybrid_source.real_source, "get_data", new_callable=AsyncMock) as mock_real_get,
            patch.object(hybrid_source.mock_source, "get_data", new_callable=AsyncMock) as mock_mock_get,
        ):
            mock_real_get.side_effect = Exception("Real source failed")
            mock_mock_get.return_value = {
                "status": "success",
                "data": {"source": "mock"},
            }

            data = await hybrid_source.get_data("market/data")

            assert data["status"] == "success"
            assert data["_source"] == "mock_fallback"
            assert "Real source failed" in data["_fallback_reason"]
            assert hybrid_source._fallback_count == 1
            assert hybrid_source._last_fallback_time is not None

    @pytest.mark.asyncio
    async def test_hybrid_data_source_fallback_disabled(self, hybrid_config):
        """测试Hybrid数据源禁用fallback"""
        hybrid_config.fallback_enabled = False

        real_config = hybrid_config.model_copy(deep=True)
        real_config.mode = DataSourceMode.REAL
        real_config.base_url = API_BASE_URL
        real_source = RealDataSource(real_config)

        mock_config = hybrid_config.model_copy(deep=True)
        mock_config.mode = DataSourceMode.MOCK
        mock_source = MockDataSource(mock_config)

        hybrid_source = HybridDataSource(hybrid_config, real_source, mock_source)

        with patch.object(hybrid_source.real_source, "get_data", new_callable=AsyncMock) as mock_real_get:
            mock_real_get.side_effect = Exception("Real source failed")

            with pytest.raises(Exception):
                await hybrid_source.get_data("market/data")

            assert hybrid_source._fallback_count == 0

    @pytest.mark.asyncio
    async def test_hybrid_data_source_both_sources_failed(self, hybrid_source):
        """测试Hybrid数据源两个源都失败"""
        with (
            patch.object(hybrid_source.real_source, "get_data", new_callable=AsyncMock) as mock_real_get,
            patch.object(hybrid_source.mock_source, "get_data", new_callable=AsyncMock) as mock_mock_get,
        ):
            mock_real_get.side_effect = Exception("Real source failed")
            mock_mock_get.side_effect = Exception("Mock source failed")

            with pytest.raises(Exception) as exc_info:
                await hybrid_source.get_data("market/data")

            assert "Both real and mock sources failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_hybrid_data_source_health_check(self, hybrid_source):
        """测试Hybrid数据源健康检查"""
        mock_real_health = HealthStatus(
            status=HealthStatusEnum.FAILED,
            response_time=100,
            message="Real source failed",
            timestamp=datetime.now(),
        )
        mock_mock_health = HealthStatus(
            status=HealthStatusEnum.HEALTHY,
            response_time=50,
            message="Mock source healthy",
            timestamp=datetime.now(),
        )

        with (
            patch.object(hybrid_source.real_source, "health_check", new_callable=AsyncMock) as mock_real_health_check,
            patch.object(hybrid_source.mock_source, "health_check", new_callable=AsyncMock) as mock_mock_health_check,
        ):
            mock_real_health_check.return_value = mock_real_health
            mock_mock_health_check.return_value = mock_mock_health

            health = await hybrid_source.health_check()

            assert health.status == HealthStatusEnum.DEGRADED
            assert "Hybrid source degraded" in health.message

    def test_hybrid_data_source_fallback_stats(self, hybrid_source):
        """测试Hybrid数据源fallback统计"""
        stats = hybrid_source.get_fallback_stats()

        assert "fallback_count" in stats
        assert "last_fallback_time" in stats
        assert "real_metrics" in stats
        assert "mock_metrics" in stats
        assert stats["fallback_count"] == 0
