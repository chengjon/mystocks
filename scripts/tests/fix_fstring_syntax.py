#!/usr/bin/env python
"""批量修复Mock文件中的f-string语法错误

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import re
from pathlib import Path


def fix_fstring_syntax(file_path):
    """修复单个文件中的f-string语法错误"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # 修复 print(f"\n 格式的错误
        # 匹配 print(f"\n后面的内容直到下一个引号
        pattern = r'print\(f"\\n[^"]*"\)'

        # 更精确的模式：匹配有问题的f-string
        problematic_patterns = [
            r'print\(f"\\n([^"]*)$',  # print(f"\n内容没有闭合
            r'print\(f"([^"]*)\\n([^"]*)$',  # print(f"内容\n内容没有闭合
        ]

        original_content = content

        # 修复第一种模式：print(f"\n内容
        content = re.sub(
            r'print\(f"\\n([^"]*)$',
            r'print(f"\\n\1")',
            content,
            flags=re.MULTILINE,
        )

        # 修复第二种模式：print(f"内容\n内容
        content = re.sub(
            r'print\(f"([^"]*)\\n([^"]*)$',
            r'print(f"\1\\n\2")',
            content,
            flags=re.MULTILINE,
        )

        # 特殊修复：修复已知的错误模式
        content = re.sub(
            r'print\(f"\\n([^"]*\) 调用测试:"\)',
            r'print(f"\\n\1 调用测试:")',
            content,
        )

        # 修复多行print语句
        content = re.sub(
            r'print\(f"([^"]*\) 返回数据:\s*\n\s*\{result\d+\}\)',
            r'print(f"\1 返回数据: {result\d+}")',
            content,
        )

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 修复了 {file_path}")
            return True
        print(f"⚪ 无需修复 {file_path}")
        return False

    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e!s}")
        return False


def main():
    """主函数"""
    mock_dir = Path(__file__).parent.parent.parent / "src" / "mock"

    if not mock_dir.exists():
        print(f"Mock目录不存在: {mock_dir}")
        return

    fixed_files = 0

    # 遍历所有Mock文件
    for file_path in mock_dir.glob("mock_*.py"):
        if file_path.suffix == ".py":
            if fix_fstring_syntax(file_path):
                fixed_files += 1

    print(f"\n修复完成! 共修复了 {fixed_files} 个文件")

    # 验证语法
    print("\n验证语法...")
    syntax_errors = 0

    for file_path in mock_dir.glob("mock_*.py"):
        if file_path.suffix == ".py":
            try:
                with open(file_path, encoding="utf-8") as f:
                    compile(f.read(), str(file_path), "exec")
                print(f"✅ {file_path.name}")
            except SyntaxError as e:
                print(f"❌ {file_path.name}: {e!s}")
                syntax_errors += 1

    if syntax_errors == 0:
        print("\n🎉 所有文件语法正确!")
    else:
        print(f"\n⚠️ 仍有 {syntax_errors} 个文件存在语法错误")


if __name__ == "__main__":
    main()
