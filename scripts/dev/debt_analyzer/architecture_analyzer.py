"""技术负债分析器子模块"""

import ast
import asyncio
import logging
from collections import defaultdict
from pathlib import Path


logger = logging.getLogger(__name__)


class ArchitectureMixin:
    """架构债务分析：耦合度、循环依赖"""

    async def analyze_architecture_debt(self):
        """分析架构债务"""
        logger.info("分析架构债务...")

        # 分析模块耦合
        await self._analyze_coupling_async()

        # 分析违反单一职责原则
        self.issues["architecture_concerns"].append(
            {
                "category": "architecture",
                "issue": "单一职责原则需要进一步分析",
                "severity": "medium",
                "recommendation": "建议进行更深入的架构分析",
            },
        )

        # 分析循环依赖
        await self._analyze_circular_dependencies_async()

        # 分析依赖倒置
        self.issues["architecture_concerns"].append(
            {
                "category": "architecture",
                "issue": "依赖注入模式使用情况需要评估",
                "severity": "medium",
                "recommendation": "检查是否应该使用依赖注入容器",
            },
        )

    async def _analyze_coupling_async(self):
        """分析模块耦合"""
        import_graph = defaultdict(set)

        python_files = list(self.project_root.rglob("*.py"))

        async def analyze_imports_for_file(py_file: Path):
            if self._should_skip_file(py_file):
                return

            try:
                content = await self._read_file_content_async(py_file)
                tree = ast.parse(content)

                # 分析导入依赖
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_graph[str(py_file)].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        import_graph[str(py_file)].add(module)
            except Exception as e:
                logger.warning(f"分析文件导入依赖失败 {py_file}: {e}")

        await asyncio.gather(*[analyze_imports_for_file(f) for f in python_files])

        # 找出高耦合模块
        for module, deps in import_graph.items():
            if len(deps) > 20:  # 依赖超过20个模块
                self.issues["high_coupling"].append(
                    {
                        "file": module,
                        "dependency_count": len(deps),
                        "dependencies": list(deps),
                        "category": "architecture",
                        "severity": "high",
                    },
                )

    async def _analyze_circular_dependencies_async(self):
        """分析循环依赖"""
        # 简化的循环依赖检测
        python_files = [f for f in list(self.project_root.rglob("*.py")) if not self._should_skip_file(f)]

        # 构建依赖图
        dependencies = defaultdict(set)

        async def collect_dependencies_for_file(py_file: Path):
            try:
                content = await self._read_file_content_async(py_file)
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module
                        if module and (
                            module.startswith("src.") or module.startswith("web.backend.app.")
                        ):  # Consider project-specific modules
                            dependencies[str(py_file)].add(module)
            except Exception as e:
                logger.warning(f"收集文件依赖失败 {py_file}: {e}")

        await asyncio.gather(*[collect_dependencies_for_file(f) for f in python_files])

        # 简化检测循环依赖（需要更复杂算法）
        self.issues["architecture_concerns"].append(
            {
                "category": "architecture",
                "issue": "循环依赖检测需要完善",
                "severity": "medium",
                "recommendation": "建议使用专业工具如pycircular进行检测",
            },
        )
