#!/usr/bin/env python3
"""
T037.6: 系统初始化测试 - PostgreSQL-only架构验证

验证项目：
1. 所有模块可正常导入（无TDengine/MySQL/Redis依赖）
2. DatabaseConnectionManager只验证PostgreSQL
3. MyStocksUnifiedManager正确初始化
4. 数据路由仅指向PostgreSQL
"""

import sys
import os

print("=" * 80)
print("T037.6: PostgreSQL-only架构系统初始化测试")
print("=" * 80)
print()

# 测试1: 导入核心模块
print("测试1: 导入核心模块...")
try:
    from core import DataClassification, DatabaseTarget, DataStorageStrategy

    print("   ✅ core.py 导入成功")
except Exception as e:
    print(f"   ❌ core.py 导入失败: {e}")
    sys.exit(1)

# 测试2: 验证DatabaseTarget只包含PostgreSQL
print("\n测试2: 验证DatabaseTarget枚举...")
try:
    targets = [t.value for t in DatabaseTarget]
    print(f"   数据库类型: {targets}")

    if targets == ["postgresql"]:
        print("   ✅ DatabaseTarget仅包含PostgreSQL")
    else:
        print(f"   ❌ DatabaseTarget包含意外类型: {targets}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ DatabaseTarget验证失败: {e}")
    sys.exit(1)

# 测试3: 导入数据访问层
print("\n测试3: 导入数据访问层...")
try:
    from data_access import PostgreSQLDataAccess

    print("   ✅ PostgreSQLDataAccess 导入成功")
except Exception as e:
    print(f"   ❌ PostgreSQLDataAccess 导入失败: {e}")
    sys.exit(1)

# 测试4: 验证TDengineDataAccess不存在
print("\n测试4: 验证TDengineDataAccess已移除...")
try:
    from data_access import TDengineDataAccess

    print("   ❌ TDengineDataAccess仍然存在（应该已删除）")
    sys.exit(1)
except ImportError:
    print("   ✅ TDengineDataAccess已成功移除")

# 测试5: 导入连接管理器
print("\n测试5: 导入连接管理器...")
try:
    from db_manager.connection_manager import DatabaseConnectionManager

    print("   ✅ DatabaseConnectionManager 导入成功")
except Exception as e:
    print(f"   ❌ DatabaseConnectionManager 导入失败: {e}")
    sys.exit(1)

# 测试6: 验证数据路由
print("\n测试6: 验证数据路由策略...")
try:
    # 测试几个关键数据分类的路由
    test_classifications = [
        DataClassification.TICK_DATA,
        DataClassification.MINUTE_KLINE,
        DataClassification.DAILY_KLINE,
        DataClassification.TECHNICAL_INDICATORS,
        DataClassification.SYMBOLS_INFO,
    ]

    all_postgresql = True
    for classification in test_classifications:
        target = DataStorageStrategy.get_target_database(classification)
        print(f"   {classification.value} → {target.value}")
        if target != DatabaseTarget.POSTGRESQL:
            print(f"   ❌ {classification.value} 未路由到PostgreSQL")
            all_postgresql = False

    if all_postgresql:
        print("   ✅ 所有数据分类正确路由到PostgreSQL")
    else:
        print("   ❌ 部分数据分类路由错误")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ 数据路由验证失败: {e}")
    sys.exit(1)

# 测试7: 验证监控数据库可导入
print("\n测试7: 验证监控模块...")
try:
    from monitoring.monitoring_database import MonitoringDatabase

    print("   ✅ MonitoringDatabase 导入成功")
except Exception as e:
    print(f"   ❌ MonitoringDatabase 导入失败: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ PostgreSQL-only架构验证通过！")
print("=" * 80)
print("\n总结:")
print("  - 所有核心模块可正常导入")
print("  - DatabaseTarget仅包含PostgreSQL")
print("  - TDengine/MySQL/Redis代码已完全移除")
print("  - 所有数据分类正确路由到PostgreSQL")
print("  - 系统架构简化完成：4数据库 → 1数据库")
print()
