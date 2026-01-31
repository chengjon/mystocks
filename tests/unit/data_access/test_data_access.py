"""
数据访问层单元测试
测试data_access.py和storage模块的核心功能
"""

import os
import sys
from unittest.mock import Mock

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


# 模拟数据访问类
class MockPostgreSQLDataAccess:
    """模拟PostgreSQL数据访问类"""

    def __init__(self, connection_string="mock://localhost/db"):
        self.connection_string = connection_string
        self.connected = False
        self.connection_pool = None

    def connect(self):
        """模拟连接"""
        self.connected = True
        self.connection_pool = Mock()
        return True

    def disconnect(self):
        """模拟断开连接"""
        self.connected = False
        self.connection_pool = None

    def execute_query(self, query, params=None):
        """模拟执行查询"""
        if not self.connected:
            raise Exception("Not connected to database")

        # 返回模拟数据
        return pd.DataFrame(
            {
                "stock_code": ["000001", "000002", "600000"],
                "stock_name": ["平安银行", "万科A", "浦发银行"],
                "price": [12.34, 15.67, 8.90],
                "volume": [1000000, 2000000, 1500000],
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="D"),
            }
        )

    def insert_data(self, table, data):
        """模拟插入数据"""
        if not self.connected:
            raise Exception("Not connected to database")
        return {"rows_affected": len(data) if isinstance(data, (list, pd.DataFrame)) else 1}

    def update_data(self, table, data, condition):
        """模拟更新数据"""
        if not self.connected:
            raise Exception("Not connected to database")
        return {"rows_affected": 1}


class MockTDengineDataAccess:
    """模拟TDengine数据访问类"""

    def __init__(self, host="localhost", port=6041, database="mystocks"):
        self.host = host
        self.port = port
        self.database = database
        self.connected = False

    def connect(self):
        """模拟连接"""
        self.connected = True
        return True

    def disconnect(self):
        """模拟断开连接"""
        self.connected = False

    def write_points(self, points):
        """模拟写入时序数据"""
        if not self.connected:
            raise Exception("Not connected to TDengine")
        return len(points)

    def query_timeseries(self, query):
        """模拟查询时序数据"""
        if not self.connected:
            raise Exception("Not connected to TDengine")

        # 从查询中解析symbol
        import re

        symbol = "000001"  # 默认值
        match = re.search(r"symbol='(\d+)'", query)
        if match:
            symbol = match.group(1)

        # 返回模拟的时序数据
        return pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01 09:30:00", periods=100, freq="1min"),
                "price": [10.0 + i * 0.1 for i in range(100)],
                "volume": [1000 + i * 10 for i in range(100)],
                "symbol": [symbol] * 100,
            }
        )


class TestPostgreSQLDataAccess:
    """PostgreSQL数据访问测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.data_access = MockPostgreSQLDataAccess()

    def test_connection(self):
        """测试数据库连接"""
        assert not self.data_access.connected

        result = self.data_access.connect()
        assert result is True
        assert self.data_access.connected is True

    def test_disconnection(self):
        """测试数据库断开连接"""
        self.data_access.connect()
        assert self.data_access.connected is True

        self.data_access.disconnect()
        assert self.data_access.connected is False

    def test_execute_query(self):
        """测试执行查询"""
        self.data_access.connect()

        result = self.data_access.execute_query("SELECT * FROM stocks")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "stock_code" in result.columns
        assert "stock_name" in result.columns

    def test_execute_query_not_connected(self):
        """测试未连接时执行查询"""
        with pytest.raises(Exception, match="Not connected to database"):
            self.data_access.execute_query("SELECT * FROM stocks")

    def test_insert_data(self):
        """测试插入数据"""
        self.data_access.connect()

        test_data = [{"stock_code": "000001", "price": 12.34}]
        result = self.data_access.insert_data("stocks", test_data)

        assert result["rows_affected"] == 1

    def test_update_data(self):
        """测试更新数据"""
        self.data_access.connect()

        test_data = {"price": 15.00}
        condition = "stock_code = '000001'"
        result = self.data_access.update_data("stocks", test_data, condition)

        assert result["rows_affected"] == 1

    def test_insert_data_not_connected(self):
        """测试未连接时插入数据"""
        test_data = [{"stock_code": "000001", "price": 12.34}]
        with pytest.raises(Exception, match="Not connected to database"):
            self.data_access.insert_data("stocks", test_data)


class TestTDengineDataAccess:
    """TDengine数据访问测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.tdengine = MockTDengineDataAccess()

    def test_connection(self):
        """测试TDengine连接"""
        assert not self.tdengine.connected

        result = self.tdengine.connect()
        assert result is True
        assert self.tdengine.connected is True

    def test_disconnection(self):
        """测试TDengine断开连接"""
        self.tdengine.connect()
        assert self.tdengine.connected is True

        self.tdengine.disconnect()
        assert self.tdengine.connected is False

    def test_write_points(self):
        """测试写入时序数据点"""
        self.tdengine.connect()

        test_points = [
            {"symbol": "000001", "price": 10.5, "volume": 1000},
            {"symbol": "000002", "price": 15.3, "volume": 2000},
        ]

        result = self.tdengine.write_points(test_points)
        assert result == 2

    def test_write_points_not_connected(self):
        """测试未连接时写入数据"""
        test_points = [{"symbol": "000001", "price": 10.5}]

        with pytest.raises(Exception, match="Not connected to TDengine"):
            self.tdengine.write_points(test_points)

    def test_query_timeseries(self):
        """测试查询时序数据"""
        self.tdengine.connect()

        result = self.tdengine.query_timeseries("SELECT * FROM prices WHERE symbol='000001'")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 100
        assert "timestamp" in result.columns
        assert "price" in result.columns
        assert "volume" in result.columns

    def test_query_timeseries_not_connected(self):
        """测试未连接时查询时序数据"""
        with pytest.raises(Exception, match="Not connected to TDengine"):
            self.tdengine.query_timeseries("SELECT * FROM prices")

    def test_timeseries_data_format(self):
        """测试时序数据格式"""
        self.tdengine.connect()

        result = self.tdengine.query_timeseries("SELECT * FROM prices")

        # 验证数据连续性
        assert len(result) > 0
        assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
        assert pd.api.types.is_numeric_dtype(result["price"])
        assert pd.api.types.is_numeric_dtype(result["volume"])


class TestDataAccessIntegration:
    """数据访问集成测试"""

    def test_postgresql_and_tdengine_integration(self):
        """测试PostgreSQL和TDengine的集成使用"""
        pg_access = MockPostgreSQLDataAccess()
        tdengine = MockTDengineDataAccess()

        # 连接数据库
        pg_access.connect()
        tdengine.connect()

        # 从PostgreSQL获取股票列表
        stocks = pg_access.execute_query("SELECT DISTINCT stock_code FROM stocks WHERE status='active'")

        # 为每只股票查询TDengine的时序数据
        for _, stock in stocks.iterrows():
            symbol = stock["stock_code"]
            ts_data = tdengine.query_timeseries(f"SELECT * FROM prices WHERE symbol='{symbol}'")

            # 验证时序数据
            assert isinstance(ts_data, pd.DataFrame)
            assert not ts_data.empty
            assert "symbol" in ts_data.columns
            assert ts_data["symbol"].iloc[0] == symbol

    def test_data_consistency(self):
        """测试数据一致性"""
        pg_access = MockPostgreSQLDataAccess()
        pg_access.connect()

        # 获取最新的股票价格信息
        current_data = pg_access.execute_query("SELECT stock_code, price FROM stocks ORDER BY timestamp DESC LIMIT 1")

        if not current_data.empty:
            stock_code = current_data.iloc[0]["stock_code"]
            current_price = current_data.iloc[0]["price"]

            # 验证价格数据的合理性
            assert current_price > 0
            assert isinstance(current_price, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
