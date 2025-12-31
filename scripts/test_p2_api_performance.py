#!/usr/bin/env python3
"""
P2 API性能测试脚本

测试所有P2 API的响应时间和吞吐量。

Author: Backend CLI (Claude Code)
Date: 2025-12-31
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import httpx

# API配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# P2 API端点列表
P2_API_ENDPOINTS = {
    "indicators": [
        {"method": "GET", "path": "/api/indicators/registry"},
        {"method": "GET", "path": "/api/indicators/registry/trend"},
        {"method": "GET", "path": "/api/indicators/cache/stats"},
        {"method": "GET", "path": "/api/indicators/configs"},
    ],
    "announcement": [
        {"method": "GET", "path": "/api/announcement/health"},
        {"method": "GET", "path": "/api/announcement/status"},
        {"method": "GET", "path": "/api/announcement/list"},
        {"method": "GET", "path": "/api/announcement/today"},
        {"method": "GET", "path": "/api/announcement/important"},
        {"method": "GET", "path": "/api/announcement/stats"},
    ],
    "system": [
        {"method": "GET", "path": "/api/health"},
        {"method": "GET", "path": "/api/health/detailed"},
        {"method": "GET", "path": "/api/system/health"},
        {"method": "GET", "path": "/api/system/adapters/health"},
        {"method": "GET", "path": "/api/system/datasources"},
        {"method": "GET", "path": "/api/system/architecture"},
        {"method": "GET", "path": "/api/system/database/health"},
        {"method": "GET", "path": "/api/system/database/stats"},
        {"method": "GET", "path": "/api/system/logs/summary"},
        {"method": "GET", "path": "/api/monitoring/summary"},
        {"method": "GET", "path": "/api/monitoring/control/status"},
    ],
}


class PerformanceTester:
    """性能测试器"""

    def __init__(self, base_url: str = BASE_URL, timeout: float = TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.results = []

    async def test_endpoint(
        self, client: httpx.AsyncClient, method: str, path: str, iteration: int = 1
    ) -> Dict[str, Any]:
        """测试单个端点性能"""

        url = f"{self.base_url}{path}"
        start_time = time.time()

        try:
            if method == "GET":
                response = await client.get(url, timeout=self.timeout)
            elif method == "POST":
                response = await client.post(url, timeout=self.timeout)
            else:
                return {
                    "endpoint": path,
                    "method": method,
                    "iteration": iteration,
                    "success": False,
                    "error": f"Unsupported method: {method}",
                    "status_code": None,
                    "response_time_ms": None,
                }

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            return {
                "endpoint": path,
                "method": method,
                "iteration": iteration,
                "success": response.status_code in [200, 201],
                "status_code": response.status_code,
                "response_time_ms": round(response_time_ms, 2),
                "error": None,
            }

        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            return {
                "endpoint": path,
                "method": method,
                "iteration": iteration,
                "success": False,
                "error": str(e),
                "status_code": None,
                "response_time_ms": round(response_time_ms, 2),
            }

    async def test_endpoint_multiple_times(
        self, client: httpx.AsyncClient, method: str, path: str, iterations: int = 5
    ) -> List[Dict[str, Any]]:
        """多次测试同一端点"""

        tasks = [
            self.test_endpoint(client, method, path, i) for i in range(1, iterations + 1)
        ]
        return await asyncio.gather(*tasks)

    async def run_all_tests(
        self, iterations: int = 5, concurrency: int = 10
    ) -> Dict[str, Any]:
        """运行所有性能测试"""

        print(f"🚀 开始P2 API性能测试")
        print(f"   基础URL: {self.base_url}")
        print(f"   每个端点测试次数: {iterations}")
        print(f"   并发数: {concurrency}")
        print()

        all_results = []
        start_time = time.time()

        # 使用limits参数设置连接限制
        limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
        async with httpx.AsyncClient(limits=limits) as client:
            # 测试所有模块
            for module, endpoints in P2_API_ENDPOINTS.items():
                print(f"📊 测试模块: {module}")

                for endpoint in endpoints:
                    method = endpoint["method"]
                    path = endpoint["path"]

                    # 多次测试同一端点
                    results = await self.test_endpoint_multiple_times(
                        client, method, path, iterations
                    )
                    all_results.extend(results)

                    # 计算统计数据
                    response_times = [r["response_time_ms"] for r in results if r["success"]]
                    success_rate = sum(1 for r in results if r["success"]) / len(results)

                    if response_times:
                        avg_time = statistics.mean(response_times)
                        min_time = min(response_times)
                        max_time = max(response_times)
                        median_time = statistics.median(response_times)

                        print(
                            f"  ✓ {method} {path}: "
                            f"平均={avg_time:.2f}ms, "
                            f"最小={min_time:.2f}ms, "
                            f"最大={max_time:.2f}ms, "
                            f"成功率={success_rate*100:.1f}%"
                        )
                    else:
                        print(f"  ✗ {method} {path}: 失败")

                print()

        total_time = time.time() - start_time

        # 生成总结报告
        summary = self.generate_summary(all_results, total_time)
        return summary

    def generate_summary(
        self, results: List[Dict[str, Any]], total_time: float
    ) -> Dict[str, Any]:
        """生成测试总结"""

        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        failed_tests = total_tests - successful_tests

        response_times = [r["response_time_ms"] for r in results if r["success"]]

        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "total_time_seconds": round(total_time, 2),
            "tests_per_second": round(total_tests / total_time, 2) if total_time > 0 else 0,
        }

        if response_times:
            summary["response_time_stats"] = {
                "average_ms": round(statistics.mean(response_times), 2),
                "min_ms": round(min(response_times), 2),
                "max_ms": round(max(response_times), 2),
                "median_ms": round(statistics.median(response_times), 2),
                "stdev_ms": round(statistics.stdev(response_times), 2)
                if len(response_times) > 1
                else 0,
            }
        else:
            summary["response_time_stats"] = None

        # 按模块分组统计
        summary["by_module"] = {}
        for module in P2_API_ENDPOINTS.keys():
            module_results = [
                r
                for r in results
                if any(ep["path"] == r["endpoint"] for ep in P2_API_ENDPOINTS[module])
            ]

            if module_results:
                module_times = [
                    r["response_time_ms"] for r in module_results if r["success"]
                ]
                module_success = sum(1 for r in module_results if r["success"])

                summary["by_module"][module] = {
                    "total_tests": len(module_results),
                    "successful_tests": module_success,
                    "success_rate": module_success / len(module_results)
                    if module_results
                    else 0,
                    "average_response_time_ms": round(statistics.mean(module_times), 2)
                    if module_times
                    else None,
                }

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """打印测试总结"""

        print("=" * 60)
        print("📈 P2 API性能测试总结")
        print("=" * 60)
        print()

        print(f"总测试数: {summary['total_tests']}")
        print(f"成功: {summary['successful_tests']}")
        print(f"失败: {summary['failed_tests']}")
        print(f"成功率: {summary['success_rate']*100:.2f}%")
        print()

        print(f"总耗时: {summary['total_time_seconds']}秒")
        print(f"吞吐量: {summary['tests_per_second']} 请求/秒")
        print()

        if summary.get("response_time_stats"):
            stats = summary["response_time_stats"]
            print("响应时间统计:")
            print(f"  平均: {stats['average_ms']}ms")
            print(f"  最小: {stats['min_ms']}ms")
            print(f"  最大: {stats['max_ms']}ms")
            print(f"  中位数: {stats['median_ms']}ms")
            print(f"  标准差: {stats['stdev_ms']}ms")
            print()

        print("按模块统计:")
        for module, stats in summary["by_module"].items():
            print(
                f"  {module}: "
                f"成功率={stats['success_rate']*100:.1f}%, "
                f"平均响应时间={stats['average_response_time_ms']}ms"
                if stats['average_response_time_ms']
                else f"  {module}: 成功率={stats['success_rate']*100:.1f}%"
            )
        print()

        print("=" * 60)

        # 性能评估
        if summary["success_rate"] >= 0.95:
            print("✅ 评估: 优秀 - 成功率>=95%")
        elif summary["success_rate"] >= 0.90:
            print("⚠️  评估: 良好 - 成功率>=90%")
        else:
            print("❌ 评估: 需要改进 - 成功率<90%")

        if summary["response_time_stats"]:
            avg_time = summary["response_time_stats"]["average_ms"]
            if avg_time <= 100:
                print("✅ 评估: 优秀 - 平均响应时间<=100ms")
            elif avg_time <= 500:
                print("⚠️  评估: 可接受 - 平均响应时间<=500ms")
            else:
                print("❌ 评估: 需要优化 - 平均响应时间>500ms")


async def main():
    """主函数"""

    tester = PerformanceTester()

    # 运行性能测试
    summary = await tester.run_all_tests(iterations=5, concurrency=10)

    # 打印总结
    tester.print_summary(summary)

    print()
    print("💡 优化建议:")

    if summary["success_rate"] < 0.95:
        print("  - 检查失败的端点,确保服务正常")
        print("  - 优化错误处理和重试逻辑")

    if summary["response_time_stats"]:
        avg_time = summary["response_time_stats"]["average_ms"]
        if avg_time > 500:
            print("  - 考虑使用缓存减少重复计算")
            print("  - 优化数据库查询性能")
            print("  - 实现异步处理")

    print("  - 实现连接池复用")
    print("  - 启用响应压缩 (gzip)")
    print("  - 考虑使用CDN加速静态资源")


if __name__ == "__main__":
    asyncio.run(main())
