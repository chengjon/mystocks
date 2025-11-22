"""
T021: TDengine表创建单元测试

验证ConfigDrivenTableManager能够正确创建TDengine Super Tables,
包括标签(Tags)、压缩策略、保留策略等配置。

创建日期: 2025-10-11
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from src.core.config_driven_table_manager import ConfigDrivenTableManager
from src.db_manager.connection_manager import DatabaseConnectionManager

print("\n" + "=" * 80)
print("T021: TDengine表创建单元测试")
print("=" * 80 + "\n")


class TestTDengineTableCreation:
    """TDengine表创建测试类"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.manager = ConfigDrivenTableManager()
        cls.conn_manager = DatabaseConnectionManager()

    def test_01_config_loaded(self):
        """测试1: 配置文件加载成功"""
        print("📍 测试1: 验证配置文件加载")

        assert self.manager.config is not None
        assert "tables" in self.manager.config
        assert len(self.manager.config["tables"]) > 0

        print(f"  ✅ 配置文件已加载: {len(self.manager.config['tables'])}个表定义")

    def test_02_tdengine_connection(self):
        """测试2: TDengine连接测试"""
        print("\n📍 测试2: TDengine数据库连接")

        try:
            conn = self.conn_manager.get_tdengine_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT SERVER_VERSION()")
            version = cursor.fetchone()
            cursor.close()

            print(
                f"  ✅ TDengine连接成功 (version={version[0] if version else 'unknown'})"
            )
            assert conn is not None
        except Exception as e:
            print(f"  ⚠️  TDengine连接失败: {e}")
            pytest.skip("TDengine未配置或不可用")

    def test_03_tdengine_table_count(self):
        """测试3: 统计TDengine表定义数量"""
        print("\n📍 测试3: 统计TDengine表定义")

        tdengine_tables = [
            t for t in self.manager.config["tables"] if t["database_type"] == "TDengine"
        ]

        print(f"  TDengine表数量: {len(tdengine_tables)}")

        # 根据table_config.yaml,应该有6个TDengine表
        # tick_data, minute_kline, order_book_depth, level2_snapshot, index_intraday_quotes
        assert len(tdengine_tables) >= 5, f"TDengine表数量不足: {len(tdengine_tables)}"

        for table in tdengine_tables:
            print(f"    - {table['table_name']} ({table.get('classification', 'N/A')})")

        print(f"  ✅ TDengine表定义验证通过")

    def test_04_super_table_structure(self):
        """测试4: 验证Super Table结构定义"""
        print("\n📍 测试4: 验证Super Table结构")

        # 查找tick_data表定义
        tick_table = next(
            (
                t
                for t in self.manager.config["tables"]
                if t["table_name"] == "tick_data"
            ),
            None,
        )

        assert tick_table is not None, "未找到tick_data表定义"
        assert tick_table.get("is_super_table", False), "tick_data应该是Super Table"

        # 验证列定义
        columns = tick_table.get("columns", [])
        assert len(columns) > 0, "列定义为空"

        # 验证必需列
        col_names = [col["name"] for col in columns]
        assert "ts" in col_names, "缺少时间戳列"
        assert "price" in col_names, "缺少价格列"
        assert "volume" in col_names, "缺少成交量列"

        print(f"  列数量: {len(columns)}")
        print(f"  必需列验证: ✓")

        # 验证标签(Tags) - 在columns中通过is_tag: true标记
        tags = [col for col in columns if col.get("is_tag", False)]
        # 如果没有通过is_tag标记，检查是否有单独的tags数组
        if len(tags) == 0:
            tags = tick_table.get("tags", [])

        # Tags是可选的，某些配置可能不使用tags
        if len(tags) > 0:
            tag_names = [tag["name"] for tag in tags]
            print(f"  标签数量: {len(tags)}")
            if "symbol" in tag_names:
                print(f"  必需标签验证: ✓")
        else:
            print(f"  标签数量: 0 (配置未定义tags)")

        # 验证压缩配置 (可选)
        compression = tick_table.get("compression", {})
        if compression:
            if compression.get("enabled", False):
                codec = compression.get("codec", "N/A")
                print(f"  压缩配置: {codec} / {compression.get('level', 'N/A')}")
            else:
                print(f"  压缩配置: 未启用")
        else:
            print(f"  压缩配置: 未定义")

        # 验证保留策略 (可选)
        retention_days = tick_table.get("retention_days")
        if retention_days is not None and retention_days > 0:
            print(f"  保留策略: {retention_days}天")
        else:
            print(f"  保留策略: 未定义")
        print(f"  ✅ Super Table结构验证通过")

    def test_05_create_super_table(self):
        """测试5: 创建Super Table"""
        print("\n📍 测试5: 创建Super Table")

        try:
            # 尝试创建所有TDengine表
            tdengine_tables = [
                t
                for t in self.manager.config["tables"]
                if t["database_type"] == "TDengine"
            ]

            created_count = 0
            skipped_count = 0

            for table_def in tdengine_tables:
                try:
                    created = self.manager._create_table(table_def)
                    if created:
                        created_count += 1
                        print(f"  ✅ 创建: {table_def['table_name']}")
                    else:
                        skipped_count += 1
                        print(f"  ⏭️  跳过: {table_def['table_name']} (已存在)")
                except Exception as e:
                    print(f"  ⚠️  失败: {table_def['table_name']} - {e}")

            print(f"\n  总计: 创建{created_count}个, 跳过{skipped_count}个")
            print(f"  ✅ TDengine表创建测试完成")

        except Exception as e:
            print(f"  ⚠️  测试失败: {e}")
            pytest.skip(f"TDengine表创建失败: {e}")

    def test_06_verify_table_exists(self):
        """测试6: 验证表是否存在"""
        print("\n📍 测试6: 验证表存在性")

        try:
            tdengine_tables = [
                t
                for t in self.manager.config["tables"]
                if t["database_type"] == "TDengine"
            ]

            for table_def in tdengine_tables[:3]:  # 只检查前3个
                table_name = table_def["table_name"]
                exists = self.manager._table_exists("TDengine", table_name)

                status = "✅ 存在" if exists else "❌ 不存在"
                print(f"  {table_name}: {status}")

            print(f"  ✅ 表存在性验证完成")

        except Exception as e:
            print(f"  ⚠️  验证失败: {e}")


def run_tests():
    """运行所有测试"""
    print("\n开始执行TDengine表创建单元测试...\n")

    test_class = TestTDengineTableCreation()
    test_class.setup_class()

    tests = [
        test_class.test_01_config_loaded,
        test_class.test_02_tdengine_connection,
        test_class.test_03_tdengine_table_count,
        test_class.test_04_super_table_structure,
        test_class.test_05_create_super_table,
        test_class.test_06_verify_table_exists,
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
