"""技术负债分析器子模块"""

import ast
import asyncio
import logging
import re
from collections import Counter
from pathlib import Path
from typing import List


logger = logging.getLogger(__name__)


class CodeQualityMixin:
    """代码质量分析：长函数、复杂度、死导入、重复代码、命名规范"""

    async def analyze_code_quality(self):
        """分析代码质量问题"""
        logger.info("分析代码质量...")

        python_files = list(self.project_root.rglob("*.py"))
        self.stats["total_files"] = len(list(self.project_root.rglob("*"))) - len(
            list(self.project_root.rglob("__pycache__")),
        )
        self.stats["python_files"] = len(python_files)

        # Process each file concurrently
        async def process_file(py_file: Path):
            if self._should_skip_file(py_file):
                return

            try:
                content = await self._read_file_content_async(py_file)
                lines = content.split("\n")

                # Use a lock or a shared counter that supports atomic increments for total_lines if needed.
                # For simplicity here, we acknowledge that direct increment might be slightly off in highly concurrent scenarios
                # but it's acceptable for statistics where exactness isn't critical.
                self.stats["total_lines"] += len(lines)

                # 解析AST
                tree = ast.parse(content, filename=str(py_file))

                # 分析各种代码质量问题
                self._analyze_long_functions(py_file, tree, lines)
                self._analyze_complex_functions(py_file, tree)
                self._analyze_dead_imports(py_file, tree, content)
                self._analyze_code_duplication(py_file, content, lines)
                self._analyze_naming_issues(py_file, tree)
                await self._analyze_file_complexity_async(
                    py_file,
                    tree,
                )  # Use async version

            except Exception as e:
                self.issues["parsing_errors"].append(
                    {"file": str(py_file), "error": str(e), "category": "code_quality"},
                )

        await asyncio.gather(*[process_file(f) for f in python_files])

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".mypy_cache",
            ".opencode",
            ".cursor",
            ".specify",
            ".taskmaster",
            ".archive",
            "tests/e2e/node_modules",
            "scripts/utils",  # Skip utility files created by the agent during refactoring
        ]

        skip_patterns.extend([".pyc", ".pyo", ".pyd"])

        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
        return False

    def _analyze_long_functions(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """分析过长的函数"""

        class FunctionAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path, lines, issues_ref):
                self.file_path = file_path
                self.lines = lines
                self.issues_ref = issues_ref

            def visit_FunctionDef(self, node):
                # 计算函数行数（包括注释和空行）
                func_start = node.lineno - 1
                func_end = node.end_lineno if hasattr(node, "end_lineno") else len(self.lines)
                func_lines = func_end - func_start

                # 警告阈值：50行以上的函数
                if func_lines > 50:
                    self.issues_ref["long_functions"].append(
                        {
                            "file": str(self.file_path),
                            "function": node.name,
                            "line_count": func_lines,
                            "start_line": node.lineno,
                            "end_line": func_end,
                            "category": "code_quality",
                            "severity": "high" if func_lines > 100 else "medium",
                        },
                    )

                self.generic_visit(node)

        analyzer = FunctionAnalyzer(file_path, lines, self.issues)
        analyzer.visit(tree)

    def _analyze_complex_functions(self, file_path: Path, tree: ast.AST):
        """分析复杂函数（高圈复杂度）"""

        class ComplexityAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path, issues_ref):
                self.file_path = file_path
                self.issues_ref = issues_ref
                self.complexity = 0

            def visit_FunctionDef(self, node):
                complexity = 1  # 基础复杂度

                # 计算条件语句复杂度
                for child in ast.walk(node):
                    if isinstance(
                        child,
                        (ast.If, ast.While, ast.For, ast.Try, ast.With),
                    ):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1

                # 复杂度超过10被认为复杂
                if complexity > 10:
                    self.issues_ref["complex_functions"].append(
                        {
                            "file": str(self.file_path),
                            "function": node.name,
                            "complexity": complexity,
                            "category": "code_quality",
                            "severity": "high" if complexity > 20 else "medium",
                        },
                    )

                self.generic_visit(node)

        analyzer = ComplexityAnalyzer(file_path, self.issues)
        analyzer.visit(tree)

    def _analyze_dead_imports(self, file_path: Path, tree: ast.AST, content: str):
        """分析未使用的导入"""

        class ImportAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path, content, tree, issues_ref):
                self.file_path = file_path
                self.content = content
                self.tree = tree
                self.issues_ref = issues_ref
                self.used_names = set()
                self.imported_names = {}

                # 收集使用的名称
                for node in ast.walk(self.tree):
                    if isinstance(node, ast.Name):
                        self.used_names.add(node.id)
                    elif isinstance(node, ast.Attribute):
                        if isinstance(node.value, ast.Name):
                            self.used_names.add(f"{node.value.id}.{node.attr}")

                # 收集导入的名称
                for node in ast.walk(self.tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.imported_names[alias.asname or alias.name] = alias.name
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            name = alias.asname or alias.name
                            self.imported_names[name] = f"{module}.{alias.name}"

            def visit_Import(self, node):
                for alias in node.names:
                    name = alias.asname or alias.name
                    # 检查是否使用
                    if name not in self.used_names and f"{name}" not in self.used_names:
                        self.issues_ref["dead_imports"].append(
                            {
                                "file": str(self.file_path),
                                "import": alias.name,
                                "asname": alias.asname,
                                "category": "code_quality",
                                "severity": "low",
                            },
                        )
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                module = node.module or ""
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name not in self.used_names:
                        self.issues_ref["dead_imports"].append(
                            {
                                "file": str(self.file_path),
                                "import": f"{module}.{alias.name}",
                                "asname": alias.asname,
                                "category": "code_quality",
                                "severity": "low",
                            },
                        )
                self.generic_visit(node)

        analyzer = ImportAnalyzer(file_path, content, tree, self.issues)
        analyzer.visit(tree)

    def _analyze_code_duplication(
        self,
        file_path: Path,
        content: str,
        lines: List[str],
    ):
        """分析代码重复"""
        # 简单的重复代码检测：查找重复的行
        line_counts = Counter()
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 10 and not stripped.startswith(
                "#",
            ):  # 忽略太短的行和注释
                line_counts[stripped] += 1

        for line, count in line_counts.items():
            if count > 2:  # 重复超过2次
                self.issues["code_duplication"].append(
                    {
                        "file": str(file_path),
                        "code": line[:100],
                        "occurrence_count": count,
                        "category": "code_quality",
                        "severity": "medium",
                    },
                )

    def _analyze_naming_issues(self, file_path: Path, tree: ast.AST):
        """分析命名问题"""

        class NamingAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path, issues_ref):
                self.file_path = file_path
                self.issues_ref = issues_ref

            def visit_FunctionDef(self, node):
                # 检查函数命名是否符合规范
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                    self.issues_ref["naming_issues"].append(
                        {
                            "file": str(self.file_path),
                            "type": "function",
                            "name": node.name,
                            "issue": "function_name_convention",
                            "category": "code_quality",
                            "severity": "low",
                        },
                    )
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                # 检查类命名是否符合规范
                if not re.match(r"^[A-Z][A-Za-z0-9]*$", node.name):
                    self.issues_ref["naming_issues"].append(
                        {
                            "file": str(self.file_path),
                            "type": "class",
                            "name": node.name,
                            "issue": "class_name_convention",
                            "category": "code_quality",
                            "severity": "medium",
                        },
                    )
                self.generic_visit(node)

        analyzer = NamingAnalyzer(file_path, self.issues)
        analyzer.visit(tree)

    async def _analyze_file_complexity_async(self, file_path: Path, tree: ast.AST):
        """分析文件复杂度"""

        class FileComplexityAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path):
                self.file_path = file_path
                self.classes = 0
                self.functions = 0
                self.imports = 0

            def visit_ClassDef(self, node):
                self.classes += 1
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                self.functions += 1
                self.generic_visit(node)

            def visit_Import(self, node):
                self.imports += len(node.names)
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                self.imports += len(node.names)
                self.generic_visit(node)

        analyzer = FileComplexityAnalyzer(file_path)
        analyzer.visit(tree)

        # 文件太复杂（超过500行或类/函数太多）
        # 这个检查需要基于实际文件长度
        try:
            content = await self._read_file_content_async(file_path)
            actual_lines = len(content.splitlines())

            if actual_lines > 500:
                self.issues["large_files"].append(
                    {
                        "file": str(file_path),
                        "line_count": actual_lines,
                        "category": "code_quality",
                        "severity": "high",
                    },
                )
        except Exception as e:
            logger.warning(f"分析文件复杂度失败 {file_path}: {e}")
