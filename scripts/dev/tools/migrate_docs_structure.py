#!/usr/bin/env python3
"""
文档目录重组脚本

将文档从旧结构迁移到8大分类新结构
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess


# 目录映射表
DIRECTORY_MAPPINGS = {
    # 中文目录 → 英文分类
    "01-项目总览与核心规范": "overview",
    "02-架构与设计文档": "architecture",
    "03-API与功能文档": "api",
    "04-测试与质量保障文档": "testing",
    "05-部署与运维监控文档": "operations",
    "06-项目管理与报告": "reports",

    # 英文目录合并
    "architecture": "architecture",  # 已存在，需合并
    "api": "api",  # 已存在，需合并
    "testing": "testing",  # 已存在，需合并
    "operations": "operations",  # 已存在，需合并
    "reports": "reports",  # 已存在，需合并
    "guides": "guides",  # 已存在，需保留

    # 归档目录
    "archived": "archive/legacy",
    "归档文档": "archive/legacy-zh",
    "归档文档/旧API文档": "archive/old-api",
    "归档文档/旧标准文档": "archive/old-standards",
}

# 根目录文件映射
ROOT_FILE_MAPPINGS = {
    "AGENTS.md": "overview/agents.md",
    "CLAUDE.md": "overview/claude.md",  # 保留副本在根目录
    "README.md": "overview/readme.md",
    "CHANGELOG.md": "overview/changelog.md",
    "DOCUMENT_ORGANIZATION_PLAN.md": "reports/doc-organization-plan.md",
    "COMPREHENSIVE_CLEANUP_REPORT.md": "reports/comprehensive-cleanup.md",
    "FILE_ORGANIZATION_RULES.md": "standards/file-organization-rules.md",
    "DEPLOYMENT_GUIDE.md": "operations/deployment-guide.md",
    "QUICK_START.md": "guides/quick-start.md",
    "ENHANCED_UI_UX_GUIDE.md": "guides/enhanced-ui-ux-guide.md",
    "IMPLEMENTATION_GUIDE.md": "guides/implementation-guide.md",
    "ARCHIVED.md": "overview/archived.md",
    "INITIALIZATION_PROMPT.md": "overview/initialization-prompt.md",
}


def run_git_mv(src, dst):
    """使用git mv移动文件"""
    try:
        subprocess.run(['git', 'mv', str(src), str(dst)], check=True, capture_output=True)
        return True, f"✅ {src} → {dst}"
    except subprocess.CalledProcessError as e:
        return False, f"❌ {src}: {e.stderr.decode().strip()}"


def migrate_directory(old_dir, new_dir, docs_root):
    """迁移目录"""
    old_path = docs_root / old_dir
    new_path = docs_root / new_dir

    if not old_path.exists():
        return False, f"⚠️  源目录不存在: {old_dir}"

    # 创建目标目录
    new_path.parent.mkdir(parents=True, exist_ok=True)

    # 移动目录下的所有文件
    success_count = 0
    errors = []

    for item in old_path.iterdir():
        if item.is_file():
            success, msg = run_git_mv(item, new_path / item.name)
            if success:
                success_count += 1
            else:
                errors.append(msg)

    # 删除空目录
    try:
        if old_path.exists() and not any(old_path.iterdir()):
            old_path.rmdir()
    except:
        pass

    return success_count > 0, f"📁 {old_dir} → {new_dir} ({success_count} files)" + ("\n" + "\n".join(errors) if errors else "")


def migrate_root_files(docs_root):
    """迁移根目录文件"""
    success_count = 0
    errors = []

    for old_name, new_path in ROOT_FILE_MAPPINGS.items():
        old_file = docs_root / old_name
        target_file = docs_root / new_path

        if not old_file.exists():
            continue

        # 创建目标目录
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # 特殊处理：CLAUDE.md保留在根目录
        if old_name == "CLAUDE.md":
            # 复制到overview，保留原文件
            shutil.copy(old_file, target_file)
            success_count += 1
            continue

        success, msg = run_git_mv(old_file, target_file)
        if success:
            success_count += 1
        else:
            errors.append(msg)

    return success_count, errors


def main():
    """主函数"""
    docs_root = Path("/opt/claude/mystocks_spec/docs")

    if not docs_root.exists():
        print(f"❌ docs目录不存在: {docs_root}")
        return 1

    print("=" * 80)
    print("📂 文档目录重组工具")
    print("=" * 80)

    total_success = 0
    total_errors = []

    print("\n📋 迁移根目录文件...")
    success, errors = migrate_root_files(docs_root)
    total_success += success
    total_errors.extend(errors)

    print(f"✅ 成功迁移 {success} 个根目录文件")

    print("\n📋 迁移子目录...")
    for old_dir, new_dir in DIRECTORY_MAPPINGS.items():
        success, msg = migrate_directory(old_dir, new_dir, docs_root)
        if success:
            print(msg)
            total_success += 1
        else:
            print(msg)
            if "⚠️" not in msg:  # 不是警告，是错误
                total_errors.append(msg)

    print("\n" + "=" * 80)
    print(f"✅ 迁移完成！")
    print(f"  成功: {total_success}")
    print(f"  错误: {len(total_errors)}")
    print("=" * 80)

    if total_errors:
        print("\n❌ 错误详情:")
        for error in total_errors[:10]:
            print(f"  {error}")
        if len(total_errors) > 10:
            print(f"  ... 还有 {len(total_errors) - 10} 个错误")

    return 0


if __name__ == "__main__":
    sys.exit(main())
