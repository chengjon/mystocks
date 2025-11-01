"""
AST 解析器 - 提取 Python 代码的结构化元数据

使用 Python 的 ast 模块解析代码文件，提取类、函数、参数等信息。

作者: MyStocks Team
日期: 2025-10-19
"""

import ast
import os
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    ModuleMetadata, ClassMetadata, FunctionMetadata,
    ParameterMetadata, CategoryEnum, estimate_complexity,
    categorize_module_by_path
)


class ASTParser:
    """AST 解析器类"""

    def __init__(self, project_root: str):
        """
        初始化 AST 解析器

        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)

    def parse_file(self, file_path: Path) -> Optional[ModuleMetadata]:
        """
        解析单个 Python 文件

        Args:
            file_path: 文件路径

        Returns:
            ModuleMetadata 对象，如果解析失败则返回 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # 解析 AST
            tree = ast.parse(source, filename=str(file_path))

            # 提取模块信息
            module_name = self._get_module_name(file_path)
            relative_path = str(file_path.relative_to(self.project_root))

            # 创建模块元数据
            module = ModuleMetadata(
                file_path=relative_path,
                module_name=module_name,
                category=categorize_module_by_path(relative_path),
                docstring=ast.get_docstring(tree),
                last_modified=datetime.fromtimestamp(os.path.getmtime(file_path))
            )

            # 计算代码行数
            lines = source.split('\n')
            module.lines_of_code = len(lines)
            module.blank_lines = sum(1 for line in lines if not line.strip())
            module.comment_lines = sum(1 for line in lines if line.strip().startswith('#'))

            # 遍历顶级节点
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    # 解析类
                    class_meta = self._parse_class(node)
                    module.classes.append(class_meta)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # 解析函数
                    func_meta = self._parse_function(node)
                    module.functions.append(func_meta)
                elif isinstance(node, ast.Import):
                    # 解析 import 语句
                    for alias in node.names:
                        module.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    # 解析 from ... import 语句
                    if node.module:
                        module.imports.append(node.module)

            return module

        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名称"""
        relative_path = file_path.relative_to(self.project_root)
        parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return '.'.join(parts)

    def _parse_class(self, node: ast.ClassDef) -> ClassMetadata:
        """
        解析类定义

        Args:
            node: ast.ClassDef 节点

        Returns:
            ClassMetadata 对象
        """
        # 提取基类
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}")

        # 提取装饰器
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]

        # 创建类元数据
        class_meta = ClassMetadata(
            name=node.name,
            line_number=node.lineno,
            base_classes=base_classes,
            docstring=ast.get_docstring(node),
            decorators=decorators,
            is_abstract='ABC' in base_classes or 'abc.ABC' in base_classes
        )

        # 解析方法
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method_meta = self._parse_function(item)
                class_meta.methods.append(method_meta)

        return class_meta

    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionMetadata:
        """
        解析函数定义

        Args:
            node: ast.FunctionDef 或 ast.AsyncFunctionDef 节点

        Returns:
            FunctionMetadata 对象
        """
        # 提取参数
        parameters = self._parse_parameters(node.args)

        # 提取返回类型
        return_type = None
        if node.returns:
            return_type = self._get_type_annotation(node.returns)

        # 提取装饰器
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]

        # 计算函数体行数
        body_lines = 0
        if node.body:
            first_line = node.body[0].lineno
            last_line = node.body[-1].end_lineno or node.body[-1].lineno
            body_lines = last_line - first_line + 1

        # 估算复杂度
        complexity = estimate_complexity(node)

        return FunctionMetadata(
            name=node.name,
            line_number=node.lineno,
            parameters=parameters,
            return_type=return_type,
            docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators,
            body_lines=body_lines,
            complexity=complexity
        )

    def _parse_parameters(self, args: ast.arguments) -> List[ParameterMetadata]:
        """
        解析函数参数

        Args:
            args: ast.arguments 节点

        Returns:
            参数元数据列表
        """
        parameters = []

        # 处理位置参数和关键字参数
        all_args = args.args
        defaults = [None] * (len(all_args) - len(args.defaults)) + args.defaults

        for arg, default in zip(all_args, defaults):
            param = ParameterMetadata(
                name=arg.arg,
                type_annotation=self._get_type_annotation(arg.annotation) if arg.annotation else None,
                default_value=self._get_default_value(default) if default else None,
                is_required=default is None
            )
            parameters.append(param)

        # 处理 *args
        if args.vararg:
            parameters.append(ParameterMetadata(
                name=f"*{args.vararg.arg}",
                type_annotation=self._get_type_annotation(args.vararg.annotation) if args.vararg.annotation else None,
                is_required=False
            ))

        # 处理 **kwargs
        if args.kwarg:
            parameters.append(ParameterMetadata(
                name=f"**{args.kwarg.arg}",
                type_annotation=self._get_type_annotation(args.kwarg.annotation) if args.kwarg.annotation else None,
                is_required=False
            ))

        return parameters

    def _get_type_annotation(self, annotation) -> str:
        """提取类型注解字符串"""
        if annotation is None:
            return "Any"

        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            # 处理泛型类型，如 List[str], Dict[str, int]
            value = self._get_type_annotation(annotation.value)
            slice_val = self._get_type_annotation(annotation.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(annotation, ast.Tuple):
            # 处理元组类型
            elements = [self._get_type_annotation(elt) for elt in annotation.elts]
            return f"({', '.join(elements)})"
        elif isinstance(annotation, ast.Attribute):
            return f"{annotation.value.id}.{annotation.attr}"
        else:
            return "Any"

    def _get_default_value(self, default) -> str:
        """提取默认值字符串"""
        if isinstance(default, ast.Constant):
            value = default.value
            if isinstance(value, str):
                return f'"{value}"'
            return str(value)
        elif isinstance(default, ast.Name):
            return default.id
        elif isinstance(default, ast.List):
            return "[]"
        elif isinstance(default, ast.Dict):
            return "{}"
        elif isinstance(default, ast.Call):
            if isinstance(default.func, ast.Name):
                return f"{default.func.id}()"
        return "..."

    def _get_decorator_name(self, decorator) -> str:
        """提取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{decorator.func.value.id}.{decorator.func.attr}"
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        return "unknown"

    def scan_directory(self, directory: Path, exclude_patterns: List[str] = None) -> List[ModuleMetadata]:
        """
        扫描目录下的所有 Python 文件

        Args:
            directory: 目录路径
            exclude_patterns: 排除的路径模式列表

        Returns:
            模块元数据列表
        """
        if exclude_patterns is None:
            exclude_patterns = [
                '__pycache__', '.git', '.venv', 'venv',
                'env', '.pytest_cache', '.mypy_cache',
                'node_modules', 'build', 'dist', '.eggs'
            ]

        modules = []

        for py_file in directory.rglob('*.py'):
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(py_file):
                    should_exclude = True
                    break

            if should_exclude:
                continue

            # 解析文件
            module = self.parse_file(py_file)
            if module:
                modules.append(module)

        return modules


def extract_code_block(file_path: str, start_line: int, end_line: int) -> str:
    """
    从文件中提取代码块

    Args:
        file_path: 文件路径
        start_line: 起始行号（从 1 开始）
        end_line: 结束行号

    Returns:
        代码块字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 转换为 0-based index
            return ''.join(lines[start_line-1:end_line])
    except Exception as e:
        print(f"Error extracting code block from {file_path}: {e}")
        return ""


def tokenize_code(code: str) -> List[str]:
    """
    将代码分词为 token 列表

    Args:
        code: 代码字符串

    Returns:
        token 列表
    """
    import re

    # 移除注释和字符串字面量
    code_no_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code_no_strings = re.sub(r'["\'].*?["\']', '', code_no_comments)

    # 按空白和符号分词
    tokens = re.findall(r'\w+|[^\w\s]', code_no_strings)

    # 过滤空 token
    return [t for t in tokens if t.strip()]


if __name__ == "__main__":
    # 测试代码
    project_root = Path("/opt/claude/mystocks_spec")
    parser = ASTParser(str(project_root))

    # 测试解析单个文件
    test_file = project_root / "unified_manager.py"
    if test_file.exists():
        print(f"Parsing {test_file}...")
        module = parser.parse_file(test_file)
        if module:
            print(f"Module: {module.module_name}")
            print(f"Category: {module.category}")
            print(f"Classes: {len(module.classes)}")
            print(f"Functions: {len(module.functions)}")
            print(f"Lines of code: {module.lines_of_code}")
