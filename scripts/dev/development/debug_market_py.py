#!/usr/bin/env python3
"""
专门调试 market.py 文件
Debug market.py specifically
"""

import ast
from pathlib import Path


def debug_market_py():
    """调试 market.py 文件"""
    file_path = Path("/opt/claude/mystocks_spec/web/backend/app/api/market.py")

    print(f"🔍 分析文件: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"📄 文件大小: {len(content)} 字符")

        # 解析AST
        tree = ast.parse(content)
        print("✅ AST 解析成功")

        # 查找所有函数定义
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                print(f"\n📝 函数: {func_name}")
                print(f"   行号: {node.lineno}")
                print(f"   装饰器数量: {len(node.decorator_list)}")

                # 详细检查装饰器
                for i, decorator in enumerate(node.decorator_list):
                    print(f"   装饰器 {i + 1}: {type(decorator).__name__}")

                    if isinstance(decorator, ast.Call):
                        print("     类型: ast.Call")
                        print(f"     func: {type(decorator.func).__name__}")

                        if isinstance(decorator.func, ast.Attribute):
                            print(f"     attr: {decorator.func.attr}")
                            if isinstance(decorator.func.value, ast.Name):
                                print(f"     value.id: {decorator.func.value.id}")

                        print(f"     args: {len(decorator.args)}")
                        for j, arg in enumerate(decorator.args):
                            print(f"       arg[{j}]: {type(arg).__name__}")
                            if isinstance(arg, ast.Constant):
                                print(f"         value: {arg.value}")

                    elif isinstance(decorator, ast.Name):
                        print(f"     name.id: {decorator.id}")

                # 显示函数的前几行源码
                lines = content.split("\n")
                start_line = max(0, node.lineno - 5)
                end_line = min(len(lines), node.lineno + 10)

                print(f"   源码片段 (行 {start_line + 1}-{end_line}):")
                for line_num in range(start_line, end_line):
                    marker = ">>> " if line_num == node.lineno - 1 else "    "
                    print(f"{marker}{line_num + 1:3d}: {lines[line_num]}")

        # 检查所有函数定义
        function_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)

        print("\n📋 发现的函数名称:")
        for i, name in enumerate(function_names[:20]):  # 只显示前20个
            print(f"   {i + 1:2d}. {name}")

        if len(function_names) > 20:
            print(f"   ... 还有 {len(function_names) - 20} 个函数")

        # 检查特定函数 get_fund_flow
        print("\n🎯 专门查找 get_fund_flow 函数:")
        fund_flow_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_fund_flow":
                fund_flow_found = True
                print(f"   找到函数: {node.name} (行 {node.lineno})")
                print(f"   装饰器数量: {len(node.decorator_list)}")

                for i, decorator in enumerate(node.decorator_list):
                    print(f"   装饰器 {i + 1}:")
                    print(f"     类型: {type(decorator).__name__}")

                    if isinstance(decorator, ast.Call):
                        print(f"     func类型: {type(decorator.func).__name__}")
                        if isinstance(decorator.func, ast.Attribute):
                            print(f"     调用: {decorator.func.attr}")
                            if isinstance(decorator.func.value, ast.Name):
                                print(f"     对象: {decorator.func.value.id}")

                        if decorator.args:
                            print(f"     参数数量: {len(decorator.args)}")
                            for j, arg in enumerate(decorator.args):
                                print(f"       arg[{j}]: {type(arg).__name__}")
                                if isinstance(arg, ast.Constant):
                                    print(f"         值: {arg.value}")

                    elif isinstance(decorator, ast.Name):
                        print(f"     name.id: {decorator.id}")

                break

        if not fund_flow_found:
            print("   ❌ 未找到 get_fund_flow 函数")
            print("   检查是否函数名有差异...")

            # 查找包含 'fund' 的函数
            fund_functions = [name for name in function_names if "fund" in name.lower()]
            if fund_functions:
                print(f"   找到包含'fund'的函数: {fund_functions}")
            else:
                print("   未找到任何包含'fund'的函数")

    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        print(f"   行号: {e.lineno}")
        print(f"   错误文本: {e.text}")

    except Exception as e:
        print(f"❌ 解析失败: {e}")


if __name__ == "__main__":
    debug_market_py()
