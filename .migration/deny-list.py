#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
禁止移动列表配置

定义在迁移过程中禁止移动的文件/目录
"""

deny_list = {
    "directories": [
        {
            "path": "src/temp/",
            "reason": "临时文件目录，需要先清理",
            "action": "检查后决定是否删除",
        },
        {"path": ".git/", "reason": "Git 版本控制目录", "action": "禁止移动"},
        {"path": ".github/", "reason": "CI/CD 配置目录", "action": "禁止移动"},
        {"path": ".claude/", "reason": "Claude Code 配置", "action": "禁止移动"},
        {"path": ".opencode/", "reason": "OpenCode 配置", "action": "禁止移动"},
        {"path": ".archive/", "reason": "归档目录", "action": "禁止移动"},
        {"path": "backups/", "reason": "备份目录", "action": "禁止移动"},
        {"path": "config/", "reason": "配置目录", "action": "禁止移动"},
        {"path": "data/", "reason": "数据目录", "action": "禁止移动"},
        {"path": "logs/", "reason": "日志目录", "action": "禁止移动"},
        {"path": "reports/", "reason": "报告目录", "action": "禁止移动"},
        {"path": "web/", "reason": "Web 应用目录", "action": "禁止移动"},
        {"path": "tests/", "reason": "测试目录", "action": "禁止移动"},
        {"path": "temp/", "reason": "临时目录", "action": "禁止移动"},
    ],
    "files": [
        {"path": ".gitignore", "reason": "Git 配置文件", "action": "禁止移动"},
        {"path": ".env", "reason": "环境变量文件（敏感）", "action": "禁止移动"},
        {"path": ".env.example", "reason": "环境变量示例文件", "action": "禁止移动"},
        {"path": "README.md", "reason": "项目主文档", "action": "禁止移动"},
        {"path": "CLAUDE.md", "reason": "Claude Code 配置文档", "action": "禁止移动"},
        {"path": "IFLOW.md", "reason": "IFLOW 文档", "action": "禁止移动"},
        {"path": "GEMINI.md", "reason": "Gemini CLI 文档", "action": "禁止移动"},
        {"path": "AGENTS.md", "reason": "OpenSpec 文档", "action": "禁止移动"},
        {"path": "core.py", "reason": "根目录入口文件", "action": "禁止移动"},
        {"path": "data_access.py", "reason": "根目录入口文件", "action": "禁止移动"},
        {"path": "monitoring.py", "reason": "根目录入口文件", "action": "禁止移动"},
        {
            "path": "unified_manager.py",
            "reason": "根目录入口文件",
            "action": "禁止移动",
        },
    ],
    "special_cases": [
        {"pattern": "**/__pycache__/", "action": "忽略", "reason": "Python 缓存目录"},
        {"pattern": "**/.pytest_cache/", "action": "忽略", "reason": "测试缓存目录"},
        {"pattern": "**/.ruff_cache/", "action": "忽略", "reason": "Ruff 缓存目录"},
        {"pattern": "**/.mypy_cache/", "action": "忽略", "reason": "MyPy 缓存目录"},
        {"pattern": "**/node_modules/", "action": "忽略", "reason": "Node.js 依赖目录"},
        {"pattern": "**/.git/", "action": "忽略", "reason": "Git 目录"},
    ],
}


def is_denied_path(path):
    """检查路径是否在禁止列表中"""
    path_str = str(path)

    for item in deny_list["directories"]:
        if path_str.startswith(item["path"]):
            return True, item

    for item in deny_list["files"]:
        if path_str == item["path"]:
            return True, item

    return False, None


def should_ignore(path):
    """检查路径是否应该忽略"""
    import fnmatch

    for item in deny_list["special_cases"]:
        if fnmatch.fnmatch(path, item["pattern"]):
            return True, item

    return False, None


if __name__ == "__main__":
    test_paths = [
        "src/temp/",
        ".git/config",
        "src/core/__init__.py",
        "tests/unit/test_core.py",
    ]

    for path in test_paths:
        denied, info = is_denied_path(path)
        ignored, ignore_info = should_ignore(path)

        if denied:
            print(f"🚫 {path} - 禁止移动: {info['reason']}")
        elif ignored:
            print(f"⏭️ {path} - 忽略: {ignore_info['reason']}")
        else:
            print(f"✅ {path} - 允许")
