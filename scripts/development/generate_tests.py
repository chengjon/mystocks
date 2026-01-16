#!/usr/bin/env python3
"""
TDD测试生成脚本

基于现有代码自动生成单元测试模板
支持双循环TDD工作流
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple
import argparse


class TestGenerator:
    """测试生成器"""

    def __init__(self, source_file: str):
        self.source_file = Path(source_file)
        self.module_name = self._get_module_name()
        self.test_file = self._get_test_file_path()

    def _get_module_name(self) -> str:
        """获取模块名"""
        # 将src/adapters/xxx.py转换为src.adapters.xxx
        parts = self.source_file.parts
        if parts[0] == "src":
            return ".".join(parts[:-1]) + "." + self.source_file.stem
        return self.source_file.stem

    def _get_test_file_path(self) -> Path:
        """获取测试文件路径"""
        # src/adapters/xxx.py -> tests/unit/adapters/test_xxx.py
        parts = self.source_file.parts
        if parts[0] == "src":
            test_parts = (
                ["tests", "unit"]
                + list(parts[1:-1])
                + [f"test_{self.source_file.stem}.py"]
            )
        else:
            test_parts = (
                ["tests", "unit"]
                + list(parts[:-1])
                + [f"test_{self.source_file.stem}.py"]
            )

        return Path(*test_parts)

    def parse_source_code(self) -> ast.Module:
        """解析源代码"""
        with open(self.source_file, "r", encoding="utf-8") as f:
            return ast.parse(f.read())

    def extract_classes_and_functions(self) -> List[Tuple[str, str, List[str]]]:
        """提取类和函数信息

        Returns:
            List of (name, type, methods/signatures)
        """
        tree = self.parse_source_code()
        items = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(self._get_function_signature(item))
                items.append((node.name, "class", methods))
            elif isinstance(node, ast.FunctionDef):
                signature = self._get_function_signature(node)
                items.append((node.name, "function", [signature]))

        return items

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """获取函数签名"""
        args = []

        # 普通参数
        for arg in node.args.args:
            args.append(arg.arg)

        # 默认参数
        defaults = len(node.args.defaults)
        if defaults > 0:
            for i, default in enumerate(node.args.defaults):
                idx = len(node.args.args) - defaults + i
                args[-1] += (
                    f"={ast.unparse(default) if hasattr(ast, 'unparse') else '...'}"
                )

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        signature = f"{node.name}({', '.join(args)})"
        if node.returns:
            signature += (
                f" -> {ast.unparse(node.returns) if hasattr(ast, 'unparse') else '...'}"
            )

        return signature

    def generate_test_file(self) -> str:
        """生成测试文件内容"""
        items = self.extract_classes_and_functions()

        content = f'''"""
{self.module_name} 的单元测试

测试策略:
- 外层循环: 集成测试验证业务功能
- 内层循环: 单元测试验证具体实现

生成时间: {self._get_current_time()}
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Any

# 导入被测试的模块
try:
    from {self.module_name} import *
except ImportError as e:
    pytest.skip(f"无法导入 {self.module_name}: {{e}}", allow_module_level=True)


class Test{self._get_class_name()}:
    """
    {self.module_name} 的单元测试

    测试覆盖:
    - 正常流程
    - 边界条件
    - 异常处理
    - 性能基准
    """

    @pytest.fixture
    def setup_mock(self):
        """测试夹具：设置模拟对象"""
        # 根据需要添加具体的mock设置
        pass

    def setup_method(self):
        """每个测试方法前的设置"""
        # 初始化测试数据
        self.test_data = {{
            'sample_input': 'test_value',
            'expected_output': 'expected_value'
        }}

'''

        # 为每个类和函数生成测试方法
        for name, item_type, signatures in items:
            if item_type == "class":
                content += self._generate_class_tests(name, signatures)
            else:
                content += self._generate_function_tests(name, signatures[0])

        content += """
if __name__ == "__main__":
    # 运行测试
    unittest.main()
"""

        return content

    def _get_class_name(self) -> str:
        """获取测试类名"""
        parts = self.module_name.split(".")
        return "".join(p.title() for p in parts)

    def _generate_class_tests(self, class_name: str, methods: List[str]) -> str:
        """为类生成测试"""
        content = f'''
    # ========================
    # {class_name} 类测试
    # ========================

    def test_{class_name.lower()}_initialization(self):
        """测试 {class_name} 初始化"""
        # TODO: 实现具体测试逻辑
        assert True  # 占位符

'''

        for method in methods:
            method_name = method.split("(")[0].strip()
            if method_name.startswith("_"):
                continue  # 跳过私有方法

            content += f'''
    def test_{class_name.lower()}_{method_name.lower()}(self):
        """测试 {class_name}.{method_name}"""
        # TODO: 实现 {method_name} 的测试
        # 测试输入:
        # 预期输出:
        # 边界条件:
        # 异常情况:
        assert True  # 占位符

'''

        return content

    def _generate_function_tests(self, function_name: str, signature: str) -> str:
        """为函数生成测试"""
        return f'''
    # ========================
    # {function_name} 函数测试
    # ========================

    def test_{function_name.lower()}_normal_case(self):
        """测试 {function_name} 正常情况"""
        # TODO: 实现正常情况测试
        # 函数签名: {signature}
        assert True  # 占位符

    def test_{function_name.lower()}_edge_case(self):
        """测试 {function_name} 边界条件"""
        # TODO: 实现边界条件测试
        assert True  # 占位符

    def test_{function_name.lower()}_error_case(self):
        """测试 {function_name} 异常处理"""
        # TODO: 实现异常情况测试
        assert True  # 占位符

    @pytest.mark.benchmark
    def test_{function_name.lower()}_performance(self):
        """测试 {function_name} 性能基准"""
        # TODO: 实现性能测试
        import time
        start_time = time.time()
        # 调用函数
        end_time = time.time()
        assert (end_time - start_time) < 1.0  # 应在1秒内完成

'''

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_test_file(self, overwrite: bool = False):
        """保存测试文件"""
        # 确保目录存在
        self.test_file.parent.mkdir(parents=True, exist_ok=True)

        # 检查文件是否已存在
        if self.test_file.exists() and not overwrite:
            print(f"测试文件已存在: {self.test_file}")
            print("使用 --overwrite 参数覆盖")
            return False

        # 生成并保存内容
        content = self.generate_test_file()
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ 测试文件已生成: {self.test_file}")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="TDD测试生成器 - 为源代码生成单元测试模板"
    )
    parser.add_argument(
        "source_file", help="源代码文件路径 (如: src/adapters/akshare_adapter.py)"
    )
    parser.add_argument(
        "--overwrite", "-o", action="store_true", help="覆盖已存在的测试文件"
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="只显示将要生成的内容，不保存文件"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="列出文件中的类和函数"
    )

    args = parser.parse_args()

    # 检查源文件是否存在
    if not Path(args.source_file).exists():
        print(f"❌ 源文件不存在: {args.source_file}")
        return 1

    try:
        generator = TestGenerator(args.source_file)

        if args.list:
            # 列出类和函数
            items = generator.extract_classes_and_functions()
            print(f"\n📋 {args.source_file} 中的类和函数:")
            for name, item_type, signatures in items:
                icon = "🏗️" if item_type == "class" else "⚡"
                print(f"  {icon} {item_type}: {name}")
                for sig in signatures:
                    print(f"      └─ {sig}")
            return 0

        if args.dry_run:
            # 显示将要生成的内容
            content = generator.generate_test_file()
            print(f"\n📄 将要生成的测试文件: {generator.test_file}")
            print("=" * 60)
            print(content[:1000] + "..." if len(content) > 1000 else content)
            return 0

        # 生成测试文件
        success = generator.save_test_file(args.overwrite)

        if success:
            # 生成运行命令
            print("\n🚀 运行测试:")
            print(f"  pytest {generator.test_file}")
            print("\n📊 生成覆盖率报告:")
            print(f"  pytest --cov=src --cov-report=html {generator.test_file}")

        return 0 if success else 1

    except Exception as e:
        print(f"❌ 生成测试时出错: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
