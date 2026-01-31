#!/usr/bin/env python3
"""
API File-Level Test Runner

Executes file-level tests for all API modules with parallel processing,
result aggregation, and comprehensive reporting.

Usage:
    python run_file_tests.py                    # Run all tests
    python run_file_tests.py --files market.py  # Run specific files
    python run_file_tests.py --priority P0      # Run by priority
    python run_file_tests.py --report json      # Generate JSON report
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api.file_tests import FileTestRunner, TestPriority


class FileTestRunnerCLI:
    """Command-line interface for file-level API testing"""

    def __init__(self):
        self.runner = FileTestRunner(max_workers=8)
        self.api_files = self._discover_api_files()

    def _discover_api_files(self) -> List[str]:
        """Discover all API files that need testing"""
        # Use absolute path from project root
        project_root = Path(__file__).parent.parent.parent
        api_dir = project_root / "web" / "backend" / "app" / "api"

        if not api_dir.exists():
            print(f"Warning: API directory {api_dir} not found")
            # Return mock file list for demonstration
            return [
                "web/backend/app/api/market.py",
                "web/backend/app/api/trade/routes.py",
                "web/backend/app/api/technical_analysis.py",
                "web/backend/app/api/strategy_management.py",
                "web/backend/app/api/risk_management.py",
                "web/backend/app/api/announcement.py",
                "web/backend/app/api/auth.py",
            ]

        api_files = []

        # Find all Python files with router decorators
        for py_file in api_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "@router." in content:
                        api_files.append(str(py_file.relative_to(Path.cwd())))
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")

        return sorted(api_files)

    def filter_files_by_priority(self, files: List[str], priority: TestPriority) -> List[str]:
        """Filter files by test priority"""
        priority_map = self.runner.file_priorities
        return [f for f in files if priority_map.get(f, TestPriority.P2_UTILITY) == priority]

    async def run_tests(
        self, files: Optional[List[str]] = None, priority: Optional[TestPriority] = None, report_format: str = "console"
    ) -> int:
        """Run file-level tests and return exit code"""

        # Determine which files to test
        if files:
            test_files = files
        elif priority:
            all_files = self.api_files
            test_files = self.filter_files_by_priority(all_files, priority)
        else:
            test_files = self.api_files

        if not test_files:
            print("No files to test")
            return 0

        print(f"🔍 Running file-level tests for {len(test_files)} API files...")
        print(f"Files: {', '.join(test_files[:5])}{'...' if len(test_files) > 5 else ''}")
        print()

        # Run the tests
        try:
            suite_result = await self.runner.run_file_tests(test_files)
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return 1

        # Generate reports
        if report_format == "json":
            self._generate_json_report(suite_result)
        elif report_format == "html":
            self._generate_html_report(suite_result)
        else:
            self._print_console_report(suite_result)

        # Return appropriate exit code
        if suite_result.failed_files > 0:
            return 1
        return 0

    def _print_console_report(self, result):
        """Print test results to console"""
        print("📊 API File-Level Test Results")
        print("=" * 50)
        print(f"Total Files: {result.total_files}")
        print(f"Tested Files: {result.tested_files}")
        print(f"Passed: {result.passed_files} ✅")
        print(f"Failed: {result.failed_files} ❌")
        print(f"Skipped: {result.skipped_files} ⏭️")
        print()
        print(f"Total Endpoints: {result.total_endpoints}")
        print(f"Tested Endpoints: {result.tested_endpoints}")
        print(f"Passed Endpoints: {result.passed_endpoints}")
        print(f"Failed Endpoints: {result.failed_endpoints}")
        print()
        print(".1f")
        print(".1f")
        print()
        print(".2f")

        # Show priority breakdown
        print("\n📋 Results by Priority:")
        for priority in [TestPriority.P0_CONTRACT, TestPriority.P1_CORE, TestPriority.P2_UTILITY]:
            files = result.get_files_by_priority(priority)
            if files:
                passed = sum(1 for f in files if f.status.name == "PASSED")
                print(f"  {priority.value}: {passed}/{len(files)} passed")

        # Show failed files
        failed_files = result.get_failed_files()
        if failed_files:
            print("\n❌ Failed Files:")
            for file_result in failed_files[:10]:  # Show first 10
                print(f"  - {file_result.file_name}: {file_result.status.value}")
                if file_result.errors:
                    print(f"    Error: {file_result.errors[0]}")
            if len(failed_files) > 10:
                print(f"  ... and {len(failed_files) - 10} more")

        # Show errors
        if result.errors:
            print("\n⚠️  Suite Errors:")
            for error in result.errors[:5]:
                print(f"  - {error}")

    def _generate_json_report(self, result):
        """Generate JSON test report"""
        report_path = Path("reports/api_file_tests.json")
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(result.to_json())

        print(f"📄 JSON report saved to: {report_path}")

    def _generate_html_report(self, result):
        """Generate HTML test report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>API File-Level Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>API File-Level Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Files:</strong> {result.total_files}</p>
        <p><strong>Tested:</strong> {result.tested_files}</p>
        <p><strong>Passed:</strong> <span class="passed">{result.passed_files}</span></p>
        <p><strong>Failed:</strong> <span class="failed">{result.failed_files}</span></p>
        <p><strong>Success Rate:</strong> {result.overall_success_rate:.1f}%</p>
        <p><strong>Coverage:</strong> {result.overall_coverage_rate:.1f}%</p>
        <p><strong>Duration:</strong> {result.total_duration:.2f}s</p>
    </div>

    <h2>File Results</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Priority</th>
            <th>Endpoints</th>
            <th>Status</th>
            <th>Success Rate</th>
            <th>Duration</th>
        </tr>
"""

        for file_result in result.file_results:
            status_class = file_result.status.name.lower()
            html_content += f"""
        <tr>
            <td>{file_result.file_name}</td>
            <td>{file_result.priority.value}</td>
            <td>{file_result.endpoint_count}</td>
            <td class="{status_class}">{file_result.status.value}</td>
            <td>{file_result.success_rate:.1f}%</td>
            <td>{file_result.duration:.2f}s</td>
        </tr>
"""

        html_content += """
    </table>
</body>
</html>
"""

        report_path = Path("reports/api_file_tests.html")
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"📄 HTML report saved to: {report_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="API File-Level Test Runner")
    parser.add_argument("--files", nargs="*", help="Specific files to test")
    parser.add_argument(
        "--priority", choices=["P0", "P1", "P2"], help="Test files by priority (P0=Contract, P1=Core, P2=Utility)"
    )
    parser.add_argument("--report", choices=["console", "json", "html"], default="console", help="Report format")
    parser.add_argument("--max-workers", type=int, default=8, help="Maximum parallel workers")
    parser.add_argument("--list-files", action="store_true", help="List all discovered API files")

    args = parser.parse_args()

    # Initialize runner
    runner = FileTestRunnerCLI()
    runner.runner.max_workers = args.max_workers

    if args.list_files:
        print("📂 Discovered API files:")
        for i, file in enumerate(runner.api_files, 1):
            priority = runner.runner.file_priorities.get(file, TestPriority.P2_UTILITY)
            print("2d")
        return 0

    # Convert priority string to enum
    priority = None
    if args.priority:
        priority_map = {"P0": TestPriority.P0_CONTRACT, "P1": TestPriority.P1_CORE, "P2": TestPriority.P2_UTILITY}
        priority = priority_map[args.priority]

    # Run tests
    exit_code = asyncio.run(runner.run_tests(files=args.files, priority=priority, report_format=args.report))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
