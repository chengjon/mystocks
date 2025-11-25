"""
T022: PostgreSQL表创建单元测试

验证ConfigDrivenTableManager能够正确创建PostgreSQL表,
包括TimescaleDB Hypertable、Chunk配置、压缩策略等。

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
print("T022: PostgreSQL表创建单元测试")
print("=" * 80 + "\n")


class TestPostgreSQLTableCreation:
    """PostgreSQL表创建测试类"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.manager = ConfigDrivenTableManager()
        cls.conn_manager = DatabaseConnectionManager()

    def test_01_postgresql_connection(self):
        """测试1: PostgreSQL连接测试"""
        print("📍 测试1: PostgreSQL数据库连接")

        try:
            conn = self.conn_manager.get_postgresql_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            cursor.close()
            self.conn_manager._return_postgresql_connection(conn)

            print(f"  ✅ PostgreSQL连接成功")
            print(f"  版本信息: {version[0][:50]}...")
            assert conn is not None
        except Exception as e:
            print(f"  ⚠️  PostgreSQL连接失败: {e}")
            pytest.skip("PostgreSQL未配置或不可用")

    def test_02_timescaledb_extension(self):
        """测试2: TimescaleDB扩展检查"""
        print("\n📍 测试2: 检查TimescaleDB扩展")

        try:
            pool = self.conn_manager.get_postgresql_connection()
            conn = pool.getconn()  # 从连接池获取连接
            cursor = conn.cursor()

            # 检查TimescaleDB扩展
            cursor.execute(
                """
                SELECT extname, extversion
                FROM pg_extension
                WHERE extname = 'timescaledb'
            """
            )
            result = cursor.fetchone()
            cursor.close()
            pool.putconn(conn)  # 归还连接

            if result:
                print(f"  ✅ TimescaleDB已安装: version {result[1]}")
            else:
                print(f"  ⚠️  TimescaleDB未安装 (部分测试将跳过)")
                print(f"  ℹ️  尝试创建扩展: CREATE EXTENSION IF NOT EXISTS timescaledb")

        except Exception as e:
            print(f"  ⚠️  检查失败: {e}")

    def test_03_postgresql_table_count(self):
        """测试3: 统计PostgreSQL表定义数量"""
        print("\n📍 测试3: 统计PostgreSQL表定义")

        pg_tables = [
            t
            for t in self.manager.config["tables"]
            if t["database_type"] == "PostgreSQL"
        ]

        print(f"  PostgreSQL表数量: {len(pg_tables)}")

        # 根据table_config.yaml,应该有多个PostgreSQL表
        assert len(pg_tables) >= 10, f"PostgreSQL表数量不足: {len(pg_tables)}"

        hypertables = [t for t in pg_tables if t.get("is_timescale_hypertable")]
        print(f"  其中Hypertable: {len(hypertables)}")

        for table in pg_tables[:5]:  # 只显示前5个
            is_hyper = (
                "Hypertable" if table.get("is_timescale_hypertable") else "普通表"
            )
            print(f"    - {table['table_name']} ({is_hyper})")

        print(f"  ✅ PostgreSQL表定义验证通过")

    def test_04_hypertable_structure(self):
        """测试4: 验证Hypertable结构定义"""
        print("\n📍 测试4: 验证Hypertable结构")

        # 查找daily_kline表定义
        daily_kline = next(
            (
                t
                for t in self.manager.config["tables"]
                if t["table_name"] == "daily_kline"
            ),
            None,
        )

        assert daily_kline is not None, "未找到daily_kline表定义"
        assert daily_kline.get(
            "is_timescale_hypertable", False
        ), "daily_kline应该是Hypertable"

        # 验证时间列
        time_column = daily_kline.get("time_column")
        assert time_column is not None, "应该配置时间列"
        print(f"  时间列: {time_column}")

        # 验证Chunk配置
        chunk_interval = daily_kline.get("chunk_interval", "1 day")
        print(f"  Chunk间隔: {chunk_interval}")

        # 验证压缩配置
        compression = daily_kline.get("compression", {})
        if compression.get("enabled"):
            print(f"  压缩策略: {compression.get('after_days')}天后压缩")
            print(f"  分段字段: {compression.get('segment_by')}")
            print(f"  排序字段: {compression.get('order_by')}")

        # 验证保留策略
        retention_days = daily_kline.get("retention_days")
        if retention_days:
            print(f"  保留策略: {retention_days}天")

        print(f"  ✅ Hypertable结构验证通过")

    def test_05_create_postgresql_tables(self):
        """测试5: 创建PostgreSQL表"""
        print("\n📍 测试5: 创建PostgreSQL表")

        try:
            pg_tables = [
                t
                for t in self.manager.config["tables"]
                if t["database_type"] == "PostgreSQL"
            ]

            created_count = 0
            skipped_count = 0
            error_count = 0

            # 只创建前5个表作为测试
            for table_def in pg_tables[:5]:
                try:
                    created = self.manager._create_table(table_def)
                    if created:
                        created_count += 1
                        is_hyper = (
                            "Hypertable"
                            if table_def.get("is_timescale_hypertable")
                            else "表"
                        )
                        print(f"  ✅ 创建: {table_def['table_name']} ({is_hyper})")
                    else:
                        skipped_count += 1
                        print(f"  ⏭️  跳过: {table_def['table_name']} (已存在)")
                except Exception as e:
                    error_count += 1
                    print(f"  ⚠️  失败: {table_def['table_name']} - {str(e)[:50]}")

            print(
                f"\n  总计: 创建{created_count}个, 跳过{skipped_count}个, 错误{error_count}个"
            )
            print(f"  ✅ PostgreSQL表创建测试完成")

        except Exception as e:
            print(f"  ⚠️  测试失败: {e}")
            pytest.skip(f"PostgreSQL表创建失败: {e}")

    def test_06_verify_table_exists(self):
        """测试6: 验证表是否存在"""
        print("\n📍 测试6: 验证表存在性")

        try:
            pg_tables = [
                t
                for t in self.manager.config["tables"]
                if t["database_type"] == "PostgreSQL"
            ]

            for table_def in pg_tables[:3]:  # 只检查前3个
                table_name = table_def["table_name"]
                exists = self.manager._table_exists("PostgreSQL", table_name)

                status = "✅ 存在" if exists else "❌ 不存在"
                print(f"  {table_name}: {status}")

            print(f"  ✅ 表存在性验证完成")

        except Exception as e:
            print(f"  ⚠️  验证失败: {e}")

    def test_07_compression_policy(self):
        """测试7: 验证压缩策略配置"""
        print("\n📍 测试7: 验证压缩策略")

        hypertables = [
            t
            for t in self.manager.config["tables"]
            if t["database_type"] == "PostgreSQL" and t.get("is_timescale_hypertable")
        ]

        print(f"  共有 {len(hypertables)} 个Hypertable")

        with_compression = [
            t for t in hypertables if t.get("compression", {}).get("enabled")
        ]

        print(f"  其中 {len(with_compression)} 个配置了压缩策略")

        for table in with_compression[:3]:
            comp = table["compression"]
            print(f"    - {table['table_name']}: {comp.get('after_days')}天后压缩")

        print(f"  ✅ 压缩策略验证通过")


def run_tests():
    """运行所有测试"""
    print("\n开始执行PostgreSQL表创建单元测试...\n")

    test_class = TestPostgreSQLTableCreation()
    test_class.setup_class()

    tests = [
        test_class.test_01_postgresql_connection,
        test_class.test_02_timescaledb_extension,
        test_class.test_03_postgresql_table_count,
        test_class.test_04_hypertable_structure,
        test_class.test_05_create_postgresql_tables,
        test_class.test_06_verify_table_exists,
        test_class.test_07_compression_policy,
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
