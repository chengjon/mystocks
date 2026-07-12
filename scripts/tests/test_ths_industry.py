#!/usr/bin/env python
"""测试同花顺行业一览表数据获取功能

该脚本用于测试新添加的同花顺行业数据获取功能，包括：
1. 获取同花顺行业一览表
2. 获取指定行业的成分股数据
"""

import os
import sys


# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import os
import sys

import pandas as pd


# 添加项目路径到模块搜索路径
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from src.adapters.akshare_adapter import AkshareDataSource


def test_ths_industry_summary():
    """测试获取同花顺行业一览表数据"""
    print("=" * 60)
    print("测试获取同花顺行业一览表数据")
    print("=" * 60)

    try:
        # 初始化Akshare数据源
        adapter = AkshareDataSource()

        # 获取同花顺行业一览表数据
        industry_data = adapter.get_ths_industry_summary()

        if not industry_data.empty:
            print(f"✅ 成功获取同花顺行业数据: {len(industry_data)}行")
            print(f"📊 数据列名: {industry_data.columns.tolist()}")
            print("\n📈 前5行数据预览:")
            print(industry_data.head())
            print(f"\n💾 数据形状: {industry_data.shape}")

            # 保存到CSV文件
            output_file = "ths_industry_summary.csv"
            industry_data.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"💾 数据已保存到: {output_file}")

            return industry_data
        print("❌ 未能获取到同花顺行业数据")
        return pd.DataFrame()

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def test_ths_industry_names():
    """测试获取同花顺行业名称列表"""
    print("=" * 60)
    print("测试获取同花顺行业名称列表")
    print("=" * 60)

    try:
        # 初始化Akshare数据源
        adapter = AkshareDataSource()

        # 获取同花顺行业名称列表
        industry_names = adapter.get_ths_industry_names()

        if not industry_names.empty:
            print(f"✅ 成功获取同花顺行业名称列表: {len(industry_names)}行")
            print(f"📊 数据列名: {industry_names.columns.tolist()}")
            print("\n📈 前10行数据预览:")
            print(industry_names.head(10))
            print(f"\n💾 数据形状: {industry_names.shape}")

            # 保存到CSV文件
            output_file = "ths_industry_names.csv"
            industry_names.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"💾 数据已保存到: {output_file}")

            return industry_names
        print("❌ 未能获取到同花顺行业名称列表")
        return pd.DataFrame()

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def test_ths_industry_stocks(industry_name: str = "银行"):
    """测试获取指定行业的成分股数据"""
    print("=" * 60)
    print(f"测试获取同花顺行业'{industry_name}'成分股数据")
    print("=" * 60)

    try:
        # 初始化Akshare数据源
        adapter = AkshareDataSource()

        # 获取指定行业的成分股数据
        stocks_data = adapter.get_ths_industry_stocks(industry_name)

        if not stocks_data.empty:
            print(f"✅ 成功获取行业'{industry_name}'成分股数据: {len(stocks_data)}行")
            print(f"📊 数据列名: {stocks_data.columns.tolist()}")
            print("\n📈 前10行数据预览:")
            print(stocks_data.head(10))
            print(f"\n💾 数据形状: {stocks_data.shape}")

            # 保存到CSV文件
            output_file = f"ths_industry_stocks_{industry_name}.csv"
            stocks_data.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"💾 数据已保存到: {output_file}")

            return stocks_data
        print(f"❌ 未能获取到行业'{industry_name}'的成分股数据")
        return pd.DataFrame()

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def main():
    """主测试函数"""
    print("🚀 开始测试同花顺行业数据获取功能")
    print("=" * 80)

    # 测试1: 获取行业一览表
    industry_summary = test_ths_industry_summary()

    print("\n" + "=" * 80)

    # 测试2: 获取行业名称列表
    industry_names = test_ths_industry_names()

    print("\n" + "=" * 80)

    # 测试3: 获取银行行业成分股
    if not industry_summary.empty:
        # 从行业列表中选择第一个行业进行测试
        if "板块" in industry_summary.columns:
            first_industry = industry_summary["板块"].iloc[0]
            print(f"🎯 将测试第一个行业: {first_industry}")
            test_ths_industry_stocks(first_industry)
        else:
            # 如果列名不是'板块'，则使用默认的'银行'
            test_ths_industry_stocks("银行")
    else:
        # 如果获取行业列表失败，则使用默认行业测试
        test_ths_industry_stocks("银行")

    print("\n" + "=" * 80)
    print("✅ 测试完成！")


if __name__ == "__main__":
    main()
