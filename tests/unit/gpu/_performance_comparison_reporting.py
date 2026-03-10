"""Reporting helpers for `test_performance_comparison.py`."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np


def generate_summary_snapshot(performance_improvements: Dict[str, Any]) -> Dict[str, Any]:
    """汇总各类别性能提升。"""
    summary = {
        "matrix_performance": {},
        "transform_performance": {},
        "memory_performance": {},
        "workflow_performance": {},
        "overall_improvement": {},
    }

    category_mapping = {
        "matrix_operations": "matrix_performance",
        "transform_operations": "transform_performance",
        "memory_operations": "memory_performance",
        "workflow_performance": "workflow_performance",
    }

    for source_key, target_key in category_mapping.items():
        if source_key not in performance_improvements:
            continue

        improvements = performance_improvements[source_key]
        speedups = [item.get("speedup_factor", 1) for item in improvements.values() if "speedup_factor" in item]
        if not speedups:
            continue

        summary[target_key] = {
            "average_speedup": np.mean(speedups),
            "max_speedup": max(speedups),
            "min_speedup": min(speedups),
        }

    all_speedups = [
        category["average_speedup"]
        for category in summary.values()
        if isinstance(category, dict) and category.get("average_speedup")
    ]
    if all_speedups:
        summary["overall_improvement"] = {
            "average_speedup_across_all_categories": np.mean(all_speedups),
            "categories_tested": len(all_speedups),
            "max_category_speedup": max(all_speedups),
            "min_category_speedup": min(all_speedups),
        }

    return summary


def build_benchmark_report_lines(report: Dict[str, Any]) -> List[str]:
    """构建性能对比报告日志行。"""
    summary = report["summary"]
    lines = [
        "",
        "=" * 80,
        "📊 GPU加速引擎性能基准对比报告",
        "=" * 80,
        f"📈 测试时间: {report['benchmark_timestamp']}",
    ]

    if summary.get("matrix_performance"):
        matrix_perf = summary["matrix_performance"]
        lines.extend(
            [
                "",
                "🧮 矩阵运算性能提升:",
                f"   📊 平均加速比: {matrix_perf['average_speedup']:.2f}x",
                f"   🚀 最大加速比: {matrix_perf['max_speedup']:.2f}x",
                f"   📉 最小加速比: {matrix_perf['min_speedup']:.2f}x",
            ]
        )

    if summary.get("transform_performance"):
        transform_perf = summary["transform_performance"]
        lines.extend(
            [
                "",
                "🔄 变换操作性能提升:",
                f"   📊 平均加速比: {transform_perf['average_speedup']:.2f}x",
                f"   🚀 最大加速比: {transform_perf['max_speedup']:.2f}x",
                f"   📉 最小加速比: {transform_perf['min_speedup']:.2f}x",
            ]
        )

    if summary.get("memory_performance"):
        memory_perf = summary["memory_performance"]
        lines.extend(
            [
                "",
                "💾 内存操作性能提升:",
                f"   📊 平均加速比: {memory_perf['average_speedup']:.2f}x",
                f"   🚀 最大加速比: {memory_perf['max_speedup']:.2f}x",
                f"   📉 最小加速比: {memory_perf['min_speedup']:.2f}x",
            ]
        )

    if summary.get("workflow_performance"):
        workflow_perf = summary["workflow_performance"]
        lines.extend(
            [
                "",
                "⚡ 工作流性能提升:",
                f"   📊 平均加速比: {workflow_perf['average_speedup']:.2f}x",
                f"   🚀 最大加速比: {workflow_perf['max_speedup']:.2f}x",
                f"   📉 最小加速比: {workflow_perf['min_speedup']:.2f}x",
            ]
        )

    if summary.get("overall_improvement"):
        overall = summary["overall_improvement"]
        lines.extend(
            [
                "",
                "🎯 总体性能提升:",
                f"   📊 所有类别平均加速比: {overall['average_speedup_across_all_categories']:.2f}x",
                f"   📈 测试类别数量: {overall['categories_tested']}",
                f"   🚀 最高类别加速比: {overall['max_category_speedup']:.2f}x",
            ]
        )

    lines.extend(["", "📋 详细性能数据:"])

    optimized_results = report["optimized_results"]

    if "matrix_operations" in optimized_results and optimized_results["matrix_operations"]["success"]:
        lines.append("")
        lines.append("   🧮 矩阵运算 (优化后):")
        for result in optimized_results["matrix_operations"]["results"]:
            size = result["matrix_size"]
            gflops = result["performance_gflops"]
            time_ms = result["avg_execution_time"] * 1000
            lines.append(f"      {size}x{size}: {gflops:.2f} GFLOPS ({time_ms:.2f}ms)")

    if "transform_operations" in optimized_results and optimized_results["transform_operations"]["success"]:
        lines.append("")
        lines.append("   🔄 变换操作 (优化后):")
        for result in optimized_results["transform_operations"]["results"]:
            operation = result["operation"]
            time_ms = result["avg_execution_time"] * 1000
            throughput = result["throughput_elements_per_sec"]
            lines.append(f"      {operation}: {time_ms:.3f}ms ({throughput:.0f} elements/s)")

    if "memory_operations" in optimized_results and optimized_results["memory_operations"]["success"]:
        lines.append("")
        lines.append("   💾 内存操作 (优化后):")
        lines.append(f"      内存池效率: {optimized_results['memory_operations']['pool_efficiency']:.1%}")

        for result in optimized_results["memory_operations"]["results"][:3]:
            size_kb = result["allocation_size_bytes"] / 1024
            time_us = result["avg_allocation_time"] * 1e6
            rate = result["allocations_per_sec"]
            lines.append(f"      {size_kb:.0f}KB: {time_us:.1f}μs ({rate:.0f} alloc/s)")

    lines.extend(["", "=" * 80])
    return lines


def log_benchmark_report(report: Dict[str, Any]) -> None:
    """输出性能对比报告日志。"""
    for line in build_benchmark_report_lines(report):
        logging.info(line)
