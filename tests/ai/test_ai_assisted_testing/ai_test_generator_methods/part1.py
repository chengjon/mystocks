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


class AITestGeneratorCoreMixin:
    """AITestGenerator 方法集 Part 1"""

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

