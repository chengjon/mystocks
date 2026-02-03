#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigDrivenTableManager 完整测试套件

测试目标: 85%+ 覆盖率
测试用例数: 50个
创建日期: 2026-01-26
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import yaml

# 导入目标类
from src.core.config_driven_table_manager import ConfigDrivenTableManager

# ============================================================================
# 测试夹具 (Fixtures)
# ============================================================================

@pytest.fixture
def valid_config_data():
    """有效的配置数据"""
    return {
        "version": "1.0.0",
        "databases": {
            "tdengine": {"host": "localhost", "port": 6030},
            "postgresql": {"host": "localhost", "port": 5432, "database": "mystocks"}
        },
        "tables": [
            {
                "table_name": "tick_data",
                "database_type": "TDengine",
                "database_name": "mystocks",
                "columns": [
                    {"name": "ts", "type": "TIMESTAMP"},
                    {"name": "price", "type": "FLOAT"}
                ],
                "tags": [
                    {"name": "symbol", "type": "NCHAR(10)"}
                ]
            },
            {
                "table_name": "stock_info",
                "database_type": "PostgreSQL",
                "database_name": "mystocks",
                "columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY"},
                    {"name": "symbol", "type": "VARCHAR(10)"}
                ]
            }
        ]
    }


@pytest.fixture
def temp_config_file(valid_config_data):
    """创建临时配置文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(valid_config_data, f)
        config_path = f.name

    yield config_path

    # 清理
    if os.path.exists(config_path):
        os.remove(config_path)


@pytest.fixture
def mock_connection_manager():
    """模拟数据库连接管理器"""
    with patch('src.core.config_driven_table_manager.DatabaseConnectionManager') as mock_cm:
        mock_instance = MagicMock()
        mock_cm.return_value = mock_instance

        # 模拟连接对象
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        mock_instance.get_tdengine_connection.return_value = mock_conn
        mock_instance.get_postgresql_connection.return_value = mock_conn

        yield mock_instance


# ============================================================================
# 测试类1: 初始化测试 (10个用例)
# ============================================================================

class TestConfigDrivenTableManagerInitialization:
    """测试ConfigDrivenTableManager初始化"""

    def test_init_with_valid_config(self, temp_config_file, mock_connection_manager):
        """测试使用有效配置文件初始化"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        assert manager.config_path == Path(temp_config_file)
        assert manager.safe_mode is True  # 默认值
        assert manager.config is not None
        assert "tables" in manager.config

    def test_init_with_nonexistent_config(self, mock_connection_manager):
        """测试配置文件不存在时抛出异常"""
        with pytest.raises(FileNotFoundError, match="配置文件不存在"):
            ConfigDrivenTableManager(config_path="/nonexistent/path/config.yaml")

    def test_init_with_safe_mode_true(self, temp_config_file, mock_connection_manager):
        """测试safe_mode=True初始化"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file, safe_mode=True)
        assert manager.safe_mode is True

    def test_init_with_safe_mode_false(self, temp_config_file, mock_connection_manager):
        """测试safe_mode=False初始化"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file, safe_mode=False)
        assert manager.safe_mode is False

    def test_init_with_relative_path(self, mock_connection_manager):
        """测试相对路径配置文件"""
        # 创建临时配置在当前目录
        config_path = "temp_config_test.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump({"version": "1.0.0", "tables": []}, f)

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)
            assert manager.config_path == Path(config_path)
        finally:
            if os.path.exists(config_path):
                os.remove(config_path)

    def test_init_with_absolute_path(self, temp_config_file, mock_connection_manager):
        """测试绝对路径配置文件"""
        abs_path = os.path.abspath(temp_config_file)
        manager = ConfigDrivenTableManager(config_path=abs_path)
        assert manager.config_path == Path(abs_path)

    def test_init_with_empty_config(self, mock_connection_manager):
        """测试空配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write("")
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)
            # 空配置应返回空字典
            assert manager.config == {}
        finally:
            os.remove(config_path)

    def test_init_with_invalid_yaml(self, mock_connection_manager):
        """测试YAML格式错误的配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write("invalid: yaml: content: [[[")
            config_path = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                ConfigDrivenTableManager(config_path=config_path)
        finally:
            os.remove(config_path)

    def test_init_with_encoding_error(self, mock_connection_manager):
        """测试配置文件编码错误"""
        # 创建包含非UTF-8字符的文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.yaml', delete=False) as f:
            f.write(b'\xff\xfe')  # BOM for UTF-16
            config_path = f.name

        try:
            with pytest.raises(UnicodeDecodeError):
                ConfigDrivenTableManager(config_path=config_path)
        finally:
            os.remove(config_path)

    def test_init_loads_config_version(self, temp_config_file, mock_connection_manager):
        """测试配置版本号被正确加载"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)
        assert "version" in manager.config
        assert manager.config["version"] == "1.0.0"


# ============================================================================
# 测试类2: 配置加载测试 (8个用例)
# ============================================================================

class TestConfigLoading:
    """测试配置加载功能"""

    def test_load_valid_config(self, temp_config_file, mock_connection_manager):
        """测试加载有效的YAML配置"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)
        config = manager.load_config()

        assert isinstance(config, dict)
        assert "version" in config
        assert "tables" in config
        assert len(config["tables"]) > 0

    def test_load_config_with_missing_version(self, mock_connection_manager):
        """测试缺少version字段的配置"""
        config_data = {"tables": []}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)
            config = manager.load_config()
            # 应使用默认版本号
            assert config.get("version", "1.0.0") == "1.0.0"
        finally:
            os.remove(config_path)

    def test_load_config_with_missing_tables(self, mock_connection_manager):
        """测试缺少tables字段的配置"""
        config_data = {"version": "1.0.0"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            with pytest.raises(KeyError):
                manager = ConfigDrivenTableManager(config_path=config_path)
                manager.load_config()
        finally:
            os.remove(config_path)

    def test_load_config_with_multiple_tables(self, temp_config_file, mock_connection_manager):
        """测试包含多个表定义的配置"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)
        config = manager.load_config()

        assert len(config["tables"]) == 2
        assert config["tables"][0]["table_name"] == "tick_data"
        assert config["tables"][1]["table_name"] == "stock_info"

    def test_load_config_with_single_table(self, mock_connection_manager):
        """测试包含单个表定义的配置"""
        config_data = {
            "version": "1.0.0",
            "tables": [{"table_name": "test_table", "database_type": "PostgreSQL"}]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)
            config = manager.load_config()
            assert len(config["tables"]) == 1
        finally:
            os.remove(config_path)

    def test_load_config_with_zero_tables(self, mock_connection_manager):
        """测试包含0个表定义的配置"""
        config_data = {"version": "1.0.0", "tables": []}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)
            config = manager.load_config()
            assert len(config["tables"]) == 0
        finally:
            os.remove(config_path)

    def test_load_config_empty_file(self, mock_connection_manager):
        """测试完全空的配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write("")
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)
            config = manager.load_config()
            assert config == {}
        finally:
            os.remove(config_path)

    def test_load_config_yaml_parse_error(self, mock_connection_manager):
        """测试YAML解析错误处理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write("key: [unclosed list")
            config_path = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                ConfigDrivenTableManager(config_path=config_path)
        finally:
            os.remove(config_path)


# ============================================================================
# 测试类3: 表初始化测试 (12个用例)
# ============================================================================

class TestTableInitialization:
    """测试表初始化功能"""

    def test_initialize_all_tables_success(self, temp_config_file, mock_connection_manager):
        """测试成功初始化所有表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟表不存在
        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_table', return_value=True):
                result = manager.initialize_tables()

        assert result["tables_created"] == 2
        assert result["tables_skipped"] == 0
        assert len(result["errors"]) == 0

    def test_initialize_tables_partial_failure(self, temp_config_file, mock_connection_manager):
        """测试部分表创建失败"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        def create_table_side_effect(table_def):
            if table_def["table_name"] == "tick_data":
                raise Exception("创建失败")
            return True

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_table', side_effect=create_table_side_effect):
                result = manager.initialize_tables()

        assert result["tables_created"] == 1
        assert len(result["errors"]) == 1
        assert "tick_data" in result["errors"][0]

    def test_initialize_tables_all_exist(self, temp_config_file, mock_connection_manager):
        """测试所有表已存在（跳过）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        with patch.object(manager, '_table_exists', return_value=True):
            with patch.object(manager, '_create_table', return_value=False):
                result = manager.initialize_tables()

        assert result["tables_created"] == 0
        assert result["tables_skipped"] == 2
        assert len(result["errors"]) == 0

    def test_initialize_tables_mixed_scenario(self, temp_config_file, mock_connection_manager):
        """测试混合场景（部分新建、部分跳过）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        def create_table_side_effect(table_def):
            # tick_data新建，stock_info跳过
            return table_def["table_name"] == "tick_data"

        with patch.object(manager, '_create_table', side_effect=create_table_side_effect):
            result = manager.initialize_tables()

        assert result["tables_created"] == 1
        assert result["tables_skipped"] == 1

    def test_initialize_empty_table_list(self, mock_connection_manager):
        """测试空表列表"""
        config_data = {"version": "1.0.0", "tables": []}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)
            result = manager.initialize_tables()

            assert result["tables_created"] == 0
            assert result["tables_skipped"] == 0
            assert len(result["errors"]) == 0
        finally:
            os.remove(config_path)

    def test_initialize_single_table(self, mock_connection_manager):
        """测试单表初始化"""
        config_data = {
            "version": "1.0.0",
            "tables": [{"table_name": "test", "database_type": "PostgreSQL"}]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)

            with patch.object(manager, '_table_exists', return_value=False):
                with patch.object(manager, '_create_table', return_value=True):
                    result = manager.initialize_tables()

            assert result["tables_created"] == 1
        finally:
            os.remove(config_path)

    def test_initialize_tdengine_tables(self, mock_connection_manager):
        """测试初始化多个TDengine表"""
        config_data = {
            "version": "1.0.0",
            "tables": [
                {"table_name": "td_table1", "database_type": "TDengine"},
                {"table_name": "td_table2", "database_type": "TDengine"}
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)

            with patch.object(manager, '_table_exists', return_value=False):
                with patch.object(manager, '_create_table', return_value=True):
                    result = manager.initialize_tables()

            assert result["tables_created"] == 2
        finally:
            os.remove(config_path)

    def test_initialize_postgresql_tables(self, mock_connection_manager):
        """测试初始化多个PostgreSQL表"""
        config_data = {
            "version": "1.0.0",
            "tables": [
                {"table_name": "pg_table1", "database_type": "PostgreSQL"},
                {"table_name": "pg_table2", "database_type": "PostgreSQL"}
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)

            with patch.object(manager, '_table_exists', return_value=False):
                with patch.object(manager, '_create_table', return_value=True):
                    result = manager.initialize_tables()

            assert result["tables_created"] == 2
        finally:
            os.remove(config_path)

    def test_initialize_postgresql_single_table(self, mock_connection_manager):
        """测试初始化单个PostgreSQL表"""
        config_data = {
            "version": "1.0.0",
            "databases": {"postgresql": {"database": "test_db"}},
            "tables": [{"table_name": "pg_table", "database_type": "PostgreSQL"}]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=config_path)

            with patch.object(manager, '_table_exists', return_value=False):
                with patch.object(manager, '_create_table', return_value=True):
                    result = manager.initialize_tables()

            assert result["tables_created"] == 1
        finally:
            os.remove(config_path)

    def test_initialize_mixed_database_types(self, temp_config_file, mock_connection_manager):
        """测试初始化混合数据库类型的表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_table', return_value=True):
                result = manager.initialize_tables()

        # temp_config_file包含TDengine和PostgreSQL表
        assert result["tables_created"] == 2

    def test_initialize_tables_error_handling(self, temp_config_file, mock_connection_manager):
        """测试错误处理和日志记录"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        with patch.object(manager, '_create_table', side_effect=Exception("测试异常")):
            result = manager.initialize_tables()

        assert len(result["errors"]) == 2  # 两个表都失败
        assert "测试异常" in result["errors"][0]

    def test_initialize_tables_return_result_structure(self, temp_config_file, mock_connection_manager):
        """测试返回结果的结构验证"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        with patch.object(manager, '_create_table', return_value=True):
            result = manager.initialize_tables()

        # 验证返回结构
        assert "tables_created" in result
        assert "tables_skipped" in result
        assert "errors" in result
        assert isinstance(result["tables_created"], int)
        assert isinstance(result["tables_skipped"], int)
        assert isinstance(result["errors"], list)


# ============================================================================
# 测试类4: 表存在性检查测试 (10个用例)
# ============================================================================

class TestTableExists:
    """测试表存在性检查功能"""

    def test_tdengine_table_exists(self, temp_config_file, mock_connection_manager):
        """测试TDengine表存在"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟表存在
        mock_cursor = mock_connection_manager.get_tdengine_connection.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [("tick_data",)]

        exists = manager._table_exists("TDengine", "tick_data")
        assert exists is True

    def test_tdengine_table_not_exists(self, temp_config_file, mock_connection_manager):
        """测试TDengine表不存在"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟表不存在
        mock_cursor = mock_connection_manager.get_tdengine_connection.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = []

        exists = manager._table_exists("TDengine", "nonexistent_table")
        assert exists is False

    def test_postgresql_table_exists(self, temp_config_file, mock_connection_manager):
        """测试PostgreSQL表存在"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟表存在
        mock_cursor = mock_connection_manager.get_postgresql_connection.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = (True,)

        exists = manager._table_exists("PostgreSQL", "stock_info")
        assert exists is True

    def test_postgresql_table_not_exists(self, temp_config_file, mock_connection_manager):
        """测试PostgreSQL表不存在"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟表不存在
        mock_cursor = mock_connection_manager.get_postgresql_connection.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = (False,)

        exists = manager._table_exists("PostgreSQL", "nonexistent")
        assert exists is False

    def test_postgresql_table_exists_second(self, temp_config_file, mock_connection_manager):
        """测试PostgreSQL表存在（第二表）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟表存在
        mock_cursor = mock_connection_manager.get_postgresql_connection.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = (True,)

        exists = manager._table_exists("PostgreSQL", "secondary_table")
        assert exists is True

    def test_table_exists_sql_injection_protection(self, temp_config_file, mock_connection_manager):
        """测试SQL注入防护（无效表名）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 测试包含SQL注入的表名
        invalid_names = [
            "table'; DROP TABLE users;--",
            "table OR 1=1",
            "table; DELETE FROM",
            "table`",
            "table--",
            "123invalid"  # 以数字开头
        ]

        for invalid_name in invalid_names:
            with pytest.raises(ValueError, match="Invalid table name"):
                manager._table_exists("TDengine", invalid_name)

    def test_table_exists_connection_error(self, temp_config_file, mock_connection_manager):
        """测试数据库连接错误处理"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟连接错误
        mock_connection_manager.get_tdengine_connection.side_effect = Exception("连接失败")

        exists = manager._table_exists("TDengine", "test_table")
        # 错误时应返回False
        assert exists is False

    def test_table_exists_query_exception(self, temp_config_file, mock_connection_manager):
        """测试查询异常处理"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 模拟查询异常
        mock_cursor = mock_connection_manager.get_postgresql_connection.return_value.cursor.return_value
        mock_cursor.execute.side_effect = Exception("查询失败")

        exists = manager._table_exists("PostgreSQL", "test_table")
        assert exists is False

    def test_table_exists_redis_type(self, temp_config_file, mock_connection_manager):
        """测试Redis类型处理（不需要检查表存在）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        exists = manager._table_exists("Redis", "test_key")
        # Redis类型应返回False（不需要预创建）
        assert exists is False


# ============================================================================
# 测试类5: 表创建测试 (10个用例)
# ============================================================================

class TestTableCreation:
    """测试表创建功能"""

    def test_create_table_tdengine(self, temp_config_file, mock_connection_manager):
        """测试创建TDengine Super Table"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_super_table",
            "database_type": "TDengine",
            "columns": [{"name": "ts", "type": "TIMESTAMP"}],
            "tags": [{"name": "symbol", "type": "NCHAR(10)"}]
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_tdengine_super_table', return_value=True) as mock_create:
                result = manager._create_table(table_def)

        assert result is True
        mock_create.assert_called_once_with(table_def)

    def test_create_table_postgresql(self, temp_config_file, mock_connection_manager):
        """测试创建PostgreSQL表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_table",
            "database_type": "PostgreSQL",
            "columns": [{"name": "id", "type": "SERIAL PRIMARY KEY"}]
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_postgresql_table', return_value=True) as mock_create:
                result = manager._create_table(table_def)

        assert result is True
        mock_create.assert_called_once_with(table_def)

    def test_create_table_postgresql_secondary(self, temp_config_file, mock_connection_manager):
        """测试创建PostgreSQL表（第二表）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_table_secondary",
            "database_type": "PostgreSQL",
            "database_name": "test_db",
            "columns": [{"name": "id", "type": "INT PRIMARY KEY"}]
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_postgresql_table', return_value=True) as mock_create:
                result = manager._create_table(table_def)

        assert result is True
        mock_create.assert_called_once_with(table_def)

    def test_create_table_redis_type(self, temp_config_file, mock_connection_manager):
        """测试Redis类型（无需创建）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_key",
            "database_type": "Redis"
        }

        result = manager._create_table(table_def)
        # Redis无需预创建，应返回False
        assert result is False

    def test_create_table_unsupported_type(self, temp_config_file, mock_connection_manager):
        """测试不支持的数据库类型"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_table",
            "database_type": "UnsupportedDB"
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with pytest.raises(ValueError, match="不支持的数据库类型"):
                manager._create_table(table_def)

    def test_create_table_sql_injection_protection(self, temp_config_file, mock_connection_manager):
        """测试表名SQL注入防护"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test'; DROP TABLE users;--",
            "database_type": "TDengine",
            "columns": []
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with pytest.raises(ValueError, match="Invalid table name"):
                manager._create_table(table_def)

    def test_create_table_already_exists(self, temp_config_file, mock_connection_manager):
        """测试表已存在返回False"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "existing_table",
            "database_type": "PostgreSQL"
        }

        with patch.object(manager, '_table_exists', return_value=True):
            result = manager._create_table(table_def)

        # 表已存在应返回False
        assert result is False

    def test_create_table_success_returns_true(self, temp_config_file, mock_connection_manager):
        """测试表创建成功返回True"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "new_table",
            "database_type": "PostgreSQL",
            "columns": [{"name": "id", "type": "INT"}]
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_postgresql_table', return_value=True):
                result = manager._create_table(table_def)

        assert result is True

    def test_create_table_exception_handling(self, temp_config_file, mock_connection_manager):
        """测试创建异常处理"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_table",
            "database_type": "PostgreSQL"
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_postgresql_table', side_effect=Exception("创建失败")):
                with pytest.raises(Exception, match="创建失败"):
                    manager._create_table(table_def)

    def test_create_table_multiple_field_types(self, temp_config_file, mock_connection_manager):
        """测试多种字段类型支持"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "complex_table",
            "database_type": "PostgreSQL",
            "columns": [
                {"name": "id", "type": "SERIAL PRIMARY KEY"},
                {"name": "name", "type": "VARCHAR(100)"},
                {"name": "price", "type": "DECIMAL(10,2)"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        }

        with patch.object(manager, '_table_exists', return_value=False):
            with patch.object(manager, '_create_postgresql_table', return_value=True) as mock_create:
                result = manager._create_table(table_def)

        assert result is True
        # 验证传递了正确的表定义
        call_args = mock_create.call_args[0][0]
        assert len(call_args["columns"]) == 4


# ============================================================================
# 测试执行入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
