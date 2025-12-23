#!/usr/bin/env python3
"""
P2模块API综合测试脚本
测试Technical Analysis、Strategy、Watchlist模块的API端点
"""

import asyncio
import json
import time
from typing import Any, Dict

import aiohttp


class P2ModuleTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {
            "technical_analysis": {},
            "strategy": {},
            "watchlist": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0.0,
            },
        }

    async def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """测试单个API端点"""
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                if method == "GET":
                    async with session.get(url) as response:
                        result = {
                            "status": "success" if response.status == 200 else "failed",
                            "status_code": response.status,
                            "endpoint": endpoint,
                            "response": (
                                await response.json()
                                if response.content_type == "application/json"
                                else await response.text()
                            ),
                            "method": method,
                        }
                elif method == "POST":
                    async with session.post(url, json=data) as response:
                        result = {
                            "status": "success" if response.status == 200 else "failed",
                            "status_code": response.status,
                            "endpoint": endpoint,
                            "response": (
                                await response.json()
                                if response.content_type == "application/json"
                                else await response.text()
                            ),
                            "method": method,
                            "data": data,
                        }
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")

                return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "endpoint": endpoint,
                "status_code": 500,
                "method": method,
            }

    async def test_technical_analysis_module(self):
        """测试Technical Analysis模块"""
        print("🧪 测试 Technical Analysis 模块...")

        # 测试技术指标端点
        test_cases = [
            {
                "name": "技术指标计算",
                "endpoint": "/api/technical/indicators/calculate",
                "method": "POST",
                "data": {"symbol": "000001", "indicators": ["ma5", "rsi", "macd"]},
                "expected_fields": ["indicators", "symbol", "timestamp"],
            },
            {
                "name": "技术指标注册表",
                "endpoint": "/api/technical/indicators/registry",
                "method": "GET",
                "expected_fields": ["indicators", "total", "timestamp"],
            },
            {
                "name": "信号分析",
                "endpoint": "/api/technical/signals/analysis",
                "method": "POST",
                "data": {"symbol": "000001"},
                "expected_fields": ["signals", "symbol", "timestamp"],
            },
        ]

        for test_case in test_cases:
            print(f"  🔍 {test_case['name']}...")
            result = await self.test_endpoint(
                endpoint=test_case["endpoint"],
                method=test_case["method"],
                data=test_case.get("data"),
            )

            success = result["status"] == "success"
            self.test_results["technical_analysis"][test_case["name"]] = {
                "success": success,
                "result": result,
            }

            if success:
                # 检查响应结构
                if "response" in result and isinstance(result["response"], dict):
                    for field in test_case["expected_fields"]:
                        if field not in result["response"]:
                            print(f"    ⚠️  缺少字段: {field}")
                            success = False
                            self.test_results["technical_analysis"][test_case["name"]][
                                "success"
                            ] = False
                self.test_results["technical_analysis"][test_case["name"]][
                    "success"
                ] = success

            status = "✅" if success else "❌"
            print(f"  {status} {test_case['name']}")

    async def test_strategy_module(self):
        """测试Strategy模块"""
        print("\n🎯 测试 Strategy 模块...")

        # 测试策略端点
        test_cases = [
            {
                "name": "策略定义",
                "endpoint": "/api/strategy/definitions",
                "method": "GET",
                "expected_fields": ["data", "total", "success", "message"],
            },
            {
                "name": "单股策略运行",
                "endpoint": "/api/strategy/run/single",
                "method": "POST",
                "data": {
                    "strategy_code": "volume_surge",
                    "symbol": "000001",
                    "check_date": "2025-12-01",
                },
                "expected_fields": ["success", "data", "message"],
            },
            {
                "name": "批量策略运行",
                "endpoint": "/api/strategy/run/batch",
                "method": "POST",
                "data": {"strategy_code": "ma_bullish", "market": "A", "limit": 10},
                "expected_fields": ["success", "data", "message"],
            },
        ]

        for test_case in test_cases:
            print(f"  🔍 {test_case['name']}...")
            result = await self.test_endpoint(
                endpoint=test_case["endpoint"],
                method=test_case["method"],
                data=test_case.get("data"),
            )

            success = result["status"] == "success"
            self.test_results["strategy"][test_case["name"]] = {
                "success": success,
                "result": result,
            }

            if success:
                # 检查响应结构
                if "response" in result and isinstance(result["response"], dict):
                    for field in test_case["expected_fields"]:
                        if field not in result["response"]:
                            print(f"    ⚠️  缺少字段: {field}")
                            success = False
                            self.test_results["strategy"][test_case["name"]][
                                "success"
                            ] = False
                self.test_results["strategy"][test_case["name"]]["success"] = success

            status = "✅" if success else "❌"
            print(f"  {status} {test_case['name']}")

    async def test_watchlist_module(self):
        """测试Watchlist模块"""
        print("\n📋 测试 Watchlist 模块...")

        # 测试自选股端点
        test_cases = [
            {
                "name": "获取自选股列表",
                "endpoint": "/api/watchlist/",
                "method": "GET",
                "expected_fields": [],
            },
            {
                "name": "获取自选股代码",
                "endpoint": "/api/watchlist/symbols",
                "method": "GET",
                "expected_fields": [],
            },
            {
                "name": "检查股票是否在自选股中",
                "endpoint": "/api/watchlist/check/000001",
                "method": "GET",
                "expected_fields": ["symbol", "is_in_watchlist"],
            },
            {
                "name": "获取自选股数量",
                "endpoint": "/api/watchlist/count",
                "method": "GET",
                "expected_fields": ["count"],
            },
            {
                "name": "更新自选股备注",
                "endpoint": "/api/watchlist/notes/000001",
                "method": "PUT",
                "data": {"notes": "测试备注"},
                "expected_fields": ["success", "message", "symbol"],
            },
            {
                "name": "从自选股移除股票",
                "endpoint": "/api/watchlist/remove/000001",
                "method": "DELETE",
                "expected_fields": ["success", "message", "symbol"],
            },
            {
                "name": "清空自选股列表",
                "endpoint": "/api/watchlist/clear",
                "method": "DELETE",
                "expected_fields": ["success", "message"],
            },
        ]

        for test_case in test_cases:
            print(f"  🔍 {test_case['name']}...")
            result = await self.test_endpoint(
                endpoint=test_case["endpoint"],
                method=test_case["method"],
                data=test_case.get("data"),
            )

            success = result["status"] == "success"
            self.test_results["watchlist"][test_case["name"]] = {
                "success": success,
                "result": result,
            }

            if success:
                # 检查响应结构
                if "response" in result:
                    if test_case["expected_fields"] == []:
                        # 对于空字段要求，只需要检查是否有响应数据
                        success = True
                    else:
                        # 对于指定字段要求，检查是否包含所有期望字段
                        if isinstance(result["response"], dict):
                            for field in test_case["expected_fields"]:
                                if field not in result["response"]:
                                    print(f"    ⚠️  缺少字段: {field}")
                                    success = False
                                    break
                    self.test_results["watchlist"][test_case["name"]]["success"] = (
                        success
                    )

            status = "✅" if success else "❌"
            print(f"  {status} {test_case['name']}")

    async def generate_test_report(self):
        """生成测试报告"""
        print("\n📊 生成测试报告...")

        # 计算统计
        total_tests = 0
        total_passed = 0

        for module in ["technical_analysis", "strategy", "watchlist"]:
            module_results = self.test_results[module]
            module_total = len(module_results)
            module_passed = sum(
                1 for result in module_results.values() if result["success"]
            )
            total_tests += module_total
            total_passed += module_passed

            print(f"\n{module.upper()} 模块:")
            for test_name, result in module_results.items():
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {test_name}")

            print(
                f"  通过率: {module_passed}/{module_total} ({module_passed / module_total * 100:.1f}%)"
            )

        # 更新总结
        self.test_results["summary"]["total_tests"] = total_tests
        self.test_results["summary"]["passed"] = total_passed
        self.test_results["summary"]["failed"] = total_tests - total_passed
        self.test_results["summary"]["success_rate"] = (
            (total_passed / total_tests * 100) if total_tests > 0 else 0
        )

        print("\n📈 总体统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过: {total_passed}")
        print(f"  失败: {total_tests - total_passed}")
        print(f"  成功率: {self.test_results['summary']['success_rate']:.1f}%")

        # 保存测试报告
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": self.test_results,
            "environment": "Week 3 生产验证测试",
            "modules": ["technical_analysis", "strategy", "watchlist"],
        }

        with open("docs/api/P2_MODULE_TEST_REPORT.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("\n📄 测试报告已保存到: docs/api/P2_MODULE_TEST_REPORT.json")

        return self.test_results


async def main():
    """主测试函数"""
    print("🚀 开始 P2模块API测试")
    print(f"⏰️ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    tester = P2ModuleTester()

    # 依次测试各个模块
    await tester.test_technical_analysis_module()
    await tester.test_strategy_module()
    await tester.test_watchlist_module()

    # 生成最终报告
    results = await tester.generate_test_report()

    print("\n🎯 测试完成!")
    if results["summary"]["success_rate"] >= 80:
        print("✅ P2模块测试通过 - 系统已准备好生产部署")
    else:
        print("❌ 部分测试失败 - 需要进一步修复")

    return results


if __name__ == "__main__":
    asyncio.run(main())
