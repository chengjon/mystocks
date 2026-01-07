#!/usr/bin/env python3
"""
重复文档清理工具

策略：
1. 保留主目录中的文件，删除"归档文档/临时文档/"中的重复
2. 对于其他重复，保留修改时间较新的文件
3. 使用git rm确保文件历史保留
"""

import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def calculate_file_hash(file_path: Path) -> str:
    """计算文件的MD5哈希值"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"⚠️  无法读取文件: {file_path} - {e}")
        return None


def find_duplicates(root_path: Path) -> dict:
    """查找所有重复文档"""
    print("🔍 查找重复文档...")

    file_hashes = defaultdict(list)

    for md_file in root_path.rglob("*.md"):
        file_hash = calculate_file_hash(md_file)
        if file_hash:
            rel_path = md_file.relative_to(root_path)
            file_hashes[file_hash].append({
                'path': md_file,
                'rel_path': rel_path,
                'mtime': datetime.fromtimestamp(md_file.stat().st_mtime)
            })

    # 找出重复的文件
    duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}

    print(f"✅ 发现 {len(duplicates)} 组重复文档")
    return duplicates


def resolve_duplicates(duplicates: dict, root_path: Path, dry_run: bool = True):
    """解决重复文档"""
    deleted_count = 0
    kept_count = 0

    for file_hash, files in duplicates.items():
        if len(files) < 2:
            continue

        # 排序：优先保留非归档/临时文档，其次保留修改时间较新的
        def sort_key(item):
            path_str = str(item['rel_path'])
            # 归档/临时文档优先级低
            priority = 0
            if '归档文档/临时文档' in path_str or '归档文档/旧' in path_str:
                priority = 1
            elif '/archive/' in path_str.lower() or '/archived/' in path_str.lower():
                priority = 1

            return (priority, -item['mtime'].timestamp())

        files_sorted = sorted(files, key=sort_key)
        keep = files_sorted[0]
        delete = files_sorted[1:]

        print(f"\n📋 重复组 ({len(files)} 个文件):")
        print(f"  ✅ 保留: {keep['rel_path']} ({keep['mtime'].strftime('%Y-%m-%d')})")

        for file_info in delete:
            print(f"  ❌ 删除: {file_info['rel_path']} ({file_info['mtime'].strftime('%Y-%m-%d')})")

            if not dry_run:
                try:
                    # 使用git rm保留历史
                    os.system(f'git rm -f "{file_info["path"]}"')
                    deleted_count += 1
                except Exception as e:
                    print(f"    ⚠️  删除失败: {e}")
            else:
                deleted_count += 1

        kept_count += 1

    print(f"\n📊 统计:")
    print(f"  保留文件组: {kept_count}")
    print(f"  删除文件数: {deleted_count}")

    if dry_run:
        print(f"\n⚠️  这是试运行模式，实际没有删除文件")
        print(f"   要真正删除，请使用: --execute")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="重复文档清理工具")
    parser.add_argument("--path", default="docs/", help="文档目录路径（默认: docs/）")
    parser.add_argument("--execute", action="store_true", help="真正执行删除（默认是试运行）")

    args = parser.parse_args()

    root_path = Path(args.path)

    if not root_path.exists():
        print(f"❌ 目录不存在: {root_path}")
        return 1

    print("=" * 80)
    print("📦 重复文档清理工具")
    print("=" * 80)

    # 查找重复文档
    duplicates = find_duplicates(root_path)

    if not duplicates:
        print("\n✅ 未发现重复文档！")
        return 0

    # 解决重复
    print("\n" + "=" * 80)
    print("🔧 处理重复文档")
    print("=" * 80)

    resolve_duplicates(duplicates, root_path, dry_run=not args.execute)

    if not args.execute:
        print("\n" + "=" * 80)
        print("💡 如果以上结果符合预期，请运行:")
        print(f"   python scripts/tools/remove_duplicate_docs.py --path {args.path} --execute")
        print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
