"""Performance analysis helpers for `ai_validator.py`."""

from __future__ import annotations

import ast


class AIValidatorPerformanceAnalysisMixin:
    """AI 校验器的性能分析尾部方法集。"""

    def _analyze_performance_patterns(self, tree: ast.AST) -> list:
        """通过AST分析性能反模式"""
        issues = []

        for node in ast.walk(tree):
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
                        },
                    )
            elif isinstance(node, ast.ListComp) and self._is_large_comprehension(node):
                issues.append(
                    {
                        "file": "current_file",
                        "category": "MEMORY",
                        "type": "大型列表推导式可能消耗大量内存",
                        "severity": "medium",
                        "suggestion": "考虑使用生成器表达式或分批处理",
                        "line_number": getattr(node, "lineno", 0),
                    },
                )

        return issues

    def _generate_performance_suggestions(self, content: str, lines: list, file_path: str) -> list:
        """生成具体的性能优化建议"""
        suggestions = []

        if "import pandas as pd" in content and "pd.read_csv" in content:
            suggestions.append(
                {
                    "file": file_path,
                    "type": "IO_OPTIMIZATION",
                    "title": "Pandas读取优化",
                    "description": "使用chunksize参数分块读取大文件",
                    "code_example": "pd.read_csv('large_file.csv', chunksize=10000)",
                    "impact": "high",
                },
            )

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
                },
            )

        return suggestions

    def _calculate_performance_score(self, issues: list, files_analyzed: int) -> float:
        """计算性能优化评分"""
        if files_analyzed == 0:
            return 100.0

        base_score = 100.0
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "high":
                base_score -= 8
            elif severity == "medium":
                base_score -= 4
            else:
                base_score -= 1

        return max(0.0, min(100.0, base_score))

    def _prioritize_optimizations(self, suggestions: list, issues: list) -> list:
        """优先排序优化建议"""
        prioritized = []

        high_impact = [suggestion for suggestion in suggestions if suggestion.get("impact") == "high"]
        prioritized.extend(high_impact)

        medium_impact = [suggestion for suggestion in suggestions if suggestion.get("impact") == "medium"]
        prioritized.extend(medium_impact)

        issue_count = len(issues)
        if issue_count > 5:
            prioritized.append(
                {
                    "type": "ARCHITECTURE_REVIEW",
                    "title": "架构性能审查",
                    "description": f"检测到{issue_count}个性能问题，建议进行架构级优化",
                    "priority": "critical",
                },
            )

        return prioritized[:5]

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
        generators = len(node.generators)
        has_complex_conditions = any(len(generator.ifs) > 1 for generator in node.generators)

        return generators > 2 or has_complex_conditions
