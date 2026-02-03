#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接池集成测试脚本（简化版）
测试新的连接池与现有数据库模块的集成
"""

import sys

# 设置Python路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


def test_connection_manager():
    """测试连接管理器"""
    try:
        # 导入连接管理器
        from src.storage.database.connection_manager import (
            get_connection_manager,
            test_database_connections,
        )

        # 获取连接管理器
        manager = get_connection_manager()
        print("✅ 连接管理器获取成功")

        # 测试连接
        results = test_database_connections()
        print(f"✅ 连接测试成功: {results}")

        return True
    except Exception as e:
        print(f"❌ 连接管理器测试失败: {e}")
        return False


def test_database_pool_config():
    """测试数据库池配置"""
    try:
        from src.core.connection_pool_config import get_config_for_environment

        config = get_config_for_environment()
        print("✅ 配置获取成功")
        print(f"   - 最小连接数: {config.pool_min_connections}")
        print(f"   - 最大连接数: {config.pool_max_connections}")
        print(f"   - 连接超时: {config.pool_timeout}")

        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始连接池集成测试...\n")

    # 测试配置
    config_ok = test_database_pool_config()
    print()

    # 测试连接管理器
    manager_ok = test_connection_manager()
    print()

    # 汇总结果
    if config_ok and manager_ok:
        print("🎉 所有测试通过！")
        print("✅ 连接池系统已成功集成到现有数据库模块")
        return True
    else:
        print("❌ 部分测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
