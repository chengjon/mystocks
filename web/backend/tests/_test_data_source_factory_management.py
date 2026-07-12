"""数据源工厂模式单元测试 - 配置管理与工厂部分
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from ._test_data_source_factory_support import (
    DataSourceFactory,
    DataSourceMode,
    DynamicConfigManager,
    HealthStatusEnum,
    get_data_source_mode,
    is_fallback_enabled,
)


class TestDynamicConfigManager:
    """测试DynamicConfigManager"""

    @pytest.fixture
    def temp_config_file(self):
        """临时配置文件fixture"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as file_handle:
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "test": {
                        "name": "Test Source",
                        "type": "test",
                        "enabled": True,
                        "mode": "mock",
                    },
                },
            }
            json.dump(config_data, file_handle)
            temp_path = file_handle.name

        yield temp_path
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as file_handle:
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "test": {
                        "name": "Test Source",
                        "type": "test",
                        "enabled": True,
                        "mode": "mock",
                    },
                },
            }
            yaml.dump(config_data, file_handle)
            temp_path = file_handle.name

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
            assert config_path.exists()

    @pytest.mark.asyncio
    async def test_config_watcher(self, temp_config_file):
        """测试配置文件变化监听"""
        manager = DynamicConfigManager(temp_config_file)
        await manager.load_config()
        callback_called = False
        old_config_value = None
        new_config_value = None

        async def test_callback(old_config, new_config):
            nonlocal callback_called, old_config_value, new_config_value
            callback_called = True
            old_config_value = old_config
            new_config_value = new_config

        manager.add_watcher(test_callback)
        watch_task = asyncio.create_task(manager.watch_config_changes())

        try:
            await asyncio.sleep(0.1)

            new_config = {
                "version": "2.0",
                "data_sources": {
                    "test": {
                        "name": "Updated Test Source",
                        "type": "test",
                        "enabled": True,
                        "mode": "real",
                    },
                },
            }

            with open(temp_config_file, "w") as file_handle:
                json.dump(new_config, file_handle)

            old_config = manager._config_data.copy()
            await manager.load_config()
            await manager._safe_call_watcher(test_callback, old_config, manager._config_data)

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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as file_handle:
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
                        "enabled": False,
                        "mode": "mock",
                    },
                },
                "global_settings": {
                    "default_timeout": 30.0,
                    "health_check_interval": 60.0,
                },
            }
            json.dump(config_data, file_handle)
            temp_path = file_handle.name

        yield temp_path
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_factory_initialization(self, temp_config_file):
        """测试工厂初始化"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        assert factory._initialized is True
        assert "market" in factory._data_sources
        assert "dashboard" not in factory._data_sources
        assert len(factory.get_available_sources()) == 1

        await factory.cleanup()

    @pytest.mark.asyncio
    async def test_factory_get_data_source(self, temp_config_file):
        """测试获取数据源"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        source = await factory.get_data_source("market")
        assert source is not None
        assert source.__class__.__name__ == "MarketDataSourceAdapter"

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
        assert health_results["market"].status == HealthStatusEnum.HEALTHY

        await factory.cleanup()

    @pytest.mark.asyncio
    async def test_factory_config_reload(self, temp_config_file):
        """测试工厂配置重载"""
        factory = DataSourceFactory(temp_config_file)
        await factory.initialize()

        initial_sources = factory.get_available_sources()
        assert "market" in initial_sources

        config_data = {
            "version": "1.0",
            "data_sources": {
                "market": {
                    "name": "Market Data Source",
                    "type": "market",
                    "enabled": True,
                    "mode": "mock",
                },
                "technical": {
                    "name": "Technical Analysis Source",
                    "type": "technical_analysis",
                    "enabled": True,
                    "mode": "mock",
                },
            },
        }

        with open(temp_config_file, "w") as file_handle:
            json.dump(config_data, file_handle)

        old_config = factory.config_manager._config_data.copy()
        await factory.config_manager.load_config()
        await factory._on_config_changed(old_config, factory.config_manager._config_data)

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
