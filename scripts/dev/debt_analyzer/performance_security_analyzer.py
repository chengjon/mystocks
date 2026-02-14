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


class PerformanceSecurityMixin:
    """性能与安全分析：N+1查询、同步IO、内存操作、硬编码密钥、SQL注入"""

    async def analyze_performance_issues(self):
        """分析性能问题"""
        logger.info("分析性能问题...")

        python_files = list(self.project_root.rglob("*.py"))

        async def process_performance_for_file(py_file: Path):
            if self._should_skip_file(py_file):
                return

            try:
                content = await self._read_file_content_async(py_file)

                # 检查常见的性能反模式
                self._check_n_plus_one_queries(py_file, content)
                self._check_synchronous_io(py_file, content)
                self._check_memory_intensive_operations(py_file, content)
                self._check_inefficient_data_structures(py_file, content)

            except Exception as e:
                logger.warning(f"分析性能问题失败 {py_file}: {e}")

        await asyncio.gather(*[process_performance_for_file(f) for f in python_files])

    def _check_n_plus_one_queries(self, file_path: Path, content: str):
        """检查N+1查询问题"""
        # 查找数据库查询模式
        query_patterns = [
            r"\.query\s*\(",
            r"\.execute\s*\(",
            r"\.fetch\s*\(",
            r"sql\.execute",
        ]

        for pattern in query_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if len(matches) > 5:  # 超过5个查询可能有问题
                self.issues["performance_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "potential_n_plus_one",
                        "query_count": len(matches),
                        "category": "performance",
                        "severity": "medium",
                    }
                )
                break

    def _check_synchronous_io(self, file_path: Path, content: str):
        """检查同步I/O操作"""
        sync_patterns = [
            r"requests\.get\s*\(",
            r"requests\.post\s*\(",
            r"(?<!a)open\s*\(",  # Exclude aiofiles.open
            r"file\.read\s*\(",
        ]

        for pattern in sync_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues["performance_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "synchronous_io",
                        "pattern": pattern,
                        "category": "performance",
                        "severity": "low",
                    }
                )
                break

    def _check_memory_intensive_operations(self, file_path: Path, content: str):
        """检查内存密集型操作"""
        memory_patterns = [
            r"\.read\s*\(\)",
            r"json\.loads\s*\(",
            r"eval\s*\(",
        ]

        for pattern in memory_patterns:
            if re.search(pattern, content):
                self.issues["performance_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "memory_intensive",
                        "pattern": pattern,
                        "category": "performance",
                        "severity": "medium",
                    }
                )
                break

    def _check_inefficient_data_structures(self, file_path: Path, content: str):
        """检查低效数据结构"""
        # 检查是否使用list作为dictionary的key
        if "list(" in content and "dict(" in content:
            self.issues["performance_issues"].append(
                {
                    "file": str(file_path),
                    "issue": "inefficient_data_structure",
                    "category": "performance",
                    "severity": "low",
                }
            )

    async def analyze_security_issues(self):
        """分析安全问题"""
        logger.info("分析安全问题...")

        python_files = list(self.project_root.rglob("*.py"))

        async def process_security_for_file(py_file: Path):
            if self._should_skip_file(py_file):
                return

            try:
                content = await self._read_file_content_async(py_file)

                # 检查常见安全漏洞
                self._check_hardcoded_secrets(py_file, content)
                self._check_sql_injection(py_file, content)
                self._check_insecure_file_operations(py_file, content)
                self._check_unsafe_eval(py_file, content)

            except Exception as e:
                logger.warning(f"分析安全问题失败 {py_file}: {e}")

        await asyncio.gather(*[process_security_for_file(f) for f in python_files])

    def _check_hardcoded_secrets(self, file_path: Path, content: str):
        """检查硬编码密钥"""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
        ]

        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                self.issues["security_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "hardcoded_secret",
                        "matches": matches[:3],  # 只记录前3个
                        "category": "security",
                        "severity": "high",
                    }
                )
                break

    def _check_sql_injection(self, file_path: Path, content: str):
        """检查SQL注入风险"""
        sql_patterns = [
            r'\.execute\s*\(\s*["\'].*%.*["\'].*\)',
            r'cursor\.execute\s*\(\s*f["\'].*\{{.*\}}.*["\'].*\)',
        ]

        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues["security_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "sql_injection_risk",
                        "category": "security",
                        "severity": "high",
                    }
                )
                break

    def _check_insecure_file_operations(self, file_path: Path, content: str):
        """检查不安全的文件操作"""
        insecure_patterns = [
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(",
            r"(?<!a)exec\s*\(",  # Exclude aiofiles related exec or similar
            r"(?<!a)eval\s*\(",  # Exclude aiofiles related eval or similar
        ]

        for pattern in insecure_patterns:
            if re.search(pattern, content):
                self.issues["security_issues"].append(
                    {
                        "file": str(file_path),
                        "issue": "insecure_file_operation",
                        "pattern": pattern,
                        "category": "security",
                        "severity": "medium",
                    }
                )
                break

    def _check_unsafe_eval(self, file_path: Path, content: str):
        """检查不安全的eval使用"""
        if re.search(
            r"(?<!a)eval\(", content
        ):  # Exclude aiofiles related eval or similar
            self.issues["security_issues"].append(
                {
                    "file": str(file_path),
                    "issue": "unsafe_eval",
                    "category": "security",
                    "severity": "high",
                }
            )

