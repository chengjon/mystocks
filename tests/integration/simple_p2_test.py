#!/usr/bin/env python3
"""
简化的P2模块API测试脚本
测试数据源工厂模式的核心功能
"""

import asyncio
import json
import sys
from datetime import datetime

import aiohttp

# Add project root to Python path
sys.path.insert(0, "/opt/claude/mystocks_spec")


async def test_data_source_factory():
    """直接测试数据源工厂功能"""
    print("🧪 直接测试数据源工厂功能...")

    try:
        # Import and test the data source factory directly
        sys.path.insert(0, "/opt/claude/mystocks_spec/web/backend")
        from app.services.data_source_factory import DataSourceFactory

        factory = DataSourceFactory()

        # Test Technical Analysis adapter
        print("\n📊 测试 Technical Analysis 适配器...")
        tech_adapter = await factory.get_data_source("technical")
        if tech_adapter:
            # Test indicators registry
            result = await tech_adapter.get_data("registry", {})
            print("  ✅ Technical Analysis 适配器初始化成功")
            print(f"  📈 Registry 测试: {result.get('success', False)}")
            if result.get("success"):
                print(f"  📊 数据点数: {len(result.get('data', []))}")
        else:
            print("  ❌ Technical Analysis 适配器初始化失败")

        # Test Strategy adapter
        print("\n🎯 测试 Strategy 适配器...")
        strategy_adapter = await factory.get_data_source("strategy")
        if strategy_adapter:
            # Test strategy definitions
            result = await strategy_adapter.get_data("definitions", {})
            print("  ✅ Strategy 适配器初始化成功")
            print(f"  📈 Definitions 测试: {result.get('success', False)}")
            if result.get("success"):
                print(f"  📊 策略数量: {len(result.get('data', []))}")
        else:
            print("  ❌ Strategy 适配器初始化失败")

        # Test Watchlist adapter
        print("\n📋 测试 Watchlist 适配器...")
        watchlist_adapter = await factory.get_data_source("watchlist")
        if watchlist_adapter:
            # Test watchlist list
            result = await watchlist_adapter.get_data("list", {"user_id": 1})
            print("  ✅ Watchlist 适配器初始化成功")
            print(f"  📈 List 测试: {result.get('success', False)}")
            if result.get("success"):
                print(f"  📊 自选股数量: {len(result.get('data', []))}")
        else:
            print("  ❌ Watchlist 适配器初始化失败")

        return True

    except Exception as e:
        print(f"❌ 数据源工厂测试失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_mock_data_manager():
    """测试Mock数据管理器"""
    print("\n🎭 测试 Mock 数据管理器...")

    try:
        sys.path.insert(0, "/opt/claude/mystocks_spec/web/backend")
        from app.mock.unified_mock_data import get_mock_data_manager

        mock_manager = get_mock_data_manager()

        # Test technical data
        print("  📊 测试技术指标数据...")
        tech_data = mock_manager.get_data("technical", symbol="000001")
        print(f"    ✅ 技术指标数据: {len(tech_data.get('indicators', {}))} 个指标")

        # Test strategy data
        print("  🎯 测试策略数据...")
        strategy_data = mock_manager.get_data("strategy", action="definitions")
        print(f"    ✅ 策略定义: {len(strategy_data.get('data', []))} 个策略")

        # Test watchlist data
        print("  📋 测试自选股数据...")
        watchlist_data = mock_manager.get_data("watchlist", action="list", user_id=1)
        print(f"    ✅ 自选股列表: {len(watchlist_data.get('data', []))} 只股票")

        return True

    except Exception as e:
        print(f"❌ Mock数据管理器测试失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_api_connectivity():
    """测试API连接性（简单健康检查）"""
    print("\n🌐 测试 API 连接性...")

    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(
                "http://localhost:8000/health", timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"  ✅ 健康检查: {health_data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"  ❌ 健康检查失败: HTTP {response.status}")
                    return False

    except Exception as e:
        print(f"  ⚠️  API连接测试失败: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始 P2模块简化测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    results = {
        "data_source_factory": False,
        "mock_data_manager": False,
        "api_connectivity": False,
    }

    # 1. 测试数据源工厂
    results["data_source_factory"] = await test_data_source_factory()

    # 2. 测试Mock数据管理器
    results["mock_data_manager"] = await test_mock_data_manager()

    # 3. 测试API连接性
    results["api_connectivity"] = await test_api_connectivity()

    # 生成测试报告
    print("\n📊 测试结果总结:")
    print("=" * 50)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n🎯 总体结果: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 P2模块数据源工厂模式测试通过!")
    else:
        print("⚠️  部分测试失败，需要进一步检查")

    # 保存测试报告
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "P2模块简化测试",
        "results": results,
        "summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": success_rate,
        },
    }

    with open(
        "/opt/claude/mystocks_spec/docs/api/P2_SIMPLIFIED_TEST_REPORT.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("📄 测试报告已保存到: docs/api/P2_SIMPLIFIED_TEST_REPORT.json")

    return results


if __name__ == "__main__":
    asyncio.run(main())
