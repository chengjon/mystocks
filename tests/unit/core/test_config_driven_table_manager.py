"""
ConfigDrivenTableManager单元测试

测试配置驱动的表管理器核心功能
"""

import pytest
import yaml
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# 确保能导入src模块
sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.core.config_driven_table_manager import ConfigDrivenTableManager


@pytest.fixture
def sample_table_config():
    """提供测试用的表配置数据"""
    return {
        "version": "2.0.0",
        "databases": {
            "tdengine": {"host": "localhost", "port": 6041, "database": "market_data"},
            "postgresql": {"host": "localhost", "port": 5432, "database": "mystocks"},
            "mysql": {"host": "localhost", "port": 3306, "database": "test_db"},
        },
        "tables": [
            {
                "table_name": "tick_data",
                "database_type": "TDengine",
                "data_classification": "高频市场数据",
                "columns": [
                    {"name": "ts", "type": "TIMESTAMP", "nullable": False},
                    {"name": "symbol", "type": "NCHAR", "length": 20},
                    {"name": "price", "type": "FLOAT"},
                    {"name": "volume", "type": "BIGINT"},
                ],
                "tags": [{"name": "exchange", "type": "NCHAR(10)"}],
                "compression": {"enabled": True, "codec": "zstd", "level": "high"},
                "retention_days": 90,
            },
            {
                "table_name": "stock_daily",
                "database_type": "PostgreSQL",
                "data_classification": "日线市场数据",
                "is_timescale_hypertable": True,
                "time_column": "trade_date",
                "columns": [
                    {"name": "id", "type": "SERIAL", "primary_key": True},
                    {
                        "name": "symbol",
                        "type": "VARCHAR",
                        "length": 20,
                        "nullable": False,
                    },
                    {"name": "trade_date", "type": "DATE", "nullable": False},
                    {"name": "open", "type": "NUMERIC", "precision": 10, "scale": 2},
                    {"name": "close", "type": "NUMERIC", "precision": 10, "scale": 2},
                    {"name": "volume", "type": "BIGINT"},
                ],
                "indexes": [
                    {
                        "name": "idx_stock_daily_symbol_date",
                        "columns": ["symbol", "trade_date"],
                        "unique": True,
                    }
                ],
            },
            {
                "table_name": "user_profiles",
                "database_type": "MySQL",
                "columns": [
                    {
                        "name": "id",
                        "type": "INT",
                        "primary_key": True,
                        "auto_increment": True,
                    },
                    {
                        "name": "username",
                        "type": "VARCHAR",
                        "length": 50,
                        "nullable": False,
                        "unique": True,
                    },
                    {"name": "email", "type": "VARCHAR", "length": 100},
                    {
                        "name": "created_at",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP",
                    },
                ],
                "indexes": [
                    {"name": "idx_username", "columns": ["username"], "unique": True}
                ],
            },
            {
                "table_name": "cache_data",
                "database_type": "Redis",
                "data_classification": "缓存数据",
            },
        ],
    }


@pytest.fixture
def temp_config_file(sample_table_config):
    """创建临时配置文件"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(sample_table_config, f, allow_unicode=True)
        temp_path = f.name

    yield temp_path

    # 清理
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestConfigDrivenTableManagerInitialization:
    """测试ConfigDrivenTableManager初始化"""

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_initialization_with_valid_config(
        self, mock_conn_manager, temp_config_file
    ):
        """测试使用有效配置文件初始化"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file, safe_mode=True)

        assert manager.config_path == Path(temp_config_file)
        assert manager.safe_mode is True
        assert manager.config is not None
        assert manager.config["version"] == "2.0.0"
        assert len(manager.config["tables"]) == 4
        mock_conn_manager.assert_called_once()

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_initialization_with_invalid_config_path(self, mock_conn_manager):
        """测试使用无效配置文件路径初始化"""
        with pytest.raises(FileNotFoundError, match="配置文件不存在"):
            ConfigDrivenTableManager(config_path="/nonexistent/config.yaml")

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_initialization_with_safe_mode_disabled(
        self, mock_conn_manager, temp_config_file
    ):
        """测试关闭安全模式"""
        manager = ConfigDrivenTableManager(
            config_path=temp_config_file, safe_mode=False
        )
        assert manager.safe_mode is False


class TestConfigDrivenTableManagerLoadConfig:
    """测试配置加载功能"""

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_load_config_returns_dict(self, mock_conn_manager, temp_config_file):
        """测试load_config返回字典"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)
        config = manager.load_config()

        assert isinstance(config, dict)
        assert "version" in config
        assert "tables" in config
        assert "databases" in config

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_load_config_parses_yaml_correctly(
        self, mock_conn_manager, temp_config_file
    ):
        """测试YAML解析正确性"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)
        config = manager.load_config()

        assert config["version"] == "2.0.0"
        assert len(config["tables"]) == 4
        assert config["tables"][0]["table_name"] == "tick_data"


class TestConfigDrivenTableManagerInitializeTables:
    """测试表初始化功能"""

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_initialize_tables_creates_all_tables(
        self, mock_conn_manager, temp_config_file
    ):
        """测试初始化所有表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock _create_table方法返回True(表示成功创建)
        with patch.object(manager, "_create_table", return_value=True) as mock_create:
            result = manager.initialize_tables()

            assert result["tables_created"] == 4  # 4个表都应该被创建
            assert result["tables_skipped"] == 0
            assert len(result["errors"]) == 0
            assert mock_create.call_count == 4

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_initialize_tables_skips_existing_tables(
        self, mock_conn_manager, temp_config_file
    ):
        """测试跳过已存在的表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 前两个表已存在(返回False),后两个表不存在(返回True)
        with patch.object(
            manager, "_create_table", side_effect=[False, False, True, True]
        ):
            result = manager.initialize_tables()

            assert result["tables_created"] == 2
            assert result["tables_skipped"] == 2
            assert len(result["errors"]) == 0

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_initialize_tables_handles_errors(
        self, mock_conn_manager, temp_config_file
    ):
        """测试处理创建表时的错误"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # 第一个表成功,第二个表失败,第三个表成功,第四个表成功
        def create_side_effect(table_def):
            if table_def["table_name"] == "stock_daily":
                raise RuntimeError("创建失败")
            return True

        with patch.object(manager, "_create_table", side_effect=create_side_effect):
            result = manager.initialize_tables()

            assert result["tables_created"] == 3
            assert result["tables_skipped"] == 0
            assert len(result["errors"]) == 1
            assert "stock_daily" in result["errors"][0]


class TestConfigDrivenTableManagerTableExists:
    """测试表存在性检查"""

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_table_exists_tdengine_true(self, mock_conn_manager, temp_config_file):
        """测试TDengine表存在检查(存在)"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock TDengine连接
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("tick_data",)]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        manager.conn_manager.get_tdengine_connection = Mock(return_value=mock_conn)

        exists = manager._table_exists("TDengine", "tick_data")
        assert exists is True
        mock_cursor.execute.assert_called_once()

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_table_exists_tdengine_false(self, mock_conn_manager, temp_config_file):
        """测试TDengine表存在检查(不存在)"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock TDengine连接
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        manager.conn_manager.get_tdengine_connection = Mock(return_value=mock_conn)

        exists = manager._table_exists("TDengine", "nonexistent_table")
        assert exists is False

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_table_exists_postgresql_true(self, mock_conn_manager, temp_config_file):
        """测试PostgreSQL表存在检查(存在)"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock PostgreSQL连接
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (True,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        manager.conn_manager.get_postgresql_connection = Mock(return_value=mock_conn)
        manager.conn_manager._return_postgresql_connection = Mock()

        exists = manager._table_exists("PostgreSQL", "stock_daily")
        assert exists is True

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_table_exists_mysql_true(self, mock_conn_manager, temp_config_file):
        """测试MySQL表存在检查(存在)"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock MySQL连接
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        manager.conn_manager.get_mysql_connection = Mock(return_value=mock_conn)

        exists = manager._table_exists("MySQL", "user_profiles", "test_db")
        assert exists is True

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_table_exists_handles_errors(self, mock_conn_manager, temp_config_file):
        """测试表存在性检查时的错误处理"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock连接抛出异常
        manager.conn_manager.get_postgresql_connection = Mock(
            side_effect=Exception("连接失败")
        )

        exists = manager._table_exists("PostgreSQL", "test_table")
        assert exists is False  # 错误时返回False

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_table_exists_invalid_table_name(self, mock_conn_manager, temp_config_file):
        """测试无效表名检查(SQL注入防护)"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock TDengine连接
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        manager.conn_manager.get_tdengine_connection = Mock(return_value=mock_conn)

        # 表名包含SQL注入字符 - 代码会捕获异常并返回False
        exists = manager._table_exists("TDengine", "'; DROP TABLE users; --")
        assert exists is False  # SQL注入尝试被阻止,返回False


class TestConfigDrivenTableManagerValidateStructure:
    """测试表结构验证功能"""

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_validate_table_structure_success(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试表结构验证成功"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表存在
        manager._table_exists = Mock(return_value=True)

        # Mock获取表结构
        manager._get_table_structure = Mock(
            return_value=[
                {"name": "ts", "type": "TIMESTAMP"},
                {"name": "symbol", "type": "NCHAR"},
                {"name": "price", "type": "FLOAT"},
                {"name": "volume", "type": "BIGINT"},
            ]
        )

        table_def = sample_table_config["tables"][0]  # tick_data
        result = manager.validate_table_structure(table_def)

        assert result is True

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_validate_table_structure_table_not_exists(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试验证不存在的表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表不存在
        manager._table_exists = Mock(return_value=False)

        table_def = sample_table_config["tables"][0]
        result = manager.validate_table_structure(table_def)

        assert result is False

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_validate_table_structure_missing_columns(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试检测缺失的列"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表存在
        manager._table_exists = Mock(return_value=True)

        # Mock获取表结构(缺少volume列)
        manager._get_table_structure = Mock(
            return_value=[
                {"name": "ts", "type": "TIMESTAMP"},
                {"name": "symbol", "type": "NCHAR"},
                {"name": "price", "type": "FLOAT"},
            ]
        )

        table_def = sample_table_config["tables"][0]
        result = manager.validate_table_structure(table_def)

        assert result is False

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_validate_table_structure_type_mismatch(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试检测列类型不匹配"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表存在
        manager._table_exists = Mock(return_value=True)

        # Mock获取表结构(price类型错误)
        manager._get_table_structure = Mock(
            return_value=[
                {"name": "ts", "type": "TIMESTAMP"},
                {"name": "symbol", "type": "NCHAR"},
                {"name": "price", "type": "INT"},  # 应该是FLOAT
                {"name": "volume", "type": "BIGINT"},
            ]
        )

        table_def = sample_table_config["tables"][0]
        result = manager.validate_table_structure(table_def)

        assert result is False


class TestConfigDrivenTableManagerGetTableStructure:
    """测试获取表结构功能"""

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_get_table_structure_postgresql(self, mock_conn_manager, temp_config_file):
        """测试获取PostgreSQL表结构"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock PostgreSQL连接
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("id", "integer"),
            ("symbol", "character varying"),
            ("trade_date", "date"),
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        manager.conn_manager.get_postgresql_connection = Mock(return_value=mock_conn)
        manager.conn_manager._return_postgresql_connection = Mock()

        structure = manager._get_table_structure("PostgreSQL", "stock_daily")

        assert structure is not None
        assert len(structure) == 3
        assert structure[0]["name"] == "id"
        assert structure[0]["type"] == "integer"

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_get_table_structure_tdengine(self, mock_conn_manager, temp_config_file):
        """测试获取TDengine表结构"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock TDengine连接
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("ts", "TIMESTAMP"),
            ("symbol", "NCHAR(20)"),
            ("price", "FLOAT"),
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        manager.conn_manager.get_tdengine_connection = Mock(return_value=mock_conn)

        structure = manager._get_table_structure("TDengine", "tick_data")

        assert structure is not None
        assert len(structure) == 3
        assert structure[0]["name"] == "ts"

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_get_table_structure_handles_errors(
        self, mock_conn_manager, temp_config_file
    ):
        """测试获取表结构时的错误处理"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock连接抛出异常
        manager.conn_manager.get_postgresql_connection = Mock(
            side_effect=Exception("查询失败")
        )

        structure = manager._get_table_structure("PostgreSQL", "test_table")
        assert structure is None

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_get_table_structure_unsupported_db_type(
        self, mock_conn_manager, temp_config_file
    ):
        """测试不支持的数据库类型"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        structure = manager._get_table_structure("Oracle", "test_table")
        assert structure is None


class TestConfigDrivenTableManagerCreateTable:
    """测试创建表功能"""

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_create_table_tdengine(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试创建TDengine表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表不存在
        manager._table_exists = Mock(return_value=False)
        manager._create_tdengine_super_table = Mock(return_value=True)

        table_def = sample_table_config["tables"][0]  # tick_data (TDengine)
        result = manager._create_table(table_def)

        assert result is True
        manager._create_tdengine_super_table.assert_called_once_with(table_def)

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_create_table_postgresql(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试创建PostgreSQL表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表不存在
        manager._table_exists = Mock(return_value=False)
        manager._create_postgresql_table = Mock(return_value=True)

        table_def = sample_table_config["tables"][1]  # stock_daily (PostgreSQL)
        result = manager._create_table(table_def)

        assert result is True
        manager._create_postgresql_table.assert_called_once_with(table_def)

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_create_table_mysql(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试创建MySQL表"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表不存在
        manager._table_exists = Mock(return_value=False)
        manager._create_mysql_table = Mock(return_value=True)

        table_def = sample_table_config["tables"][2]  # user_profiles (MySQL)
        result = manager._create_table(table_def)

        assert result is True
        manager._create_mysql_table.assert_called_once_with(table_def)

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_create_table_redis_skip(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试Redis表跳过创建"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表不存在
        manager._table_exists = Mock(return_value=False)

        table_def = sample_table_config["tables"][3]  # cache_data (Redis)
        result = manager._create_table(table_def)

        assert result is False  # Redis不需要创建表

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_create_table_already_exists(
        self, mock_conn_manager, temp_config_file, sample_table_config
    ):
        """测试表已存在时跳过创建"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表已存在
        manager._table_exists = Mock(return_value=True)

        table_def = sample_table_config["tables"][0]
        result = manager._create_table(table_def)

        assert result is False

    @patch("src.core.config_driven_table_manager.DatabaseConnectionManager")
    def test_create_table_unsupported_db_type(
        self, mock_conn_manager, temp_config_file
    ):
        """测试不支持的数据库类型"""
        manager = ConfigDrivenTableManager(config_path=temp_config_file)

        # Mock表不存在
        manager._table_exists = Mock(return_value=False)

        table_def = {
            "table_name": "test_table",
            "database_type": "MongoDB",  # 不支持
        }

        with pytest.raises(ValueError, match="不支持的数据库类型"):
            manager._create_table(table_def)
