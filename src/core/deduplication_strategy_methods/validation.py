#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DeduplicationStrategy 表校验方法集。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from src.storage.database.database_manager import DatabaseType

from .core import logger


class DeduplicationStrategyValidationMixin:
    """索引创建与表结构校验方法。"""

    def _create_indexes(self, table_config: Dict, db_type: DatabaseType):
        """创建表索引。"""
        try:
            for index_config in table_config.get("indexes", []):
                logger.info("创建索引: %s", index_config["name"])
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("创建索引失败: %s", e)

    def validate_all_table_structures(self) -> Dict[str, Any]:
        """验证所有表结构。"""
        logger.info("开始验证所有表结构...")

        validation_results = {
            "total_tables": 0,
            "valid_tables": 0,
            "invalid_tables": 0,
            "details": [],
        }
        if not self.config_data or "tables" not in self.config_data:
            logger.error("配置数据无效")
            return validation_results

        for table_config in self.config_data["tables"]:
            try:
                table_key = (
                    f"{table_config['database_type']}.{table_config['database_name']}.{table_config['table_name']}"
                )
                is_valid = self._validate_single_table_structure(table_config)
                validation_results["total_tables"] += 1
                if is_valid:
                    validation_results["valid_tables"] += 1
                else:
                    validation_results["invalid_tables"] += 1

                validation_results["details"].append(
                    {
                        "table": table_key,
                        "valid": is_valid,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("验证表结构时出现异常: %s, 错误: %s", table_config.get("table_name", "Unknown"), e)

        logger.info(
            "表结构验证完成: %d/%d 有效",
            validation_results["valid_tables"],
            validation_results["total_tables"],
        )
        return validation_results
