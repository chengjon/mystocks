"""
主程序入口
提供用户交互界面和示例用法

作用：
- 主程序入口，提供用户交互界面
- 创建统一数据管理器实例
- 处理用户输入和命令

功能：
- 展示数据和结果
- 提供示例用法和测试功能
- 作为系统的入口点，使用统一数据管理器来获取数据
"""
import pandas as pd
import sys
import os
import datetime

# 将当前目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mystocks.manager.unified_data_manager import UnifiedDataManager


def main():
    """主程序入口"""
    print("===== MyStocks 数据管理系统 =====")
    
    # 创建统一数据管理器
    manager = UnifiedDataManager()
    
    # 设置默认数据源
    manager.set_default_source('akshare')
    
    # 示例：获取股票数据
    print("\n===== 获取股票数据示例 =====")
    try:
        # 支持多种股票代码格式
        stock_data = manager.get_stock_daily("sh600000", "2023-01-01", "2023-01-10")
        print(f"获取到 {len(stock_data)} 行股票数据")
        if not stock_data.empty:
            print(stock_data.head())
    except Exception as e:
        print(f"获取股票数据失败: {e}")
    
    # 示例：获取指数数据
    print("\n===== 获取指数数据示例 =====")
    try:
        # 支持多种指数代码格式
        index_codes = ["sh000001", "sz399001"]
        for code in index_codes:
            print(f"\n尝试获取指数数据: {code}")
            index_data = manager.get_index_daily(code, "2023-01-01", "2023-01-10")
            print(f"获取到 {len(index_data)} 行指数数据")
            if not index_data.empty:
                print(index_data.head())
    except Exception as e:
        print(f"获取指数数据失败: {e}")
    
    # 示例：比较数据源
    print("\n===== 数据源比较示例 =====")
    try:
        manager.compare_data_sources("600000", "2023-01-01", "2023-01-10")
    except Exception as e:
        print(f"数据源比较失败: {e}")
    
    print("\n===== 程序结束 =====")


if __name__ == "__main__":
    main()