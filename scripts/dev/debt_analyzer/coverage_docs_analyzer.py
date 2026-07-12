"""技术负债分析器子模块"""

import ast
import asyncio
import logging
import re
from pathlib import Path


logger = logging.getLogger(__name__)


class CoverageDocsMixin:
    """测试覆盖、文档质量、配置问题分析"""

    async def analyze_test_coverage(self):
        """分析测试覆盖"""
        logger.info("分析测试覆盖...")

        # 查找测试文件
        test_files = list(self.project_root.rglob("test_*.py"))
        test_files.extend(list(self.project_root.rglob("*_test.py")))
        test_files.extend(list(self.project_root.rglob("tests/**/*.py")))

        # 查找源代码文件
        source_files = [
            f for f in list(self.project_root.rglob("*.py")) if not self._should_skip_file(f) and "test" not in str(f)
        ]

        test_to_source_ratio = len(test_files) / max(len(source_files), 1)

        if test_to_source_ratio < 0.1:  # 测试文件比例小于10%
            self.issues["test_issues"].append(
                {
                    "issue": "low_test_coverage_ratio",
                    "test_files": len(test_files),
                    "source_files": len(source_files),
                    "ratio": test_to_source_ratio,
                    "category": "testing",
                    "severity": "high",
                },
            )

        # 检查是否有e2e测试
        e2e_files = list(self.project_root.rglob("e2e/**/*.py"))
        if not e2e_files:
            self.issues["test_issues"].append(
                {
                    "issue": "missing_e2e_tests",
                    "category": "testing",
                    "severity": "medium",
                },
            )

        # 检查测试配置
        pytest_ini = self.project_root / "pytest.ini"
        if not pytest_ini.exists():
            self.issues["test_issues"].append(
                {
                    "issue": "missing_pytest_config",
                    "category": "testing",
                    "severity": "low",
                },
            )

    async def analyze_documentation_issues(self):
        """分析文档问题"""
        logger.info("分析文档问题...")

        # 统计文档文件
        doc_files = {
            "markdown": list(self.project_root.rglob("*.md")),
            "rst": list(self.project_root.rglob("*.rst")),
            "txt": list(self.project_root.rglob("*.txt")),
        }

        total_doc_files = sum(len(files) for files in doc_files.values())

        # 检查README文件
        readme_files = list(self.project_root.rglob("README*"))
        if not readme_files:
            self.issues["documentation_issues"].append(
                {
                    "issue": "missing_readme",
                    "category": "documentation",
                    "severity": "high",
                },
            )

        # 检查API文档
        if "docs/api" not in [str(d) for d in self.project_root.rglob("docs/api")]:
            self.issues["documentation_issues"].append(
                {
                    "issue": "missing_api_docs",
                    "category": "documentation",
                    "severity": "medium",
                },
            )

        # 检查docstrings覆盖率
        python_files = [f for f in list(self.project_root.rglob("*.py")) if not self._should_skip_file(f)]

        files_without_docstrings = 0

        async def check_docstring_for_file(py_file: Path):
            nonlocal files_without_docstrings  # Declare as nonlocal
            try:
                content = await self._read_file_content_async(py_file)
                tree = ast.parse(content)

                has_docstring = False
                if (
                    isinstance(tree, ast.Module)
                    and tree.body
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                    and isinstance(tree.body[0].value.value, str)
                ):
                    has_docstring = True

                if not has_docstring:
                    files_without_docstrings += 1
            except Exception as e:
                logger.warning(f"检查docstring失败 {py_file}: {e}")

        await asyncio.gather(*[check_docstring_for_file(f) for f in python_files])

        if files_without_docstrings > len(python_files) * 0.7:  # 超过70%的文件没有docstring
            self.issues["documentation_issues"].append(
                {
                    "issue": "low_docstring_coverage",
                    "files_without_docstrings": files_without_docstrings,
                    "total_files": len(python_files),
                    "ratio": files_without_docstrings / len(python_files),
                    "category": "documentation",
                    "severity": "medium",
                },
            )

    async def analyze_configuration_issues(self):
        """分析配置管理问题"""
        logger.info("分析配置管理问题...")

        # 检查硬编码配置
        python_files = list(self.project_root.rglob("*.py"))

        async def process_config_for_file(py_file: Path):
            if self._should_skip_file(py_file):
                return

            try:
                content = await self._read_file_content_async(py_file)

                # 检查硬编码配置
                if re.search(r'=\s*["\'][^"\']*[\d\.]+["\']', content):  # 硬编码数字
                    self.issues["configuration_issues"].append(
                        {
                            "file": str(py_file),
                            "issue": "hardcoded_numbers",
                            "category": "configuration",
                            "severity": "medium",
                        },
                    )

                if re.search(
                    r'=\s*["\'][^"\']*(?:localhost|127\.0\.0\.1|3306|5432)["\']',
                    content,
                ):
                    self.issues["configuration_issues"].append(
                        {
                            "file": str(py_file),
                            "issue": "hardcoded_config",
                            "category": "configuration",
                            "severity": "high",
                        },
                    )

            except Exception as e:
                logger.warning(f"分析配置问题失败 {py_file}: {e}")

        await asyncio.gather(*[process_config_for_file(f) for f in python_files])

        # 检查环境变量使用
        env_vars_used = False
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
            try:
                content = await self._read_file_content_async(py_file)  # await here
                if "os.environ" in content or "getenv" in content:
                    env_vars_used = True
                    break
            except Exception as e:
                logger.warning(f"检查环境变量使用失败 {py_file}: {e}")

        if not env_vars_used:
            self.issues["configuration_issues"].append(
                {
                    "issue": "no_environment_variables",
                    "category": "configuration",
                    "severity": "medium",
                },
            )
