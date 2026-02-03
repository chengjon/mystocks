#!/usr/bin/env python3
"""
批量修复Python文件语法错误
Batch fix Python syntax errors

用于修复项目中的缩进错误和其他常见语法问题
"""

import os
import re
import ast
import subprocess
from pathlib import Path


def fix_indentation_issues(file_path: str) -> bool:
    """
    修复常见的缩进问题

    Args:
        file_path: 文件路径

    Returns:
        是否修复成功
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 查找并修复常见的缩进错误模式
        fixed_lines = []
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if not stripped or stripped.startswith("#"):
                fixed_lines.append(line)
                continue

            # 检查@classmethod装饰器后的缩进
            if stripped == "@classmethod":
                # 检查下一行是否正确缩进
                if i + 1 < len(lines):
                    next_line = lines[i + 1].rstrip()
                    if next_line and not next_line.startswith("    def "):
                        # 修复缩进
                        if next_line.startswith("def "):
                            lines[i + 1] = "    " + next_line + "\n"
                            print(f"修复了第{i + 2}行的@classmethod缩进")

            # 检查except块的缩进
            if stripped.startswith("except ") or stripped == "finally:":
                # 确保except/finally与try对齐
                # 这里需要更复杂的逻辑来确定正确的缩进级别
                pass

            fixed_lines.append(line)

        # 写回文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)

        return True

    except Exception as e:
        print(f"修复文件失败 {file_path}: {e}")
        return False


def find_and_fix_syntax_errors(directory: str):
    """
    查找并修复目录中的语法错误

    Args:
        directory: 目录路径
    """
    print(f"开始扫描目录: {directory}")

    fixed_count = 0
    error_count = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # 检查语法
                try:
                    subprocess.run(
                        ["python", "-m", "py_compile", file_path],
                        capture_output=True,
                        check=True,
                    )
                except subprocess.CalledProcessError:
                    print(f"发现语法错误: {file_path}")

                    # 尝试修复
                    if fix_indentation_issues(file_path):
                        # 再次检查
                        try:
                            subprocess.run(
                                ["python", "-m", "py_compile", file_path],
                                capture_output=True,
                                check=True,
                            )
                            print(f"✅ 修复成功: {file_path}")
                            fixed_count += 1
                        except subprocess.CalledProcessError:
                            print(f"❌ 修复失败: {file_path}")
                            error_count += 1
                    else:
                        error_count += 1

    print(f"\n修复完成:")
    print(f"  ✅ 成功修复: {fixed_count} 个文件")
    print(f"  ❌ 仍需手动修复: {error_count} 个文件")


if __name__ == "__main__":
    # 修复src目录中的语法错误
    find_and_fix_syntax_errors("src")
