#!/usr/bin/env python3
"""
TDengine数据访问功能测试
使用Mock测试时序数据库操作逻辑，专注于高频金融数据
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestTDengineDataAccessFunctionality:
    """TDengine数据访问功能测试"""

    def test_timeseries_data_structure(self):
        """测试时序数据结构"""
        # 创建时序数据
        timestamp = datetime.now()
        timeseries_data = pd.DataFrame(
            {
                "ts": [timestamp, timestamp + timedelta(minutes=1)],
                "symbol": ["600519", "600519"],
                "price": [1750.50, 1751.00],
                "volume": [1000, 1200],
                "high": [1752.00, 1753.00],
                "low": [1750.00, 1750.50],
                "open": [1751.00, 1751.50],
                "close": [1750.50, 1751.00],
            }
        )

        # 验证数据结构
        assert len(timeseries_data) == 2
        assert "ts" in timeseries_data.columns  # 时间戳列
        assert "symbol" in timeseries_data.columns
        assert timeseries_data["symbol"].iloc[0] == "600519"
        assert timeseries_data["price"].sum() == pytest.approx(3501.5, rel=1e-2)

    def test_time_range_query(self):
        """测试时间范围查询"""

        def generate_time_range_query(table, symbol, start_time, end_time):
            """生成时间范围查询SQL"""
            return f"""
            SELECT * FROM {table}
            WHERE symbol = '{symbol}'
            AND ts >= '{start_time.strftime("%Y-%m-%d %H:%M:%S")}'
            AND ts <= '{end_time.strftime("%Y-%m-%d %H:%M:%S")}'
            ORDER BY ts ASC
            """

        # 测试时间范围查询生成
        symbol = "600519"
        start_time = datetime(2024, 1, 1, 9, 30, 0)
        end_time = datetime(2024, 1, 1, 15, 0, 0)

        query = generate_time_range_query("minute_kline", symbol, start_time, end_time)

        assert "minute_kline" in query
        assert "600519" in query
        assert "2024-01-01 09:30:00" in query
        assert "2024-01-01 15:00:00" in query
        assert "ORDER BY ts ASC" in query

    def test_tick_data_handling(self):
        """测试tick数据处理"""

        def create_tick_data(symbol, base_price, count):
            """创建tick数据"""
            base_time = datetime.now()
            data = []
            for i in range(count):
                price = base_price + (i * 0.01)
                volume = 100 + (i * 10)
                data.append(
                    {
                        "ts": base_time + timedelta(milliseconds=i * 500),
                        "symbol": symbol,
                        "price": price,
                        "volume": volume,
                        "direction": "BUY" if i % 2 == 0 else "SELL",
                    }
                )
            return pd.DataFrame(data)

        # 测试tick数据创建
        tick_data = create_tick_data("600519", 1750.00, 10)

        assert len(tick_data) == 10
        assert tick_data["price"].iloc[0] == 1750.00
        assert tick_data["price"].iloc[-1] == 1750.09
        assert tick_data["direction"].value_counts()["BUY"] == 5
        assert tick_data["direction"].value_counts()["SELL"] == 5

    def test_data_aggregation(self):
        """测试数据聚合"""
        # 创建分钟K线数据
        base_time = datetime(2024, 1, 1, 9, 30, 0)
        minute_data = pd.DataFrame(
            {
                "ts": [base_time + timedelta(minutes=i) for i in range(5)],
                "symbol": ["600519"] * 5,
                "close": [1750.00, 1751.00, 1749.50, 1752.00, 1751.50],
                "volume": [1000, 1200, 800, 1500, 900],
            }
        )

        # 模拟OHLC聚合逻辑
        def aggregate_to_ohlcv(data):
            """聚合数据为OHLCV格式"""
            return {
                "open": data["close"].iloc[0],
                "high": data["close"].max(),
                "low": data["close"].min(),
                "close": data["close"].iloc[-1],
                "volume": data["volume"].sum(),
                "count": len(data),
            }

        # 测试聚合
        ohlcv = aggregate_to_ohlcv(minute_data)

        assert ohlcv["open"] == 1750.00
        assert ohlcv["high"] == 1752.00
        assert ohlcv["low"] == 1749.50
        assert ohlcv["close"] == 1751.50
        assert ohlcv["volume"] == 5400
        assert ohlcv["count"] == 5

    def test_supertable_operations(self):
        """测试超级表操作"""

        class MockSupertable:
            def __init__(self, name):
                self.name = name
                self.subtables = {}

            def create_subtable(self, subtable_name, tags):
                """创建子表"""
                self.subtables[subtable_name] = tags
                return True

            def get_subtables(self, tag_filter=None):
                """获取子表列表"""
                if tag_filter:
                    result = {}
                    for table_name, table_tags in self.subtables.items():
                        match = True
                        for filter_key, filter_value in tag_filter.items():
                            if table_tags.get(filter_key) != filter_value:
                                match = False
                                break
                        if match:
                            result[table_name] = table_tags
                    return result
                return self.subtables

        # 测试超级表操作
        st = MockSupertable("market_data")

        # 创建子表
        st.create_subtable("stock_600519", {"symbol": "600519", "market": "SZ"})
        st.create_subtable("stock_000001", {"symbol": "000001", "market": "SZ"})

        assert len(st.subtables) == 2
        assert "stock_600519" in st.subtables
        assert st.subtables["stock_600519"]["symbol"] == "600519"

        # 测试子表查询
        sz_stocks = st.get_subtables({"market": "SZ"})
        assert len(sz_stocks) == 2

    def test_compression_ratio(self):
        """测试压缩比计算"""

        def calculate_compression_ratio(original_size, compressed_size):
            """计算压缩比"""
            if original_size == 0:
                return 0
            return (original_size - compressed_size) / original_size * 100

        # 测试压缩比计算
        original_size = 1000000  # 1MB
        compressed_size = 50000  # 50KB

        ratio = calculate_compression_ratio(original_size, compressed_size)
        assert ratio == 95.0  # 95%压缩率

        # 测试边界情况
        assert calculate_compression_ratio(0, 0) == 0
        assert calculate_compression_ratio(100, 100) == 0

    def test_high_frequency_write_simulation(self):
        """测试高频写入模拟"""

        class MockTDengineConnector:
            def __init__(self):
                self.insert_count = 0
                self.batch_size = 1000
                self.buffer = []

            def insert(self, data):
                """模拟数据插入"""
                self.buffer.extend(data)
                if len(self.buffer) >= self.batch_size:
                    self.flush()
                    return True
                return False

            def flush(self):
                """刷新缓冲区"""
                if self.buffer:
                    self.insert_count += len(self.buffer)
                    self.buffer = []
                return self.insert_count

        # 测试高频写入
        connector = MockTDengineConnector()

        # 模拟高频数据插入
        for i in range(2500):
            data = [{"symbol": "600519", "price": 1750.0 + i * 0.01}]
            connector.insert(data)

        assert connector.insert_count == 2000  # 两次批量刷新
        assert len(connector.buffer) == 500  # 剩余缓冲区

    def test_data_retention_policy(self):
        """测试数据保留策略"""

        def calculate_retention_duration(retention_policy):
            """计算保留时间（秒）"""
            unit_mapping = {
                "d": 86400,  # 天
                "h": 3600,  # 小时
                "m": 60,  # 分钟
                "s": 1,  # 秒
            }

            if retention_policy.endswith(("d", "h", "m", "s")):
                number = int(retention_policy[:-1])
                unit = retention_policy[-1]
                return number * unit_mapping[unit]
            raise ValueError("Invalid retention policy format")

        # 测试保留策略
        assert calculate_retention_duration("7d") == 7 * 86400
        assert calculate_retention_duration("24h") == 24 * 3600
        assert calculate_retention_duration("60m") == 60 * 60
        assert calculate_retention_duration("300s") == 300

        # 测试无效策略
        with pytest.raises(ValueError):
            calculate_retention_duration("invalid")

    def test_connection_pool_optimization(self):
        """测试连接池优化"""

        class MockTDengineConnectionPool:
            def __init__(self, max_connections=20):
                self.max_connections = max_connections
                self.active_connections = 0
                self.total_requests = 0
                self.pool_hits = 0

            def get_connection(self):
                """获取连接"""
                self.total_requests += 1
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    self.pool_hits += 1
                    return MagicMock()
                raise Exception("Connection pool exhausted")

            def return_connection(self, conn):
                """归还连接"""
                self.active_connections -= 1

            def get_pool_efficiency(self):
                """获取连接池效率"""
                return self.pool_hits / self.total_requests * 100 if self.total_requests > 0 else 0

        # 测试连接池效率
        pool = MockTDengineConnectionPool(max_connections=10)

        # 模拟连接请求
        connections = []
        for i in range(8):
            try:
                conn = pool.get_connection()
                connections.append(conn)
            except Exception:
                break

        efficiency = pool.get_pool_efficiency()
        assert efficiency == 100.0  # 所有请求都成功
        assert pool.active_connections == 8

        # 归还连接
        for conn in connections:
            pool.return_connection(conn)

        assert pool.active_connections == 0

    def test_real_time_query_optimization(self):
        """测试实时查询优化"""

        def optimize_realtime_query(query, time_window=3600):
            """优化实时查询"""
            # 添加时间窗口限制
            if "WHERE" in query:
                optimized = query + f" AND ts >= NOW() - {time_window}s"
            else:
                optimized = query + f" WHERE ts >= NOW() - {time_window}s"

            # 添加LIMIT限制
            if "LIMIT" not in optimized.upper():
                optimized += " LIMIT 10000"

            return optimized

        # 测试查询优化
        original_query = "SELECT * FROM tick_data WHERE symbol = '600519'"
        optimized = optimize_realtime_query(original_query, time_window=1800)

        assert "NOW() - 1800s" in optimized
        assert "LIMIT 10000" in optimized
        assert "symbol = '600519'" in optimized

        # 测试已有WHERE子句
        query_with_where = "SELECT * FROM minute_kline WHERE price > 1000"
        optimized2 = optimize_realtime_query(query_with_where)
        assert "WHERE" in optimized2 and "AND" in optimized2  # 应该包含WHERE和AND


class TestTDengineDataAccessIntegration:
    """TDengine数据访问集成测试"""

    def test_end_to_end_market_data_workflow(self):
        """测试端到端市场数据工作流程"""
        # Mock TDengine连接
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # 模拟完整的市场数据处理流程
        def save_tick_data(conn, symbol, tick_data):
            """保存tick数据"""
            cursor = conn.cursor()
            # 模拟批量插入
            insert_sql = f"INSERT INTO tick_data USING market_data TAGS('{symbol}') VALUES "
            values = []
            for _, row in tick_data.iterrows():
                values.append(f"('{row['ts']}', {row['price']}, {row['volume']})")

            cursor.execute(insert_sql + ",".join(values))
            conn.commit()

        def query_latest_data(conn, symbol, limit=100):
            """查询最新数据"""
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT ts, price, volume
                FROM tick_data
                WHERE symbol = '{symbol}'
                ORDER BY ts DESC
                LIMIT {limit}
            """
            )
            return cursor.fetchall()

        # 测试数据保存和查询
        import pandas as pd

        test_data = pd.DataFrame(
            {
                "ts": [datetime.now() + timedelta(seconds=i) for i in range(5)],
                "price": [1750.00 + i * 0.01 for i in range(5)],
                "volume": [100 + i * 10 for i in range(5)],
            }
        )

        mock_conn.cursor.return_value = mock_cursor
        save_tick_data(mock_conn, "600519", test_data)

        # 验证SQL执行
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

        # 测试查询
        mock_cursor.fetchall.return_value = [
            (datetime.now(), 1750.04, 140),
            (datetime.now(), 1750.03, 130),
            (datetime.now(), 1750.02, 120),
            (datetime.now(), 1750.01, 110),
            (datetime.now(), 1750.00, 100),
        ]

        results = query_latest_data(mock_conn, "600519", 5)
        assert len(results) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
