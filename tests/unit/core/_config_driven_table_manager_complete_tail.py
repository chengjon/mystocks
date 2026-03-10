#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Support tests extracted from `test_config_driven_table_manager_complete.py`."""

from unittest.mock import patch

import pytest

from src.core.config_driven_table_manager import ConfigDrivenTableManager


class TestTableCreation:
    """测试表创建功能"""

    def test_create_table_tdengine(self, temp_config_file, mock_connection_manager):
        """测试创建TDengine Super Table"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_super_table",
            "database_type": "TDengine",
            "columns": [{"name": "ts", "type": "TIMESTAMP"}],
            "tags": [{"name": "symbol", "type": "NCHAR(10)"}],
        }

        with patch.object(manager, "_table_exists", return_value=False):
            with patch.object(manager, "_create_tdengine_super_table", return_value=True) as mock_create:
                result = manager._create_table(table_def)

        assert result is True
        mock_create.assert_called_once_with(table_def)

    def test_create_table_postgresql(self, temp_config_file, mock_connection_manager):
        """测试创建PostgreSQL表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test_table",
            "database_type": "PostgreSQL",
            "columns": [{"name": "id", "type": "SERIAL PRIMARY KEY"}],
        }

        with patch.object(manager, "_table_exists", return_value=False):
            with patch.object(manager, "_create_postgresql_table", return_value=True) as mock_create:
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
            "columns": [{"name": "id", "type": "INT PRIMARY KEY"}],
        }

        with patch.object(manager, "_table_exists", return_value=False):
            with patch.object(manager, "_create_postgresql_table", return_value=True) as mock_create:
                result = manager._create_table(table_def)

        assert result is True
        mock_create.assert_called_once_with(table_def)

    def test_create_table_redis_type(self, temp_config_file, mock_connection_manager):
        """测试Redis类型（无需创建）"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {"table_name": "test_key", "database_type": "Redis"}

        result = manager._create_table(table_def)
        assert result is False

    def test_create_table_unsupported_type(self, temp_config_file, mock_connection_manager):
        """测试不支持的数据库类型"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {"table_name": "test_table", "database_type": "UnsupportedDB"}

        with patch.object(manager, "_table_exists", return_value=False):
            with pytest.raises(ValueError, match="不支持的数据库类型"):
                manager._create_table(table_def)

    def test_create_table_sql_injection_protection(self, temp_config_file, mock_connection_manager):
        """测试表名SQL注入防护"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "test'; DROP TABLE users;--",
            "database_type": "TDengine",
            "columns": [],
        }

        with patch.object(manager, "_table_exists", return_value=False):
            with pytest.raises(ValueError, match="Invalid table name"):
                manager._create_table(table_def)

    def test_create_table_already_exists(self, temp_config_file, mock_connection_manager):
        """测试表已存在返回False"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {"table_name": "existing_table", "database_type": "PostgreSQL"}

        with patch.object(manager, "_table_exists", return_value=True):
            result = manager._create_table(table_def)

        assert result is False

    def test_create_table_success_returns_true(self, temp_config_file, mock_connection_manager):
        """测试表创建成功返回True"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {
            "table_name": "new_table",
            "database_type": "PostgreSQL",
            "columns": [{"name": "id", "type": "INT"}],
        }

        with patch.object(manager, "_table_exists", return_value=False):
            with patch.object(manager, "_create_postgresql_table", return_value=True):
                result = manager._create_table(table_def)

        assert result is True

    def test_create_table_exception_handling(self, temp_config_file, mock_connection_manager):
        """测试创建异常处理"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        table_def = {"table_name": "test_table", "database_type": "PostgreSQL"}

        with patch.object(manager, "_table_exists", return_value=False):
            with patch.object(manager, "_create_postgresql_table", side_effect=Exception("创建失败")):
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
                {"name": "created_at", "type": "TIMESTAMP"},
            ],
        }

        with patch.object(manager, "_table_exists", return_value=False):
            with patch.object(manager, "_create_postgresql_table", return_value=True) as mock_create:
                result = manager._create_table(table_def)

        assert result is True
        call_args = mock_create.call_args[0][0]
        assert len(call_args["columns"]) == 4
