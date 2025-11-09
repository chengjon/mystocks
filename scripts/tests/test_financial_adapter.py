"""
财务数据适配器测试脚本
测试FinancialDataSource的功能
"""

import sys
import os
import pandas as pd

# 将项目根目录添加到模块搜索路径中
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

# 直接从adapters目录导入FinancialDataSource
from adapters.financial_adapter import FinancialDataSource


def test_financial_adapter():
    """测试FinancialDataSource的功能"""
    print("=" * 50)
    print("FinancialDataSource 功能测试")
    print("=" * 50)

    # 创建FinancialDataSource实例
    print("1. 创建FinancialDataSource实例...")
    try:
        adapter = FinancialDataSource()
        print("   ✓ FinancialDataSource实例创建成功")
    except Exception as e:
        print(f"   ✗ FinancialDataSource实例创建失败: {e}")
        return

    # 测试获取财务数据
    print("\n2. 测试获取财务数据...")
    try:
        financial_data = adapter.get_financial_data("000001")
        if isinstance(financial_data, pd.DataFrame) and not financial_data.empty:
            print(f"   ✓ 成功获取到股票000001的财务数据，共{len(financial_data)}条记录")
            print(f"   数据预览:")
            print(financial_data.head())
        else:
            print("   ! 未能获取到股票000001的财务数据")
    except Exception as e:
        print(f"   ✗ 获取股票000001财务数据失败: {e}")

    # 测试获取交易日历
    print("\n3. 测试获取交易日历...")
    try:
        calendar_data = adapter.get_market_calendar()
        if isinstance(calendar_data, pd.DataFrame) and not calendar_data.empty:
            print(f"   ✓ 成功获取到交易日历，共{len(calendar_data)}条记录")
            print(f"   数据预览:")
            print(calendar_data.head())
        else:
            print("   ! 未能获取到交易日历")
    except Exception as e:
        print(f"   ✗ 获取交易日历失败: {e}")

    # 测试获取股票基本信息
    print("\n4. 测试获取股票基本信息...")
    try:
        stock_info = adapter.get_stock_basic("000001")
        if stock_info:
            print(f"   ✓ 成功获取到股票000001的基本信息: {stock_info}")
        else:
            print("   ! 未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ✗ 获取股票000001基本信息失败: {e}")

    print("\n" + "=" * 50)
    print("FinancialDataSource 功能测试完成")
    print("=" * 50)


if __name__ == "__main__":
    print("开始执行FinancialDataSource功能测试...")
    test_financial_adapter()
    print("测试执行完成。")
