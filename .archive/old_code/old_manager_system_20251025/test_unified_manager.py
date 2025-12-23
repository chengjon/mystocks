"""
统一数据管理器测试脚本
测试UnifiedDataManager使用Customer数据源的功能
"""

import sys
import os
import pandas as pd

# 将项目根目录添加到模块搜索路径中
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 直接从manager目录导入UnifiedDataManager
from manager.unified_data_manager import UnifiedDataManager


def test_unified_data_manager_with_customer_source():
    """测试UnifiedDataManager使用Customer数据源"""
    print("=" * 50)
    print("UnifiedDataManager 使用Customer数据源测试")
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

    # 测试获取股票日线数据
    print("\n3. 测试获取股票日线数据...")
    try:
        # 以平安银行(000001)为例
        daily_data = manager.get_stock_daily("000001", "2025-09-01", "2025-09-19")
        if isinstance(daily_data, pd.DataFrame) and not daily_data.empty:
            print(f"   ✓ 成功获取到股票000001的日线数据，共{len(daily_data)}条记录")
            print("   数据预览:")
            print(daily_data.head())
        else:
            print("   ! 未能获取到股票000001的日线数据")
    except Exception as e:
        print(f"   ✗ 获取股票000001日线数据失败: {e}")

    # 测试获取股票基本信息
    print("\n4. 测试获取股票基本信息...")
    try:
        stock_info = manager.get_stock_basic("000001")
        if stock_info:
            print(f"   ✓ 成功获取到股票000001的基本信息: {stock_info}")
        else:
            print("   ! 未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ✗ 获取股票000001基本信息失败: {e}")

    # 测试获取财务数据
    print("\n5. 测试获取财务数据...")
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
    print("UnifiedDataManager 使用Customer数据源测试完成")
    print("=" * 50)


if __name__ == "__main__":
    print("开始执行UnifiedDataManager使用Customer数据源测试...")
    test_unified_data_manager_with_customer_source()
    print("测试执行完成。")
