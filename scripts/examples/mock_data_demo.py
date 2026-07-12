#!/usr/bin/env python3
"""Mock数据系统演示脚本
展示如何使用增强后的Mock数据系统进行开发和测试

运行方法:
python examples/mock_data_demo.py

作者: Claude Code
创建时间: 2025-11-13
"""

import os
import sys
from pathlib import Path


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def demo_basic_usage():
    """演示基本使用方法"""
    print("🎯 Mock数据系统基本使用方法")
    print("=" * 50)

    # 设置环境变量使用Mock数据
    os.environ["USE_MOCK_DATA"] = "true"

    try:
        from web.backend.app.mock.unified_mock_data import get_mock_data_manager

        # 创建Mock数据管理器
        manager = get_mock_data_manager()
        print("✅ Mock数据管理器创建成功")

        # 获取市场热力图数据
        print("\n📊 获取市场热力图数据:")
        heatmap_data = manager.get_data("market_heatmap", market="cn", limit=5)

        if heatmap_data and heatmap_data.get("data"):
            print(f"   获取到 {len(heatmap_data['data'])} 只股票:")
            for stock in heatmap_data["data"][:3]:  # 只显示前3只
                print(
                    f"   - {stock['name']}({stock['symbol']}): ¥{stock['price']:.2f} ({stock['change_pct']:+.2f}%)",
                )
        else:
            print("   ❌ 获取市场热力图数据失败")

        # 搜索股票
        print("\n🔍 搜索股票:")
        search_data = manager.get_data("stock_search", keyword="平安", limit=3)

        if search_data and search_data.get("data"):
            print(f"   搜索到 {len(search_data['data'])} 只股票:")
            for stock in search_data["data"]:
                print(
                    f"   - {stock['description']}({stock['symbol']}) - {stock.get('exchange', 'N/A')}",
                )
        else:
            print("   ❌ 搜索股票失败")

        # 获取TradingView配置
        print("\n📈 获取TradingView图表配置:")
        chart_data = manager.get_data(
            "tradingview_chart",
            symbol="000001",
            market="CN",
            theme="dark",
        )

        if chart_data and chart_data.get("config"):
            config = chart_data["config"]
            print("   ✅ TradingView配置生成成功:")
            print(f"   - 容器ID: {config.get('container_id')}")
            print(f"   - 股票代码: {config.get('symbol')}")
            print(f"   - 主题: {config.get('theme')}")
            print(f"   - 语言: {config.get('locale')}")
        else:
            print("   ❌ 获取TradingView配置失败")

        return True

    except Exception as e:
        print(f"   ❌ 基本使用演示失败: {e}")
        return False


def demo_data_source_switching():
    """演示数据源切换"""
    print("\n🔄 数据源切换演示")
    print("=" * 50)

    try:
        from web.backend.app.mock.unified_mock_data import get_mock_data_manager

        manager = get_mock_data_manager()

        # 当前模式
        print(f"当前Mock模式: {'启用' if manager.use_mock_data else '禁用'}")

        # 切换到Mock模式
        print("\n🔄 切换到Mock模式...")
        manager.set_mock_mode(True)
        mock_data = manager.get_data("market_heatmap", market="cn", limit=3)
        print(f"Mock数据源标识: {mock_data.get('source', 'unknown')}")

        # 切换到真实数据模式
        print("\n🔄 尝试切换到真实数据模式...")
        manager.set_mock_mode(False)
        try:
            real_data = manager.get_data("market_heatmap", market="cn", limit=3)
            print(f"真实数据源标识: {real_data.get('source', 'unknown')}")
        except NotImplementedError:
            print("ℹ️ 真实数据模式尚未实现，自动降级到Mock数据")
            manager.set_mock_mode(True)

        # 缓存管理
        print("\n💾 缓存管理演示:")
        cache_info = manager.get_cache_info()
        print(f"   缓存大小: {cache_info['cache_size']}")
        print(f"   缓存TTL: {cache_info['cache_ttl']}秒")
        print(f"   当前模式: {'Mock' if cache_info['mock_mode'] else '真实数据'}")

        # 清除缓存
        manager.clear_cache()
        print("   ✅ 缓存已清除")

        return True

    except Exception as e:
        print(f"   ❌ 数据源切换演示失败: {e}")
        return False


def demo_performance_testing():
    """演示性能测试"""
    print("\n⚡ Mock数据性能测试")
    print("=" * 50)

    import time

    try:
        from src.mock.mock_Market import get_market_heatmap
        from src.mock.mock_StockSearch import search_stocks

        # 测试大量数据生成
        print("📊 测试大量数据生成性能...")

        start_time = time.time()
        large_data = get_market_heatmap(market="cn", limit=200)
        heatmap_time = time.time() - start_time

        print(f"   ✅ 生成200条市场数据耗时: {heatmap_time:.3f}秒")
        print(f"   ✅ 平均每条数据耗时: {heatmap_time / 200 * 1000:.2f}毫秒")

        # 测试搜索性能
        start_time = time.time()
        search_results = search_stocks(keyword="", limit=100)
        search_time = time.time() - start_time

        print(f"   ✅ 搜索100只股票耗时: {search_time:.3f}秒")
        print(f"   ✅ 平均每次搜索耗时: {search_time / 100 * 1000:.2f}毫秒")

        # 性能评估
        if heatmap_time < 0.1:
            print("   🏆 市场数据生成性能: 优秀")
        elif heatmap_time < 1.0:
            print("   👍 市场数据生成性能: 良好")
        else:
            print("   ⚠️ 市场数据生成性能: 需要优化")

        if search_time < 0.1:
            print("   🏆 股票搜索性能: 优秀")
        elif search_time < 1.0:
            print("   👍 股票搜索性能: 良好")
        else:
            print("   ⚠️ 股票搜索性能: 需要优化")

        return True

    except Exception as e:
        print(f"   ❌ 性能测试失败: {e}")
        return False


def demo_realistic_data():
    """演示真实数据特征"""
    print("\n📈 Mock数据真实性演示")
    print("=" * 50)

    try:
        from src.mock.mock_Market import get_market_heatmap

        # 生成市场数据
        market_data = get_market_heatmap(market="cn", limit=20)

        # 分析数据特征
        if not market_data:
            print("   ❌ 无法生成市场数据")
            return False

        prices = [item["price"] for item in market_data]
        changes = [item["change_pct"] for item in market_data]
        volumes = [item["volume"] for item in market_data]

        print("   📊 数据统计特征:")
        print(f"   - 价格分布: ¥{min(prices):.2f} - ¥{max(prices):.2f}")
        print(f"   - 价格平均: ¥{sum(prices) / len(prices):.2f}")
        print(f"   - 涨跌幅分布: {min(changes):.2f}% - {max(changes):.2f}%")
        print(f"   - 涨跌幅平均: {sum(changes) / len(changes):.2f}%")

        # 检查涨停跌停
        limit_up = [p for p in prices if any(s["change_pct"] >= 9.9 for s in market_data if s["price"] == p)]
        limit_down = [p for p in prices if any(s["change_pct"] <= -9.9 for s in market_data if s["price"] == p)]

        print(f"   📈 涨停股票数: {len(limit_up)}")
        print(f"   📉 跌停股票数: {len(limit_down)}")

        # 显示前5只股票
        print("   📋 前5只股票详情:")
        for i, stock in enumerate(market_data[:5], 1):
            print(f"   {i}. {stock['name']}({stock['symbol']}): ¥{stock['price']:.2f}")
            print(
                f"      涨跌: {stock['change_pct']:+.2f}% 成交量: {stock['volume']:,}",
            )

        return True

    except Exception as e:
        print(f"   ❌ 真实数据演示失败: {e}")
        return False


def main():
    """主演示函数"""
    print("🚀 MyStocks Mock数据系统演示")
    print("=" * 60)
    print("🎯 本演示展示如何使用Mock数据系统进行开发和测试")
    print(
        "📅 演示时间:",
        __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    print("=" * 60)

    # 设置使用Mock数据
    os.environ["USE_MOCK_DATA"] = "true"

    # 执行演示
    demos = [
        ("基本使用方法", demo_basic_usage),
        ("数据源切换", demo_data_source_switching),
        ("性能测试", demo_performance_testing),
        ("真实数据特征", demo_realistic_data),
    ]

    success_count = 0
    for demo_name, demo_func in demos:
        try:
            print(f"\n🎬 开始演示: {demo_name}")
            result = demo_func()
            if result:
                print(f"✅ {demo_name}演示成功")
                success_count += 1
            else:
                print(f"❌ {demo_name}演示失败")
        except Exception as e:
            print(f"❌ {demo_name}演示异常: {e}")

    # 总结
    print("\n" + "=" * 60)
    print("📊 演示总结")
    print("=" * 60)
    print(f"✅ 成功演示: {success_count}/{len(demos)} 项")

    if success_count == len(demos):
        print("🎉 所有演示成功！Mock数据系统运行正常！")
        print("\n💡 使用建议:")
        print("1. 开发阶段设置 USE_MOCK_DATA=true")
        print("2. 使用统一管理器获取Mock数据")
        print("3. 利用缓存机制提高性能")
        print("4. 根据需要进行数据源切换")
    else:
        print("⚠️ 部分演示失败，请检查系统配置")

    print("\n🔗 相关文档:")
    print("- 详细报告: docs/ARCHITECTURE/MOCK_DATA_COVERAGE_REPORT.md")
    print("- 快速参考: docs/ARCHITECTURE/MOCK_DATA_QUICK_REFERENCE.md")
    print("- 测试脚本: scripts/tests/test_enhanced_mock_data.py")


if __name__ == "__main__":
    main()
