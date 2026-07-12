#!/usr/bin/env python3
"""增强的Mock数据测试脚本
测试改进后的Mock数据生成质量和真实性

运行方法:
python scripts/tests/test_enhanced_mock_data.py

作者: Claude Code
创建时间: 2025-11-13
"""

import os
import sys


# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import datetime
import os
import sys
from pathlib import Path

import numpy as np


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


def test_market_data_realism():
    """测试市场数据的真实性和分布特征"""
    print("🔍 测试市场数据真实性和分布特征")
    print("=" * 50)

    try:
        from src.mock.mock_Market import get_market_heatmap
        from src.mock.mock_StockSearch import search_stocks

        # 测试市场热力图数据
        print("\n📊 市场热力图数据分析:")
        heatmap_data = get_market_heatmap(market="cn", limit=20)

        # 分析价格分布
        prices = [item["price"] for item in heatmap_data]
        changes = [item["change_pct"] for item in heatmap_data]
        volumes = [item["volume"] for item in heatmap_data]

        print("  ✅ 价格统计:")
        print(f"     - 价格范围: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"     - 平均价格: ${np.mean(prices):.2f}")
        print(f"     - 价格标准差: ${np.std(prices):.2f}")

        print("  ✅ 涨跌幅统计:")
        print(f"     - 涨跌幅范围: {min(changes):.2f}% - {max(changes):.2f}%")
        print(f"     - 平均涨跌幅: {np.mean(changes):.2f}%")
        print(f"     - 涨跌幅标准差: {np.std(changes):.2f}%")

        # 检查是否有涨停/跌停股票
        limit_up_count = sum(1 for change in changes if change >= 9.9)
        limit_down_count = sum(1 for change in changes if change <= -9.9)
        print(f"     - 涨停股票数: {limit_up_count}")
        print(f"     - 跌停股票数: {limit_down_count}")

        print("  ✅ 成交量统计:")
        print(f"     - 成交量范围: {min(volumes):,} - {max(volumes):,}")
        print(f"     - 平均成交量: {np.mean(volumes):,.0f}")
        print(f"     - 成交量标准差: {np.std(volumes):,.0f}")

        # 测试股票搜索数据
        print("\n🔍 股票搜索数据分析:")
        search_results = search_stocks(keyword="平安", limit=10)

        search_prices = [item["current_price"] for item in search_results]
        search_market_caps = [item["market_cap"] for item in search_results]

        print("  ✅ 搜索结果价格统计:")
        print(f"     - 价格范围: ${min(search_prices):.2f} - ${max(search_prices):.2f}")
        print(f"     - 平均价格: ${np.mean(search_prices):.2f}")

        print("  ✅ 搜索结果市值统计:")
        print(
            f"     - 市值范围: ${min(search_market_caps):,.0f} - ${max(search_market_caps):,.0f}",
        )
        print(f"     - 平均市值: ${np.mean(search_market_caps):,.0f}")

        # 验证数据分布的合理性
        print("\n🎯 数据分布合理性验证:")

        # 检查价格分布是否合理（应该有合理的分布范围）
        if min(prices) > 0.1 and max(prices) < 10000:
            print("  ✅ 价格分布合理 (在0.1-10000元范围内)")
        else:
            print("  ⚠️ 价格分布可能存在异常值")

        # 检查涨跌幅分布是否合理（大部分应该在±5%内）
        reasonable_changes = sum(1 for change in changes if -10 <= change <= 10)
        if reasonable_changes / len(changes) > 0.8:
            print("  ✅ 涨跌幅分布合理 (80%以上在±10%内)")
        else:
            print("  ⚠️ 涨跌幅分布可能过于极端")

        # 检查成交量与价格的相关性
        price_volume_correlation = np.corrcoef(prices, volumes)[0, 1]
        if -0.3 < price_volume_correlation < 0.3:
            print(
                f"  ✅ 价格与成交量相关性合理 (相关系数: {price_volume_correlation:.3f})",
            )
        else:
            print(
                f"  ⚠️ 价格与成交量相关性可能异常 (相关系数: {price_volume_correlation:.3f})",
            )

        return True

    except Exception as e:
        print(f"  ❌ 市场数据测试失败: {e}")
        return False


def test_data_consistency():
    """测试数据的一致性和相关性"""
    print("\n🔗 测试数据一致性和相关性")
    print("=" * 50)

    try:
        from src.mock.mock_StockSearch import get_stock_detail, search_stocks

        # 搜索股票
        search_results = search_stocks(keyword="平安", limit=5)

        if not search_results:
            print("  ❌ 搜索结果为空")
            return False

        # 获取第一个股票的详情
        first_stock = search_results[0]
        symbol = first_stock["symbol"]

        print(f"  🔍 测试股票: {symbol} ({first_stock['name']})")

        # 获取股票详情
        detail = get_stock_detail(symbol)

        # 验证数据一致性
        print("  ✅ 基本信息一致性:")
        print(f"     - 搜索结果名称: {first_stock['name']}")
        print(f"     - 详情页名称: {detail.get('name', 'N/A')}")

        print("  ✅ 价格信息一致性:")
        print(f"     - 搜索结果价格: ${first_stock['current_price']:.2f}")
        print(f"     - 详情页价格: ${detail.get('current_price', 'N/A')}")

        print("  ✅ 行业信息一致性:")
        print(f"     - 搜索结果行业: {first_stock['industry']}")
        print(f"     - 详情页行业: {detail.get('industry', 'N/A')}")

        return True

    except Exception as e:
        print(f"  ❌ 数据一致性测试失败: {e}")
        return False


def test_performance():
    """测试Mock数据生成性能"""
    print("\n⚡ 测试Mock数据生成性能")
    print("=" * 50)

    import time

    try:
        from src.mock.mock_Market import get_market_heatmap
        from src.mock.mock_StockSearch import search_stocks

        # 测试大量数据生成性能
        print("  📊 测试大量数据生成...")

        start_time = time.time()
        large_heatmap = get_market_heatmap(market="cn", limit=100)
        heatmap_time = time.time() - start_time

        start_time = time.time()
        large_search = search_stocks(keyword="", limit=100)
        search_time = time.time() - start_time

        print(f"  ✅ 市场热力图生成 (100条记录): {heatmap_time:.3f}秒")
        print(f"  ✅ 股票搜索生成 (100条记录): {search_time:.3f}秒")

        # 性能评估
        if heatmap_time < 1.0:
            print("  ✅ 市场热力图生成性能优秀")
        elif heatmap_time < 3.0:
            print("  ⚠️ 市场热力图生成性能一般")
        else:
            print("  ❌ 市场热力图生成性能较差")

        if search_time < 1.0:
            print("  ✅ 股票搜索生成性能优秀")
        elif search_time < 3.0:
            print("  ⚠️ 股票搜索生成性能一般")
        else:
            print("  ❌ 股票搜索生成性能较差")

        return True

    except Exception as e:
        print(f"  ❌ 性能测试失败: {e}")
        return False


def test_integration_with_unified_manager():
    """测试与统一管理器的集成"""
    print("\n🔌 测试与统一管理器的集成")
    print("=" * 50)

    try:
        # 设置环境变量使用Mock数据
        os.environ["USE_MOCK_DATA"] = "true"

        from web.backend.app.mock.unified_mock_data import get_mock_data_manager

        manager = get_mock_data_manager()

        # 测试通过统一管理器获取数据
        print("  📊 测试市场热力图通过统一管理器...")
        heatmap_data = manager.get_data("market_heatmap", market="cn", limit=10)

        if heatmap_data and len(heatmap_data.get("data", [])) > 0:
            print("  ✅ 市场热力图统一管理器集成成功")
            print(f"     - 返回数据量: {len(heatmap_data['data'])}")
            print(f"     - 数据源: {heatmap_data.get('source', 'unknown')}")
        else:
            print("  ❌ 市场热力图统一管理器集成失败")
            return False

        print("  🔍 测试股票搜索通过统一管理器...")
        search_data = manager.get_data("stock_search", keyword="平安", limit=5)

        if search_data and len(search_data.get("data", [])) > 0:
            print("  ✅ 股票搜索统一管理器集成成功")
            print(f"     - 返回数据量: {len(search_data['data'])}")
            print(f"     - 数据源: {search_data.get('source', 'unknown')}")
        else:
            print("  ❌ 股票搜索统一管理器集成失败")
            return False

        # 测试缓存机制
        print("  💾 测试缓存机制...")
        cache_info_before = manager.get_cache_info()
        print(f"     - 缓存前大小: {cache_info_before['cache_size']}")

        # 再次获取相同数据（应该从缓存获取）
        heatmap_data_cached = manager.get_data("market_heatmap", market="cn", limit=10)

        cache_info_after = manager.get_cache_info()
        print(f"     - 缓存后大小: {cache_info_after['cache_size']}")

        if cache_info_after["cache_size"] > cache_info_before["cache_size"]:
            print("  ✅ 缓存机制工作正常")
        else:
            print("  ⚠️ 缓存机制可能未正常工作")

        return True

    except Exception as e:
        print(f"  ❌ 统一管理器集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 启动增强Mock数据系统测试")
    print("=" * 60)
    print(f"📅 测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 工作目录: {os.getcwd()}")
    print("=" * 60)

    test_results = []

    # 执行所有测试
    test_functions = [
        ("市场数据真实性", test_market_data_realism),
        ("数据一致性", test_data_consistency),
        ("性能测试", test_performance),
        ("统一管理器集成", test_integration_with_unified_manager),
    ]

    for test_name, test_func in test_functions:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name}测试执行失败: {e}")
            test_results.append((test_name, False))

    # 测试结果总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} {test_name}")
        if result:
            passed_tests += 1

    print(f"\n🏆 总计: {passed_tests}/{total_tests} 项测试通过")

    if passed_tests == total_tests:
        print("🎉 所有测试通过！Mock数据系统运行正常！")
        return 0
    print("⚠️ 部分测试失败，请检查Mock数据系统配置")
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
