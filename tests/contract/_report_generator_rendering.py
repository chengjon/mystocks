#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""契约测试报告渲染与摘要导出辅助方法。"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from .models import ContractTestReport

logger = logging.getLogger(__name__)


class ContractTestReportGeneratorRenderingMixin:
    """契约测试报告渲染与摘要导出方法集。"""

    def _generate_markdown_report(self, report: ContractTestReport) -> str:
        """生成 Markdown 格式报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_report_{timestamp}.md"
        filepath = self.output_dir / filename

        md_content = self._generate_markdown_content(report)

        with open(filepath, "w", encoding="utf-8") as file_obj:
            file_obj.write(md_content)

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

        md_content += "## 测试结果详情\n\n"
        md_content += "| 测试用例 | 端点 | 类别 | 状态 | 耗时(ms) | 响应时间(ms) | 详情 |\n"
        md_content += "|----------|------|------|------|----------|--------------|------|\n"

        for result in report.results:
            status_badge = result.status.value.replace("_", " ").title()
            details = ""

            if result.error_message:
                details = f"错误: {result.error_message}"

            if result.validation_results:
                valid_count = sum(1 for item in result.validation_results if item["valid"])
                total_count = len(result.validation_results)
                if details:
                    details += " | "
                details += f"验证: {valid_count}/{total_count}"

            md_content += f"| {result.test_case.name} | {result.test_case.endpoint} | "
            md_content += f"{result.test_case.category.value.replace('_', ' ').title()} | "
            md_content += f"{status_badge} | {result.duration:.2f} | "
            md_content += f"{result.performance_metrics.get('response_time_ms', 0):.2f} | {details} |\n"

        if report.recommendations:
            md_content += "\n## 优化建议\n\n"
            for index, recommendation in enumerate(report.recommendations, 1):
                md_content += f"{index}. {recommendation}\n"

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
            "total_tests": sum(report.get("total_tests", 0) for report in all_reports),
            "total_passed": sum(report.get("passed_tests", 0) for report in all_reports),
            "total_failed": sum(report.get("failed_tests", 0) for report in all_reports),
            "total_skipped": sum(report.get("skipped_tests", 0) for report in all_reports),
            "total_error": sum(report.get("error_tests", 0) for report in all_reports),
            "overall_success_rate": round(
                (sum(report.get("passed_tests", 0) for report in all_reports) / sum(report.get("total_tests", 1) for report in all_reports))
                * 100,
                2,
            ),
            "suite_reports": all_reports,
        }

        with open(filepath, "w", encoding="utf-8") as file_obj:
            json.dump(summary, file_obj, ensure_ascii=False, indent=2, default=str)

        logger.info("综合报告摘要已保存: %(filepath)s")
        return str(filepath)
