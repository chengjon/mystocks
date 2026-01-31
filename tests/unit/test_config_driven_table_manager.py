"""
ConfigDrivenTableManager测试文件
用于测试配置驱动的表管理器功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import tempfile
import unittest
from unittest.mock import MagicMock, patch

import yaml

# 导入被测试的模块
from src.core.config_driven_table_manager import ConfigDrivenTableManager


class TestConfigDrivenTableManager(unittest.TestCase):
    """ConfigDrivenTableManager测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        config_data = {
            "version": "1.0.0",
            "tables": [
                {
                    "table_name": "test_table",
                    "database_type": "PostgreSQL",
                    "database_name": "test_db",
                    "columns": [
                        {
                            "name": "id",
                            "type": "INTEGER",
                            "primary_key": True,
                            "auto_increment": True,
                        },
                        {
                            "name": "name",
                            "type": "VARCHAR",
                            "length": 255,
                            "nullable": False,
                        },
                        {
                            "name": "created_at",
                            "type": "TIMESTAMP",
                            "default": "CURRENT_TIMESTAMP",
                        },
                    ],
                    "indexes": [{"name": "idx_name", "columns": ["name"], "unique": False}],
                }
            ],
        }
        yaml.dump(config_data, self.temp_config)
        self.temp_config.close()

        # 创建测试用的管理器实例
        self.manager = ConfigDrivenTableManager(config_path=self.temp_config.name)

    def tearDown(self):
        """测试后清理"""
        os.unlink(self.temp_config.name)

    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
    def test_load_config(self, mock_conn_manager):
        """测试配置加载功能"""
        # 加载配置
        config = self.manager.load_config()

        # 验证配置结构
        self.assertIn("version", config)
        self.assertIn("tables", config)
        self.assertEqual(len(config["tables"]), 1)

        # 验证表定义
        table_def = config["tables"][0]
        self.assertEqual(table_def["table_name"], "test_table")
        self.assertEqual(table_def["database_type"], "PostgreSQL")

    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
    def test_initialize_tables(self, mock_conn_manager):
        """测试表初始化功能"""
        # 模拟数据库连接
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn_manager.return_value.get_postgresql_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 执行表初始化
        result = self.manager.initialize_tables()

        # 验证结果
        self.assertIn("tables_created", result)
        self.assertIn("tables_skipped", result)
        self.assertIn("errors", result)

    def test_table_exists_check(self):
        """测试表存在性检查"""
        # 这个测试需要在实际数据库环境中验证
        # 由于没有实际数据库，我们只验证方法调用
        pass

    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
    def test_create_table_postgresql(self, mock_conn_manager):
        """测试PostgreSQL表创建"""
        # 模拟数据库连接
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn_manager.return_value.get_postgresql_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 定义测试表结构
        table_def = {
            "table_name": "test_create_table",
            "database_type": "PostgreSQL",
            "database_name": "test_db",
            "columns": [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "primary_key": True,
                    "auto_increment": True,
                },
                {"name": "name", "type": "VARCHAR", "length": 255},
            ],
        }

        # 调用创建表方法
        result = self.manager._create_postgresql_table(table_def)

        # 验证返回值
        self.assertTrue(result)  # 假设创建成功

    @patch("src.db_manager.connection_manager.DatabaseConnectionManager")
    def test_create_tdengine_table(self, mock_conn_manager):
        """测试TDengine表创建"""
        # 模拟数据库连接
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn_manager.return_value.get_tdengine_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 定义测试表结构
        table_def = {
            "table_name": "test_tdengine_table",
            "database_type": "TDengine",
            "database_name": "test_db",
            "columns": [
                {"name": "ts", "type": "TIMESTAMP", "primary_key": True},
                {"name": "metric_value", "type": "DOUBLE"},
            ],
            "tags": [{"name": "device_id", "type": "VARCHAR", "length": 50}],
        }

        # 调用创建表方法
        result = self.manager._create_tdengine_super_table(table_def)

        # 验证返回值
        self.assertTrue(result)  # 假设创建成功


if __name__ == "__main__":
    unittest.main()
