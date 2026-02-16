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


