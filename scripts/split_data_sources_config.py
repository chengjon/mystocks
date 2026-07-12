#!/usr/bin/env python3
"""数据源配置文件自动拆分脚本
Data Sources Configuration Auto-Split Script

将大型的 data_sources_registry.yaml 文件按数据源类型自动拆分为多个子文件。
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSourcesSplitter:
    """数据源配置拆分器"""

    def __init__(self, config_dir: str = "config", config_file: str = None):
        self.config_dir = Path(config_dir)
        if config_file:
            self.main_config_file = Path(config_file)
        else:
            self.main_config_file = self.config_dir / "data_sources_registry.yaml"
        self.sources_dir = self.config_dir / "data_sources"
        self.sources_dir.mkdir(exist_ok=True)

    def split_config(self):
        """执行配置文件拆分"""
        logger.info("开始拆分数据源配置文件...")

        # 1. 加载原始配置
        original_config = self._load_yaml_file(self.main_config_file)
        if not original_config or "data_sources" not in original_config:
            logger.error("原始配置文件无效")
            return False

        data_sources = original_config["data_sources"]
        logger.info(f"发现 {len(data_sources)} 个数据源配置")

        # 2. 按source_name分组
        grouped_sources = self._group_by_source_name(data_sources)

        # 3. 创建子配置文件
        for source_name, sources in grouped_sources.items():
            self._create_sub_config(source_name, sources)

        # 4. 创建新的主配置文件
        self._create_main_config(original_config, list(grouped_sources.keys()))

        # 5. 创建模板文件
        self._create_template()

        logger.info("✅ 配置文件拆分完成")
        return True

    def _group_by_source_name(
        self,
        data_sources: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """按source_name对数据源进行分组"""
        grouped = {}

        for endpoint_name, config in data_sources.items():
            source_name = config.get("source_name", "unknown")

            if source_name not in grouped:
                grouped[source_name] = {}

            grouped[source_name][endpoint_name] = config

        logger.info(f"按source_name分组结果: {list(grouped.keys())}")
        return grouped

    def _create_sub_config(self, source_name: str, sources: Dict[str, Any]):
        """创建子配置文件"""
        sub_config = {
            "#": f"{source_name.upper()} 数据源配置",
            "#": f"包含所有{source_name}相关的{len(sources)}个数据源",
            "data_sources": sources,
        }

        filename = f"{source_name}.yaml"
        filepath = self.sources_dir / filename

        self._save_yaml_file(filepath, sub_config)
        logger.info(f"✅ 创建子配置文件: {filepath} ({len(sources)} 个数据源)")

    def _create_main_config(
        self,
        original_config: Dict[str, Any],
        source_names: List[str],
    ):
        """创建新的主配置文件"""
        main_config = {
            "#": "数据源注册表主配置文件",
            "#": "控制子配置文件的加载",
            "version": "2.1",
            "last_updated": "2026-01-15T10:00:00",
            "load_sources": source_names,  # 动态生成加载列表
            "global_config": {
                "default_target_db": "postgresql",
                "enable_caching": True,
                "health_check_interval": 300,
            },
            "aliases": {
                "akshare.stock_zh_a_hist": "akshare_daily_kline",
                "sina_finance.stock_ratings": "stock_ratings_sina",
            },
        }

        # 备份原文件
        backup_file = self.main_config_file.with_suffix(".yaml.backup")
        if backup_file.exists():
            backup_file.unlink()
        self.main_config_file.rename(backup_file)
        logger.info(f"✅ 原配置文件已备份到: {backup_file}")

        # 保存新主配置文件
        self._save_yaml_file(self.main_config_file, main_config)
        logger.info(f"✅ 创建新的主配置文件: {self.main_config_file}")

    def _create_template(self):
        """创建配置模板文件"""
        template = {
            "#": "数据源配置模板",
            "#": "复制此模板创建新的数据源配置",
            "data_sources": {
                "your_source_name_endpoint": {
                    "source_name": "your_source_name",
                    "source_type": "api_library",  # api_library | crawler | database | file | mock
                    "endpoint_name": "your_source_name.your_endpoint",
                    "call_method": "function_call",
                    "#": "5层数据分类绑定",
                    "data_category": "DAILY_KLINE",  # 数据分类
                    "data_classification": "market_data",  # market_data | reference_data | derived_data | transaction_data | metadata
                    "classification_level": 1,  # 1-5层
                    "target_db": "postgresql",  # postgresql | tdengine
                    "table_name": "your_table_name",
                    "#": "参数定义 (JSON Schema格式)",
                    "parameters": {
                        "symbol": {
                            "type": "string",
                            "required": True,
                            "description": "股票代码",
                            "example": "600000",
                        },
                    },
                    "description": "数据源描述",
                    "update_frequency": "daily",  # daily | weekly | realtime
                    "data_quality_score": 8.0,  # 1-10分
                    "priority": 1,  # 1-10, 越高优先级越高
                    "status": "active",  # active | maintenance | deprecated
                    "tags": ["tag1", "tag2"],
                    "#": "测试参数",
                    "test_parameters": {"symbol": "600000"},
                    "#": "数据质量规则",
                    "quality_rules": {
                        "min_record_count": 1,
                        "max_response_time": 10.0,
                        "required_columns": ["column1", "column2"],
                    },
                },
            },
        }

        template_file = self.sources_dir / "_template.yaml"
        self._save_yaml_file(template_file, template)
        logger.info(f"✅ 创建配置模板: {template_file}")

    def _load_yaml_file(self, filepath: Path) -> Dict[str, Any]:
        """加载YAML文件"""
        try:
            with open(filepath, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载YAML文件失败 {filepath}: {e}")
            return {}

    def _save_yaml_file(self, filepath: Path, data: Dict[str, Any]):
        """保存YAML文件"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
        except Exception as e:
            logger.error(f"保存YAML文件失败 {filepath}: {e}")


def main():
    """主函数"""
    import sys

    config_file = sys.argv[1] if len(sys.argv) > 1 else None
    splitter = DataSourcesSplitter(config_file=config_file)

    if splitter.split_config():
        logger.info("\n🎉 数据源配置拆分完成！")
        logger.info("\n📋 下一步操作:")
        logger.info("1. 检查拆分后的文件结构")
        logger.info("2. 运行测试验证加载功能")
        logger.info("3. 更新相关文档")
    else:
        logger.error("❌ 数据源配置拆分失败")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
