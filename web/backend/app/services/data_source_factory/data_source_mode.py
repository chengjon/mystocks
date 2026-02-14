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

class DataSourceMode(str, Enum):
    """数据源模式枚举"""

    MOCK = "mock"  # 完全使用模拟数据
    REAL = "real"  # 完全使用真实数据
    HYBRID = "hybrid"  # 混合模式：优先Real，失败时fallback到Mock


@dataclass
class DataSourceMetrics:
    """数据源监控指标"""

    availability: float = 0.0  # 可用性百分比 (0-100)
    response_time: float = 0.0  # 平均响应时间 (ms)
    success_rate: float = 0.0  # 成功率百分比 (0-100)
    error_count: int = 0  # 错误次数
    last_error: Optional[str] = None  # 最后错误信息
    last_check: Optional[datetime] = None  # 最后检查时间
    total_requests: int = 0  # 总请求数
    data_delay: Optional[float] = None  # 数据延迟 (秒)

    def record_request(self, success: bool = True, error_msg: Optional[str] = None):
        """记录请求结果，更新指标"""
        self.total_requests += 1
        if success:
            # 计算成功率 (移动平均)
            if self.total_requests == 1:
                self.success_rate = 100.0
            else:
                # 使用指数移动平均
                alpha = 0.1  # 平滑因子
                self.success_rate = alpha * 100.0 + (1 - alpha) * self.success_rate
        else:
            self.error_count += 1
            if error_msg:
                self.last_error = error_msg

            # 更新成功率
            if self.total_requests == 1:
                self.success_rate = 0.0
            else:
                failed_rate = (self.error_count / self.total_requests) * 100
                self.success_rate = 100.0 - failed_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()

    def record_success(self, response_time: float = 0.0):
        """记录成功请求，更新指标"""
        self.total_requests += 1
        self.response_time = response_time

        # 计算成功率 (移动平均)
        if self.total_requests == 1:
            self.success_rate = 100.0
        else:
            # 使用指数移动平均
            alpha = 0.1  # 平滑因子
            self.success_rate = alpha * 100.0 + (1 - alpha) * self.success_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()

    def record_error(self, response_time: float = 0.0, error_msg: str = ""):
        """记录错误，更新指标"""
        self.total_requests += 1
        self.error_count += 1
        if error_msg:
            self.last_error = error_msg

        # 更新成功率
        if self.total_requests == 1:
            self.success_rate = 0.0
        else:
            failed_rate = (self.error_count / self.total_requests) * 100
            self.success_rate = 100.0 - failed_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()


@dataclass
class DataSourceConfig:
    """数据源配置"""

    name: str
    type: str  # market, dashboard, technical_analysis, etc.
    enabled: bool = True
    mode: DataSourceMode = DataSourceMode.MOCK
    base_url: Optional[str] = None
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    health_check_interval: float = 60.0  # 健康检查间隔(秒)
    fallback_enabled: bool = True  # 是否启用fallback
    custom_headers: Dict[str, str] = field(default_factory=dict)
    cache_enabled: bool = True
    cache_ttl: int = 300  # 缓存时间(秒)


class BaseDataSource(IDataSource):
    """基础数据源实现"""

    def __init__(self, config: DataSourceConfig):
        super().__init__(config.__dict__)
        self.config_obj = config  # Keep the typed config object
        self.metrics = DataSourceMetrics()
        self._session: Optional[aiohttp.ClientSession] = None
        self._health_status: Optional[HealthStatus] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()

    async def initialize(self):
        """初始化数据源"""
        if not self._session:
            timeout = aiohttp.ClientTimeout(total=self.config_obj.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout, headers=self.config_obj.custom_headers)

    async def cleanup(self):
        """清理资源"""
        if self._session:
            await self._session.close()
            self._session = None

    def update_metrics(self, success: bool, response_time: float, error: str = None):
        """更新监控指标"""
        self.metrics.total_requests += 1
        self.metrics.last_check = datetime.now()

        if success:
            # 更新响应时间 (使用指数移动平均)
            if self.metrics.response_time == 0:
                self.metrics.response_time = response_time
            else:
                alpha = 0.3  # 平滑因子
                self.metrics.response_time = alpha * response_time + (1 - alpha) * self.metrics.response_time
        else:
            self.metrics.error_count += 1
            self.metrics.last_error = error

        # 计算成功率
        if self.metrics.total_requests > 0:
            self.metrics.success_rate = (
                (self.metrics.total_requests - self.metrics.error_count) / self.metrics.total_requests * 100
            )

        # 计算可用性 (基于最近的成功率)
        self.metrics.availability = self.metrics.success_rate

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "total_requests": self.metrics.total_requests,
            "success_rate": self.metrics.success_rate,
            "error_count": self.metrics.error_count,
            "last_check": self.metrics.last_check.isoformat() if self.metrics.last_check else None,
            "last_error": self.metrics.last_error,
            "response_time": self.metrics.response_time,
            "availability": self.metrics.availability,
        }


class MockDataSource(BaseDataSource):
    """Mock数据源"""

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self._mock_data = self._generate_mock_data()

    def _generate_mock_data(self) -> Dict[str, Any]:
        """生成模拟数据"""
        return {
            "status": "success",
            "data": {
                "market_overview": {
                    "indices": [
                        {"name": "上证指数", "value": 3200.15, "change": "+1.2%"},
                        {"name": "深证成指", "value": 10500.23, "change": "-0.8%"},
                        {"name": "创业板指", "value": 2150.45, "change": "+2.1%"},
                    ],
                    "up_count": 2156,
                    "down_count": 1832,
                    "total_volume": "8500亿",
                    "timestamp": datetime.now().isoformat(),
                },
                "portfolio": {
                    "total_value": 500000.00,
                    "daily_pnl": 2500.00,
                    "total_pnl": 15000.00,
                    "positions": [
                        {
                            "symbol": "000001",
                            "name": "平安银行",
                            "shares": 1000,
                            "price": 12.50,
                        },
                        {
                            "symbol": "000002",
                            "name": "万科A",
                            "shares": 500,
                            "price": 18.75,
                        },
                    ],
                },
            },
            "message": "Mock data generated successfully",
        }

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取Mock数据"""
        start_time = time.time()

        try:
            # 模拟网络延迟
            await asyncio.sleep(0.1)

            # 根据endpoint返回不同的mock数据
            if "market" in endpoint:
                data = self._mock_data["data"]["market_overview"]
            elif "portfolio" in endpoint:
                data = self._mock_data["data"]["portfolio"]
            else:
                data = self._mock_data

            response_time = (time.time() - start_time) * 1000
            self.update_metrics(True, response_time)

            logger.debug("Mock data returned for endpoint: %(endpoint)s")
            return data

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"Mock data generation failed: {str(e)}"
            self.update_metrics(False, response_time, error_msg)

            logger.error(error_msg)
            raise

    async def health_check(self) -> HealthStatus:
        """Mock数据源健康检查"""
        start_time = time.time()

        try:
            # Mock数据源总是健康的
            await asyncio.sleep(0.01)
            response_time = (time.time() - start_time) * 1000

            return HealthStatus(
                status=HealthStatusEnum.HEALTHY,
                response_time=response_time,
                message="Mock data source is healthy",
                timestamp=datetime.now(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=response_time,
                message=f"Mock health check failed: {str(e)}",
                timestamp=datetime.now(),
            )


class RealDataSource(BaseDataSource):
    """真实数据源"""

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        if not config.base_url:
            raise ValueError(f"Real data source '{config.name}' requires base_url")

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """从真实API获取数据"""
        if not self._session:
            await self.initialize()

        start_time = time.time()
        url = f"{self.config_obj.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        params = params or {}

        for attempt in range(self.config_obj.retry_count + 1):
            try:
                logger.debug("Fetching data from %(url)s (attempt {attempt + 1})")

                async with self._session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_time = (time.time() - start_time) * 1000
                        self.update_metrics(True, response_time)

                        logger.debug("Successfully fetched data from %(url)s")
                        return data
                    else:
                        error_msg = f"HTTP {response.status}: {await response.text()}"
                        raise aiohttp.ClientError(error_msg)

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                error_msg = f"Request failed (attempt {attempt + 1}): {str(e)}"

                if attempt < self.config_obj.retry_count:
                    logger.warning("%(error_msg)s, retrying in {self.config_obj.retry_delay}s...")
                    await asyncio.sleep(self.config_obj.retry_delay)
                else:
                    self.update_metrics(False, response_time, error_msg)
                    logger.error("All retries failed for %(url)s: %(error_msg)s")
                    raise

    async def health_check(self) -> HealthStatus:
        """真实数据源健康检查"""
        if not self._session:
            await self.initialize()

        start_time = time.time()

        try:
            # 使用健康检查端点
            health_url = f"{self.config_obj.base_url.rstrip('/')}/health"

            async with self._session.get(health_url) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    await response.json()
                    return HealthStatus(
                        status=HealthStatusEnum.HEALTHY,
                        response_time=response_time,
                        message="Real data source is healthy",
                        timestamp=datetime.now(),
                    )
                else:
                    return HealthStatus(
                        status=HealthStatusEnum.FAILED,
                        response_time=response_time,
                        message=f"Health check failed: HTTP {response.status}",
                        timestamp=datetime.now(),
                    )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=response_time,
                message=f"Health check error: {str(e)}",
                timestamp=datetime.now(),
            )


class HybridDataSource(BaseDataSource):
    """混合数据源：优先Real，失败时fallback到Mock"""

    def __init__(
        self,
        config: DataSourceConfig,
        real_source: RealDataSource,
        mock_source: MockDataSource,
    ):
        super().__init__(config)
        self.real_source = real_source
        self.mock_source = mock_source
        self._fallback_count = 0
        self._last_fallback_time: Optional[datetime] = None

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """混合数据获取：优先Real，失败时fallback到Mock"""
        start_time = time.time()

        if not self.config_obj.fallback_enabled:
            # 如果禁用fallback，只使用Real数据源
            return await self.real_source.get_data(endpoint, params)

        try:
            # 首先尝试真实数据源
            logger.debug("Trying real data source for endpoint: %(endpoint)s")
            data = await self.real_source.get_data(endpoint, params)

            # 重置fallback计数器
            if self._fallback_count > 0:
                logger.info("Real data source recovered for {self.config_obj.name}")
                self._fallback_count = 0
                self._last_fallback_time = None

            response_time = (time.time() - start_time) * 1000
            self.update_metrics(True, response_time)

            # 添加数据源标识
            if isinstance(data, dict):
                data["_source"] = "real"

            return data

        except Exception as real_error:
            logger.warning("Real data source failed for %(endpoint)s: {str(real_error)}")

            # Fallback到Mock数据源
            try:
                logger.debug("Falling back to mock data source for endpoint: %(endpoint)s")
                data = await self.mock_source.get_data(endpoint, params)

                # 更新fallback统计
                self._fallback_count += 1
                self._last_fallback_time = datetime.now()

                response_time = (time.time() - start_time) * 1000
                self.update_metrics(True, response_time, f"Fallback used: {str(real_error)}")

                logger.info("Fallback successful for %(endpoint)s (fallback count: {self._fallback_count})")

                # 添加数据源标识
                if isinstance(data, dict):
                    data["_source"] = "mock_fallback"
                    data["_fallback_reason"] = str(real_error)

                return data

            except Exception as mock_error:
                response_time = (time.time() - start_time) * 1000
                error_msg = f"Both real and mock sources failed: Real({real_error}), Mock({mock_error})"
                self.update_metrics(False, response_time, error_msg)

                logger.error(error_msg)
                raise Exception(error_msg)

    async def health_check(self) -> HealthStatus:
        """混合数据源健康检查"""
        start_time = time.time()

        try:
            # 检查真实数据源健康状态
            real_health = await self.real_source.health_check()
            mock_health = await self.mock_source.health_check()

            response_time = (time.time() - start_time) * 1000

            # 混合状态判断
            if real_health.status == HealthStatusEnum.HEALTHY:
                status = HealthStatusEnum.HEALTHY
                message = "Hybrid source healthy (real active)"
            elif mock_health.status == HealthStatusEnum.HEALTHY:
                status = HealthStatusEnum.DEGRADED
                message = "Hybrid source degraded (mock fallback active)"
            else:
                status = HealthStatusEnum.FAILED
                message = "Hybrid source failed (both real and mock failed)"

            return HealthStatus(
                status=status,
                response_time=response_time,
                message=message,
                timestamp=datetime.now(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=response_time,
                message=f"Hybrid health check failed: {str(e)}",
                timestamp=datetime.now(),
            )

    def get_fallback_stats(self) -> Dict[str, Any]:
        """获取fallback统计信息"""
        return {
            "fallback_count": self._fallback_count,
            "last_fallback_time": self._last_fallback_time.isoformat() if self._last_fallback_time else None,
            "real_metrics": self.real_source.get_metrics(),
            "mock_metrics": self.mock_source.get_metrics(),
        }


class DynamicConfigManager:
    """动态配置管理器 - 支持热更新"""

    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self._config_data: Dict[str, Any] = {}
        self._last_modified: Optional[float] = None
        self._watchers: List[Callable[[Dict[str, Any]], None]] = []

    async def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not self.config_file.exists():
                logger.warning("Config file {self.config_file} not found, creating default config")
                await self._create_default_config()

            async with aiofiles.open(self.config_file, "r", encoding="utf-8") as f:
                if self.config_file.suffix.lower() in [".yaml", ".yml"]:
                    content = await f.read()
                    self._config_data = yaml.safe_load(content) or {}
                else:
                    content = await f.read()
                    self._config_data = json.loads(content) if content else {}

            self._last_modified = self.config_file.stat().st_mtime
            logger.info("Configuration loaded from {self.config_file}")
            return self._config_data

        except Exception:
            logger.error("Failed to load config from {self.config_file}: %(e)s")
            # 返回默认配置
            return await self._get_default_config()

    async def watch_config_changes(self):
        """监控配置文件变化"""
        while True:
            try:
                if self.config_file.exists():
                    current_modified = self.config_file.stat().st_mtime
                    if self._last_modified and current_modified > self._last_modified:
                        logger.info("Configuration file changed, reloading...")
                        old_config = self._config_data.copy()
                        await self.load_config()

                        # 通知所有监听器
                        for watcher in self._watchers:
                            try:
                                await self._safe_call_watcher(watcher, old_config, self._config_data)
                            except Exception:
                                logger.error("Config change notification failed: %(e)s")

                await asyncio.sleep(5)  # 每5秒检查一次

            except Exception:
                logger.error("Config watching error: %(e)s")
                await asyncio.sleep(10)  # 出错时等待更长时间

    def add_watcher(self, callback: Callable[[Dict[str, Any]], None]):
        """添加配置变化监听器"""
        self._watchers.append(callback)

    def remove_watcher(self, callback: Callable[[Dict[str, Any]], None]):
        """移除配置变化监听器"""
        if callback in self._watchers:
            self._watchers.remove(callback)

    async def _safe_call_watcher(self, watcher: Callable, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """安全调用监听器"""
        if asyncio.iscoroutinefunction(watcher):
            await watcher(old_config, new_config)
        else:
            watcher(old_config, new_config)

    async def _create_default_config(self):
        """创建默认配置文件"""
        default_config = await self._get_default_config()

        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(self.config_file, "w", encoding="utf-8") as f:
            if self.config_file.suffix.lower() in [".yaml", ".yml"]:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            else:
                await f.write(json.dumps(default_config, indent=2, ensure_ascii=False))

        logger.info("Default configuration created at {self.config_file}")

    async def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version": "1.0",
            "data_sources": {
                "market": {
                    "name": "Market Data Source",
                    "type": "market",
                    "enabled": True,
                    "mode": os.getenv("USE_MOCK_DATA", "true").lower() == "true"
                    and DataSourceMode.MOCK
                    or DataSourceMode.REAL,
                    "base_url": os.getenv("REAL_DATA_AVAILABLE", "false").lower() == "true"
                    and "http://localhost:8000/api/market"
                    or None,
                    "timeout": 30.0,
                    "retry_count": 3,
                    "retry_delay": 1.0,
                    "health_check_interval": 60.0,
                    "fallback_enabled": True,
                    "cache_enabled": True,
                    "cache_ttl": 300,
                },
                "dashboard": {
                    "name": "Dashboard Data Source",
                    "type": "dashboard",
                    "enabled": True,
                    "mode": DataSourceMode.MOCK,
                    "base_url": None,
                    "timeout": 15.0,
                    "retry_count": 2,
                    "retry_delay": 0.5,
                    "health_check_interval": 30.0,
                    "fallback_enabled": False,
                    "cache_enabled": True,
                    "cache_ttl": 120,
                },
                "technical_analysis": {
                    "name": "Technical Analysis Data Source",
                    "type": "technical_analysis",
                    "enabled": True,
                    "mode": DataSourceMode.MOCK,
                    "base_url": None,
                    "timeout": 20.0,
                    "retry_count": 3,
                    "retry_delay": 1.0,
                    "health_check_interval": 60.0,
                    "fallback_enabled": True,
                    "cache_enabled": True,
                    "cache_ttl": 600,
                },
            },
            "global_settings": {
                "default_timeout": 30.0,
                "default_retry_count": 3,
                "default_retry_delay": 1.0,
                "health_check_interval": 60.0,
                "metrics_retention_hours": 24,
                "log_level": "INFO",
            },
        }


