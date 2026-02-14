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


class CoreAnalyzerMixin:
    """核心分析器：初始化、文件读取、分析编排"""

    def __init__(self, project_root: str = "/opt/claude/mystocks_spec"):
        self.project_root = Path(project_root)
        self.issues = defaultdict(list)
        self.stats = {
            "total_files": 0,
            "python_files": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
        }

    async def _read_file_content_async(self, file_path: Path) -> str:
        """异步读取文件内容"""
        async with aiofiles.open(
            file_path, "r", encoding="utf-8", errors="ignore"
        ) as f:
            content = await f.read()
        return content

    async def analyze_all(self) -> Dict[str, Any]:
        """执行全面的技术负债分析"""
        logger.info("开始技术负债分析...")

        # 1. 代码质量分析
        await self.analyze_code_quality()

        # 2. 架构债务分析
        await self.analyze_architecture_debt()

        # 3. 性能问题分析
        await self.analyze_performance_issues()

        # 4. 安全问题分析
        await self.analyze_security_issues()

        # 5. 依赖问题分析
        await self.analyze_dependency_issues()

        # 6. 测试覆盖分析
        await self.analyze_test_coverage()

        # 7. 文档问题分析
        await self.analyze_documentation_issues()

        # 8. 配置管理问题分析
        await self.analyze_configuration_issues()

        return {
            "analysis_summary": self.generate_summary(),
            "detailed_issues": dict(self.issues),
            "recommendations": self.generate_recommendations(),
            "technical_debt_score": self.calculate_debt_score(),
            "priority_actions": self.get_priority_actions(),
        }

