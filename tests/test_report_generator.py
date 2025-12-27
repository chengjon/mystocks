#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告生成器

支持多种格式的测试报告生成：
- JSON: 机器可读的结果
- HTML: 漂亮的可视化报告
- Markdown: 文档友好的格式
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """单个测试结果"""

    name: str
    module: str
    status: str  # passed, failed, skipped, error
    duration: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuiteResult:
    """测试套件结果"""

    name: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    test_results: List[TestResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed / self.total_tests * 100


@dataclass
class ReportConfig:
    """报告配置"""

    output_dir: str = "reports"
    formats: List[str] = field(default_factory=lambda: ["json", "html", "markdown"])
    include_tracebacks: bool = True
    theme: str = "light"


class TestReportGenerator:
    """测试报告生成器"""

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.suite_results: List[TestSuiteResult] = []

    def add_suite_result(self, result: TestSuiteResult):
        """添加测试套件结果"""
        self.suite_results.append(result)

    def add_result(
        self,
        suite_name: str,
        name: str,
        module: str,
        status: str,
        duration: float,
        error_message: Optional[str] = None,
        error_traceback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """添加单个测试结果"""
        suite = next((s for s in self.suite_results if s.name == suite_name), None)
        if not suite:
            suite = TestSuiteResult(name=suite_name)
            self.suite_results.append(suite)

        result = TestResult(
            name=name,
            module=module,
            status=status,
            duration=duration,
            error_message=error_message,
            error_traceback=error_traceback if self.config.include_tracebacks else None,
            metadata=metadata or {},
        )
        suite.test_results.append(result)
        suite.total_tests += 1
        suite.duration += duration

        if status == "passed":
            suite.passed += 1
        elif status == "failed":
            suite.failed += 1
        elif status == "skipped":
            suite.skipped += 1
        else:
            suite.errors += 1

    def generate_all(self, report_name: str = "test_report") -> Dict[str, str]:
        """
        生成所有格式的报告

        Returns:
            Dict: 生成的报告文件路径
        """
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        if "json" in self.config.formats:
            json_path = output_dir / f"{report_name}.json"
            self._generate_json(json_path)
            generated["json"] = str(json_path)

        if "html" in self.config.formats:
            html_path = output_dir / f"{report_name}.html"
            self._generate_html(html_path)
            generated["html"] = str(html_path)

        if "markdown" in self.config.formats:
            md_path = output_dir / f"{report_name}.md"
            self._generate_markdown(md_path)
            generated["markdown"] = str(md_path)

        return generated

    def _generate_json(self, path: Path):
        """生成 JSON 格式报告"""
        data = {
            "report_name": "Test Report",
            "generated_at": datetime.now().isoformat(),
            "suites": [],
            "summary": self._get_summary(),
        }

        for suite in self.suite_results:
            suite_data = {
                "name": suite.name,
                "total_tests": suite.total_tests,
                "passed": suite.passed,
                "failed": suite.failed,
                "skipped": suite.skipped,
                "errors": suite.errors,
                "duration": suite.duration,
                "success_rate": suite.success_rate,
                "tests": [
                    {
                        "name": r.name,
                        "module": r.module,
                        "status": r.status,
                        "duration": r.duration,
                        "error": r.error_message,
                        "metadata": r.metadata,
                    }
                    for r in suite.test_results
                ],
            }
            data["suites"].append(suite_data)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _generate_html(self, path: Path):
        """生成 HTML 格式报告"""
        theme = self.config.theme

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report</title>
    <style>
        :root {{
            --primary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --bg-color: #f5f6fa;
            --card-bg: #ffffff;
            --text-color: #2c3e50;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary-color), #2980b9);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}

        .header .meta {{
            margin-top: 10px;
            opacity: 0.9;
        }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .card {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            text-align: center;
        }}

        .card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .card .label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}

        .card.success .value {{ color: var(--success-color); }}
        .card.danger .value {{ color: var(--danger-color); }}
        .card.warning .value {{ color: var(--warning-color); }}

        .suite {{
            background: var(--card-bg);
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            overflow: hidden;
        }}

        .suite-header {{
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .suite-header:hover {{
            background: #f1f3f5;
        }}

        .suite-title {{
            font-weight: bold;
            font-size: 1.1em;
        }}

        .suite-stats {{
            display: flex;
            gap: 15px;
            font-size: 0.9em;
        }}

        .stat {{
            padding: 3px 10px;
            border-radius: 12px;
            background: #eee;
        }}

        .stat.passed {{ background: #d4edda; color: #155724; }}
        .stat.failed {{ background: #f8d7da; color: #721c24; }}
        .stat.skipped {{ background: #fff3cd; color: #856404; }}

        .suite-details {{
            display: none;
            padding: 15px 20px;
        }}

        .suite-details.show {{
            display: block;
        }}

        .test-item {{
            padding: 10px 15px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .test-item:last-child {{
            border-bottom: none;
        }}

        .test-name {{
            flex: 1;
        }}

        .test-meta {{
            font-size: 0.85em;
            color: #7f8c8d;
        }}

        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }}

        .status-badge.passed {{
            background: #d4edda;
            color: #155724;
        }}

        .status-badge.failed {{
            background: #f8d7da;
            color: #721c24;
        }}

        .status-badge.skipped {{
            background: #fff3cd;
            color: #856404;
        }}

        .error-details {{
            background: #fff5f5;
            padding: 15px;
            margin-top: 10px;
            border-radius: 5px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }}

        .progress-bar {{
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--success-color), #2ecc71);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Report</h1>
            <div class="meta">
                Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </div>

        <div class="summary-cards">
            <div class="card">
                <div class="label">Total Tests</div>
                <div class="value">{self._get_summary()["total"]}</div>
            </div>
            <div class="card success">
                <div class="label">Passed</div>
                <div class="value">{self._get_summary()["passed"]}</div>
            </div>
            <div class="card danger">
                <div class="label">Failed</div>
                <div class="value">{self._get_summary()["failed"]}</div>
            </div>
            <div class="card warning">
                <div class="label">Skipped</div>
                <div class="value">{self._get_summary()["skipped"]}</div>
            </div>
        </div>

        <div class="card">
            <div class="label">Success Rate</div>
            <div class="value">{self._get_summary()["success_rate"]:.1f}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {self._get_summary()["success_rate"]}%"></div>
            </div>
        </div>
"""

        for suite in self.suite_results:
            html_content += f"""
        <div class="suite">
            <div class="suite-header" onclick="toggleSuite(this)">
                <div class="suite-title">{suite.name}</div>
                <div class="suite-stats">
                    <span class="stat passed">{suite.passed} passed</span>
                    <span class="stat failed">{suite.failed} failed</span>
                    <span class="stat skipped">{suite.skipped} skipped</span>
                </div>
            </div>
            <div class="suite-details">
"""

            for result in suite.test_results:
                status_class = (
                    "passed" if result.status == "passed" else "failed" if result.status == "failed" else "skipped"
                )
                error_html = ""
                if result.error_message and self.config.include_tracebacks:
                    error_html = f"""
                <div class="error-details">
                    <strong>Error:</strong> {result.error_message}
                    <pre>{result.error_traceback or ""}</pre>
                </div>
"""

                html_content += f"""
                <div class="test-item">
                    <div class="test-name">
                        <div>{result.name}</div>
                        <div class="test-meta">{result.module} • {result.duration:.2f}s</div>
                        {error_html}
                    </div>
                    <span class="status-badge {status_class}">{result.status}</span>
                </div>
"""

            html_content += """
            </div>
        </div>
"""

        html_content += """
        <script>
            function toggleSuite(header) {
                const details = header.nextElementSibling;
                details.classList.toggle('show');
            }
        </script>
    </div>
</body>
</html>
"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_markdown(self, path: Path):
        """生成 Markdown 格式报告"""
        summary = self._get_summary()

        md_content = f"""# Test Report

**Generated at**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| Total Tests | {summary["total"]} |
| Passed | {summary["passed"]} ✅ |
| Failed | {summary["failed"]} ❌ |
| Skipped | {summary["skipped"]} ⏭️ |
| Success Rate | {summary["success_rate"]:.1f}% |

---

## 📋 Test Suites

"""

        for suite in self.suite_results:
            status_emoji = "✅" if suite.failed == 0 else "❌" if suite.failed > 0 else "⏭️"
            md_content += f"""### {status_emoji} {suite.name}

- **Total**: {suite.total_tests} tests
- **Passed**: {suite.passed}
- **Failed**: {suite.failed}
- **Skipped**: {suite.skipped}
- **Duration**: {suite.duration:.2f}s
- **Success Rate**: {suite.success_rate:.1f}%

"""

            if suite.failed > 0:
                md_content += "#### Failed Tests\n\n"
                for result in suite.test_results:
                    if result.status == "failed":
                        md_content += f"- ❌ **{result.name}** ({result.module})\n"
                        if result.error_message:
                            md_content += f"  - Error: {result.error_message}\n"

        md_content += """
---

*Generated by Comprehensive Testing Solution*
"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)

    def _get_summary(self) -> Dict[str, Any]:
        """获取汇总信息"""
        total = sum(s.total_tests for s in self.suite_results)
        passed = sum(s.passed for s in self.suite_results)
        failed = sum(s.failed for s in self.suite_results)
        skipped = sum(s.skipped for s in self.suite_results)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": passed / total * 100 if total > 0 else 0,
        }


def run_tests_with_report(
    test_paths: List[str],
    report_name: str = "test_report",
    formats: Optional[List[str]] = None,
) -> Dict[str, str]:
    """
    运行测试并生成报告

    Args:
        test_paths: 测试路径列表
        report_name: 报告名称
        formats: 输出格式列表

    Returns:
        生成的报告文件路径
    """
    import subprocess

    config = ReportConfig(
        output_dir="reports",
        formats=formats or ["json", "html", "markdown"],
        include_tracebacks=True,
    )

    generator = TestReportGenerator(config)

    # 运行测试
    print(f"🧪 Running tests: {test_paths}")
    result = subprocess.run(
        ["python", "-m", "pytest", "-v", "--tb=short", "-q"] + test_paths,
        capture_output=True,
        text=True,
    )

    # 解析测试结果
    lines = result.stdout.split("\n")
    current_suite = "default"

    for line in lines:
        if "::" in line and "::test_" in line:
            parts = line.split("::")
            if len(parts) >= 2:
                module = parts[0].replace("/", ".")
                test_name = parts[1]

                if "PASSED" in line:
                    status = "passed"
                elif "FAILED" in line:
                    status = "failed"
                elif "SKIPPED" in line:
                    status = "skipped"
                else:
                    continue

                duration = 0.0
                if "--" in line:
                    try:
                        duration = float(line.split("--")[-1].strip().split()[0])
                    except (ValueError, IndexError):
                        pass

                generator.add_result(
                    suite_name=current_suite,
                    name=test_name,
                    module=module,
                    status=status,
                    duration=duration,
                )

    return generator.generate_all(report_name)


if __name__ == "__main__":

    # 示例：生成测试报告
    generator = TestReportGenerator(
        ReportConfig(
            output_dir="reports",
            formats=["json", "html", "markdown"],
        )
    )

    # 添加一些模拟测试结果
    generator.add_result(
        suite_name="ai_tests",
        name="test_ai_assisted_testing",
        module="tests.ai.test_ai_assisted_testing",
        status="passed",
        duration=1.234,
    )

    generator.add_result(
        suite_name="ai_tests",
        name="test_data_analyzer",
        module="tests.ai.test_data_analyzer",
        status="passed",
        duration=0.876,
    )

    generator.add_result(
        suite_name="contract_tests",
        name="test_contract_validator",
        module="tests.contract.test_contract_validator",
        status="passed",
        duration=2.345,
    )

    generator.add_result(
        suite_name="performance_tests",
        name="test_benchmark",
        module="tests.performance.test_benchmark",
        status="failed",
        duration=0.123,
        error_message="AssertionError: throughput too low",
        error_traceback="AssertionError: 100 ops/s < 1000 ops/s expected",
    )

    # 生成报告
    reports = generator.generate_all("comprehensive_test_report")

    print("✅ Reports generated:")
    for fmt, path in reports.items():
        print(f"  - {fmt.upper()}: {path}")

    print("\n📊 Summary:")
    summary = generator._get_summary()
    print(f"  Total: {summary['total']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
