#!/usr/bin/env python3
"""AI算法增强器
专注于智能测试生成和代码质量提升

核心功能:
1. 智能代码模式识别
2. Bug预测和防护测试生成
3. 性能瓶颈检测和优化建议
4. 自动化测试用例生成

作者: MyStocks AI Team
版本: 2.0 (算法增强版)
日期: 2025-12-22
"""

import logging
import re
import sys
from pathlib import Path
from typing import Dict, List


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from .dataclasses import CodeInsight, SmartTestCase


class _BugPredictionMixin:
    """Bug 预测与测试生成方法集"""

    def predict_bugs(self, source_file: str) -> List[Dict]:
        """预测潜在Bug"""
        logger.info(f"🐛 开始Bug预测: {source_file}")

        bugs = []

        try:
            with open(source_file, encoding="utf-8") as f:
                source_code = f.read()

            lines = source_code.split("\n")

            # 应用Bug模式检测
            for bug_type, bug_info in self.bug_patterns.items():
                for pattern in bug_info["patterns"]:
                    matches = list(re.finditer(pattern, source_code, re.MULTILINE))

                    for match in matches:
                        line_num = source_code[: match.start()].count("\n") + 1

                        # 检查上下文是否有防护措施
                        context_start = max(0, line_num - 5)
                        context_end = min(len(lines), line_num + 5)
                        context = "\n".join(lines[context_start:context_end])

                        has_protection = self._check_context_protection(context)

                        if not has_protection:
                            bugs.append(
                                {
                                    "type": bug_type,
                                    "line": line_num,
                                    "severity": bug_info["severity"],
                                    "description": self._get_bug_description(bug_type),
                                    "suggestion": self._get_bug_suggestion(bug_type),
                                },
                            )

            logger.info(f"✅ Bug预测完成，发现 {len(bugs)} 个潜在问题")
            return bugs

        except Exception as e:
            logger.error(f"Bug预测失败: {e}")
            return []

    def _check_context_protection(self, context: str) -> bool:
        """检查上下文是否有保护措施"""
        protection_patterns = [
            r"if.*is not None",
            r"if.*len\(",
            r"if.*in\s+",
            r"try\s*:",
            r"with\s+",
            r"assert\s+",
        ]

        for pattern in protection_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True

        return False

    def _get_bug_description(self, bug_type: str) -> str:
        """获取Bug描述"""
        descriptions = {
            "null_pointer_risk": "存在空指针解引用风险",
            "off_by_one_risk": "存在索引越界风险",
            "resource_leak_risk": "存在资源泄漏风险",
            "sql_injection_risk": "存在SQL注入风险",
        }
        return descriptions.get(bug_type, "未知类型风险")

    def _get_bug_suggestion(self, bug_type: str) -> str:
        """获取Bug修复建议"""
        suggestions = {
            "null_pointer_risk": "添加空值检查",
            "off_by_one_risk": "验证索引范围",
            "resource_leak_risk": "使用with语句或确保资源释放",
            "sql_injection_risk": "使用参数化查询",
        }
        return suggestions.get(bug_type, "请仔细检查代码逻辑")

    def generate_smart_tests(
        self,
        source_file: str,
        insights: List[CodeInsight],
        bugs: List[Dict],
    ) -> List[SmartTestCase]:
        """生成智能测试用例"""
        logger.info(f"🧪 开始生成智能测试: {source_file}")

        test_cases = []

        module_name = Path(source_file).stem

        # 为每个高优先级洞察生成测试
        high_priority_insights = [i for i in insights if i.test_priority in ["critical", "high"]]

        for insight in high_priority_insights:
            test_cases.extend(self._generate_tests_for_insight(insight, module_name))

        # 为每个Bug生成防护性测试
        for bug in bugs[:5]:  # 限制Bug测试数量
            test_cases.append(self._generate_bug_prevention_test(bug, module_name))

        # 生成通用测试
        test_cases.extend(self._generate_general_tests(module_name, insights))

        # 按优先级排序
        test_cases.sort(key=lambda t: t.priority_score, reverse=True)

        logger.info(f"✅ 测试生成完成，共生成 {len(test_cases)} 个测试用例")
        return test_cases[:15]  # 限制测试数量

    def _generate_tests_for_insight(
        self,
        insight: CodeInsight,
        module_name: str,
    ) -> List[SmartTestCase]:
        """为洞察生成测试"""
        tests = []

        # 基于风险等级生成不同类型的测试
        if insight.risk_level == "critical":
            tests.append(self._generate_security_test(insight, module_name))
            tests.append(self._generate_error_test(insight, module_name))

        if insight.risk_level in ["critical", "high"]:
            tests.append(self._generate_boundary_test(insight, module_name))

        # 基于复杂度生成测试
        if insight.complexity_score > self.complexity_thresholds["medium"]:
            tests.append(self._generate_performance_test(insight, module_name))

        # 基于潜在问题生成测试
        if "缺少错误处理" in insight.potential_issues:
            tests.append(self._generate_error_handling_test(insight, module_name))

        if "缺少输入验证" in insight.potential_issues:
            tests.append(self._generate_validation_test(insight, module_name))

        return tests

    def _generate_security_test(
        self,
        insight: CodeInsight,
        module_name: str,
    ) -> SmartTestCase:
        """生成安全测试"""
        test_name = f"test_{module_name}_{insight.function_name}_security"

        test_code = f'''
    def {test_name}(self):
        """安全测试 - {insight.function_name} (高风险函数)"""
        # 测试恶意输入
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "{{" * 10000,  # 模板注入
            "null",
            None,
        ]

        for malicious_input in malicious_inputs:
            with self.assertRaises((ValueError, SecurityError, TypeError)):
                result = {module_name}.{insight.function_name}(malicious_input)

        # 验证函数不会崩溃或泄露敏感信息
        try:
            result = {module_name}.{insight.function_name}("safe_input")
            self.assertIsNotNone(result)
        except Exception as e:
            # 确保异常不包含敏感信息
            self.assertNotIn("password", str(e).lower())
            self.assertNotIn("secret", str(e).lower())
'''

        return SmartTestCase(
            name=test_name,
            description=f"安全测试: {insight.function_name}",
            test_code=test_code.strip(),
            coverage_targets=[insight.function_name],
            test_type="security",
            priority_score=15.0,
        )

    def _generate_error_test(
        self,
        insight: CodeInsight,
        module_name: str,
    ) -> SmartTestCase:
        """生成错误测试"""
        test_name = f"test_{module_name}_{insight.function_name}_errors"

        test_code = f'''
    def {test_name}(self):
        """错误处理测试 - {insight.function_name}"""
        # 测试各种异常情况
        error_scenarios = [
            ("空输入", None),
            ("空字符串", ""),
            ("错误类型", 12345 if str in dir({module_name}) else object()),
            ("超大输入", "x" * 1000000),
        ]

        for scenario_name, test_input in error_scenarios:
            with self.subTest(scenario=scenario_name):
                try:
                    result = {module_name}.{insight.function_name}(test_input)
                    # 如果没有异常，验证结果合理性
                    self.assertIsNotNone(result)
                except (ValueError, TypeError, IndexError, KeyError):
                    # 期望的异常，测试通过
                    pass
                except Exception as e:
                    # 意外异常，应该被正确处理
                    self.fail(f"未处理的异常类型: {{type(e).__name__}}, 信息: {{e}}")
'''

        return SmartTestCase(
            name=test_name,
            description=f"错误处理测试: {insight.function_name}",
            test_code=test_code.strip(),
            coverage_targets=[insight.function_name],
            test_type="unit",
            priority_score=12.0,
        )

    def _generate_boundary_test(
        self,
        insight: CodeInsight,
        module_name: str,
    ) -> SmartTestCase:
        """生成边界测试"""
        test_name = f"test_{module_name}_{insight.function_name}_boundary"

        test_code = f'''
    def {test_name}(self):
        """边界测试 - {insight.function_name}"""
        # 测试边界值
        boundary_test_cases = [
            # 最小值
            ("最小正整数", 1),
            ("零值", 0),
            ("最小负整数", -1),

            # 边界字符串
            ("空字符串", ""),
            ("单字符", "a"),
            ("最大长度字符串", "x" * 255),

            # 边界集合
            ("空列表", []),
            ("单元素列表", [1]),
            ("最大大小列表", list(range(1000))),
        ]

        for test_name, test_input in boundary_test_cases:
            with self.subTest(test_case=test_name):
                try:
                    result = {module_name}.{insight.function_name}(test_input)
                    # 验证边界情况下的行为
                    self.assertIsNotNone(result)
                except (ValueError, IndexError):
                    # 边界值可能导致的预期异常
                    pass
                except Exception as e:
                    self.fail(f"边界测试失败: {{type(e).__name__}} - {{e}}")
'''

        return SmartTestCase(
            name=test_name,
            description=f"边界测试: {insight.function_name}",
            test_code=test_code.strip(),
            coverage_targets=[insight.function_name],
            test_type="unit",
            priority_score=10.0,
        )

    def _generate_performance_test(
        self,
        insight: CodeInsight,
        module_name: str,
    ) -> SmartTestCase:
        """生成性能测试"""
        test_name = f"test_{module_name}_{insight.function_name}_performance"

        test_code = f'''
    def {test_name}(self):
        """性能测试 - {insight.function_name} (复杂度: {insight.complexity_score:.1f})"""
        import time

        # 测试小数据集
        small_data = self._get_test_data('small')
        start_time = time.time()
        result_small = {module_name}.{insight.function_name}(small_data)
        small_time = time.time() - start_time

        # 测试中等数据集
        medium_data = self._get_test_data('medium')
        start_time = time.time()
        result_medium = {module_name}.{insight.function_name}(medium_data)
        medium_time = time.time() - start_time

        # 性能断言
        self.assertLess(small_time, 1.0, "小数据集处理时间过长")
        self.assertLess(medium_time, 5.0, "中等数据集处理时间过长")

        # 时间复杂度检查
        if small_time > 0:
            time_ratio = medium_time / small_time
            self.assertLess(time_ratio, 100, "检测到性能退化，可能的时间复杂度过高")

        # 验证结果一致性
        self._validate_result_consistency(result_small, result_medium)

    def _get_test_data(self, size):
        """获取测试数据"""
        if size == 'small':
            return [1, 2, 3, 4, 5]
        elif size == 'medium':
            return list(range(1, 1000))
        else:
            return []

    def _validate_result_consistency(self, result1, result2):
        """验证结果一致性"""
        # 基本的一致性检查
        self.assertTrue(result1 is not None or result2 is not None)
'''

        return SmartTestCase(
            name=test_name,
            description=f"性能测试: {insight.function_name}",
            test_code=test_code.strip(),
            coverage_targets=[insight.function_name],
            test_type="performance",
            priority_score=8.0,
        )
