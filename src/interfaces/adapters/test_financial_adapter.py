#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial适配器测试文件
用于测试FinancialDataSource类的功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from src.interfaces.adapters.financial import FinancialDataSource  # noqa: E402


def test_financial_adapter():
    """测试Financial适配器"""
    print("=== Financial适配器测试 ===")

    # 创建Financial数据源实例
    financial_ds = FinancialDataSource()

    # 检查数据源是否初始化成功
    print(
        f"Financial数据源初始化状态: efinance可用={financial_ds.efinance_available}, "
        # pylint: disable=no-member
        f"easyquotation可用={financial_ds.easyquotation_available}"
    )

    # 测试获取股票日线数据（以平安银行为例）
    print("\n--- 测试获取股票日线数据 ---")
    symbol = "000001"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    daily_data = financial_ds.get_stock_daily(symbol, start_date, end_date)
    if isinstance(daily_data, pd.DataFrame) and not daily_data.empty:
        print(f"获取到{len(daily_data)}行日线数据")
        print("前5行数据:")
        print(daily_data.head())
    else:
        print("未获取到日线数据")

    # 测试获取股票基本信息
    print("\n--- 测试获取股票基本信息 ---")
    basic_info = financial_ds.get_stock_basic(symbol)
    print(f"基本信息类型: {type(basic_info)}")
    if isinstance(basic_info, pd.DataFrame) and not basic_info.empty:  # pylint: disable=no-member
        print("基本信息:")
        print(basic_info.head())  # pylint: disable=no-member
    else:
        print("未获取到基本信息")

    # 测试获取实时数据（特定股票）
    print("\n--- 测试获取特定股票实时数据 ---")
    real_time_data = financial_ds.get_real_time_data(symbol)
    print(f"实时数据类型: {type(real_time_data)}")
    if isinstance(real_time_data, pd.DataFrame) and not real_time_data.empty:  # pylint: disable=no-member
        print("实时数据:")
        print(real_time_data.head())  # pylint: disable=no-member
    else:
        print("未获取到特定股票实时数据")

    # 测试获取市场快照
    print("\n--- 测试获取市场快照 ---")
    market_snapshot = financial_ds.get_real_time_data(market="CN")
    print(f"市场快照数据类型: {type(market_snapshot)}")
    if isinstance(market_snapshot, pd.DataFrame) and not market_snapshot.empty:  # pylint: disable=no-member
        print(f"获取到{len(market_snapshot)}只股票的市场快照")
        print("市场快照数据:")
        print(market_snapshot.head())  # pylint: disable=no-member
    else:
        print("未获取到市场快照数据")


if __name__ == "__main__":
    test_financial_adapter()
