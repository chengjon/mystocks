"""
财务数据功能测试脚本
测试UnifiedDataManager使用Customer数据源获取财务数据的功能
"""

import sys
import os
import pandas as pd

# 将项目根目录添加到模块搜索路径中
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 直接从manager目录导入UnifiedDataManager
from manager.unified_data_manager import UnifiedDataManager


def test_financial_data_with_customer_source():
    """测试UnifiedDataManager使用Customer数据源获取财务数据"""
    print("=" * 50)
    print("UnifiedDataManager 财务数据功能测试")
    print("=" * 50)

    # 创建统一数据管理器实例
    print("1. 创建UnifiedDataManager实例...")
    try:
        manager = UnifiedDataManager()
        print("   ✓ UnifiedDataManager实例创建成功")
    except Exception as e:
        print(f"   ✗ UnifiedDataManager实例创建失败: {e}")
        return

    # 设置默认数据源为Customer
    print("\n2. 设置默认数据源为Customer...")
    try:
        manager.set_default_source("customer")
        print("   ✓ 默认数据源设置为Customer")
    except Exception as e:
        print(f"   ✗ 设置默认数据源失败: {e}")

    # 测试获取财务数据
    print("\n3. 测试获取财务数据...")
    try:
        # 通过UnifiedDataManager直接调用Customer数据源的财务数据功能
        financial_data = manager.get_stock_basic("000001")
        if financial_data:
            print("   ✓ 成功获取到股票000001的基本信息")
            print(f"   数据预览: {financial_data}")
        else:
            print("   ! 未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ✗ 获取股票000001基本信息失败: {e}")

    # 测试获取财务数据
    print("\n4. 测试获取财务数据...")
    try:
        # 通过UnifiedDataManager直接调用Customer数据源的财务数据功能
        customer_source = manager.get_source("customer")
        financial_data = customer_source.get_financial_data("000001")
        if isinstance(financial_data, pd.DataFrame) and not financial_data.empty:
            print(f"   ✓ 成功获取到股票000001的财务数据，共{len(financial_data)}条记录")
            print("   数据预览:")
            print(financial_data.head())
        else:
            print("   ! 未能获取到股票000001的财务数据")
    except Exception as e:
        print(f"   ✗ 获取股票000001财务数据失败: {e}")

    print("\n" + "=" * 50)
    print("UnifiedDataManager 财务数据功能测试完成")
    print("=" * 50)


if __name__ == "__main__":
    print("开始执行UnifiedDataManager财务数据功能测试...")
    test_financial_data_with_customer_source()
    print("测试执行完成。")
