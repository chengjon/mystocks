"""
Support loader for data source factory split tests.
"""

from __future__ import annotations

import importlib
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from types import ModuleType


def _build_adapter_modules() -> dict[str, ModuleType]:
    data_adapter_module = ModuleType("app.services.data_adapter")
    market_data_adapter_module = ModuleType("app.services.market_data_adapter")

    class _AdapterBase:
        def __init__(self, config):
            self.config = config
            self.metrics = SimpleNamespace(
                total_requests=0,
                successful_requests=0,
                error_count=0,
                success_rate=0.0,
                response_time=0.0,
                availability=100.0,
                last_error=None,
                last_check=None,
            )
            self._fallback_count = 0

        async def initialize(self):
            return None

        async def cleanup(self):
            return None

        async def get_data(self, endpoint, params=None):
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.success_rate = 100.0
            self.metrics.last_check = datetime.now()

            mode = str(self.config.get("mode", "mock")).lower()
            payload = {"endpoint": endpoint, "params": params}

            if self.config.get("type") == "market":
                payload = {"indices": [{"symbol": "000001", "name": "上证指数"}]}

            if "hybrid" in mode:
                self._fallback_count += 1
                payload["_source"] = "mock_fallback"

            return payload

        async def health_check(self):
            mode = str(self.config.get("mode", "mock")).lower()
            status = HealthStatusEnum.DEGRADED if "hybrid" in mode else HealthStatusEnum.HEALTHY
            message = "Fallback active" if status == HealthStatusEnum.DEGRADED else "Stub adapter healthy"
            return HealthStatus(status=status, response_time=1.0, message=message, timestamp=datetime.now())

        def get_metrics(self):
            return self.metrics

    class MarketDataSourceAdapter(_AdapterBase):
        pass

    class DataDataSourceAdapter(_AdapterBase):
        pass

    class DashboardDataSourceAdapter(_AdapterBase):
        pass

    class TechnicalAnalysisDataSourceAdapter(_AdapterBase):
        pass

    class StrategyDataSourceAdapter(_AdapterBase):
        pass

    class WatchlistDataSourceAdapter(_AdapterBase):
        pass

    data_adapter_module.DashboardDataSourceAdapter = DashboardDataSourceAdapter
    data_adapter_module.DataDataSourceAdapter = DataDataSourceAdapter
    data_adapter_module.StrategyDataSourceAdapter = StrategyDataSourceAdapter
    data_adapter_module.TechnicalAnalysisDataSourceAdapter = TechnicalAnalysisDataSourceAdapter
    data_adapter_module.WatchlistDataSourceAdapter = WatchlistDataSourceAdapter
    market_data_adapter_module.MarketDataSourceAdapter = MarketDataSourceAdapter

    return {
        "app.services.data_adapter": data_adapter_module,
        "app.services.market_data_adapter": market_data_adapter_module,
    }


def _load_split_modules():
    package_paths = {
        "app": Path("web/backend/app"),
        "app.services": Path("web/backend/app/services"),
    }
    previous = {name: sys.modules.get(name) for name in package_paths}
    original_keys = set(sys.modules)

    for package_name, package_path in package_paths.items():
        fake_package = ModuleType(package_name)
        fake_package.__path__ = [str(package_path.resolve())]
        sys.modules[package_name] = fake_package

    for module_name, module in _build_adapter_modules().items():
        previous[module_name] = sys.modules.get(module_name)
        sys.modules[module_name] = module

    package = importlib.import_module("app.services.data_source_factory")
    factory_module = importlib.import_module("app.services.data_source_factory.data_source_factory")
    interface_module = importlib.import_module("app.services.data_source_interface")

    new_keys = {name for name in sys.modules if name not in original_keys}
    for name in new_keys:
        sys.modules.pop(name, None)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return package, factory_module, interface_module


data_source_factory_package, data_source_factory_module, data_source_interface_module = _load_split_modules()

DataSourceFactory = data_source_factory_package.DataSourceFactory
DataSourceConfig = data_source_factory_package.DataSourceConfig
DataSourceMode = data_source_factory_package.DataSourceMode
DynamicConfigManager = data_source_factory_package.DynamicConfigManager
HybridDataSource = data_source_factory_package.HybridDataSource
MockDataSource = data_source_factory_package.MockDataSource
RealDataSource = data_source_factory_package.RealDataSource
get_dashboard_data = data_source_factory_package.get_dashboard_data
get_data_source_mode = data_source_factory_package.get_data_source_mode
get_market_data = data_source_factory_package.get_market_data
get_technical_analysis_data = data_source_factory_package.get_technical_analysis_data
is_fallback_enabled = data_source_factory_package.is_fallback_enabled

HealthStatus = data_source_interface_module.HealthStatus
HealthStatusEnum = data_source_interface_module.HealthStatusEnum
