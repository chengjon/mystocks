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


class QualityAssessmentMixin:
    """代码质量评估：最佳实践、安全实践、性能实践、架构模式、类型提示、日志"""

    def _validate_code_quality_assessment(self) -> Dict[str, Any]:
        """验证智能代码质量评估"""
        try:
            import os
            import ast
            import re

            quality_metrics = {}
            quality_issues = []
            files_analyzed = 0

            # 1. 测试覆盖率分析
            test_coverage = self._analyze_test_coverage()
            quality_metrics["test_coverage"] = test_coverage["score"]
            quality_issues.extend(test_coverage["issues"])

            # 2. 文档覆盖率分析
            doc_coverage = self._analyze_documentation_coverage()
            quality_metrics["documentation_coverage"] = doc_coverage["score"]
            quality_issues.extend(doc_coverage["issues"])

            # 3. 代码复杂度分析
            complexity_analysis = self._analyze_code_complexity()
            quality_metrics["avg_complexity"] = complexity_analysis["avg_complexity"]
            quality_metrics["max_complexity"] = complexity_analysis["max_complexity"]
            quality_issues.extend(complexity_analysis["issues"])

            # 4. 代码重复度分析
            duplication_analysis = self._analyze_code_duplication()
            quality_metrics["code_duplication"] = duplication_analysis["score"]
            quality_issues.extend(duplication_analysis["issues"])

            # 5. 导入和依赖分析
            dependency_analysis = self._analyze_dependencies()
            quality_metrics["import_health"] = dependency_analysis["score"]
            quality_issues.extend(dependency_analysis["issues"])

            # 计算综合质量评分
            quality_score = self._calculate_quality_score(quality_metrics)

            # 生成质量改进建议
            improvement_suggestions = self._generate_quality_improvements(
                quality_metrics, quality_issues
            )

            # 质量评估通过标准：评分>=65且无严重问题
            critical_issues = [
                issue for issue in quality_issues if issue.get("severity") == "critical"
            ]
            quality_ok = quality_score >= 65 and len(critical_issues) == 0

            return {
                "passed": quality_ok,
                "details": {
                    "quality_score": quality_score,
                    "metrics": quality_metrics,
                    "issues_found": len(quality_issues),
                    "critical_issues": len(critical_issues),
                    "files_analyzed": files_analyzed,
                    "assessment": self._assess_quality_level(quality_score),
                    "improvement_suggestions": improvement_suggestions[:3],
                    "issues": quality_issues[:4],  # 限制输出
                },
            }

        except Exception as e:
            import traceback

            error_msg = f"代码质量评估异常: {str(e)}\n{traceback.format_exc()}"
            return {"passed": False, "error": error_msg}

    def _analyze_test_coverage(self) -> dict:
        """分析测试覆盖率"""
        test_files = 0
        src_files = 0

        try:
            for root, dirs, files in os.walk("src"):
                src_files += len([f for f in files if f.endswith(".py")])
        except:
            src_files = 1

        try:
            if os.path.exists("tests"):
                for root, dirs, files in os.walk("tests"):
                    test_files += len([f for f in files if f.endswith(".py")])
        except:
            pass

        test_ratio = (test_files / src_files * 100) if src_files > 0 else 0

        issues = []
        if test_ratio < 50:
            issues.append(
                {
                    "category": "TESTING",
                    "type": "测试覆盖率不足",
                    "severity": "high",
                    "description": f"测试文件比例仅为{test_ratio:.1f}%，建议提高到70%以上",
                }
            )

        return {
            "score": min(100, test_ratio * 2),  # 标准化到0-100
            "issues": issues,
        }

    def _analyze_documentation_coverage(self) -> dict:
        """分析文档覆盖率"""
        documented_functions = 0
        total_functions = 0
        issues = []

        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                                total_functions += 1
                                if self._has_docstring(node):
                                    documented_functions += 1
                    except:
                        continue

        doc_ratio = (
            (documented_functions / total_functions * 100) if total_functions > 0 else 0
        )

        if doc_ratio < 60:
            issues.append(
                {
                    "category": "DOCUMENTATION",
                    "type": "文档覆盖率不足",
                    "severity": "medium",
                    "description": f"函数/类文档覆盖率仅为{doc_ratio:.1f}%，建议提高到80%以上",
                }
            )

        return {
            "score": doc_ratio,
            "issues": issues,
        }

    def _analyze_code_complexity(self) -> dict:
        """分析代码复杂度"""
        total_complexity = 0
        function_count = 0
        max_complexity = 0
        issues = []

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
                                complexity = self._calculate_function_complexity(node)
                                total_complexity += complexity
                                max_complexity = max(max_complexity, complexity)
                                function_count += 1

                                if complexity > 15:
                                    issues.append(
                                        {
                                            "category": "COMPLEXITY",
                                            "type": f"函数复杂度过高: {node.name} ({complexity})",
                                            "severity": "medium",
                                            "file": file_path,
                                            "line_number": node.lineno,
                                        }
                                    )
                    except:
                        continue

        avg_complexity = total_complexity / function_count if function_count > 0 else 0

        return {
            "avg_complexity": avg_complexity,
            "max_complexity": max_complexity,
            "issues": issues,
        }

    def _analyze_code_duplication(self) -> dict:
        """分析代码重复度（简化版）"""
        # 简化的重复检测：检查相似的导入语句
        import_lines = []
        issues = []

        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines[:20]):  # 只检查前20行
                                if line.strip().startswith(
                                    "import "
                                ) or line.strip().startswith("from "):
                                    import_lines.append(
                                        (line.strip(), file_path, i + 1)
                                    )
                    except:
                        continue

        # 检测重复导入
        import_counts = {}
        for imp_line, file_path, line_num in import_lines:
            if imp_line in import_counts:
                import_counts[imp_line].append((file_path, line_num))
            else:
                import_counts[imp_line] = [(file_path, line_num)]

        duplication_score = 0
        for imp_line, locations in import_counts.items():
            if len(locations) > 1:
                duplication_score += len(locations) - 1
                if len(locations) > 3:  # 重复3次以上
                    issues.append(
                        {
                            "category": "DUPLICATION",
                            "type": f"重复导入: {imp_line}",
                            "severity": "low",
                            "description": f"在{len(locations)}个文件中重复出现",
                        }
                    )

        # 标准化评分（0-100，越低越好）
        duplication_score = min(100, duplication_score * 10)

        return {
            "score": 100 - duplication_score,  # 转换为质量评分
            "issues": issues,
        }

    def _analyze_dependencies(self) -> dict:
        """分析导入和依赖健康度"""
        issues = []
        health_score = 100

        try:
            # 检查导入问题
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                            # 检查相对导入
                            if "from .." in content or "from ." in content:
                                issues.append(
                                    {
                                        "category": "DEPENDENCIES",
                                        "type": "使用相对导入",
                                        "severity": "low",
                                        "file": file_path,
                                        "description": "建议使用绝对导入以提高可维护性",
                                    }
                                )
                                health_score -= 5

                            # 检查循环导入风险
                            imports = re.findall(r"^from (\S+)", content, re.MULTILINE)
                            if len(set(imports)) < len(imports):
                                issues.append(
                                    {
                                        "category": "DEPENDENCIES",
                                        "type": "可能的循环导入",
                                        "severity": "medium",
                                        "file": file_path,
                                    }
                                )
                                health_score -= 10

                        except:
                            continue

        except Exception:
            health_score = 50  # 如果分析失败，给中等分数

        return {
            "score": max(0, health_score),
            "issues": issues,
        }

    def _calculate_quality_score(self, metrics: dict) -> float:
        """计算综合质量评分"""
        # 为不同指标设置权重
        weights = {
            "test_coverage": 0.25,
            "documentation_coverage": 0.20,
            "avg_complexity": -0.15,  # 复杂度越低越好（负权重）
            "max_complexity": -0.10,  # 最大复杂度越低越好
            "code_duplication": 0.15,
            "import_health": 0.15,
        }

        total_score = 0
        total_weight = 0

        for metric, weight in weights.items():
            if metric in metrics:
                value = metrics[metric]
                # 标准化复杂度指标（假设复杂度>10为差）
                if "complexity" in metric:
                    value = max(0, 100 - (value - 5) * 5)  # 复杂度5=100分，复杂度15=0分

                total_score += value * abs(weight)
                total_weight += abs(weight)

        return total_score / total_weight if total_weight > 0 else 50

    def _assess_quality_level(self, score: float) -> str:
        """评估质量等级"""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 55:
            return "fair"
        else:
            return "poor"

    def _generate_quality_improvements(self, metrics: dict, issues: list) -> list:
        """生成质量改进建议"""
        suggestions = []

        # 基于指标生成建议
        if metrics.get("test_coverage", 0) < 70:
            suggestions.append(
                {
                    "category": "TESTING",
                    "title": "提高测试覆盖率",
                    "description": "增加单元测试和集成测试",
                    "priority": "high",
                }
            )

        if metrics.get("documentation_coverage", 0) < 80:
            suggestions.append(
                {
                    "category": "DOCUMENTATION",
                    "title": "完善代码文档",
                    "description": "为函数和类添加详细的文档字符串",
                    "priority": "medium",
                }
            )

        if metrics.get("avg_complexity", 0) > 10:
            suggestions.append(
                {
                    "category": "ARCHITECTURE",
                    "title": "重构复杂函数",
                    "description": "将复杂函数拆分为更小的、可测试的函数",
                    "priority": "medium",
                }
            )

        return suggestions

    def _validate_best_practices(self) -> Dict[str, Any]:
        """验证智能最佳实践分析"""
        try:
            import os
            import ast
            import re

            # 扩展的最佳实践检查
            best_practice_checks = [
                ("type_hints", "类型提示使用", self._check_type_hints),
                ("error_handling", "错误处理模式", self._check_error_handling),
                ("logging", "日志记录实践", self._check_logging),
                ("documentation", "文档编写规范", self._check_docstrings),
                ("testing", "测试覆盖和质量", self._check_testing),
                ("security", "安全编码实践", self._check_security_practices),
                ("performance", "性能优化实践", self._check_performance_practices),
                ("architecture", "架构设计模式", self._check_architecture_patterns),
            ]

            practice_results = {}
            all_suggestions = []
            total_score = 0
            practices_checked = 0

            # 执行所有最佳实践检查
            for check_id, check_name, check_func in best_practice_checks:
                try:
                    result = check_func()
                    practice_results[check_id] = result
                    practices_checked += 1

                    # 累积评分
                    if "score" in result:
                        total_score += result["score"]

                    # 收集建议
                    suggestions = result.get("suggestions", [])
                    all_suggestions.extend(suggestions)

                except Exception as e:
                    # 如果某个检查失败，继续其他检查
                    practice_results[check_id] = {
                        "passed": False,
                        "error": str(e),
                        "score": 0,
                    }

            # 计算综合最佳实践评分
            avg_score = total_score / practices_checked if practices_checked > 0 else 0

            # 生成优先级排序的改进建议
            prioritized_suggestions = self._prioritize_best_practice_suggestions(
                all_suggestions
            )

            # 最佳实践验证通过标准：平均评分>=60
            practices_ok = avg_score >= 60

            return {
                "passed": practices_ok,
                "details": {
                    "practices_checked": practices_checked,
                    "average_score": avg_score,
                    "practice_results": practice_results,
                    "total_suggestions": len(all_suggestions),
                    "prioritized_suggestions": prioritized_suggestions[:5],
                    "implementation_level": self._assess_implementation_level(
                        avg_score
                    ),
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"最佳实践分析异常: {str(e)}"}

    def _prioritize_best_practice_suggestions(self, suggestions: list) -> list:
        """优先级排序最佳实践建议"""
        # 按优先级和影响程度排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        def sort_key(suggestion):
            priority = suggestion.get("priority", "medium")
            impact = suggestion.get("impact", "medium")
            return (
                priority_order.get(priority, 2),
                priority_order.get(impact, 2),
                -suggestion.get("score_improvement", 0),  # 得分改善潜力
            )

        return sorted(suggestions, key=sort_key)

    def _assess_implementation_level(self, score: float) -> str:
        """评估最佳实践实施水平"""
        if score >= 85:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 65:
            return "fair"
        elif score >= 50:
            return "basic"
        else:
            return "poor"

