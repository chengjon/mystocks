#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX增强功能测试脚本

测试新增的K线周期和板块数据功能。

@author: MyStocks Project
@version: 1.0
@created: 2026-01-02
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.adapters.tdx_adapter import TdxDataSource


def test_extended_kline_periods():
    """测试扩展的K线周期"""
    print("\n" + "=" * 70)
    print("测试1: 扩展的K线周期 (周/月/季/年)")
    print("=" * 70)

    try:
        tdx = TdxDataSource()

        # 测试股票代码
        test_symbol = "600519"  # 贵州茅台

        # 计算日期范围（最近2年）
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

        # 测试新周期
        new_periods = [
            ('1w', '周线'),
            ('1M', '月线'),
            ('1q', '季线'),
            ('1y', '年线')
        ]

        print(f"\n测试股票: {test_symbol}")
        print(f"日期范围: {start_date} 至 {end_date}")
        print("\n测试结果:")

        for period_code, period_name in new_periods:
            try:
                print(f"\n  【{period_name}】获取中...")
                df = tdx.get_stock_kline(test_symbol, start_date, end_date, period=period_code)

                if not df.empty:
                    print(f"    ✅ 成功! 获取 {len(df)} 条数据")
                    print(f"    日期范围: {df['date'].min()} 至 {df['date'].max()}")
                    print(f"    价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
                else:
                    print("    ⚠️  无数据返回")

            except Exception as e:
                print(f"    ❌ 失败: {e}")

        print("\n" + "-" * 70)
        print("测试1完成!")

    except Exception as e:
        print(f"❌ 测试1失败: {e}")


def test_index_extended_periods():
    """测试指数扩展的K线周期"""
    print("\n" + "=" * 70)
    print("测试2: 指数扩展K线周期")
    print("=" * 70)

    try:
        tdx = TdxDataSource()

        # 测试指数代码
        test_index = "000001"  # 上证指数

        # 计算日期范围
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n测试指数: {test_index} (上证指数)")
        print(f"日期范围: {start_date} 至 {end_date}")

        # 测试周线和月线
        for period_code, period_name in [('1w', '周线'), ('1M', '月线')]:
            try:
                print(f"\n  【指数{period_name}】获取中...")
                df = tdx.get_index_kline(test_index, start_date, end_date, period=period_code)

                if not df.empty:
                    print(f"    ✅ 成功! 获取 {len(df)} 条数据")
                    print(f"    日期范围: {df['date'].min()} 至 {df['date'].max()}")
                else:
                    print("    ⚠️  无数据返回")

            except Exception as e:
                print(f"    ❌ 失败: {e}")

        print("\n" + "-" * 70)
        print("测试2完成!")

    except Exception as e:
        print(f"❌ 测试2失败: {e}")


def test_block_data():
    """测试板块数据功能"""
    print("\n" + "=" * 70)
    print("测试3: 板块数据功能")
    print("=" * 70)

    try:
        tdx = TdxDataSource()

        # 检查环境变量
        tdx_path = os.getenv('TDX_DATA_PATH')
        if not tdx_path:
            print("\n⚠️  环境变量 TDX_DATA_PATH 未设置")
            print("   请设置通达信数据路径:")
            print("   export TDX_DATA_PATH=/mnt/d/ProgramData/tdx_new")
            print("\n跳过板块数据测试...")
            return

        print(f"\nTDX路径: {tdx_path}")

        # 测试获取概念板块
        print("\n  【概念板块】获取中...")
        try:
            df_concept = tdx.get_block_data(block_type='concept')

            if not df_concept.empty:
                print(f"    ✅ 成功! 获取 {len(df_concept)} 条记录")
                print(f"    板块数量: {df_concept['blockname'].nunique()}")

                # 显示前5个板块
                print("\n    前5个概念板块:")
                top_blocks = df_concept['blockname'].unique()[:5]
                for i, block in enumerate(top_blocks, 1):
                    stock_count = len(df_concept[df_concept['blockname'] == block])
                    print(f"      {i}. {block} ({stock_count}只股票)")
            else:
                print("    ⚠️  无数据返回")

        except Exception as e:
            print(f"    ❌ 失败: {e}")

        # 测试获取股票所属板块
        print("\n  【股票板块查询】获取中...")
        test_stock = "600519"  # 贵州茅台
        try:
            blocks = tdx.get_stock_blocks(test_stock)

            if blocks:
                print(f"    ✅ 成功! {test_stock} 属于 {len(blocks)} 个板块")
                print("\n    前10个板块:")
                for i, block in enumerate(blocks[:10], 1):
                    print(f"      {i}. {block['blockname']} ({block['block_type']})")
            else:
                print("    ⚠️  未找到板块信息")

        except Exception as e:
            print(f"    ❌ 失败: {e}")

        # 测试获取板块包含的股票
        print("\n  【板块股票查询】获取中...")
        test_block = "白酒"
        try:
            stocks = tdx.get_block_stocks(test_block)

            if stocks:
                print(f"    ✅ 成功! {test_block}板块包含 {len(stocks)} 只股票")
                print(f"    前10只股票: {stocks[:10]}")
            else:
                print(f"    ⚠️  未找到板块: {test_block}")

        except Exception as e:
            print(f"    ❌ 失败: {e}")

        print("\n" + "-" * 70)
        print("测试3完成!")

    except Exception as e:
        print(f"❌ 测试3失败: {e}")


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("     TDX增强功能测试")
    print("     测试时间: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("=" * 70)

    # 运行所有测试
    test_extended_kline_periods()
    test_index_extended_periods()
    test_block_data()

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print("\n✅ 已完成测试:")
    print("  1. 扩展K线周期 (周/月/季/年)")
    print("  2. 指数扩展K线周期")
    print("  3. 板块数据功能")
    print("\n📊 功能覆盖率提升:")
    print("  • K线周期: 6种 → 10种 (+67%)")
    print("  • 板块数据: 0种 → 4种 (+∞)")
    print("\n💡 使用建议:")
    print("  • 周线/月线: 适合长期投资分析")
    print("  • 季线/年线: 适合超长期趋势分析")
    print("  • 板块数据: 适合板块轮动策略")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
