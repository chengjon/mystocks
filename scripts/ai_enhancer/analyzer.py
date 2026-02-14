#!/usr/bin/env python3
"""
AI算法增强器
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

import ast
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
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

from .dataclasses import CodeInsight, SmartTestCase

class AIAlgorithmEnhancer:
    """AI算法增强器"""

    def __init__(self):
        self.complexity_thresholds = {"low": 3.0, "medium": 6.0, "high": 9.0}
        self.code_patterns = self._init_code_patterns()
        self.bug_patterns = self._init_bug_patterns()

    def _init_code_patterns(self) -> Dict[str, Any]:
        """初始化代码模式库"""
        return {
            "validation_logic": {
                "keywords": ["validate", "check", "verify", "ensure", "assert"],
                "risk_factor": 0.7,
            },
            "error_handling": {
                "keywords": ["try", "except", "finally", "raise"],
                "risk_factor": 0.8,
            },
            "file_operations": {
                "keywords": ["open", "read", "write", "close"],
                "risk_factor": 0.9,
            },
            "database_operations": {
                "keywords": ["sql", "query", "execute", "fetch"],
                "risk_factor": 0.85,
            },
            "data_processing": {
                "keywords": ["process", "transform", "parse", "convert"],
                "risk_factor": 0.5,
            },
            "network_operations": {
                "keywords": ["http", "request", "response", "api"],
                "risk_factor": 0.8,
            },
        }

    def _init_bug_patterns(self) -> Dict[str, Any]:
        """初始化Bug模式库"""
        return {
            "null_pointer_risk": {
                "patterns": [r"\.split\(", r"\.index\(", r"\.lower\(", r"\.upper\("],
                "conditions": ["no null check", "no isinstance check"],
                "severity": "high",
            },
            "off_by_one_risk": {
                "patterns": [r"range\(", r"\[.*:\d+\]"],
                "conditions": ["no bounds check"],
                "severity": "medium",
            },
            "resource_leak_risk": {
                "patterns": [r"open\(", r"connect\(", r"create_connection"],
                "conditions": ["no with statement", "no finally"],
                "severity": "critical",
            },
            "sql_injection_risk": {
                "patterns": [r"%.*%", r"format\(", r'f".*\{.*\}'],
                "contexts": ["execute", "query"],
                "severity": "critical",
            },
        }

    def analyze_code_enhanced(self, source_file: str) -> List[CodeInsight]:
        """增强代码分析"""
        logger.info(f"🔍 开始增强代码分析: {source_file}")

        try:
            with open(source_file, "r", encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code)
            insights = []

            # 分析每个函数
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    insight = self._analyze_function_enhanced(
                        node, source_code, source_file
                    )
                    insights.append(insight)

            # 按优先级排序
            insights.sort(key=lambda x: x.priority_score, reverse=True)

            logger.info(f"✅ 分析完成，发现 {len(insights)} 个代码洞察")
            return insights

        except Exception as e:
            logger.error(f"代码分析失败: {e}")
            return []

    def _analyze_function_enhanced(
        self, node, source_code: str, source_file: str
    ) -> CodeInsight:
        """增强函数分析"""
        function_name = node.name

        # 计算复杂度
        complexity_score = self._calculate_complexity(node, source_code)

        # 确定风险等级
        risk_level = self._determine_risk_level(
            complexity_score, function_name, source_code
        )

        # 确定测试优先级
        test_priority = self._determine_test_priority(
            risk_level, complexity_score, function_name
        )

        # 识别潜在问题
        potential_issues = self._identify_potential_issues(node, source_code)

        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(
            complexity_score, risk_level, potential_issues, node
        )

        return CodeInsight(
            function_name=function_name,
            complexity_score=complexity_score,
            risk_level=risk_level,
            test_priority=test_priority,
            potential_issues=potential_issues,
            optimization_suggestions=optimization_suggestions,
        )

    def _calculate_complexity(self, node, source_code: str) -> float:
        """计算复杂度评分"""
        complexity = 1.0  # 基础复杂度

        # 基于AST结构计算
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 0.5
            elif isinstance(child, ast.ListComp) or isinstance(child, ast.DictComp):
                complexity += 0.8
            elif isinstance(child, ast.Try):
                complexity += 0.7
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child != node:  # 不计算嵌套函数的基础复杂度
                    complexity += 0.5

        # 基于代码行数
        lines = source_code.split("\n")
        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
            func_lines = node.end_lineno - node.lineno + 1
            complexity += func_lines * 0.1

        return min(complexity, 20.0)  # 限制最大复杂度

    def _determine_risk_level(
        self, complexity_score: float, function_name: str, source_code: str
    ) -> str:
        """确定风险等级"""
        # 基于复杂度的风险
        if complexity_score > self.complexity_thresholds["high"]:
            base_risk = "critical"
        elif complexity_score > self.complexity_thresholds["medium"]:
            base_risk = "high"
        elif complexity_score > self.complexity_thresholds["low"]:
            base_risk = "medium"
        else:
            base_risk = "low"

        # 基于函数名称和内容的调整
        if any(
            keyword in function_name.lower()
            for keyword in ["admin", "root", "exec", "eval"]
        ):
            if base_risk != "critical":
                base_risk = "high"

        # 检查是否包含高风险操作
        high_risk_patterns = [
            "exec(",
            "eval(",
            "subprocess.call",
            "os.system",
            "__import__",
        ]
        for pattern in high_risk_patterns:
            if pattern in source_code:
                base_risk = "critical"
                break

        return base_risk

    def _determine_test_priority(
        self, risk_level: str, complexity_score: float, function_name: str
    ) -> str:
        """确定测试优先级"""
        # 计算优先级评分
        risk_scores = {"critical": 10, "high": 8, "medium": 6, "low": 4}
        priority_score = risk_scores.get(risk_level, 5) + (complexity_score * 0.3)

        # 特殊函数处理
        if function_name in ["__init__", "__main__"]:
            return "medium"
        elif function_name.startswith("test_"):
            return "low"
        elif function_name.startswith("_"):
            priority_score += 1  # 私有函数稍微提高优先级

        if priority_score > 12:
            return "critical"
        elif priority_score > 9:
            return "high"
        elif priority_score > 6:
            return "medium"
        else:
            return "low"

    def _identify_potential_issues(self, node, source_code: str) -> List[str]:
        """识别潜在问题"""
        issues = []

        # 检查常见的代码问题
        if not self._has_error_handling(node):
            issues.append("缺少错误处理机制")

        if not self._has_input_validation(node):
            issues.append("缺少输入参数验证")

        if self._has_hardcoded_values(node, source_code):
            issues.append("存在硬编码值")

        if self._has_long_function(node):
            issues.append("函数过长，建议拆分")

        if self._has_deep_nesting(node):
            issues.append("嵌套层级过深")

        if self._has_duplicate_code(node):
            issues.append("存在重复代码")

        return issues

    def _generate_optimization_suggestions(
        self, complexity_score: float, risk_level: str, issues: List[str], node
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if complexity_score > self.complexity_thresholds["medium"]:
            suggestions.append("考虑将复杂函数拆分为多个小函数")
            suggestions.append("添加更多的单元测试来覆盖复杂逻辑")

        if risk_level in ["high", "critical"]:
            suggestions.append("增强错误处理和输入验证")
            suggestions.append("添加安全相关的测试用例")

        for issue in issues:
            if "缺少错误处理" in issue:
                suggestions.append("添加try-except块处理可能的异常")
            elif "缺少输入验证" in issue:
                suggestions.append("添加参数类型和范围验证")
            elif "硬编码" in issue:
                suggestions.append("将硬编码值提取为配置项或常量")
            elif "函数过长" in issue:
                suggestions.append("遵循单一职责原则，拆分函数功能")
            elif "嵌套层级" in issue:
                suggestions.append("使用早期返回或提取子函数来减少嵌套")

        return suggestions

    def _has_error_handling(self, node) -> bool:
        """检查是否有错误处理"""
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False

    def _has_input_validation(self, node) -> bool:
        """检查是否有输入验证"""
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # 简单检查：如果if语句包含验证相关的关键词
                if isinstance(child.test, ast.Compare):
                    continue  # 跳过简单的比较
                # 这里可以添加更复杂的验证逻辑检测
        return False

    def _has_hardcoded_values(self, node, source_code: str) -> bool:
        """检查是否有硬编码值"""
        # 检查常见的硬编码模式
        hardcoded_patterns = [
            r"localhost",
            r"127\.0\.0\.1",
            r"password",
            r"secret",
            r"http://",
            r"https://",
            r"test@",
            r"admin@",
        ]
        for pattern in hardcoded_patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                return True
        return False

    def _has_long_function(self, node) -> bool:
        """检查函数是否过长"""
        return hasattr(node, "end_lineno") and node.end_lineno - node.lineno > 50

    def _has_deep_nesting(self, node) -> bool:
        """检查嵌套是否过深"""
        max_nesting = 0
        current_nesting = 0

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif isinstance(child, ast.FunctionDef) and child != node:
                current_nesting = 0  # 重置嵌套计数

        return max_nesting > 4

    def _has_duplicate_code(self, node) -> bool:
        """检查是否有重复代码（简化实现）"""
        # 这里可以实现更复杂的重复代码检测算法
        # 目前返回False，避免过度检测
        return False
