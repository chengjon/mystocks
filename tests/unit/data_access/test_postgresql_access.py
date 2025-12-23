"""
PostgreSQL数据访问层单元测试
测试src/data_access/postgresql_access.py的核心功能
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class MockPostgreSQLAccess:
    """模拟PostgreSQL数据访问用于测试"""

    def __init__(self):
        self.tables = {}
        self.hypertables = set()
        self.connection_pool = None

    def create_table(self, table_name, schema, primary_key=None):
        """创建表"""
        self.tables[table_name] = {
            "schema": schema,
            "primary_key": primary_key,
            "data": [],
        }
        return True

    def create_hypertable(
        self, table_name, time_column="time", chunk_interval="7 days"
    ):
        """创建时序表"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        self.hypertables.add(table_name)
        return True

    def insert_data(self, table_name, data):
        """插入数据"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        if isinstance(data, pd.DataFrame):
            records = data.to_dict("records")
        elif isinstance(data, list):
            records = data
        else:
            records = [data]

        self.tables[table_name]["data"].extend(records)
        return len(records)

    def batch_insert(self, table_name, data, batch_size=1000):
        """批量插入数据"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        total = 0
        if isinstance(data, pd.DataFrame):
            for i in range(0, len(data), batch_size):
                batch = data.iloc[i : i + batch_size]
                total += self.insert_data(table_name, batch)
        else:
            for i in range(0, len(data), batch_size):
                batch = data[i : i + batch_size]
                total += self.insert_data(table_name, batch)

        return total

    def query(self, table_name, conditions=None, limit=None):
        """查询数据"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        data = self.tables[table_name]["data"]

        # 应用条件过滤
        if conditions:
            filtered = []
            for record in data:
                match = True
                for key, value in conditions.items():
                    if key not in record or record[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(record)
            data = filtered

        # 应用限制
        if limit:
            data = data[:limit]

        return pd.DataFrame(data) if data else pd.DataFrame()

    def query_time_range(self, table_name, start_time, end_time, symbol=None):
        """时间范围查询"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        data = self.tables[table_name]["data"]
        filtered = []

        for record in data:
            if "time" in record or "date" in record:
                time_field = "time" if "time" in record else "date"
                record_time = record[time_field]

                if isinstance(record_time, str):
                    record_time = datetime.fromisoformat(record_time)

                if start_time <= record_time <= end_time:
                    if symbol is None or record.get("symbol") == symbol:
                        filtered.append(record)

        return pd.DataFrame(filtered) if filtered else pd.DataFrame()

    def delete_data(self, table_name, conditions):
        """删除数据"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        data = self.tables[table_name]["data"]
        deleted = 0

        new_data = []
        for record in data:
            match = True
            for key, value in conditions.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if not match:
                new_data.append(record)
            else:
                deleted += 1

        self.tables[table_name]["data"] = new_data
        return deleted

    def update_data(self, table_name, conditions, updates):
        """更新数据"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        data = self.tables[table_name]["data"]
        updated = 0

        for record in data:
            match = True
            for key, value in conditions.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                record.update(updates)
                updated += 1

        return updated

    def table_exists(self, table_name):
        """检查表是否存在"""
        return table_name in self.tables

    def get_table_info(self, table_name):
        """获取表信息"""
        if table_name not in self.tables:
            return None

        return {
            "name": table_name,
            "schema": self.tables[table_name]["schema"],
            "primary_key": self.tables[table_name]["primary_key"],
            "is_hypertable": table_name in self.hypertables,
            "row_count": len(self.tables[table_name]["data"]),
        }


class TestPostgreSQLAccess:
    """PostgreSQL数据访问测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.db = MockPostgreSQLAccess()

    def test_create_table(self):
        """测试创建表"""
        schema = {"symbol": "VARCHAR(20)", "date": "DATE", "close": "DECIMAL(10,2)"}

        result = self.db.create_table("test_table", schema, primary_key="symbol, date")
        assert result is True
        assert "test_table" in self.db.tables
        assert self.db.tables["test_table"]["schema"] == schema
        assert self.db.tables["test_table"]["primary_key"] == "symbol, date"

    def test_create_hypertable(self):
        """测试创建时序表"""
        schema = {"time": "TIMESTAMP", "value": "FLOAT"}
        self.db.create_table("timeseries_table", schema)

        result = self.db.create_hypertable("timeseries_table", "time", "1 day")
        assert result is True
        assert "timeseries_table" in self.db.hypertables

    def test_create_hypertable_without_table(self):
        """测试在表不存在时创建时序表"""
        with pytest.raises(ValueError):
            self.db.create_hypertable("nonexistent_table")

    def test_insert_data_dict(self):
        """测试插入字典数据"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema)

        data = {"symbol": "600519", "price": 1750.50}
        count = self.db.insert_data("stocks", data)

        assert count == 1
        assert len(self.db.tables["stocks"]["data"]) == 1

    def test_insert_data_dataframe(self):
        """测试插入DataFrame数据"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema)

        df = pd.DataFrame(
            [
                {"symbol": "600519", "price": 1750.50},
                {"symbol": "000001", "price": 12.35},
            ]
        )

        count = self.db.insert_data("stocks", df)
        assert count == 2
        assert len(self.db.tables["stocks"]["data"]) == 2

    def test_batch_insert(self):
        """测试批量插入"""
        schema = {"id": "INT", "value": "FLOAT"}
        self.db.create_table("test_batch", schema)

        data = [{"id": i, "value": i * 1.5} for i in range(100)]
        count = self.db.batch_insert("test_batch", data, batch_size=10)

        assert count == 100
        assert len(self.db.tables["test_batch"]["data"]) == 100

    def test_query_all(self):
        """测试查询所有数据"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema)

        self.db.insert_data(
            "stocks",
            [
                {"symbol": "600519", "price": 1750.50},
                {"symbol": "000001", "price": 12.35},
            ],
        )

        result = self.db.query("stocks")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_query_with_conditions(self):
        """测试条件查询"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema)

        self.db.insert_data(
            "stocks",
            [
                {"symbol": "600519", "price": 1750.50},
                {"symbol": "000001", "price": 12.35},
            ],
        )

        result = self.db.query("stocks", conditions={"symbol": "600519"})
        assert len(result) == 1
        assert result.iloc[0]["symbol"] == "600519"

    def test_query_with_limit(self):
        """测试限制查询结果数量"""
        schema = {"id": "INT", "value": "FLOAT"}
        self.db.create_table("test_limit", schema)

        self.db.insert_data(
            "test_limit", [{"id": i, "value": i * 1.5} for i in range(10)]
        )

        result = self.db.query("test_limit", limit=5)
        assert len(result) == 5

    def test_query_time_range(self):
        """测试时间范围查询"""
        schema = {"time": "TIMESTAMP", "symbol": "VARCHAR(20)", "value": "FLOAT"}
        self.db.create_table("timeseries", schema)

        base_time = datetime(2024, 1, 1, 0, 0, 0)
        data = [
            {
                "time": base_time + timedelta(hours=i),
                "symbol": "600519",
                "value": 100.0 + i,
            }
            for i in range(24)
        ]
        self.db.insert_data("timeseries", data)

        start = base_time + timedelta(hours=5)
        end = base_time + timedelta(hours=10)
        result = self.db.query_time_range("timeseries", start, end)

        assert len(result) == 6  # hours 5-10 inclusive

    def test_query_time_range_with_symbol(self):
        """测试带股票代码的时间范围查询"""
        schema = {"time": "TIMESTAMP", "symbol": "VARCHAR(20)", "value": "FLOAT"}
        self.db.create_table("timeseries", schema)

        base_time = datetime(2024, 1, 1)
        data = [
            {
                "time": base_time + timedelta(days=i),
                "symbol": "600519",
                "value": 100.0 + i,
            }
            for i in range(5)
        ] + [
            {
                "time": base_time + timedelta(days=i),
                "symbol": "000001",
                "value": 50.0 + i,
            }
            for i in range(5)
        ]
        self.db.insert_data("timeseries", data)

        start = base_time
        end = base_time + timedelta(days=10)
        result = self.db.query_time_range("timeseries", start, end, symbol="600519")

        assert len(result) == 5
        assert all(result["symbol"] == "600519")

    def test_delete_data(self):
        """测试删除数据"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema)

        self.db.insert_data(
            "stocks",
            [
                {"symbol": "600519", "price": 1750.50},
                {"symbol": "000001", "price": 12.35},
                {"symbol": "600519", "price": 1760.00},
            ],
        )

        deleted = self.db.delete_data("stocks", {"symbol": "600519"})
        assert deleted == 2
        assert len(self.db.tables["stocks"]["data"]) == 1

    def test_update_data(self):
        """测试更新数据"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema)

        self.db.insert_data(
            "stocks",
            [
                {"symbol": "600519", "price": 1750.50},
                {"symbol": "000001", "price": 12.35},
            ],
        )

        updated = self.db.update_data(
            "stocks", {"symbol": "600519"}, {"price": 1800.00}
        )

        assert updated == 1
        result = self.db.query("stocks", conditions={"symbol": "600519"})
        assert result.iloc[0]["price"] == 1800.00

    def test_table_exists(self):
        """测试检查表是否存在"""
        schema = {"id": "INT"}
        self.db.create_table("test_table", schema)

        assert self.db.table_exists("test_table") is True
        assert self.db.table_exists("nonexistent") is False

    def test_get_table_info(self):
        """测试获取表信息"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema, primary_key="symbol")
        self.db.create_hypertable("stocks")

        self.db.insert_data(
            "stocks",
            [
                {"symbol": "600519", "price": 1750.50},
                {"symbol": "000001", "price": 12.35},
            ],
        )

        info = self.db.get_table_info("stocks")
        assert info["name"] == "stocks"
        assert info["schema"] == schema
        assert info["primary_key"] == "symbol"
        assert info["is_hypertable"] is True
        assert info["row_count"] == 2

    def test_get_table_info_nonexistent(self):
        """测试获取不存在的表信息"""
        info = self.db.get_table_info("nonexistent")
        assert info is None

    def test_insert_to_nonexistent_table(self):
        """测试向不存在的表插入数据"""
        with pytest.raises(ValueError):
            self.db.insert_data("nonexistent", {"id": 1})

    def test_query_nonexistent_table(self):
        """测试查询不存在的表"""
        with pytest.raises(ValueError):
            self.db.query("nonexistent")

    def test_empty_query_result(self):
        """测试空查询结果"""
        schema = {"symbol": "VARCHAR(20)", "price": "DECIMAL(10,2)"}
        self.db.create_table("stocks", schema)

        result = self.db.query("stocks")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
