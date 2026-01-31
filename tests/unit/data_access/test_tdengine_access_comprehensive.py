"""
TDengine Access 综合测试 - 增强版
全面测试 TDengineDataAccess 类的所有功能，提升覆盖率
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.data_access.tdengine_access import TDengineDataAccess


class TestTDengineDataAccessComprehensive:
    """TDengineDataAccess 综合测试 - 专注覆盖率"""

    @pytest.fixture
    def access(self):
        with patch("src.data_access.tdengine_access.get_connection_manager") as mock_get_manager:
            mock_manager = Mock()
            mock_conn = Mock()
            mock_manager.get_tdengine_connection.return_value = mock_conn
            mock_get_manager.return_value = mock_manager

            da = TDengineDataAccess()
            return da

    def test_init(self, access):
        """测试初始化属性"""
        assert access.conn is None
        assert access.conn_manager is not None

    def test_get_connection(self, access):
        """测试获取连接及缓存"""
        conn1 = access._get_connection()
        assert conn1 is not None
        conn2 = access._get_connection()
        assert conn1 == conn2

    def test_create_stable_success(self, access):
        """测试成功创建超表"""
        mock_cursor = access._get_connection().cursor.return_value
        access.create_stable("st1", {"ts": "timestamp"}, {"tag1": "int"})
        assert mock_cursor.execute.called
        assert mock_cursor.close.called

    def test_create_stable_error(self, access):
        """测试创建超表错误"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Create Stable Error")
        with pytest.raises(Exception, match="Create Stable Error"):
            access.create_stable("st1", {}, {})
        assert mock_cursor.close.called

    def test_create_table_success(self, access):
        """测试成功创建子表"""
        mock_cursor = access._get_connection().cursor.return_value
        access.create_table("t1", "st1", {"tag1": 100})
        assert mock_cursor.execute.called
        assert mock_cursor.close.called

    def test_create_table_error(self, access):
        """测试创建子表错误"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Create Table Error")
        with pytest.raises(Exception, match="Create Table Error"):
            access.create_table("t1", "st1", {})
        assert mock_cursor.close.called

    def test_insert_dataframe_success(self, access):
        """测试批量插入DataFrame"""
        df = pd.DataFrame(
            {
                "ts": [datetime(2024, 1, 1), datetime(2024, 1, 1, 0, 0, 1)],
                "val": [1.1, None],
                "str_col": ["a", "b"],
            }
        )
        mock_cursor = access._get_connection().cursor.return_value
        count = access.insert_dataframe("t1", df)
        assert count == 2
        assert mock_cursor.execute.called
        assert mock_cursor.close.called

    def test_insert_dataframe_empty(self, access):
        """测试插入空数据"""
        assert access.insert_dataframe("t1", pd.DataFrame()) == 0

    def test_insert_dataframe_error(self, access):
        """测试插入错误"""
        df = pd.DataFrame({"ts": [datetime.now()], "v": [1]})
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Insert Error")
        with pytest.raises(Exception, match="Insert Error"):
            access.insert_dataframe("t1", df)
        assert mock_cursor.close.called

    def test_query_by_time_range_success(self, access):
        """测试时间范围查询"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.description = [("ts",), ("val",)]
        mock_cursor.fetchall.return_value = [(datetime(2024, 1, 1), 10.5)]

        df = access.query_by_time_range(
            "t1",
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            columns=["ts", "val"],
            limit=10,
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert mock_cursor.close.called

    def test_query_by_time_range_error(self, access):
        """测试查询错误"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Query Error")
        with pytest.raises(Exception, match="Query Error"):
            access.query_by_time_range("t1", datetime.now(), datetime.now())
        assert mock_cursor.close.called

    def test_query_latest_success(self, access):
        """测试查询最新数据"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.description = [("ts",), ("val",)]
        mock_cursor.fetchall.return_value = [(datetime.now(), 99)]

        df = access.query_latest("t1", limit=5)
        assert len(df) == 1
        assert mock_cursor.close.called

    def test_query_latest_error(self, access):
        """测试查询最新数据错误"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Latest Error")
        with pytest.raises(Exception, match="Latest Error"):
            access.query_latest("t1")
        assert mock_cursor.close.called

    def test_aggregate_to_kline_success(self, access):
        """测试K线聚合"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.description = [
            ("ts",),
            ("open",),
            ("high",),
            ("low",),
            ("close",),
            ("volume",),
        ]
        mock_cursor.fetchall.return_value = [(datetime.now(), 10, 11, 9, 10.5, 1000)]

        df = access.aggregate_to_kline("t1", datetime.now(), datetime.now(), interval="5m")
        assert len(df) == 1
        assert mock_cursor.close.called

    def test_aggregate_to_kline_error(self, access):
        """测试K线聚合错误"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Agg Error")
        with pytest.raises(Exception, match="Agg Error"):
            access.aggregate_to_kline("t1", datetime.now(), datetime.now())
        assert mock_cursor.close.called

    def test_delete_by_time_range_success(self, access):
        """测试按时间范围删除"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.rowcount = 50

        count = access.delete_by_time_range("t1", datetime.now(), datetime.now())
        assert count == 50
        assert mock_cursor.close.called

    def test_delete_by_time_range_error(self, access):
        """测试删除错误"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Delete Error")
        with pytest.raises(Exception, match="Delete Error"):
            access.delete_by_time_range("t1", datetime.now(), datetime.now())
        assert mock_cursor.close.called

    def test_get_table_info_success(self, access):
        """测试获取表信息"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.fetchone.return_value = (
            100,
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
        )

        info = access.get_table_info("t1")
        assert info["row_count"] == 100
        assert info["start_time"] == datetime(2024, 1, 1)
        assert mock_cursor.close.called

    def test_get_table_info_error(self, access):
        """测试获取表信息错误"""
        mock_cursor = access._get_connection().cursor.return_value
        mock_cursor.execute.side_effect = Exception("Info Error")
        info = access.get_table_info("t1")
        assert info["row_count"] == 0
        assert mock_cursor.close.called

    def test_save_data_interface(self, access):
        """测试save_data接口"""
        df = pd.DataFrame({"ts": [datetime.now()], "v": [1]})
        with patch.object(access, "insert_dataframe", return_value=1):
            assert access.save_data(df, None, "t1") is True

        with patch.object(access, "insert_dataframe", side_effect=Exception("Save Error")):
            assert access.save_data(df, None, "t1") is False

    def test_load_data_interface(self, access):
        """测试load_data接口"""
        mock_df = pd.DataFrame({"a": [1]})

        # 时间范围分支
        with patch.object(access, "query_by_time_range", return_value=mock_df):
            res = access.load_data("t1", start_time=datetime.now(), end_time=datetime.now())
            assert len(res) == 1

        # 最新数据分支
        with patch.object(access, "query_latest", return_value=mock_df):
            res = access.load_data("t1", limit=10)
            assert len(res) == 1

    def test_load_data_interface_error(self, access):
        """测试load_data接口错误"""
        with patch.object(access, "query_latest", side_effect=Exception("Load Error")):
            assert access.load_data("t1") is None

    def test_close(self, access):
        """测试关闭连接"""
        mock_conn = access._get_connection()
        access.close()
        assert mock_conn.close.called
        assert access.conn is None


if __name__ == "__main__":
    pytest.main([__file__])
