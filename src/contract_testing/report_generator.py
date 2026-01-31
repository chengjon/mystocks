"""
Contract Test Report Generator

Generates comprehensive reports from contract test results.
Supports JSON, HTML, and Markdown formats.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContractTestReportGenerator:
    """
    Generates contract testing reports in multiple formats.

    Task 12.1 Implementation: Report generation
    """

    def __init__(self):
        """Initialize report generator"""
        self.test_results = []
        self.consistency_summary = {}
        self.discrepancies = []
        self.start_time = None
        self.end_time = None

    def add_test_results(self, results: List[Dict]) -> None:
        """Add test results"""
        self.test_results = results

    def add_consistency_check(self, summary: Dict, discrepancies: List[Dict]) -> None:
        """Add consistency check results"""
        self.consistency_summary = summary
        self.discrepancies = discrepancies

    def set_time_range(self, start: datetime, end: datetime) -> None:
        """Set test execution time range"""
        self.start_time = start
        self.end_time = end

    def generate_json_report(self, output_path: str) -> None:
        """Generate JSON report"""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "start_time": self.start_time.isoformat() if self.start_time else "",
                "end_time": self.end_time.isoformat() if self.end_time else "",
            },
            "test_results": self.test_results,
            "consistency_check": self.consistency_summary,
            "discrepancies": self.discrepancies,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info("✅ Generated JSON report: %s", output_path)

    def generate_markdown_report(self, output_path: str) -> None:
        """Generate Markdown report"""
        lines = [
            "# Contract Test Report\n",
            f"**Generated**: {datetime.now().isoformat()}\n",
        ]

        # Test Results Summary
        if self.test_results:
            lines.append("## Test Results\n")
            total = len(self.test_results)
            passed = sum(1 for r in self.test_results if r.get("status") == "passed")
            failed = sum(1 for r in self.test_results if r.get("status") == "failed")

            lines.append(f"- **Total Tests**: {total}\n")
            lines.append(f"- **Passed**: {passed} ✅\n")
            lines.append(f"- **Failed**: {failed} ❌\n")
            lines.append(f"- **Pass Rate**: {(passed / total * 100) if total > 0 else 0:.1f}%\n\n")

            # Failed tests detail
            if failed > 0:
                lines.append("### Failed Tests\n")
                for result in self.test_results:
                    if result.get("status") == "failed":
                        lines.append(f"- `{result['endpoint_method']} {result['endpoint_path']}`\n")
                        if result.get("error_message"):
                            lines.append(f"  - Error: {result['error_message']}\n")
                lines.append("\n")

        # Consistency Check Summary
        if self.consistency_summary:
            lines.append("## API Consistency\n")
            lines.append(f"- **Consistency Score**: {self.consistency_summary.get('consistency_score', 0):.1f}/100\n")
            lines.append(f"- **Total Discrepancies**: {self.consistency_summary.get('total_discrepancies', 0)}\n")
            lines.append(f"- **Critical Issues**: {self.consistency_summary.get('critical_issues', 0)}\n")
            lines.append(f"- **Warnings**: {self.consistency_summary.get('warnings', 0)}\n\n")

        # Discrepancies Detail
        if self.discrepancies:
            critical = [d for d in self.discrepancies if d.get("severity") == "critical"]
            warnings = [d for d in self.discrepancies if d.get("severity") == "warning"]

            if critical:
                lines.append("### Critical Issues\n")
                for disc in critical:
                    lines.append(f"- **{disc['type']}** - `{disc['endpoint_method']} {disc['endpoint_path']}`\n")
                    lines.append(f"  - {disc['description']}\n")
                    lines.append(f"  - Suggestion: {disc['suggestion']}\n")
                lines.append("\n")

            if warnings:
                lines.append("### Warnings\n")
                for disc in warnings:
                    lines.append(f"- **{disc['type']}** - `{disc['endpoint_method']} {disc['endpoint_path']}`\n")
                    lines.append(f"  - {disc['description']}\n")

        # Write report
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        logger.info("✅ Generated Markdown report: %s", output_path)

    def generate_html_report(self, output_path: str) -> None:
        """Generate HTML report"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get("status") == "passed")
        failed = total - passed
        consistency = self.consistency_summary.get("consistency_score", 0)

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Contract Test Report</title>
    <style>
        * {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ margin: 20px; background: #f5f5f5; }}
        .container {{
            max-width: 1200px; margin: 0 auto; background: white;
            padding: 30px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin: 20px 0; }}
        .card {{
            background: #f9f9f9; padding: 15px; border-radius: 5px;
            text-align: center; border-left: 4px solid #007bff;
        }}
        .card h3 {{ margin: 0; color: #555; }}
        .card .number {{ font-size: 28px; font-weight: bold; color: #007bff; }}
        .passed {{ border-left-color: #28a745; }}
        .passed .number {{ color: #28a745; }}
        .failed {{ border-left-color: #dc3545; }}
        .failed .number {{ color: #dc3545; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-radius: 4px; }}
        .test-passed {{ background: #d4edda; }}
        .test-failed {{ background: #f8d7da; }}
        .consistency-critical {{ color: #dc3545; font-weight: bold; }}
        .consistency-warning {{ color: #ffc107; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
        tr:hover {{ background: #f9f9f9; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Contract Test Report</h1>
        <p><strong>Generated</strong>: {datetime.now().isoformat()}</p>

        <h2>Test Execution Summary</h2>
        <div class="summary">
            <div class="card">
                <h3>Total Tests</h3>
                <div class="number">{total}</div>
            </div>
            <div class="card passed">
                <h3>Passed</h3>
                <div class="number">{passed}</div>
            </div>
            <div class="card failed">
                <h3>Failed</h3>
                <div class="number">{failed}</div>
            </div>
            <div class="card">
                <h3>Pass Rate</h3>
                <div class="number">{(passed / total * 100) if total > 0 else 0:.1f}%</div>
            </div>
        </div>

        <h2>API Consistency Score</h2>
        <div class="card">
            <h3>Consistency Score</h3>
            <div class="number">{consistency:.1f}/100</div>
        </div>

        <h2>Critical Issues</h2>
        <p>Critical issues must be resolved before deployment.</p>
        <div class="issues">
            {"".join([
                f'<div class="test-result consistency-critical">❌ '
                f'{d["type"]}: {d["description"]}</div>'
                for d in self.discrepancies
                if d.get("severity") == "critical"
            ])}
        </div>

        <div class="footer">
            <p>Generated by MyStocks Contract Testing Framework</p>
        </div>
    </div>
</body>
</html>
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("✅ Generated HTML report: %s", output_path)

    def generate_all_reports(self, output_dir: str = "reports") -> None:
        """Generate all report formats"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generate_json_report(f"{output_dir}/contract_test_report_{timestamp}.json")
        self.generate_markdown_report(f"{output_dir}/contract_test_report_{timestamp}.md")
        self.generate_html_report(f"{output_dir}/contract_test_report_{timestamp}.html")

        logger.info("✅ Generated all reports in %s", output_dir)
