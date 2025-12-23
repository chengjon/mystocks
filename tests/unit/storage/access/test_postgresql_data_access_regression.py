"""
PostgreSQLDataAccess._build_analytical_query 方法的回归测试

该测试旨在捕获_build_analytical_query 方法在重构前的当前行为，
特别是其在处理各种过滤、排序和分页参数时生成SQL语句的逻辑。
"""

import os
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# 添加项目根目录到sys.path
sys.path.insert(0, os.getcwd())

import pytest
from src.storage.access.base import DataClassification

# 添加源码路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent / "src"))



# 导入目标模块和类
from src.data_access.postgresql_access import PostgreSQLDataAccess
from src.monitoring.monitoring_database import MonitoringDatabase

# 模拟环境变量
@pytest.fixture(autouse=True)
def mock_os_getenv():
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            "POSTGRESQL_HOST": "test_host",
            "POSTGRESQL_USER": "test_user",
            "POSTGRESQL_PASSWORD": "test_password",
            "POSTGRESQL_PORT": "5432"
        }.get(key, default)
        yield mock_getenv

class TestPostgreSQLDataAccessRegression:
    """PostgreSQLDataAccess._build_analytical_query 方法的回归测试类"""

    @pytest.fixture
    def data_access_instance(self):
        """为测试提供PostgreSQLDataAccess实例，并模拟MonitoringDatabase"""
        mock_monitoring_db = Mock(spec=MonitoringDatabase)

        # Mock DatabaseTableManager which is called in PostgreSQLDataAccess __init__
        with patch('src.storage.database.database_manager.DatabaseTableManager') as mock_db_manager_class:
            mock_db_manager_instance = Mock()
            mock_db_manager_class.return_value = mock_db_manager_instance
            instance = PostgreSQLDataAccess(mock_monitoring_db)
            return instance
        return instance

    def test_basic_query(self, data_access_instance):
        """测试基本查询语句生成"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline"
        )
        assert sql == "SELECT * FROM daily_kline ORDER BY trade_date DESC"
        assert params == ()

    def test_query_with_single_filter(self, data_access_instance):
        """测试带单个过滤条件的查询"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", filters={"symbol": "AAPL"}
        )
        assert sql == "SELECT * FROM daily_kline WHERE symbol = %s ORDER BY trade_date DESC"
        assert params == ("AAPL",)

    def test_query_with_multiple_filters(self, data_access_instance):
        """测试带多个过滤条件的查询"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            filters={"symbol": "AAPL", "trade_date": "2023-01-01"},
        )
        assert sql == "SELECT * FROM daily_kline WHERE symbol = %s AND trade_date = %s ORDER BY trade_date DESC"
        assert params == ("AAPL", "2023-01-01")

    def test_query_with_list_filter_in_clause(self, data_access_instance):
        """测试带列表过滤条件的查询 (IN 子句)"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            filters={"symbol": ["AAPL", "MSFT"]},
        )
        assert sql == "SELECT * FROM daily_kline WHERE symbol IN (%s, %s) ORDER BY trade_date DESC"
        assert params == ("AAPL", "MSFT")

    def test_query_with_order_by_asc(self, data_access_instance):
        """测试带升序排序的查询"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", order_by="trade_date ASC"
        )
        assert sql == "SELECT * FROM daily_kline ORDER BY trade_date ASC"
        assert params == ()

    def test_query_with_order_by_desc(self, data_access_instance):
        """测试带降序排序的查询"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", order_by="trade_date DESC"
        )
        assert sql == "SELECT * FROM daily_kline ORDER BY trade_date DESC"
        assert params == ()

    def test_query_with_multiple_order_by_columns(self, data_access_instance):
        """测试带多列排序的查询"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", order_by="trade_date DESC, symbol ASC"
        )
        assert sql == "SELECT * FROM daily_kline ORDER BY trade_date DESC, symbol ASC"
        assert params == ()

    def test_query_with_limit_and_offset(self, data_access_instance):
        """测试带限制和偏移量的查询"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", limit=10, offset=5
        )
        assert sql == "SELECT * FROM daily_kline ORDER BY trade_date DESC LIMIT 10 OFFSET 5"
        assert params == ()

    def test_query_invalid_table_name_raises_error(self, data_access_instance):
        """测试非法表名引发错误"""
        with pytest.raises(ValueError, match="Invalid table name"):
            data_access_instance._build_analytical_query(
                DataClassification.DAILY_KLINE, "drop_table"
            )

    def test_query_invalid_order_by_column_uses_default(self, data_access_instance):
        """测试非法排序列名使用默认排序"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", order_by="invalid_col ASC"
        )
        assert sql == "SELECT * FROM daily_kline ORDER BY trade_date DESC"
        assert params == ()

    @patch('src.data_access.postgresql_access.logger') # patch logger to capture warnings
    def test_query_invalid_order_by_column_logs_warning(self, mock_logger, data_access_instance):
        """测试非法排序列名记录警告日志"""
        data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", order_by="invalid_col ASC"
        )
        mock_logger.warning.assert_called_once()
        assert "Invalid order_by columns: invalid_col ASC, using default sort" in mock_logger.warning.call_args[0][0]

    def test_query_with_kwargs_filters(self, data_access_instance):
        """测试kwargs中传递的过滤条件"""
        sql, params = data_access_instance._build_analytical_query(
            DataClassification.DAILY_KLINE, "daily_kline", symbol="MSFT", trade_date="2023-01-02"
        )
        assert sql == "SELECT * FROM daily_kline WHERE symbol = %s AND trade_date = %s ORDER BY trade_date DESC"
        assert params == ("MSFT", "2023-01-02")
