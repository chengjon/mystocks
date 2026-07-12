"""数据源工厂模式单元测试 - 便捷函数与集成场景部分
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from ._test_data_source_factory_support import (
    DataSourceFactory,
    HealthStatusEnum,
    data_source_factory_module,
    get_dashboard_data,
    get_market_data,
    get_technical_analysis_data,
)


class TestConvenienceFunctions:
    """测试便捷函数"""

    @pytest.fixture
    def temp_config_file(self):
        """便捷函数测试配置文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as file_handle:
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "market": {
                        "name": "Market Data Source",
                        "type": "market",
                        "enabled": True,
                        "mode": "mock",
                    },
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
            json.dump(config_data, file_handle)
            temp_path = file_handle.name

        yield temp_path
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_get_market_data(self, temp_config_file):
        """测试获取市场数据便捷函数"""
        with patch.object(data_source_factory_module, "_global_factory", None):
            with patch.object(data_source_factory_module, "DataSourceFactory") as mock_factory_class:
                mock_factory = Mock()
                mock_factory_class.return_value = mock_factory

                mock_factory.get_data = AsyncMock(return_value={"market": "data"})
                mock_factory.initialize = AsyncMock()

                data = await get_market_data("overview")

                assert data == {"market": "data"}
                mock_factory.get_data.assert_awaited_once_with("market", "overview", None)

    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, temp_config_file):
        """测试获取仪表盘数据便捷函数"""
        with patch.object(data_source_factory_module, "_global_factory", None):
            with patch.object(data_source_factory_module, "DataSourceFactory") as mock_factory_class:
                mock_factory = Mock()
                mock_factory_class.return_value = mock_factory

                mock_factory.get_data = AsyncMock(return_value={"dashboard": "data"})
                mock_factory.initialize = AsyncMock()

                data = await get_dashboard_data("summary")

                assert data == {"dashboard": "data"}
                mock_factory.get_data.assert_awaited_once_with("dashboard", "summary", None)

    @pytest.mark.asyncio
    async def test_get_technical_analysis_data(self, temp_config_file):
        """测试获取技术分析数据便捷函数"""
        with patch.object(data_source_factory_module, "_global_factory", None):
            with patch.object(data_source_factory_module, "DataSourceFactory") as mock_factory_class:
                mock_factory = Mock()
                mock_factory_class.return_value = mock_factory

                mock_factory.get_data = AsyncMock(return_value={"technical": "data"})
                mock_factory.initialize = AsyncMock()

                data = await get_technical_analysis_data("indicators")

                assert data == {"technical": "data"}
                mock_factory.get_data.assert_awaited_once_with("technical_analysis", "indicators", None)


class TestIntegrationScenarios:
    """集成测试场景"""

    @pytest.mark.asyncio
    async def test_end_to_end_mock_workflow(self):
        """端到端Mock工作流程测试"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            config_data = {
                "version": "1.0",
                "data_sources": {
                    "market": {
                        "name": "Market Test",
                        "type": "market",
                        "enabled": True,
                        "mode": "mock",
                        "timeout": 10.0,
                    },
                },
            }

            with open(config_file, "w") as file_handle:
                json.dump(config_data, file_handle)

            factory = DataSourceFactory(str(config_file))
            await factory.initialize()

            try:
                source = await factory.get_data_source("market")
                assert source is not None

                data = await factory.get_data("market", "overview")
                assert "indices" in data

                health_results = await factory.health_check_all()
                assert health_results["market"].status == HealthStatusEnum.HEALTHY

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
                    },
                },
            }

            with open(config_file, "w") as file_handle:
                json.dump(config_data, file_handle)

            factory = DataSourceFactory(str(config_file))
            await factory.initialize()

            try:
                data = await factory.get_data("market", "overview")

                assert "indices" in data
                assert data.get("_source") == "mock_fallback"

                hybrid_source = factory._data_sources["market"]
                assert getattr(hybrid_source, "_fallback_count", 0) == 1

                health_results = await factory.health_check_all()
                assert health_results["market"].status == HealthStatusEnum.DEGRADED
            finally:
                await factory.cleanup()
