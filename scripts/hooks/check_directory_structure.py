#!/usr/bin/env python3
"""
目录结构合规性检查脚本

检查新创建的文件/目录是否符合项目规范：
1. 新文件必须在允许的目录范围内
2. 新子目录必须包含 __init__.py
3. 不允许在禁止目录中创建文件
"""

import os
import sys
from pathlib import Path

# 允许的顶层目录
ALLOWED_TOP_DIRS = [
    "src/",
    "scripts/",
    "docs/",
    "tests/",
    "config/",
]

# 禁止创建文件的目录
FORBIDDEN_DIRS = [
    "src/temp/",
    "docs/docs/",
    "docs/reports/",
]

sys.path.insert(0, str(Path(__file__).parent.parent))
from .deny_list import is_denied_path, should_ignore


def get_staged_changes():
    """获取暂存的变更"""
    result = os.popen("git diff --cached --name-only").read()
    return [Path(f) for f in result.strip().split("\n") if f]


def check_file_location(file_path):
    """检查文件是否在允许的位置"""
    file_str = str(file_path)

    in_allowed_dir = any(file_str.startswith(d) for d in ALLOWED_TOP_DIRS)
    if not in_allowed_dir:
        print(f"❌ 文件 {file_path} 不在允许的目录范围内")
        print(f"   允许的顶层目录: {ALLOWED_TOP_DIRS}")
        return False

    return True


def check_init_py(file_path):
    """检查新子目录是否包含 __init__.py"""
    if file_path.is_dir():
        init_file = file_path / "__init__.py"
        if not init_file.exists():
            print(f"❌ 新目录 {file_path} 缺少 __init__.py")
            return False

    return True


def check_forbidden_dir(file_path):
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
    staged_files = get_staged_changes()

    if not staged_files:
        print("✅ 没有暂存的变更")
        return 0

    errors = []

    for file_path in staged_files:
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
