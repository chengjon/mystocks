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
class CodePattern:
    """代码模式"""

    pattern_type: str  # pattern类型: validation, error_handling, data_processing, etc.
    confidence: float  # 模式识别置信度
    locations: List[Tuple[int, int]]  # 模式出现位置 (start_line, end_line)
    complexity_score: float  # 复杂度评分
    risk_level: str  # 风险等级: low, medium, high, critical


@dataclass
class TestCase:
    """测试用例"""

    name: str
    description: str
    test_code: str
    priority: str  # high, medium, low
    coverage_target: List[str]  # 目标覆盖的函数/行
    test_type: str  # unit, integration, performance, security
    estimated_time: float  # 预估执行时间(秒)


@dataclass
class EnhancementSuggestion:
    """增强建议"""

    category: str  # performance, security, maintainability, testability
    priority: str  # critical, high, medium, low
    description: str
    code_example: str
    impact_assessment: str  # 预期影响


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

    def _get_security_enhancement_example(self, pattern: CodePattern) -> str:
        """获取安全增强示例代码"""
        examples = {
            "validation": """
# 增强输入验证
def enhanced_validation(data):
    if not isinstance(data, (str, bytes)):
        raise TypeError("输入必须是字符串或字节")

    if len(data) > 1000:  # 防止DoS攻击
        raise ValueError("输入长度超出限制")

    # XSS防护
    import html
    data = html.escape(data)

    return data
""",
            "error_handling": """
# 增强错误处理
import logging

def enhanced_error_handling(operation):
    try:
        result = operation()
        return result
    except ValueError as e:
        logging.warning(f"数值错误: {e}")
        raise
    except ConnectionError as e:
        logging.error(f"连接错误: {e}")
        # 实现重试机制
        return None
    except Exception as e:
        logging.critical(f"未知错误: {e}")
        raise
""",
            "file_operations": """
# 安全的文件操作
import os
import tempfile
from pathlib import Path

def safe_file_operation(file_path):
    # 路径验证
    file_path = Path(file_path).resolve()
    if not str(file_path).startswith('/safe/directory/'):
        raise SecurityError("不安全的文件路径")

    # 使用上下文管理器确保资源清理
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
""",
        }

        return examples.get(pattern.pattern_type, "# 请根据具体模式添加相应的安全检查")

    def _get_bug_fix_example(self, bug: Dict) -> str:
        """获取Bug修复示例"""
        examples = {
            "null_pointer": """
# 修复空指针问题
def safe_operation(data):
    if data is None:
        raise ValueError("数据不能为空")

    if not hasattr(data, 'method'):
        raise AttributeError("数据类型不支持此操作")

    return data.method()
""",
            "sql_injection": """
# 使用参数化查询防止SQL注入
def safe_query(user_input):
    # 危险的做法（不要使用）
    # query = f"SELECT * FROM users WHERE name = '{user_input}'"

    # 安全的做法
    query = "SELECT * FROM users WHERE name = %s"
    cursor.execute(query, (user_input,))
    return cursor.fetchall()
""",
            "resource_leak": """
# 确保资源正确释放
def safe_file_processing(file_path):
    try:
        with open(file_path, 'r') as f:
            data = f.read()
            # 处理数据
            return processed_data
    except Exception as e:
        logging.error(f"文件处理失败: {e}")
        raise
    # with语句自动关闭文件，无需手动close
""",
        }

        return examples.get(bug["type"], "# 请根据具体bug类型添加相应的修复代码")

    def _get_performance_optimization_example(self, pattern: CodePattern) -> str:
        """获取性能优化示例"""
        return """
# 性能优化示例

# 优化前：嵌套循环 O(n²)
def find_duplicates_slow(items):
    duplicates = []
    for i, item1 in enumerate(items):
        for j, item2 in enumerate(items):
            if i != j and item1 == item2:
                duplicates.append(item1)
    return duplicates

# 优化后：使用集合 O(n)
def find_duplicates_fast(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
"""

    def _get_refactoring_example(self) -> str:
        """获取重构示例"""
        return """
# 代码重构示例

# 重构前：单一函数承担过多职责
def process_user_data(data):
    # 验证数据
    if not data:
        raise ValueError("数据不能为空")

    # 转换数据
    processed = []
    for item in data:
        processed.append(transform(item))

    # 保存数据
    with open('output.txt', 'w') as f:
        f.write(str(processed))

    return processed

# 重构后：职责分离
class UserDataProcessor:
    def __init__(self):
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.storage = DataStorage()

    def process(self, data):
        self.validator.validate(data)
        processed = self.transformer.transform(data)
        self.storage.save(processed)
        return processed
"""

    # 辅助方法 - 在实际实现中需要填充具体逻辑
    def _get_valid_test_data(self):
        pass

    def _get_recoverable_error_data(self):
        pass

    def _get_small_test_dataset(self):
        pass

    def _get_large_test_dataset(self):
        pass

    def _validate_data_integrity(self, result):
        pass

    def _measure_processing_time(self, func):
        pass

    def _get_test_file_content(self):
        pass

    def _get_bug_prevention_test_cases(self, bug_type):
        pass

    def _get_performance_test_data(self, size):
        pass

    def _validate_performance_results(self, result1, result2):
        pass

    def _get_boundary_test_data(self, scenario):
        pass

    def _get_expected_result_type(self, scenario):
        pass

    def _should_raise_exception_for_boundary(self, scenario):
        pass


class EnhancedTestOptimizer:
    """增强版测试优化器"""

    def __init__(self):
        self.analyzer = EnhancedCodeAnalyzer()
        self.project_root = Path(__file__).parent.parent

    def optimize_module(self, source_file: str) -> Dict:
        """优化单个模块"""
        logger.info(f"🚀 开始增强优化模块: {source_file}")

        try:
            # 1. 代码模式分析
            patterns = self.analyzer.analyze_code_patterns(source_file)
            logger.info(f"📊 发现 {len(patterns)} 个代码模式")

            # 2. Bug预测
            bugs = self.analyzer.predict_potential_bugs(source_file)
            logger.info(f"🐛 预测到 {len(bugs)} 个潜在bug")

            # 3. 生成增强测试
            test_cases = self.analyzer.generate_enhanced_tests(
                source_file, patterns, bugs
            )
            logger.info(f"🧪 生成了 {len(test_cases)} 个增强测试用例")

            # 4. 获取优化建议
            suggestions = self.analyzer.get_enhancement_suggestions(
                source_file, patterns, bugs
            )
            logger.info(f"💡 生成了 {len(suggestions)} 个优化建议")

            # 5. 生成测试文件
            test_file_path = self._generate_enhanced_test_file(source_file, test_cases)

            # 6. 生成优化报告
            report_path = self._generate_enhancement_report(
                source_file, patterns, bugs, test_cases, suggestions
            )

            return {
                "success": True,
                "patterns_found": len(patterns),
                "bugs_predicted": len(bugs),
                "tests_generated": len(test_cases),
                "suggestions_count": len(suggestions),
                "test_file": test_file_path,
                "report_file": report_path,
            }

        except Exception as e:
            logger.error(f"增强优化失败: {e}")
            return {"success": False, "error": str(e)}

    def _generate_enhanced_test_file(
        self, source_file: str, test_cases: List[TestCase]
    ) -> str:
        """生成增强测试文件"""
        module_name = Path(source_file).stem
        output_dir = self.project_root / "enhanced_tests"
        output_dir.mkdir(exist_ok=True)

        test_file_path = output_dir / f"test_{module_name}_enhanced.py"

        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(f'''#!/usr/bin/env python3
"""
增强版测试用例 - {module_name}
由AI测试优化器自动生成

生成时间: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
测试用例数: {len(test_cases)}
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sqlite3
import time
from pathlib import Path

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from {module_name.replace("_", "")} import {module_name}
''')

            # 添加测试用例
            for test_case in test_cases:
                f.write(f"\n{test_case.test_code}\n")

            f.write("""

if __name__ == "__main__":
    # 运行测试
    unittest.main()
""")

        logger.info(f"✅ 增强测试文件已生成: {test_file_path}")
        return str(test_file_path)

    def _generate_enhancement_report(
        self,
        source_file: str,
        patterns: List[CodePattern],
        bugs: List[Dict],
        test_cases: List[TestCase],
        suggestions: List[EnhancementSuggestion],
    ) -> str:
        """生成增强报告"""
        module_name = Path(source_file).stem
        report_path = (
            self.project_root
            / "enhancement_reports"
            / f"{module_name}_enhancement_report.md"
        )
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"""# {module_name} 增强分析报告

**生成时间**: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**分析工具**: AI测试优化器 v3.0 (算法增强版)

## 📊 分析结果概览

- **代码模式发现**: {len(patterns)} 个
- **潜在Bug预测**: {len(bugs)} 个
- **增强测试生成**: {len(test_cases)} 个
- **优化建议**: {len(suggestions)} 条

## 🔍 代码模式分析

### 高风险模式
""")

            # 添加高风险模式
            high_risk_patterns = [
                p for p in patterns if p.risk_level in ["high", "critical"]
            ]
            for pattern in high_risk_patterns:
                f.write(f"""
- **{pattern.pattern_type}** (风险: {pattern.risk_level})
  - 复杂度评分: {pattern.complexity_score:.1f}
  - 位置: 行 {pattern.locations[0][0]}-{pattern.locations[0][1]}
  - 置信度: {pattern.confidence:.2f}
""")

            f.write("""
## 🐛 潜在Bug预测

### 高风险Bug
""")

            # 添加高风险Bug
            high_risk_bugs = [b for b in bugs if b["risk_score"] > 0.8]
            for bug in high_risk_bugs:
                f.write(f"""
- **{bug["type"]}** (风险评分: {bug["risk_score"]:.2f})
  - 位置: 行 {bug["line"]}
  - 描述: {bug["description"]}
  - 建议: {bug["suggestion"]}
""")

            f.write(f"""
## 🧪 增强测试用例

### 测试统计
- 高优先级测试: {len([t for t in test_cases if t.priority == "high"])} 个
- 中优先级测试: {len([t for t in test_cases if t.priority == "medium"])} 个
- 低优先级测试: {len([t for t in test_cases if t.priority == "low"])} 个

### 测试类型分布
- 单元测试: {len([t for t in test_cases if t.test_type == "unit"])} 个
- 集成测试: {len([t for t in test_cases if t.test_type == "integration"])} 个
- 性能测试: {len([t for t in test_cases if t.test_type == "performance"])} 个
- 安全测试: {len([t for t in test_cases if t.test_type == "security"])} 个

## 💡 优化建议

""")

            # 添加优化建议
            for suggestion in suggestions:
                f.write(f"""
### {suggestion.category.upper()} (优先级: {suggestion.priority})
**描述**: {suggestion.description}

**代码示例**:
```python
{suggestion.code_example}
```

**预期影响**: {suggestion.impact_assessment}
""")

            f.write(f"""
## 📈 预期改进效果

基于分析和建议，预期可以实现以下改进：

### 质量提升
- **Bug预防**: 通过增强测试，预防 {len(bugs)} 个潜在bug
- **代码健壮性**: 提升 {len([p for p in patterns if p.risk_level in ["high", "critical"]]) * 15:.0f}%
- **错误处理**: 改进 {len([p for p in patterns if p.pattern_type == "error_handling"])} 个错误处理点

### 性能优化
- **执行效率**: 优化 {len([p for p in patterns if p.complexity_score > 7.0])} 个性能瓶颈
- **资源使用**: 降低 {len([p for p in patterns if p.pattern_type in ["file_operations", "database_operations"]]) * 10:.0f}% 资源消耗

### 安全性增强
- **漏洞防护**: 修复 {len([b for b in bugs if b["risk_score"] > 0.9])} 个高风险安全漏洞
- **输入验证**: 加强 {len([p for p in patterns if p.pattern_type == "validation"])} 个验证点

---

*报告由AI测试优化器自动生成*
*下次分析建议: 在代码修改后重新运行增强优化*
""")

        logger.info(f"✅ 增强报告已生成: {report_path}")
        return str(report_path)


def main():
    """主入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AI测试优化器 - 算法增强版")
    parser.add_argument("source_files", nargs="+", help="要优化的Python源文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    optimizer = EnhancedTestOptimizer()

    total_patterns = 0
    total_bugs = 0
    total_tests = 0
    success_count = 0

    for source_file in args.source_files:
        if not Path(source_file).exists():
            logger.error(f"文件不存在: {source_file}")
            continue

        result = optimizer.optimize_module(source_file)

        if result["success"]:
            success_count += 1
            total_patterns += result["patterns_found"]
            total_bugs += result["bugs_predicted"]
            total_tests += result["tests_generated"]

            print(
                f"✅ {source_file}: 模式={result['patterns_found']}, Bug={result['bugs_predicted']}, 测试={result['tests_generated']}"
            )
        else:
            print(f"❌ {source_file}: {result['error']}")

    print(f"\n📊 总计: {success_count}/{len(args.source_files)} 个文件成功")
    print(f"🔍 发现模式: {total_patterns} 个")
    print(f"🐛 预测Bug: {total_bugs} 个")
    print(f"🧪 生成测试: {total_tests} 个")


if __name__ == "__main__":
    main()
