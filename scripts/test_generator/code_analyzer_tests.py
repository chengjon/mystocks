#!/usr/bin/env python3
"""
增强版AI测试生成器
提供更智能的测试算法、模式识别和优化建议

核心功能:
1. 智能代码分析 - 基于AST的深度代码理解
2. 模式识别测试 - 识别代码模式并生成针对性测试
3. 缺陷预测 - 预测潜在bug并生成防护性测试
4. 性能优化建议 - 基于代码复杂度的性能优化建议
5. 测试质量评估 - 评估生成测试的有效性和完整性

作者: MyStocks AI Team
版本: 3.0 (算法增强版)
日期: 2025-12-22
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass

class _TestGenerationMixin:
    """EnhancedCodeAnalyzer 测试生成方法集"""


    def _generate_database_tests(
        self, pattern: CodePattern, source_file: str
    ) -> List[TestCase]:
        """生成数据库操作测试"""
        tests = []
        module_name = Path(source_file).stem

        for start_line, end_line in pattern.locations:
            test_name = f"test_{module_name}_database_operations_{start_line}"
            test_code = f'''
    def {test_name}(self):
        """测试数据库操作 - 行{start_line}-{end_line}"""
        from unittest.mock import Mock, patch

        # Mock数据库连接
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # 模拟查询结果
            mock_cursor.fetchall.return_value = [(1, 'test'), (2, 'test2')]

            # 正常查询测试
            result = {module_name}.{self._extract_function_name(source_file, start_line)}()
            self.assertIsNotNone(result)

            # 验证SQL执行
            mock_cursor.execute.assert_called()

            # 数据库连接错误测试
            mock_connect.side_effect = sqlite3.Error("Connection failed")
            with self.assertRaises(sqlite3.Error):
                {module_name}.{self._extract_function_name(source_file, start_line)}()

            # SQL注入防护测试
            malicious_input = "'; DROP TABLE users; --"
            with patch.object(mock_cursor, 'execute') as mock_execute:
                try:
                    {module_name}.{self._extract_function_name(source_file, start_line)}(malicious_input)
                except:
                    pass

                # 验证使用了参数化查询
                call_args = mock_execute.call_args
                if call_args:
                    sql_query = call_args[0][0] if call_args[0] else ""
                    self.assertNotIn("';", sql_query, "检测到潜在的SQL注入风险")
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=f"测试第{start_line}-{end_line}行的数据库操作逻辑",
                    test_code=test_code.strip(),
                    priority="high",
                    coverage_target=[f"lines:{start_line}-{end_line}"],
                    test_type="integration",
                    estimated_time=4.0,
                )
            )

        return tests

    def _generate_network_tests(
        self, pattern: CodePattern, source_file: str
    ) -> List[TestCase]:
        """生成网络操作测试"""
        tests = []
        module_name = Path(source_file).stem

        for start_line, end_line in pattern.locations:
            test_name = f"test_{module_name}_network_operations_{start_line}"
            test_code = f'''
    def {test_name}(self):
        """测试网络操作 - 行{start_line}-{end_line}"""
        from unittest.mock import Mock, patch
        import requests

        # Mock网络请求
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {{"status": "success", "data": "test"}}
            mock_get.return_value = mock_response

            # 正常网络请求测试
            result = {module_name}.{self._extract_function_name(source_file, start_line)}()
            self.assertIsNotNone(result)

            # 网络超时测试
            mock_get.side_effect = requests.Timeout("Connection timeout")
            with self.assertRaises(requests.Timeout):
                {module_name}.{self._extract_function_name(source_file, start_line)}()

            # 网络连接错误测试
            mock_get.side_effect = requests.ConnectionError("Connection failed")
            with self.assertRaises(requests.ConnectionError):
                {module_name}.{self._extract_function_name(source_file, start_line)}()

            # HTTP错误状态测试
            mock_response.status_code = 404
            mock_get.side_effect = None
            mock_get.return_value = mock_response

            with self.assertRaises(requests.HTTPError):
                {module_name}.{self._extract_function_name(source_file, start_line)}()
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=f"测试第{start_line}-{end_line}行的网络操作逻辑",
                    test_code=test_code.strip(),
                    priority="medium",
                    coverage_target=[f"lines:{start_line}-{end_line}"],
                    test_type="integration",
                    estimated_time=3.0,
                )
            )

        return tests

    def _generate_bug_prevention_test(self, bug: Dict, source_file: str) -> TestCase:
        """生成Bug防护测试"""
        module_name = Path(source_file).stem
        test_name = f"test_{module_name}_bug_prevention_{bug['type']}_{bug['line']}"

        test_code = f'''
    def {test_name}(self):
        """测试Bug防护 - {bug["description"]} (行{bug["line"]})"""
        # {bug["suggestion"]}

        # 测试防护措施
        test_cases = self._get_bug_prevention_test_cases('{bug["type"]}')

        for test_case in test_cases:
            input_data, expected_behavior = test_case

            try:
                result = {module_name}.{self._extract_function_name(source_file, bug["line"])}(input_data)

                # 验证预期行为
                if expected_behavior['should_raise_exception']:
                    self.fail(f"期望抛出异常但没有抛出: {{input_data}}")
                else:
                    self.assertIsNotNone(result, f"期望正常返回但返回None: {{input_data}}")

            except Exception as e:
                if not expected_behavior['should_raise_exception']:
                    self.fail(f"意外异常: {{e}}, 输入: {{input_data}}")
                else:
                    # 验证异常类型
                    self.assertIn(type(e).__name__, expected_behavior['expected_exceptions'],
                                 f"异常类型不匹配: {{type(e).__name__}}")
'''

        return TestCase(
            name=test_name,
            description=f"测试Bug防护: {bug['description']}",
            test_code=test_code.strip(),
            priority="high",
            coverage_target=[f"line:{bug['line']}"],
            test_type="security",
            estimated_time=2.0,
        )

    def _generate_performance_tests(
        self, patterns: List[CodePattern], source_file: str
    ) -> List[TestCase]:
        """生成性能测试"""
        tests = []
        module_name = Path(source_file).stem

        # 识别性能瓶颈
        performance_patterns = [p for p in patterns if p.complexity_score > 5.0]

        for pattern in performance_patterns[:3]:  # 限制最多3个性能测试
            test_name = f"test_{module_name}_performance_{pattern.pattern_type}"
            test_code = f'''
    def {test_name}(self):
        """测试{pattern.pattern_type}性能 - 复杂度: {pattern.complexity_score:.1f}"""
        import time

        # 小数据集性能基准
        small_data = self._get_performance_test_data('small')
        start_time = time.time()
        result_small = {module_name}.{self._extract_function_name(source_file, pattern.locations[0][0])}(small_data)
        small_time = time.time() - start_time

        # 中等数据集性能测试
        medium_data = self._get_performance_test_data('medium')
        start_time = time.time()
        result_medium = {module_name}.{self._extract_function_name(source_file, pattern.locations[0][0])}(medium_data)
        medium_time = time.time() - start_time

        # 性能断言
        self.assertLess(small_time, 1.0, "小数据集处理时间过长")
        self.assertLess(medium_time, 5.0, "中等数据集处理时间过长")

        # 验证结果一致性
        self._validate_performance_results(result_small, result_medium)

        # 性能退化检测
        time_complexity_ratio = medium_time / max(small_time, 0.001)
        self.assertLess(time_complexity_ratio, 100, "检测到性能退化，可能的时间复杂度过高")
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=f"测试{pattern.pattern_type}性能，复杂度评分: {pattern.complexity_score:.1f}",
                    test_code=test_code.strip(),
                    priority="medium",
                    coverage_target=[
                        f"lines:{pattern.locations[0][0]}-{pattern.locations[0][1]}"
                    ],
                    test_type="performance",
                    estimated_time=8.0,
                )
            )

        return tests

    def _generate_boundary_tests(self, source_file: str) -> List[TestCase]:
        """生成边界测试"""
        tests = []
        module_name = Path(source_file).stem

        # 常见边界测试场景
        boundary_scenarios = [
            {"name": "empty_input", "description": "空输入测试"},
            {"name": "single_item", "description": "单项输入测试"},
            {"name": "maximum_size", "description": "最大尺寸测试"},
            {"name": "unicode_input", "description": "Unicode字符测试"},
            {"name": "special_characters", "description": "特殊字符测试"},
        ]

        for scenario in boundary_scenarios:
            test_name = f"test_{module_name}_boundary_{scenario['name']}"
            test_code = f'''
    def {test_name}(self):
        """{scenario["description"]}"""
        test_data = self._get_boundary_test_data('{scenario["name"]}')

        # 验证不会崩溃
        try:
            result = {module_name}.{self._extract_function_name(source_file, 1)}(test_data)
            # 验证结果有效性
            self.assertIsNotNone(result, "边界测试返回了None")

            # 验证结果类型
            expected_type = self._get_expected_result_type('{scenario["name"]}')
            if expected_type:
                self.assertIsInstance(result, expected_type,
                                    f"结果类型不匹配: 期望 {{expected_type}}, 实际 {{type(result)}}")

        except Exception as e:
            # 某些边界情况可能期望异常
            if self._should_raise_exception_for_boundary('{scenario["name"]}'):
                self.assertIsInstance(e, (ValueError, TypeError, IndexError),
                                      f"边界测试异常类型不匹配: {{type(e)}}")
            else:
                self.fail(f"边界测试意外失败: {{e}}, 测试数据: {{test_data}}")
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=scenario["description"],
                    test_code=test_code.strip(),
                    priority="low",
                    coverage_target=["boundary_conditions"],
                    test_type="unit",
                    estimated_time=1.5,
                )
            )

        return tests

    def _extract_function_name(self, source_file: str, line_num: int) -> str:
        """提取指定行的函数名"""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if 1 <= line_num <= len(lines):
                line = lines[line_num - 1].strip()

                # 查找函数定义
                func_match = re.search(r"def\s+(\w+)\s*\(", line)
                if func_match:
                    return func_match.group(1)

                # 查找类方法
                method_match = re.search(r"def\s+(\w+)\s*\(", line)
                if method_match:
                    return method_match.group(1)

                # 如果不是函数定义，尝试向上查找最近的函数
                for i in range(line_num - 2, max(0, line_num - 20), -1):
                    prev_line = lines[i].strip()
                    func_match = re.search(r"def\s+(\w+)\s*\(", prev_line)
                    if func_match:
                        return func_match.group(1)

            return "target_function"

        except Exception:
            return "target_function"

    def _get_test_priority_score(self, test_case: TestCase) -> float:
        """计算测试优先级评分"""
        priority_scores = {"high": 10.0, "medium": 6.0, "low": 3.0}

        test_type_scores = {
            "security": 9.0,
            "unit": 7.0,
            "integration": 6.0,
            "performance": 5.0,
        }

        base_score = priority_scores.get(test_case.priority, 5.0)
        type_modifier = test_type_scores.get(test_case.test_type, 5.0)

        # 复杂度调节
        complexity_modifier = min(test_case.estimated_time / 5.0, 2.0)

        return base_score + type_modifier + complexity_modifier

    def get_enhancement_suggestions(
        self, source_file: str, patterns: List[CodePattern], bugs: List[Dict]
    ) -> List[EnhancementSuggestion]:
        """获取增强建议"""
        suggestions = []

        # 基于模式分析的建议
        for pattern in patterns:
            if pattern.risk_level in ["high", "critical"]:
                suggestions.append(
                    EnhancementSuggestion(
                        category="security",
                        priority="high",
                        description=f"高风险{pattern.pattern_type}模式需要加强安全检查",
                        code_example=self._get_security_enhancement_example(pattern),
                        impact_assessment="降低安全风险，提高代码健壮性",
                    )
                )

        # 基于bug预测的建议
        critical_bugs = [b for b in bugs if b["risk_score"] > 0.8]
        if critical_bugs:
            suggestions.append(
                EnhancementSuggestion(
                    category="security",
                    priority="critical",
                    description=f"发现{len(critical_bugs)}个高风险bug模式，需要立即修复",
                    code_example=self._get_bug_fix_example(critical_bugs[0]),
                    impact_assessment="防止潜在的安全漏洞和系统崩溃",
                )
            )

        # 性能优化建议
        high_complexity_patterns = [p for p in patterns if p.complexity_score > 7.0]
        if high_complexity_patterns:
            suggestions.append(
                EnhancementSuggestion(
                    category="performance",
                    priority="medium",
                    description=f"{len(high_complexity_patterns)}个高复杂度模块需要性能优化",
                    code_example=self._get_performance_optimization_example(
                        high_complexity_patterns[0]
                    ),
                    impact_assessment="提升系统性能，降低资源消耗",
                )
            )

        # 可维护性建议
        if len(patterns) > 10:
            suggestions.append(
                EnhancementSuggestion(
                    category="maintainability",
                    priority="medium",
                    description="模块包含过多代码模式，建议拆分以提高可维护性",
                    code_example=self._get_refactoring_example(),
                    impact_assessment="提高代码可读性和维护效率",
                )
            )

        return suggestions
