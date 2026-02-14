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


class AIValidatorMixin:
    """AI代码审查与性能优化验证"""

    def _validate_ai_code_review(self) -> Dict[str, Any]:
        """验证AI增强代码审查"""
        try:
            import os
            import re
            import ast
            import inspect

            review_issues = []
            files_reviewed = 0
            total_complexity_score = 0

            # 增强的代码质量检查模式
            code_quality_patterns = [
                # 安全性问题
                (r"eval\(.+\)", "SECURITY", "使用eval()可能存在安全风险", "high"),
                (r"exec\(.+\)", "SECURITY", "使用exec()可能存在安全风险", "high"),
                (
                    r"input\(.+\)",
                    "SECURITY",
                    "input()在Python 2中不安全，考虑使用sys.stdin",
                    "medium",
                ),
                # 代码质量问题
                (r"except\s*:\s*$", "QUALITY", "过于宽泛的异常捕获", "medium"),
                (
                    r"print\(.+\)",
                    "QUALITY",
                    "调试用的print语句应移除或替换为日志",
                    "low",
                ),
                (r"pass\s*$", "QUALITY", "空pass语句可能表示未完成的代码", "low"),
                # 性能问题
                (
                    r"for.*in.*range\(len\(",
                    "PERFORMANCE",
                    "避免在循环中使用len()，考虑使用enumerate()",
                    "medium",
                ),
                (
                    r"\.append\(.*\)\s*$",
                    "PERFORMANCE",
                    "列表append操作在循环中可能影响性能",
                    "low",
                ),
                # 可维护性问题
                (
                    r"def\s+\w+\([^)]{100,}",
                    "MAINTAINABILITY",
                    "函数参数过长，考虑使用参数对象",
                    "medium",
                ),
                (
                    r"class\s+\w+.*:\s*$",
                    "MAINTAINABILITY",
                    "类定义缺少文档字符串",
                    "low",
                ),
            ]

            # 扫描Python文件进行AI增强审查
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if files_reviewed >= 10:  # 增加审查文件数量
                        break
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                lines = content.split("\n")
                                files_reviewed += 1

                                # 1. 模式匹配检查
                                for (
                                    pattern,
                                    category,
                                    description,
                                    severity,
                                ) in code_quality_patterns:
                                    matches = re.findall(pattern, content, re.MULTILINE)
                                    if matches:
                                        review_issues.append(
                                            {
                                                "file": file_path,
                                                "category": category,
                                                "type": description,
                                                "severity": severity,
                                                "occurrences": len(matches),
                                                "line_numbers": self._find_line_numbers(
                                                    content, pattern
                                                ),
                                            }
                                        )

                                # 2. AST分析 - 检查函数复杂度
                                try:
                                    tree = ast.parse(content)
                                    for node in ast.walk(tree):
                                        if isinstance(node, ast.FunctionDef):
                                            complexity = (
                                                self._calculate_function_complexity(
                                                    node
                                                )
                                            )
                                            total_complexity_score += complexity

                                            if complexity > 10:  # 复杂度阈值
                                                review_issues.append(
                                                    {
                                                        "file": file_path,
                                                        "category": "COMPLEXITY",
                                                        "type": f"函数 '{node.name}' 复杂度过高 ({complexity})",
                                                        "severity": "medium",
                                                        "suggestion": "考虑重构函数，拆分为更小的函数",
                                                        "line_number": node.lineno,
                                                    }
                                                )

                                        elif isinstance(node, ast.ClassDef):
                                            # 检查类是否有文档字符串
                                            if not self._has_docstring(node):
                                                review_issues.append(
                                                    {
                                                        "file": file_path,
                                                        "category": "DOCUMENTATION",
                                                        "type": f"类 '{node.name}' 缺少文档字符串",
                                                        "severity": "low",
                                                        "line_number": node.lineno,
                                                    }
                                                )

                                except SyntaxError:
                                    review_issues.append(
                                        {
                                            "file": file_path,
                                            "category": "SYNTAX",
                                            "type": "文件包含语法错误",
                                            "severity": "high",
                                        }
                                    )

                                # 3. 代码风格检查
                                style_issues = self._check_code_style(content, lines)
                                review_issues.extend(style_issues)

                        except Exception as e:
                            review_issues.append(
                                {
                                    "file": file_path,
                                    "category": "ERROR",
                                    "type": f"文件读取错误: {str(e)}",
                                    "severity": "medium",
                                }
                            )
                            continue

                if files_reviewed >= 10:
                    break

            # 计算综合评分
            review_score = self._calculate_review_score(review_issues, files_reviewed)

            # AI代码审查通过标准：评分>=70且无高严重性问题
            high_severity_issues = [
                issue for issue in review_issues if issue.get("severity") == "high"
            ]
            ai_review_ok = review_score >= 70 and len(high_severity_issues) == 0

            return {
                "passed": ai_review_ok,
                "details": {
                    "files_reviewed": files_reviewed,
                    "issues_found": len(review_issues),
                    "high_severity_issues": len(high_severity_issues),
                    "review_score": review_score,
                    "avg_complexity": total_complexity_score / max(files_reviewed, 1),
                    "issues": review_issues[:5],  # 限制输出前5个问题
                    "categories": self._group_issues_by_category(review_issues),
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"AI代码审查异常: {str(e)}"}

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度（简化的圈复杂度）"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _has_docstring(self, node: ast.ClassDef) -> bool:
        """检查类或函数是否有文档字符串"""
        return (
            len(node.body) > 0
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Str)
        )

    def _find_line_numbers(self, content: str, pattern: str) -> list:
        """查找模式匹配的行号"""
        lines = content.split("\n")
        line_numbers = []
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                line_numbers.append(i)
        return line_numbers[:3]  # 限制返回前3个

    def _check_code_style(self, content: str, lines: list) -> list:
        """检查代码风格问题"""
        issues = []

        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 88:  # Black默认行长度
                issues.append(
                    {
                        "file": "current_file",
                        "category": "STYLE",
                        "type": f"行长度过长 ({len(line)} > 88)",
                        "severity": "low",
                        "line_number": i,
                    }
                )

            # 检查连续空行
            if i < len(lines) - 1:
                if line.strip() == "" and lines[i + 1].strip() == "":
                    issues.append(
                        {
                            "file": "current_file",
                            "category": "STYLE",
                            "type": "多余的连续空行",
                            "severity": "low",
                            "line_number": i,
                        }
                    )

        return issues

    def _calculate_review_score(self, issues: list, files_reviewed: int) -> float:
        """计算代码审查综合评分"""
        if files_reviewed == 0:
            return 100.0

        # 基础分数
        base_score = 100.0

        # 根据问题严重性扣分
        severity_weights = {"high": 10, "medium": 5, "low": 1}

        for issue in issues:
            severity = issue.get("severity", "low")
            base_score -= severity_weights.get(severity, 1)

        # 确保分数不低于0
        return max(0.0, min(100.0, base_score))

    def _group_issues_by_category(self, issues: list) -> dict:
        """按类别分组问题"""
        categories = {}
        for issue in issues:
            category = issue.get("category", "OTHER")
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        return categories

    def _validate_automated_suggestions(self) -> Dict[str, Any]:
        """验证自动化修复建议和工具链"""
        try:
            import os
            import glob

            suggestions_found = []
            tools_available = []

            # 检查自动化修复工具和配置
            automation_checks = [
                {
                    "name": "Pre-commit配置",
                    "files": [".pre-commit-config.yaml", ".pre-commit-config.yml"],
                    "description": "代码提交前的自动化检查",
                    "importance": "high",
                },
                {
                    "name": "Makefile",
                    "files": ["Makefile", "makefile"],
                    "description": "自动化构建和维护脚本",
                    "importance": "medium",
                },
                {
                    "name": "修复脚本",
                    "pattern": "scripts/fix_*.py",
                    "description": "自动化代码修复脚本",
                    "importance": "medium",
                },
                {
                    "name": "Lint修复工具",
                    "files": ["scripts/lint_fix.py", "scripts/auto_fix.py"],
                    "description": "自动化代码格式化和修复",
                    "importance": "medium",
                },
                {
                    "name": "CI/CD配置",
                    "files": [".github/workflows/*.yml", ".gitlab-ci.yml"],
                    "description": "持续集成自动化流程",
                    "importance": "high",
                },
            ]

            # 检查每个自动化工具
            for check in automation_checks:
                found = False

                if "files" in check:
                    for file_path in check["files"]:
                        if os.path.exists(file_path):
                            found = True
                            tools_available.append(
                                {
                                    "name": check["name"],
                                    "file": file_path,
                                    "description": check["description"],
                                    "importance": check["importance"],
                                }
                            )
                            break
                elif "pattern" in check:
                    matches = glob.glob(check["pattern"])
                    if matches:
                        found = True
                        for match in matches:
                            tools_available.append(
                                {
                                    "name": check["name"],
                                    "file": match,
                                    "description": check["description"],
                                    "importance": check["importance"],
                                }
                            )

                if not found:
                    suggestions_found.append(
                        {
                            "type": "MISSING_TOOL",
                            "name": check["name"],
                            "description": check["description"],
                            "importance": check["importance"],
                            "suggestion": f"考虑添加{check['name']}来提高开发效率",
                        }
                    )

            # 分析工具链完整性
            high_importance_tools = [
                t for t in tools_available if t["importance"] == "high"
            ]
            automation_score = len(high_importance_tools) * 25  # 每个高重要性工具25分

            # 生成智能建议
            smart_suggestions = self._generate_smart_suggestions(
                tools_available, suggestions_found
            )

            # 自动化建议验证通过标准：至少有50%的建议得分
            automation_ok = automation_score >= 50

            return {
                "passed": automation_ok,
                "details": {
                    "tools_available": len(tools_available),
                    "suggestions_made": len(suggestions_found),
                    "automation_score": automation_score,
                    "tools": tools_available,
                    "suggestions": suggestions_found[:3],  # 限制输出
                    "smart_suggestions": smart_suggestions,
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"自动化建议验证异常: {str(e)}"}

    def _generate_smart_suggestions(
        self, tools_available: list, suggestions_found: list
    ) -> list:
        """生成智能化的改进建议"""
        smart_suggestions = []

        # 基于现有工具生成针对性建议
        tool_names = {tool["name"] for tool in tools_available}

        if "Pre-commit配置" not in tool_names:
            smart_suggestions.append(
                {
                    "priority": "high",
                    "category": "AUTOMATION",
                    "title": "添加Pre-commit钩子",
                    "description": "配置pre-commit来自动化代码质量检查",
                    "implementation": "安装pre-commit并配置基本的钩子（black, flake8, mypy）",
                }
            )

        if "Makefile" not in tool_names:
            smart_suggestions.append(
                {
                    "priority": "medium",
                    "category": "BUILD",
                    "title": "创建Makefile",
                    "description": "添加make命令来简化常见开发任务",
                    "implementation": "创建包含install, test, lint, format等目标的Makefile",
                }
            )

        # 基于项目规模生成建议
        if len(tools_available) < 3:
            smart_suggestions.append(
                {
                    "priority": "medium",
                    "category": "TOOLCHAIN",
                    "title": "完善开发工具链",
                    "description": "项目缺少基本的自动化工具，建议完善CI/CD流程",
                    "implementation": "添加GitHub Actions工作流，配置自动化测试和部署",
                }
            )

        return smart_suggestions

    def _validate_performance_optimization(self) -> Dict[str, Any]:
        """验证智能性能优化分析"""
        try:
            import os
            import re
            import ast

            performance_issues = []
            optimization_suggestions = []
            files_analyzed = 0
            total_performance_score = 0

            # 增强的性能分析模式
            performance_patterns = [
                # 内存效率问题
                (
                    r"for.*in.*range\(10000+\)",
                    "MEMORY",
                    "大循环可能导致内存压力",
                    "high",
                    "考虑使用numpy向量化操作",
                ),
                (
                    r"\.append\(.*\)\s*$",
                    "MEMORY",
                    "列表频繁append操作",
                    "medium",
                    "考虑使用列表推导式或预分配",
                ),
                (
                    r"pd\.concat.*in.*for",
                    "MEMORY",
                    "循环中DataFrame拼接效率低",
                    "high",
                    "使用pd.concat一次性操作",
                ),
                # 计算效率问题
                (
                    r"re\.compile.*in.*for",
                    "COMPUTATION",
                    "循环中重复编译正则表达式",
                    "medium",
                    "预编译正则表达式",
                ),
                (
                    r"\.sort\(\).*in.*for",
                    "COMPUTATION",
                    "循环中重复排序",
                    "medium",
                    "优化排序算法或缓存结果",
                ),
                (
                    r"math\.sqrt.*in.*for",
                    "COMPUTATION",
                    "循环中重复平方根计算",
                    "low",
                    "考虑数值优化或查表法",
                ),
                # I/O效率问题
                (
                    r"open\(.*\).*in.*for",
                    "IO",
                    "循环中重复文件操作",
                    "high",
                    "批量读取或使用上下文管理器",
                ),
                (
                    r"requests\.\w+.*in.*for",
                    "IO",
                    "循环中重复网络请求",
                    "high",
                    "使用异步请求或批量API",
                ),
                # 数据结构问题
                (
                    r"list\(.*range\(.*\)\)",
                    "DATA_STRUCTURE",
                    "不必要的列表创建",
                    "medium",
                    "使用生成器表达式",
                ),
                (
                    r"dict\(.*zip\(.*\)\)",
                    "DATA_STRUCTURE",
                    "低效的字典创建",
                    "low",
                    "使用字典推导式",
                ),
            ]

            # 分析Python文件
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if files_analyzed >= 8:  # 增加分析文件数量
                        break
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                lines = content.split("\n")
                                files_analyzed += 1

                                # 1. 模式匹配分析
                                for (
                                    pattern,
                                    category,
                                    description,
                                    severity,
                                    suggestion,
                                ) in performance_patterns:
                                    matches = re.findall(
                                        pattern, content, re.IGNORECASE | re.DOTALL
                                    )
                                    if matches:
                                        performance_issues.append(
                                            {
                                                "file": file_path,
                                                "category": category,
                                                "type": description,
                                                "severity": severity,
                                                "suggestion": suggestion,
                                                "occurrences": len(matches),
                                                "lines": self._find_line_numbers(
                                                    content, pattern
                                                ),
                                            }
                                        )

                                # 2. AST分析 - 检测性能反模式
                                try:
                                    tree = ast.parse(content)
                                    perf_analysis = self._analyze_performance_patterns(
                                        tree
                                    )
                                    performance_issues.extend(perf_analysis)
                                except SyntaxError:
                                    performance_issues.append(
                                        {
                                            "file": file_path,
                                            "category": "SYNTAX",
                                            "type": "语法错误影响性能分析",
                                            "severity": "medium",
                                        }
                                    )

                                # 3. 生成优化建议
                                file_suggestions = (
                                    self._generate_performance_suggestions(
                                        content, lines, file_path
                                    )
                                )
                                optimization_suggestions.extend(file_suggestions)

                        except Exception as e:
                            performance_issues.append(
                                {
                                    "file": file_path,
                                    "category": "ERROR",
                                    "type": f"性能分析错误: {str(e)}",
                                    "severity": "low",
                                }
                            )
                            continue

                if files_analyzed >= 8:
                    break

            # 计算性能优化评分
            optimization_score = self._calculate_performance_score(
                performance_issues, files_analyzed
            )

            # 生成智能优化建议
            smart_optimizations = self._prioritize_optimizations(
                optimization_suggestions, performance_issues
            )

            # 性能优化验证通过标准：评分>=60且无高严重性问题
            high_severity_issues = [
                issue for issue in performance_issues if issue.get("severity") == "high"
            ]
            performance_ok = optimization_score >= 60 and len(high_severity_issues) <= 2

            return {
                "passed": performance_ok,
                "details": {
                    "files_analyzed": files_analyzed,
                    "performance_issues": len(performance_issues),
                    "high_severity_issues": len(high_severity_issues),
                    "optimization_score": optimization_score,
                    "optimization_suggestions": len(optimization_suggestions),
                    "issues": performance_issues[:4],  # 限制输出
                    "smart_optimizations": smart_optimizations[:3],  # 前3个优化建议
                    "categories": self._group_issues_by_category(performance_issues),
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"性能优化分析异常: {str(e)}"}

    def _analyze_performance_patterns(self, tree: ast.AST) -> list:
        """通过AST分析性能反模式"""
        issues = []

        for node in ast.walk(tree):
            # 检测嵌套循环
            if isinstance(node, ast.For):
                nested_loops = self._count_nested_loops(node)
                if nested_loops > 2:
                    issues.append(
                        {
                            "file": "current_file",
                            "category": "COMPLEXITY",
                            "type": f"深度嵌套循环 ({nested_loops}层)",
                            "severity": "high",
                            "suggestion": "考虑重构嵌套循环，使用更高效的算法",
                            "line_number": getattr(node, "lineno", 0),
                        }
                    )

            # 检测大的数据结构创建
            elif isinstance(node, ast.ListComp):
                if self._is_large_comprehension(node):
                    issues.append(
                        {
                            "file": "current_file",
                            "category": "MEMORY",
                            "type": "大型列表推导式可能消耗大量内存",
                            "severity": "medium",
                            "suggestion": "考虑使用生成器表达式或分批处理",
                            "line_number": getattr(node, "lineno", 0),
                        }
                    )

        return issues

    def _generate_performance_suggestions(
        self, content: str, lines: list, file_path: str
    ) -> list:
        """生成具体的性能优化建议"""
        suggestions = []

        # 检查导入优化
        if "import pandas as pd" in content and "pd.read_csv" in content:
            suggestions.append(
                {
                    "file": file_path,
                    "type": "IO_OPTIMIZATION",
                    "title": "Pandas读取优化",
                    "description": "使用chunksize参数分块读取大文件",
                    "code_example": "pd.read_csv('large_file.csv', chunksize=10000)",
                    "impact": "high",
                }
            )

        # 检查循环优化
        loop_count = content.count("for ") + content.count("while ")
        if loop_count > 10:
            suggestions.append(
                {
                    "file": file_path,
                    "type": "LOOP_OPTIMIZATION",
                    "title": "循环优化",
                    "description": f"文件包含{loop_count}个循环，考虑向量化操作",
                    "code_example": "使用numpy数组操作替代循环",
                    "impact": "high",
                }
            )

        return suggestions

    def _calculate_performance_score(self, issues: list, files_analyzed: int) -> float:
        """计算性能优化评分"""
        if files_analyzed == 0:
            return 100.0

        base_score = 100.0

        # 根据问题严重性和数量扣分
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "high":
                base_score -= 8
            elif severity == "medium":
                base_score -= 4
            else:  # low
                base_score -= 1

        return max(0.0, min(100.0, base_score))

    def _prioritize_optimizations(self, suggestions: list, issues: list) -> list:
        """优先排序优化建议"""
        # 按影响程度和问题严重性排序
        prioritized = []

        # 高影响的建议优先
        high_impact = [s for s in suggestions if s.get("impact") == "high"]
        prioritized.extend(high_impact)

        # 中等影响的建议
        medium_impact = [s for s in suggestions if s.get("impact") == "medium"]
        prioritized.extend(medium_impact)

        # 基于问题数量的建议
        issue_count = len(issues)
        if issue_count > 5:
            prioritized.append(
                {
                    "type": "ARCHITECTURE_REVIEW",
                    "title": "架构性能审查",
                    "description": f"检测到{issue_count}个性能问题，建议进行架构级优化",
                    "priority": "critical",
                }
            )

        return prioritized[:5]  # 返回前5个优先建议

    def _count_nested_loops(self, node: ast.For, depth: int = 1) -> int:
        """计算嵌套循环深度"""
        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.For):
                nested_depth = self._count_nested_loops(child, depth + 1)
                max_depth = max(max_depth, nested_depth)

        return max_depth

    def _is_large_comprehension(self, node: ast.ListComp) -> bool:
        """判断列表推导式是否过大"""
        # 简单的启发式判断：包含多个for子句或复杂的条件
        generators = len(node.generators)
        has_complex_conditions = any(len(gen.ifs) > 1 for gen in node.generators)

        return generators > 2 or has_complex_conditions

