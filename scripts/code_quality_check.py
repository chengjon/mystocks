#!/usr/bin/env python3
"""
代码质量检查脚本
运行 ruff 和 mypy 检查，并生成报告
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime


class CodeQualityChecker:
    """代码质量检查器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "ruff": {},
            "mypy": {},
            "summary": {},
        }

    def run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[int, str, str]:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=cwd or self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def check_ruff(self) -> Dict:
        """检查代码风格"""
        print("🔍 Running ruff check...")

        # 检查代码风格
        returncode, stdout, stderr = self.run_command(
            ["ruff", "check", ".", "--output-format=json"]
        )

        if returncode == 0:
            self.results["ruff"]["status"] = "passed"
            self.results["ruff"]["errors"] = []
            self.results["ruff"]["warnings"] = []
        else:
            try:
                issues = json.loads(stdout)
                self.results["ruff"]["status"] = "failed"
                self.results["ruff"]["errors"] = [
                    issue
                    for issue in issues
                    if issue.get("code", "").startswith(("E", "F"))
                ]
                self.results["ruff"]["warnings"] = [
                    issue
                    for issue in issues
                    if issue.get("code", "").startswith(("W", "I"))
                ]
            except:
                self.results["ruff"]["status"] = "error"
                self.results["ruff"]["errors"] = [
                    {"message": "Failed to parse ruff output"}
                ]

        # 检查格式
        returncode_fmt, stdout_fmt, stderr_fmt = self.run_command(
            ["ruff", "format", "--check", "."]
        )

        self.results["ruff"]["format_ok"] = returncode_fmt == 0

        print(f"   Ruff: {self.results['ruff']['status']}")
        print(f"   Format: {'✅' if self.results['ruff']['format_ok'] else '❌'}")

        return self.results["ruff"]

    def check_mypy(self) -> Dict:
        """检查类型"""
        print("🔍 Running mypy check...")

        returncode, stdout, stderr = self.run_command(
            [
                "mypy",
                ".",
                "--ignore-missing-imports",
                "--show-error-codes",
                "--no-error-summary",
            ]
        )

        if returncode == 0:
            self.results["mypy"]["status"] = "passed"
            self.results["mypy"]["errors"] = []
        else:
            self.results["mypy"]["status"] = "failed"
            self.results["mypy"]["errors"] = (
                stderr.split("\n") if stderr else ["Unknown error"]
            )

        print(f"   MyPy: {self.results['mypy']['status']}")

        return self.results["mypy"]

    def generate_summary(self):
        """生成检查摘要"""
        ruff_errors = len(self.results["ruff"].get("errors", []))
        ruff_warnings = len(self.results["ruff"].get("warnings", []))
        mypy_errors = len(self.results["mypy"].get("errors", []))

        total_issues = ruff_errors + ruff_warnings + mypy_errors

        self.results["summary"] = {
            "total_issues": total_issues,
            "ruff_errors": ruff_errors,
            "ruff_warnings": ruff_warnings,
            "mypy_errors": mypy_errors,
            "overall_status": "passed" if total_issues == 0 else "failed",
        }

        print("\n📊 Code Quality Summary:")
        print(f"   Total Issues: {total_issues}")
        print(f"   Ruff Errors: {ruff_errors}")
        print(f"   Ruff Warnings: {ruff_warnings}")
        print(f"   MyPy Errors: {mypy_errors}")
        print(f"   Overall: {'✅ PASSED' if total_issues == 0 else '❌ FAILED'}")

    def save_report(self):
        """保存检查报告"""
        report_file = self.project_root / "code_quality_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Report saved to: {report_file}")

    def run(self):
        """运行完整的代码质量检查"""
        print("🚀 Starting code quality check...")
        print("=" * 50)

        self.check_ruff()
        self.check_mypy()
        self.generate_summary()
        self.save_report()

        # 根据检查结果决定退出状态
        return 0 if self.results["summary"]["overall_status"] == "passed" else 1


def main():
    """主函数"""
    checker = CodeQualityChecker()
    return checker.run()


if __name__ == "__main__":
    sys.exit(main())
