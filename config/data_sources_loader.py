"""
数据源配置动态加载器
Data Sources Configuration Dynamic Loader

支持从拆分后的多个YAML文件加载和合并数据源配置。
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DataSourcesLoader:
    """数据源配置加载器"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.main_config_file = self.config_dir / "data_sources_registry.yaml"
        self.sources_dir = self.config_dir / "data_sources"

    def load_all_sources(self) -> Dict[str, Any]:
        """
        加载所有数据源配置

        1. 加载主配置文件
        2. 根据load_sources列表加载子文件
        3. 合并所有配置
        4. 应用别名映射

        Returns:
            合并后的完整配置字典
        """
        # 1. 加载主配置
        main_config = self._load_yaml_file(self.main_config_file)
        if not main_config:
            logger.error("主配置文件不存在或无效")
            return {}

        # 2. 获取要加载的子文件列表
        load_sources = main_config.get("load_sources", [])
        logger.info(f"将加载以下数据源: {load_sources}")

        # 3. 加载所有子配置文件
        all_sources = {}
        for source_name in load_sources:
            source_file = self.sources_dir / f"{source_name}.yaml"
            if source_file.exists():
                source_config = self._load_yaml_file(source_file)
                if source_config and "data_sources" in source_config:
                    sources_count = len(source_config["data_sources"])
                    all_sources.update(source_config["data_sources"])
                    logger.info(f"✅ 加载 {source_name}: {sources_count} 个数据源")
                else:
                    logger.warning(f"⚠️ {source_name}.yaml 格式无效")
            else:
                logger.warning(f"⚠️ 子配置文件不存在: {source_file}")

        # 4. 合并配置
        merged_config = main_config.copy()
        merged_config["data_sources"] = all_sources

        # 5. 应用别名映射
        aliases = main_config.get("aliases", {})
        self._apply_aliases(merged_config, aliases)

        total_sources = len(all_sources)
        logger.info(f"✅ 总共加载了 {total_sources} 个数据源配置")
        return merged_config

    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """加载单个YAML文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载YAML文件失败 {file_path}: {e}")
            return {}

    def _apply_aliases(self, config: Dict[str, Any], aliases: Dict[str, str]):
        """应用别名映射"""
        data_sources = config.get("data_sources", {})
        for endpoint_name, alias in aliases.items():
            if endpoint_name in data_sources:
                # 创建别名副本
                data_sources[alias] = data_sources[endpoint_name].copy()
                data_sources[alias]["endpoint_name"] = alias
                logger.debug(f"创建别名: {endpoint_name} -> {alias}")


# 全局加载器实例
loader = DataSourcesLoader()


def load_data_sources_config() -> Dict[str, Any]:
    """便捷函数：加载完整的数据源配置"""
    return loader.load_all_sources()
