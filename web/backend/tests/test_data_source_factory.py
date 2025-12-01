"""
数据源工厂模式单元测试 (Week 1 Day 1)
验证环境变量驱动的模式切换、Hybrid fallback机制、动态配置热更新
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import aiohttp
import pytest
import yaml

from app.services.data_source_factory import (
    DataSourceConfig,
    DataSourceFactory,
    DataSourceHealthCheck,
    DataSourceMetrics,
    DataSourceMode,
    DataSourceStatus,
    DynamicConfigManager,
    HybridDataSource,
    MockDataSource,
    RealDataSource,
    get_dashboard_data,
    get_data_source,
    get_data_source_factory,
    get_data_source_mode,
    get_market_data,
    get_technical_analysis_data,
    is_fallback_enabled,
)


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
            # 成功请求
            await source.get_data("market/overview")
            assert source.metrics.total_requests == 1
            assert source.metrics.success_rate == 100.0
            assert source.metrics.error_count == 0

            # 模拟失败请求
            with patch.object(source, "_generate_mock_data", side_effect=Exception("Test error")):
                with pytest.raises(Exception):
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

            assert health.status == DataSourceStatus.HEALTHY
            assert health.response_time > 0
            assert "Mock data source is healthy" in health.message
            assert isinstance(health.timestamp, datetime)


class TestRealDataSource:
    """测试RealDataSource"""

    @pytest.fixture
    def real_config(self):
        """Real数据源配置fixture"""
        return DataSourceConfig(
            name="Real Test", type="market", mode=DataSourceMode.REAL, base_url="http://localhost:8000/api"
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

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            async with source:
                data = await source.get_data("market/data")

                assert data["status"] == "success"
                assert data["data"]["test"] == "value"

                # 验证metrics更新
                assert source.metrics.total_requests == 1
                assert source.metrics.success_rate == 100.0

    @pytest.mark.asyncio
    async def test_real_data_source_get_data_with_retry(self, real_config):
        """测试Real数据源重试机制"""
        source = RealDataSource(real_config)

        # 前两次失败，第三次成功
        mock_fail_response = Mock()
        mock_fail_response.status = 500
        mock_fail_response.text = AsyncMock(return_value="Server Error")

        mock_success_response = Mock()
        mock_success_response.status = 200
        mock_success_response.json = AsyncMock(return_value={"status": "success"})

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.side_effect = [
                mock_fail_response,  # 第一次失败
                mock_fail_response,  # 第二次失败
                mock_success_response,  # 第三次成功
            ]

            with patch("asyncio.sleep"):  # 跳过sleep
                async with source:
                    data = await source.get_data("market/data")

                    assert data["status"] == "success"
                    assert source.metrics.total_requests == 1  # 只成功后计入
                    assert source.metrics.success_rate == 100.0

    @pytest.mark.asyncio
    async def test_real_data_source_get_data_all_retries_failed(self, real_config):
        """测试Real数据源所有重试都失败"""
        source = RealDataSource(real_config)

        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Server Error")

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            with patch("asyncio.sleep"):  # 跳过sleep
                async with source:
                    with pytest.raises(Exception):
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

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            async with source:
                health = await source.health_check()

                assert health.status == DataSourceStatus.HEALTHY
                assert "Real data source is healthy" in health.message
                assert health.details["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_real_data_source_health_check_failure(self, real_config):
        """测试Real数据源健康检查失败"""
        source = RealDataSource(real_config)

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Connection failed")

            async with source:
                health = await source.health_check()

                assert health.status == DataSourceStatus.FAILED
                assert "Health check error" in health.message


class TestHybridDataSource:
    """测试HybridDataSource"""

    @pytest.fixture
    def hybrid_config(self):
        """Hybrid配置fixture"""
        return DataSourceConfig(name="Hybrid Test", type="market", mode=DataSourceMode.HYBRID, fallback_enabled=True)

    @pytest.fixture
    def hybrid_source(self, hybrid_config):
        """Hybrid数据源fixture"""
        real_config = hybrid_config.model_copy(deep=True)
        real_config.mode = DataSourceMode.REAL
        real_config.base_url = "http://localhost:8000/api"
        real_source = RealDataSource(real_config)

        mock_config = hybrid_config.model_copy(deep=True)
        mock_config.mode = DataSourceMode.MOCK
        mock_source = MockDataSource(mock_config)

        return HybridDataSource(hybrid_config, real_source, mock_source)

    @pytest.mark.asyncio
    async def test_hybrid_data_source_real_success(self, hybrid_source):
        """测试Hybrid数据源Real成功"""
        # Mock Real数据源成功
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "success", "data": {"source": "real"}})

        with patch.object(hybrid_source.real_source, "get_data", new_callable=AsyncMock) as mock_real_get:
            mock_real_get.return_value = {"status": "success", "data": {"source": "real"}}

            data = await hybrid_source.get_data("market/data")

            assert data["status"] == "success"
            assert data["_source"] == "real"
            assert hybrid_source._fallback_count == 0

            mock_real_get.assert_called_once_with("market/data", None)

    @pytest.mark.asyncio
    async def test_hybrid_data_source_fallback_to_mock(self, hybrid_source):
        """测试Hybrid数据源fallback到Mock"""
        # Mock Real数据源失败，Mock成功
        with (
            patch.object(hybrid_source.real_source, "get_data", new_callable=AsyncMock) as mock_real_get,
            patch.object(hybrid_source.mock_source, "get_data", new_callable=AsyncMock) as mock_mock_get,
        ):

            mock_real_get.side_effect = Exception("Real source failed")
            mock_mock_get.return_value = {"status": "success", "data": {"source": "mock"}}

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
        real_config.base_url = "http://localhost:8000/api"
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
        mock_real_health = DataSourceHealthCheck(
            status=DataSourceStatus.FAILED, response_time=100, message="Real source failed"
        )

        mock_mock_health = DataSourceHealthCheck(
            status=DataSourceStatus.HEALTHY, response_time=50, message="Mock source healthy"
        )

        with (
            patch.object(hybrid_source.real_source, "health_check", new_callable=AsyncMock) as mock_real_health_check,
            patch.object(hybrid_source.mock_source, "health_check", new_callable=AsyncMock) as mock_mock_health_check,
        ):

            mock_real_health_check.return_value = mock_real_health
            mock_mock_health_check.return_value = mock_mock_health

            health = await hybrid_source.health_check()

            assert health.status == DataSourceStatus.DEGRADED
            assert "Hybrid source degraded" in health.message
            assert "fallback_count" in health.details
            assert health.details["real_source"]["status"] == "failed"
            assert health.details["mock_source"]["status"] == "healthy"

    def test_hybrid_data_source_fallback_stats(self, hybrid_source):
        """测试Hybrid数据源fallback统计"""
        stats = hybrid_source.get_fallback_stats()

        assert "fallback_count" in stats
        assert "last_fallback_time" in stats
        assert "real_metrics" in stats
        assert "mock_metrics" in stats
        assert stats["fallback_count"] == 0


class TestDynamicConfigManager:
    """测试DynamicConfigManager"""

    @pytest.fixture
    def temp_config_file(self):
        """临时配置文件fixture"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {
                "version": "1.0",
                "data_sources": {"test": {"name": "Test Source", "type": "test", "enabled": True, "mode": "mock"}},
            }
            json.dump(config_data, f)
            temp_path = f.name

        yield temp_path

        # 清理
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_load_config_json(self, temp_config_file):
        """测试加载JSON配置文件"""
        manager = DynamicConfigManager(temp_config_file)
        config = await manager.load_config()

        assert config["version"] == "1.0"
        assert "data_sources" in config
        assert config["data_sources"]["test"]["name"] == "Test Source"

    @pytest.mark.asyncio
    async def test_load_config_yaml(self):
        """测试加载YAML配置文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_data = {
                "version": "1.0",
                "data_sources": {"test": {"name": "Test Source", "type": "test", "enabled": True, "mode": "mock"}},
            }
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            manager = DynamicConfigManager(temp_path)
            config = await manager.load_config()

            assert config["version"] == "1.0"
            assert "data_sources" in config
            assert config["data_sources"]["test"]["name"] == "Test Source"

        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_load_config_file_not_exists(self):
        """测试配置文件不存在时创建默认配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent_config.json"
            manager = DynamicConfigManager(str(config_path))

            config = await manager.load_config()

            assert config is not None
            assert "version" in config
            assert "data_sources" in config
            assert config_path.exists()  # 文件应该被创建

    @pytest.mark.asyncio
    async def test_config_watcher(self, temp_config_file):
        """测试配置文件变化监听"""
        manager = DynamicConfigManager(temp_config_file)
        callback_called = False
        old_config_value = None
        new_config_value = None

        async def test_callback(old_config, new_config):
            nonlocal callback_called, old_config_value, new_config_value
            callback_called = True
            old_config_value = old_config
            new_config_value = new_config

        manager.add_watcher(test_callback)

        # 启动监控任务
        watch_task = asyncio.create_task(manager.watch_config_changes())

        try:
            # 等待一小段时间让监控开始
            await asyncio.sleep(0.1)

            # 修改配置文件
            new_config = {
                "version": "2.0",
                "data_sources": {
                    "test": {"name": "Updated Test Source", "type": "test", "enabled": True, "mode": "real"}
                },
            }

            with open(temp_config_file, "w") as f:
                json.dump(new_config, f)

            # 等待变化检测
            await asyncio.sleep(0.2)

            assert callback_called
            assert old_config_value["version"] == "1.0"
            assert new_config_value["version"] == "2.0"

        finally:
            watch_task.cancel()
            try:
                await watch_task
            except asyncio.CancelledError:
                pass


class TestDataSourceFactory:
    """测试DataSourceFactory"""

    @pytest.fixture
    def temp_config_file(self):
        """临时工厂配置文件fixture"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "market": {
                        "name": "Market Data Source",
                        "type": "market",
                        "enabled": True,
                        "mode": "mock",
                        "timeout": 15.0,
                    },
                    "dashboard": {
                        "name": "Dashboard Data Source",
                        "type": "dashboard",
                        "enabled": False,  # 禁用这个数据源
                        "mode": "mock",
                    },
                },
                "global_settings": {"default_timeout": 30.0, "health_check_interval": 60.0},
            }
            json.dump(config_data, f)
            temp_path = f.name

        yield temp_path

        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_factory_initialization(self, temp_config_file):
        """测试工厂初始化"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        assert factory._initialized is True
        assert "market" in factory._data_sources
        assert "dashboard" not in factory._data_sources  # 被禁用
        assert len(factory.get_available_sources()) == 1

        await factory.cleanup()

    @pytest.mark.asyncio
    async def test_factory_get_data_source(self, temp_config_file):
        """测试获取数据源"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        source = await factory.get_data_source("market")
        assert source is not None
        assert isinstance(source, MockDataSource)

        # 获取不存在的数据源
        source = await factory.get_data_source("nonexistent")
        assert source is None

        await factory.cleanup()

    @pytest.mark.asyncio
    async def test_factory_get_data(self, temp_config_file):
        """测试通过工厂获取数据"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        data = await factory.get_data("market", "overview")
        assert "indices" in data

        # 获取不存在的数据源数据
        with pytest.raises(ValueError, match="Data source 'nonexistent' not found"):
            await factory.get_data("nonexistent", "test")

        await factory.cleanup()

    @pytest.mark.asyncio
    async def test_factory_health_check_all(self, temp_config_file):
        """测试工厂健康检查"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        health_results = await factory.health_check_all()

        assert "market" in health_results
        assert health_results["market"].status == DataSourceStatus.HEALTHY

        await factory.cleanup()

    @pytest.mark.asyncio
    async def test_factory_config_reload(self, temp_config_file):
        """测试工厂配置重载"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        initial_sources = factory.get_available_sources()

        # 修改配置文件，添加新的数据源
        config_data = {
            "version": "1.0",
            "data_sources": {
                "market": {"name": "Market Data Source", "type": "market", "enabled": True, "mode": "mock"},
                "technical": {
                    "name": "Technical Analysis Source",
                    "type": "technical_analysis",
                    "enabled": True,
                    "mode": "mock",
                },
            },
        }

        with open(temp_config_file, "w") as f:
            json.dump(config_data, f)

        # 等待配置重载
        await asyncio.sleep(0.1)

        updated_sources = factory.get_available_sources()
        assert len(updated_sources) == 2
        assert "technical" in updated_sources

        await factory.cleanup()


class TestEnvironmentVariables:
    """测试环境变量驱动的功能"""

    def test_get_data_source_mode_mock_only(self):
        """测试仅Mock模式"""
        with patch.dict(os.environ, {"USE_MOCK_DATA": "true", "REAL_DATA_AVAILABLE": "false"}):
            mode = get_data_source_mode()
            assert mode == DataSourceMode.MOCK

    def test_get_data_source_mode_real_only(self):
        """测试仅Real模式"""
        with patch.dict(os.environ, {"USE_MOCK_DATA": "false", "REAL_DATA_AVAILABLE": "true"}):
            mode = get_data_source_mode()
            assert mode == DataSourceMode.REAL

    def test_get_data_source_mode_hybrid(self):
        """测试Hybrid模式"""
        with patch.dict(os.environ, {"USE_MOCK_DATA": "true", "REAL_DATA_AVAILABLE": "true"}):
            mode = get_data_source_mode()
            assert mode == DataSourceMode.HYBRID

    def test_is_fallback_enabled(self):
        """测试fallback启用状态"""
        with patch.dict(os.environ, {"FALLBACK_ENABLED": "true"}):
            assert is_fallback_enabled() is True

        with patch.dict(os.environ, {"FALLBACK_ENABLED": "false"}):
            assert is_fallback_enabled() is False


class TestConvenienceFunctions:
    """测试便捷函数"""

    @pytest.fixture
    def temp_config_file(self):
        """便捷函数测试配置文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "market": {"name": "Market Data Source", "type": "market", "enabled": True, "mode": "mock"},
                    "dashboard": {
                        "name": "Dashboard Data Source",
                        "type": "dashboard",
                        "enabled": True,
                        "mode": "mock",
                    },
                    "technical_analysis": {
                        "name": "Technical Analysis Source",
                        "type": "technical_analysis",
                        "enabled": True,
                        "mode": "mock",
                    },
                },
            }
            json.dump(config_data, f)
            temp_path = f.name

        yield temp_path

        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_get_market_data(self, temp_config_file):
        """测试获取市场数据便捷函数"""
        with patch("app.services.data_source_factory._global_factory", None):
            with patch("app.services.data_source_factory.DataSourceFactory") as MockFactory:
                mock_factory = Mock()
                MockFactory.return_value = mock_factory

                # 模拟工厂和数据源
                mock_data_source = AsyncMock()
                mock_data_source.get_data.return_value = {"market": "data"}
                mock_factory.get_data_source.return_value = mock_data_source
                mock_factory.initialize = AsyncMock()

                data = await get_market_data("overview")

                assert data == {"market": "data"}
                mock_factory.get_data_source.assert_called_once_with("market")
                mock_data_source.get_data.assert_called_once_with("overview", None)

    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, temp_config_file):
        """测试获取仪表盘数据便捷函数"""
        with patch("app.services.data_source_factory._global_factory", None):
            with patch("app.services.data_source_factory.DataSourceFactory") as MockFactory:
                mock_factory = Mock()
                MockFactory.return_value = mock_factory

                mock_data_source = AsyncMock()
                mock_data_source.get_data.return_value = {"dashboard": "data"}
                mock_factory.get_data_source.return_value = mock_data_source
                mock_factory.initialize = AsyncMock()

                data = await get_dashboard_data("summary")

                assert data == {"dashboard": "data"}
                mock_factory.get_data_source.assert_called_once_with("dashboard")
                mock_data_source.get_data.assert_called_once_with("summary", None)

    @pytest.mark.asyncio
    async def test_get_technical_analysis_data(self, temp_config_file):
        """测试获取技术分析数据便捷函数"""
        with patch("app.services.data_source_factory._global_factory", None):
            with patch("app.services.data_source_factory.DataSourceFactory") as MockFactory:
                mock_factory = Mock()
                MockFactory.return_value = mock_factory

                mock_data_source = AsyncMock()
                mock_data_source.get_data.return_value = {"technical": "data"}
                mock_factory.get_data_source.return_value = mock_data_source
                mock_factory.initialize = AsyncMock()

                data = await get_technical_analysis_data("indicators")

                assert data == {"technical": "data"}
                mock_factory.get_data_source.assert_called_once_with("technical_analysis")
                mock_data_source.get_data.assert_called_once_with("indicators", None)


class TestIntegrationScenarios:
    """集成测试场景"""

    @pytest.mark.asyncio
    async def test_end_to_end_mock_workflow(self):
        """端到端Mock工作流程测试"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"

            # 创建测试配置
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "market": {
                        "name": "Market Test",
                        "type": "market",
                        "enabled": True,
                        "mode": "mock",
                        "timeout": 10.0,
                    }
                },
            }

            with open(config_file, "w") as f:
                json.dump(config_data, f)

            # 创建工厂
            factory = DataSourceFactory(str(config_file))
            await factory.initialize()

            try:
                # 测试完整工作流程
                # 1. 获取数据源
                source = await factory.get_data_source("market")
                assert source is not None

                # 2. 获取数据
                data = await factory.get_data("market", "overview")
                assert "indices" in data

                # 3. 健康检查
                health_results = await factory.health_check_all()
                assert health_results["market"].status == DataSourceStatus.HEALTHY

                # 4. 获取指标
                metrics = factory.get_source_metrics("market")
                assert metrics.total_requests > 0
                assert metrics.success_rate > 0

            finally:
                await factory.cleanup()

    @pytest.mark.asyncio
    async def test_hybrid_fallback_workflow(self):
        """Hybrid fallback工作流程测试"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "hybrid_config.json"

            # 创建Hybrid测试配置
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "market": {
                        "name": "Hybrid Market Test",
                        "type": "market",
                        "enabled": True,
                        "mode": "hybrid",
                        "base_url": "http://invalid-url-that-will-fail.com/api",
                        "fallback_enabled": True,
                        "timeout": 5.0,
                        "retry_count": 1,
                    }
                },
            }

            with open(config_file, "w") as f:
                json.dump(config_data, f)

            # 创建工厂
            factory = DataSourceFactory(str(config_file))
            await factory.initialize()

            try:
                # 测试Hybrid fallback
                data = await factory.get_data("market", "overview")

                # 应该fallback到Mock数据
                assert "indices" in data
                assert data.get("_source") == "mock_fallback"

                # 检查fallback统计
                hybrid_source = factory._data_sources["market"]
                assert isinstance(hybrid_source, HybridDataSource)
                assert hybrid_source._fallback_count == 1

                # 健康检查应该显示DEGRADED状态
                health_results = await factory.health_check_all()
                assert health_results["market"].status == DataSourceStatus.DEGRADED

            finally:
                await factory.cleanup()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
