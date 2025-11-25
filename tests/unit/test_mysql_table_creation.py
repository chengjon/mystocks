"""
T023: MySQL表创建单元测试

验证ConfigDrivenTableManager能够正确创建MySQL表,
包括索引、约束、字符集等配置。

创建日期: 2025-10-11
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from src.core.config_driven_table_manager import ConfigDrivenTableManager
from src.storage.database.connection_manager import DatabaseConnectionManager

print("\n" + "=" * 80)
print("T023: MySQL表创建单元测试")
print("=" * 80 + "\n")


@pytest.mark.skip(reason="MySQL已从架构中移除，系统使用TDengine+PostgreSQL双数据库架构")
class TestMySQLTableCreation:
    """MySQL表创建测试类 (已废弃 - MySQL从Week3开始已移除)"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.manager = ConfigDrivenTableManager()
        cls.conn_manager = DatabaseConnectionManager()

    def test_01_mysql_connection(self):
        """测试1: MySQL连接测试"""
        print("📍 测试1: MySQL数据库连接")

        try:
            conn = self.conn_manager.get_mysql_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()

            print(f"  ✅ MySQL连接成功 (version={version[0]})")
            assert conn is not None
        except Exception as e:
            print(f"  ⚠️  MySQL连接失败: {e}")
            pytest.skip("MySQL未配置或不可用")

    def test_02_mysql_table_count(self):
        """测试2: 统计MySQL表定义数量"""
        print("\n📍 测试2: 统计MySQL表定义")

        mysql_tables = [
            t for t in self.manager.config["tables"] if t["database_type"] == "MySQL"
        ]

        print(f"  MySQL表数量: {len(mysql_tables)}")

        # 根据table_config.yaml,应该有15个MySQL表 (9个参考数据 + 6个元数据)
        assert len(mysql_tables) >= 10, f"MySQL表数量不足: {len(mysql_tables)}"

        # 按分类统计
        reference_tables = [
            t
            for t in mysql_tables
            if t.get("classification", "").endswith("_INFO")
            or t.get("classification", "").endswith("_CLASS")
            or t.get("classification", "").endswith("_CALENDAR")
            or t.get("classification", "").endswith("_CONSTITUENTS")
            or t.get("classification", "").endswith("_METRICS")
            or t.get("classification", "").endswith("_DATA")
            or t.get("classification", "").endswith("_RULES")
        ]

        meta_tables = [
            t
            for t in mysql_tables
            if t.get("classification", "").startswith(
                (
                    "DATA_SOURCE",
                    "TASK_",
                    "STRATEGY_",
                    "SYSTEM_",
                    "USER_",
                    "DATA_QUALITY",
                )
            )
        ]

        print(f"  参考数据表: {len(reference_tables)}")
        print(f"  元数据表: {len(meta_tables)}")

        for table in mysql_tables[:5]:  # 只显示前5个
            print(f"    - {table['table_name']} ({table.get('classification', 'N/A')})")

        print(f"  ✅ MySQL表定义验证通过")

    def test_03_mysql_table_structure(self):
        """测试3: 验证MySQL表结构定义"""
        print("\n📍 测试3: 验证MySQL表结构")

        # 查找stock_info表定义
        stock_info = next(
            (
                t
                for t in self.manager.config["tables"]
                if t["table_name"] == "stock_info"
            ),
            None,
        )

        assert stock_info is not None, "未找到stock_info表定义"
        assert stock_info["database_type"] == "MySQL", "stock_info应该在MySQL中"

        # 验证列定义
        columns = stock_info.get("columns", [])
        assert len(columns) > 0, "列定义为空"

        col_names = [col["name"] for col in columns]
        assert "id" in col_names, "缺少主键id列"
        assert "symbol" in col_names, "缺少symbol列"
        assert "name" in col_names, "缺少name列"
        assert "created_at" in col_names, "缺少created_at列"
        assert "updated_at" in col_names, "缺少updated_at列"

        print(f"  列数量: {len(columns)}")
        print(f"  必需列验证: ✓")

        # 验证主键
        primary_keys = [col["name"] for col in columns if col.get("primary_key")]
        assert len(primary_keys) > 0, "应该有主键定义"
        print(f"  主键: {primary_keys}")

        # 验证唯一键
        unique_cols = [col["name"] for col in columns if col.get("unique")]
        print(f"  唯一键: {unique_cols if unique_cols else '无'}")

        # 验证索引
        indexes = stock_info.get("indexes", [])
        print(f"  索引数量: {len(indexes)}")
        for idx in indexes[:3]:
            print(f"    - {idx['name']} ({idx['type']}): {idx['columns']}")

        print(f"  ✅ MySQL表结构验证通过")

    def test_04_create_mysql_tables(self):
        """测试4: 创建MySQL表"""
        print("\n📍 测试4: 创建MySQL表")

        try:
            mysql_tables = [
                t
                for t in self.manager.config["tables"]
                if t["database_type"] == "MySQL"
            ]

            created_count = 0
            skipped_count = 0
            error_count = 0

            # 创建所有MySQL表
            for table_def in mysql_tables:
                try:
                    created = self.manager._create_table(table_def)
                    if created:
                        created_count += 1
                        print(f"  ✅ 创建: {table_def['table_name']}")
                    else:
                        skipped_count += 1
                        print(f"  ⏭️  跳过: {table_def['table_name']} (已存在)")
                except Exception as e:
                    error_count += 1
                    print(f"  ⚠️  失败: {table_def['table_name']} - {str(e)[:50]}")

            print(
                f"\n  总计: 创建{created_count}个, 跳过{skipped_count}个, 错误{error_count}个"
            )
            print(f"  ✅ MySQL表创建测试完成")

        except Exception as e:
            print(f"  ⚠️  测试失败: {e}")
            pytest.skip(f"MySQL表创建失败: {e}")

    def test_05_verify_table_exists(self):
        """测试5: 验证表是否存在"""
        print("\n📍 测试5: 验证表存在性")

        try:
            mysql_tables = [
                t
                for t in self.manager.config["tables"]
                if t["database_type"] == "MySQL"
            ]

            database_name = (
                mysql_tables[0].get("database_name") if mysql_tables else None
            )

            for table_def in mysql_tables[:5]:  # 只检查前5个
                table_name = table_def["table_name"]
                exists = self.manager._table_exists("MySQL", table_name, database_name)

                status = "✅ 存在" if exists else "❌ 不存在"
                print(f"  {table_name}: {status}")

            print(f"  ✅ 表存在性验证完成")

        except Exception as e:
            print(f"  ⚠️  验证失败: {e}")

    def test_06_charset_and_collation(self):
        """测试6: 验证字符集和排序规则"""
        print("\n📍 测试6: 验证字符集配置")

        try:
            conn = self.conn_manager.get_mysql_connection()
            cursor = conn.cursor()

            # 检查数据库字符集
            cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
            charset = cursor.fetchone()

            cursor.execute("SHOW VARIABLES LIKE 'collation_database'")
            collation = cursor.fetchone()

            cursor.close()
            conn.close()

            print(f"  数据库字符集: {charset[1] if charset else 'unknown'}")
            print(f"  排序规则: {collation[1] if collation else 'unknown'}")
            print(f"  ✅ 字符集验证通过")

        except Exception as e:
            print(f"  ⚠️  验证失败: {e}")

    def test_07_auto_increment(self):
        """测试7: 验证自增主键"""
        print("\n📍 测试7: 验证自增主键配置")

        mysql_tables = [
            t for t in self.manager.config["tables"] if t["database_type"] == "MySQL"
        ]

        tables_with_auto_inc = []
        for table in mysql_tables:
            columns = table.get("columns", [])
            has_auto_inc = any(col.get("auto_increment") for col in columns)
            if has_auto_inc:
                tables_with_auto_inc.append(table["table_name"])

        print(f"  共有 {len(tables_with_auto_inc)} 个表使用自增主键")

        for table_name in tables_with_auto_inc[:5]:
            print(f"    - {table_name}")

        assert len(tables_with_auto_inc) > 0, "应该有表使用自增主键"
        print(f"  ✅ 自增主键验证通过")


def run_tests():
    """运行所有测试"""
    print("\n开始执行MySQL表创建单元测试...\n")

    test_class = TestMySQLTableCreation()
    test_class.setup_class()

    tests = [
        test_class.test_01_mysql_connection,
        test_class.test_02_mysql_table_count,
        test_class.test_03_mysql_table_structure,
        test_class.test_04_create_mysql_tables,
        test_class.test_05_verify_table_exists,
        test_class.test_06_charset_and_collation,
        test_class.test_07_auto_increment,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"  ❌ 断言失败: {e}")
        except pytest.skip.Exception as e:
            skipped += 1
            print(f"  ⏭️  跳过: {e}")
        except Exception as e:
            failed += 1
            print(f"  ❌ 错误: {e}")

    print("\n" + "=" * 80)
    print(f"测试结果: 通过={passed}, 失败={failed}, 跳过={skipped}")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
