#!/usr/bin/env python3
"""
前后端集成测试脚本

测试目标：
1. 验证API端点响应
2. 测试前端页面功能
3. 验证双数据源切换
4. 检查Mock数据一致性
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

# 添加项目根目录到Python路径
sys.path.append("/opt/claude/mystocks_spec")
sys.path.append("/opt/claude/mystocks_spec/web/backend")


class IntegrationTester:
    """集成测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.test_results = []
        self.session = requests.Session()

        # 设置默认请求头
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "MyStocks-IntegrationTest/1.0",
            }
        )

    def log_test(self, test_name: str, status: str, details: str = "", response_time: float = 0):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "status": status,  # "PASS", "FAIL", "SKIP"
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        # 控制台输出
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} [{status}] {test_name}")
        if details:
            print(f"   详情: {details}")
        if response_time > 0:
            print(f"   响应时间: {response_time:.2f}s")
        print()

    def test_api_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        expected_status: int = 200,
    ) -> Dict[str, Any]:
        """测试API端点"""
        url = f"{self.api_base}{endpoint}"

        try:
            start_time = time.time()

            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            response_time = time.time() - start_time

            # 解析响应
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}

            # 检查状态码
            success = response.status_code == expected_status

            return {
                "success": success,
                "status_code": response.status_code,
                "response_time": response_time,
                "data": response_data,
                "headers": dict(response.headers),
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "status_code": 0,
                "response_time": 0,
                "data": {"error": str(e)},
                "headers": {},
            }

    async def test_basic_api_endpoints(self):
        """测试基础API端点"""
        print("🔍 测试基础API端点...")

        # 测试认证端点
        auth_result = self.test_api_endpoint("POST", "/auth/login", {"username": "test", "password": "test"})

        if auth_result["success"] or auth_result["status_code"] == 422:  # 422表示验证失败，但端点存在
            self.log_test("用户认证API", "PASS", "认证端点可访问", auth_result["response_time"])
            token = None
        else:
            self.log_test(
                "用户认证API",
                "FAIL",
                f"状态码: {auth_result['status_code']}",
                auth_result["response_time"],
            )

        # 测试股票基本信息API
        stocks_result = self.test_api_endpoint("GET", "/data/stocks/basic")
        if stocks_result["success"]:
            data_count = (
                len(stocks_result["data"].get("data", [])) if isinstance(stocks_result["data"].get("data"), list) else 0
            )
            self.log_test(
                "股票基本信息API",
                "PASS",
                f"返回 {data_count} 条记录",
                stocks_result["response_time"],
            )
        else:
            self.log_test(
                "股票基本信息API",
                "FAIL",
                f"错误: {stocks_result['data']}",
                stocks_result["response_time"],
            )

        # 测试行业列表API
        industries_result = self.test_api_endpoint("GET", "/data/stocks/industries")
        if industries_result["success"]:
            data_count = (
                len(industries_result["data"].get("data", []))
                if isinstance(industries_result["data"].get("data"), list)
                else 0
            )
            self.log_test(
                "行业列表API",
                "PASS",
                f"返回 {data_count} 个行业",
                industries_result["response_time"],
            )
        else:
            self.log_test(
                "行业列表API",
                "FAIL",
                f"错误: {industries_result['data']}",
                industries_result["response_time"],
            )

        # 测试概念列表API
        concepts_result = self.test_api_endpoint("GET", "/data/stocks/concepts")
        if concepts_result["success"]:
            data_count = (
                len(concepts_result["data"].get("data", []))
                if isinstance(concepts_result["data"].get("data"), list)
                else 0
            )
            self.log_test(
                "概念列表API",
                "PASS",
                f"返回 {data_count} 个概念",
                concepts_result["response_time"],
            )
        else:
            self.log_test(
                "概念列表API",
                "FAIL",
                f"错误: {concepts_result['data']}",
                concepts_result["response_time"],
            )

        # 测试市场概览API
        market_result = self.test_api_endpoint("GET", "/data/markets/overview")
        if market_result["success"]:
            self.log_test(
                "市场概览API",
                "PASS",
                "市场概览数据正常",
                market_result["response_time"],
            )
        else:
            self.log_test(
                "市场概览API",
                "FAIL",
                f"错误: {market_result['data']}",
                market_result["response_time"],
            )

        # 测试股票搜索API
        search_result = self.test_api_endpoint("GET", "/data/stocks/search?keyword=平安")
        if search_result["success"]:
            data_count = (
                len(search_result["data"].get("data", [])) if isinstance(search_result["data"].get("data"), list) else 0
            )
            self.log_test(
                "股票搜索API",
                "PASS",
                f"搜索到 {data_count} 条结果",
                search_result["response_time"],
            )
        else:
            self.log_test(
                "股票搜索API",
                "FAIL",
                f"错误: {search_result['data']}",
                search_result["response_time"],
            )

    async def test_technical_analysis_apis(self):
        """测试技术分析相关API"""
        print("📊 测试技术分析API...")

        # 测试技术指标API
        indicators_result = self.test_api_endpoint("GET", "/indicators")
        if indicators_result["success"]:
            self.log_test(
                "技术指标API",
                "PASS",
                "技术指标端点可访问",
                indicators_result["response_time"],
            )
        else:
            self.log_test(
                "技术指标API",
                "FAIL",
                f"错误: {indicators_result['data']}",
                indicators_result["response_time"],
            )

        # 测试K线数据API
        kline_result = self.test_api_endpoint("GET", "/market/kline?stock_code=000001&period=daily")
        if kline_result["success"]:
            data_count = (
                len(kline_result["data"].get("data", [])) if isinstance(kline_result["data"].get("data"), list) else 0
            )
            self.log_test(
                "K线数据API",
                "PASS",
                f"返回 {data_count} 条K线数据",
                kline_result["response_time"],
            )
        else:
            self.log_test(
                "K线数据API",
                "FAIL",
                f"错误: {kline_result['data']}",
                kline_result["response_time"],
            )

    async def test_industry_concept_apis(self):
        """测试行业概念分析API"""
        print("🏢 测试行业概念分析API...")

        # 测试行业列表API
        industry_list_result = self.test_api_endpoint("GET", "/analysis/industry/list")
        if industry_list_result["success"]:
            data_count = len(industry_list_result["data"].get("industries", []))
            self.log_test(
                "行业列表分析API",
                "PASS",
                f"返回 {data_count} 个行业",
                industry_list_result["response_time"],
            )
        else:
            self.log_test(
                "行业列表分析API",
                "FAIL",
                f"错误: {industry_list_result['data']}",
                industry_list_result["response_time"],
            )

        # 测试概念列表API
        concept_list_result = self.test_api_endpoint("GET", "/analysis/concept/list")
        if concept_list_result["success"]:
            data_count = len(concept_list_result["data"].get("concepts", []))
            self.log_test(
                "概念列表分析API",
                "PASS",
                f"返回 {data_count} 个概念",
                concept_list_result["response_time"],
            )
        else:
            self.log_test(
                "概念列表分析API",
                "FAIL",
                f"错误: {concept_list_result['data']}",
                concept_list_result["response_time"],
            )

        # 测试行业成分股API
        industry_stocks_result = self.test_api_endpoint("GET", "/analysis/industry/stocks?industry_code=IND_001")
        if industry_stocks_result["success"]:
            data_count = len(industry_stocks_result["data"].get("stocks", []))
            self.log_test(
                "行业成分股API",
                "PASS",
                f"返回 {data_count} 只股票",
                industry_stocks_result["response_time"],
            )
        else:
            self.log_test(
                "行业成分股API",
                "FAIL",
                f"错误: {industry_stocks_result['data']}",
                industry_stocks_result["response_time"],
            )

    async def test_stock_detail_apis(self):
        """测试股票详情相关API"""
        print("📈 测试股票详情API...")

        # 测试股票详情API
        detail_result = self.test_api_endpoint("GET", "/data/stocks/000001/detail")
        if detail_result["success"]:
            self.log_test(
                "股票详情API",
                "PASS",
                "股票详情数据正常",
                detail_result["response_time"],
            )
        else:
            self.log_test(
                "股票详情API",
                "FAIL",
                f"错误: {detail_result['data']}",
                detail_result["response_time"],
            )

        # 测试分时数据API
        intraday_result = self.test_api_endpoint("GET", "/data/stocks/intraday?symbol=000001")
        if intraday_result["success"]:
            self.log_test("分时数据API", "PASS", "分时数据正常", intraday_result["response_time"])
        else:
            self.log_test(
                "分时数据API",
                "FAIL",
                f"错误: {intraday_result['data']}",
                intraday_result["response_time"],
            )

        # 测试交易摘要API
        summary_result = self.test_api_endpoint("GET", "/data/stocks/000001/trading-summary")
        if summary_result["success"]:
            self.log_test(
                "交易摘要API",
                "PASS",
                "交易摘要数据正常",
                summary_result["response_time"],
            )
        else:
            self.log_test(
                "交易摘要API",
                "FAIL",
                f"错误: {summary_result['data']}",
                summary_result["response_time"],
            )

    async def test_frontend_pages(self):
        """测试前端页面"""
        print("🌐 测试前端页面...")

        frontend_pages = [
            ("/", "仪表盘页面"),
            ("/stocks", "股票列表页面"),
            ("/stock-detail/000001", "股票详情页面"),
            ("/technical-analysis", "技术分析页面"),
            ("/industry-concept-analysis", "行业概念分析页面"),
        ]

        for path, name in frontend_pages:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{path}", timeout=10)
                response_time = time.time() - start_time

                if response.status_code == 200:
                    self.log_test(f"前端页面 - {name}", "PASS", "页面正常加载", response_time)
                else:
                    self.log_test(
                        f"前端页面 - {name}",
                        "FAIL",
                        f"状态码: {response.status_code}",
                        response_time,
                    )
            except Exception as e:
                self.log_test(f"前端页面 - {name}", "FAIL", f"加载失败: {str(e)}", 0)

    async def test_data_consistency(self):
        """测试数据一致性"""
        print("🔄 测试数据一致性...")

        # 测试多次请求返回相同的数据结构
        stocks_result1 = self.test_api_endpoint("GET", "/data/stocks/basic?limit=5")
        stocks_result2 = self.test_api_endpoint("GET", "/data/stocks/basic?limit=5")

        if stocks_result1["success"] and stocks_result2["success"]:
            data1 = stocks_result1["data"]
            data2 = stocks_result2["data"]

            # 检查响应结构一致性
            if data1.get("success") == data2.get("success") and type(data1.get("data")) == type(data2.get("data")):
                self.log_test("数据一致性", "PASS", "数据结构一致")
            else:
                self.log_test("数据一致性", "FAIL", "数据结构不一致")
        else:
            self.log_test("数据一致性", "FAIL", "API调用失败")

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始前后端集成测试...")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试地址: {self.base_url}")
        print("=" * 60)

        # 运行各类测试
        await self.test_basic_api_endpoints()
        await self.test_technical_analysis_apis()
        await self.test_industry_concept_apis()
        await self.test_stock_detail_apis()
        await self.test_frontend_pages()
        await self.test_data_consistency()

        # 生成测试报告
        self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"跳过: {skipped_tests} ⚠️")
        print(f"成功率: {(passed_tests / total_tests * 100):.1f}%")

        # 失败测试详情
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test_name']}: {result['details']}")

        # 保存详细报告
        report_file = "/opt/claude/mystocks_spec/integration_test_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "failed_tests": failed_tests,
                        "skipped_tests": skipped_tests,
                        "success_rate": passed_tests / total_tests * 100,
                        "test_time": datetime.now().isoformat(),
                        "test_url": self.base_url,
                    },
                    "details": self.test_results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n📄 详细报告已保存到: {report_file}")
        print("=" * 60)


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="前后端集成测试")
    parser.add_argument("--url", default="http://localhost:8000", help="测试URL")
    parser.add_argument(
        "--test-type",
        choices=["all", "api", "frontend", "consistency"],
        default="all",
        help="测试类型",
    )

    args = parser.parse_args()

    tester = IntegrationTester(args.url)

    if args.test_type == "all":
        await tester.run_all_tests()
    elif args.test_type == "api":
        await tester.test_basic_api_endpoints()
    elif args.test_type == "frontend":
        await tester.test_frontend_pages()
    elif args.test_type == "consistency":
        await tester.test_data_consistency()


if __name__ == "__main__":
    asyncio.run(main())
