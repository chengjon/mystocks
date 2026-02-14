"""
数据源工厂模式实现 (Week 1 Day 1)
支持环境变量驱动的模式切换：Mock/Real/Hybrid
实现动态配置热更新和fallback机制
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import aiofiles
import aiohttp
import yaml

from app.services.data_adapter import (
    DashboardDataSourceAdapter,
    DataDataSourceAdapter,
    StrategyDataSourceAdapter,
    TechnicalAnalysisDataSourceAdapter,
    WatchlistDataSourceAdapter,
)

# 导入数据源接口和适配器
from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource,
)
from app.services.market_data_adapter import MarketDataSourceAdapter

logger = logging.getLogger(__name__)

class DataSourceFactory:
    """数据源工厂 - 核心工厂类"""

    def __init__(self, config_file: str = "config/data_sources.json"):
        self.config_file = config_file
        self.config_manager = DynamicConfigManager(config_file)
        self._data_sources: Dict[str, IDataSource] = {}
        self._source_configs: Dict[str, DataSourceConfig] = {}
        self._initialized = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._config_watch_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """初始化工厂"""
        if self._initialized:
            return

        logger.info("Initializing DataSourceFactory...")

        # 加载配置
        config_data = await self.config_manager.load_config()

        # 创建数据源
        await self._create_data_sources(config_data)

        # 启动配置监控
        self.config_manager.add_watcher(self._on_config_changed)
        self._config_watch_task = asyncio.create_task(self.config_manager.watch_config_changes())

        # 启动健康检查
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        self._initialized = True
        logger.info("DataSourceFactory initialized successfully")

    async def _create_data_sources(self, config_data: Dict[str, Any]):
        """根据配置创建数据源"""
        data_sources_config = config_data.get("data_sources", {})

        for source_name, source_config in data_sources_config.items():
            try:
                config = DataSourceConfig(**source_config)
                self._source_configs[source_name] = config

                if not config.enabled:
                    logger.info("Data source '%(source_name)s' is disabled, skipping")
                    continue

                # 创建数据源实例
                data_source = await self._create_single_data_source(config)
                self._data_sources[source_name] = data_source

                logger.info("Data source '%(source_name)s' created successfully (mode: {config.mode})")

            except Exception:
                logger.error("Failed to create data source '%(source_name)s': %(e)s")

    async def _create_single_data_source(self, config: DataSourceConfig) -> IDataSource:
        """创建单个数据源实例"""
        source_type = config.type or "default"

        # 特定类型的数据源
        if source_type == "market":
            return MarketDataSourceAdapter(config.__dict__)

        if source_type == "data":
            return DataDataSourceAdapter(config.__dict__)

        if source_type == "dashboard":
            return DashboardDataSourceAdapter(config.__dict__)

        if source_type == "technical_analysis":
            return TechnicalAnalysisDataSourceAdapter(config.__dict__)

        if source_type == "strategy":
            return StrategyDataSourceAdapter(config.__dict__)

        if source_type == "watchlist":
            return WatchlistDataSourceAdapter(config.__dict__)

        # 通用数据源模式
        if config.mode == DataSourceMode.MOCK:
            return MockDataSource(config)

        elif config.mode == DataSourceMode.REAL:
            return RealDataSource(config)

        elif config.mode == DataSourceMode.HYBRID:
            # Hybrid模式需要创建Real和Mock两个数据源
            real_config = config.model_copy(deep=True)
            real_config.mode = DataSourceMode.REAL
            real_source = RealDataSource(real_config)

            mock_config = config.model_copy(deep=True)
            mock_config.mode = DataSourceMode.MOCK
            mock_source = MockDataSource(mock_config)

            return HybridDataSource(config, real_source, mock_source)

        else:
            raise ValueError(f"Unsupported data source mode: {config.mode}")

    async def get_data_source(self, source_name: str) -> Optional[IDataSource]:
        """获取数据源"""
        if not self._initialized:
            await self.initialize()

        return self._data_sources.get(source_name)

    async def get_data(self, source_name: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """通过数据源获取数据"""
        data_source = await self.get_data_source(source_name)
        if not data_source:
            raise ValueError(f"Data source '{source_name}' not found or not enabled")

        return await data_source.get_data(endpoint, params)

    async def get_data_with_fallback(
        self, source_name: str, endpoint: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """获取数据，支持自动fallback"""
        try:
            return await self.get_data(source_name, endpoint, params)
        except Exception as e:
            logger.warning("Primary data source '%(source_name)s' failed: %(e)s")

            # 尝试找到Mock数据源作为fallback
            mock_source_name = f"{source_name}_mock"
            mock_source = await self.get_data_source(mock_source_name)

            if mock_source:
                logger.info("Using fallback data source '%(mock_source_name)s'")
                return await mock_source.get_data(endpoint, params)
            else:
                raise e

    def get_available_sources(self) -> List[str]:
        """获取所有可用的数据源名称"""
        return list(self._data_sources.keys())

    def get_source_config(self, source_name: str) -> Optional[DataSourceConfig]:
        """获取数据源配置"""
        return self._source_configs.get(source_name)

    def get_source_metrics(self, source_name: str) -> Optional[DataSourceMetrics]:
        """获取数据源监控指标"""
        data_source = self._data_sources.get(source_name)
        return data_source.metrics if data_source else None

    async def health_check_all(self) -> Dict[str, HealthStatus]:
        """对所有数据源进行健康检查"""
        health_results = {}

        for source_name, data_source in self._data_sources.items():
            try:
                health_results[source_name] = await data_source.health_check()
            except Exception as e:
                logger.error("Health check failed for '%(source_name)s': %(e)s")
                health_results[source_name] = HealthStatus(
                    status=HealthStatusEnum.FAILED,
                    response_time=0,
                    message=f"Health check error: {str(e)}",
                    timestamp=datetime.now(),
                )

        return health_results

    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒进行一次健康检查
                health_results = await self.health_check_all()

                # 记录不健康的数据源
                for source_name, health in health_results.items():
                    if health.status != HealthStatusEnum.HEALTHY:
                        logger.warning("Data source '%(source_name)s' is {health.status.value}: {health.message}")

            except Exception:
                logger.error("Health check loop error: %(e)s")

    async def _on_config_changed(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """配置变化处理器"""
        logger.info("Configuration changed, recreating data sources...")

        try:
            # 清理旧的数据源
            await self._cleanup_data_sources()

            # 创建新的数据源
            await self._create_data_sources(new_config)

            logger.info("Data sources recreated successfully")

        except Exception:
            logger.error("Failed to recreate data sources: %(e)s")

    async def _cleanup_data_sources(self):
        """清理数据源"""
        for source_name, data_source in self._data_sources.items():
            try:
                await data_source.cleanup()
                logger.debug("Data source '%(source_name)s' cleaned up")
            except Exception:
                logger.error("Failed to cleanup data source '%(source_name)s': %(e)s")

        self._data_sources.clear()
        self._source_configs.clear()

    async def cleanup(self):
        """清理工厂资源"""
        logger.info("Cleaning up DataSourceFactory...")

        # 停止任务
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        if self._config_watch_task:
            self._config_watch_task.cancel()
            try:
                await self._config_watch_task
            except asyncio.CancelledError:
                pass

        # 清理数据源
        await self._cleanup_data_sources()

        self._initialized = False
        logger.info("DataSourceFactory cleaned up successfully")

    @asynccontextmanager
    async def get_context(self, source_name: str):
        """获取数据源上下文管理器"""
        data_source = await self.get_data_source(source_name)
        if not data_source:
            raise ValueError(f"Data source '{source_name}' not found")

        async with data_source:
            yield data_source


async def get_data_source_factory() -> DataSourceFactory:
    """获取全局数据源工厂实例"""
    global _global_factory
    if _global_factory is None:
        _global_factory = DataSourceFactory()
        await _global_factory.initialize()
    return _global_factory


async def get_data_source(source_name: str) -> Optional[IDataSource]:
    """便捷函数：获取数据源"""
    factory = await get_data_source_factory()
    return await factory.get_data_source(source_name)


async def get_market_data(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """便捷函数：获取市场数据"""
    factory = await get_data_source_factory()
    return await factory.get_data("market", endpoint, params)


async def get_dashboard_data(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """便捷函数：获取仪表盘数据"""
    factory = await get_data_source_factory()
    return await factory.get_data("dashboard", endpoint, params)


async def get_technical_analysis_data(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """便捷函数：获取技术分析数据"""
    factory = await get_data_source_factory()
    return await factory.get_data("technical_analysis", endpoint, params)


def get_data_source_mode() -> DataSourceMode:
    """从环境变量获取数据源模式"""
    use_mock = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
    real_available = os.getenv("REAL_DATA_AVAILABLE", "false").lower() == "true"

    if use_mock and not real_available:
        return DataSourceMode.MOCK
    elif not use_mock and real_available:
        return DataSourceMode.REAL
    else:
        return DataSourceMode.HYBRID


def is_fallback_enabled() -> bool:
    """检查是否启用fallback"""
    return os.getenv("FALLBACK_ENABLED", "true").lower() == "true"


