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


class DependencyMixin:
    """依赖分析：requirements、Docker、package.json"""

    async def analyze_dependency_issues(self):
        """分析依赖问题"""
        logger.info("分析依赖问题...")

        # 分析requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            await self._analyze_requirements_async(requirements_file)

        # 分析Docker依赖
        dockerfiles = list(self.project_root.rglob("Dockerfile*"))
        await asyncio.gather(
            *[self._analyze_docker_dependencies_async(f) for f in dockerfiles]
        )

        # 分析package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            await self._analyze_package_json_async(package_json)

    async def _analyze_requirements_async(self, requirements_file: Path):
        """分析requirements.txt"""
        try:
            content = await self._read_file_content_async(requirements_file)
            lines = content.splitlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # 检查版本固定
                    if "==" not in line and ">=" not in line and "<=" not in line:
                        self.issues["dependency_issues"].append(
                            {
                                "file": str(requirements_file),
                                "package": line,
                                "issue": "unpinned_version",
                                "category": "dependencies",
                                "severity": "medium",
                            }
                        )
        except Exception as e:
            logger.warning(f"分析requirements.txt失败: {e}")

    async def _analyze_docker_dependencies_async(self, dockerfile: Path):
        """分析Docker依赖"""
        try:
            content = await self._read_file_content_async(dockerfile)

            # 检查latest标签使用
            if re.search(r"FROM\s+[\w/:-]+:latest", content, re.IGNORECASE):
                self.issues["dependency_issues"].append(
                    {
                        "file": str(dockerfile),
                        "issue": "using_latest_tag",
                        "category": "dependencies",
                        "severity": "low",
                    }
                )
        except Exception as e:
            logger.warning(f"分析Dockerfile失败 {dockerfile}: {e}")

    async def _analyze_package_json_async(self, package_json: Path):
        """分析package.json"""
        try:
            content = await self._read_file_content_async(package_json)
            data = json.loads(content)

            # 检查devDependencies和dependencies的版本固定
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in data:
                    for package, version in data[dep_type].items():
                        if (
                            version == "*"
                            or version == "latest"
                            or not re.match(r"^\d+\.\d+\.\d+$", version)
                        ):  # Also check for ~ ^ versions
                            self.issues["dependency_issues"].append(
                                {
                                    "file": str(package_json),
                                    "package": package,
                                    "version": version,
                                    "issue": "unpinned_version",
                                    "dependency_type": dep_type,
                                    "category": "dependencies",
                                    "severity": "medium",
                                }
                            )
        except Exception as e:
            logger.warning(f"分析package.json失败: {e}")

