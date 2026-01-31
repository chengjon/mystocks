#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks AI辅助测试工具
提供智能测试用例生成、优化和故障诊断
集成AST分析和项目上下文感知
"""

import ast
import asyncio
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pytest

# Import specific test configuration
try:
    from tests.config.test_config import ai_config, test_data
except ImportError:
    # Fallback if test_config doesn't exist
    ai_config = {}
    test_data = {}


class TestPriority(Enum):
    """测试优先级"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCategory(Enum):
    """测试类别"""

    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"


@dataclass
class TestCase:
    """增强的测试用例数据结构"""

    name: str
    description: str
    code: str
    method_name: str
    coverage: List[str]
    complexity_score: float
    priority: TestPriority
    category: TestCategory
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    execution_time_estimate: float = 0.0
    flakiness_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """增强的代码分析结果"""

    method_name: str
    complexity: int
    length: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    coupling_score: float
    cohesion_score: float
    test_coverage: List[str]
    dependencies: List[str]
    risk_level: str  # low, medium, high
    security_issues: List[str]
    performance_issues: List[str]
    maintainability_score: float


class ProjectContextAnalyzer:
    """项目上下文分析器"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.context_cache = {}

    def get_project_structure(self) -> Dict[str, Any]:
        """获取项目结构"""
        if "structure" in self.context_cache:
            return self.context_cache["structure"]

        structure = {
            "modules": [],
            "config_files": [],
            "test_files": [],
            "api_endpoints": [],
            "business_entities": [],
        }

        # 扫描项目目录
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)

            # 排除特定目录
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules"]]

            # 分析模块
            if "__init__.py" in files:
                module_path = root_path.relative_to(self.project_root)
                structure["modules"].append(str(module_path))

            # 收集配置文件
            for file in files:
                if file.endswith((".yaml", ".yml", ".json", ".toml", ".ini")):
                    structure["config_files"].append(str(root_path / file))

            # 收集测试文件
            if "test_" in file or file.endswith("_test.py"):
                structure["test_files"].append(str(root_path / file))

        self.context_cache["structure"] = structure
        return structure

    def detect_patterns(self, source_code: str) -> Dict[str, Any]:
        """检测代码模式"""
        patterns = {
            "data_models": [],
            "api_handlers": [],
            "business_logic": [],
            "utility_functions": [],
            "external_calls": [],
        }

        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            # 检测数据模型（Pydantic类）
            if isinstance(node, ast.ClassDef) and any(
                isinstance(base, ast.Attribute) and base.attr == "BaseModel"
                for base in node.bases
                if isinstance(base, ast.Attribute)
            ):
                patterns["data_models"].append(node.name)

            # 检测API处理器
            elif isinstance(node, ast.FunctionDef) and (
                "api" in node.name.lower() or "endpoint" in node.name.lower() or "route" in node.name.lower()
            ):
                patterns["api_handlers"].append(node.name)

            # 检测业务逻辑
            elif isinstance(node, ast.FunctionDef) and any(
                keyword in node.name.lower()
                for keyword in [
                    "calculate",
                    "get",
                    "set",
                    "update",
                    "process",
                    "analyze",
                ]
            ):
                patterns["business_logic"].append(node.name)

            # 检测外部调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "requests":
                    patterns["external_calls"].append("HTTP requests detected")
                elif isinstance(node.func, ast.Attribute) and node.func.attr == "fetch":
                    patterns["external_calls"].append("Data fetch detected")

        return patterns


class AITestGenerator:
    """增强的AI测试生成器"""

    def __init__(self, project_context: ProjectContextAnalyzer = None):
        self.test_cache_dir = Path(__file__).parent / "cache"
        self.test_cache_dir.mkdir(exist_ok=True)
        self.context_analyzer = project_context or ProjectContextAnalyzer()
        self.pattern_library = self._load_pattern_library()

    def _load_pattern_library(self) -> Dict[str, Any]:
        """加载测试模式库"""
        return {
            "financial_functions": {
                "patterns": [
                    "get_stock_daily",
                    "get_index_daily",
                    "calculate_profit_loss",
                ],
                "test_cases": [
                    "normal_input",
                    "boundary_conditions",
                    "invalid_symbols",
                    "date_range_validation",
                ],
            },
            "data_processing": {
                "patterns": ["fetch_kline_data", "process_market_data"],
                "test_cases": [
                    "data_format_validation",
                    "missing_data_handling",
                    "data_quality_checks",
                ],
            },
            "api_endpoints": {
                "patterns": ["get_", "post_", "put_", "delete_"],
                "test_cases": [
                    "status_code_verification",
                    "response_schema_validation",
                    "authentication",
                    "rate_limiting",
                ],
            },
        }

    async def generate_test_cases_from_source(self, source_code: str, method_name: str) -> List[TestCase]:
        """从源代码生成测试用例 - 增强版"""
        print(f"🤖 AI正在生成测试用例: {method_name}")

        try:
            # 解析源代码
            tree = ast.parse(source_code)

            # 查找目标方法
            target_method = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    target_method = node
                    break

            if not target_method:
                raise ValueError(f"方法 {method_name} 未找到")

            # 项目上下文分析
            project_structure = self.context_analyzer.get_project_structure()
            detected_patterns = self.context_analyzer.detect_patterns(source_code)

            # 深度分析方法结构
            analysis = await self._analyze_method_structure_enhanced(target_method)

            # 基于上下文生成测试用例
            test_cases = await self._generate_test_cases_for_method_enhanced(
                method_name,
                target_method,
                analysis,
                detected_patterns,
                project_structure,
            )

            # 优化测试用例
            optimized_cases = await self._optimize_test_cases(test_cases)

            return optimized_cases

        except Exception as e:
            print(f"❌ 测试用例生成失败: {str(e)}")
            return []

    async def _analyze_method_structure_enhanced(self, method_node: ast.FunctionDef) -> AnalysisResult:
        """增强的方法结构分析"""
        # 基础分析
        args = []
        parameters = []
        return_types = []
        exceptions = []

        # 提取参数信息
        for arg in method_node.args.args:
            args.append(arg.arg)
            parameters.append(
                {
                    "name": arg.arg,
                    "type": self._get_annotation_type(arg.annotation),
                    "has_default": arg.default is not None,
                }
            )

        # 分析异常处理
        exceptions = self._extract_exception_types(method_node)

        # 计算各种复杂度
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(method_node)
        cognitive_complexity = self._calculate_cognitive_complexity(method_node)
        coupling_score = self._calculate_coupling_score(method_node)
        cohesion_score = self._calculate_cohesion_score(method_node)

        # 分析安全问题和性能问题
        security_issues = self._analyze_security_issues(method_node)
        performance_issues = self._analyze_performance_issues(method_node)

        # 计算可维护性分数
        maintainability_score = self._calculate_maintainability_score(
            cyclomatic_complexity, cognitive_complexity, coupling_score, cohesion_score
        )

        return AnalysisResult(
            method_name=method_node.name,
            complexity=len(method_node.body),
            length=len(method_node.body),
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_complexity=cognitive_complexity,
            coupling_score=coupling_score,
            cohesion_score=cohesion_score,
            test_coverage=[],
            dependencies=self._extract_dependencies(method_node),
            risk_level=self._assess_risk_level(cyclomatic_complexity, coupling_score),
            security_issues=security_issues,
            performance_issues=performance_issues,
            maintainability_score=maintainability_score,
        )

    def _analyze_method_structure(self, method_node: ast.FunctionDef) -> Dict[str, Any]:
        """分析方法结构 - 兼容性方法"""
        analysis = {
            "arguments": [],
            "parameters": [],
            "return_types": [],
            "exceptions": [],
            "complexity": self._calculate_complexity(method_node),
            "length": len(method_node.body),
            "control_flow": [],
        }

        # 提取参数信息
        for arg in method_node.args.args:
            analysis["arguments"].append(arg.arg)
            analysis["parameters"].append({"name": arg.arg, "type": self._get_annotation_type(arg.annotation)})

        # 分析控制流
        for node in method_node.body:
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                analysis["control_flow"].append(type(node).__name__)

        return analysis

    # 新增的增强分析方法
    def _extract_exception_types(self, method_node: ast.FunctionDef) -> List[str]:
        """提取异常类型"""
        exceptions = []
        for node in ast.walk(method_node):
            if isinstance(node, ast.ExceptHandler):
                if node.type:
                    if isinstance(node.type, ast.Name):
                        exceptions.append(node.type.id)
                    elif isinstance(node.type, ast.Attribute):
                        exceptions.append(node.type.attr)
        return list(set(exceptions))

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度 - 增强版"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.ExceptHandler,
                    ast.With,
                    ast.AsyncWith,
                    ast.comprehension,
                    ast.DictComp,
                    ast.ListComp,
                    ast.SetComp,
                    ast.GeneratorExp,
                ),
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Compare):
                complexity += len(child.ops) - 1

        return complexity

    def _calculate_cognitive_complexity(self, node: ast.FunctionDef) -> int:
        """计算认知复杂度"""
        complexity = 0
        nesting_level = 0

        def _calculate_complexity_recursive(n, level):
            nonlocal complexity
            complexity += level

            for child in ast.iter_child_nodes(n):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                    _calculate_complexity_recursive(child, level + 1)
                else:
                    _calculate_complexity_recursive(child, level)

        _calculate_complexity_recursive(node, 0)
        return complexity

    def _calculate_coupling_score(self, node: ast.FunctionDef) -> float:
        """计算耦合度分数"""
        external_calls = 0
        internal_calls = 0

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    internal_calls += 1
                elif isinstance(child.func, ast.Attribute):
                    # 检查是否是外部调用
                    if child.func.value.id not in ["self", "cls", "pytest"]:
                        external_calls += 1

        total_calls = internal_calls + external_calls
        if total_calls == 0:
            return 0.0

        return external_calls / total_calls

    def _calculate_cohesion_score(self, node: ast.FunctionDef) -> float:
        """计算内聚度分数"""
        variables = set()
        variable_usages = {}

        # 收集变量定义和使用
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                variables.add(child.id)
                variable_usages[child.id] = 0
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                if child.id in variable_usages:
                    variable_usages[child.id] += 1

        if len(variables) == 0:
            return 1.0

        # 计算内聚度
        total_usages = sum(variable_usages.values())
        if total_usages == 0:
            return 0.5

        return min(total_usages / (len(variables) * 2), 1.0)

    def _extract_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """提取依赖项"""
        dependencies = []

        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    dependencies.append(alias.name)
            elif isinstance(child, ast.ImportFrom):
                if child.module:
                    dependencies.append(child.module)

        return list(set(dependencies))

    def _analyze_security_issues(self, node: ast.FunctionDef) -> List[str]:
        """分析安全问题"""
        security_issues = []

        # 检查SQL注入风险
        for child in ast.walk(node):
            if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Mod):
                if isinstance(child.left, ast.Constant) and "SELECT" in str(child.left.value):
                    security_issues.append("潜在的SQL注入风险")

        # 检查命令注入风险
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute) and child.func.attr in [
                    "exec",
                    "eval",
                ]:
                    security_issues.append("命令注入风险")

        # 检查敏感数据日志
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute) and child.func.attr in [
                    "print",
                    "logger",
                    "log",
                ]:
                    if isinstance(child.args[0], ast.Constant) and "password" in str(child.args[0]).lower():
                        security_issues.append("敏感数据可能被记录")

        return security_issues

    def _analyze_performance_issues(self, node: ast.FunctionDef) -> List[str]:
        """分析性能问题"""
        performance_issues = []

        # 检查循环中可能的性能问题
        loops = []
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                loops.append(child)

        # 检查嵌套循环
        for i, loop1 in enumerate(loops):
            for loop2 in loops[i + 1 :]:
                if self._is_nested_loop(loop1, loop2):
                    performance_issues.append("深层嵌套循环可能影响性能")
                    break

        # 检查重复计算
        calculations = []
        for child in ast.walk(node):
            if isinstance(child, ast.BinOp) and isinstance(child.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                calculations.append(child)

        # 简单的重复检测
        calc_strs = [ast.dump(calc) for calc in calculations]
        if len(calc_strs) != len(set(calc_strs)):
            performance_issues.append("可能存在重复计算")

        return performance_issues

    def _is_nested_loop(self, outer: ast.AST, inner: ast.AST) -> bool:
        """检查循环是否嵌套"""
        outer_line = outer.lineno
        outer_end = getattr(outer, "end_lineno", outer_line + 1)
        inner_line = inner.lineno
        inner_end = getattr(inner, "end_lineno", inner_line + 1)

        return inner_line > outer_line and inner_end <= outer_end

    def _calculate_maintainability_score(
        self, cyclomatic: int, cognitive: int, coupling: float, cohesion: float
    ) -> float:
        """计算可维护性分数"""
        # 基于多个因素计算综合分数
        complexity_score = max(0, (20 - cyclomatic - cognitive) / 20)
        coupling_score = max(0, (1 - coupling))
        cohesion_score = cohesion

        # 加权平均
        overall_score = complexity_score * 0.4 + coupling_score * 0.3 + cohesion_score * 0.3

        return round(overall_score, 2)

    def _assess_risk_level(self, cyclomatic_complexity: int, coupling_score: float) -> str:
        """评估风险等级"""
        if cyclomatic_complexity > 20 or coupling_score > 0.8:
            return "high"
        elif cyclomatic_complexity > 10 or coupling_score > 0.6:
            return "medium"
        else:
            return "low"

    async def _generate_test_cases_for_method_enhanced(
        self,
        method_name: str,
        method_node: ast.FunctionDef,
        analysis: AnalysisResult,
        patterns: Dict[str, Any],
        project_structure: Dict[str, Any],
    ) -> List[TestCase]:
        """为方法生成测试用例 - 增强版"""
        test_cases = []

        # 基于项目结构确定测试类别
        category = self._determine_test_category(method_name, patterns, project_structure)

        # 基于分析结果确定优先级
        priority = self._determine_test_priority(analysis)

        # 1. 基础功能测试
        normal_cases = self._create_normal_cases_enhanced(method_name, analysis, category, priority)
        test_cases.extend(normal_cases)

        # 2. 边界条件测试
        boundary_cases = self._create_boundary_cases_enhanced(method_name, analysis, category, priority)
        test_cases.extend(boundary_cases)

        # 3. 异常处理测试
        exception_cases = self._create_exception_cases_enhanced(method_name, analysis, category, priority)
        test_cases.extend(exception_cases)

        # 4. 参数验证测试
        validation_cases = self._create_validation_cases_enhanced(method_name, analysis, category, priority)
        test_cases.extend(validation_cases)

        # 5. 安全测试
        security_cases = self._create_security_test_cases(method_name, analysis, category, priority)
        test_cases.extend(security_cases)

        # 6. 性能测试
        performance_cases = self._create_performance_test_cases(method_name, analysis, category, priority)
        test_cases.extend(performance_cases)

        # 7. 模式特定的测试用例
        pattern_cases = self._create_pattern_specific_tests(method_name, patterns, category, priority)
        test_cases.extend(pattern_cases)

        return test_cases

    def _determine_test_category(
        self,
        method_name: str,
        patterns: Dict[str, Any],
        project_structure: Dict[str, Any],
    ) -> TestCategory:
        """确定测试类别"""
        method_lower = method_name.lower()

        # API处理函数
        if any(pattern in method_lower for pattern in ["get_", "post_", "put_", "delete_", "api_", "endpoint"]):
            return TestCategory.INTEGRATION

        # 数据处理函数
        elif any(pattern in method_lower for pattern in ["calculate_", "process_", "analyze_", "transform_"]):
            return TestCategory.PERFORMANCE

        # 业务逻辑函数
        elif any(pattern in method_lower for pattern in ["get_", "set_", "update_", "save_", "delete_"]):
            return TestCategory.UNIT

        # 安全相关函数
        elif any(pattern in method_lower for pattern in ["auth_", "validate_", "encrypt_", "decrypt_"]):
            return TestCategory.SECURITY

        else:
            return TestCategory.UNIT

    def _determine_test_priority(self, analysis: AnalysisResult) -> TestPriority:
        """确定测试优先级"""
        # 基于风险等级、复杂度和安全/性能问题
        priority_score = 0

        # 风险等级权重
        if analysis.risk_level == "high":
            priority_score += 3
        elif analysis.risk_level == "medium":
            priority_score += 2

        # 复杂度权重
        if analysis.cyclomatic_complexity > 15:
            priority_score += 3
        elif analysis.cyclomatic_complexity > 8:
            priority_score += 2

        # 安全问题权重
        priority_score += len(analysis.security_issues) * 2

        # 性能问题权重
        priority_score += len(analysis.performance_issues) * 1

        # 可维护性分数权重
        if analysis.maintainability_score < 0.5:
            priority_score += 2

        # 确定优先级
        if priority_score >= 8:
            return TestPriority.CRITICAL
        elif priority_score >= 5:
            return TestPriority.HIGH
        elif priority_score >= 3:
            return TestPriority.MEDIUM
        else:
            return TestPriority.LOW

    async def _create_normal_cases_enhanced(
        self,
        method_name: str,
        analysis: AnalysisResult,
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建正常测试用例"""
        test_cases = []

        # 基础功能测试
        basic_case = TestCase(
            name=f"test_{method_name}_basic",
            description=f"基本功能测试: {method_name}",
            code=self._generate_basic_test_case(analysis),
            category=category,
            priority=priority,
            method_name=method_name,
            coverage=["normal_input"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "basic"},
        )
        test_cases.append(basic_case)

        # 参数验证测试
        if analysis.parameters:
            param_validation_case = TestCase(
                name=f"test_{method_name}_parameter_validation",
                description=f"参数验证测试: {method_name}",
                code=self._generate_parameter_validation_test(analysis),
                category=TestCategory.UNIT,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["parameter_validation"],
                complexity_score=analysis.cyclomatic_complexity,
                metadata={
                    "complexity": analysis.complexity,
                    "type": "parameter_validation",
                },
            )
            test_cases.append(param_validation_case)

        # 返回值测试
        return_case = TestCase(
            name=f"test_{method_name}_return_validation",
            description=f"返回值验证测试: {method_name}",
            code=self._generate_return_validation_test(analysis),
            category=TestCategory.UNIT,
            priority=self._adjust_priority(priority, 1),
            method_name=method_name,
            coverage=["return_validation"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "return_validation"},
        )
        test_cases.append(return_case)

        return test_cases

    async def _create_boundary_cases_enhanced(
        self,
        method_name: str,
        analysis: AnalysisResult,
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建边界测试用例"""
        test_cases = []

        # 边界条件测试
        if analysis.complexity > 3:
            boundary_case = TestCase(
                name=f"test_{method_name}_boundary",
                description=f"边界条件测试: {method_name}",
                code=self._generate_boundary_test_case(analysis),
                category=TestCategory.INTEGRATION,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["boundary_conditions"],
                complexity_score=analysis.cyclomatic_complexity,
                metadata={"complexity": analysis.complexity, "type": "boundary"},
            )
            test_cases.append(boundary_case)

        # 极值测试
        extreme_case = TestCase(
            name=f"test_{method_name}_extreme_values",
            description=f"极值测试: {method_name}",
            code=self._generate_extreme_values_test(analysis),
            category=TestCategory.PERFORMANCE,
            priority=self._adjust_priority(priority, 2),
            method_name=method_name,
            coverage=["extreme_values"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "extreme_values"},
        )
        test_cases.append(extreme_case)

        # 空值测试
        null_case = TestCase(
            name=f"test_{method_name}_null_values",
            description=f"空值测试: {method_name}",
            code=self._generate_null_values_test(analysis),
            category=TestCategory.UNIT,
            priority=self._adjust_priority(priority, 1),
            method_name=method_name,
            coverage=["null_values"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "null_values"},
        )
        test_cases.append(null_case)

        return test_cases

    async def _create_exception_cases_enhanced(
        self,
        method_name: str,
        analysis: AnalysisResult,
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建异常测试用例"""
        test_cases = []

        # 异常处理测试
        exception_case = TestCase(
            name=f"test_{method_name}_exceptions",
            description=f"异常处理测试: {method_name}",
            code=self._generate_exception_test_case(analysis),
            category=TestCategory.SECURITY,
            priority=self._adjust_priority(priority, 2),
            method_name=method_name,
            coverage=["exception_handling"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={
                "complexity": analysis.complexity,
                "security_issues": analysis.security_issues,
                "performance_issues": analysis.performance_issues,
            },
        )
        test_cases.append(exception_case)

        # 错误传播测试
        error_propagation_case = TestCase(
            name=f"test_{method_name}_error_propagation",
            description=f"错误传播测试: {method_name}",
            code=self._generate_error_propagation_test(analysis),
            category=TestCategory.INTEGRATION,
            priority=self._adjust_priority(priority, 2),
            method_name=method_name,
            coverage=["error_propagation"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "error_propagation"},
        )
        test_cases.append(error_propagation_case)

        # 资源清理测试
        if analysis.performance_issues and any("resource" in issue for issue in analysis.performance_issues):
            cleanup_case = TestCase(
                name=f"test_{method_name}_resource_cleanup",
                description=f"资源清理测试: {method_name}",
                code=self._generate_resource_cleanup_test(analysis),
                category=TestCategory.PERFORMANCE,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["resource_cleanup"],
                complexity_score=analysis.cyclomatic_complexity,
                metadata={
                    "complexity": analysis.complexity,
                    "type": "resource_cleanup",
                },
            )
            test_cases.append(cleanup_case)

        return test_cases

    async def _create_validation_cases_enhanced(
        self,
        method_name: str,
        analysis: AnalysisResult,
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建验证测试用例"""
        test_cases = []

        # 输入验证测试
        input_validation_case = TestCase(
            name=f"test_{method_name}_input_validation",
            description=f"输入验证测试: {method_name}",
            code=self._generate_input_validation_test(analysis),
            category=TestCategory.SECURITY,
            priority=self._adjust_priority(priority, 1),
            method_name=method_name,
            coverage=["input_validation"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "input_validation"},
        )
        test_cases.append(input_validation_case)

        # 类型验证测试
        type_validation_case = TestCase(
            name=f"test_{method_name}_type_validation",
            description=f"类型验证测试: {method_name}",
            code=self._generate_type_validation_test(analysis),
            category=TestCategory.UNIT,
            priority=self._adjust_priority(priority, 1),
            method_name=method_name,
            coverage=["type_validation"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "type_validation"},
        )
        test_cases.append(type_validation_case)

        # 格式验证测试
        format_validation_case = TestCase(
            name=f"test_{method_name}_format_validation",
            description=f"格式验证测试: {method_name}",
            code=self._generate_format_validation_test(analysis),
            category=TestCategory.UNIT,
            priority=self._adjust_priority(priority, 2),
            method_name=method_name,
            coverage=["format_validation"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "format_validation"},
        )
        test_cases.append(format_validation_case)

        return test_cases

    async def _create_security_test_cases(
        self,
        method_name: str,
        analysis: AnalysisResult,
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建安全测试用例"""
        test_cases = []

        # SQL注入测试
        if analysis.security_issues and any("sql" in issue.lower() for issue in analysis.security_issues):
            sql_injection_case = TestCase(
                name=f"test_{method_name}_sql_injection",
                description=f"SQL注入防护测试: {method_name}",
                code=self._generate_sql_injection_test(analysis),
                category=TestCategory.SECURITY,
                priority=TestPriority.CRITICAL,
                method_name=method_name,
                coverage=["sql_injection"],
                complexity_score=analysis.cyclomatic_complexity,
                metadata={"complexity": analysis.complexity, "type": "sql_injection"},
            )
            test_cases.append(sql_injection_case)

        # XSS测试
        xss_case = TestCase(
            name=f"test_{method_name}_xss_protection",
            description=f"XSS防护测试: {method_name}",
            code=self._generate_xss_test(analysis),
            category=TestCategory.SECURITY,
            priority=TestPriority.CRITICAL,
            method_name=method_name,
            coverage=["xss_protection"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "xss_protection"},
        )
        test_cases.append(xss_case)

        # CSRF测试
        csrf_case = TestCase(
            name=f"test_{method_name}_csrf_protection",
            description=f"CSRF防护测试: {method_name}",
            code=self._generate_csrf_test(analysis),
            category=TestCategory.SECURITY,
            priority=TestPriority.CRITICAL,
            method_name=method_name,
            coverage=["csrf_protection"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "csrf_protection"},
        )
        test_cases.append(csrf_case)

        # 权限验证测试
        auth_case = TestCase(
            name=f"test_{method_name}_authorization",
            description=f"权限验证测试: {method_name}",
            code=self._generate_authorization_test(analysis),
            category=TestCategory.SECURITY,
            priority=TestPriority.HIGH,
            method_name=method_name,
            coverage=["authorization"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "authorization"},
        )
        test_cases.append(auth_case)

        return test_cases

    async def _create_performance_test_cases(
        self,
        method_name: str,
        analysis: AnalysisResult,
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建性能测试用例"""
        test_cases = []

        # 性能基准测试
        performance_case = TestCase(
            name=f"test_{method_name}_performance",
            description=f"性能基准测试: {method_name}",
            code=self._generate_performance_test(analysis),
            category=TestCategory.PERFORMANCE,
            priority=self._adjust_priority(priority, 1),
            method_name=method_name,
            coverage=["performance_benchmark"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={
                "complexity": analysis.complexity,
                "type": "performance_benchmark",
            },
        )
        test_cases.append(performance_case)

        # 内存使用测试
        memory_case = TestCase(
            name=f"test_{method_name}_memory_usage",
            description=f"内存使用测试: {method_name}",
            code=self._generate_memory_usage_test(analysis),
            category=TestCategory.PERFORMANCE,
            priority=self._adjust_priority(priority, 2),
            method_name=method_name,
            coverage=["memory_usage"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "memory_usage"},
        )
        test_cases.append(memory_case)

        # 并发测试
        if analysis.cyclomatic_complexity > 5:
            concurrency_case = TestCase(
                name=f"test_{method_name}_concurrency",
                description=f"并发测试: {method_name}",
                code=self._generate_concurrency_test(analysis),
                category=TestCategory.PERFORMANCE,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["concurrency"],
                complexity_score=analysis.cyclomatic_complexity,
                metadata={"complexity": analysis.complexity, "type": "concurrency"},
            )
            test_cases.append(concurrency_case)

        # 超时测试
        timeout_case = TestCase(
            name=f"test_{method_name}_timeout",
            description=f"超时测试: {method_name}",
            code=self._generate_timeout_test(analysis),
            category=TestCategory.PERFORMANCE,
            priority=self._adjust_priority(priority, 2),
            method_name=method_name,
            coverage=["timeout"],
            complexity_score=analysis.cyclomatic_complexity,
            metadata={"complexity": analysis.complexity, "type": "timeout"},
        )
        test_cases.append(timeout_case)

        return test_cases

    async def _create_pattern_specific_tests(
        self,
        method_name: str,
        patterns: Dict[str, Any],
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建特定模式测试"""
        test_cases = []

        # 递归函数测试
        if self._is_recursive_function(method_name):
            recursive_case = TestCase(
                name=f"test_{method_name}_recursive",
                description=f"递归函数测试: {method_name}",
                code=self._generate_recursive_test(method_name),
                category=TestCategory.PERFORMANCE,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["recursive"],
                complexity_score=10.0,  # 递归函数复杂度较高
                metadata={"type": "recursive"},
            )
            test_cases.append(recursive_case)

        # 回调函数测试
        if self._has_callback_function(method_name):
            callback_case = TestCase(
                name=f"test_{method_name}_callback",
                description=f"回调函数测试: {method_name}",
                code=self._generate_callback_test(method_name),
                category=TestCategory.INTEGRATION,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["callback"],
                complexity_score=8.0,
                metadata={"type": "callback"},
            )
            test_cases.append(callback_case)

        # 异步函数测试
        if self._is_async_function(method_name):
            async_case = TestCase(
                name=f"test_{method_name}_async",
                description=f"异步函数测试: {method_name}",
                code=self._generate_async_test(method_name),
                category=TestCategory.INTEGRATION,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["async"],
                complexity_score=8.0,
                metadata={"type": "async"},
            )
            test_cases.append(async_case)

        # 状态管理测试
        if self._has_state_management(method_name):
            state_case = TestCase(
                name=f"test_{method_name}_state_management",
                description=f"状态管理测试: {method_name}",
                code=self._generate_state_management_test(method_name),
                category=TestCategory.INTEGRATION,
                priority=self._adjust_priority(priority, 2),
                method_name=method_name,
                coverage=["state_management"],
                complexity_score=9.0,
                metadata={"type": "state_management"},
            )
            test_cases.append(state_case)

        # 事务测试
        if self._has_transaction_logic(method_name):
            transaction_case = TestCase(
                name=f"test_{method_name}_transaction",
                description=f"事务测试: {method_name}",
                code=self._generate_transaction_test(method_name),
                category=TestCategory.INTEGRATION,
                priority=self._adjust_priority(priority, 1),
                method_name=method_name,
                coverage=["transaction"],
                complexity_score=8.0,
                metadata={"type": "transaction"},
            )
            test_cases.append(transaction_case)

        return test_cases

    # Helper methods for test case generation
    def _adjust_priority(self, priority: TestPriority, adjustment: int) -> TestPriority:
        """调整优先级"""
        priority_order = [
            TestPriority.LOW,
            TestPriority.MEDIUM,
            TestPriority.HIGH,
            TestPriority.CRITICAL,
        ]
        current_index = priority_order.index(priority)
        new_index = max(0, min(3, current_index - adjustment))
        return priority_order[new_index]

    def _generate_basic_test_case(self, analysis: AnalysisResult) -> str:
        """生成基础测试用例"""
        return f"""
def test_{analysis.method_name}_basic():
    # 基本功能测试
    # TODO: 实现具体的测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_parameter_validation_test(self, analysis: AnalysisResult) -> str:
        """生成参数验证测试"""
        return f"""
def test_{analysis.method_name}_parameter_validation():
    # 参数验证测试
    # TODO: 实现参数验证逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_return_validation_test(self, analysis: AnalysisResult) -> str:
        """生成返回值验证测试"""
        return f"""
def test_{analysis.method_name}_return_validation():
    # 返回值验证测试
    # TODO: 实现返回值验证逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_boundary_test_case(self, analysis: AnalysisResult) -> str:
        """生成边界测试用例"""
        return f"""
def test_{analysis.method_name}_boundary():
    # 边界条件测试
    # TODO: 实现边界条件测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_extreme_values_test(self, analysis: AnalysisResult) -> str:
        """生成极值测试"""
        return f"""
def test_{analysis.method_name}_extreme_values():
    # 极值测试
    # TODO: 实现极值测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_null_values_test(self, analysis: AnalysisResult) -> str:
        """生成空值测试"""
        return f"""
def test_{analysis.method_name}_null_values():
    # 空值测试
    # TODO: 实现空值测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_exception_test_case(self, analysis: AnalysisResult) -> str:
        """生成异常测试用例"""
        return f"""
def test_{analysis.method_name}_exceptions():
    # 异常处理测试
    # TODO: 实现异常处理测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_error_propagation_test(self, analysis: AnalysisResult) -> str:
        """生成错误传播测试"""
        return f"""
def test_{analysis.method_name}_error_propagation():
    # 错误传播测试
    # TODO: 实现错误传播测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_resource_cleanup_test(self, analysis: AnalysisResult) -> str:
        """生成资源清理测试"""
        return f"""
def test_{analysis.method_name}_resource_cleanup():
    # 资源清理测试
    # TODO: 实现资源清理测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_input_validation_test(self, analysis: AnalysisResult) -> str:
        """生成输入验证测试"""
        return f"""
def test_{analysis.method_name}_input_validation():
    # 输入验证测试
    # TODO: 实现输入验证测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_type_validation_test(self, analysis: AnalysisResult) -> str:
        """生成类型验证测试"""
        return f"""
def test_{analysis.method_name}_type_validation():
    # 类型验证测试
    # TODO: 实现类型验证测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_format_validation_test(self, analysis: AnalysisResult) -> str:
        """生成格式验证测试"""
        return f"""
def test_{analysis.method_name}_format_validation():
    # 格式验证测试
    # TODO: 实现格式验证测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_sql_injection_test(self, analysis: AnalysisResult) -> str:
        """生成SQL注入测试"""
        return f"""
def test_{analysis.method_name}_sql_injection():
    # SQL注入防护测试
    # TODO: 实现SQL注入防护测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_xss_test(self, analysis: AnalysisResult) -> str:
        """生成XSS测试"""
        return f"""
def test_{analysis.method_name}_xss_protection():
    # XSS防护测试
    # TODO: 实现XSS防护测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_csrf_test(self, analysis: AnalysisResult) -> str:
        """生成CSRF测试"""
        return f"""
def test_{analysis.method_name}_csrf_protection():
    # CSRF防护测试
    # TODO: 实现CSRF防护测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_authorization_test(self, analysis: AnalysisResult) -> str:
        """生成权限验证测试"""
        return f"""
def test_{analysis.method_name}_authorization():
    # 权限验证测试
    # TODO: 实现权限验证测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_performance_test(self, analysis: AnalysisResult) -> str:
        """生成性能测试"""
        return f"""
def test_{analysis.method_name}_performance():
    # 性能基准测试
    # TODO: 实现性能基准测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_memory_usage_test(self, analysis: AnalysisResult) -> str:
        """生成内存使用测试"""
        return f"""
def test_{analysis.method_name}_memory_usage():
    # 内存使用测试
    # TODO: 实现内存使用测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_concurrency_test(self, analysis: AnalysisResult) -> str:
        """生成并发测试"""
        return f"""
def test_{analysis.method_name}_concurrency():
    # 并发测试
    # TODO: 实现并发测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_timeout_test(self, analysis: AnalysisResult) -> str:
        """生成超时测试"""
        return f"""
def test_{analysis.method_name}_timeout():
    # 超时测试
    # TODO: 实现超时测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_recursive_test(self, method_name: str) -> str:
        """生成递归测试"""
        return f"""
def test_{method_name}_recursive():
    # 递归函数测试
    # TODO: 实现递归测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_callback_test(self, method_name: str) -> str:
        """生成回调测试"""
        return f"""
def test_{method_name}_callback():
    # 回调函数测试
    # TODO: 实现回调测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_async_test(self, method_name: str) -> str:
        """生成异步测试"""
        return f"""
def test_{method_name}_async():
    # 异步函数测试
    # TODO: 实现异步测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_state_management_test(self, method_name: str) -> str:
        """生成状态管理测试"""
        return f"""
def test_{method_name}_state_management():
    # 状态管理测试
    # TODO: 实现状态管理测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    def _generate_transaction_test(self, method_name: str) -> str:
        """生成事务测试"""
        return f"""
def test_{method_name}_transaction():
    # 事务测试
    # TODO: 实现事务测试逻辑
    assert True  # 占位符，需要实现具体测试
"""

    # Pattern detection methods
    def _is_recursive_function(self, method_name: str) -> bool:
        """检查是否为递归函数"""
        # 简化的递归检测逻辑
        recursive_patterns = [
            "recursive",
            "fibonacci",
            "factorial",
            "tree_",
            "traverse",
        ]
        return any(pattern in method_name.lower() for pattern in recursive_patterns)

    def _has_callback_function(self, method_name: str) -> bool:
        """检查是否包含回调函数"""
        callback_patterns = ["callback", "handler", "listener", "observer"]
        return any(pattern in method_name.lower() for pattern in callback_patterns)

    def _is_async_function(self, method_name: str) -> bool:
        """检查是否为异步函数"""
        return method_name.startswith("async_") or "async" in method_name.lower()

    def _has_state_management(self, method_name: str) -> bool:
        """检查是否包含状态管理"""
        state_patterns = ["state", "cache", "session", "context", "manager"]
        return any(pattern in method_name.lower() for pattern in state_patterns)

    def _has_transaction_logic(self, method_name: str) -> bool:
        """检查是否包含事务逻辑"""
        transaction_patterns = ["transaction", "commit", "rollback", "save", "update"]
        return any(pattern in method_name.lower() for pattern in transaction_patterns)

    async def _optimize_test_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """优化测试用例"""
        optimized = []

        for test_case in test_cases:
            # 估算执行时间
            test_case.execution_time_estimate = self._estimate_execution_time(test_case)

            # 计算不稳定分数
            test_case.flakiness_score = self._calculate_flakiness_score(test_case)

            # 根据优先级和复杂度过滤
            if test_case.priority != TestPriority.LOW or test_case.complexity_score < 2.0:
                optimized.append(test_case)

        # 去重
        unique_cases = {}
        for case in optimized:
            case_hash = self._generate_test_hash(case)
            if case_hash not in unique_cases:
                unique_cases[case_hash] = case

        return list(unique_cases.values())

    def _generate_test_hash(self, test_case: TestCase) -> str:
        """生成测试用例哈希"""
        content = f"{test_case.name}{test_case.description}{test_case.code}"
        return hashlib.md5(content.encode()).hexdigest()

    def _estimate_execution_time(self, test_case: TestCase) -> float:
        """估算测试执行时间"""
        # 基于测试类型和复杂度估算
        base_time = 0.1  # 基础时间

        if test_case.category == TestCategory.PERFORMANCE:
            base_time = 1.0
        elif test_case.category == TestCategory.INTEGRATION:
            base_time = 0.5
        elif test_case.category == TestCategory.SECURITY:
            base_time = 0.3

        # 复杂度调整
        complexity_factor = test_case.complexity_score * 0.1

        return base_time + complexity_factor

    def _calculate_flakiness_score(self, test_case: TestCase) -> float:
        """计算测试不稳定分数"""
        # 基于各种因素计算
        factors = []

        # 网络相关测试
        if "api" in test_case.name.lower() or "http" in test_case.name.lower():
            factors.append(0.3)

        # 异步测试
        if "async" in test_case.code.lower():
            factors.append(0.2)

        # 时间相关测试
        if "time" in test_case.name.lower() or "date" in test_case.name.lower():
            factors.append(0.2)

        # 外部依赖
        if "requests" in test_case.code.lower() or "fetch" in test_case.code.lower():
            factors.append(0.3)

        return min(sum(factors), 1.0)

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度

        # 计算条件语句
        for child in ast.walk(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.ExceptHandler,
                    ast.With,
                    ast.AsyncWith,
                ),
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _get_annotation_type(self, annotation: Optional[ast.AST]) -> str:
        """获取参数类型注解"""
        if annotation is None:
            return "Any"

        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            return f"{annotation.value.id}[...]"
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        else:
            return "Unknown"

    def _generate_test_cases_for_method(
        self, method_name: str, method_node: ast.FunctionDef, analysis: Dict[str, Any]
    ) -> List[TestCase]:
        """为方法生成测试用例"""
        test_cases = []

        # 1. 正常情况测试用例
        normal_case = self._create_normal_case(method_name, analysis)
        test_cases.append(normal_case)

        # 2. 边界条件测试用例
        boundary_cases = self._create_boundary_cases(method_name, analysis)
        test_cases.extend(boundary_cases)

        # 3. 异常情况测试用例
        exception_cases = self._create_exception_cases(method_name, analysis)
        test_cases.extend(exception_cases)

        # 4. 参数验证测试用例
        validation_cases = self._create_validation_cases(method_name, analysis)
        test_cases.extend(validation_cases)

        return test_cases

    def _create_normal_case(self, method_name: str, analysis: Dict[str, Any]) -> TestCase:
        """创建正常情况测试用例"""
        test_code = f"""
def test_{method_name}_normal_case():
    # 正常情况测试
    args = self._generate_normal_args({analysis["arguments"]})
    result = {method_name}(*args)
    assert result is not None
    assert isinstance(result, {self._get_expected_return_type(analysis)})
"""

        return TestCase(
            name=f"test_{method_name}_normal_case",
            description="验证方法在正常输入下的行为",
            code=test_code.strip(),
            method_name=method_name,
            coverage=["normal_input"],
            complexity_score=1.0,
            created_at=datetime.now(),
            metadata={"test_type": "normal", "priority": "high"},
        )

    def _create_boundary_cases(self, method_name: str, analysis: Dict[str, Any]) -> List[TestCase]:
        """创建边界条件测试用例"""
        cases = []

        # 空值边界测试
        boundary_code = f"""
def test_{method_name}_boundary_cases():
    # 边界条件测试
    # 1. 空值测试
    with pytest.raises(ValueError):
        {method_name}(None, None)

    # 2. 空字符串测试
    empty_args = [""] * len({analysis["arguments"]})
    result = {method_name}(*empty_args)
    assert result is not None
"""

        cases.append(
            TestCase(
                name=f"test_{method_name}_boundary_cases",
                description="验证方法在边界条件下的行为",
                code=boundary_code.strip(),
                method_name=method_name,
                coverage=["boundary_conditions"],
                complexity_score=1.2,
                created_at=datetime.now(),
                metadata={"test_type": "boundary", "priority": "medium"},
            )
        )

        return cases

    def _create_exception_cases(self, method_name: str, analysis: Dict[str, Any]) -> List[TestCase]:
        """创建异常情况测试用例"""
        exception_code = f"""
def test_{method_name}_exception_cases():
    # 异常情况测试
    # 1. 无效参数类型
    invalid_args = ["invalid"] * len({analysis["arguments"]})
    with pytest.raises(TypeError):
        {method_name}(*invalid_args)

    # 2. 超出范围参数
    out_of_range_args = [999999] * len({analysis["arguments"]})
    result = {method_name}(*out_of_range_args)
    # 验证异常处理或默认返回值
"""

        return [
            TestCase(
                name=f"test_{method_name}_exception_cases",
                description="验证方法在异常输入下的行为",
                code=exception_code.strip(),
                method_name=method_name,
                coverage=["exception_handling"],
                complexity_score=1.5,
                created_at=datetime.now(),
                metadata={"test_type": "exception", "priority": "medium"},
            )
        ]

    def _create_validation_cases(self, method_name: str, analysis: Dict[str, Any]) -> List[TestCase]:
        """创建参数验证测试用例"""
        validation_code = f"""
def test_{method_name}_parameter_validation():
    # 参数验证测试
    # 1. 参数类型验证
    for param in {analysis["parameters"]}:
        invalid_value = self._generate_invalid_value(param['type'])
        with pytest.raises((TypeError, ValueError)):
            {method_name}({invalid_value})

    # 2. 参数范围验证
    if any(param['type'] in ['int', 'float'] for param in {analysis["parameters"]}):
        negative_args = [-1] * len({analysis["arguments"]})
        result = {method_name}(*negative_args)
        # 验证负数处理
"""

        return [
            TestCase(
                name=f"test_{method_name}_parameter_validation",
                description="验证方法参数验证逻辑",
                code=validation_code.strip(),
                method_name=method_name,
                coverage=["parameter_validation"],
                complexity_score=1.3,
                created_at=datetime.now(),
                metadata={"test_type": "validation", "priority": "low"},
            )
        ]

    def _get_expected_return_type(self, analysis: Dict[str, Any]) -> str:
        """获取预期返回类型"""
        # 基于方法名称和参数推断返回类型
        if "get" in analysis.get("method_name", ""):
            return "dict"
        elif "is" in analysis.get("method_name", ""):
            return "bool"
        elif "calculate" in analysis.get("method_name", ""):
            return "float"
        else:
            return "Any"

    async def optimize_test_suite(self, test_files: List[str]) -> Dict[str, Any]:
        """优化测试套件"""
        print("🤖 AI正在优化测试套件...")

        optimization_results = {}

        for test_file in test_files:
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    source_code = f.read()

                # 分析现有测试
                analysis = self._analyze_test_file(source_code, test_file)

                # 生成优化建议
                suggestions = await self._generate_optimization_suggestions(analysis)

                optimization_results[test_file] = {
                    "analysis": analysis,
                    "suggestions": suggestions,
                    "improvement_score": self._calculate_improvement_score(suggestions),
                }

            except Exception as e:
                print(f"❌ 测试文件 {test_file} 分析失败: {str(e)}")
                optimization_results[test_file] = {"error": str(e)}

        return optimization_results

    def _analyze_test_file(self, source_code: str, file_path: str) -> Dict[str, Any]:
        """分析测试文件"""
        try:
            tree = ast.parse(source_code)

            test_methods = []
            total_lines = len(source_code.split("\n"))

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_methods.append(
                        {
                            "name": node.name,
                            "lines": node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
                            "complexity": self._calculate_complexity(node),
                        }
                    )

            return {
                "file_path": file_path,
                "total_lines": total_lines,
                "test_count": len(test_methods),
                "test_methods": test_methods,
                "avg_complexity": sum(m["complexity"] for m in test_methods) / len(test_methods) if test_methods else 0,
                "max_complexity": max(m["complexity"] for m in test_methods) if test_methods else 0,
            }

        except Exception as e:
            return {"error": str(e)}

    async def _generate_optimization_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if "avg_complexity" in analysis and analysis["avg_complexity"] > 10:
            suggestions.append("测试方法复杂度过高，建议拆分为多个简单的测试")

        if "max_complexity" in analysis and analysis["max_complexity"] > 20:
            suggestions.append("存在非常复杂的测试方法，考虑使用参数化测试或重构")

        if "test_count" in analysis and analysis["test_count"] < 5:
            suggestions.append("测试覆盖率较低，建议增加更多测试用例")

        # 添加AI优化建议
        if analysis.get("test_count", 0) > 0:
            suggestions.extend(
                [
                    "建议添加数据驱动测试以提高覆盖率",
                    "考虑使用pytest.mark.parametrize进行参数化测试",
                    "建议添加性能基准测试",
                    "考虑添加契约测试验证API规范",
                ]
            )

        return suggestions

    def _calculate_improvement_score(self, suggestions: List[str]) -> float:
        """计算改进分数"""
        base_score = 0
        for suggestion in suggestions:
            if "复杂度" in suggestion:
                base_score += 30
            elif "覆盖率" in suggestion:
                base_score += 25
            elif "参数化" in suggestion:
                base_score += 20
            elif "性能" in suggestion:
                base_score += 15
            else:
                base_score += 10

        return min(base_score, 100) / 100.0


class IntelligentTestOptimizer:
    """智能测试优化器"""

    def __init__(self):
        self.ai_generator = AITestGenerator()

    async def optimize_test_coverage(self, module_path: str) -> Dict[str, Any]:
        """优化测试覆盖率"""
        print(f"🤖 AI正在优化 {module_path} 的测试覆盖率...")

        # 分析源代码
        source_code = self._read_module_source(module_path)

        # 提取所有可测试方法
        testable_methods = self._extract_testable_methods(source_code)

        # 生成缺失的测试用例
        generated_tests = []
        for method in testable_methods:
            if not self._has_test_case(method["name"], module_path):
                test_cases = self.ai_generator.generate_test_cases_from_source(source_code, method["name"])
                generated_tests.extend(test_cases)

        # 生成优化报告
        report = {
            "module_path": module_path,
            "total_methods": len(testable_methods),
            "tested_methods": len([m for m in testable_methods if self._has_test_case(m["name"], module_path)]),
            "coverage_percentage": self._calculate_coverage(testable_methods, module_path),
            "generated_tests": len(generated_tests),
            "suggestions": self._generate_coverage_suggestions(testable_methods, module_path),
        }

        return report

    def _read_module_source(self, module_path: str) -> str:
        """读取模块源代码"""
        try:
            with open(module_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ 无法读取模块文件 {module_path}: {str(e)}")
            return ""

    def _extract_testable_methods(self, source_code: str) -> List[Dict[str, Any]]:
        """提取可测试方法"""
        try:
            tree = ast.parse(source_code)
            methods = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 跳过测试方法和私有方法
                    if not node.name.startswith("_") and not node.name.startswith("test_"):
                        methods.append(
                            {
                                "name": node.name,
                                "line": node.lineno,
                                "complexity": self.ai_generator._calculate_complexity(node),
                                "args": [arg.arg for arg in node.args.args],
                                "has_return": len(node.body) > 0 and isinstance(node.body[-1], ast.Return),
                            }
                        )

            return methods

        except Exception as e:
            print(f"❌ 源代码解析失败: {str(e)}")
            return []

    def _has_test_case(self, method_name: str, module_path: str) -> bool:
        """检查是否已有测试用例"""
        test_file = module_path.replace(".py", "_test.py")
        test_dir = module_path.replace(".py", "/tests/test_")

        test_paths = [test_file, test_dir]

        for path in test_paths:
            if Path(path).exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if f"test_{method_name}" in content:
                            return True
                except Exception:
                    pass

        return False

    def _calculate_coverage(self, methods: List[Dict[str, Any]], module_path: str) -> float:
        """计算测试覆盖率"""
        tested_count = len([m for m in methods if self._has_test_case(m["name"], module_path)])
        total_count = len(methods)
        return (tested_count / total_count * 100) if total_count > 0 else 0

    def _generate_coverage_suggestions(self, methods: List[Dict[str, Any]], module_path: str) -> List[str]:
        """生成覆盖率优化建议"""
        suggestions = []

        # 分析未测试的方法
        untested_methods = [m for m in methods if not self._has_test_case(m["name"], module_path)]

        if len(untested_methods) > 0:
            # 按复杂度排序
            untested_methods.sort(key=lambda x: x["complexity"], reverse=True)

            # 为高复杂度方法生成优先级建议
            high_complexity_untested = [m for m in untested_methods if m["complexity"] > 10]
            if high_complexity_untested:
                suggestions.append(f"优先测试高复杂度方法: {[m['name'] for m in high_complexity_untested[:3]]}")

            # 测试覆盖率低的建议
            coverage = self._calculate_coverage(methods, module_path)
            if coverage < 50:
                suggestions.append("当前测试覆盖率低于50%，建议增加基础功能测试")

            # 业务关键功能建议
            critical_methods = [
                m for m in untested_methods if "get" in m["name"].lower() or "calculate" in m["name"].lower()
            ]
            if critical_methods:
                suggestions.append(f"建议为业务核心方法添加测试: {[m['name'] for m in critical_methods[:3]]}")

        return suggestions


# AI辅助测试工具
class AITestAssistant:
    """AI测试助手"""

    def __init__(self):
        self.generator = AITestGenerator()
        self.optimizer = IntelligentTestOptimizer()

    async def generate_comprehensive_test_suite(self, target_module: str) -> Dict[str, Any]:
        """生成全面的测试套件"""
        print(f"🤖 AI正在为 {target_module} 生成全面测试套件...")

        # 分析目标模块
        source_code = self.generator._read_module_source(target_module)
        methods = self.generator._extract_testable_methods(source_code)

        comprehensive_tests = []

        # 为每个方法生成测试用例
        for method in methods:
            test_cases = self.generator.generate_test_cases_from_source(source_code, method["name"])
            comprehensive_tests.extend(test_cases)

        # 生成测试套件文件
        test_suite_file = self._generate_test_suite_file(target_module, comprehensive_tests)

        return {
            "target_module": target_module,
            "generated_tests": len(comprehensive_tests),
            "test_file": test_suite_file,
            "coverage_analysis": await self.optimizer.optimize_test_coverage(target_module),
            "ai_recommendations": self._generate_ai_recommendations(methods, comprehensive_tests),
        }

    def _generate_test_suite_file(self, target_module: str, test_cases: List[TestCase]) -> str:
        """生成测试套件文件"""
        module_name = Path(target_module).stem
        test_file = f"tests/{module_name}_comprehensive_test.py"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(
                f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{module_name} 综合测试套件
AI生成的全面测试用例
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
\"\"\"

import pytest
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import specific functions from the target module
try:
    from {module_name} import calculate_profit_loss, get_stock_price
except ImportError:
    # Fallback imports if the specific functions don't exist
    try:
        import {module_name}
    except ImportError:
        pass

"""
            )

            for test_case in test_cases:
                f.write(
                    f"""
{test_case.code}

"""
                )

                # 添加辅助方法
                if "test_type" in test_case.metadata and test_case.metadata["test_type"] == "boundary":
                    f.write(
                        """
    def _generate_normal_args(self, args):
        \"\"\"生成正常参数值\"\"\"
        return ["normal_value"] * len(args)

    def _generate_invalid_value(self, param_type):
        \"\"\"生成无效参数值\"\"\"
        invalid_values = {
            "str": 123,
            "int": "invalid",
            "float": "not_float",
            "bool": "not_bool"
        }
        return invalid_values.get(param_type, None)

"""
                    )

                f.write("\n")

        return test_file

    def _generate_ai_recommendations(self, methods: List[Dict[str, Any]], test_cases: List[TestCase]) -> List[str]:
        """生成AI建议"""
        recommendations = []

        # 复杂度分析建议
        high_complexity = [m for m in methods if m["complexity"] > 10]
        if high_complexity:
            recommendations.append(f"检测到 {len(high_complexity)} 个高复杂度方法，建议重构或拆分")

        # 覆盖率建议
        covered_methods = len([tc for tc in test_cases if tc.complexity_score < 1.5])
        total_generated = len(test_cases)
        if total_generated > 0:
            coverage_ratio = covered_methods / total_generated
            if coverage_ratio < 0.8:
                recommendations.append(f"建议增加边界和异常测试用例，当前基础用例占比: {coverage_ratio:.1%}")

        # 性能建议
        if len(test_cases) > 20:
            recommendations.append("测试用例数量较多，建议考虑使用测试分组或并行执行")

        # 维护性建议
        avg_test_complexity = sum(tc.complexity_score for tc in test_cases) / len(test_cases)
        if avg_test_complexity > 1.3:
            recommendations.append("测试用例复杂度较高，建议保持测试简单明了")

        return recommendations


# Pytest测试用例
@pytest.mark.ai_assisted
async def test_ai_test_generation():
    """AI测试生成测试"""
    ai_assistant = AITestAssistant()

    # 生成测试用例
    test_cases = ai_assistant.generator.generate_test_cases_from_source(
        """
def calculate_profit_loss(symbol, start_date, end_date):
    \"\"\"计算盈亏\"\"\"
    if not symbol or not start_date or not end_date:
        raise ValueError("参数不能为空")

    # 获取历史数据
    data = fetch_kline_data(symbol, start_date, end_date)

    # 计算盈亏
    profit_loss = 0.0
    for i in range(1, len(data)):
        change = data[i]['close'] - data[i-1]['close']
        profit_loss += change

    return round(profit_loss, 2)
        """,
        "calculate_profit_loss",
    )

    assert len(test_cases) >= 4  # 应该生成至少4个测试用例
    assert any("normal_case" in tc.name for tc in test_cases)
    assert any("boundary_cases" in tc.name for tc in test_cases)
    assert any("exception_cases" in tc.name for tc in test_cases)


@pytest.mark.ai_assisted
async def test_test_suite_optimization():
    """测试套件优化测试"""
    ai_assistant = AITestAssistant()

    # 优化测试套件
    test_files = ["src/adapters/financial_adapter.py", "src/data_access.py"]

    optimization_results = await ai_assistant.optimizer.optimize_test_suite(test_files)

    assert len(optimization_results) >= 1
    assert all("analysis" in result for result in optimization_results.values())


@pytest.mark.ai_assisted
async def test_comprehensive_test_generation():
    """全面测试套件生成测试"""
    ai_assistant = AITestAssistant()

    # 为financial_adapter生成综合测试套件
    result = await ai_assistant.generate_comprehensive_test_suite("src/adapters/financial_adapter.py")

    assert "target_module" in result
    assert "generated_tests" in result
    assert result["generated_tests"] > 0
    assert "coverage_analysis" in result
    assert "ai_recommendations" in result


if __name__ == "__main__":
    # 运行AI辅助测试
    import asyncio

    async def main():
        print("🤖 启动AI辅助测试工具...")

        # 测试用例生成
        ai_assistant = AITestAssistant()

        # 生成示例测试用例
        test_cases = ai_assistant.generator.generate_test_cases_from_source(
            """
def get_stock_price(symbol):
    \"\"\"获取股票价格\"\"\"
    if symbol == "600519":
        return {"symbol": "600519", "price": 1800.0, "change": 2.5}
    elif symbol == "600036":
        return {"symbol": "600036", "price": 45.6, "change": -1.2}
    else:
        return None
            """,
            "get_stock_price",
        )

        print(f"✅ 生成了 {len(test_cases)} 个测试用例")

        # 生成综合测试套件
        result = await ai_assistant.generate_comprehensive_test_suite("src/adapters/financial_adapter.py")

        print("📊 测试套件生成结果:")
        print(f"  - 目标模块: {result['target_module']}")
        print(f"  - 生成的测试用例数: {result['generated_tests']}")
        print(f"  - 覆盖率分析: {result['coverage_analysis']['coverage_percentage']:.1f}%")
        print(f"  - 测试文件: {result['test_file']}")
        print(f"  - AI建议: {len(result['ai_recommendations'])} 条")

        for rec in result["ai_recommendations"]:
            print(f"    • {rec}")

    asyncio.run(main())
