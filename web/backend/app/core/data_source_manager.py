"""
数据源配置中心

管理 Mock 数据与真实数据的切换配置。
支持按模块、按时段、按条件切换数据源。
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """数据源类型"""

    MOCK = "mock"
    REAL = "real"
    HYBRID = "hybrid"


@dataclass
class ModuleConfig:
    """模块数据源配置"""

    module_name: str
    data_source: DataSourceType = DataSourceType.MOCK
    fallback: DataSourceType = DataSourceType.REAL
    endpoints: List[str] = field(default_factory=list)
    cache_ttl: int = 300  # 缓存时间（秒）
    enabled: bool = True


class DataSourceManager:
    """数据源管理器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/data_sources.json"
        self.modules: Dict[str, ModuleConfig] = {}
        self._config_format = "modules"
        self._raw_config: Dict = {}
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self._raw_config = data
                self.modules.clear()

                if "modules" in data:
                    self._config_format = "modules"
                    for module_data in data.get("modules", []):
                        self.modules[module_data["name"]] = ModuleConfig(
                            module_name=module_data["name"],
                            data_source=DataSourceType(module_data.get("data_source", "mock")),
                            fallback=DataSourceType(module_data.get("fallback", "real")),
                            endpoints=module_data.get("endpoints", []),
                            cache_ttl=module_data.get("cache_ttl", 300),
                            enabled=module_data.get("enabled", True),
                        )
                    return

                if "data_sources" in data:
                    self._config_format = "data_sources"
                    for source_name, source_config in data.get("data_sources", {}).items():
                        mode = source_config.get("mode", "mock")
                        fallback = "mock" if source_config.get("fallback_enabled", False) and mode != "mock" else "real"
                        self.modules[source_name] = ModuleConfig(
                            module_name=source_name,
                            data_source=DataSourceType(mode),
                            fallback=DataSourceType(fallback),
                            endpoints=source_config.get("endpoints", []),
                            cache_ttl=source_config.get("cache_ttl", 300),
                            enabled=source_config.get("enabled", True),
                        )

    def save_config(self):
        """保存配置"""
        if self._config_format == "data_sources":
            data = dict(self._raw_config)
            data_sources = {
                name: dict(config)
                for name, config in data.get("data_sources", {}).items()
            }
            for module_name, module in self.modules.items():
                source_config = data_sources.get(module_name, {})
                source_config["enabled"] = module.enabled
                source_config["mode"] = module.data_source.value
                source_config["cache_ttl"] = module.cache_ttl
                source_config.setdefault("type", module_name)
                if "fallback_enabled" not in source_config:
                    source_config["fallback_enabled"] = module.fallback == DataSourceType.MOCK
                data_sources[module_name] = source_config
            data["data_sources"] = data_sources
        else:
            data = {
                "modules": [
                    {
                        "name": m.module_name,
                        "data_source": m.data_source.value,
                        "fallback": m.fallback.value,
                        "endpoints": m.endpoints,
                        "cache_ttl": m.cache_ttl,
                        "enabled": m.enabled,
                    }
                    for m in self.modules.values()
                ]
            }

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def set_module_source(self, module_name: str, source: DataSourceType):
        """设置模块数据源"""
        if module_name not in self.modules:
            self.modules[module_name] = ModuleConfig(module_name=module_name)
        self.modules[module_name].data_source = source
        self.save_config()

    def get_module_source(self, module_name: str) -> DataSourceType:
        """获取模块数据源"""
        if module_name in self.modules:
            return self.modules[module_name].data_source
        return DataSourceType.MOCK  # 默认使用 Mock

    def get_enabled_modules(self) -> List[str]:
        """获取已启用的模块"""
        return [m.module_name for m in self.modules.values() if m.enabled]

    def switch_all_to_real(self):
        """切换所有模块到真实数据"""
        for module in self.modules.values():
            module.data_source = DataSourceType.REAL
        self.save_config()

    def switch_all_to_mock(self):
        """切换所有模块到 Mock 数据"""
        for module in self.modules.values():
            module.data_source = DataSourceType.MOCK
        self.save_config()


# 预定义模块配置
DEFAULT_MODULE_CONFIG = {
    "modules": [
        {
            "name": "market",
            "data_source": "hybrid",
            "fallback": "mock",
            "endpoints": ["/api/market/stock/*", "/api/market/indices"],
            "cache_ttl": 60,
        },
        {"name": "data", "data_source": "real", "fallback": "mock", "endpoints": ["/api/data/*"], "cache_ttl": 300},
        {
            "name": "indicators",
            "data_source": "real",
            "fallback": "mock",
            "endpoints": ["/api/indicators/*"],
            "cache_ttl": 600,
        },
        {
            "name": "strategy",
            "data_source": "hybrid",
            "fallback": "mock",
            "endpoints": ["/api/strategy/*"],
            "cache_ttl": 300,
        },
        {
            "name": "stock_search",
            "data_source": "mock",
            "fallback": "real",
            "endpoints": ["/api/stock-search/*"],
            "cache_ttl": 3600,
        },
        {
            "name": "monitoring",
            "data_source": "real",
            "fallback": "mock",
            "endpoints": ["/api/monitoring/*", "/api/metrics/*"],
            "cache_ttl": 30,
        },
    ]
}


def init_default_config(config_path: str = "config/data_sources.json"):
    """初始化默认配置"""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(DEFAULT_MODULE_CONFIG, f, indent=2)
    logger.info("Default data source config saved to %s", config_path)
