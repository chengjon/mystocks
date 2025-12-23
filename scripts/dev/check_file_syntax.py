#!/usr/bin/env python3
"""
检查文件语法和编码
Check file syntax and encoding
"""

import ast
from pathlib import Path


def check_file_syntax():
    """检查文件语法"""
    file_path = Path("/opt/claude/mystocks_spec/web/backend/app/api/market.py")

    print(f"🔍 检查文件: {file_path}")
    print(f"文件存在: {file_path.exists()}")

    if not file_path.exists():
        print("❌ 文件不存在！")
        return

    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"📄 文件大小: {len(content)} 字符")
        print(f"📄 行数: {len(content.splitlines())}")

        # 检查前几行
        lines = content.splitlines()
        print("\n📝 前10行内容:")
        for i, line in enumerate(lines[:10], 1):
            print(f"{i:3d}: {repr(line)}")

        print("\n🔍 检查函数定义模式...")
        # 查找包含 "def " 的行
        def_lines = []
        for i, line in enumerate(lines, 1):
            if "def " in line:
                def_lines.append((i, line.strip()))

        print(f"找到 {len(def_lines)} 个函数定义:")
        for line_num, line in def_lines[:10]:  # 显示前10个
            print(f"  行 {line_num}: {line}")

        print("\n🔍 检查装饰器模式...")
        # 查找包含 "@" 的行
        decorator_lines = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("@"):
                decorator_lines.append((i, line.strip()))

        print(f"找到 {len(decorator_lines)} 个装饰器:")
        for line_num, line in decorator_lines[:20]:  # 显示前20个
            print(f"  行 {line_num}: {line}")

        print("\n🔍 尝试AST解析...")
        try:
            tree = ast.parse(content)
            print("✅ AST解析成功")

            # 统计AST节点
            node_counts = {}
            for node in ast.walk(tree):
                node_type = type(node).__name__
                node_counts[node_type] = node_counts.get(node_type, 0) + 1

            print("AST节点统计:")
            for node_type, count in sorted(node_counts.items()):
                print(f"  {node_type}: {count}")

            # 检查FunctionDef节点
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append((node.name, node.lineno))

            print(f"\n🎯 找到 {len(functions)} 个函数定义:")
            for name, line_num in functions:
                print(f"  函数: {name} (行 {line_num})")

        except SyntaxError as e:
            print(f"❌ AST解析失败: {e}")
            print(f"   错误行: {e.lineno}")
            print(f"   错误列: {e.offset}")
            print(f"   错误文本: {e.text}")

            # 显示错误行及其周围的几行
            error_line = e.lineno - 1  # AST使用0基索引
            if 0 <= error_line < len(lines):
                start_line = max(0, error_line - 2)
                end_line = min(len(lines), error_line + 3)
                print("\n错误行周围内容:")
                for i in range(start_line, end_line):
                    marker = ">>> " if i == error_line else "    "
                    print(f"{marker}{i + 1:3d}: {lines[i]}")

        except Exception as e:
            print(f"❌ 意外错误: {e}")
            import traceback

            traceback.print_exc()

    except UnicodeDecodeError as e:
        print(f"❌ 编码错误: {e}")
        print("尝试其他编码...")

        # 尝试不同的编码
        encodings = ["gbk", "gb2312", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                print(f"✅ 使用 {encoding} 编码成功读取")
                break
            except:
                print(f"❌ {encoding} 编码失败")

    except Exception as e:
        print(f"❌ 读取文件失败: {e}")


if __name__ == "__main__":
    check_file_syntax()
