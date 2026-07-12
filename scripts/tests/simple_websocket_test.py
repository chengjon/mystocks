#!/usr/bin/env python3
"""简化的WebSocket压力测试
Simple WebSocket Stress Test - Basic Connection Testing

用于测试WebSocket服务器基本连接功能，不依赖复杂的库。

Author: Claude Code
Date: 2025-11-13
"""

import asyncio
import json
import os
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TestResult:
    """测试结果"""

    connection_id: str
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "success": self.success,
            "response_time_ms": round(self.response_time_ms, 2),
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


async def simple_connection_test(
    url: str = os.getenv("BACKEND_URL", f"http://localhost:{os.getenv('BACKEND_PORT', '8020')}"),
) -> List[TestResult]:
    """简单的连接测试

    Args:
        url: 服务器URL

    Returns:
        测试结果列表

    """
    import aiohttp

    results = []

    async with aiohttp.ClientSession() as session:
        # 测试API端点可用性
        try:
            async with session.get(f"{url}/api/socketio-status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 服务器状态正常: {data.get('status', 'unknown')}")
                    return [TestResult("status_check", True, 0)]
                error_msg = f"服务器返回状态码: {response.status}"
                print(f"❌ {error_msg}")
                return [TestResult("status_check", False, 0, error_msg)]
        except Exception as e:
            error_msg = f"连接失败: {e!s}"
            print(f"❌ {error_msg}")
            return [TestResult("status_check", False, 0, error_msg)]


async def run_basic_stress_test(
    url: str = os.getenv("BACKEND_URL", f"http://localhost:{os.getenv('BACKEND_PORT', '8020')}"),
    concurrent_requests: int = 50,
    requests_per_connection: int = 10,
) -> Dict[str, Any]:
    """运行基本的压力测试

    Args:
        url: 服务器URL
        concurrent_requests: 并发请求数
        requests_per_connection: 每连接的请求数

    Returns:
        测试统计结果

    """
    print("🚀 开始基本压力测试")
    print(f"   并发请求数: {concurrent_requests}")
    print(f"   每连接请求数: {requests_per_connection}")

    start_time = time.time()
    results = []

    async def single_request(request_id: str) -> TestResult:
        """单个请求"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                req_start = time.time()

                # 测试基本API端点
                async with session.get(f"{url}/api/socketio-status") as response:
                    response_time = (time.time() - req_start) * 1000

                    if response.status == 200:
                        return TestResult(request_id, True, response_time)
                    return TestResult(
                        request_id,
                        False,
                        response_time,
                        f"HTTP {response.status}",
                    )

        except Exception as e:
            return TestResult(request_id, False, 0, str(e))

    # 创建并发任务
    tasks = []
    for i in range(concurrent_requests):
        for j in range(requests_per_connection):
            request_id = f"req_{i}_{j}"
            task = asyncio.create_task(single_request(request_id))
            tasks.append(task)

    # 等待所有任务完成
    print(f"⏳ 执行 {len(tasks)} 个并发请求...")
    completed_results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理结果
    for result in completed_results:
        if isinstance(result, TestResult):
            results.append(result)
        else:
            # 处理异常
            results.append(TestResult("unknown", False, 0, str(result)))

    end_time = time.time()
    total_duration = end_time - start_time

    # 统计分析
    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]

    success_rate = (len(successful_results) / len(results)) * 100 if results else 0

    response_times = [r.response_time_ms for r in successful_results if r.response_time_ms > 0]
    avg_response_time = statistics.mean(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0

    throughput = len(results) / total_duration if total_duration > 0 else 0

    stats = {
        "total_requests": len(results),
        "successful_requests": len(successful_results),
        "failed_requests": len(failed_results),
        "success_rate": round(success_rate, 2),
        "total_duration": round(total_duration, 2),
        "throughput": round(throughput, 2),
        "avg_response_time_ms": round(avg_response_time, 2),
        "max_response_time_ms": round(max_response_time, 2),
        "min_response_time_ms": round(min_response_time, 2),
        "errors": [r.error_message for r in failed_results if r.error_message],
    }

    # 显示结果
    print("\n📊 测试结果:")
    print(f"   总请求数: {stats['total_requests']}")
    print(f"   成功请求: {stats['successful_requests']}")
    print(f"   失败请求: {stats['failed_requests']}")
    print(f"   成功率: {stats['success_rate']}%")
    print(f"   总耗时: {stats['total_duration']}秒")
    print(f"   吞吐量: {stats['throughput']} 请求/秒")
    print(f"   平均响应时间: {stats['avg_response_time_ms']}ms")
    print(f"   最大响应时间: {stats['max_response_time_ms']}ms")
    print(f"   最小响应时间: {stats['min_response_time_ms']}ms")

    if stats["errors"]:
        print("\n⚠️ 错误信息:")
        unique_errors = list(set(stats["errors"]))[:5]  # 只显示前5个唯一错误
        for error in unique_errors:
            print(f"   - {error}")

    return stats


async def main():
    """主函数"""
    print("🔧 WebSocket服务器连接测试")
    print("=" * 40)

    # 1. 基本连接测试
    basic_results = await simple_connection_test()

    if not basic_results or not basic_results[0].success:
        print("❌ 基本连接测试失败，请检查服务器状态")
        return

    print("\n" + "=" * 40)

    # 2. 运行不同规模的测试
    test_scenarios = [
        {"concurrent_requests": 20, "requests_per_connection": 5},
        {"concurrent_requests": 50, "requests_per_connection": 10},
        {"concurrent_requests": 100, "requests_per_connection": 20},
    ]

    all_stats = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 测试场景 {i}/{len(test_scenarios)}")
        print(f"并发请求数: {scenario['concurrent_requests']}")
        print(f"每连接请求数: {scenario['requests_per_connection']}")
        print("-" * 30)

        try:
            stats = await run_basic_stress_test(**scenario)
            all_stats.append(stats)
        except Exception as e:
            print(f"❌ 测试场景 {i} 失败: {e}")

    # 3. 生成综合报告
    if all_stats:
        print("\n📈 综合测试报告")
        print("=" * 40)

        best_scenario = min(all_stats, key=lambda s: s["avg_response_time_ms"])
        worst_scenario = max(all_stats, key=lambda s: s["avg_response_time_ms"])

        print("最佳性能场景:")
        print(
            f"  并发: {best_scenario['concurrent_requests']}, "
            f"响应时间: {best_scenario['avg_response_time_ms']}ms, "
            f"成功率: {best_scenario['success_rate']}%",
        )

        print("最差性能场景:")
        print(
            f"  并发: {worst_scenario['concurrent_requests']}, "
            f"响应时间: {worst_scenario['avg_response_time_ms']}ms, "
            f"成功率: {worst_scenario['success_rate']}%",
        )

        avg_success_rate = statistics.mean(s["success_rate"] for s in all_stats)
        avg_throughput = statistics.mean(s["throughput"] for s in all_stats)

        print("\n平均指标:")
        print(f"  平均成功率: {avg_success_rate:.2f}%")
        print(f"  平均吞吐量: {avg_throughput:.2f} 请求/秒")

        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("/opt/claude/mystocks_spec/var/log/tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f"basic_websocket_test_{timestamp}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "test_type": "basic_websocket_stress_test",
                        "timestamp": datetime.now().isoformat(),
                        "scenarios": all_stats,
                        "summary": {
                            "best_performance": best_scenario,
                            "worst_performance": worst_scenario,
                            "average_success_rate": avg_success_rate,
                            "average_throughput": avg_throughput,
                        },
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"\n💾 测试结果已保存: {filename}")
        except Exception as e:
            print(f"\n❌ 保存结果失败: {e}")


if __name__ == "__main__":
    # 设置事件循环策略
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
