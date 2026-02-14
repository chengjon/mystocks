"""量化策略验证器子模块"""

import ast
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PracticesChecksMixin:
    """实践检查：安全实践、性能实践、架构模式、类型提示、错误处理、日志、文档、测试"""

    def _check_security_practices(self) -> Dict[str, Any]:
        """检查安全编码实践"""
        issues = []
        score = 100

        try:
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                            lines = content.split("\n")
                            for i, line in enumerate(lines, 1):
                                # 检查硬编码密码
                                if re.search(
                                    r'password\s*=\s*["\'][^"\']*["\']',
                                    line,
                                    re.IGNORECASE,
                                ):
                                    issues.append(
                                        {
                                            "category": "SECURITY",
                                            "type": "硬编码密码",
                                            "severity": "critical",
                                            "file": file_path,
                                            "line": i,
                                            "suggestion": "使用环境变量或配置文件存储敏感信息",
                                            "priority": "critical",
                                        }
                                    )
                                    score -= 20

                                # 检查SQL注入风险
                                if re.search(r"(execute|raw).*\s*\+", line):
                                    issues.append(
                                        {
                                            "category": "SECURITY",
                                            "type": "可能的SQL注入",
                                            "severity": "high",
                                            "file": file_path,
                                            "line": i,
                                            "suggestion": "使用参数化查询或ORM",
                                            "priority": "high",
                                        }
                                    )
                                    score -= 15

                        except:
                            continue

        except Exception:
            score = 50

        return {
            "passed": len([i for i in issues if i["severity"] == "critical"]) == 0,
            "score": max(0, score),
            "issues": issues,
            "suggestions": self._generate_security_suggestions(issues),
        }

    def _check_performance_practices(self) -> Dict[str, Any]:
        """检查性能优化实践"""
        issues = []
        score = 100

        try:
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                            # 检查全局变量滥用
                            global_vars = re.findall(
                                r"^\s*global\s+\w+", content, re.MULTILINE
                            )
                            if len(global_vars) > 5:
                                issues.append(
                                    {
                                        "category": "PERFORMANCE",
                                        "type": "过多全局变量",
                                        "severity": "medium",
                                        "file": file_path,
                                        "suggestion": "减少全局变量使用，考虑依赖注入",
                                        "priority": "medium",
                                    }
                                )
                                score -= 10

                            # 检查大对象的创建
                            if "range(10000)" in content or "list(range(" in content:
                                issues.append(
                                    {
                                        "category": "PERFORMANCE",
                                        "type": "创建大对象",
                                        "severity": "low",
                                        "file": file_path,
                                        "suggestion": "考虑使用生成器或分批处理",
                                        "priority": "low",
                                    }
                                )
                                score -= 5

                        except:
                            continue

        except Exception:
            score = 50

        return {
            "passed": True,  # 性能问题不阻断
            "score": max(0, score),
            "issues": issues,
            "suggestions": self._generate_performance_suggestions(issues),
        }

    def _check_architecture_patterns(self) -> Dict[str, Any]:
        """检查架构设计模式"""
        issues = []
        score = 100

        try:
            # 检查文件大小和复杂度
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                            lines_count = len(content.split("\n"))

                            # 检查文件过大
                            if lines_count > 1000:
                                issues.append(
                                    {
                                        "category": "ARCHITECTURE",
                                        "type": f"文件过大 ({lines_count}行)",
                                        "severity": "medium",
                                        "file": file_path,
                                        "suggestion": "考虑将文件拆分为多个模块",
                                        "priority": "medium",
                                    }
                                )
                                score -= 10

                            # 检查类数量
                            tree = ast.parse(content)
                            class_count = len(
                                [
                                    node
                                    for node in ast.walk(tree)
                                    if isinstance(node, ast.ClassDef)
                                ]
                            )

                            if class_count > 10:
                                issues.append(
                                    {
                                        "category": "ARCHITECTURE",
                                        "type": f"文件包含过多类 ({class_count}个)",
                                        "severity": "low",
                                        "file": file_path,
                                        "suggestion": "考虑将类分散到不同文件",
                                        "priority": "low",
                                    }
                                )
                                score -= 5

                        except:
                            continue

        except Exception:
            score = 50

        return {
            "passed": True,
            "score": max(0, score),
            "issues": issues,
            "suggestions": self._generate_architecture_suggestions(issues),
        }

    def _generate_security_suggestions(self, issues: list) -> list:
        """生成安全改进建议"""
        suggestions = []

        if any(i["type"] == "硬编码密码" for i in issues):
            suggestions.append(
                {
                    "title": "实施安全配置管理",
                    "description": "使用环境变量和密钥管理服务",
                    "priority": "critical",
                    "impact": "high",
                    "score_improvement": 20,
                }
            )

        if any("SQL注入" in i["type"] for i in issues):
            suggestions.append(
                {
                    "title": "升级数据库访问模式",
                    "description": "采用ORM或参数化查询",
                    "priority": "high",
                    "impact": "high",
                    "score_improvement": 15,
                }
            )

        return suggestions

    def _generate_performance_suggestions(self, issues: list) -> list:
        """生成性能优化建议"""
        suggestions = []

        if any("全局变量" in i["type"] for i in issues):
            suggestions.append(
                {
                    "title": "优化状态管理",
                    "description": "减少全局状态，采用局部变量和参数传递",
                    "priority": "medium",
                    "impact": "medium",
                    "score_improvement": 10,
                }
            )

        return suggestions

    def _generate_architecture_suggestions(self, issues: list) -> list:
        """生成架构改进建议"""
        suggestions = []

        if any("文件过大" in i["type"] for i in issues):
            suggestions.append(
                {
                    "title": "实施模块化重构",
                    "description": "将大型文件拆分为职责明确的模块",
                    "priority": "medium",
                    "impact": "high",
                    "score_improvement": 15,
                }
            )

        return suggestions

    def _check_type_hints(self) -> Dict[str, Any]:
        """检查类型提示使用"""
        try:
            import ast
            import os

            functions_with_hints = 0
            total_functions = 0

            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                                tree = ast.parse(content)

                                for node in ast.walk(tree):
                                    if isinstance(node, ast.FunctionDef):
                                        total_functions += 1
                                        if node.returns or node.args.args:
                                            # 检查是否有类型注解
                                            has_return_hint = node.returns is not None
                                            has_arg_hints = any(
                                                arg.annotation for arg in node.args.args
                                            )

                                            if has_return_hint or has_arg_hints:
                                                functions_with_hints += 1

                        except Exception:
                            continue

                if total_functions >= 20:  # 限制分析数量
                    break

            hint_ratio = (
                (functions_with_hints / total_functions * 100)
                if total_functions > 0
                else 0
            )
            has_good_hints = hint_ratio >= 50

            return {
                "passed": has_good_hints,
                "ratio": hint_ratio,
                "suggestions": ["增加类型提示以提高代码可维护性"]
                if not has_good_hints
                else [],
            }

        except Exception as e:
            return {"passed": False, "error": str(e), "suggestions": []}

    def _check_error_handling(self) -> Dict[str, Any]:
        """检查错误处理"""
        try:
            import ast
            import os

            functions_with_try = 0
            total_functions = 0

            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                                tree = ast.parse(content)

                                for node in ast.walk(tree):
                                    if isinstance(node, ast.FunctionDef):
                                        total_functions += 1

                                        # 检查函数是否包含try语句
                                        has_try = any(
                                            isinstance(n, ast.Try)
                                            for n in ast.walk(node)
                                        )
                                        if has_try:
                                            functions_with_try += 1

                        except Exception:
                            continue

                if total_functions >= 20:
                    break

            error_handling_ratio = (
                (functions_with_try / total_functions * 100)
                if total_functions > 0
                else 0
            )
            has_good_error_handling = error_handling_ratio >= 30

            return {
                "passed": has_good_error_handling,
                "ratio": error_handling_ratio,
                "suggestions": ["增加适当的错误处理和异常捕获"]
                if not has_good_error_handling
                else [],
            }

        except Exception as e:
            return {"passed": False, "error": str(e), "suggestions": []}

    def _check_logging(self) -> Dict[str, Any]:
        """检查日志记录"""
        try:
            import os
            import re

            files_with_logging = 0
            total_files = 0

            logging_patterns = [r"logging\.", r"logger\.", r"log\."]

            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        total_files += 1

                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                                has_logging = any(
                                    re.search(pattern, content)
                                    for pattern in logging_patterns
                                )
                                if has_logging:
                                    files_with_logging += 1

                        except Exception:
                            continue

                if total_files >= 20:
                    break

            logging_ratio = (
                (files_with_logging / total_files * 100) if total_files > 0 else 0
            )
            has_good_logging = logging_ratio >= 40

            return {
                "passed": has_good_logging,
                "ratio": logging_ratio,
                "suggestions": ["增加适当的日志记录以便调试和监控"]
                if not has_good_logging
                else [],
            }

        except Exception as e:
            return {"passed": False, "error": str(e), "suggestions": []}

    def _check_docstrings(self) -> Dict[str, Any]:
        """检查文档字符串"""
        try:
            import ast
            import os

            functions_with_docs = 0
            total_functions = 0

            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                                tree = ast.parse(content)

                                for node in ast.walk(tree):
                                    if isinstance(node, ast.FunctionDef):
                                        total_functions += 1
                                        if ast.get_docstring(node):
                                            functions_with_docs += 1

                        except Exception:
                            continue

                if total_functions >= 20:
                    break

            doc_ratio = (
                (functions_with_docs / total_functions * 100)
                if total_functions > 0
                else 0
            )
            has_good_docs = doc_ratio >= 40

            return {
                "passed": has_good_docs,
                "ratio": doc_ratio,
                "suggestions": ["增加函数文档字符串以提高代码可读性"]
                if not has_good_docs
                else [],
            }

        except Exception as e:
            return {"passed": False, "error": str(e), "suggestions": []}

    def _check_testing(self) -> Dict[str, Any]:
        """检查测试覆盖"""
        try:
            import os

            # 计算测试文件与源代码文件的比例
            test_files = 0
            src_files = 0

            for root, dirs, files in os.walk("src"):
                src_files += len([f for f in files if f.endswith(".py")])

            for root, dirs, files in os.walk("tests"):
                test_files += len([f for f in files if f.endswith(".py")])

            test_ratio = (test_files / src_files * 100) if src_files > 0 else 0
            has_good_testing = test_ratio >= 50  # 理想情况下每个源文件对应一个测试文件

            return {
                "passed": has_good_testing,
                "ratio": test_ratio,
                "suggestions": ["增加单元测试覆盖率"] if not has_good_testing else [],
            }

        except Exception as e:
            return {"passed": False, "error": str(e), "suggestions": []}

