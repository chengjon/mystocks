"""
查询构建器测试用例
遵循TDD原则：先写失败测试，再实现功能
"""

import pytest
import sys
import os
from unittest.mock import Mock

# 添加项目根路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.insert(0, project_root)

try:
    from src.data_sources.real.query_builder import QueryBuilder, QueryExecutor

    QUERY_BUILDER_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    QUERY_BUILDER_AVAILABLE = False


class MockConnectionProvider:
    """模拟数据库连接提供者"""

    def __init__(self):
        self.mock_conn = Mock()
        self.mock_cursor = Mock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def _get_connection(self):
        return self.mock_conn

    def _return_connection(self, conn):
        pass


@pytest.mark.skipif(not QUERY_BUILDER_AVAILABLE, reason="Query builder not available")
class TestQueryBuilder:
    """查询构建器测试"""

    def setup_method(self):
        """测试设置"""
        self.connection_provider = MockConnectionProvider()
        self.query_builder = QueryBuilder(self.connection_provider)

    def test_init_query_builder(self):
        """测试查询构建器初始化"""
        assert self.query_builder is not None
        assert self.query_builder.connection_provider == self.connection_provider
        assert self.query_builder._query_type is None

    def test_select_basic(self):
        """测试基础SELECT查询构建"""
        sql, params = (
            self.query_builder.select("id", "name").from_table("users").build()
        )

        expected_sql = "SELECT id, name FROM users"
        assert sql == expected_sql
        assert params == []

    def test_select_with_where(self):
        """测试带WHERE条件的SELECT查询"""
        sql, params = (
            self.query_builder.select("id", "name")
            .from_table("users")
            .where("age > %s", 18)
            .build()
        )

        expected_sql = "SELECT id, name FROM users WHERE age > %s"
        assert sql == expected_sql
        assert params == [18]

    def test_select_with_multiple_conditions(self):
        """测试多条件SELECT查询"""
        sql, params = (
            self.query_builder.select("*")
            .from_table("users")
            .where("age > %s", 18)
            .where("status = %s", "active")
            .build()
        )

        expected_sql = "SELECT * FROM users WHERE age > %s AND status = %s"
        assert sql == expected_sql
        assert params == [18, "active"]

    def test_select_with_join(self):
        """测试带JOIN的SELECT查询"""
        sql, params = (
            self.query_builder.select("u.id", "u.name", "p.title")
            .from_table("users", "u")
            .join("posts", "u.id = p.user_id")
            .build()
        )

        expected_sql = "SELECT u.id, u.name, p.title FROM users AS u INNER JOIN posts ON u.id = p.user_id"
        assert sql == expected_sql
        assert params == []

    def test_select_with_left_join(self):
        """测试LEFT JOIN查询"""
        sql, params = (
            self.query_builder.select("u.id", "u.name", "p.title")
            .from_table("users", "u")
            .left_join("posts", "u.id = p.user_id")
            .build()
        )

        expected_sql = "SELECT u.id, u.name, p.title FROM users AS u LEFT JOIN posts ON u.id = p.user_id"
        assert sql == expected_sql

    def test_select_with_order_by_limit_offset(self):
        """测试排序、限制、偏移"""
        sql, params = (
            self.query_builder.select("*")
            .from_table("users")
            .order_by("created_at", "DESC")
            .limit(10)
            .offset(20)
            .build()
        )

        expected_sql = "SELECT * FROM users ORDER BY created_at DESC LIMIT 10 OFFSET 20"
        assert sql == expected_sql

    def test_select_with_where_in(self):
        """测试WHERE IN条件"""
        ids = [1, 2, 3, 4, 5]
        sql, params = (
            self.query_builder.select("*")
            .from_table("users")
            .where_in("id", ids)
            .build()
        )

        expected_sql = "SELECT * FROM users WHERE id IN (%s,%s,%s,%s,%s)"
        assert sql == expected_sql
        assert params == ids

    def test_select_with_where_between(self):
        """测试WHERE BETWEEN条件"""
        sql, params = (
            self.query_builder.select("*")
            .from_table("orders")
            .where_between("created_at", "2023-01-01", "2023-12-31")
            .build()
        )

        expected_sql = "SELECT * FROM orders WHERE created_at BETWEEN %s AND %s"
        assert sql == expected_sql
        assert params == ["2023-01-01", "2023-12-31"]

    def test_insert_basic(self):
        """测试基础INSERT查询"""
        data = {"name": "John", "email": "john@example.com", "age": 30}
        sql, params = self.query_builder.insert_into("users").values(data).build()

        expected_sql = "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)"
        assert sql == expected_sql
        assert params == ["John", "john@example.com", 30]

    def test_insert_with_returning(self):
        """测试带RETURNING的INSERT查询"""
        data = {"name": "John", "email": "john@example.com"}
        sql, params = (
            self.query_builder.insert_into("users")
            .values(data)
            .returning("id", "created_at")
            .build()
        )

        expected_sql = (
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, created_at"
        )
        assert sql == expected_sql
        assert params == ["John", "john@example.com"]

    def test_insert_with_conflict_do_nothing(self):
        """测试冲突时不做操作的INSERT查询"""
        data = {"name": "John", "email": "john@example.com"}
        sql, params = (
            self.query_builder.insert_into("users")
            .values(data)
            .on_conflict_do_nothing()
            .build()
        )

        expected_sql = (
            "INSERT INTO users (name, email) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        )
        assert sql == expected_sql

    def test_insert_with_conflict_update(self):
        """测试冲突时更新的INSERT查询"""
        data = {"name": "John", "email": "john@example.com"}
        update_data = {"updated_at": "2023-12-01"}
        sql, params = (
            self.query_builder.insert_into("users")
            .values(data)
            .on_conflict_update(update_data)
            .build()
        )

        expected_sql = "INSERT INTO users (name, email) VALUES (%s, %s) ON CONFLICT DO UPDATE SET updated_at = %s"
        assert sql == expected_sql
        assert params == ["John", "john@example.com", "2023-12-01"]

    def test_update_basic(self):
        """测试基础UPDATE查询"""
        update_data = {"name": "Jane", "age": 25}
        sql, params = (
            self.query_builder.update("users")
            .set(update_data)
            .where("id = %s", 1)
            .build()
        )

        expected_sql = "UPDATE users SET name = %s, age = %s WHERE id = %s"
        assert sql == expected_sql
        assert params == ["Jane", 25, 1]

    def test_delete_basic(self):
        """测试基础DELETE查询"""
        sql, params = (
            self.query_builder.delete_from("users").where("id = %s", 1).build()
        )

        expected_sql = "DELETE FROM users WHERE id = %s"
        assert sql == expected_sql
        assert params == [1]

    def test_group_by_and_having(self):
        """测试GROUP BY和HAVING"""
        sql, params = (
            self.query_builder.select("category", "COUNT(*) as count")
            .from_table("products")
            .where("price > %s", 100)
            .group_by("category")
            .having("COUNT(*) > %s", 5)
            .build()
        )

        expected_sql = "SELECT category, COUNT(*) as count FROM products WHERE price > %s GROUP BY category HAVING COUNT(*) > %s"
        assert sql == expected_sql
        assert params == [100, 5]

    def test_reset(self):
        """测试重置查询构建器"""
        # 构建一个查询
        self.query_builder.select("*").from_table("users").where("id = %s", 1)

        # 重置
        self.query_builder.reset()

        # 验证状态已重置
        assert self.query_builder._query_type is None
        assert self.query_builder._select_fields == []
        assert self.query_builder._table_name is None
        assert self.query_builder._where_conditions == []

    def test_chained_building(self):
        """测试链式构建不会影响原始查询"""
        # 构建第一个查询
        self.query_builder.select("*").from_table("users").where("id = %s", 1)
        sql1, params1 = self.query_builder.build()

        # 重置并构建第二个查询
        self.query_builder.reset()
        sql2, params2 = (
            self.query_builder.select("name")
            .from_table("users")
            .where("status = %s", "active")
            .build()
        )

        # 验证两个查询不同
        assert sql1 != sql2
        assert "WHERE id = %s" in sql1
        assert "WHERE status = %s" in sql2

    def test_error_handling(self):
        """测试错误处理"""
        # 尝试构建没有指定表的查询
        with pytest.raises(ValueError, match="表名未指定"):
            self.query_builder.select("*").build()

        # 尝试构建INSERT查询时没有指定数据
        with pytest.raises(ValueError, match="插入数据未指定"):
            self.query_builder.insert_into("users").build()

        # 尝试构建UPDATE查询时没有指定数据
        with pytest.raises(ValueError, match="更新数据未指定"):
            self.query_builder.update("users").build()


@pytest.mark.skipif(not QUERY_BUILDER_AVAILABLE, reason="Query builder not available")
class TestQueryExecution:
    """查询执行器测试"""

    def setup_method(self):
        """测试设置"""
        self.connection_provider = MockConnectionProvider()
        self.query_executor = QueryExecutor(self.connection_provider)

    def test_create_query(self):
        """测试创建新查询"""
        query = self.query_executor.create_query()
        assert isinstance(query, QueryBuilder)
        assert query.connection_provider == self.connection_provider

    def test_reset_functionality(self):
        """测试查询构建器重置功能"""
        query = self.query_executor.create_query()

        # 构建查询
        query.select("*").from_table("users").where("id = %s", 1)

        # 重置
        query.reset()

        # 验证重置状态
        assert query._query_type is None
        assert query._select_fields == []


@pytest.mark.skipif(not QUERY_BUILDER_AVAILABLE, reason="Query builder not available")
class TestQueryBuilderIntegration:
    """查询构建器集成测试"""

    def setup_method(self):
        """测试设置"""
        self.connection_provider = MockConnectionProvider()
        self.query_builder = QueryBuilder(self.connection_provider)

    def test_watchlist_query_pattern(self):
        """测试自选股查询模式"""
        # 模拟原始的watchlist查询
        user_id = 123
        list_type = "favorite"

        sql, params = (
            self.query_builder.select(
                "w.id",
                "w.user_id",
                "w.symbol",
                "w.list_type",
                "w.note",
                "w.added_at",
                "s.name",
                "s.industry",
                "s.market",
                "s.pinyin",
            )
            .from_table("watchlist", "w")
            .left_join("stock_basic_info s", "w.symbol = s.symbol")
            .where("w.user_id = %s", user_id)
            .where("w.list_type = %s", list_type)
            .order_by("w.added_at", "DESC")
            .build()
        )

        expected_keywords = [
            "SELECT",
            "FROM watchlist AS w",
            "LEFT JOIN",
            "WHERE",
            "ORDER BY",
        ]
        for keyword in expected_keywords:
            assert keyword in sql

        assert params == [user_id, list_type]

    def test_strategy_config_query_pattern(self):
        """测试策略配置查询模式"""
        user_id = 456

        sql, params = (
            self.query_builder.select("*")
            .from_table("strategy_configs")
            .where("user_id = %s", user_id)
            .where("status != %s", "deleted")
            .order_by("created_at", "DESC")
            .build()
        )

        assert "WHERE user_id = %s AND status != %s" in sql
        assert params == [user_id, "deleted"]

    def test_risk_alerts_query_pattern(self):
        """测试风险预警查询模式"""
        user_id = 789
        alert_type = "price_change"

        sql, params = (
            self.query_builder.select("*")
            .from_table("risk_alerts")
            .where("user_id = %s", user_id)
            .where("alert_type = %s", alert_type)
            .where("status = %s", "pending")
            .where("created_at > %s", "2023-01-01")
            .order_by("created_at", "DESC")
            .limit(50)
            .build()
        )

        assert (
            "WHERE user_id = %s AND alert_type = %s AND status = %s AND created_at > %s"
            in sql
        )
        assert params == [user_id, alert_type, "pending", "2023-01-01"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
