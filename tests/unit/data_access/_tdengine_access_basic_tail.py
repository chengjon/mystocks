"""Support tests extracted from `test_tdengine_access_basic.py`."""

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd

from src.data_access.tdengine_access import TDengineDataAccess


class TestTDengineDataAccessBasicTailMixin:
    """TDengineDataAccess基础测试尾部方法集"""

    def test_method_parameter_validation(self):
        """测试方法参数验证"""
        import inspect

        data_access = TDengineDataAccess()

        methods_to_check = [
            "create_stable",
            "create_table",
            "insert_dataframe",
            "query_by_time_range",
            "query_latest",
            "aggregate_to_kline",
            "delete_by_time_range",
            "get_table_info",
        ]

        for method_name in methods_to_check:
            method = getattr(data_access, method_name)
            sig = inspect.signature(method)
            assert sig is not None
            assert len(sig.parameters) >= 1

    def test_dataframe_processing_capabilities(self):
        """测试DataFrame处理能力"""
        data_access = TDengineDataAccess()

        test_dfs = [
            pd.DataFrame({"ts": pd.date_range("2025-01-01", periods=2), "price": [10.0, 20.0]}),
            pd.DataFrame({"timestamp": pd.date_range("2025-01-01", periods=2), "bid": [0.5, 0.8]}),
            pd.DataFrame({"ts": ["2025-01-01", "2025-01-02"], "value": [1, 2]}),
        ]

        for df in test_dfs:
            assert not df.empty
            assert len(df) > 0

    def test_class_documentation(self):
        """测试类文档"""
        class_doc = TDengineDataAccess.__doc__
        assert class_doc is not None
        assert len(class_doc.strip()) > 0
        assert "TDengine" in class_doc

    def test_module_imports(self):
        """测试模块导入"""
        from src.data_access.tdengine_access import TDengineDataAccess, datetime, pd

        assert TDengineDataAccess is not None
        assert pd is not None
        assert datetime is not None

    def test_database_error_handling_in_get_table_info(self):
        """测试获取表信息时的数据库错误处理"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.execute.side_effect = Exception("Connection failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.get_table_info("test_table")

            assert result == {"row_count": 0, "start_time": None, "end_time": None}

    def test_timestamp_formatting_in_insert(self):
        """测试插入时时间戳格式化"""
        test_df = pd.DataFrame(
            {
                "ts": [datetime(2025, 1, 1, 9, 30, 0, 500000)],
                "price": [10.5],
                "volume": [1000],
            }
        )

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            data_access.insert_dataframe("test_table", test_df)

            sql_call = mock_cursor.execute.call_args[0][0]
            assert "2025-01-01 09:30:00.500" in sql_call

    def test_all_method_signatures(self):
        """测试所有方法签名的完整性"""
        import inspect

        data_access = TDengineDataAccess()

        expected_methods = [
            "__init__",
            "_get_connection",
            "create_stable",
            "create_table",
            "insert_dataframe",
            "query_by_time_range",
            "query_latest",
            "aggregate_to_kline",
            "delete_by_time_range",
            "get_table_info",
            "save_data",
            "load_data",
            "close",
        ]

        for method_name in expected_methods:
            assert hasattr(data_access, method_name), f"缺少方法: {method_name}"

            method = getattr(data_access, method_name)
            sig = inspect.signature(method)
            assert sig is not None, f"方法签名为空: {method_name}"
