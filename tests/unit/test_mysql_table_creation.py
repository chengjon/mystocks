"""
T023: PostgreSQL table configuration tests
验证配置驱动表结构管理的PostgreSQL表配置
"""

import sys

import pytest

sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.core.config_driven_table_manager import ConfigDrivenTableManager


class TestPostgreSQLTableConfig:
    """PostgreSQL表配置测试"""

    def test_postgresql_tables_present(self):
        """配置中应包含PostgreSQL表"""
        manager = ConfigDrivenTableManager()
        pg_tables = [t for t in manager.config["tables"] if t["database_type"] == "PostgreSQL"]
        assert len(pg_tables) > 0

    def test_table_database_types_allowed(self):
        """表配置仅允许TDengine/PostgreSQL/Redis"""
        manager = ConfigDrivenTableManager()
        allowed_types = {"TDengine", "PostgreSQL", "Redis"}
        for table_def in manager.config["tables"]:
            assert table_def["database_type"] in allowed_types
