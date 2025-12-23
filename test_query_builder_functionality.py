#!/usr/bin/env python3
"""
查询构建器功能验证测试
"""

import sys
from pathlib import Path

# 添加项目根路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# 模拟连接提供者
class MockConnectionProvider:
    def _get_connection(self):
        return None

    def _return_connection(self, conn):
        pass


def test_query_builder():
    """测试查询构建器功能"""
    print("🧪 测试查询构建器功能...")

    try:
        # 导入查询构建器
        from src.data_sources.real.query_builder import QueryBuilder

        print("✅ 查询构建器导入成功")
    except ImportError as e:
        print(f"❌ 查询构建器导入失败: {e}")
        return False

    # 创建实例
    connection_provider = MockConnectionProvider()
    query_builder = QueryBuilder(connection_provider)
    print("✅ 查询构建器实例创建成功")

    # 测试SELECT查询
    try:
        sql, params = (
            query_builder.select("id", "name", "email")
            .from_table("users")
            .where("age > %s", 18)
            .where("status = %s", "active")
            .order_by("created_at", "DESC")
            .limit(10)
            .build()
        )

        expected_sql = "SELECT id, name, email FROM users WHERE age > %s AND status = %s ORDER BY created_at DESC LIMIT 10"

        if sql == expected_sql and params == [18, "active"]:
            print("✅ SELECT查询构建测试通过")
        else:
            print("❌ SELECT查询构建测试失败")
            print(f"   期望SQL: {expected_sql}")
            print(f"   实际SQL: {sql}")
            print("   期望参数: [18, 'active']")
            print(f"   实际参数: {params}")
            return False
    except Exception as e:
        print(f"❌ SELECT查询构建测试异常: {e}")
        return False

    # 重置构建器
    query_builder.reset()

    # 测试INSERT查询
    try:
        data = {"name": "John", "email": "john@example.com", "age": 30}
        sql, params = (
            query_builder.insert_into("users")
            .values(data)
            .returning("id", "created_at")
            .build()
        )

        expected_sql = "INSERT INTO users (name, email, age) VALUES (%s, %s, %s) RETURNING id, created_at"

        if sql == expected_sql and params == ["John", "john@example.com", 30]:
            print("✅ INSERT查询构建测试通过")
        else:
            print("❌ INSERT查询构建测试失败")
            print(f"   期望SQL: {expected_sql}")
            print(f"   实际SQL: {sql}")
            print("   期望参数: ['John', 'john@example.com', 30]")
            print(f"   实际参数: {params}")
            return False
    except Exception as e:
        print(f"❌ INSERT查询构建测试异常: {e}")
        return False

    # 重置构建器
    query_builder.reset()

    # 测试带JOIN的复杂查询
    try:
        sql, params = (
            query_builder.select("u.id", "u.name", "p.title")
            .from_table("users", "u")
            .left_join("posts", "u.id = p.user_id")
            .where("u.status = %s", "active")
            .where("p.published = %s", True)
            .order_by("u.created_at", "DESC")
            .limit(20)
            .build()
        )

        expected_sql = "SELECT u.id, u.name, p.title FROM users AS u LEFT JOIN posts ON u.id = p.user_id WHERE u.status = %s AND p.published = %s ORDER BY u.created_at DESC LIMIT 20"

        if sql == expected_sql and params == ["active", True]:
            print("✅ 复杂JOIN查询构建测试通过")
        else:
            print("❌ 复杂JOIN查询构建测试失败")
            print(f"   期望SQL: {expected_sql}")
            print(f"   实际SQL: {sql}")
            print("   期望参数: ['active', True]")
            print(f"   实际参数: {params}")
            return False
    except Exception as e:
        print(f"❌ 复杂JOIN查询构建测试异常: {e}")
        return False

    # 重置构建器
    query_builder.reset()

    # 测试WHERE IN和BETWEEN
    try:
        user_ids = [1, 2, 3, 4, 5]
        sql, params = (
            query_builder.select("*")
            .from_table("orders")
            .where_in("user_id", user_ids)
            .where_between("created_at", "2023-01-01", "2023-12-31")
            .build()
        )

        expected_params = user_ids + ["2023-01-01", "2023-12-31"]
        expected_sql_pattern = "SELECT * FROM orders WHERE user_id IN (%s,%s,%s,%s,%s) AND created_at BETWEEN %s AND %s"

        if expected_sql_pattern == sql and params == expected_params:
            print("✅ WHERE IN和BETWEEN查询构建测试通过")
        else:
            print("❌ WHERE IN和BETWEEN查询构建测试失败")
            print(f"   期望SQL: {expected_sql_pattern}")
            print(f"   实际SQL: {sql}")
            print(f"   期望参数: {expected_params}")
            print(f"   实际参数: {params}")
            return False
    except Exception as e:
        print(f"❌ WHERE IN和BETWEEN查询构建测试异常: {e}")
        return False

    # 测试UPDATE查询
    try:
        query_builder.reset()
        update_data = {"status": "inactive", "updated_at": "2023-12-01"}
        sql, params = (
            query_builder.update("users").set(update_data).where("id = %s", 123).build()
        )

        expected_sql = "UPDATE users SET status = %s, updated_at = %s WHERE id = %s"
        expected_params = ["inactive", "2023-12-01", 123]

        if sql == expected_sql and params == expected_params:
            print("✅ UPDATE查询构建测试通过")
        else:
            print("❌ UPDATE查询构建测试失败")
            print(f"   期望SQL: {expected_sql}")
            print(f"   实际SQL: {sql}")
            print(f"   期望参数: {expected_params}")
            print(f"   实际参数: {params}")
            return False
    except Exception as e:
        print(f"❌ UPDATE查询构建测试异常: {e}")
        return False

    # 测试DELETE查询
    try:
        query_builder.reset()
        sql, params = (
            query_builder.delete_from("temp_data")
            .where("created_at < %s", "2023-01-01")
            .build()
        )

        expected_sql = "DELETE FROM temp_data WHERE created_at < %s"
        expected_params = ["2023-01-01"]

        if sql == expected_sql and params == expected_params:
            print("✅ DELETE查询构建测试通过")
        else:
            print("❌ DELETE查询构建测试失败")
            print(f"   期望SQL: {expected_sql}")
            print(f"   实际SQL: {sql}")
            print(f"   期望参数: {expected_params}")
            print(f"   实际参数: {params}")
            return False
    except Exception as e:
        print(f"❌ DELETE查询构建测试异常: {e}")
        return False

    print("\n🎉 所有查询构建器功能测试通过！")
    return True


def test_watchlist_pattern():
    """测试自选股查询模式"""
    print("\n🧪 测试自选股查询模式...")

    try:
        from src.data_sources.real.query_builder import QueryBuilder

        connection_provider = MockConnectionProvider()
        query_builder = QueryBuilder(connection_provider)

        # 模拟原始的watchlist查询
        user_id = 123
        list_type = "favorite"

        sql, params = (
            query_builder.select(
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

        # 验证SQL结构
        expected_keywords = [
            "SELECT",
            "FROM watchlist AS w",
            "LEFT JOIN",
            "WHERE",
            "ORDER BY",
        ]
        for keyword in expected_keywords:
            if keyword not in sql:
                print(f"❌ 缺少关键字: {keyword}")
                return False

        # 验证参数
        expected_params = [user_id, list_type]
        if params != expected_params:
            print(f"❌ 参数不匹配: 期望 {expected_params}, 实际 {params}")
            return False

        print("✅ 自选股查询模式测试通过")
        print(f"   SQL: {sql}")
        print(f"   参数: {params}")
        return True

    except Exception as e:
        print(f"❌ 自选股查询模式测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 查询构建器功能验证测试")
    print("=" * 60)

    # 基础功能测试
    basic_test_passed = test_query_builder()

    # 模式测试
    pattern_test_passed = test_watchlist_pattern()

    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   基础功能测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    print(f"   自选股模式测试: {'✅ 通过' if pattern_test_passed else '❌ 失败'}")

    if basic_test_passed and pattern_test_passed:
        print("\n🎉 所有测试通过！查询构建器功能正常。")
        print("\n📋 下一步建议:")
        print("   1. 开始重构 postgresql_relational.py 中的查询")
        print("   2. 使用查询构建器替换内嵌SQL")
        print("   3. 验证重构后的功能一致性")
        return 0
    else:
        print("\n❌ 部分测试失败，需要修复查询构建器。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
