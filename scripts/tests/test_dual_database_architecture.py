#!/usr/bin/env python3
"""TDengine + PostgreSQL双数据库架构验证测试

验证项:
1. DatabaseTarget枚举只包含TDENGINE和POSTGRESQL
2. 所有34个数据分类正确路由到两种数据库之一
3. TDengineDataAccess和PostgreSQLDataAccess可正常导入
4. MySQL和Redis访问类文件不存在
5. requirements.txt不包含pymysql和redis依赖
"""

import os
import sys


# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import sys
from pathlib import Path


def test_database_target_enum():
    """测试DatabaseTarget枚举只包含2种数据库"""
    print("\n=== 测试1: DatabaseTarget枚举验证 ===")

    from src.core.data_classification import DatabaseTarget

    targets = [t.value for t in DatabaseTarget]
    print(f"DatabaseTarget包含: {targets}")

    assert len(targets) == 2, f"❌ 期望2种数据库，实际{len(targets)}种"
    assert "tdengine" in targets, "❌ 缺少tdengine"
    assert "postgresql" in targets, "❌ 缺少postgresql"
    assert "mysql" not in targets, "❌ 不应包含mysql"
    assert "redis" not in targets, "❌ 不应包含redis"

    print("✅ DatabaseTarget枚举正确 (仅TDengine和PostgreSQL)")
    return True


def test_data_routing():
    """测试所有数据分类正确路由"""
    print("\n=== 测试2: 数据路由验证 ===")

    from src.core.data_classification import DatabaseTarget, DataClassification

    all_classifications = list(DataClassification)
    print(f"总数据分类数: {len(all_classifications)}")

    tdengine_count = 0
    postgresql_count = 0

    for classification in all_classifications:
        target = DataManager().get_target_database(classification)

        if target == DatabaseTarget.TDENGINE:
            tdengine_count += 1
        elif target == DatabaseTarget.POSTGRESQL:
            postgresql_count += 1
        else:
            print(f"❌ 未知路由目标: {classification.value} → {target}")
            return False

    print(f"TDengine路由: {tdengine_count}项")
    print(f"PostgreSQL路由: {postgresql_count}项")
    print(f"总计: {tdengine_count + postgresql_count}项")

    assert tdengine_count > 0, "❌ TDengine应至少处理高频时序数据"
    assert postgresql_count > 0, "❌ PostgreSQL应处理其他所有数据"
    assert tdengine_count + postgresql_count == len(
        all_classifications,
    ), "❌ 路由覆盖不完整"

    print(f"✅ 所有{len(all_classifications)}项数据分类正确路由到2种数据库")
    return True


def test_data_access_imports():
    """测试数据访问类导入"""
    print("\n=== 测试3: 数据访问类导入验证 ===")

    try:
        from src.data_access import PostgreSQLDataAccess, TDengineDataAccess

        print("✅ TDengineDataAccess导入成功")
        print("✅ PostgreSQLDataAccess导入成功")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 验证不应存在的类无法导入
    try:
        from src.data_access import MySQLDataAccess

        print("❌ MySQLDataAccess不应存在但可以导入")
        return False
    except ImportError:
        print("✅ MySQLDataAccess已移除")

    try:
        from src.data_access import RedisDataAccess

        print("❌ RedisDataAccess不应存在但可以导入")
        return False
    except ImportError:
        print("✅ RedisDataAccess已移除")

    return True


def test_removed_files():
    """测试已删除的文件"""
    print("\n=== 测试4: 已删除文件验证 ===")

    removed_files = [
        "data_access/mysql_access.py",
        "data_access/redis_access.py",
    ]

    all_removed = True
    for filepath in removed_files:
        if Path(filepath).exists():
            print(f"❌ 文件应已删除但仍存在: {filepath}")
            all_removed = False
        else:
            print(f"✅ 文件已删除: {filepath}")

    return all_removed


def test_requirements():
    """测试requirements.txt依赖"""
    print("\n=== 测试5: requirements.txt验证 ===")

    with open("requirements.txt") as f:
        content = f.read()

    # 应该包含的依赖
    required_deps = ["taospy", "psycopg2-binary"]
    for dep in required_deps:
        if dep in content:
            print(f"✅ 包含必需依赖: {dep}")
        else:
            print(f"❌ 缺少必需依赖: {dep}")
            return False

    # 不应该包含的依赖
    removed_deps = ["pymysql", "redis"]
    for dep in removed_deps:
        if dep in content:
            print(f"❌ 不应包含已移除依赖: {dep}")
            return False
        print(f"✅ 已移除依赖: {dep}")

    return True


def test_routing_statistics():
    """打印路由统计信息"""
    print("\n=== 路由统计摘要 ===")

    stats = DataManager().get_routing_statistics()

    for db_type, count in stats.items():
        classifications = DataManager().get_classifications_by_database(db_type)
        print(f"\n{db_type.value.upper()} ({count}项):")
        for i, classification in enumerate(classifications, 1):
            print(f"  {i}. {classification.value}")

    return True


def main():
    """运行所有验证测试"""
    print("=" * 80)
    print("TDengine + PostgreSQL 双数据库架构验证")
    print("=" * 80)

    tests = [
        ("DatabaseTarget枚举", test_database_target_enum),
        ("数据路由映射", test_data_routing),
        ("数据访问类导入", test_data_access_imports),
        ("已删除文件", test_removed_files),
        ("requirements.txt", test_requirements),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试失败: {name} - {e}")
            results.append((name, False))

    # 打印路由统计
    test_routing_statistics()

    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！TDengine + PostgreSQL 双数据库架构验证成功")
        return 0
    print(f"\n⚠️  {total - passed} 项测试失败")
    return 1


if __name__ == "__main__":
    sys.exit(main())
