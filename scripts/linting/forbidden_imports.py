#!/usr/bin/env python3
"""SOT §八.1 CI强制校验脚本: forbidden_imports.

Phase 1.1 (B4.014) 交付. 检查全仓库 Python 源代码是否直接 import
akshare / baostock / zzshare / eltdx 等退役数据源库.

参考: architecture/standards/openstock-consumer-boundary-sot.md §一 与 §八.

用法:
    python scripts/linting/forbidden_imports.py                # 默认 baseline 模式
    python scripts/linting/forbidden_imports.py --strict       # 任何违规 exit 1 (Phase 3 后启用)
    python scripts/linting/forbidden_imports.py --baseline-file .planning/forbidden_imports_baseline.txt
    python scripts/linting/forbidden_imports.py --path src     # 指定扫描路径

退出码:
    0 — 无新增违规 (baseline 模式: 当前违规 ≤ baseline 数量)
    1 — 存在新增违规 (strict 模式: 任何违规 / baseline 模式: 当前违规 > baseline)
    2 — 脚本自身错误

Phase 接入策略 (SOT §八.1):
    Phase 1.x: 默认 baseline 模式, 仅证明 PR 未新增违规, 不阻断历史债务
    Phase 2:   跟随迁移 PR 同步收紧 baseline (decrement 模式)
    Phase 3:   切换为 strict 模式, 任何违规阻断合入
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# SOT §一: 禁止直接 import 的退役数据源库.
# 形如 `import akshare` / `from akshare import ...` / `import akshare as ...`.
FORBIDDEN_MODULES: tuple[str, ...] = (
    "akshare",
    "baostock",
    "zzshare",
    "eltdx",
)

# SOT §一: 唯一允许引用退役库的例外目录.
# 注: tests/ 仅当测试目的明确为"验证某退役路径已不再被调用"时允许.
EXCEPTION_PATHS: tuple[str, ...] = (
    "web/backend/app/services/openstock_client.py",
    "tests/",
)

# 匹配 import 形式的正则.
# 捕获三种语法: `import X` / `import X.Y` / `from X import ...` / `from X.Y import ...`
IMPORT_PATTERN = re.compile(
    r"^\s*(?:from\s+(?P<from_mod>[a-zA-Z_][a-zA-Z0-9_.]*)\s+import|import\s+(?P<import_mod>[a-zA-Z_][a-zA-Z0-9_.]*))",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Violation:
    """单条违规记录."""

    file_path: str
    line_number: int
    line_content: str
    module: str

    def format(self) -> str:
        return (
            f"{self.file_path}:{self.line_number}: "
            f"forbidden import of '{self.module}' "
            f"(SOT §一 OpenStock consumer boundary)\n"
            f"    > {self.line_content.strip()}"
        )


def is_exception_path(file_path: Path, repo_root: Path) -> bool:
    """判断文件是否在 SOT §一定义的例外目录内."""
    try:
        rel = file_path.relative_to(repo_root)
    except ValueError:
        return False
    rel_posix = rel.as_posix()
    for exception in EXCEPTION_PATHS:
        if exception.endswith("/"):
            if rel_posix.startswith(exception):
                return True
        else:
            if rel_posix == exception:
                return True
    return False


def scan_file(file_path: Path) -> Iterable[Violation]:
    """扫描单个 Python 文件的违规 import."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return

    for match in IMPORT_PATTERN.finditer(text):
        module = match.group("from_mod") or match.group("import_mod")
        if not module:
            continue
        root_module = module.split(".")[0]
        if root_module not in FORBIDDEN_MODULES:
            continue
        line_number = text.count("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.start())
        if line_end == -1:
            line_end = len(text)
        line_content = text[
            text.rfind("\n", 0, match.start()) + 1 : line_end
        ]
        yield Violation(
            file_path=str(file_path),
            line_number=line_number,
            line_content=line_content,
            module=root_module,
        )


def iter_python_files(root: Path) -> Iterable[Path]:
    """遍历根目录下所有 Python 文件, 排除明显的非源代码目录."""
    exclude_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "build",
        "dist",
        ".tox",
    }
    for path in root.rglob("*.py"):
        if any(part in exclude_dirs for part in path.parts):
            continue
        yield path


def run_scan(
    scan_paths: list[Path], repo_root: Path
) -> tuple[list[Violation], int]:
    """执行扫描, 返回 (违规清单, 扫描文件数)."""
    violations: list[Violation] = []
    files_scanned = 0
    for path in scan_paths:
        if path.is_file() and path.suffix == ".py":
            files = [path]
        elif path.is_dir():
            files = list(iter_python_files(path))
        else:
            continue
        for file_path in files:
            files_scanned += 1
            if is_exception_path(file_path, repo_root):
                continue
            violations.extend(scan_file(file_path))
    return violations, files_scanned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SOT §八.1 forbidden imports CI lint",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=None,
        help="指定扫描路径 (可多次指定, 默认为仓库根目录)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="任何违规 exit 1 (Phase 3 后启用, 默认关闭)",
    )
    parser.add_argument(
        "--baseline-file",
        default=None,
        help=(
            "baseline 文件路径, 内含历史违规数量阈值; "
            "当前违规数 > baseline 时 exit 1. "
            "Phase 1.x 默认 CI 模式."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="仓库根目录 (默认自动探测, 包含 .git 的目录)",
    )
    args = parser.parse_args(argv)

    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                repo_root = current
                break
            current = current.parent
        else:
            repo_root = Path.cwd()

    if args.path:
        scan_paths = [Path(p).resolve() for p in args.path]
    else:
        scan_paths = [repo_root]

    violations, files_scanned = run_scan(scan_paths, repo_root)

    print(
        f"[forbidden_imports] scanned {files_scanned} file(s) under "
        f"{', '.join(str(p) for p in scan_paths)}",
        file=sys.stderr,
    )

    if not violations:
        print(
            "[forbidden_imports] PASS — no forbidden imports detected",
            file=sys.stderr,
        )
        return 0

    print(
        f"[forbidden_imports] {len(violations)} violation(s) found:",
        file=sys.stderr,
    )
    for v in violations:
        print(v.format(), file=sys.stderr)

    # Phase 3 strict 模式: 任何违规阻断
    if args.strict:
        print(
            f"[forbidden_imports] FAIL (strict mode) — {len(violations)} violation(s)",
            file=sys.stderr,
        )
        return 1

    # Phase 1.x/2 baseline 模式: 仅在新增违规时阻断
    if args.baseline_file:
        baseline_path = Path(args.baseline_file)
        try:
            baseline_text = baseline_path.read_text(encoding="utf-8").strip()
            baseline_count = int(baseline_text.splitlines()[0]) if baseline_text else 0
        except (OSError, ValueError):
            print(
                f"[forbidden_imports] WARN — baseline file {args.baseline_file} "
                f"unreadable, treating as 0",
                file=sys.stderr,
            )
            baseline_count = 0

        if len(violations) > baseline_count:
            print(
                f"[forbidden_imports] FAIL (baseline mode) — "
                f"{len(violations)} current > {baseline_count} baseline; "
                f"PR introduces new violations",
                file=sys.stderr,
            )
            return 1
        print(
            f"[forbidden_imports] PASS (baseline mode) — "
            f"{len(violations)} current ≤ {baseline_count} baseline",
            file=sys.stderr,
        )
        return 0

    # 默认 (Phase 1.x): 仅打印违规清单, 不阻断 (基线尚未建立)
    print(
        "[forbidden_imports] WARN (advisory mode) — violations exist but not strict; "
        "Phase 1.x baseline collection only",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
