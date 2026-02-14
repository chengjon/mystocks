"""技术负债分析器子模块"""

import ast
import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List
import asyncio
import aiofiles

logger = logging.getLogger(__name__)


class ReportMixin:
    """报告生成：摘要、建议、评分、优先行动"""

    def generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        total_issues = sum(len(issues) for issues in self.issues.values())

        category_counts = defaultdict(int)
        severity_counts = defaultdict(int)

        for category, issues in self.issues.items():
            category_counts[category] = len(issues)
            for issue in issues:
                severity_counts[issue.get("severity", "unknown")] += 1

        return {
            "total_issues": total_issues,
            "categories": dict(category_counts),
            "severities": dict(severity_counts),
            "project_stats": dict(self.stats),
            "analysis_date": "2025-11-25",
        }

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []

        # 基于发现的问题生成建议
        if len(self.issues["long_functions"]) > 10:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "code_quality",
                    "title": "重构长函数",
                    "description": f"发现{len(self.issues['long_functions'])}个过长函数，建议进行重构",
                    "actions": [
                        "将长函数拆分为多个小函数",
                        "提取公共逻辑到独立函数",
                        "使用装饰器简化横切关注点",
                    ],
                }
            )

        if len(self.issues["security_issues"]) > 0:
            recommendations.append(
                {
                    "priority": "critical",
                    "category": "security",
                    "title": "修复安全漏洞",
                    "description": f"发现{len(self.issues['security_issues'])}个安全问题，需要立即处理",
                    "actions": [
                        "移除硬编码的密钥和密码",
                        "使用环境变量管理敏感配置",
                        "实施输入验证和SQL注入防护",
                    ],
                }
            )

        if len(self.issues["test_issues"]) > 0:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "testing",
                    "title": "提高测试覆盖率",
                    "description": "测试覆盖率不足，建议增加单元测试和集成测试",
                    "actions": [
                        "为关键业务逻辑编写单元测试",
                        "实施自动化测试",
                        "增加端到端测试",
                    ],
                }
            )

        return recommendations

    def calculate_debt_score(self) -> float:
        """计算技术负债评分（0-100，100为无负债）"""
        score = 100.0

        # 根据问题数量和严重程度扣分
        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}

        total_deduction = 0
        for category, issues in self.issues.items():
            for issue in issues:
                severity = issue.get("severity", "low")
                weight = severity_weights.get(severity, 1)
                total_deduction += weight

        # 根据代码行数调整评分
        # Need to ensure stats['code_lines'] is accurate when collected asynchronously
        if self.stats["total_lines"] > 100000:  # Use total_lines for now
            total_deduction *= 1.5
        elif self.stats["total_lines"] > 50000:
            total_deduction *= 1.2

        score = max(0, 100 - total_deduction)
        return round(score, 2)

    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """获取优先处理行动"""
        actions = []

        # 按严重程度排序所有问题
        all_issues = []
        for category, issues in self.issues.items():
            for issue in issues:
                all_issues.append({**issue, "category": category})

        all_issues.sort(
            key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(
                x.get("severity", "low"), 1
            ),
            reverse=True,
        )

        # 取前10个最严重的问题
        for issue in all_issues[:10]:
            actions.append(
                {
                    "priority": issue.get("severity", "low"),
                    "category": issue["category"],
                    "file": issue.get("file", "N/A"),
                    "issue": issue.get("issue", issue.get("category", "unknown")),
                    "description": f"在{issue.get('file', '未知文件')}中发现{issue.get('issue', '问题')}",
                }
            )

        return actions


