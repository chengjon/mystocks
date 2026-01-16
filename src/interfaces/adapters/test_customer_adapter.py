"""
Customer 数据源适配器测试脚本
测试 efinance 和 easyquotation 数据源的功能

示例用法：
    >>> python test_customer_adapter.py
"""

from src.adapters.customer_adapter import CustomerDataSource
import sys
import os
import pandas as pd

# 将项目根目录添加到模块搜索路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 使用相对导入


def test_customer_data_source():
    """测试Customer数据源"""
    print("=" * 50)
    print("Customer 数据源适配器测试")
    print("=" * 50)

    # 创建数据源实例
    print("1. 创建Customer数据源实例...")
    try:
        customer_source = CustomerDataSource()
        print("   ✓ Customer数据源实例创建成功")
    except Exception as e:
        print(f"   ✗ Customer数据源实例创建失败: {e}")
        return

    # 测试获取实时数据功能（重点测试efinance的沪深市场A股最新状况）
    print("\n2. 测试获取沪深市场A股最新状况...")
    try:
        # 获取沪深市场A股最新状况
        realtime_data = customer_source.get_real_time_data("hs")  # hs表示沪深市场
        if isinstance(realtime_data, pd.DataFrame) and not realtime_data.empty:
            print(f"   ✓ 成功获取到沪深市场A股最新状况，共{len(realtime_data)}条记录")
            print("   前5行数据预览:")
            print(realtime_data.head())
        elif isinstance(realtime_data, dict) and realtime_data:
            print(f"   ✓ 成功获取到沪深市场A股最新状况: {realtime_data}")
        else:
            print("   ! 未能获取到沪深市场A股最新状况数据")
    except Exception as e:
        print(f"   ✗ 获取沪深市场A股最新状况失败: {e}")

    # 测试获取特定股票实时数据
    print("\n3. 测试获取特定股票实时数据...")
    try:
        # 以平安银行(000001)为例
        stock_data = customer_source.get_real_time_data("000001")
        if isinstance(stock_data, pd.DataFrame) and not stock_data.empty:
            print(f"   ✓ 成功获取到股票000001的实时数据，共{len(stock_data)}条记录")
            print("   数据预览:")
            print(stock_data.head())
        elif isinstance(stock_data, dict) and stock_data:
            print(f"   ✓ 成功获取到股票000001的实时数据: {stock_data}")
        else:
            print("   ! 未能获取到股票000001的实时数据")
    except Exception as e:
        print(f"   ✗ 获取股票000001实时数据失败: {e}")

    # 测试获取股票日线数据
    print("\n4. 测试获取股票日线数据...")
    try:
        # 以平安银行(000001)为例，获取最近一个月的数据
        from datetime import datetime, timedelta
        from src.utils.date_utils import normalize_date

        end_date = normalize_date(datetime.now())
        start_date = normalize_date(datetime.now() - timedelta(days=30))

        daily_data = customer_source.get_stock_daily("000001", start_date, end_date)
        if isinstance(daily_data, pd.DataFrame) and not daily_data.empty:
            print(f"   ✓ 成功获取到股票000001的日线数据，共{len(daily_data)}条记录")
            print("   数据预览:")
            print(daily_data.head())
        else:
            print("   ! 未能获取到股票000001的日线数据")
    except Exception as e:
        print(f"   ✗ 获取股票000001日线数据失败: {e}")

    # 测试获取股票基本信息
    print("\n5. 测试获取股票基本信息...")
    try:
        stock_info = customer_source.get_stock_basic("000001")
        if stock_info:
            print(f"   ✓ 成功获取到股票000001的基本信息: {stock_info}")
        else:
            print("   ! 未能获取到股票000001的基本信息")
    except Exception as e:
        print(f"   ✗ 获取股票000001基本信息失败: {e}")

    # 测试获取财务数据
    print("\n6. 测试获取财务数据...")
    try:
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
    print("Customer 数据源适配器测试完成")
    print("=" * 50)


if __name__ == "__main__":
    print("开始执行Customer数据源测试...")
    test_customer_data_source()
    print("Customer数据源测试执行完成。")
