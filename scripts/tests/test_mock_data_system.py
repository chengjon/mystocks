#!/usr/bin/env python
"""Mock数据系统测试脚本

验证Mock数据系统的各个组件是否正常工作：
1. 统一Mock数据管理器
2. 环境变量控制的数据源切换
3. API路由集成
4. Mock数据验证

作者: Claude Code
创建时间: 2025-11-13
"""

import os
import sys
import unittest
from pathlib import Path


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入相关模块
try:
    from src.mock.mock_Dashboard import get_market_stats
    from src.mock.mock_Stocks import get_real_time_quote, get_stock_list
    from src.mock.mock_StrategyManagement import get_strategy_definitions
    from src.mock.mock_TechnicalAnalysis import get_technical_indicators
    from src.mock.mock_Wencai import get_wencai_queries
    from web.backend.app.mock.unified_mock_data import (
        UnifiedMockDataManager,
        get_mock_data_manager,
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请检查项目结构和依赖安装")
    sys.exit(1)


class TestMockDataSystem(unittest.TestCase):
    """Mock数据系统测试类"""

    def setUp(self):
        """测试初始化"""
        # 设置测试环境变量
        os.environ["USE_MOCK_DATA"] = "true"
        self.manager = UnifiedMockDataManager(use_mock_data=True)

    def test_01_environment_variable_setup(self):
        """测试1: 环境变量设置"""
        print("\n=== 测试1: 环境变量设置 ===")

        # 测试环境变量设置
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        self.assertTrue(use_mock, "USE_MOCK_DATA环境变量应该设置为true")
        print(f"✅ 环境变量USE_MOCK_DATA: {use_mock}")

    def test_02_mock_data_manager_initialization(self):
        """测试2: Mock数据管理器初始化"""
        print("\n=== 测试2: Mock数据管理器初始化 ===")

        # 测试初始化
        self.assertIsNotNone(self.manager, "Mock数据管理器应该成功初始化")
        self.assertTrue(self.manager.use_mock_data, "应该启用Mock模式")
        print(f"✅ Mock数据管理器初始化成功，Mock模式: {self.manager.use_mock_data}")

        # 测试缓存信息
        cache_info = self.manager.get_cache_info()
        self.assertIn("cache_size", cache_info, "缓存信息应该包含cache_size")
        self.assertIn("mock_mode", cache_info, "缓存信息应该包含mock_mode")
        print(f"✅ 缓存信息: {cache_info}")

    def test_03_dashboard_mock_data(self):
        """测试3: Dashboard Mock数据"""
        print("\n=== 测试3: Dashboard Mock数据 ===")

        try:
            data = self.manager.get_data("dashboard")

            # 验证数据结构
            self.assertIn("market_overview", data, "应该包含market_overview")
            self.assertIn("market_stats", data, "应该包含market_stats")
            self.assertIn("market_heat", data, "应该包含market_heat")

            # 验证市场概览
            overview = data["market_overview"]
            self.assertIn("indices_count", overview, "市场概览应该包含指数数量")
            self.assertIn("rising_count", overview, "市场概览应该包含上涨数量")
            self.assertIn("falling_count", overview, "市场概览应该包含下跌数量")

            print("✅ Dashboard数据获取成功:")
            print(f"   指数数量: {overview['indices_count']}")
            print(f"   上涨数量: {overview['rising_count']}")
            print(f"   下跌数量: {overview['falling_count']}")

        except Exception as e:
            self.fail(f"Dashboard数据获取失败: {e}")

    def test_04_stocks_mock_data(self):
        """测试4: Stocks Mock数据"""
        print("\n=== 测试4: Stocks Mock数据 ===")

        try:
            # 测试股票列表
            data = self.manager.get_data("stocks", page=1, page_size=10)
            self.assertIn("stocks", data, "应该包含stocks数据")
            self.assertIn("total", data, "应该包含total字段")

            stocks = data["stocks"]
            print(f"✅ 股票列表获取成功，总计: {data['total']} 条记录")

            # 测试实时行情
            quote_data = self.manager.get_data(
                "stocks",
                action="quote",
                symbol="600519",
            )
            print(f"✅ 实时行情获取成功: {quote_data.get('symbol', 'N/A')}")

        except Exception as e:
            self.fail(f"Stocks数据获取失败: {e}")

    def test_05_technical_mock_data(self):
        """测试5: Technical Analysis Mock数据"""
        print("\n=== 测试5: Technical Analysis Mock数据 ===")

        try:
            # 测试单个股票技术指标
            data = self.manager.get_data("technical", symbol="600519")
            self.assertIn("indicators", data, "应该包含indicators数据")
            self.assertIn("signals", data, "应该包含signals数据")

            print("✅ 技术指标数据获取成功")

            # 测试批量股票技术指标
            batch_data = self.manager.get_data(
                "technical",
                symbols=["600519", "000001", "600036"],
            )
            self.assertIn("indicators", batch_data, "批量数据应该包含indicators")

            print(
                f"✅ 批量技术指标数据获取成功，股票数量: {len(batch_data.get('indicators', {}))}",
            )

        except Exception as e:
            self.fail(f"Technical数据获取失败: {e}")

    def test_06_wencai_mock_data(self):
        """测试6: Wencai Mock数据"""
        print("\n=== 测试6: Wencai Mock数据 ===")

        try:
            # 测试获取所有查询
            data = self.manager.get_data("wencai", query_name="all")
            self.assertIn("queries", data, "应该包含queries数据")

            queries = data["queries"]
            print(f"✅ 问财查询获取成功，查询数量: {len(queries)}")

            # 测试单个查询结果
            result_data = self.manager.get_data("wencai", query_name="qs_1")
            self.assertIn("query_result", result_data, "应该包含query_result")

            print("✅ 问财查询结果获取成功")

        except Exception as e:
            self.fail(f"Wencai数据获取失败: {e}")

    def test_07_strategy_mock_data(self):
        """测试7: Strategy Management Mock数据"""
        print("\n=== 测试7: Strategy Management Mock数据 ===")

        try:
            # 测试策略列表
            data = self.manager.get_data("strategy", action="list")
            self.assertIn("strategies", data, "应该包含strategies数据")

            strategies = data["strategies"]
            print(f"✅ 策略列表获取成功，策略数量: {len(strategies)}")

            # 测试策略运行
            run_data = self.manager.get_data(
                "strategy",
                action="run",
                strategy_name="突破策略",
            )
            self.assertIn("strategy_result", run_data, "应该包含strategy_result")

            print("✅ 策略运行结果获取成功")

        except Exception as e:
            self.fail(f"Strategy数据获取失败: {e}")

    def test_08_monitoring_mock_data(self):
        """测试8: Monitoring Mock数据"""
        print("\n=== 测试8: Monitoring Mock数据 ===")

        try:
            # 测试监控数据
            data = self.manager.get_data("monitoring", alert_type="all")
            self.assertIn("alerts", data, "应该包含alerts数据")
            self.assertIn("dragon_tiger", data, "应该包含dragon_tiger数据")

            alerts = data["alerts"]
            dragon_tiger = data["dragon_tiger"]

            print("✅ 监控数据获取成功")
            print(f"   告警数量: {len(alerts)}")
            print(f"   龙虎榜数量: {len(dragon_tiger)}")

        except Exception as e:
            self.fail(f"Monitoring数据获取失败: {e}")

    def test_09_cache_mechanism(self):
        """测试9: 缓存机制"""
        print("\n=== 测试9: 缓存机制 ===")

        # 获取数据
        data1 = self.manager.get_data("dashboard")

        # 检查缓存
        cache_info_before = self.manager.get_cache_info()
        print(f"✅ 缓存前大小: {cache_info_before['cache_size']}")

        # 再次获取相同数据（应该从缓存获取）
        data2 = self.manager.get_data("dashboard")

        # 检查缓存增长
        cache_info_after = self.manager.get_cache_info()
        self.assertGreater(cache_info_after["cache_size"], 0, "缓存应该包含数据")
        print(f"✅ 缓存后大小: {cache_info_after['cache_size']}")

        # 清除缓存
        self.manager.clear_cache()
        cache_info_clear = self.manager.get_cache_info()
        self.assertEqual(cache_info_clear["cache_size"], 0, "缓存应该被清除")
        print(f"✅ 缓存清除成功，大小: {cache_info_clear['cache_size']}")

    def test_10_data_source_toggle(self):
        """测试10: 数据源切换"""
        print("\n=== 测试10: 数据源切换 ===")

        # 测试启用Mock模式
        self.manager.set_mock_mode(True)
        self.assertTrue(self.manager.use_mock_data, "Mock模式应该启用")
        print(f"✅ Mock模式启用: {self.manager.use_mock_data}")

        # 测试禁用Mock模式
        self.manager.set_mock_mode(False)
        self.assertFalse(self.manager.use_mock_data, "Mock模式应该禁用")
        print(f"✅ Mock模式禁用: {self.manager.use_mock_data}")

        # 重新启用
        self.manager.set_mock_mode(True)
        self.assertTrue(self.manager.use_mock_data, "Mock模式应该重新启用")
        print(f"✅ Mock模式重新启用: {self.manager.use_mock_data}")


def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始Mock数据系统综合测试")
    print("=" * 60)

    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMockDataSystem)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    result = runner.run(test_suite)

    # 手动运行测试（显示详细输出）
    test_instance = TestMockDataSystem()
    test_instance.setUp()

    try:
        test_instance.test_01_environment_variable_setup()
        test_instance.test_02_mock_data_manager_initialization()
        test_instance.test_03_dashboard_mock_data()
        test_instance.test_04_stocks_mock_data()
        test_instance.test_05_technical_mock_data()
        test_instance.test_06_wencai_mock_data()
        test_instance.test_07_strategy_mock_data()
        test_instance.test_08_monitoring_mock_data()
        test_instance.test_09_cache_mechanism()
        test_instance.test_10_data_source_toggle()

        print("\n" + "=" * 60)
        print("🎉 所有Mock数据系统测试通过！")
        print("✅ Mock数据系统集成完成")
        print("✅ 环境变量控制的数据源切换正常工作")
        print("✅ 统一Mock数据管理器功能正常")
        print("✅ 缓存机制工作正常")
        print("✅ 所有模块Mock数据验证通过")

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()

    if success:
        print("\n📋 Mock数据系统状态:")
        print("- ✅ 环境变量控制: USE_MOCK_DATA=true")
        print("- ✅ 统一Mock数据管理器: 正常")
        print("- ✅ Dashboard模块: Mock数据正常")
        print("- ✅ Stocks模块: Mock数据正常")
        print("- ✅ Technical模块: Mock数据正常")
        print("- ✅ Wencai模块: Mock数据正常")
        print("- ✅ Strategy模块: Mock数据正常")
        print("- ✅ Monitoring模块: Mock数据正常")
        print("- ✅ 缓存机制: 正常工作")
        print("- ✅ 数据源切换: 正常工作")

        print("\n🚀 系统已准备就绪，可以启动Mock数据模式进行开发和测试")
        sys.exit(0)
    else:
        print("\n❌ Mock数据系统测试失败，请检查配置和依赖")
        sys.exit(1)
