#!/usr/bin/env python3
"""
目录结构合规性检查脚本

检查新创建的文件/目录是否符合项目规范：
1. 新文件必须在允许的目录范围内
2. 新子目录必须包含 __init__.py
3. 不允许在禁止目录中创建文件
"""

import os
import subprocess
import sys
from pathlib import Path

# 允许的顶层目录
ALLOWED_TOP_DIRS = [
    "src/",
    "scripts/",
    "docs/",
    "tests/",
    "config/",
    "web/",
    "openspec/",
    "services/",
    "monitoring-stack/",
    "reports/",
    "gpu_api_system/",
    "ai_test_optimizer_toolkit/",
    ".github/",
    ".claude/",
]

# 允许的根目录文件（仅用于新文件）
ALLOWED_ROOT_FILES = {
    # 项目入口/说明
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "IFLOW.md",
    "LICENSE",
    "CHANGELOG.md",
    # Git / 开发工具
    ".gitignore",
    ".gitattributes",
    ".coveragerc",
    ".env.example",
    ".pre-commit-config.yaml",
    ".pre-commit-hooks.yaml",
    # Python 工具链
    "pyproject.toml",
    "pytest.ini",
    "mypy.ini",
    "conftest.py",
    # Node / E2E 工具链
    "package.json",
    "package-lock.json",
    # OpenSpec / OpenCode
    "opencode.json",
    ".mcp.json",
    # 兼容入口点
    "core.py",
    "data_access.py",
    "monitoring.py",
    "unified_manager.py",
}

# `.claude/` is a special top-level directory: it often contains local tooling and
# user-specific files that should not be committed. For new files, we enforce a
# tight allowlist that mirrors `.gitignore` exceptions.
ALLOWED_CLAUDE_FILES = {
    ".claude/settings.json",
    ".claude/build-checker-python.json",
    ".claude/skill-rules.json",
}

# Reports are allowed under `reports/` but should not be committed unless explicitly curated.
# Enforce a strict rule: new JSON/HTML reports are not allowed by default.
DISALLOWED_REPORT_PREFIXES = ("reports/",)

DISALLOWED_REPORT_SUFFIXES = {
    ".json",
    ".html",
}

# NOTE: this script is executed as a file (not a package module) in CI.
# Add `scripts/` to sys.path so we can import `hooks.*`.
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from hooks.deny_list import is_denied_path, should_ignore
except Exception:  # pragma: no cover
    from .deny_list import is_denied_path, should_ignore


def get_staged_changes() -> list[tuple[str, Path]]:
    """获取暂存的变更 (status, path).

    本脚本主要用于约束“新文件”的位置，不应阻止对历史遗留目录中文件的正常修改。
    """

    completed = subprocess.run(
        ["git", "diff", "--cached", "--name-status"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return []

    changes: list[tuple[str, Path]] = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        raw_status = parts[0].strip()
        status_code = raw_status[:1] if raw_status else raw_status

        # Rename/Copy entries have 3 columns: STATUS<TAB>OLD<TAB>NEW
        if status_code in {"R", "C"} and len(parts) >= 3:
            changes.append((status_code, Path(parts[2])))
            continue

        if len(parts) >= 2:
            changes.append((status_code or raw_status, Path(parts[1])))
    return changes


def check_file_location(file_path: Path) -> bool:
    """检查文件是否在允许的位置"""
    file_str = str(file_path)

    # Root-level files are allowed only if they are in the explicit allowlist.
    if file_path.parent == Path("."):
        if file_path.name in ALLOWED_ROOT_FILES:
            return True
        print(f"❌ 文件 {file_path} 不在允许的根目录文件 allowlist 内")
        print(f"   允许的根目录文件: {sorted(ALLOWED_ROOT_FILES)}")
        return False

    # `.claude/` is allowed at top-level, but only a small subset of files should be committed.
    if file_str.startswith(".claude/"):
        if file_str in ALLOWED_CLAUDE_FILES:
            return True
        if file_str.startswith(".claude/hooks/") and file_path.suffix == ".sh":
            return True

        print(f"❌ 文件 {file_path} 不在允许的 .claude/ 受控范围内")
        print(f"   允许的 .claude/ 文件: {sorted(ALLOWED_CLAUDE_FILES)}")
        print("   允许的 .claude/hooks/ 文件类型: *.sh")
        return False

    # Generated reports: keep in `reports/` but don't allow committing typical generated formats.
    if file_str.startswith(DISALLOWED_REPORT_PREFIXES) and file_path.suffix in DISALLOWED_REPORT_SUFFIXES:
        print(f"❌ 文件 {file_path} 看起来是生成的报告（{file_path.suffix}），默认禁止提交")
        print("   处理建议: 将其作为 CI artifact，或添加到 .gitignore")
        return False

    in_allowed_dir = any(file_str.startswith(d) for d in ALLOWED_TOP_DIRS)
    if not in_allowed_dir:
        print(f"❌ 文件 {file_path} 不在允许的目录范围内")
        print(f"   允许的顶层目录: {ALLOWED_TOP_DIRS}")
        return False

    return True


def check_init_py(file_path: Path) -> bool:
    """检查新子目录是否包含 __init__.py"""
    if file_path.is_dir():
        init_file = file_path / "__init__.py"
        if not init_file.exists():
            print(f"❌ 新目录 {file_path} 缺少 __init__.py")
            return False

    return True


def check_forbidden_dir(file_path: Path) -> bool:
    """检查是否在禁止的目录中创建文件"""
    file_str = str(file_path)

    denied, info = is_denied_path(file_str)
    if denied:
        print(f"❌ {info['action']}: {file_str} ({info['reason']})")
        return False

    ignored, ignore_info = should_ignore(file_str)
    if ignored:
        print(f"⏭️ 跳过: {file_str} ({ignore_info['reason']})")
        return True

    return True


def main():
    """主函数"""
    staged = get_staged_changes()

    if not staged:
        print("✅ 没有暂存的变更")
        return 0

    errors = []

    for status, file_path in staged:
        # Only enforce structure for newly added/copied files.
        if status not in {"A", "C"}:
            continue

        if not file_path.exists():
            continue

        if not check_forbidden_dir(file_path):
            errors.append(f"禁止目录: {file_path}")
            continue

        if not check_file_location(file_path):
            errors.append(f"位置违规: {file_path}")

        if file_path.is_dir() and not check_init_py(file_path):
            errors.append(f"缺少 __init__.py: {file_path}")

    if errors:
        print("\n❌ 目录结构检查未通过")
        for error in errors:
            print(f"   - {error}")
        print("\n请修复上述问题后重新提交")
        return 1

    print("✅ 目录结构检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
