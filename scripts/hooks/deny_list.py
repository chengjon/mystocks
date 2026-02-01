#!/usr/bin/env python3
"""Deny/ignore rules for repository structure checks.

This module is imported by `scripts/hooks/check_directory_structure.py`.

The intent is to:
- Block obviously wrong locations (e.g. duplicated nesting like `docs/docs/`).
- Ignore generated artifacts (caches, node_modules, etc.).

It is NOT intended to forbid edits to existing legacy areas; enforcement is applied
only to newly-added files in the caller.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Rule:
    action: str
    reason: str
    prefix: str | None = None
    path: str | None = None
    pattern: str | None = None


DENIED: list[Rule] = [
    Rule(prefix="src/temp/", action="禁止创建", reason="临时目录不应提交到版本库"),
    Rule(prefix="docs/docs/", action="禁止创建", reason="文档目录不应重复嵌套"),
    Rule(path=".env", action="禁止创建", reason="敏感环境变量文件禁止提交"),
    Rule(prefix="docs/test_reports/", action="禁止创建", reason="测试报告属于生成物，禁止提交"),
    Rule(prefix="docs/api/openapi/", action="禁止创建", reason="OpenAPI 生成物应作为构建产物，禁止提交"),
    # Common generated artifacts (deny anywhere)
    Rule(pattern="**/*.log", action="禁止提交", reason="日志文件属于生成物，禁止提交"),
    Rule(pattern="**/*.tmp", action="禁止提交", reason="临时文件属于生成物，禁止提交"),
    Rule(pattern="**/*.bak", action="禁止提交", reason="备份文件属于生成物，禁止提交"),
    Rule(pattern="**/*.swp", action="禁止提交", reason="编辑器交换文件属于生成物，禁止提交"),
    Rule(pattern="**/*.swo", action="禁止提交", reason="编辑器交换文件属于生成物，禁止提交"),
    Rule(pattern="*~", action="禁止提交", reason="编辑器备份文件属于生成物，禁止提交"),
    Rule(pattern="**/*~", action="禁止提交", reason="编辑器备份文件属于生成物，禁止提交"),
    # Secrets / certificates (deny anywhere)
    Rule(pattern="**/*.key", action="禁止提交", reason="密钥文件禁止提交"),
    Rule(pattern="**/*.pem", action="禁止提交", reason="证书/密钥文件禁止提交"),
    Rule(pattern="**/*.pfx", action="禁止提交", reason="证书文件禁止提交"),
    Rule(pattern="**/*.p12", action="禁止提交", reason="证书文件禁止提交"),
    Rule(pattern="**/*.crt", action="禁止提交", reason="证书文件禁止提交"),
    Rule(pattern="**/*.csr", action="禁止提交", reason="证书请求文件禁止提交"),
    # DB / archive binaries (deny anywhere)
    Rule(pattern="**/*.db", action="禁止提交", reason="数据库文件通常为生成物/数据文件，禁止提交"),
    Rule(pattern="**/*.sqlite", action="禁止提交", reason="数据库文件通常为生成物/数据文件，禁止提交"),
    Rule(pattern="**/*.sqlite3", action="禁止提交", reason="数据库文件通常为生成物/数据文件，禁止提交"),
    Rule(pattern="**/*.zip", action="禁止提交", reason="压缩包通常为生成物，禁止提交"),
    Rule(pattern="**/*.tar", action="禁止提交", reason="归档文件通常为生成物，禁止提交"),
    Rule(pattern="**/*.tar.gz", action="禁止提交", reason="归档文件通常为生成物，禁止提交"),
    Rule(pattern="**/*.tgz", action="禁止提交", reason="归档文件通常为生成物，禁止提交"),
    # Generated directories (deny anywhere)
    Rule(pattern="node_modules/**", action="禁止提交", reason="node_modules 属于依赖目录，禁止提交"),
    Rule(pattern="**/node_modules/**", action="禁止提交", reason="node_modules 属于依赖目录，禁止提交"),
    Rule(pattern="__pycache__/**", action="禁止提交", reason="Python 缓存目录禁止提交"),
    Rule(pattern="**/__pycache__/**", action="禁止提交", reason="Python 缓存目录禁止提交"),
    Rule(pattern=".pytest_cache/**", action="禁止提交", reason="pytest 缓存目录禁止提交"),
    Rule(pattern="**/.pytest_cache/**", action="禁止提交", reason="pytest 缓存目录禁止提交"),
    Rule(pattern=".mypy_cache/**", action="禁止提交", reason="MyPy 缓存目录禁止提交"),
    Rule(pattern="**/.mypy_cache/**", action="禁止提交", reason="MyPy 缓存目录禁止提交"),
    Rule(pattern=".ruff_cache/**", action="禁止提交", reason="Ruff 缓存目录禁止提交"),
    Rule(pattern="**/.ruff_cache/**", action="禁止提交", reason="Ruff 缓存目录禁止提交"),
]

IGNORED: list[Rule] = [
    Rule(pattern="**/__pycache__/**", action="忽略", reason="Python 缓存目录"),
    Rule(pattern="**/.pytest_cache/**", action="忽略", reason="pytest 缓存目录"),
    Rule(pattern="**/.ruff_cache/**", action="忽略", reason="Ruff 缓存目录"),
    Rule(pattern="**/.mypy_cache/**", action="忽略", reason="MyPy 缓存目录"),
    Rule(pattern="**/node_modules/**", action="忽略", reason="Node.js 依赖目录"),
    Rule(pattern="**/.git/**", action="忽略", reason="Git 目录"),
    Rule(pattern="**/.DS_Store", action="忽略", reason="macOS 元数据文件"),
    Rule(pattern="**/*.pyc", action="忽略", reason="Python 编译产物"),
    Rule(pattern="**/.claude-trace/**", action="忽略", reason="Claude trace 目录"),
    Rule(pattern="**/.opencode/**", action="忽略", reason="OpenCode 工作目录"),
    Rule(pattern="**/.specify/**", action="忽略", reason="Specify 工具目录"),
]


def is_denied_path(path: str) -> tuple[bool, dict[str, Any]]:
    """Return (denied, info).

    `info` matches the shape expected by the caller:
    - action: str
    - reason: str
    """

    for rule in DENIED:
        if rule.path is not None and path == rule.path:
            return True, {"action": rule.action, "reason": rule.reason}
        if rule.prefix is not None and path.startswith(rule.prefix):
            return True, {"action": rule.action, "reason": rule.reason}
        if rule.pattern is not None and fnmatch.fnmatch(path, rule.pattern):
            return True, {"action": rule.action, "reason": rule.reason}
    return False, {}


def should_ignore(path: str) -> tuple[bool, dict[str, Any]]:
    """Return (ignored, info)."""

    for rule in IGNORED:
        if rule.pattern is not None and fnmatch.fnmatch(path, rule.pattern):
            return True, {"action": rule.action, "reason": rule.reason}
    return False, {}
