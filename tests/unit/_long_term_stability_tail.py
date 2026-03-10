#!/usr/bin/env python3
"""Tail helpers extracted from `tests/unit/test_long_term_stability.py`."""

import time
from typing import Any, Dict

import numpy as np


class LongTermStabilityTailMixin:
    """Support methods extracted from `LongTermStabilityTester`."""

    async def test_memory_pool_stability(self) -> Dict[str, Any]:
        """测试内存池长期稳定性"""
        try:
            from src.gpu.core.hardware_abstraction.memory_pool import get_memory_pool

            memory_pool = get_memory_pool()
            await memory_pool.initialize()

            duration_seconds = 60
            allocation_cycles = 1000
            allocation_sizes = [512, 1024, 2048, 4096, 8192, 16384, 32768]

            allocation_results = []
            deallocation_results = []
            pool_stats_history = []

            start_time = time.time()
            cycle = 0

            print(f"      💾 执行 {allocation_cycles} 次内存分配循环...")

            while cycle < allocation_cycles and (time.time() - start_time) < duration_seconds:
                size = np.random.choice(allocation_sizes)
                alloc_start = time.time()
                block_id = await memory_pool.allocate(size)
                alloc_time = time.time() - alloc_start

                if block_id:
                    allocation_results.append(
                        {
                            "cycle": cycle,
                            "size": size,
                            "allocation_time": alloc_time,
                            "success": True,
                            "block_id": block_id,
                        }
                    )

                    if np.random.random() > 0.5:
                        dealloc_start = time.time()
                        success = await memory_pool.deallocate(block_id)
                        dealloc_time = time.time() - dealloc_start

                        deallocation_results.append(
                            {
                                "cycle": cycle,
                                "block_id": block_id,
                                "deallocation_time": dealloc_time,
                                "success": success,
                            }
                        )
                else:
                    allocation_results.append(
                        {
                            "cycle": cycle,
                            "size": size,
                            "allocation_time": alloc_time,
                            "success": False,
                            "block_id": None,
                        }
                    )

                if cycle % 100 == 0:
                    stats = memory_pool.get_stats()
                    pool_stats_history.append(
                        {
                            "cycle": cycle,
                            "timestamp": time.time() - start_time,
                            "stats": stats.copy(),
                        }
                    )
                    print(f"         第 {cycle} 次循环: 池效率={stats.get('pool_efficiency', 0):.1%}")

                cycle += 1

            final_stats = memory_pool.get_stats()
            if hasattr(memory_pool, "cleanup") and callable(getattr(memory_pool, "cleanup")):
                await memory_pool.cleanup()

            successful_allocations = sum(1 for result in allocation_results if result["success"])
            successful_deallocations = sum(1 for result in deallocation_results if result["success"])
            allocation_times = [result["allocation_time"] for result in allocation_results if result["success"]]
            deallocation_times = [
                result["deallocation_time"] for result in deallocation_results if result["success"]
            ]

            if pool_stats_history:
                pool_efficiency_history = [item["stats"].get("pool_efficiency", 0) for item in pool_stats_history]
                pool_stability = {
                    "avg_efficiency": np.mean(pool_efficiency_history),
                    "min_efficiency": min(pool_efficiency_history),
                    "max_efficiency": max(pool_efficiency_history),
                    "efficiency_stable": np.std(pool_efficiency_history) < 0.1,
                }
            else:
                pool_stability = {}

            return {
                "success": successful_allocations >= allocation_cycles * 0.95
                and successful_deallocations >= len(deallocation_results) * 0.95,
                "allocation_cycles": cycle,
                "allocation_analysis": {
                    "total_allocations": len(allocation_results),
                    "successful_allocations": successful_allocations,
                    "allocation_success_rate": successful_allocations / len(allocation_results),
                    "avg_allocation_time": np.mean(allocation_times) if allocation_times else 0,
                    "min_allocation_time": min(allocation_times) if allocation_times else 0,
                    "max_allocation_time": max(allocation_times) if allocation_times else 0,
                },
                "deallocation_analysis": {
                    "total_deallocations": len(deallocation_results),
                    "successful_deallocations": successful_deallocations,
                    "deallocation_success_rate": (
                        successful_deallocations / len(deallocation_results) if deallocation_results else 1
                    ),
                    "avg_deallocation_time": np.mean(deallocation_times) if deallocation_times else 0,
                    "min_deallocation_time": min(deallocation_times) if deallocation_times else 0,
                    "max_deallocation_time": max(deallocation_times) if deallocation_times else 0,
                },
                "pool_stability": pool_stability,
                "final_pool_stats": final_stats,
            }

        except Exception as error:
            return {"success": False, "error": str(error)}

    def get_current_memory_usage(self) -> float:
        """获取当前内存使用量（MB）"""
        try:
            return self.process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0

    def generate_stability_report(self) -> Dict[str, Any]:
        """生成稳定性测试报告"""
        total_suites = len(self.test_results)
        successful_suites = sum(1 for result in self.test_results.values() if result.get("success", False))

        memory_usages = [result.get("memory_usage_mb", 0) for result in self.test_results.values()]
        max_memory_usage = max(memory_usages) if memory_usages else 0
        total_memory_growth = max_memory_usage - (self.initial_memory / (1024 * 1024)) if self.initial_memory else 0

        return {
            "stability_test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stability_phase": "Phase 6.4.4",
            "total_test_suites": total_suites,
            "successful_test_suites": successful_suites,
            "failed_test_suites": total_suites - successful_suites,
            "stability_success_rate": (successful_suites / total_suites * 100) if total_suites > 0 else 0,
            "detailed_results": self.test_results,
            "memory_analysis": {
                "initial_memory_mb": self.initial_memory / (1024 * 1024) if self.initial_memory else 0,
                "max_memory_usage_mb": max_memory_usage,
                "total_memory_growth_mb": total_memory_growth,
                "memory_leak_detected": total_memory_growth > 200,
            },
            "summary": {
                "long_running_stable": self.test_results.get("长时间运行稳定性测试", {}).get("success", False),
                "memory_leak_free": not self.test_results.get("内存泄漏检测测试", {})
                .get("details", {})
                .get("memory_analysis", {})
                .get("memory_stability", True),
                "resource_cleanup_working": self.test_results.get("资源清理验证测试", {}).get("success", False),
                "concurrent_stress_stable": self.test_results.get("并发压力稳定性测试", {}).get("success", False),
                "exception_recovery_working": self.test_results.get("异常恢复稳定性测试", {}).get("success", False),
                "memory_pool_stable": self.test_results.get("内存池长期稳定性测试", {}).get("success", False),
                "overall_stability_achieved": successful_suites >= total_suites * 0.8,
            },
        }

    def print_summary(self, report: Dict[str, Any]):
        """打印稳定性测试摘要"""
        print("\n" + "=" * 80)
        print("📊 GPU加速引擎长期稳定性测试报告")
        print("=" * 80)

        summary = report["summary"]
        memory_analysis = report["memory_analysis"]

        print(
            f"📈 稳定性测试成功率: {report['stability_success_rate']:.1f}% ({report['successful_test_suites']}/{report['total_test_suites']})"
        )
        print(f"🕒 测试时间: {report['stability_test_timestamp']}")
        print(f"💾 内存增长: {memory_analysis['total_memory_growth_mb']:.1f}MB")

        print("\n🔧 稳定性指标:")
        print(f"   ✅ 长期运行稳定: {'是' if summary['long_running_stable'] else '否'}")
        print(f"   ✅ 无内存泄漏: {'是' if summary['memory_leak_free'] else '否'}")
        print(f"   ✅ 资源清理正常: {'是' if summary['resource_cleanup_working'] else '否'}")
        print(f"   ✅ 并发压力稳定: {'是' if summary['concurrent_stress_stable'] else '否'}")
        print(f"   ✅ 异常恢复正常: {'是' if summary['exception_recovery_working'] else '否'}")
        print(f"   ✅ 内存池稳定: {'是' if summary['memory_pool_stable'] else '否'}")
        print(f"🚀 整体稳定性达成: {'是' if summary['overall_stability_achieved'] else '否'}")

        print("\n📋 详细结果:")
        for suite_name, result in report["detailed_results"].items():
            status = "✅" if result.get("success", False) else "❌"
            execution_time = result.get("execution_time", 0)
            memory_usage = result.get("memory_usage_mb", 0)
            print(f"   {status} {suite_name} ({execution_time:.2f}s, {memory_usage:.1f}MB)")

        if "长时间运行稳定性测试" in report["detailed_results"]:
            long_run_result = report["detailed_results"]["长时间运行稳定性测试"]["details"]
            if long_run_result.get("success", False):
                print("\n⏰ 长期运行摘要:")
                print(f"   • 运行时长: {long_run_result.get('stability_duration_minutes', 0)} 分钟")
                print(f"   • 操作成功率: {long_run_result.get('success_rate', 0) * 100:.1f}%")
                print(
                    f"   • 内存增长率: {long_run_result.get('memory_analysis', {}).get('memory_growth_rate_mb_per_sec', 0):.3f} MB/s"
                )

        if "内存泄漏检测测试" in report["detailed_results"]:
            leak_result = report["detailed_results"]["内存泄漏检测测试"]["details"]
            if leak_result.get("success", False):
                print("\n🔍 内存泄漏摘要:")
                print(f"   • 内存增长: {leak_result.get('memory_analysis', {}).get('memory_growth_mb', 0):.1f}MB")
                print(
                    f"   • 对象清理率: {leak_result.get('object_cleanup_analysis', {}).get('cleanup_rate', 0) * 100:.1f}%"
                )

        if "并发压力稳定性测试" in report["detailed_results"]:
            concurrent_result = report["detailed_results"]["并发压力稳定性测试"]["details"]
            if concurrent_result.get("success", False):
                print("\n🔄 并发压力摘要:")
                print(f"   • 并发任务数: {concurrent_result.get('concurrent_workers', 0)}")
                print(f"   • 成功率: {concurrent_result.get('success_rate', 0) * 100:.1f}%")
                print(f"   • 操作吞吐量: {concurrent_result.get('operations_per_second', 0):.1f} ops/s")

        print("\n" + "=" * 80)


async def run_long_term_stability_main(tester_cls: Any):
    """运行长期稳定性测试主流程。"""
    print("🚀 Phase 6.4.4 GPU加速引擎长期稳定性测试")
    print("=" * 80)

    tester = tester_cls()
    report = await tester.run_comprehensive_stability_tests()
    tester.print_summary(report)
    return report
