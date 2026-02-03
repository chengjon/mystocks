"""
Indicator Registry System
=========================

指标注册中心，管理所有指标的元数据注册、查询、验证功能。

功能:
- 指标注册/注销
- 指标查询（按名称、分类）
- 参数验证
- 版本控制
- 配置热重载支持1.0.

Version: 0
Author: MyStocks Project
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .indicator_metadata import (
    IndicatorCategory,
    IndicatorMetadata,
    IndicatorParameter,
    IndicatorTemplate,
    PanelType,
    ParameterConstraint,
)

logger = logging.getLogger(__name__)


@dataclass
class RegistryStats:
    """注册表统计信息"""

    total_indicators: int = 0
    by_category: Dict[str, int] = None
    by_complexity: Dict[str, int] = None
    deprecated_count: int = 0
    last_updated: str = ""

    def __post_init__(self):
        if self.by_category is None:
            self.by_category = {}
        if self.by_complexity is None:
            self.by_complexity = {}


class IndicatorRegistry:
    """
    指标注册中心

    单例模式，确保全局唯一的指标注册表
    """

    _instance: Optional["IndicatorRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "IndicatorRegistry":
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化注册表"""
        if not self._initialized:
            self._registry: Dict[str, IndicatorMetadata] = {}
            self._templates: Dict[str, IndicatorTemplate] = {}
            self._config_path: Optional[Path] = None
            self._last_reload: float = 0
            IndicatorRegistry._initialized = True
            logger.info("IndicatorRegistry initialized")

    def register(self, metadata: IndicatorMetadata) -> bool:
        """
        注册指标

        Args:
            metadata: 指标元数据

        Returns:
            是否注册成功（ False 表示已存在）
        """
        abbr = metadata.abbreviation.upper()

        if abbr in self._registry:
            logger.warning("指标 %(abbr)s 已存在，将被覆盖")
            self._registry[abbr].version

        self._registry[abbr] = metadata
        logger.info("指标 %(abbr)s v{metadata.version} 注册成功")

        return True

    def unregister(self, abbreviation: str) -> bool:
        """
        注销指标

        Args:
            abbreviation: 指标缩写

        Returns:
            是否成功注销
        """
        abbr = abbreviation.upper()

        if abbr not in self._registry:
            logger.warning("指标 %(abbr)s 不存在")
            return False

        del self._registry[abbr]
        logger.info("指标 %(abbr)s 已注销")
        return True

    def get(self, abbreviation: str) -> Optional[IndicatorMetadata]:
        """
        获取指标元数据

        Args:
            abbreviation: 指标缩写

        Returns:
            指标元数据，不存在返回 None
        """
        return self._registry.get(abbreviation.upper())

    def get_all(self) -> Dict[str, IndicatorMetadata]:
        """
        获取所有指标

        Returns:
            指标元数据字典
        """
        return self._registry.copy()

    def get_by_category(self, category: IndicatorCategory) -> Dict[str, IndicatorMetadata]:
        """
        按分类获取指标

        Args:
            category: 指标分类

        Returns:
            该分类下的所有指标
        """
        return {abbr: meta for abbr, meta in self._registry.items() if meta.category == category}

    def get_by_categories(self, categories: List[IndicatorCategory]) -> Dict[str, IndicatorMetadata]:
        """
        按多个分类获取指标

        Args:
            categories: 指标分类列表

        Returns:
            符合任一分类的所有指标
        """
        category_set = set(categories)
        return {abbr: meta for abbr, meta in self._registry.items() if meta.category in category_set}

    def get_enabled(self) -> Dict[str, IndicatorMetadata]:
        """
        获取所有未废弃的指标

        Returns:
            未废弃的指标字典
        """
        return {abbr: meta for abbr, meta in self._registry.items() if not meta.deprecated}

    def search(
        self,
        query: str,
        include_deprecated: bool = False,
        max_results: int = 50,
    ) -> List[IndicatorMetadata]:
        """
        搜索指标

        Args:
            query: 搜索关键词
            include_deprecated: 是否包含已废弃指标
            max_results: 最大返回数量

        Returns:
            匹配的指标列表
        """
        query_lower = query.lower()
        results = []

        for meta in self._registry.values():
            if meta.deprecated and not include_deprecated:
                continue

            searchable_text = " ".join(
                [
                    meta.abbreviation.lower(),
                    meta.full_name.lower(),
                    meta.chinese_name.lower(),
                    meta.description.lower(),
                ]
            )

            if query_lower in searchable_text:
                results.append(meta)

        return results[:max_results]

    def exists(self, abbreviation: str) -> bool:
        """
        检查指标是否存在

        Args:
            abbreviation: 指标缩写

        Returns:
            是否存在
        """
        return abbreviation.upper() in self._registry

    def validate_indicator(self, abbreviation: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证指标及其参数

        Args:
            abbreviation: 指标缩写
            parameters: 参数字典

        Returns:
            (是否有效, 错误消息)
        """
        meta = self.get(abbreviation)
        if not meta:
            return False, f"指标 '{abbreviation}' 不存在"

        return meta.validate_parameters(parameters)

    def get_min_data_points(self, abbreviation: str, parameters: Dict[str, Any]) -> int:
        """
        获取指标所需的最小数据点数

        Args:
            abbreviation: 指标缩写
            parameters: 参数字典

        Returns:
            最小数据点数
        """
        meta = self.get(abbreviation)
        if not meta:
            return 0

        return meta.get_min_data_points(parameters)

    def load_from_config(self, config_path: str) -> int:
        """
        从配置文件加载指标

        Args:
            config_path: 配置文件路径

        Returns:
            加载的指标数量
        """
        path = Path(config_path)
        if not path.exists():
            logger.error("配置文件不存在: %(config_path)s")
            return 0

        self._config_path = path
        self._last_reload = time.time()

        with open(path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        if not config_data or "indicators" not in config_data:
            logger.warning("配置文件格式错误: %(config_path)s")
            return 0

        count = 0
        for abbr, ind_data in config_data["indicators"].items():
            if not ind_data.get("enabled", True):
                continue

            try:
                metadata = self._parse_indicator_config(abbr, ind_data)
                self.register(metadata)
                count += 1
            except Exception as e:
                logger.error("加载指标 %(abbr)s 失败: %(e)s")

        logger.info("从配置文件加载了 %(count)s 个指标")
        return count

    def _parse_indicator_config(self, abbr: str, ind_data: Dict[str, Any]) -> IndicatorMetadata:
        """解析指标配置为元数据"""
        params = []
        for param_data in ind_data.get("parameters", []):
            constraints = ParameterConstraint(
                min_value=param_data.get("min"),
                max_value=param_data.get("max"),
                allowed_values=param_data.get("allowed_values"),
                step=param_data.get("step"),
            )
            params.append(
                IndicatorParameter(
                    name=param_data["name"],
                    type=param_data["type"],
                    default=param_data["default"],
                    description=param_data.get("description", ""),
                    display_name=param_data.get("display_name", ""),
                    unit=param_data.get("unit"),
                    constraints=constraints,
                )
            )

        display = ind_data.get("display", {})
        dependencies = ind_data.get("dependencies", [])

        return IndicatorMetadata(
            abbreviation=abbr,
            full_name=ind_data.get("full_name", abbr),
            chinese_name=ind_data.get("chinese_name", abbr),
            category=IndicatorCategory(ind_data.get("category", "trend")),
            description=ind_data.get("description", ""),
            version=ind_data.get("version", "1.0.0"),
            parameters=params,
            dependencies=dependencies,
            panel_type=PanelType(display.get("panel", "overlay")),
            display_colors=display.get("colors", []),
            line_width=display.get("line_width", 1.5),
            deprecated=ind_data.get("deprecated", False),
        )

    def load_templates(self, config_path: str) -> int:
        """
        加载指标模板

        Args:
            config_path: 配置文件路径

        Returns:
            加载的模板数量
        """
        path = Path(config_path)
        if not path.exists():
            return 0

        with open(path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        if not config_data or "templates" not in config_data:
            return 0

        count = 0
        for template_id, template_data in config_data["templates"].items():
            try:
                self._templates[template_id] = IndicatorTemplate(
                    id=template_id,
                    name=template_data["name"],
                    description=template_data.get("description", ""),
                    indicators=template_data["indicators"],
                    market_type=template_data.get("market_type", "medium"),
                    tags=template_data.get("tags", []),
                )
                count += 1
            except Exception as e:
                logger.error("加载模板 %(template_id)s 失败: %(e)s")

        logger.info("加载了 %(count)s 个指标模板")
        return count

    def get_template(self, template_id: str) -> Optional[IndicatorTemplate]:
        """获取指标模板"""
        return self._templates.get(template_id)

    def get_all_templates(self) -> Dict[str, IndicatorTemplate]:
        """获取所有模板"""
        return self._templates.copy()

    def reload(self) -> int:
        """
        重新加载配置文件

        Returns:
            加载的指标数量
        """
        if not self._config_path:
            logger.warning("未设置配置文件路径")
            return 0

        self._registry.clear()
        count = self.load_from_config(str(self._config_path))

        if self._templates:
            self.load_templates(str(self._config_path))

        logger.info("重新加载了 %(count)s 个指标")
        return count

    def get_stats(self) -> RegistryStats:
        """
        获取注册表统计信息

        Returns:
            统计信息
        """
        stats = RegistryStats()
        stats.total_indicators = len(self._registry)

        for meta in self._registry.values():
            category = meta.category
            # 处理 category 可能是字符串或枚举的情况
            if hasattr(category, "value"):
                category = category.value

            complexity = meta.complexity
            if hasattr(complexity, "value"):
                complexity = complexity.value

            stats.by_category[category] = stats.by_category.get(category, 0) + 1
            stats.by_complexity[complexity] = stats.by_complexity.get(complexity, 0) + 1
            if meta.deprecated:
                stats.deprecated_count += 1

        stats.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
        return stats

    def clear(self):
        """清空注册表"""
        self._registry.clear()
        self._templates.clear()
        logger.info("注册表已清空")

    def export(self) -> Dict[str, Any]:
        """
        导出注册表为字典

        Returns:
            注册表数据
        """
        return {
            "indicators": {abbr: meta.dict() for abbr, meta in self._registry.items()},
            "templates": {tid: template.dict() for tid, template in self._templates.items()},
            "stats": self.get_stats().__dict__,
        }


# 全局单例
_indicator_registry: Optional[IndicatorRegistry] = None


def get_indicator_registry() -> IndicatorRegistry:
    """获取指标注册表单例"""
    global _indicator_registry
    if _indicator_registry is None:
        _indicator_registry = IndicatorRegistry()
    return _indicator_registry


def reset_indicator_registry() -> IndicatorRegistry:
    """重置并返回指标注册表单例"""
    global _indicator_registry
    _indicator_registry = IndicatorRegistry()
    return _indicator_registry
