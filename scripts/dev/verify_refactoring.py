#!/usr/bin/env python3
"""MyStocks 量化交易数据管理系统 - 重构验证脚本

验证代码拆分后的模块化实现是否正常工作

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import os
import sys
import traceback


# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入模块化后的类
try:
    from src.storage.access.data_access import (
        MySQLDataAccess,
        PostgreSQLDataAccess,
        RedisDataAccess,
        TDengineDataAccess,
    )

    print("✅ 成功导入模块化后的数据访问类")
except ImportError as e:
    print(f"❌ 导入模块化后的数据访问类失败: {e}")
    traceback.print_exc()
    sys.exit(1)


# 验证每个模块的代码结构
def verify_module_structure():
    """验证模块结构"""
    results = {
        "base": False,
        "tdengine": False,
        "postgresql": False,
        "mysql": False,
        "redis": False,
    }

    # 验证基础模块
    try:
        from src.storage.access.modules.base import (
            IDataAccessLayer,
            normalize_dataframe,
        )

        print("✅ 成功导入基础模块")
        results["base"] = True
    except ImportError as e:
        print(f"❌ 导入基础模块失败: {e}")
        traceback.print_exc()

    # 验证 TDengine 模块
    try:
        # 只导入模块，不实例化
        from src.storage.access.modules import tdengine

        print("✅ 成功导入 TDengine 模块")
        results["tdengine"] = True
    except ImportError as e:
        print(f"❌ 导入 TDengine 模块失败: {e}")
        traceback.print_exc()

    # 验证 PostgreSQL 模块
    try:
        from src.storage.access.modules import postgresql

        print("✅ 成功导入 PostgreSQL 模块")
        results["postgresql"] = True
    except ImportError as e:
        print(f"❌ 导入 PostgreSQL 模块失败: {e}")
        traceback.print_exc()

    # 验证 MySQL 模块
    try:
        from src.storage.access.modules import mysql

        print("✅ 成功导入 MySQL 模块")
        results["mysql"] = True
    except ImportError as e:
        print(f"❌ 导入 MySQL 模块失败: {e}")
        traceback.print_exc()

    # 验证 Redis 模块
    try:
        from src.storage.access.modules import redis

        print("✅ 成功导入 Redis 模块")
        results["redis"] = True
    except ImportError as e:
        print(f"❌ 导入 Redis 模块失败: {e}")
        traceback.print_exc()

    return results


# 验证向后兼容性
def verify_backward_compatibility():
    """验证向后兼容性"""
    try:
        # 尝试从新模块导入，使用旧的导入方式
        from src.storage.access.data_access import (
            IDataAccess,
            MySQLAccess,
            PostgreSQLAccess,
            RedisAccess,
            TDengineAccess,
        )

        print("✅ 向后兼容的别名导入成功")
        return True
    except ImportError as e:
        print(f"❌ 向后兼容的别名导入失败: {e}")
        traceback.print_exc()
        return False


# 验证代码示例
def verify_code_examples():
    """验证代码示例"""
    print("\n验证代码示例:")

    # 示例1: 从 data_access 导入类
    try:
        from src.storage.access.data_access import TDengineDataAccess

        print("✅ 示例1: 从 data_access 导入 TDengineDataAccess 成功")
    except ImportError as e:
        print(f"❌ 示例1: 从 data_access 导入 TDengineDataAccess 失败: {e}")
        return False

    # 示例2: 从 modules 子模块导入类
    try:
        from src.storage.access.modules import tdengine

        print("✅ 示例2: 从 modules 子模块导入模块成功")
    except ImportError as e:
        print(f"❌ 示例2: 从 modules 子模块导入模块失败: {e}")
        return False

    # 示例3: 直接从 modules 目录中的文件导入类
    try:
        from src.storage.access.modules.tdengine import TDengineDataAccess

        print("✅ 示例3: 直接从 modules 目录中的文件导入类成功")
    except ImportError as e:
        print(f"❌ 示例3: 直接从 modules 目录中的文件导入类失败: {e}")
        return False

    return True


# 主函数
def main():
    """主函数"""
    print("开始验证模块化重构...")
    print("-" * 80)

    # 验证模块结构
    print("\n验证模块结构:")
    module_results = verify_module_structure()

    # 验证向后兼容性
    print("\n验证向后兼容性:")
    compat_result = verify_backward_compatibility()

    # 验证代码示例
    print("\n验证代码示例:")
    example_result = verify_code_examples()

    # 总结验证结果
    print("\n" + "-" * 80)
    print("验证结果总结:")

    all_passed = True
    for module, passed in module_results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"- {module.upper()} 模块: {status}")
        all_passed = all_passed and passed

    status = "✅ 通过" if compat_result else "❌ 失败"
    print(f"- 向后兼容性: {status}")
    all_passed = all_passed and compat_result

    status = "✅ 通过" if example_result else "❌ 失败"
    print(f"- 代码示例: {status}")
    all_passed = all_passed and example_result

    if all_passed:
        print("\n🎉 所有验证测试通过！模块化重构成功。")
        return 0
    print("\n⚠️ 存在失败的验证测试，请检查错误信息。")
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
