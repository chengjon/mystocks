#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
契约测试报告生成器
负责生成各种格式的契约测试报告
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .models import (
    ContractTestReport,
    ContractTestSuite,
    TestExecutionResult,
    TestStatus,
)

logger = logging.getLogger(__name__)


class ContractTestReportGenerator:
    """契约测试报告生成器"""

    def __init__(self, output_dir: str = "reports/contract"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        suite: ContractTestSuite,
        results: List[TestExecutionResult],
        format: str = "json",
    ) -> str:
        """生成测试报告"""
        logger.info("生成测试报告: {suite.name} (格式: %(format)s)")

        # 创建报告对象
        report = ContractTestReport(suite=suite, results=results)

        # 计算统计信息
        self._calculate_statistics(report)

        # 生成报告内容
        if format.lower() == "json":
            return self._generate_json_report(report)
        elif format.lower() == "html":
            return self._generate_html_report(report)
        elif format.lower() == "xml":
            return self._generate_xml_report(report)
        elif format.lower() == "markdown":
            return self._generate_markdown_report(report)
        else:
            raise ValueError(f"不支持的报告格式: {format}")

    def _calculate_statistics(self, report: ContractTestReport):
        """计算报告统计信息"""
        results = report.results

        # 基础统计
        report.total_tests = len(results)
        report.passed_tests = sum(1 for r in results if r.status == TestStatus.PASSED)
        report.failed_tests = sum(1 for r in results if r.status == TestStatus.FAILED)
        report.skipped_tests = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        report.error_tests = sum(1 for r in results if r.status == TestStatus.ERROR)
        report.success_rate = round(
            (report.passed_tests / report.total_tests * 100) if report.total_tests > 0 else 0,
            2,
        )

        # 按类别统计
        report.category_stats = self._calculate_category_statistics(results)

        # 性能统计
        report.performance_stats = self._calculate_performance_statistics(results)

        # 生成建议
        report.recommendations = self._generate_recommendations(results)

    def _calculate_category_statistics(self, results: List[TestExecutionResult]) -> Dict[str, Dict[str, int]]:
        """计算按类别的统计信息"""
        category_stats = {}

        for result in results:
            category = result.test_case.category.value
            if category not in category_stats:
                category_stats[category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "error": 0,
                }

            category_stats[category]["total"] += 1

            if result.status == TestStatus.PASSED:
                category_stats[category]["passed"] += 1
            elif result.status == TestStatus.FAILED:
                category_stats[category]["failed"] += 1
            elif result.status == TestStatus.SKIPPED:
                category_stats[category]["skipped"] += 1
            elif result.status == TestStatus.ERROR:
                category_stats[category]["error"] += 1

        return category_stats

    def _calculate_performance_statistics(self, results: List[TestExecutionResult]) -> Dict[str, Dict[str, float]]:
        """计算性能统计信息"""
        performance_stats = {}

        # 响应时间统计
        response_times = [r.performance_metrics.get("response_time_ms", 0) for r in results if r.performance_metrics]

        if response_times:
            performance_stats["response_time"] = {
                "min_ms": round(min(response_times), 2),
                "max_ms": round(max(response_times), 2),
                "avg_ms": round(sum(response_times) / len(response_times), 2),
                "median_ms": round(self._calculate_median(response_times), 2),
                "p95_ms": round(self._calculate_percentile(response_times, 95), 2),
                "p99_ms": round(self._calculate_percentile(response_times, 99), 2),
            }

        # 性能评分统计
        performance_scores = [
            r.performance_metrics.get("performance_score", 0)
            for r in results
            if r.performance_metrics and "performance_score" in r.performance_metrics
        ]

        if performance_scores:
            performance_stats["performance_score"] = {
                "min": round(min(performance_scores), 2),
                "max": round(max(performance_scores), 2),
                "avg": round(sum(performance_scores) / len(performance_scores), 2),
            }

        return performance_stats

    def _calculate_median(self, values: List[float]) -> float:
        """计算中位数"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 1:
            return sorted_values[n // 2]
        else:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2

    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """计算百分位数"""
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = lower + 1
        if upper >= len(sorted_values):
            return sorted_values[lower]
        return sorted_values[lower] + (index - lower) * (sorted_values[upper] - sorted_values[lower])

    def _generate_recommendations(self, results: List[TestExecutionResult]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 失败测试建议
        failed_results = [r for r in results if r.status == TestStatus.FAILED]
        if failed_results:
            recommendations.append(f"有 {len(failed_results)} 个测试失败，建议检查相关功能的实现")

        # 性能建议
        slow_tests = [r for r in results if r.performance_metrics.get("response_time_ms", 0) > 2000]
        if slow_tests:
            recommendations.append(f"有 {len(slow_tests)} 个测试响应时间超过2秒，建议优化性能")

        # 错误建议
        error_results = [r for r in results if r.status == TestStatus.ERROR]
        if error_results:
            recommendations.append(f"有 {len(error_results)} 个测试执行时发生错误，建议检查日志")

        # 跳过测试建议
        skipped_results = [r for r in results if r.status == TestStatus.SKIPPED]
        if skipped_results:
            recommendations.append(f"有 {len(skipped_results)} 个测试被跳过，建议检查前置条件")

        # 成功率建议
        success_rate = sum(1 for r in results if r.status == TestStatus.PASSED) / len(results) * 100 if results else 0
        if success_rate < 90:
            recommendations.append(f"测试成功率 {success_rate:.1f}% 较低，建议提高测试质量")
        elif success_rate >= 95:
            recommendations.append(f"测试成功率 {success_rate:.1f}% 优秀，继续保持")

        return recommendations

    def _generate_json_report(self, report: ContractTestReport) -> str:
        """生成 JSON 格式报告"""
        # 转换为可序列化的字典
        report_dict = asdict(report)

        # 清理不可序列化的字段
        report_dict["suite"].pop("start_time", None)
        report_dict["suite"].pop("end_time", None)
        report_dict["generated_at"] = report.generated_at.isoformat()

        # 序列化结果
        serialized_results = []
        for result in report.results:
            result_dict = asdict(result)
            result_dict["test_case"] = {
                "id": result.test_case.id,
                "name": result.test_case.name,
                "category": result.test_case.category.value,
                "endpoint": result.test_case.endpoint,
                "method": result.test_case.method,
            }
            result_dict["status"] = result.status.value
            serialized_results.append(result_dict)

        report_dict["results"] = serialized_results

        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_report_{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2, default=str)

        logger.info("JSON 报告已保存: %(filepath)s")
        return str(filepath)

    def _generate_html_report(self, report: ContractTestReport) -> str:
        """生成 HTML 格式报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_report_{timestamp}.html"
        filepath = self.output_dir / filename

        # 生成 HTML 内容
        html_content = self._generate_html_content(report)

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("HTML 报告已保存: %(filepath)s")
        return str(filepath)

    def _generate_html_content(self, report: ContractTestReport) -> str:
        """生成 HTML 内容"""
        # 概览统计
        overview_html = f"""
        <div class="overview">
            <h2>测试概览</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">{report.total_tests}</div>
                    <div class="stat-label">总测试数</div>
                </div>
                <div class="stat-item success">
                    <div class="stat-value">{report.passed_tests}</div>
                    <div class="stat-label">通过</div>
                </div>
                <div class="stat-item danger">
                    <div class="stat-value">{report.failed_tests}</div>
                    <div class="stat-label">失败</div>
                </div>
                <div class="stat-item warning">
                    <div class="stat-value">{report.skipped_tests}</div>
                    <div class="stat-label">跳过</div>
                </div>
                <div class="stat-item error">
                    <div class="stat-value">{report.error_tests}</div>
                    <div class="stat-label">错误</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{report.success_rate:.1f}%</div>
                    <div class="stat-label">成功率</div>
                </div>
            </div>
        </div>
        """

        # 类别统计
        category_html = ""
        if report.category_stats:
            category_html = """
            <div class="category-stats">
                <h2>类别统计</h2>
                <div class="category-grid">
            """
            for category, stats in report.category_stats.items():
                success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                category_html += f"""
                <div class="category-item">
                    <h3>{category.replace("_", " ").title()}</h3>
                    <div class="category-stats-grid">
                        <div><strong>{stats["total"]}</strong> 总数</div>
                        <div class="success"><strong>{stats["passed"]}</strong> 通过</div>
                        <div class="danger"><strong>{stats["failed"]}</strong> 失败</div>
                        <div><strong>{success_rate:.1f}%</strong> 成功率</div>
                    </div>
                </div>
                """
            category_html += "</div></div>"

        # 性能统计
        performance_html = ""
        if report.performance_stats:
            performance_html = """
            <div class="performance-stats">
                <h2>性能统计</h2>
                <div class="performance-grid">
            """
            for metric, values in report.performance_stats.items():
                performance_html += f"""
                <div class="performance-item">
                    <h3>{metric.replace("_", " ").title()}</h3>
                    <div class="performance-metrics">
                """
                for key, value in values.items():
                    unit = "ms" if "ms" in key else ""
                    performance_html += f"""
                        <div><strong>{key.replace("_", " ").title()}:</strong> {value}{unit}</div>
                    """
                performance_html += """
                    </div>
                </div>
                """
            performance_html += "</div></div>"

        # 测试结果表格
        results_html = """
        <div class="test-results">
            <h2>测试结果详情</h2>
            <table>
                <thead>
                    <tr>
                        <th>测试用例</th>
                        <th>端点</th>
                        <th>类别</th>
                        <th>状态</th>
                        <th>耗时(ms)</th>
                        <th>响应时间(ms)</th>
                        <th>详情</th>
                    </tr>
                </thead>
                <tbody>
        """

        for result in report.results:
            status_class = result.status.value
            status_text = result.status.value.replace("_", " ").title()

            results_html += f"""
                <tr class="status-{status_class}">
                    <td>{result.test_case.name}</td>
                    <td>{result.test_case.endpoint}</td>
                    <td>{result.test_case.category.value.replace("_", " ").title()}</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                    <td>{result.duration:.2f}</td>
                    <td>{result.performance_metrics.get("response_time_ms", 0):.2f}</td>
                    <td>
            """

            if result.error_message:
                results_html += f"""
                        <div class="error-message">错误: {result.error_message}</div>
                """

            if result.validation_results:
                valid_count = sum(1 for v in result.validation_results if v["valid"])
                total_count = len(result.validation_results)
                results_html += f"""
                        <div class="validation-summary">
                            验证: {valid_count}/{total_count} 通过
                        </div>
                """

            results_html += """
                    </td>
                </tr>
            """

        results_html += """
                </tbody>
            </table>
        </div>
        """

        # 建议
        recommendations_html = ""
        if report.recommendations:
            recommendations_html = """
            <div class="recommendations">
                <h2>优化建议</h2>
                <ul>
            """
            for rec in report.recommendations:
                recommendations_html += f"""
                    <li>{rec}</li>
                """
            recommendations_html += """
                </ul>
            </div>
            """

        # 完整 HTML
        html_template = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MyStocks 契约测试报告</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .stat-item {{
                    background: #ecf0f1;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .stat-item.success {{ background: #d4edda; }}
                .stat-item.danger {{ background: #f8d7da; }}
                .stat-item.warning {{ background: #fff3cd; }}
                .stat-item.error {{ background: #f8d7da; }}
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .stat-label {{
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
                .category-grid, .performance-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }}
                .category-item, .performance-item {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #3498db;
                }}
                .category-stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                    margin-top: 10px;
                }}
                .status-badge {{
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.8em;
                    font-weight: bold;
                }}
                .status-passed {{ background: #28a745; color: white; }}
                .status-failed {{ background: #dc3545; color: white; }}
                .status-skipped {{ background: #ffc107; color: #212529; }}
                .status-error {{ background: #6c757d; color: white; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: 600;
                }}
                tr:hover {{
                    background-color: #f8f9fa;
                }}
                .error-message {{
                    color: #dc3545;
                    font-size: 0.9em;
                }}
                .validation-summary {{
                    color: #28a745;
                    font-size: 0.9em;
                }}
                .recommendations ul {{
                    padding-left: 20px;
                }}
                .recommendations li {{
                    margin: 10px 0;
                    color: #e74c3c;
                }}
                .timestamp {{
                    text-align: right;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MyStocks 契约测试报告</h1>
                <p><strong>测试套件:</strong> {report.suite.name}</p>
                <p><strong>描述:</strong> {report.suite.description}</p>
                <p><strong>生成时间:</strong> {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}</p>

                {overview_html}
                {category_html}
                {performance_html}
                {results_html}
                {recommendations_html}

                <div class="timestamp">
                    报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </div>
            </div>
        </body>
        </html>
        """

        return html_template

    def _generate_xml_report(self, report: ContractTestReport) -> str:
        """生成 XML 格式报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_report_{timestamp}.xml"
        filepath = self.output_dir / filename

        # 生成 XML 内容
        xml_content = self._generate_xml_content(report)

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_content)

        logger.info("XML 报告已保存: %(filepath)s")
        return str(filepath)

    def _generate_xml_content(self, report: ContractTestReport) -> str:
        """生成 XML 内容"""
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<contract_test_report>
    <metadata>
        <generated_at>{report.generated_at.isoformat()}</generated_at>
        <suite_name>{report.suite.name}</suite_name>
        <suite_description>{report.suite.description}</suite_description>
    </metadata>

    <summary>
        <total_tests>{report.total_tests}</total_tests>
        <passed_tests>{report.passed_tests}</passed_tests>
        <failed_tests>{report.failed_tests}</failed_tests>
        <skipped_tests>{report.skipped_tests}</skipped_tests>
        <error_tests>{report.error_tests}</error_tests>
        <success_rate>{report.success_rate:.2f}</success_rate>
    </summary>
"""

        # 添加类别统计
        if report.category_stats:
            xml_content += "    <category_statistics>\n"
            for category, stats in report.category_stats.items():
                xml_content += f"""
        <category name="{category}">
            <total>{stats["total"]}</total>
            <passed>{stats["passed"]}</passed>
            <failed>{stats["failed"]}</failed>
            <skipped>{stats["skipped"]}</skipped>
            <error>{stats["error"]}</error>
        </category>
"""
            xml_content += "    </category_statistics>\n"

        # 添加测试结果
        xml_content += "    <test_results>\n"
        for result in report.results:
            xml_content += f"""
        <test_result>
            <test_case_id>{result.test_case.id}</test_case_id>
            <test_case_name>{result.test_case.name}</test_case_name>
            <endpoint>{result.test_case.endpoint}</endpoint>
            <method>{result.test_case.method}</method>
            <category>{result.test_case.category.value}</category>
            <status>{result.status.value}</status>
            <duration>{result.duration:.3f}</duration>
            <performance_metrics>
"""
            for key, value in result.performance_metrics.items():
                xml_content += f"""
                <metric name="{key}">{value}</metric>
"""
            xml_content += """
            </performance_metrics>
            <validation_results>
"""
            for validation in result.validation_results:
                xml_content += f"""
                <validation rule="{validation["rule"]}" valid="{validation["valid"]}">
                    {validation["message"]}
                </validation>
"""
            xml_content += """
            </validation_results>
"""
            if result.error_message:
                xml_content += f"""
            <error_message>{result.error_message}</error_message>
"""
            xml_content += """
        </test_result>
"""
        xml_content += "    </test_results>\n"

        # 添加建议
        if report.recommendations:
            xml_content += "    <recommendations>\n"
            for rec in report.recommendations:
                xml_content += f"""
        <recommendation>{rec}</recommendation>
"""
            xml_content += "    </recommendations>\n"

        xml_content += "</contract_test_report>"

        return xml_content

    def _generate_markdown_report(self, report: ContractTestReport) -> str:
        """生成 Markdown 格式报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_report_{timestamp}.md"
        filepath = self.output_dir / filename

        # 生成 Markdown 内容
        md_content = self._generate_markdown_content(report)

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info("Markdown 报告已保存: %(filepath)s")
        return str(filepath)

    def _generate_markdown_content(self, report: ContractTestReport) -> str:
        """生成 Markdown 内容"""
        md_content = f"""# MyStocks 契约测试报告

## 基本信息
- **测试套件**: {report.suite.name}
- **描述**: {report.suite.description}
- **生成时间**: {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}

## 测试概览

| 指标 | 数值 |
|------|------|
| 总测试数 | {report.total_tests} |
| 通过 | {report.passed_tests} |
| 失败 | {report.failed_tests} |
| 跳过 | {report.skipped_tests} |
| 错误 | {report.error_tests} |
| 成功率 | {report.success_rate:.2f}% |

## 类别统计

"""

        for category, stats in report.category_stats.items():
            success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            md_content += f"""
### {category.replace("_", " ").title()}

| 统计 | 数值 |
|------|------|
| 总数 | {stats["total"]} |
| 通过 | {stats["passed"]} |
| 失败 | {stats["failed"]} |
| 跳过 | {stats["skipped"]} |
| 错误 | {stats["error"]} |
| 成功率 | {success_rate:.2f}% |

"""

        # 性能统计
        if report.performance_stats:
            md_content += "## 性能统计\n\n"
            for metric, values in report.performance_stats.items():
                md_content += f"### {metric.replace('_', ' ').title()}\n\n"
                md_content += "| 指标 | 数值 |\n"
                md_content += "|------|------|\n"
                for key, value in values.items():
                    unit = "ms" if "ms" in key else ""
                    md_content += f"| {key.replace('_', ' ').title()} | {value}{unit} |\n"
                md_content += "\n"

        # 测试结果详情
        md_content += "## 测试结果详情\n\n"
        md_content += "| 测试用例 | 端点 | 类别 | 状态 | 耗时(ms) | 响应时间(ms) | 详情 |\n"
        md_content += "|----------|------|------|------|----------|--------------|------|\n"

        for result in report.results:
            status_badge = result.status.value.replace("_", " ").title()
            details = ""

            if result.error_message:
                details = f"错误: {result.error_message}"

            if result.validation_results:
                valid_count = sum(1 for v in result.validation_results if v["valid"])
                total_count = len(result.validation_results)
                if details:
                    details += " | "
                details += f"验证: {valid_count}/{total_count}"

            md_content += f"| {result.test_case.name} | {result.test_case.endpoint} | "
            md_content += f"{result.test_case.category.value.replace('_', ' ').title()} | "
            md_content += f"{status_badge} | {result.duration:.2f} | "
            md_content += f"{result.performance_metrics.get('response_time_ms', 0):.2f} | {details} |\n"

        # 建议
        if report.recommendations:
            md_content += "\n## 优化建议\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                md_content += f"{i}. {rec}\n"

        md_content += f"\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return md_content

    def generate_summary_report(self, all_reports: List[Dict[str, Any]]) -> str:
        """生成综合报告摘要"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_summary_{timestamp}.json"
        filepath = self.output_dir / filename

        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_suites": len(all_reports),
            "total_tests": sum(r.get("total_tests", 0) for r in all_reports),
            "total_passed": sum(r.get("passed_tests", 0) for r in all_reports),
            "total_failed": sum(r.get("failed_tests", 0) for r in all_reports),
            "total_skipped": sum(r.get("skipped_tests", 0) for r in all_reports),
            "total_error": sum(r.get("error_tests", 0) for r in all_reports),
            "overall_success_rate": round(
                (sum(r.get("passed_tests", 0) for r in all_reports) / sum(r.get("total_tests", 1) for r in all_reports))
                * 100,
                2,
            ),
            "suite_reports": all_reports,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

        logger.info("综合报告摘要已保存: %(filepath)s")
        return str(filepath)
