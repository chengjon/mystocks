#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Python 文件大小的兼容入口。

该脚本保留历史 CLI 形态，但内部复用 canonical file-size guardrail 逻辑。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.compliance.file_size_guardrail import build_report


def to_python_file_report(report: dict[str, object], limit: int) -> dict[str, object]:
    violations = [
        {"path": item["path"], "lines": item["lines"]}
        for item in report["violations"]
    ]
    return {
        "total_files": report["checked_files"],
        "oversized_files": violations,
        "oversized_count": report["oversized_count"],
        "limit": limit,
    }


def print_report(report: dict[str, object], output_format: str = "text") -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("\n文件大小检查报告")
    print("=====================")
    print(f"检查限制: {report['limit']} 行")
    print(f"总文件数: {report['total_files']}")
    print(f"超过限制的文件数: {report['oversized_count']}")

    if report["oversized_files"]:
        print("\n超过限制的文件:")
        for file_info in sorted(
            report["oversized_files"], key=lambda item: item["lines"], reverse=True
        ):
            print(f"  - {file_info['path']}: {file_info['lines']} 行")
    else:
        print("\n没有文件超过限制。")

    print("\n建议:")
    if report["oversized_files"]:
        print("  - 根据《代码文件长度优化规范》，建议对这些文件进行模块化拆分")
        print("  - 参考 'docs/guides/MODULAR_CODE_USAGE_GUIDE.md' 了解拆分最佳实践")
    else:
        print("  - 所有文件都符合《代码文件长度优化规范》")


def main() -> int:
    parser = argparse.ArgumentParser(description="检查Python文件大小")
    parser.add_argument("--limit", type=int, default=2000, help="文件行数限制，默认为2000")
    parser.add_argument("--exclude-dir", action="append", default=[], help="排除的目录名称，可以多次使用")
    parser.add_argument("--exclude-file", action="append", default=[], help="排除的文件名，可以多次使用")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("--root-dir", type=str, default=".", help="检查的根目录")
    args = parser.parse_args()

    report = build_report(
        args.root_dir,
        limits={".py": args.limit},
        ignore_directories={".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", *args.exclude_dir},
        exclude_files=set(args.exclude_file),
    )
    python_report = to_python_file_report(report, args.limit)
    print_report(python_report, args.format)
    return 1 if python_report["oversized_files"] else 0


if __name__ == "__main__":
    sys.exit(main())
