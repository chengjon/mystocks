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
class EnhancedCodeAnalyzer:
    """增强版代码分析器"""

    def __init__(self):
        self.patterns = self._init_pattern_library()
        self.bug_patterns = self._init_bug_pattern_library()
        self.performance_patterns = self._init_performance_pattern_library()

    def _init_pattern_library(self) -> Dict[str, Any]:
        """初始化模式库"""
        return {
            "validation": {
                "keywords": ["validate", "check", "verify", "ensure"],
                "patterns": [
                    r"if\s+.*:\s*raise\s+\w+",
                    r"if\s+not\s+.*:",
                    r"assert\s+.+",
                ],
                "weight": 0.8,
            },
            "error_handling": {
                "keywords": ["try", "except", "finally", "raise"],
                "patterns": [r"try\s*:", r"except\s+\w+:", r"raise\s+\w+"],
                "weight": 0.9,
            },
            "data_processing": {
                "keywords": ["process", "transform", "convert", "parse"],
                "patterns": [r"for\s+.*\s+in\s+.*:", r"\.map\(", r"\.filter\("],
                "weight": 0.7,
            },
            "file_operations": {
                "keywords": ["open", "read", "write", "close", "file"],
                "patterns": [r"with\s+open\s*\(", r"\.read\(", r"\.write\s*\("],
                "weight": 0.85,
            },
            "database_operations": {
                "keywords": ["sql", "query", "execute", "fetch", "connect"],
                "patterns": [r"cursor\.", r"execute\s*\(", r"fetch\w*\("],
                "weight": 0.9,
            },
            "network_operations": {
                "keywords": ["http", "request", "response", "api", "url"],
                "patterns": [r"requests\.", r"urllib\.", r"http\.", r"POST\s*|GET\s*"],
                "weight": 0.8,
            },
        }

    def _init_bug_pattern_library(self) -> Dict[str, Any]:
        """初始化Bug模式库"""
        return {
            "null_pointer": {
                "patterns": [r"\.split\(", r"\.index\(", r"\.[a-z_]+\s*\(\s*\)"],
                "conditions": ["not isinstance", "is not None"],
                "risk_score": 0.8,
            },
            "off_by_one": {
                "patterns": [r"range\s*\([^)]+\)", r"\[.*:\s*\d+\]"],
                "risk_score": 0.6,
            },
            "resource_leak": {
                "patterns": [r"open\s*\(", r"connect\s*\("],
                "conditions": ["not with", "no close", "no finally"],
                "risk_score": 0.9,
            },
            "sql_injection": {
                "patterns": [r"%.*\s*%", r"format\s*\(", r'f["\'].*\{.*\}'],
                "contexts": ["execute", "query"],
                "risk_score": 0.95,
            },
            "race_condition": {
                "patterns": [r"global\s+", r"threading\.", r"multiprocessing\."],
                "risk_score": 0.7,
            },
        }

    def _init_performance_pattern_library(self) -> Dict[str, Any]:
        """初始化性能模式库"""
        return {
            "nested_loops": {
                "patterns": [r"for\s+.+:\s*\n\s*for\s+.+:"],
                "complexity_factor": 2.0,
                "suggestion": "考虑使用字典查找或集合来优化嵌套循环",
            },
            "string_concatenation": {
                "patterns": [r'\w+\s*\+=\s*["\']', r'\+\s*["\'][^)]*["\']\s*\+'],
                "complexity_factor": 1.5,
                "suggestion": "使用join()或f-string来优化字符串拼接",
            },
            "repeated_computation": {
                "patterns": [r"for\s+.+:\s*\n.*\{.*\}.*for"],
                "complexity_factor": 1.3,
                "suggestion": "将重复计算提取到循环外部",
            },
            "inefficient_data_structures": {
                "patterns": [
                    r"\.index\s*\(",
                    r"in\s+range\s*\(",
                    r"list\(.*\.keys\(\)\)",
                ],
                "complexity_factor": 1.4,
                "suggestion": "使用适当的数据结构来提升查找效率",
            },
        }

    def analyze_code_patterns(self, source_file: str) -> List[CodePattern]:
        """分析代码模式"""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code)
            patterns = []

            # 分析AST模式
            for pattern_type, pattern_info in self.patterns.items():
                pattern_matches = self._find_pattern_matches(
                    source_code, pattern_type, pattern_info
                )

                for match in pattern_matches:
                    # 计算复杂度评分
                    complexity_score = self._calculate_pattern_complexity(
                        source_code, match["start_line"], match["end_line"]
                    )

                    # 评估风险等级
                    risk_level = self._assess_risk_level(pattern_type, complexity_score)

                    pattern = CodePattern(
                        pattern_type=pattern_type,
                        confidence=match["confidence"],
                        locations=[(match["start_line"], match["end_line"])],
                        complexity_score=complexity_score,
                        risk_level=risk_level,
                    )
                    patterns.append(pattern)

            return sorted(patterns, key=lambda p: p.complexity_score, reverse=True)

        except Exception as e:
            logger.error(f"代码模式分析失败: {e}")
            return []

    def _find_pattern_matches(
        self, source_code: str, pattern_type: str, pattern_info: Dict
    ) -> List[Dict]:
        """查找模式匹配"""
        matches = []
        lines = source_code.split("\n")

        # 关键词匹配
        keyword_matches = []
        for i, line in enumerate(lines, 1):
            for keyword in pattern_info["keywords"]:
                if keyword.lower() in line.lower():
                    keyword_matches.append(i)

        # 正则表达式匹配
        regex_matches = []
        for pattern in pattern_info["patterns"]:
            for match in re.finditer(pattern, source_code, re.MULTILINE):
                start_line = source_code[: match.start()].count("\n") + 1
                end_line = source_code[: match.end()].count("\n") + 1
                regex_matches.append(
                    {
                        "start_line": start_line,
                        "end_line": end_line,
                        "confidence": pattern_info["weight"],
                    }
                )

        return regex_matches

    def _calculate_pattern_complexity(
        self, source_code: str, start_line: int, end_line: int
    ) -> float:
        """计算模式复杂度"""
        lines = source_code.split("\n")
        pattern_lines = lines[start_line - 1 : end_line]

        complexity = 0.0

        # 基础复杂度：行数
        complexity += len(pattern_lines) * 0.1

        # 嵌套深度
        max_nesting = 0
        current_nesting = 0
        for line in pattern_lines:
            stripped = line.strip()
            if stripped.endswith(":"):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped and not line.startswith(" "):
                current_nesting = 0

        complexity += max_nesting * 0.5

        # 复杂表达式
        complex_expressions = 0
        for line in pattern_lines:
            if "if" in line and "and" in line or "or" in line:
                complex_expressions += 1
            if line.count("(") > 2 or line.count("[") > 2:
                complex_expressions += 1

        complexity += complex_expressions * 0.3

        return min(complexity, 10.0)  # 限制最大复杂度为10

    def _assess_risk_level(self, pattern_type: str, complexity_score: float) -> str:
        """评估风险等级"""
        if pattern_type in [
            "error_handling",
            "file_operations",
            "database_operations",
            "network_operations",
        ]:
            if complexity_score > 7:
                return "critical"
            elif complexity_score > 4:
                return "high"
            elif complexity_score > 2:
                return "medium"
        else:
            if complexity_score > 8:
                return "high"
            elif complexity_score > 4:
                return "medium"

        return "low"

    def predict_potential_bugs(self, source_file: str) -> List[Dict]:
        """预测潜在bug"""
        bugs = []

        try:
            with open(source_file, "r", encoding="utf-8") as f:
                source_code = f.read()

            for bug_type, bug_info in self.bug_patterns.items():
                for pattern in bug_info["patterns"]:
                    for match in re.finditer(pattern, source_code, re.MULTILINE):
                        # 检查上下文条件
                        context_start = max(0, match.start() - 200)
                        context_end = min(len(source_code), match.end() + 200)
                        context = source_code[context_start:context_end]

                        # 检查是否有防护措施
                        has_protection = self._check_protection_measures(
                            context, bug_info
                        )

                        if not has_protection:
                            line_num = source_code[: match.start()].count("\n") + 1
                            bugs.append(
                                {
                                    "type": bug_type,
                                    "line": line_num,
                                    "risk_score": bug_info["risk_score"],
                                    "description": self._get_bug_description(bug_type),
                                    "suggestion": self._get_bug_suggestion(bug_type),
                                }
                            )

            return sorted(bugs, key=lambda b: b["risk_score"], reverse=True)

        except Exception as e:
            logger.error(f"Bug预测失败: {e}")
            return []

    def _check_protection_measures(self, context: str, bug_info: Dict) -> bool:
        """检查是否有防护措施"""
        protection_patterns = [
            r"if\s+.*is\s+not\s+None",
            r"if\s+len\s*\(",
            r"if\s+.*in\s+.*:",
            r"try\s*:.*?except",
            r"with\s+.*:",
            r"assert\s+.+",
        ]

        for pattern in protection_patterns:
            if re.search(pattern, context, re.DOTALL):
                return True

        return False

    def _get_bug_description(self, bug_type: str) -> str:
        """获取bug描述"""
        descriptions = {
            "null_pointer": "可能出现空指针异常",
            "off_by_one": "可能出现索引越界错误",
            "resource_leak": "可能出现资源泄漏",
            "sql_injection": "可能存在SQL注入风险",
            "race_condition": "可能存在竞态条件",
        }
        return descriptions.get(bug_type, "未知类型bug")

    def _get_bug_suggestion(self, bug_type: str) -> str:
        """获取bug修复建议"""
        suggestions = {
            "null_pointer": "添加空值检查 before 使用变量",
            "off_by_one": "验证索引范围和循环边界",
            "resource_leak": "使用with语句或确保资源正确释放",
            "sql_injection": "使用参数化查询代替字符串拼接",
            "race_condition": "添加适当的同步机制或锁",
        }
        return suggestions.get(bug_type, "请仔细检查代码逻辑")

    def generate_enhanced_tests(
        self, source_file: str, patterns: List[CodePattern], bugs: List[Dict]
    ) -> List[TestCase]:
        """生成增强测试用例"""
        test_cases = []

        # 基于模式生成测试
        for pattern in patterns:
            if pattern.pattern_type == "validation":
                test_cases.extend(self._generate_validation_tests(pattern, source_file))
            elif pattern.pattern_type == "error_handling":
                test_cases.extend(
                    self._generate_error_handling_tests(pattern, source_file)
                )
            elif pattern.pattern_type == "data_processing":
                test_cases.extend(
                    self._generate_data_processing_tests(pattern, source_file)
                )
            elif pattern.pattern_type == "file_operations":
                test_cases.extend(
                    self._generate_file_operation_tests(pattern, source_file)
                )
            elif pattern.pattern_type == "database_operations":
                test_cases.extend(self._generate_database_tests(pattern, source_file))
            elif pattern.pattern_type == "network_operations":
                test_cases.extend(self._generate_network_tests(pattern, source_file))

        # 基于预测的bug生成防护性测试
        for bug in bugs:
            test_cases.append(self._generate_bug_prevention_test(bug, source_file))

        # 生成性能测试
        test_cases.extend(self._generate_performance_tests(patterns, source_file))

        # 生成边界测试
        test_cases.extend(self._generate_boundary_tests(source_file))

        # 按优先级排序
        test_cases = sorted(
            test_cases, key=lambda t: self._get_test_priority_score(t), reverse=True
        )

        return test_cases[:20]  # 限制最多20个测试用例

    def _generate_validation_tests(
        self, pattern: CodePattern, source_file: str
    ) -> List[TestCase]:
        """生成验证测试"""
        tests = []
        module_name = Path(source_file).stem

        for start_line, end_line in pattern.locations:
            test_name = f"test_{module_name}_validation_scenario_{start_line}"
            test_code = f'''
    def {test_name}(self):
        """测试验证逻辑 - 行{start_line}-{end_line}"""
        # 正常情况测试
        valid_data = self._get_valid_test_data()
        result = {module_name}.{self._extract_function_name(source_file, start_line)}(valid_data)
        self.assertIsNotNone(result)

        # 异常情况测试
        invalid_data_cases = [
            None,  # 空值
            "",    # 空字符串
            [],    # 空列表
            {{}},   # 空字典
        ]

        for invalid_data in invalid_data_cases:
            with self.assertRaises((ValueError, TypeError, AssertionError)):
                {module_name}.{self._extract_function_name(source_file, start_line)}(invalid_data)
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=f"验证第{start_line}-{end_line}行的输入验证逻辑",
                    test_code=test_code.strip(),
                    priority="high",
                    coverage_target=[f"lines:{start_line}-{end_line}"],
                    test_type="unit",
                    estimated_time=2.0,
                )
            )

        return tests

    def _generate_error_handling_tests(
        self, pattern: CodePattern, source_file: str
    ) -> List[TestCase]:
        """生成错误处理测试"""
        tests = []
        module_name = Path(source_file).stem

        for start_line, end_line in pattern.locations:
            test_name = f"test_{module_name}_error_handling_{start_line}"
            test_code = f'''
    def {test_name}(self):
        """测试错误处理 - 行{start_line}-{end_line}"""
        # 模拟各种异常情况
        error_scenarios = [
            {{'type': 'FileNotFoundError', 'trigger': lambda: self._trigger_file_error()}},
            {{'type': 'ConnectionError', 'trigger': lambda: self._trigger_connection_error()}},
            {{'type': 'TimeoutError', 'trigger': lambda: self._trigger_timeout_error()}},
            {{'type': 'PermissionError', 'trigger': lambda: self._trigger_permission_error()}},
        ]

        for scenario in error_scenarios:
            with self.assertRaises(scenario['type']):
                {module_name}.{self._extract_function_name(source_file, start_line)}(scenario['trigger']())

        # 测试错误恢复
        try:
            # 触发可恢复的错误
            {module_name}.{self._extract_function_name(source_file, start_line)}(self._get_recoverable_error_data())
        except Exception as e:
            # 验证错误信息
            self.assertIsNotNone(str(e))
            # 验证系统状态仍然正常
            self.assertTrue(self._check_system_health())
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=f"测试第{start_line}-{end_line}行的错误处理逻辑",
                    test_code=test_code.strip(),
                    priority="high",
                    coverage_target=[f"lines:{start_line}-{end_line}"],
                    test_type="unit",
                    estimated_time=3.0,
                )
            )

        return tests

    def _generate_data_processing_tests(
        self, pattern: CodePattern, source_file: str
    ) -> List[TestCase]:
        """生成数据处理测试"""
        tests = []
        module_name = Path(source_file).stem

        for start_line, end_line in pattern.locations:
            test_name = f"test_{module_name}_data_processing_{start_line}"
            test_code = f'''
    def {test_name}(self):
        """测试数据处理 - 行{start_line}-{end_line}"""
        # 小数据集测试
        small_data = self._get_small_test_dataset()
        result_small = {module_name}.{self._extract_function_name(source_file, start_line)}(small_data)
        self._validate_data_integrity(result_small)

        # 大数据集测试
        large_data = self._get_large_test_dataset()
        result_large = {module_name}.{self._extract_function_name(source_file, start_line)}(large_data)
        self._validate_data_integrity(result_large)

        # 性能断言
        processing_time = self._measure_processing_time(
            lambda: {module_name}.{self._extract_function_name(source_file, start_line)}(large_data)
        )
        self.assertLess(processing_time, 5.0, "数据处理时间过长")

        # 边界数据测试
        edge_cases = [
            self._get_empty_dataset(),
            self._get_single_item_dataset(),
            self._get_max_size_dataset(),
        ]

        for edge_data in edge_cases:
            result_edge = {module_name}.{self._extract_function_name(source_file, start_line)}(edge_data)
            self._validate_data_integrity(result_edge)
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=f"测试第{start_line}-{end_line}行的数据处理逻辑",
                    test_code=test_code.strip(),
                    priority="medium",
                    coverage_target=[f"lines:{start_line}-{end_line}"],
                    test_type="performance",
                    estimated_time=5.0,
                )
            )

        return tests

    def _generate_file_operation_tests(
        self, pattern: CodePattern, source_file: str
    ) -> List[TestCase]:
        """生成文件操作测试"""
        tests = []
        module_name = Path(source_file).stem

        for start_line, end_line in pattern.locations:
            test_name = f"test_{module_name}_file_operations_{start_line}"
            test_code = f'''
    def {test_name}(self):
        """测试文件操作 - 行{start_line}-{end_line}"""
        import tempfile
        import os

        # 使用临时文件进行测试
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(self._get_test_file_content())
            temp_file_path = temp_file.name

        try:
            # 正常文件操作测试
            result = {module_name}.{self._extract_function_name(source_file, start_line)}(temp_file_path)
            self.assertIsNotNone(result)

            # 文件不存在测试
            with self.assertRaises(FileNotFoundError):
                {module_name}.{self._extract_function_name(source_file, start_line)}("non_existent_file.txt")

            # 权限错误测试
            os.chmod(temp_file_path, 0o000)
            with self.assertRaises(PermissionError):
                {module_name}.{self._extract_function_name(source_file, start_line)}(temp_file_path)

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.chmod(temp_file_path, 0o644)
                os.unlink(temp_file_path)

        # 测试资源清理
        self.assertFalse(os.path.exists(temp_file_path), "临时文件未正确清理")
'''

            tests.append(
                TestCase(
                    name=test_name,
                    description=f"测试第{start_line}-{end_line}行的文件操作逻辑",
                    test_code=test_code.strip(),
                    priority="high",
                    coverage_target=[f"lines:{start_line}-{end_line}"],
                    test_type="integration",
                    estimated_time=3.0,
                )
            )

        return tests
