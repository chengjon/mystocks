#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks技术负债分析器

全面分析项目中的技术负债，包括：
1. 代码质量问题
2. 架构债务
3. 性能问题
4. 安全问题
5. 依赖问题
6. 测试覆盖
7. 文档问题

作者: iFlow CLI
日期: 2025-11-25
版本: v1.0
"""

import ast
import json
import logging
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TechnicalDebtAnalyzer:
    """技术负债分析器"""

    def __init__(self, project_root: str = "/opt/claude/mystocks_spec"):
        self.project_root = Path(project_root)
        self.issues = defaultdict(list)
        self.stats = {
            "total_files": 0,
            "python_files": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
        }

    def analyze_all(self) -> Dict[str, Any]:
        """执行全面的技术负债分析"""
        logger.info("开始技术负债分析...")

        # 1. 代码质量分析
        self.analyze_code_quality()

        # 2. 架构债务分析
        self.analyze_architecture_debt()

        # 3. 性能问题分析
        self.analyze_performance_issues()

        # 4. 安全问题分析
        self.analyze_security_issues()

        # 5. 依赖问题分析
        self.analyze_dependency_issues()

        # 6. 测试覆盖分析
        self.analyze_test_coverage()

        # 7. 文档问题分析
        self.analyze_documentation_issues()

        # 8. 配置管理问题分析
        self.analyze_configuration_issues()

        return {
            "analysis_summary": self.generate_summary(),
            "detailed_issues": dict(self.issues),
            "recommendations": self.generate_recommendations(),
            "technical_debt_score": self.calculate_debt_score(),
            "priority_actions": self.get_priority_actions(),
        }

    def analyze_code_quality(self):
        """分析代码质量问题"""
        logger.info("分析代码质量...")

        python_files = list(self.project_root.rglob("*.py"))
        self.stats["total_files"] = len(list(self.project_root.rglob("*"))) - len(
            list(self.project_root.rglob("__pycache__"))
        )
        self.stats["python_files"] = len(python_files)

        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")
                    self.stats["total_lines"] += len(lines)

                # 解析AST
                tree = ast.parse(content, filename=str(py_file))

                # 分析各种代码质量问题
                self._analyze_long_functions(py_file, tree, lines)
                self._analyze_complex_functions(py_file, tree)
                self._analyze_dead_imports(py_file, tree, content)
                self._analyze_code_duplication(py_file, content, lines)
                self._analyze_naming_issues(py_file, tree)
                self._analyze_file_complexity(py_file, tree)

            except Exception as e:
                self.issues["parsing_errors"].append(
                    {"file": str(py_file), "error": str(e), "category": "code_quality"}
                )

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
        ]

        skip_patterns.extend([".pyc", ".pyo", ".pyd"])

        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
        return False

    def _analyze_long_functions(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """分析过长的函数"""

        class FunctionAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path, lines):
                self.file_path = file_path
                self.lines = lines

            def visit_FunctionDef(self, node):
                # 计算函数行数（包括注释和空行）
                func_start = node.lineno - 1
                func_end = node.end_lineno if hasattr(node, "end_lineno") else len(self.lines)
                func_lines = func_end - func_start

                # 警告阈值：50行以上的函数
                if func_lines > 50:
                    self.file_path.parent.parent.parent.parent.issues["long_functions"].append(
                        {
                            "file": str(self.file_path),
                            "function": node.name,
                            "line_count": func_lines,
                            "start_line": node.lineno,
                            "end_line": func_end,
                            "category": "code_quality",
                            "severity": "high" if func_lines > 100 else "medium",
                        }
                    )

                self.generic_visit(node)

        analyzer = FunctionAnalyzer(file_path, lines)
        analyzer.visit(tree)

    def _analyze_complex_functions(self, file_path: Path, tree: ast.AST):
        """分析复杂函数（高圈复杂度）"""

        class ComplexityAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path):
                self.file_path = file_path
                self.complexity = 0

            def visit_FunctionDef(self, node):
                complexity = 1  # 基础复杂度

                # 计算条件语句复杂度
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1

                # 复杂度超过10被认为复杂
                if complexity > 10:
                    self.file_path.parent.parent.parent.parent.issues["complex_functions"].append(
                        {
                            "file": str(self.file_path),
                            "function": node.name,
                            "complexity": complexity,
                            "category": "code_quality",
                            "severity": "high" if complexity > 20 else "medium",
                        }
                    )

                self.generic_visit(node)

        analyzer = ComplexityAnalyzer(file_path)
        analyzer.visit(tree)

    def _analyze_dead_imports(self, file_path: Path, tree: ast.AST, content: str):
        """分析未使用的导入"""

        class ImportAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path, content):
                self.file_path = file_path
                self.content = content
                self.used_names = set()
                self.imported_names = {}

                # 收集使用的名称
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        self.used_names.add(node.id)
                    elif isinstance(node, ast.Attribute):
                        if isinstance(node.value, ast.Name):
                            self.used_names.add(f"{node.value.id}.{node.attr}")

                # 收集导入的名称
                for node in ast.walk(tree):
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
                        self.file_path.parent.parent.parent.parent.issues["dead_imports"].append(
                            {
                                "file": str(self.file_path),
                                "import": alias.name,
                                "asname": alias.asname,
                                "category": "code_quality",
                                "severity": "low",
                            }
                        )

            def visit_ImportFrom(self, node):
                module = node.module or ""
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name not in self.used_names:
                        self.file_path.parent.parent.parent.parent.issues["dead_imports"].append(
                            {
                                "file": str(self.file_path),
                                "import": f"{module}.{alias.name}",
                                "asname": alias.asname,
                                "category": "code_quality",
                                "severity": "low",
                            }
                        )

        analyzer = ImportAnalyzer(file_path, content)
        analyzer.visit(tree)

    def _analyze_code_duplication(self, file_path: Path, content: str, lines: List[str]):
        """分析代码重复"""
        # 简单的重复代码检测：查找重复的行
        line_counts = Counter()
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 10 and not stripped.startswith("#"):  # 忽略太短的行和注释
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
                    }
                )

    def _analyze_naming_issues(self, file_path: Path, tree: ast.AST):
        """分析命名问题"""

        class NamingAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path):
                self.file_path = file_path

            def visit_FunctionDef(self, node):
                # 检查函数命名是否符合规范
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                    self.file_path.parent.parent.parent.parent.issues["naming_issues"].append(
                        {
                            "file": str(self.file_path),
                            "type": "function",
                            "name": node.name,
                            "issue": "function_name_convention",
                            "category": "code_quality",
                            "severity": "low",
                        }
                    )

            def visit_ClassDef(self, node):
                # 检查类命名是否符合规范
                if not re.match(r"^[A-Z][A-Za-z0-9]*$", node.name):
                    self.file_path.parent.parent.parent.parent.issues["naming_issues"].append(
                        {
                            "file": str(self.file_path),
                            "type": "class",
                            "name": node.name,
                            "issue": "class_name_convention",
                            "category": "code_quality",
                            "severity": "medium",
                        }
                    )

        analyzer = NamingAnalyzer(file_path)
        analyzer.visit(tree)

    def _analyze_file_complexity(self, file_path: Path, tree: ast.AST):
        """分析文件复杂度"""

        class FileComplexityAnalyzer(ast.NodeVisitor):
            def __init__(self, file_path):
                self.file_path = file_path
                self.classes = 0
                self.functions = 0
                self.imports = 0

            def visit_ClassDef(self, node):
                self.classes += 1

            def visit_FunctionDef(self, node):
                self.functions += 1

            def visit_Import(self, node):
                self.imports += len(node.names)

            def visit_ImportFrom(self, node):
                self.imports += len(node.names)

        analyzer = FileComplexityAnalyzer(file_path)
        analyzer.visit(tree)

        # 文件太复杂（超过500行或类/函数太多）
        file_lines = len(tree.body) if hasattr(tree, "body") else 0

        # 这个检查需要基于实际文件长度，让我们重新读取
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                actual_lines = len(f.readlines())

            if actual_lines > 500:
                self.issues["large_files"].append(
                    {"file": str(file_path), "line_count": actual_lines, "category": "code_quality", "severity": "high"}
                )
        except:
            pass

    def analyze_architecture_debt(self):
        """分析架构债务"""
        logger.info("分析架构债务...")

        # 分析模块耦合
        self._analyze_coupling()

        # 分析违反单一职责原则
        self._analyze_single_responsibility()

        # 分析循环依赖
        self._analyze_circular_dependencies()

        # 分析依赖倒置
        self._analyze_dependency_inversion()

    def _analyze_coupling(self):
        """分析模块耦合"""
        import_graph = defaultdict(set)

        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    tree = ast.parse(content)

                # 分析导入依赖
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_graph[str(py_file)].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        import_graph[str(py_file)].add(module)
            except:
                continue

        # 找出高耦合模块
        for module, deps in import_graph.items():
            if len(deps) > 20:  # 依赖超过20个模块
                self.issues["high_coupling"].append(
                    {
                        "file": module,
                        "dependency_count": len(deps),
                        "dependencies": list(deps),
                        "category": "architecture",
                        "severity": "high",
                    }
                )

    def _analyze_single_responsibility(self):
        """分析单一职责原则违反"""
        # 这里需要更复杂的分析，暂时标记为架构债务
        self.issues["architecture_concerns"].append(
            {
                "category": "architecture",
                "issue": "单一职责原则需要进一步分析",
                "severity": "medium",
                "recommendation": "建议进行更深入的架构分析",
            }
        )

    def _analyze_circular_dependencies(self):
        """分析循环依赖"""
        # 简化的循环依赖检测
        python_files = [f for f in list(self.project_root.rglob("*.py")) if not self._should_skip_file(f)]

        # 构建依赖图
        dependencies = defaultdict(set)

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module
                        if module and module.startswith("src."):
                            dependencies[str(py_file)].add(module)
            except:
                continue

        # 简化检测循环依赖（需要更复杂算法）
        self.issues["architecture_concerns"].append(
            {
                "category": "architecture",
                "issue": "循环依赖检测需要完善",
                "severity": "medium",
                "recommendation": "建议使用专业工具如pycircular进行检测",
            }
        )

    def _analyze_dependency_inversion(self):
        """分析依赖倒置原则"""
        # 检查是否正确使用依赖注入
        self.issues["architecture_concerns"].append(
            {
                "category": "architecture",
                "issue": "依赖注入模式使用情况需要评估",
                "severity": "medium",
                "recommendation": "检查是否应该使用依赖注入容器",
            }
        )

    def analyze_performance_issues(self):
        """分析性能问题"""
        logger.info("分析性能问题...")

        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # 检查常见的性能反模式
                self._check_n_plus_one_queries(py_file, content)
                self._check_synchronous_io(py_file, content)
                self._check_memory_intensive_operations(py_file, content)
                self._check_inefficient_data_structures(py_file, content)

            except Exception as e:
                logger.warning(f"分析性能问题失败 {py_file}: {e}")

    def _check_n_plus_one_queries(self, file_path: Path, content: str):
        """检查N+1查询问题"""
        # 查找数据库查询模式
        query_patterns = [
            r"\.query\s*\(",
            r"\.execute\s*\(",
            r"\.fetch\s*\(",
            r"sql\.execute",
        ]

        for pattern in query_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if len(matches) > 5:  # 超过5个查询可能有问题
                self.issues["performance_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "potential_n_plus_one",
                        "query_count": len(matches),
                        "category": "performance",
                        "severity": "medium",
                    }
                )
                break

    def _check_synchronous_io(self, file_path: Path, content: str):
        """检查同步I/O操作"""
        sync_patterns = [
            r"requests\.get\s*\(",
            r"requests\.post\s*\(",
            r"open\s*\(",
            r"file\.read\s*\(",
        ]

        for pattern in sync_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues["performance_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "synchronous_io",
                        "pattern": pattern,
                        "category": "performance",
                        "severity": "low",
                    }
                )
                break

    def _check_memory_intensive_operations(self, file_path: Path, content: str):
        """检查内存密集型操作"""
        memory_patterns = [
            r"\.read\s*\(\)",
            r"json\.loads\s*\(",
            r"eval\s*\(",
        ]

        for pattern in memory_patterns:
            if re.search(pattern, content):
                self.issues["performance_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "memory_intensive",
                        "pattern": pattern,
                        "category": "performance",
                        "severity": "medium",
                    }
                )
                break

    def _check_inefficient_data_structures(self, file_path: Path, content: str):
        """检查低效数据结构"""
        # 检查是否使用list作为dictionary的key
        if "list(" in content and "dict(" in content:
            self.issues["performance_issues"].append(
                {
                    "file": str(file_path),
                    "issue": "inefficient_data_structure",
                    "category": "performance",
                    "severity": "low",
                }
            )

    def analyze_security_issues(self):
        """分析安全问题"""
        logger.info("分析安全问题...")

        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # 检查常见安全漏洞
                self._check_hardcoded_secrets(py_file, content)
                self._check_sql_injection(py_file, content)
                self._check_insecure_file_operations(py_file, content)
                self._check_unsafe_eval(py_file, content)

            except Exception as e:
                logger.warning(f"分析安全问题失败 {py_file}: {e}")

    def _check_hardcoded_secrets(self, file_path: Path, content: str):
        """检查硬编码密钥"""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
        ]

        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                self.issues["security_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "hardcoded_secret",
                        "matches": matches[:3],  # 只记录前3个
                        "category": "security",
                        "severity": "high",
                    }
                )
                break

    def _check_sql_injection(self, file_path: Path, content: str):
        """检查SQL注入风险"""
        sql_patterns = [
            r'\.execute\s*\(\s*["\'].*%.*["\'].*\)',
            r'cursor\.execute\s*\(\s*f["\'].*\{{.*\}}.*["\'].*\)',
        ]

        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues["security_issues"].append(
                    {"file": str(file_path), "issue": "sql_injection_risk", "category": "security", "severity": "high"}
                )
                break

    def _check_insecure_file_operations(self, file_path: Path, content: str):
        """检查不安全的文件操作"""
        insecure_patterns = [
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(",
            r"exec\s*\(",
            r"eval\s*\(",
        ]

        for pattern in insecure_patterns:
            if re.search(pattern, content):
                self.issues["security_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "insecure_file_operation",
                        "pattern": pattern,
                        "category": "security",
                        "severity": "medium",
                    }
                )
                break

    def _check_unsafe_eval(self, file_path: Path, content: str):
        """检查不安全的eval使用"""
        if "eval(" in content:
            self.issues["security_issues"].append(
                {"file": str(file_path), "issue": "unsafe_eval", "category": "security", "severity": "high"}
            )

    def analyze_dependency_issues(self):
        """分析依赖问题"""
        logger.info("分析依赖问题...")

        # 分析requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            self._analyze_requirements(requirements_file)

        # 分析Docker依赖
        dockerfiles = list(self.project_root.rglob("Dockerfile*"))
        for dockerfile in dockerfiles:
            self._analyze_docker_dependencies(dockerfile)

        # 分析package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            self._analyze_package_json(package_json)

    def _analyze_requirements(self, requirements_file: Path):
        """分析requirements.txt"""
        try:
            with open(requirements_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # 检查版本固定
                    if "==" not in line and ">=" not in line and "<=" not in line:
                        self.issues["dependency_issues"].append(
                            {
                                "file": str(requirements_file),
                                "package": line,
                                "issue": "unpinned_version",
                                "category": "dependencies",
                                "severity": "medium",
                            }
                        )
        except Exception as e:
            logger.warning(f"分析requirements.txt失败: {e}")

    def _analyze_docker_dependencies(self, dockerfile: Path):
        """分析Docker依赖"""
        try:
            with open(dockerfile, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 检查latest标签使用
            if "FROM.*:latest" in content:
                self.issues["dependency_issues"].append(
                    {
                        "file": str(dockerfile),
                        "issue": "using_latest_tag",
                        "category": "dependencies",
                        "severity": "low",
                    }
                )
        except Exception as e:
            logger.warning(f"分析Dockerfile失败 {dockerfile}: {e}")

    def _analyze_package_json(self, package_json: Path):
        """分析package.json"""
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 检查devDependencies和dependencies的版本固定
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in data:
                    for package, version in data[dep_type].items():
                        if version == "*" or version == "latest":
                            self.issues["dependency_issues"].append(
                                {
                                    "file": str(package_json),
                                    "package": package,
                                    "version": version,
                                    "issue": "unpinned_version",
                                    "dependency_type": dep_type,
                                    "category": "dependencies",
                                    "severity": "medium",
                                }
                            )
        except Exception as e:
            logger.warning(f"分析package.json失败: {e}")

    def analyze_test_coverage(self):
        """分析测试覆盖"""
        logger.info("分析测试覆盖...")

        # 查找测试文件
        test_files = list(self.project_root.rglob("test_*.py"))
        test_files.extend(list(self.project_root.rglob("*_test.py")))
        test_files.extend(list(self.project_root.rglob("tests/**/*.py")))

        # 查找源代码文件
        source_files = [
            f for f in list(self.project_root.rglob("*.py")) if not self._should_skip_file(f) and "test" not in str(f)
        ]

        test_to_source_ratio = len(test_files) / max(len(source_files), 1)

        if test_to_source_ratio < 0.1:  # 测试文件比例小于10%
            self.issues["test_issues"].append(
                {
                    "issue": "low_test_coverage_ratio",
                    "test_files": len(test_files),
                    "source_files": len(source_files),
                    "ratio": test_to_source_ratio,
                    "category": "testing",
                    "severity": "high",
                }
            )

        # 检查是否有e2e测试
        e2e_files = list(self.project_root.rglob("e2e/**/*.py"))
        if not e2e_files:
            self.issues["test_issues"].append(
                {"issue": "missing_e2e_tests", "category": "testing", "severity": "medium"}
            )

        # 检查测试配置
        pytest_ini = self.project_root / "pytest.ini"
        if not pytest_ini.exists():
            self.issues["test_issues"].append(
                {"issue": "missing_pytest_config", "category": "testing", "severity": "low"}
            )

    def analyze_documentation_issues(self):
        """分析文档问题"""
        logger.info("分析文档问题...")

        # 统计文档文件
        doc_files = {
            "markdown": list(self.project_root.rglob("*.md")),
            "rst": list(self.project_root.rglob("*.rst")),
            "txt": list(self.project_root.rglob("*.txt")),
        }

        total_doc_files = sum(len(files) for files in doc_files.values())

        # 检查README文件
        readme_files = list(self.project_root.rglob("README*"))
        if not readme_files:
            self.issues["documentation_issues"].append(
                {"issue": "missing_readme", "category": "documentation", "severity": "high"}
            )

        # 检查API文档
        if "docs/api" not in [str(d) for d in self.project_root.rglob("docs/api")]:
            self.issues["documentation_issues"].append(
                {"issue": "missing_api_docs", "category": "documentation", "severity": "medium"}
            )

        # 检查docstrings覆盖率
        python_files = [f for f in list(self.project_root.rglob("*.py")) if not self._should_skip_file(f)]

        files_without_docstrings = 0
        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    tree = ast.parse(content)

                has_docstring = False
                if (
                    isinstance(tree, ast.Module)
                    and tree.body
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                    and isinstance(tree.body[0].value.value, str)
                ):
                    has_docstring = True

                if not has_docstring:
                    files_without_docstrings += 1
            except:
                continue

        if files_without_docstrings > len(python_files) * 0.7:  # 超过70%的文件没有docstring
            self.issues["documentation_issues"].append(
                {
                    "issue": "low_docstring_coverage",
                    "files_without_docstrings": files_without_docstrings,
                    "total_files": len(python_files),
                    "ratio": files_without_docstrings / len(python_files),
                    "category": "documentation",
                    "severity": "medium",
                }
            )

    def analyze_configuration_issues(self):
        """分析配置管理问题"""
        logger.info("分析配置管理问题...")

        # 检查硬编码配置
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # 检查硬编码配置
                if re.search(r'=\s*["\'][^"\']*[\d\.]+["\']', content):  # 硬编码数字
                    self.issues["configuration_issues"].append(
                        {
                            "file": str(py_file),
                            "issue": "hardcoded_numbers",
                            "category": "configuration",
                            "severity": "medium",
                        }
                    )
                    break

                if re.search(r'=\s*["\'][^"\']*(?:localhost|127\.0\.0\.1|3306|5432)["\']', content):
                    self.issues["configuration_issues"].append(
                        {
                            "file": str(py_file),
                            "issue": "hardcoded_config",
                            "category": "configuration",
                            "severity": "high",
                        }
                    )
                    break

            except Exception as e:
                logger.warning(f"分析配置问题失败 {py_file}: {e}")

        # 检查环境变量使用
        env_vars_used = False
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if "os.environ" in content or "getenv" in content:
                    env_vars_used = True
                    break
            except:
                continue

        if not env_vars_used:
            self.issues["configuration_issues"].append(
                {"issue": "no_environment_variables", "category": "configuration", "severity": "medium"}
            )

    def generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        total_issues = sum(len(issues) for issues in self.issues.values())

        category_counts = defaultdict(int)
        severity_counts = defaultdict(int)

        for category, issues in self.issues.items():
            category_counts[category] = len(issues)
            for issue in issues:
                severity_counts[issue.get("severity", "unknown")] += 1

        return {
            "total_issues": total_issues,
            "categories": dict(category_counts),
            "severities": dict(severity_counts),
            "project_stats": dict(self.stats),
            "analysis_date": "2025-11-25",
        }

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []

        # 基于发现的问题生成建议
        if len(self.issues["long_functions"]) > 10:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "code_quality",
                    "title": "重构长函数",
                    "description": f'发现{len(self.issues["long_functions"])}个过长函数，建议进行重构',
                    "actions": ["将长函数拆分为多个小函数", "提取公共逻辑到独立函数", "使用装饰器简化横切关注点"],
                }
            )

        if len(self.issues["security_issues"]) > 0:
            recommendations.append(
                {
                    "priority": "critical",
                    "category": "security",
                    "title": "修复安全漏洞",
                    "description": f'发现{len(self.issues["security_issues"])}个安全问题，需要立即处理',
                    "actions": ["移除硬编码的密钥和密码", "使用环境变量管理敏感配置", "实施输入验证和SQL注入防护"],
                }
            )

        if len(self.issues["test_issues"]) > 0:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "testing",
                    "title": "提高测试覆盖率",
                    "description": "测试覆盖率不足，建议增加单元测试和集成测试",
                    "actions": ["为关键业务逻辑编写单元测试", "实施自动化测试", "增加端到端测试"],
                }
            )

        return recommendations

    def calculate_debt_score(self) -> float:
        """计算技术负债评分（0-100，100为无负债）"""
        score = 100.0

        # 根据问题数量和严重程度扣分
        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}

        total_deduction = 0
        for category, issues in self.issues.items():
            for issue in issues:
                severity = issue.get("severity", "low")
                weight = severity_weights.get(severity, 1)
                total_deduction += weight

        # 根据代码行数调整评分
        if self.stats["code_lines"] > 100000:
            total_deduction *= 1.5
        elif self.stats["code_lines"] > 50000:
            total_deduction *= 1.2

        score = max(0, 100 - total_deduction)
        return round(score, 2)

    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """获取优先处理行动"""
        actions = []

        # 按严重程度排序所有问题
        all_issues = []
        for category, issues in self.issues.items():
            for issue in issues:
                all_issues.append({**issue, "category": category})

        all_issues.sort(
            key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x.get("severity", "low"), 1),
            reverse=True,
        )

        # 取前10个最严重的问题
        for issue in all_issues[:10]:
            actions.append(
                {
                    "priority": issue.get("severity", "low"),
                    "category": issue["category"],
                    "file": issue.get("file", "N/A"),
                    "issue": issue.get("issue", issue.get("category", "unknown")),
                    "description": f"在{issue.get('file', '未知文件')}中发现{issue.get('issue', '问题')}",
                }
            )

        return actions


def main():
    """主函数"""
    analyzer = TechnicalDebtAnalyzer()
    results = analyzer.analyze_all()

    # 生成报告
    report_file = "/opt/claude/mystocks_spec/technical_debt_assessment_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# MyStocks 技术负债评估报告\n\n")
        f.write(f"**评估日期**: {results['analysis_summary']['analysis_date']}\n")
        f.write(f"**技术负债评分**: {results['technical_debt_score']}/100\n\n")

        # 总体概况
        f.write("## 📊 总体概况\n\n")
        summary = results["analysis_summary"]
        f.write(f"- **问题总数**: {summary['total_issues']}\n")
        f.write(f"- **代码文件数**: {summary['project_stats']['python_files']}\n")
        f.write(f"- **总代码行数**: {summary['project_stats']['total_lines']:,}\n")
        f.write(f"- **Python文件数**: {summary['project_stats']['python_files']}\n\n")

        # 按类别统计
        f.write("## 📋 问题分类统计\n\n")
        for category, count in summary["categories"].items():
            severity_info = []
            for issue in results["detailed_issues"][category]:
                severity = issue.get("severity", "unknown")
                if severity not in [s[0] for s in severity_info]:
                    severity_count = sum(
                        1 for i in results["detailed_issues"][category] if i.get("severity") == severity
                    )
                    severity_info.append((severity, severity_count))

            f.write(f"### {category.replace('_', ' ').title()}\n")
            f.write(f"- 总数: {count}\n")
            for severity, count in severity_info:
                f.write(f"- {severity}: {count}\n")
            f.write("\n")

        # 优先行动
        f.write("## 🚨 优先处理行动\n\n")
        for i, action in enumerate(results["priority_actions"][:5], 1):
            f.write(f"{i}. **{action['priority'].upper()}** - {action['description']}\n")
            f.write(f"   - 文件: `{action['file']}`\n")
            f.write(f"   - 类别: {action['category']}\n\n")

        # 优化建议
        f.write("## 💡 优化建议\n\n")
        for rec in results["recommendations"]:
            f.write(f"### {rec['title']} ({rec['priority'].upper()})\n")
            f.write(f"{rec['description']}\n\n")
            f.write("**行动建议**:\n")
            for action in rec["actions"]:
                f.write(f"- {action}\n")
            f.write("\n")

        # 详细问题列表
        f.write("## 📝 详细问题列表\n\n")
        for category, issues in results["detailed_issues"].items():
            if issues:
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                for issue in issues[:20]:  # 只显示前20个问题
                    f.write(f"- **文件**: `{issue.get('file', 'N/A')}`\n")
                    f.write(f"  - **问题**: {issue.get('issue', issue.get('category', 'unknown'))}\n")
                    f.write(f"  - **严重程度**: {issue.get('severity', 'unknown')}\n\n")

                if len(issues) > 20:
                    f.write(f"*... 还有{len(issues) - 20}个类似问题*\n\n")

        f.write("---\n")
        f.write("*本报告由iFlow CLI自动生成 - 技术负债分析器 v1.0*\n")

    logger.info(f"技术负债评估报告已生成: {report_file}")

    # 输出到控制台
    print(f"\n{'='*60}")
    print(f"🔍 MyStocks 技术负债评估报告")
    print(f"{'='*60}")
    print(f"📊 技术负债评分: {results['technical_debt_score']}/100")
    print(f"📋 问题总数: {results['analysis_summary']['total_issues']}")
    print(f"🐍 Python文件: {results['analysis_summary']['project_stats']['python_files']}")
    print(f"📄 总代码行: {results['analysis_summary']['project_stats']['total_lines']:,}")
    print(f"{'='*60}")
    print(f"📝 详细报告: {report_file}")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    main()
