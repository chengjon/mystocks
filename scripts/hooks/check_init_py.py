#!/usr/bin/env python3
"""
__init__.py 规范检查脚本

检查新子目录是否包含规范的 __init__.py：
1. 必须包含 __version__
2. 必须包含 AUTHOR
3. 必须包含 __all__
"""

import os
import sys
from pathlib import Path


def get_staged_changes():
    """获取暂存的变更"""
    result = os.popen("git diff --cached --name-only").read()
    return [Path(f) for f in result.strip().split("\n") if f]


def check_init_py_content(init_file):
    """检查 __init__.py 内容是否规范"""
    if not init_file.exists():
        return False, "文件不存在"

    content = init_file.read_text()
    errors = []

    if "__version__" not in content:
        errors.append("缺少 __version__")

    if "AUTHOR" not in content:
        errors.append("缺少 AUTHOR")

    if "__all__" not in content:
        errors.append("缺少 __all__")

    if errors:
        return False, "; ".join(errors)

    return True, None


def main():
    """主函数"""
    staged_files = get_staged_changes()

    if not staged_files:
        print("✅ 没有暂存的变更")
        return 0

    errors = []

    for file_path in staged_files:
        if file_path.is_dir():
            init_file = file_path / "__init__.py"
            if init_file.exists():
                valid, reason = check_init_py_content(init_file)
                if not valid:
                    errors.append(f"{file_path}/__init__.py: {reason}")

    if errors:
        print("\n❌ __init__.py 检查未通过")
        for error in errors:
            print(f"   - {error}")
        print("\n请修复上述问题后重新提交")
        return 1

    print("✅ __init__.py 检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
