#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial适配器使用示例
展示如何使用FinancialDataSource类获取各种金融数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.financial_adapter import FinancialDataSource
import pandas as pd


def main():
    """主函数：演示Financial适配器的使用方法"""
    print("=== Financial适配器使用示例 ===")

    # 创建Financial数据源实例
    financial_ds = FinancialDataSource()

    # 检查数据源是否初始化成功
    print("数据源初始化状态:")
    print(f"  - efinance可用: {financial_ds.efinance_available}")
    print(f"  - easyquotation可用: {financial_ds.easyquotation_available}")

    # 示例1: 获取股票日线数据
    print("\n--- 示例1: 获取股票日线数据 ---")
    symbol = "000001"  # 平安银行
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    daily_data = financial_ds.get_stock_daily(symbol, start_date, end_date)
    if not daily_data.empty:
        print(f"成功获取到{len(daily_data)}行日线数据")
        print("数据列名:", list(daily_data.columns))
        print("前3行数据:")
        print(daily_data.head(3))
    else:
        print("未能获取到日线数据")

    # 示例2: 获取股票基本信息
    print("\n--- 示例2: 获取股票基本信息 ---")
    basic_info = financial_ds.get_stock_basic(symbol)
    if isinstance(basic_info, pd.DataFrame) and not basic_info.empty:
        print("股票基本信息:")
        print(basic_info)
    else:
        print("未能获取到股票基本信息")

    # 示例3: 获取特定股票实时数据
    print("\n--- 示例3: 获取特定股票实时数据 ---")
    real_time_data = financial_ds.get_real_time_data(symbol)
    if isinstance(real_time_data, pd.DataFrame) and not real_time_data.empty:
        print("特定股票实时数据:")
        print(real_time_data)
    else:
        print("未能获取到特定股票实时数据")

    # 示例4: 获取市场快照数据
    print("\n--- 示例4: 获取市场快照数据 ---")
    market_snapshot = financial_ds.get_real_time_data(market="CN")
    if isinstance(market_snapshot, pd.DataFrame) and not market_snapshot.empty:
        print(f"获取到{len(market_snapshot)}只股票的市场快照数据")
        print("市场快照数据列名:", list(market_snapshot.columns))
        print("前3行数据:")
        print(market_snapshot.head(3))
    else:
        print("未能获取到市场快照数据")

    # 示例5: 获取指数日线数据
    print("\n--- 示例5: 获取指数日线数据 ---")
    index_symbol = "000300"  # 沪深300
    index_data = financial_ds.get_index_daily(index_symbol, start_date, end_date)
    if not index_data.empty:
        print(f"成功获取到{len(index_data)}行指数日线数据")
        print("指数数据列名:", list(index_data.columns))
        print("前3行数据:")
        print(index_data.head(3))
    else:
        print("未能获取到指数日线数据")

    # 示例6: 获取指数成分股
    print("\n--- 示例6: 获取指数成分股 ---")
    components = financial_ds.get_index_components(
        index_symbol
    )  # 也可以使用指数名称如"沪深300"
    if not components.empty:
        print(f"成功获取到{len(components)}个指数成分股")
        print("前10个成分股:")
        print(components.head(10))
    else:
        print("未能获取到指数成分股")

    # 示例7: 获取财务数据
    print("\n--- 示例7: 获取财务数据 ---")
    financial_data = financial_ds.get_financial_data(symbol)
    if not financial_data.empty:
        print(f"成功获取到{len(financial_data)}行财务数据")
        print("财务数据列名:", list(financial_data.columns))
        print("前3行数据:")
        print(financial_data.head(3))
    else:
        print("未能获取到财务数据")


if __name__ == "__main__":
    main()
