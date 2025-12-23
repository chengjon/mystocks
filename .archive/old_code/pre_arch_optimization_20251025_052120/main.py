"""
主程序入口
演示统一数据接口的使用
"""

import sys
import os

# 将当前目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mystocks.manager.unified_data_manager import UnifiedDataManager


def main():
    """主函数：演示统一数据接口的使用"""
    # 初始化统一数据管理器
    manager = UnifiedDataManager()

    # 设置时间范围 - 使用固定的日期范围以确保有数据
    end_date = "2023-08-31"
    start_date = "2023-08-01"

    print(f"查询时间范围: {start_date} 至 {end_date}")

    # 演示1: 从Akshare获取数据
    print("=" * 50)
    print("演示1: 从Akshare获取数据")
    print("=" * 50)

    # 测试不同的股票代码格式
    test_stocks = ["600000", "000001", "000001.SZ", "600000.SH"]

    for stock_code in test_stocks:
        print(f"\n尝试获取股票数据: {stock_code}")
        stock_data_ak = manager.get_stock_daily(
            symbol=stock_code,
            start_date=start_date,
            end_date=end_date,
            source_type="akshare",
        )
        print(f"获取到 {len(stock_data_ak)} 行股票数据")
        if not stock_data_ak.empty:
            print(stock_data_ak.head())
            break  # 只要有一个成功就停止测试

    # 测试不同的指数代码格式
    test_indices = ["sh000001", "sz399001", "000001", "399001"]

    for index_code in test_indices:
        print(f"\n尝试获取指数数据: {index_code}")
        index_data_ak = manager.get_index_daily(
            symbol=index_code,
            start_date=start_date,
            end_date=end_date,
            source_type="akshare",
        )
        print(f"获取到 {len(index_data_ak)} 行指数数据")
        if not index_data_ak.empty:
            print(index_data_ak.head())
            break  # 只要有一个成功就停止测试

    # 获取股票基本信息
    stock_basic_ak = manager.get_stock_basic("000001", "akshare")
    print(f"\n获取到股票基本信息: {len(stock_basic_ak)} 项")
    for key, value in list(stock_basic_ak.items())[:5]:  # 只显示前5项
        print(f"  {key}: {value}")

    # 演示2: 从Baostock获取数据
    print("\n" + "=" * 50)
    print("演示2: 从Baostock获取数据")
    print("=" * 50)

    # 获取股票日线数据
    stock_data_bs = manager.get_stock_daily(
        symbol="sz.000001",
        start_date=start_date,
        end_date=end_date,
        source_type="baostock",
    )
    print(f"获取到 {len(stock_data_bs)} 行股票数据")
    if not stock_data_bs.empty:
        print(stock_data_bs.head())

    # 获取指数日线数据
    index_data_bs = manager.get_index_daily(
        symbol="sh.000001",
        start_date=start_date,
        end_date=end_date,
        source_type="baostock",
    )
    print(f"\n获取到 {len(index_data_bs)} 行指数数据")
    if not index_data_bs.empty:
        print(index_data_bs.head())

    # 获取股票基本信息
    stock_basic_bs = manager.get_stock_basic("sz.000001", "baostock")
    print(f"\n获取到股票基本信息: {len(stock_basic_bs)} 项")
    for key, value in list(stock_basic_bs.items())[:5]:  # 只显示前5项
        print(f"  {key}: {value}")

    # 演示3: 比较两个数据源
    print("\n" + "=" * 50)
    print("演示3: 比较两个数据源")
    print("=" * 50)

    manager.compare_data_sources("sz.000001", start_date, end_date)

    # 演示4: 使用默认数据源
    print("\n" + "=" * 50)
    print("演示4: 使用默认数据源")
    print("=" * 50)

    default_data = manager.get_stock_daily("000001", start_date, end_date)
    print(f"使用默认数据源获取到 {len(default_data)} 行数据")


if __name__ == "__main__":
    main()
