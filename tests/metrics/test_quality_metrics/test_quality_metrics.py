#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 测试质量指标系统

提供全面的测试质量评估、度量和分析功能，支持多维度质量指标计算和优化建议。
"""

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from .metric_category import (
    MetricCategory,
    MetricWeight,
    QualityMetric,
    TestCoverageAnalyzer,
    TestPerformanceAnalyzer,
    TestReliabilityAnalyzer,
    TestResult,
    TestSuiteMetrics,
)

class TestQualityMetrics:
    """测试质量指标主类"""

    def __init__(self):
        self.coverage_analyzer = TestCoverageAnalyzer()
        self.reliability_analyzer = TestReliabilityAnalyzer()
        self.performance_analyzer = TestPerformanceAnalyzer()
        self.metrics_registry = self._initialize_metrics_registry()
        self.quality_history = []

    def _initialize_metrics_registry(self) -> Dict[str, QualityMetric]:
        """初始化指标注册表"""
        return {
            # 覆盖率指标
            "test_coverage": QualityMetric(
                name="测试覆盖率",
                category=MetricCategory.COVERAGE,
                description="测试用例对代码的覆盖程度",
                unit="%",
                weight=MetricWeight.CRITICAL,
                formula="covered_lines / total_lines * 100",
                target_value=90.0,
                min_value=0.0,
                max_value=100.0,
                is_higher_better=True,
            ),
            "function_coverage": QualityMetric(
                name="函数覆盖率",
                category=MetricCategory.COVERAGE,
                description="测试用例对函数的覆盖程度",
                unit="%",
                weight=MetricWeight.HIGH,
                formula="covered_functions / total_functions * 100",
                target_value=95.0,
                min_value=0.0,
                max_value=100.0,
                is_higher_better=True,
            ),
            # 可靠性指标
            "pass_rate": QualityMetric(
                name="测试通过率",
                category=MetricCategory.RELIABILITY,
                description="测试用例通过的比例",
                unit="%",
                weight=MetricWeight.CRITICAL,
                formula="passed_tests / total_tests * 100",
                target_value=98.0,
                min_value=0.0,
                max_value=100.0,
                is_higher_better=True,
            ),
            "stability_score": QualityMetric(
                name="稳定性得分",
                category=MetricCategory.RELIABILITY,
                description="测试执行结果的稳定性",
                unit="分",
                weight=MetricWeight.HIGH,
                formula="100 - coefficient_of_variation",
                target_value=90.0,
                min_value=0.0,
                max_value=100.0,
                is_higher_better=True,
            ),
            # 性能指标
            "test_execution_time": QualityMetric(
                name="测试执行时间",
                category=MetricCategory.PERFORMANCE,
                description="测试套件的平均执行时间",
                unit="秒",
                weight=MetricWeight.MEDIUM,
                formula="total_duration / total_tests",
                target_value=2.0,
                min_value=0.0,
                max_value=60.0,
                is_higher_better=False,
            ),
            "concurrent_performance": QualityMetric(
                name="并发性能",
                category=MetricCategory.PERFORMANCE,
                description="测试并发执行的性能表现",
                unit="req/s",
                weight=MetricWeight.MEDIUM,
                formula="successful_requests / time_seconds",
                target_value=100.0,
                min_value=0.0,
                max_value=1000.0,
                is_higher_better=True,
            ),
            # 可维护性指标
            "test_maintainability": QualityMetric(
                name="可维护性得分",
                category=MetricCategory.MAINTAINABILITY,
                description="测试代码的可维护程度",
                unit="分",
                weight=MetricWeight.MEDIUM,
                formula="基于代码复杂度和耦合度的评分",
                target_value=85.0,
                min_value=0.0,
                max_value=100.0,
                is_higher_better=True,
            ),
            # 可用性指标
            "test_usability": QualityMetric(
                name="测试可用性",
                category=MetricCategory.USABILITY,
                description="测试框架和工具的易用性",
                unit="分",
                weight=MetricWeight.LOW,
                formula="基于用户反馈和工具易用性",
                target_value=80.0,
                min_value=0.0,
                max_value=100.0,
                is_higher_better=True,
            ),
            # 安全性指标
            "test_security": QualityMetric(
                name="测试安全性",
                category=MetricCategory.SECURITY,
                description="测试过程中的安全性保障",
                unit="分",
                weight=MetricWeight.HIGH,
                formula="安全测试覆盖率 + 漏洞检测能力",
                target_value=90.0,
                min_value=0.0,
                max_value=100.0,
                is_higher_better=True,
            ),
        }

    def calculate_test_suite_metrics(
        self, test_results: List[TestResult], code_files: List[str] = None
    ) -> TestSuiteMetrics:
        """计算测试套件质量指标"""
        print("🎯 计算测试套件质量指标...")

        if not test_results:
            print("⚠️  没有测试结果数据")
            return None

        # 基本统计
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.status == "passed"])
        failed_tests = len([r for r in test_results if r.status == "failed"])
        skipped_tests = len([r for r in test_results if r.status == "skipped"])
        error_tests = len([r for r in test_results if r.status == "error"])

        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        average_duration = statistics.mean([r.duration for r in test_results])
        total_duration = sum([r.duration for r in test_results])

        # 分析覆盖率
        coverage_metrics = self.coverage_analyzer.analyze_code_coverage(test_results, code_files or [])
        coverage_percentage = coverage_metrics.get("overall_coverage_percentage", 0)

        # 分析可靠性
        reliability_metrics = self.reliability_analyzer.analyze_reliability(test_results)
        reliability_score = reliability_metrics.get("reliability_score", 0)

        # 分析性能
        performance_metrics = self.performance_analyzer.analyze_performance(test_results)
        performance_score = performance_metrics.get("performance_score", 0)

        # 计算综合质量得分
        quality_score = self._calculate_quality_score(coverage_percentage, reliability_score, performance_score)

        # 创建测试套件指标
        suite_metrics = TestSuiteMetrics(
            suite_name="comprehensive_test_suite",
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            pass_rate=round(pass_rate, 2),
            average_duration=round(average_duration, 3),
            total_duration=round(total_duration, 2),
            coverage_percentage=round(coverage_percentage, 2),
            reliability_score=round(reliability_score, 2),
            performance_score=round(performance_score, 2),
            quality_score=round(quality_score, 2),
            timestamp=datetime.now(),
            test_results=test_results,
        )

        # 保存到历史记录
        self.quality_history.append(suite_metrics)

        return suite_metrics

    def _calculate_quality_score(self, coverage: float, reliability: float, performance: float) -> float:
        """计算综合质量得分"""
        # 使用加权平均
        weights = {"coverage": 0.3, "reliability": 0.4, "performance": 0.3}

        quality_score = (
            coverage * weights["coverage"] + reliability * weights["reliability"] + performance * weights["performance"]
        )

        return round(quality_score, 2)

    def generate_quality_report(self, suite_metrics: TestSuiteMetrics) -> Dict[str, Any]:
        """生成质量报告"""
        print("📊 生成质量报告...")

        # 分析各维度指标
        coverage_analysis = self.coverage_analyzer.analyze_code_coverage(
            suite_metrics.test_results, ["sample_file1.py", "sample_file2.py"]
        )
        reliability_analysis = self.reliability_analyzer.analyze_reliability(suite_metrics.test_results)
        performance_analysis = self.performance_analyzer.analyze_performance(suite_metrics.test_results)

        # 生成建议
        quality_recommendations = self._generate_quality_recommendations(suite_metrics)

        # 识别改进机会
        improvement_opportunities = self._identify_improvement_opportunities(
            coverage_analysis, reliability_analysis, performance_analysis
        )

        # 质量趋势分析
        quality_trend = self._analyze_quality_trend()

        quality_report = {
            "report_summary": {
                "suite_name": suite_metrics.suite_name,
                "generated_at": suite_metrics.timestamp.isoformat(),
                "quality_score": suite_metrics.quality_score,
                "overall_rating": self._get_quality_rating(suite_metrics.quality_score),
                "total_test_executions": suite_metrics.total_tests,
            },
            "metrics_by_category": {
                "coverage": coverage_analysis,
                "reliability": reliability_analysis,
                "performance": performance_analysis,
            },
            "detailed_metrics": {
                "test_results": {
                    "total": suite_metrics.total_tests,
                    "passed": suite_metrics.passed_tests,
                    "failed": suite_metrics.failed_tests,
                    "skipped": suite_metrics.skipped_tests,
                    "errors": suite_metrics.error_tests,
                    "pass_rate": suite_metrics.pass_rate,
                },
                "performance": {
                    "average_duration_ms": suite_metrics.average_duration * 1000,
                    "total_duration_ms": suite_metrics.total_duration * 1000,
                },
                "coverage": {"percentage": suite_metrics.coverage_percentage},
            },
            "quality_recommendations": quality_recommendations,
            "improvement_opportunities": improvement_opportunities,
            "quality_trend": quality_trend,
            "metric_definitions": {name: metric.__dict__ for name, metric in self.metrics_registry.items()},
            "benchmark_comparison": self._compare_with_benchmarks(suite_metrics),
        }

        return quality_report

    def _generate_quality_recommendations(self, suite_metrics: TestSuiteMetrics) -> List[Dict[str, Any]]:
        """生成质量改进建议"""
        recommendations = []

        # 基于通过率的建议
        if suite_metrics.pass_rate < 95:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "reliability",
                    "issue": f"测试通过率较低 ({suite_metrics.pass_rate:.1f}%)",
                    "recommendation": "修复失败的测试用例，提高测试质量",
                    "estimated_effort": "medium",
                }
            )

        # 基于覆盖率的建议
        if suite_metrics.coverage_percentage < 85:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "coverage",
                    "issue": f"代码覆盖率不足 ({suite_metrics.coverage_percentage:.1f}%)",
                    "recommendation": "增加测试用例以提高覆盖率",
                    "estimated_effort": "high",
                }
            )

        # 基于性能的建议
        if suite_metrics.average_duration > 5:
            recommendations.append(
                {
                    "priority": "low",
                    "category": "performance",
                    "issue": f"测试执行时间较长 ({suite_metrics.average_duration:.2f}s)",
                    "recommendation": "优化测试逻辑，提高执行效率",
                    "estimated_effort": "low",
                }
            )

        # 基于综合质量的建议
        if suite_metrics.quality_score < 80:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "overall",
                    "issue": f"整体质量评分较低 ({suite_metrics.quality_score:.1f})",
                    "recommendation": "全面提升测试质量",
                    "estimated_effort": "high",
                }
            )

        return recommendations

    def _identify_improvement_opportunities(
        self, coverage: Dict, reliability: Dict, performance: Dict
    ) -> List[Dict[str, Any]]:
        """识别改进机会"""
        opportunities = []

        # 覆盖率改进机会
        if coverage.get("overall_coverage_percentage", 0) < 90:
            opportunities.append(
                {
                    "area": "coverage",
                    "potential_improvement": 90 - coverage.get("overall_coverage_percentage", 0),
                    "priority": "medium",
                    "description": "提高代码覆盖率",
                    "estimated_effort": "medium",
                }
            )

        # 可靠性改进机会
        if reliability.get("pass_rate", 0) < 98:
            opportunities.append(
                {
                    "area": "reliability",
                    "potential_improvement": 98 - reliability.get("pass_rate", 0),
                    "priority": "high",
                    "description": "提高测试可靠性",
                    "estimated_effort": "medium",
                }
            )

        # 性能改进机会
        if performance.get("average_duration_ms", 0) > 2000:
            opportunities.append(
                {
                    "area": "performance",
                    "potential_improvement": performance.get("average_duration_ms", 0) - 2000,
                    "priority": "low",
                    "description": "优化测试执行性能",
                    "estimated_effort": "low",
                }
            )

        return opportunities

    def _analyze_quality_trend(self) -> Dict[str, Any]:
        """分析质量趋势"""
        if len(self.quality_history) < 2:
            return {"status": "insufficient_data"}

        # 获取最近10次的结果
        recent_history = self.quality_history[-10:]

        dates = [m.timestamp.strftime("%Y-%m-%d") for m in recent_history]
        quality_scores = [m.quality_score for m in recent_history]

        trend_direction = "improving" if quality_scores[-1] > quality_scores[0] else "declining"

        return {
            "dates": dates,
            "quality_scores": quality_scores,
            "trend_direction": trend_direction,
            "average_score": round(statistics.mean(quality_scores), 2),
            "score_change": round(quality_scores[-1] - quality_scores[0], 2),
            "volatility": round(statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0, 2),
        }

    def _get_quality_rating(self, quality_score: float) -> str:
        """获取质量评级"""
        if quality_score >= 95:
            return "excellent"
        elif quality_score >= 85:
            return "good"
        elif quality_score >= 75:
            return "fair"
        elif quality_score >= 60:
            return "poor"
        else:
            return "critical"

    def _compare_with_benchmarks(self, suite_metrics: TestSuiteMetrics) -> Dict[str, Any]:
        """与行业标准基准对比"""
        # 模拟行业标准数据
        industry_benchmarks = {
            "coverage": 85.0,
            "pass_rate": 95.0,
            "performance_score": 80.0,
            "quality_score": 82.0,
        }

        comparison = {}
        for metric, benchmark in industry_benchmarks.items():
            if metric == "coverage":
                actual = suite_metrics.coverage_percentage
            elif metric == "pass_rate":
                actual = suite_metrics.pass_rate
            elif metric == "performance_score":
                actual = suite_metrics.performance_score
            else:
                actual = suite_metrics.quality_score

            comparison[metric] = {
                "actual": round(actual, 2),
                "benchmark": benchmark,
                "difference": round(actual - benchmark, 2),
                "status": "above" if actual > benchmark else ("below" if actual < benchmark else "meets"),
            }

        return comparison

    def export_metrics(
        self,
        suite_metrics: TestSuiteMetrics,
        format: str = "json",
        file_path: str = None,
    ) -> str:
        """导出质量指标"""
        print(f"📤 导出质量指标 ({format})...")

        quality_report = self.generate_quality_report(suite_metrics)

        if format == "json":
            output = json.dumps(quality_report, ensure_ascii=False, indent=2, default=str)
        elif format == "html":
            output = self._generate_html_report(quality_report)
        else:
            raise ValueError(f"不支持的格式: {format}")

        # 保存到文件
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 质量指标已保存到: {file_path}")
            return file_path
        else:
            return output

    def _generate_html_report(self, quality_report: Dict[str, Any]) -> str:
        """生成HTML格式的质量报告"""
        html_template = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>测试质量报告</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                .metric { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }
                .recommendation { background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 3px; }
                .excellent { color: green; font-weight: bold; }
                .good { color: blue; font-weight: bold; }
                .fair { color: orange; font-weight: bold; }
                .poor { color: red; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>测试质量报告</h1>
                <p>生成时间: {generated_at}</p>
                <p>综合质量得分: <span class="{rating}">{quality_score}</span></p>
            </div>

            <div class="metric">
                <h2>测试结果统计</h2>
                <table>
                    <tr><th>总测试数</th><th>通过</th><th>失败</th><th>跳过</th><th>错误</th></tr>
                    <tr><td>{total_tests}</td><td>{passed_tests}</td><td>{failed_tests}</td><td>{skipped_tests}</td><td>{error_tests}</td></tr>
                </table>
            </div>

            <div class="metric">
                <h2>覆盖率分析</h2>
                <p>总体覆盖率: {coverage_percentage}%</p>
            </div>

            <div class="metric">
                <h2>改进建议</h2>
                {recommendations}
            </div>
        </body>
        </html>
        """

        # 格式化建议
        recommendations_html = ""
        for rec in quality_report.get("quality_recommendations", []):
            priority_class = rec.get("priority", "medium")
            recommendations_html += f"""
            <div class="recommendation">
                <strong>{priority_class.upper()}</strong> - {rec["category"]}
                <br>问题: {rec["issue"]}
                <br>建议: {rec["recommendation"]}
                <br>预估工作量: {rec.get("estimated_effort", "unknown")}
            </div>
            """

        return html_template.format(
            generated_at=quality_report["report_summary"]["generated_at"],
            quality_score=quality_report["report_summary"]["quality_score"],
            rating=quality_report["report_summary"]["overall_rating"],
            total_tests=quality_report["detailed_metrics"]["test_results"]["total"],
            passed_tests=quality_report["detailed_metrics"]["test_results"]["passed"],
            failed_tests=quality_report["detailed_metrics"]["test_results"]["failed"],
            skipped_tests=quality_report["detailed_metrics"]["test_results"]["skipped"],
            error_tests=quality_report["detailed_metrics"]["test_results"]["errors"],
            coverage_percentage=quality_report["detailed_metrics"]["coverage"]["percentage"],
            recommendations=recommendations_html,
        )

    def get_metric_dashboard_data(self) -> Dict[str, Any]:
        """获取质量指标仪表盘数据"""
        if not self.quality_history:
            return {"status": "no_data"}

        latest_metrics = self.quality_history[-1]

        return {
            "current_metrics": {
                "quality_score": latest_metrics.quality_score,
                "pass_rate": latest_metrics.pass_rate,
                "coverage_percentage": latest_metrics.coverage_percentage,
                "performance_score": latest_metrics.performance_score,
                "average_duration": latest_metrics.average_duration,
                "timestamp": latest_metrics.timestamp.isoformat(),
            },
            "trend_data": {
                "dates": [m.timestamp.strftime("%Y-%m-%d %H:%M") for m in self.quality_history[-20:]],
                "quality_scores": [m.quality_score for m in self.quality_history[-20:]],
                "pass_rates": [m.pass_rate for m in self.quality_history[-20:]],
                "coverage_percentages": [m.coverage_percentage for m in self.quality_history[-20:]],
            },
            "alert_summary": {
                "critical_issues": len([m for m in self.quality_history if m.quality_score < 60]),
                "warning_issues": len([m for m in self.quality_history if 60 <= m.quality_score < 80]),
                "healthy_executions": len([m for m in self.quality_history if m.quality_score >= 85]),
            },
        }


def demo_test_quality_metrics():
    """演示测试质量指标功能"""
    print("🚀 演示测试质量指标功能")

    # 创建质量指标系统
    quality_system = TestQualityMetrics()

    # 生成模拟测试结果
    test_results = []
    for i in range(100):
        status = np.random.choice(["passed", "failed", "skipped", "error"], p=[0.92, 0.05, 0.02, 0.01])
        duration = np.random.uniform(0.1, 8.0) if status == "passed" else np.random.uniform(0.5, 3.0)

        test_result = TestResult(
            test_id=f"test_{i + 1:03d}",
            test_name=f"Test Case {i + 1}",
            status=status,
            duration=duration,
            timestamp=datetime.now() - timedelta(hours=np.random.randint(0, 24)),
            error_message=f"Error message {i}" if status in ["failed", "error"] else None,
            metadata={
                "error_type": np.random.choice(["assertion", "timeout", "network", "unknown"]),
                "failure_count": np.random.randint(1, 5) if status != "passed" else 0,
            },
        )
        test_results.append(test_result)

    # 计算质量指标
    suite_metrics = quality_system.calculate_test_suite_metrics(test_results, ["src/main.py", "src/utils.py"])

    if suite_metrics:
        print("\n📊 测试套件质量指标:")
        print(f"   总测试数: {suite_metrics.total_tests}")
        print(f"   通过率: {suite_metrics.pass_rate:.1f}%")
        print(f"   覆盖率: {suite_metrics.coverage_percentage:.1f}%")
        print(f"   可靠性得分: {suite_metrics.reliability_score:.1f}")
        print(f"   性能得分: {suite_metrics.performance_score:.1f}")
        print(f"   综合质量得分: {suite_metrics.quality_score:.1f}")

        # 生成质量报告
        quality_report = quality_system.generate_quality_report(suite_metrics)
        print(f"\n📈 质量评级: {quality_report['report_summary']['overall_rating']}")

        # 导出质量指标
        json_file = quality_system.export_metrics(suite_metrics, "json", "/tmp/test_quality_report.json")
        print(f"📄 JSON报告已保存: {json_file}")

        # 获取仪表盘数据
        dashboard_data = quality_system.get_metric_dashboard_data()
        print("\n🎯 仪表盘数据更新成功")

        # 显示改进建议
        print("\n💡 改进建议:")
        for rec in quality_report.get("quality_recommendations", [])[:3]:
            print(f"   {rec['priority'].upper()}: {rec['recommendation']}")

