#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据管理系统演示脚本
展示UnifiedDataManager如何统一管理多种数据源
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manager.unified_data_manager import UnifiedDataManager
import pandas as pd


def main():
    """主演示函数"""
    print("=" * 70)
    print("股票数据管理系统演示")
    print("=" * 70)
    
    # 创建统一数据管理器
    manager = UnifiedDataManager()
    
    # 要测试的股票代码
    stock_code = "000001"  # 平安银行
    
    print(f"\n正在获取股票 {stock_code} 的数据...")
    print("-" * 50)
    
    # 1. 使用默认数据源(Akshare)获取日线数据
    print("1. 使用Akshare获取日线数据:")
    try:
        daily_data = manager.get_stock_daily(stock_code, '2024-01-01', '2024-12-31')
        if not daily_data.empty:
            print(f"   成功获取 {len(daily_data)} 条日线数据")
            print("   最新5条记录:")
            print(daily_data.tail().to_string(index=False))
        else:
            print("   未能获取到日线数据")
    except Exception as e:
        print(f"   获取日线数据时出错: {e}")
    
    # 2. 使用默认数据源获取基本信息
    print("\n2. 使用Akshare获取基本信息:")
    try:
        basic_info = manager.get_stock_basic(stock_code)
        if basic_info:
            print("   基本信息:")
            for key, value in basic_info.items():
                print(f"     {key}: {value}")
        else:
            print("   未能获取到基本信息")
    except Exception as e:
        print(f"   获取基本信息时出错: {e}")
    
    # 3. 切换到Financial数据源
    print("\n3. 切换到Financial数据源:")
    manager.set_default_source('financial')
    print("   默认数据源已切换到Financial")
    
    # 4. 使用Financial数据源获取基本信息
    print("\n4. 使用Financial获取基本信息:")
    try:
        basic_info = manager.get_stock_basic(stock_code)
        if basic_info:
            print("   基本信息:")
            for key, value in basic_info.items():
                print(f"     {key}: {value}")
        else:
            print("   未能获取到基本信息")
    except Exception as e:
        print(f"   获取基本信息时出错: {e}")
    
    # 5. 使用Financial数据源获取财务数据
    print("\n5. 使用Financial获取财务数据:")
    try:
        financial_data = manager.get_financial_data(stock_code)
        if not financial_data.empty:
            print(f"   成功获取 {len(financial_data)} 条财务数据")
            print("   财务数据预览:")
            # 只显示部分重要列
            important_columns = ['股票代码', '股票简称', '公告日期', '营业收入', '净利润', '每股收益', '净资产收益率']
            display_columns = [col for col in important_columns if col in financial_data.columns]
            if display_columns:
                print(financial_data[display_columns].to_string(index=False))
            else:
                print(financial_data.head().to_string(index=False))
        else:
            print("   未能获取到财务数据")
    except Exception as e:
        print(f"   获取财务数据时出错: {e}")
    
    # 6. 数据源切换演示
    print("\n6. 数据源切换演示:")
    print("   切换回Akshare数据源获取基本信息:")
    try:
        basic_info_ak = manager.get_stock_basic(stock_code, source_type='akshare')
        if basic_info_ak:
            print("   Akshare获取的基本信息:")
            # 只显示部分信息
            keys_to_show = ['股票代码', '股票名称', '上市日期', '行业']
            for key in keys_to_show:
                if key in basic_info_ak:
                    print(f"     {key}: {basic_info_ak[key]}")
        else:
            print("   Akshare未能获取到基本信息")
    except Exception as e:
        print(f"   Akshare获取基本信息时出错: {e}")
    
    print("\n   使用Financial数据源获取基本信息:")
    try:
        basic_info_fin = manager.get_stock_basic(stock_code, source_type='financial')
        if basic_info_fin:
            print("   Financial获取的基本信息:")
            # 只显示部分信息
            keys_to_show = ['股票代码', '股票名称', '净利润', '总市值']
            for key in keys_to_show:
                if key in basic_info_fin:
                    print(f"     {key}: {basic_info_fin[key]}")
        else:
            print("   Financial未能获取到基本信息")
    except Exception as e:
        print(f"   Financial获取基本信息时出错: {e}")
    
    print("\n" + "=" * 70)
    print("演示完成")
    print("=" * 70)
    print("\n系统特点:")
    print("1. 统一接口: 通过UnifiedDataManager统一管理多种数据源")
    print("2. 灵活切换: 可以轻松在不同数据源之间切换")
    print("3. 数据标准化: 自动处理股票代码和日期格式标准化")
    print("4. 扩展性强: 支持添加新的数据源适配器")
    print("5. 错误处理: 完善的异常处理机制")


if __name__ == "__main__":
    main()