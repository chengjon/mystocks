#!/usr/bin/env python3
"""
文件命名规范检查脚本

检查文件名是否符合规范：
1. 必须使用英文
2. Python 文件使用 snake_case
3. 不允许使用中文、空格、特殊字符
"""

import os
import sys
import re
from pathlib import Path


def get_staged_changes():
    """获取暂存的变更"""
    result = os.popen("git diff --cached --name-only").read()
    return [Path(f) for f in result.strip().split("\n") if f]


def is_valid_filename(filename):
    """检查文件名是否规范"""
    pattern = r"^[a-zA-Z0-9_\-\.]+$"

    if re.search(r"[\u4e00-\u9fff]", str(filename)):
        return False, "文件名包含中文字符"

    if " " in str(filename):
        return False, "文件名包含空格"

    if str(filename).endswith(".py"):
        if not re.match(r"^[a-z][a-z0-9_]*\.py$", str(filename)):
            return False, "Python 文件应使用 snake_case 命名"

    return True, None


def main():
    """主函数"""
    staged_files = get_staged_changes()

    if not staged_files:
        print("✅ 没有暂存的变更")
        return 0

    errors = []

    for file_path in staged_files:
        valid, reason = is_valid_filename(file_path.name)
        if not valid:
            errors.append(f"{file_path}: {reason}")

    if errors:
        print("\n❌ 文件命名检查未通过")
        for error in errors:
            print(f"   - {error}")
        print("\n请修复上述问题后重新提交")
        return 1

    print("✅ 文件命名检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
