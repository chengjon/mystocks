#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Support mixin extracted from `part1.py`."""

from __future__ import annotations


class AITestGeneratorCoreTailMixin:
    """AITestGenerator Core 尾部方法集。"""

    async def _create_security_test_cases(
        self,
        method_name: str,
        analysis: AnalysisResult,
        category: TestCategory,
        priority: TestPriority,
    ) -> List[TestCase]:
        """创建安全测试用例"""
        test_cases = []

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
