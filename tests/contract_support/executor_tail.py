"""Tail helpers extracted from `tests/contract/test_contract_executor.py`."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List


class ContractTestExecutorTailMixin:
    """Support methods extracted from `ContractTestExecutor`."""

    def generate_test_report(self, results: List[Any], output_path: str, format: str = "html"):
        """生成测试报告"""
        if format.lower() == "html":
            self._generate_html_report(results, output_path)
        elif format.lower() == "json":
            self._generate_json_report(results, output_path)
        elif format.lower() == "markdown":
            self._generate_markdown_report(results, output_path)
        else:
            raise ValueError(f"不支持的报告格式: {format}")

    def _generate_html_report(self, results: List[Any], output_path: str):
        """生成HTML报告"""
        total = len(results)
        passed = len([result for result in results if result.status.value == "passed"])
        failed = len([result for result in results if result.status.value == "failed"])
        errors = len([result for result in results if result.status.value == "error"])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contract Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; text-align: center; }}
                .passed {{ background-color: #c8e6c9; }}
                .failed {{ background-color: #ffcdd2; }}
                .error {{ background-color: #ffccbc; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .details {{ margin-left: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Contract Test Report</h1>
                <p>Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>

            <div class="summary">
                <div class="stat">
                    <h3>Total Tests</h3>
                    <p style="font-size: 24px; margin: 0;">{total}</p>
                </div>
                <div class="stat passed">
                    <h3>Passed</h3>
                    <p style="font-size: 24px; margin: 0;">{passed}</p>
                </div>
                <div class="stat failed">
                    <h3>Failed</h3>
                    <p style="font-size: 24px; margin: 0;">{failed}</p>
                </div>
                <div class="stat error">
                    <h3>Errors</h3>
                    <p style="font-size: 24px; margin: 0;">{errors}</p>
                </div>
            </div>

            <h2>Test Results</h2>
        """

        for result in results:
            status_class = result.status.value
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result.test_case.name}</h3>
                <p><strong>Status:</strong> {result.status.value}</p>
                <p><strong>Execution Time:</strong> {result.execution_time:.2f}s</p>
                <p><strong>Endpoint:</strong> {result.test_case.method} {result.test_case.endpoint}</p>

                {f"<p><strong>Error:</strong> {result.error_message}</p>" if result.error_message else ""}

                {f'<div class="details"><h4>Response:</h4><pre>{json.dumps(result.response_body, indent=2)}</pre></div>' if result.response_body else ""}

                <div class="details">
                    <h4>Validations:</h4>
                    <ul>
            """

            for validation in result.validation_results:
                status_icon = "✓" if validation["status"] == "passed" else "✗"
                html_content += f"<li>{status_icon} {validation['validator']}: {validation['message']}</li>"

            html_content += """
                    </ul>
                </div>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(output_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(html_content)

        print(f"✓ HTML报告已生成: {output_path}")

    def _generate_json_report(self, results: List[Any], output_path: str):
        """生成JSON报告"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_tests": len(results),
            "results": [],
        }

        for result in results:
            result_data = {
                "test_case": {
                    "id": result.test_case.id,
                    "name": result.test_case.name,
                    "endpoint": result.test_case.endpoint,
                    "method": result.test_case.method,
                },
                "status": result.status.value,
                "execution_time": result.execution_time,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "response_status": result.response_status,
                "response_body": result.response_body,
                "error_message": result.error_message,
                "validation_results": result.validation_results,
            }
            report_data["results"].append(result_data)

        with open(output_path, "w", encoding="utf-8") as file_handle:
            json.dump(report_data, file_handle, indent=2, ensure_ascii=False)

        print(f"✓ JSON报告已生成: {output_path}")

    def _generate_markdown_report(self, results: List[Any], output_path: str):
        """生成Markdown报告"""
        total = len(results)
        passed = len([result for result in results if result.status.value == "passed"])
        failed = len([result for result in results if result.status.value == "failed"])
        errors = len([result for result in results if result.status.value == "error"])

        md_content = f"""# Contract Test Report

**Generated at:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

- **Total Tests:** {total}
- **Passed:** {passed} ({passed / total * 100:.1f}%)
- **Failed:** {failed} ({failed / total * 100:.1f}%)
- **Errors:** {errors} ({errors / total * 100:.1f}%)

## Test Results

"""

        for result in results:
            md_content += f"""### {result.test_case.name}

**Status:** {result.status.value}
**Execution Time:** {result.execution_time:.2f}s
**Endpoint:** `{result.test_case.method} {result.test_case.endpoint}`

"""

            if result.error_message:
                md_content += f"**Error:** {result.error_message}\n\n"

            if result.response_body:
                md_content += "**Response:**\n```json\n"
                md_content += json.dumps(result.response_body, indent=2)
                md_content += "\n```\n\n"

            if result.validation_results:
                md_content += "**Validations:**\n"
                for validation in result.validation_results:
                    status_icon = "✓" if validation["status"] == "passed" else "✗"
                    md_content += f"- {status_icon} {validation['validator']}: {validation['message']}\n"
                md_content += "\n"

        with open(output_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(md_content)

        print(f"✓ Markdown报告已生成: {output_path}")

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.copy()


async def demo_contract_executor(executor_cls: Any, suite_cls: Any, case_cls: Any, mode_enum: Any):
    """演示契约测试执行器"""
    print("🚀 演示契约测试执行器")

    executor = executor_cls(base_url="https://httpbin.org", max_workers=5, timeout=10)
    test_suite = suite_cls(name="HTTPBin Test Suite", description="Test suite for HTTPBin API")

    test_cases = [
        case_cls(
            id="test_001",
            name="Get User Agent",
            endpoint="/user-agent",
            method="GET",
            expected_status=200,
        ),
        case_cls(
            id="test_002",
            name="Post JSON Data",
            endpoint="/post",
            method="POST",
            body={"key": "value", "number": 123},
            expected_status=200,
        ),
        case_cls(
            id="test_003",
            name="Get Headers",
            endpoint="/headers",
            method="GET",
            expected_status=200,
            validations=[
                {"type": "status_code", "config": {}},
                {"type": "json_structure", "config": {"structure": {"headers": {}}}},
            ],
        ),
    ]

    test_suite.test_cases = test_cases

    try:
        results = await executor.execute_test_suite(test_suite, execution_mode=mode_enum.PARALLEL)
        executor.generate_test_report(results, output_path="contract_test_report.html", format="html")
        executor.generate_test_report(results, output_path="contract_test_report.json", format="json")
        executor.generate_test_report(results, output_path="contract_test_report.md", format="markdown")
        print("\n✅ 契约测试执行器演示完成")
    except Exception as error:
        print(f"❌ 演示失败: {error}")
