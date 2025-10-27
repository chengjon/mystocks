#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks API 端点自动化测试脚本

测试所有核心API端点的可用性和响应格式

创建日期: 2025-10-25
版本: 1.0.0
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from examples.api_client_sdk import MyStocksClient, APIException
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIEndpointTester:
    """API端点测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化测试器

        Args:
            base_url: API服务器地址
        """
        self.client = MyStocksClient(base_url=base_url)
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'tests': []
        }

    def run_test(self, test_name: str, test_func):
        """
        运行单个测试

        Args:
            test_name: 测试名称
            test_func: 测试函数
        """
        print(f"\n{'=' * 70}")
        print(f"测试: {test_name}")
        print(f"{'=' * 70}")

        try:
            result = test_func()

            if result:
                print(f"✅ 通过: {test_name}")
                self.test_results['passed'] += 1
                self.test_results['tests'].append({
                    'name': test_name,
                    'status': 'PASSED',
                    'message': None
                })
            else:
                print(f"⚠️  跳过: {test_name}")
                self.test_results['skipped'] += 1
                self.test_results['tests'].append({
                    'name': test_name,
                    'status': 'SKIPPED',
                    'message': 'Test returned False'
                })

        except Exception as e:
            print(f"❌ 失败: {test_name}")
            print(f"   错误: {str(e)}")
            self.test_results['failed'] += 1
            self.test_results['tests'].append({
                'name': test_name,
                'status': 'FAILED',
                'message': str(e)
            })

    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client._get("/health", require_auth=False)
        assert 'status' in response, "响应缺少status字段"
        assert response['status'] == 'healthy', f"系统状态不健康: {response['status']}"
        print(f"   系统状态: {response['status']}")
        return True

    def test_authentication(self):
        """测试认证流程"""
        # 登录
        login_response = self.client.login("admin", "admin123")
        assert 'access_token' in login_response, "登录响应缺少access_token"
        print(f"   登录成功，Token长度: {len(login_response['access_token'])}")

        # 获取当前用户信息
        user_info = self.client._get("/api/auth/me")
        assert 'username' in user_info, "用户信息缺少username字段"
        print(f"   当前用户: {user_info['username']}")

        return True

    def test_stocks_basic(self):
        """测试股票基本信息查询"""
        stocks = self.client.get_stocks_basic(limit=5, market="SH")
        assert 'data' in stocks, "响应缺少data字段"
        assert isinstance(stocks['data'], list), "data字段不是列表"
        print(f"   查询到 {len(stocks['data'])} 只股票")

        if len(stocks['data']) > 0:
            stock = stocks['data'][0]
            print(f"   示例: {stock.get('symbol')} - {stock.get('name')}")

        return True

    def test_daily_kline(self):
        """测试日线数据查询"""
        kline = self.client.get_daily_kline(
            symbol="600519.SH",
            start_date="2024-01-01",
            limit=5
        )
        assert 'data' in kline, "响应缺少data字段"
        print(f"   查询到 {len(kline['data'])} 条K线数据")

        if len(kline['data']) > 0:
            bar = kline['data'][0]
            print(f"   示例: 日期={bar.get('date')}, 收盘={bar.get('close')}")

        return True

    def test_stock_search(self):
        """测试股票搜索"""
        result = self.client.search_stocks("茅台", limit=3)
        assert 'data' in result, "响应缺少data字段"
        print(f"   搜索到 {len(result['data'])} 个结果")
        return True

    def test_fund_flow(self):
        """测试资金流向查询"""
        fund_flow = self.client.get_fund_flow("600519.SH", timeframe="1")
        assert isinstance(fund_flow, list), "响应不是列表"
        print(f"   查询到 {len(fund_flow)} 条资金流向数据")

        if len(fund_flow) > 0:
            flow = fund_flow[0]
            print(f"   示例: 日期={flow.get('trade_date')}, 主力净流入={flow.get('main_net_inflow')}")

        return True

    def test_etf_list(self):
        """测试ETF列表查询"""
        etf_list = self.client.get_etf_list(limit=5)
        assert isinstance(etf_list, list), "响应不是列表"
        print(f"   查询到 {len(etf_list)} 个ETF")

        if len(etf_list) > 0:
            etf = etf_list[0]
            print(f"   示例: {etf.get('symbol')} - {etf.get('name')}")

        return True

    def test_market_quotes(self):
        """测试实时行情查询"""
        quotes = self.client.get_market_quotes("600519.SH,000001.SZ")
        assert quotes is not None, "行情响应为None"
        print(f"   行情查询成功")
        return True

    def test_indicator_registry(self):
        """测试指标注册表"""
        registry = self.client.get_indicator_registry()
        assert 'indicators' in registry, "响应缺少indicators字段"
        print(f"   注册表包含 {len(registry['indicators'])} 个指标")

        if len(registry['indicators']) > 0:
            indicator = registry['indicators'][0]
            print(f"   示例: {indicator.get('abbreviation')} - {indicator.get('full_name')}")

        return True

    def test_calculate_indicators(self):
        """测试技术指标计算"""
        result = self.client.calculate_indicators(
            symbol="600519.SH",
            indicators=[
                {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
                {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
            ],
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        assert 'data' in result, "响应缺少data字段"
        print(f"   计算了 {len(result['data'])} 个数据点")

        if len(result['data']) > 0:
            point = result['data'][0]
            print(f"   示例: 日期={point.get('date')}, SMA_20={point.get('SMA_20')}, RSI_14={point.get('RSI_14')}")

        return True

    def test_system_health(self):
        """测试系统健康检查"""
        health = self.client.get_system_health()
        assert 'status' in health, "响应缺少status字段"
        print(f"   系统状态: {health['status']}")
        print(f"   运行时间: {health.get('uptime', 'N/A')}秒")
        return True

    def test_database_health(self):
        """测试数据库健康检查"""
        db_health = self.client.get_database_health()
        assert 'data' in db_health, "响应缺少data字段"

        summary = db_health['data'].get('summary', {})
        print(f"   数据库总数: {summary.get('total_databases')}")
        print(f"   健康数据库: {summary.get('healthy_databases')}")
        print(f"   整体状态: {summary.get('overall_status')}")

        return True

    def test_database_stats(self):
        """测试数据库统计"""
        stats = self.client.get_database_stats()
        assert 'data' in stats, "响应缺少data字段"

        data = stats['data']
        print(f"   架构: {data.get('architecture')}")
        print(f"   总分类数: {data.get('total_classifications')}")

        return True

    def test_adapters_health(self):
        """测试适配器健康检查"""
        adapters = self.client.get_adapters_health()
        assert 'adapters' in adapters, "响应缺少adapters字段"

        for name, status in adapters['adapters'].items():
            print(f"   {name}: {status.get('status')}")

        return True

    def test_system_logs(self):
        """测试系统日志查询"""
        logs = self.client.get_system_logs(limit=5)
        assert 'logs' in logs or 'data' in logs, "响应缺少logs/data字段"
        print(f"   查询到日志记录")
        return True

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 70)
        print("MyStocks API 端点自动化测试")
        print("=" * 70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 定义测试套件
        test_suite = [
            ("健康检查", self.test_health_check),
            ("认证流程", self.test_authentication),
            ("股票基本信息查询", self.test_stocks_basic),
            ("日线数据查询", self.test_daily_kline),
            ("股票搜索", self.test_stock_search),
            ("资金流向查询", self.test_fund_flow),
            ("ETF列表查询", self.test_etf_list),
            ("实时行情查询", self.test_market_quotes),
            ("指标注册表", self.test_indicator_registry),
            ("技术指标计算", self.test_calculate_indicators),
            ("系统健康检查", self.test_system_health),
            ("数据库健康检查", self.test_database_health),
            ("数据库统计", self.test_database_stats),
            ("适配器健康检查", self.test_adapters_health),
            ("系统日志查询", self.test_system_logs),
        ]

        # 运行所有测试
        for test_name, test_func in test_suite:
            self.run_test(test_name, test_func)

        # 输出测试总结
        self.print_summary()

        # 返回退出码
        return 0 if self.test_results['failed'] == 0 else 1

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)

        total = self.test_results['passed'] + self.test_results['failed'] + self.test_results['skipped']

        print(f"\n总测试数: {total}")
        print(f"✅ 通过: {self.test_results['passed']}")
        print(f"❌ 失败: {self.test_results['failed']}")
        print(f"⚠️  跳过: {self.test_results['skipped']}")

        if self.test_results['failed'] > 0:
            print("\n失败的测试:")
            for test in self.test_results['tests']:
                if test['status'] == 'FAILED':
                    print(f"   - {test['name']}: {test['message']}")

        pass_rate = (self.test_results['passed'] / total * 100) if total > 0 else 0
        print(f"\n通过率: {pass_rate:.1f}%")

        if self.test_results['failed'] == 0:
            print("\n🎉 所有测试通过！API运行正常！")
        else:
            print("\n⚠️  部分测试失败，请检查日志")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MyStocks API 端点测试")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="API服务器地址 (默认: http://localhost:8000)"
    )
    args = parser.parse_args()

    # 创建测试器
    tester = APIEndpointTester(base_url=args.base_url)

    # 运行所有测试
    exit_code = tester.run_all_tests()

    # 返回退出码
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
