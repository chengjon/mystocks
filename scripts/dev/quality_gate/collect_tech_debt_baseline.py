#!/usr/bin/env python3
"""技术债基线采集脚本（Stage C 1.2）

输出字段：
- frontend_type_errors
- frontend_suppressions_count
- skip_xfail_count
- backend_todo_count
- backend_placeholder_count
- test_placeholder_assert_count

可选字段：
- generated_suppressions_count（默认仅统计 auto-imports.d.ts）
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

FRONTEND_SRC = PROJECT_ROOT / "web" / "frontend" / "src"
BACKEND_APP = PROJECT_ROOT / "web" / "backend" / "app"
CORE_SRC = PROJECT_ROOT / "src"
TEST_DIRS = [PROJECT_ROOT / "tests", PROJECT_ROOT / "web" / "backend" / "tests"]

SUPPRESSION_PATTERN = re.compile(
    r"@ts-ignore|@ts-expect-error|@ts-nocheck|\sas any\b|#\s*type:\s*ignore",
    re.IGNORECASE,
)
SKIP_XFAIL_PATTERN = re.compile(
    r"@pytest\.mark\.skip|@pytest\.mark\.xfail|pytest\.skip\(|pytest\.xfail\(",
    re.IGNORECASE,
)
TODO_PATTERN = re.compile(r"TODO|FIXME|HACK", re.IGNORECASE)
PLACEHOLDER_TEXT_PATTERN = re.compile(
    r"\b(mock|demo|hardcoded|sample data|placeholder)\b",
    re.IGNORECASE,
)
PLACEHOLDER_CODE_PATTERN = re.compile(r"\bNotImplementedError\b", re.IGNORECASE)
ASSERT_TRUE_PATTERN = re.compile(r"\bassert\s+True\b")
TS_ERROR_PATTERN = re.compile(r"error\s+TS\d+:")


@dataclass
class ScanResult:
    count: int
    files: int


def iter_files(base: Path, suffixes: tuple[str, ...]) -> Iterable[Path]:
    if not base.exists():
        return []
    return (p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in suffixes)


def count_pattern_in_files(paths: Iterable[Path], pattern: re.Pattern[str]) -> ScanResult:
    count = 0
    files = 0
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        matches = pattern.findall(text)
        if matches:
            files += 1
            count += len(matches)
    return ScanResult(count=count, files=files)


def collect_frontend_type_errors(timeout: int) -> dict:
    cmd = ["npm", "--prefix", "web/frontend", "run", "type-check"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "frontend_type_errors": -1,
            "type_check_exit_code": 124,
            "type_check_command": " ".join(cmd),
            "type_check_error": f"timeout after {timeout}s",
            "type_check_output_snippet": (exc.stdout or "")[:1000],
        }
    except FileNotFoundError:
        return {
            "frontend_type_errors": -1,
            "type_check_exit_code": 127,
            "type_check_command": " ".join(cmd),
            "type_check_error": "npm command not found",
        }

    output = f"{proc.stdout}\n{proc.stderr}"
    ts_errors = len(TS_ERROR_PATTERN.findall(output))
    return {
        "frontend_type_errors": ts_errors,
        "type_check_exit_code": proc.returncode,
        "type_check_command": " ".join(cmd),
    }


def collect_suppressions() -> dict:
    frontend_files = list(iter_files(FRONTEND_SRC, (".ts", ".tsx", ".vue", ".d.ts")))
    generated_candidates = {
        FRONTEND_SRC / "auto-imports.d.ts",
        PROJECT_ROOT / "web" / "frontend" / "auto-imports.d.ts",
    }

    generated_files = [p for p in generated_candidates if p.exists()]
    business_files = [p for p in frontend_files if p not in generated_candidates]

    business_result = count_pattern_in_files(business_files, SUPPRESSION_PATTERN)
    generated_result = count_pattern_in_files(generated_files, SUPPRESSION_PATTERN)

    return {
        "frontend_suppressions_count": business_result.count,
        "frontend_suppressions_files": business_result.files,
        "generated_suppressions_count": generated_result.count,
    }


def collect_skip_xfail() -> dict:
    test_files: list[Path] = []
    for test_dir in TEST_DIRS:
        test_files.extend(iter_files(test_dir, (".py",)))

    result = count_pattern_in_files(test_files, SKIP_XFAIL_PATTERN)
    return {
        "skip_xfail_count": result.count,
        "skip_xfail_files": result.files,
    }


def collect_backend_todo_and_placeholders() -> dict:
    backend_files = list(iter_files(BACKEND_APP, (".py",))) + list(iter_files(CORE_SRC, (".py",)))

    todo_result = count_pattern_in_files(backend_files, TODO_PATTERN)
    placeholder_text_result = count_pattern_in_files(backend_files, PLACEHOLDER_TEXT_PATTERN)
    placeholder_code_result = count_pattern_in_files(backend_files, PLACEHOLDER_CODE_PATTERN)

    return {
        "backend_todo_count": todo_result.count,
        "backend_todo_files": todo_result.files,
        "backend_placeholder_count": placeholder_text_result.count + placeholder_code_result.count,
        "backend_placeholder_files": max(placeholder_text_result.files, placeholder_code_result.files),
    }


def collect_test_placeholder_asserts() -> dict:
    test_files: list[Path] = []
    for test_dir in TEST_DIRS:
        test_files.extend(iter_files(test_dir, (".py",)))

    result = count_pattern_in_files(test_files, ASSERT_TRUE_PATTERN)
    return {
        "test_placeholder_assert_count": result.count,
        "test_placeholder_assert_files": result.files,
    }


def collect_baseline(timeout: int) -> dict:
    payload: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "metric_version": "v1",
    }

    payload.update(collect_frontend_type_errors(timeout=timeout))
    payload.update(collect_suppressions())
    payload.update(collect_skip_xfail())
    payload.update(collect_backend_todo_and_placeholders())
    payload.update(collect_test_placeholder_asserts())

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect technical debt baseline metrics")
    parser.add_argument(
        "--output",
        default="reports/analysis/tech-debt-baseline.json",
        help="Output JSON path (relative to project root)",
    )
    parser.add_argument(
        "--type-check-timeout",
        type=int,
        default=600,
        help="Timeout seconds for frontend type-check command",
    )
    args = parser.parse_args()

    baseline = collect_baseline(timeout=args.type_check_timeout)

    output_path = (PROJECT_ROOT / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[tech-debt-baseline] written: {output_path}")
    print(json.dumps(baseline, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
