#!/usr/bin/env python3
"""
上报 Hooks 配置修复问题到 BUGer 系统
"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BUGER_API_URL = os.getenv("BUGER_API_URL", "http://localhost:3030/api")
BUGER_API_KEY = os.getenv("BUGER_API_KEY", "sk_test_xyz123")
PROJECT_ID = os.getenv("PROJECT_ID", "mystocks")
PROJECT_NAME = os.getenv("PROJECT_NAME", "MyStocks")
PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/opt/claude/mystocks_spec")


def report_bug_to_bugger(bug_data):
    """上报单个 bug 到 BUGer"""
    url = f"{BUGER_API_URL}/bugs"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": BUGER_API_KEY
    }

    # 构建符合 BUGer API 要求的 payload
    # 注意：project 字段由 API 根据认证信息自动填充，不应由客户端提供
    payload = {
        "errorCode": bug_data["errorCode"],
        "title": bug_data["title"],
        "message": bug_data["message"],
        "severity": bug_data.get("severity", "medium"),
        "stackTrace": bug_data.get("stackTrace", ""),
        "context": {
            "project_name": bug_data["context"]["project_name"],
            "project_root": bug_data["context"]["project_root"],
            "component": bug_data["context"].get("component", "unknown"),
            "module": bug_data["context"].get("module", ""),
            "file": bug_data["context"].get("file", ""),
            "status": "OPEN"
        }
    }

    # 添加 tags（如果存在）
    if "tags" in bug_data:
        payload["context"]["tags"] = bug_data["tags"]

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        print(f"❌ 上报失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   响应内容: {e.response.text}")
        return None


def main():
    """上报所有 hooks 配置问题"""

    print("=" * 80)
    print("📋 上报 Hooks 配置问题到 BUGer 系统")
    print("=" * 80)
    print(f"API URL: {BUGER_API_URL}")
    print(f"Project: {PROJECT_NAME} ({PROJECT_ID})")
    print()

    # 问题 1: Pre-commit 配置违规
    bug1 = {
        "errorCode": "HOOKS_CONFIG_001",
        "title": "Pre-commit 配置不符合官方规范 - Ruff 与 Black 冲突",
        "message": """
问题描述：
- Ruff 运行 3 次（冗余配置）
- Black 和 Ruff 格式化冲突
- 执行时间过长 (20-30s)

根本原因：
- 使用了 ruff format（与 Black 冲突）
- 使用了 --fix 无差别修复（回退 Black 的格式）
- 未遵循 "Black 先行 + Ruff 补充" 的最佳实践

影响范围：
- 提交前检查性能降低 60-75%
- 可能导致格式不一致
- 开发体验受损

修复方案：
1. Black 先行（强制格式化所有代码）
2. Ruff 补充修复（只修复 F401/F841 问题）
3. Ruff 最终检查（确保没有遗漏）

关键避坑点：
- ❌ 不使用 ruff format
- ❌ 不使用 --fix 无差别修复
- ✅ 使用 --select F401,F841 --fix 选择性修复
        """,
        "severity": "medium",
        "stackTrace": ".pre-commit-config.yaml: Ruff 配置冲突",
        "context": {
            "project_name": PROJECT_NAME,
            "project_id": PROJECT_ID,
            "project_root": PROJECT_ROOT,
            "component": "CI/CD",
            "module": "pre-commit-hooks",
            "file": ".pre-commit-config.yaml",
            "configuration": r"""
修复前：
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]  # ❌ 无差别修复

修复后：
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black  # ✅ Black 先行
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--select, F401,F841, --fix]  # ✅ 选择性修复
            """
        },
        "tags": ["pre-commit", "ruff", "black", "configuration", "performance"]
    }

    # 问题 2: 安全 Hooks 配置违规
    bug2 = {
        "errorCode": "HOOKS_CONFIG_002",
        "title": "安全 Hooks 配置违反 Git Hooks 官方规范",
        "message": """
问题描述：
- 所有 hooks 使用 pass_filenames: false + files（冲突配置）
- 所有 hooks 使用 always_run: true（性能浪费）
- 大量冗余工具配置（Black, isort, flake8 重复）

根本原因：
- 违反 Git Hooks 官方规范
- pass_filenames: false 表示不接收文件列表（用于全局扫描）
- files 表示只对匹配文件运行（用于文件级检查）
- 两者混用导致 pre-commit 无法判断何时运行

影响范围：
- 即使只修改文档，也会运行所有安全扫描（性能浪费）
- 配置不符合官方规范
- 维护困难

修复方案：
1. 全局扫描器：使用 pass_filenames: false，不设置 files
2. 文件级检查器：使用 files 过滤，不设置 pass_filenames: false
3. 移除冗余工具配置（已在主配置中）

官方规范：
- pass_filenames: false → hook 不接收文件列表（扫描整个项目）
- files: pattern → 只对匹配的文件运行 hook
- ❌ 两者不应同时使用
        """,
        "severity": "high",
        "stackTrace": "config/.pre-commit-config-security.yaml: 配置冲突",
        "context": {
            "project_name": PROJECT_NAME,
            "project_id": PROJECT_ID,
            "project_root": PROJECT_ROOT,
            "component": "CI/CD",
            "module": "security-hooks",
            "file": "config/.pre-commit-config-security.yaml",
            "configuration": r"""
修复前（错误）：
- id: sql-injection-check
  pass_filenames: false  # ❌ 与 files 冲突
  files: src/.*\.py$
  always_run: true        # ❌ 性能浪费

修复后（正确）：
全局扫描器：
- id: bandit-scan
  pass_filenames: false  # ✅ 不接收文件列表
  # 不设置 files

文件级检查器：
- id: sql-injection-check
  files: src/.*\.py$      # ✅ 只检查 Python 文件
  # pass_filenames 默认为 true
            """
        },
        "tags": ["pre-commit", "security", "configuration", "git-hooks"]
    }

    # 问题 3: 代码质量问题
    bug3 = {
        "errorCode": "CODE_QUALITY_001",
        "title": "Ruff 代码质量问题 - 125 个 F401/F841 错误",
        "message": """
问题描述：
- 125 个 F401（未使用的导入）和 F841（未使用的变量）错误
- 分布在多个文件中（adapters, storage, ml_strategy 等）
- 阻止 pre-commit 通过，影响开发效率

根本原因：
- 使用 import 检查库可用性但未使用导入（F401）
- 调试代码中变量未使用（F841）
- 未遵循 Python 代码规范

影响范围：
- 代码质量下降
- Pre-commit hook 失败，阻止提交
- 可能掩盖真正的错误

修复方案：
1. 使用 importlib.util.find_spec() 检查依赖（替代 import）
2. 使用 _ 显式标记未使用的变量
3. 批量自动修复：ruff check --select F401,F841 --fix --unsafe-fixes

修复结果：
- 自动修复：110 个错误
- 剩余：23 个需要手动审查

示例修复：
# ❌ 修复前
try:
    import efinance  # F401: 未使用
    status["dependencies"]["efinance"] = True
except ImportError:
    pass

# ✅ 修复后
import importlib.util
if importlib.util.find_spec("efinance"):
    status["dependencies"]["efinance"] = True
        """,
        "severity": "medium",
        "stackTrace": "src/: 125 个 F401/F841 错误",
        "context": {
            "project_name": PROJECT_NAME,
            "project_id": PROJECT_ID,
            "project_root": PROJECT_ROOT,
            "component": "Code Quality",
            "module": "linting",
            "file": "src/",
            "statistics": {
                "total_errors": 125,
                "auto_fixed": 110,
                "manual_review_required": 23,
                "error_types": {
                    "F401": 100,  # 未使用的导入
                    "F841": 25    # 未使用的变量
                }
            }
        },
        "tags": ["code-quality", "ruff", "linting", "f401", "f841"]
    }

    # 上报问题
    bugs = [bug1, bug2, bug3]
    results = []

    for i, bug in enumerate(bugs, 1):
        print(f"\n{'=' * 80}")
        print(f"📝 上报问题 {i}/{len(bugs)}: {bug['errorCode']}")
        print(f"标题: {bug['title']}")
        print()

        result = report_bug_to_bugger(bug)
        if result and result.get('success'):
            print(f"✅ 上报成功: Bug ID = {result.get('data', {}).get('bugId', 'unknown')}")
            results.append(result)
        else:
            print("❌ 上报失败")

    # 总结
    print("\n" + "=" * 80)
    print("📊 上报总结")
    print("=" * 80)
    print(f"总问题数: {len(bugs)}")
    print(f"上报成功: {len(results)}")
    print(f"上报失败: {len(bugs) - len(results)}")
    print()

    if len(results) == len(bugs):
        print("🎉 所有问题已成功上报到 BUGer 系统！")
        print()
        print("📖 查看问题:")
        print(f"   BUGer API: {BUGER_API_URL}/bugs")
        print(f"   项目: {PROJECT_NAME} ({PROJECT_ID})")
    else:
        print("⚠️  部分问题上报失败，请检查:")
        print("   1. BUGer 服务是否启动")
        print("   2. API Key 是否正确")
        print(f"   3. API URL 是否正确: {BUGER_API_URL}")

    return len(results) == len(bugs)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
