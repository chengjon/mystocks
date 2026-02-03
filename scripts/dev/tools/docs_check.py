#!/usr/bin/env python3
"""
文档规范检查工具

功能：
1. 检查文档命名规范
2. 检测空目录
3. 检测重复文档
4. 生成检查报告

使用方法：
    python scripts/tools/docs_check.py
    python scripts/tools/docs_check.py --path docs/
    python scripts/tools/docs_check.py --fix  # 自动修复部分问题
"""

import os
import sys
import re
import argparse
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class DocsChecker:
    """文档规范检查器"""

    def __init__(self, root_path: str = "docs/"):
        self.root_path = Path(root_path)
        self.issues = {
            "naming": [],
            "empty_dirs": [],
            "duplicates": [],
            "deep_nesting": [],
            "missing_index": []
        }

    def check_all(self) -> Dict:
        """执行所有检查"""
        print(f"🔍 检查目录: {self.root_path}\n")

        self.check_naming()
        self.check_empty_dirs()
        self.check_duplicates()
        self.check_deep_nesting()
        self.check_missing_index()

        return self.issues

    def check_naming(self):
        """检查命名规范"""
        print("🔤 检查命名规范...")

        for md_file in self.root_path.rglob("*.md"):
            rel_path = md_file.relative_to(self.root_path)

            # 检查文件名
            filename = md_file.name
            issues = []

            # 检查中文字符
            if re.search(r'[\u4e00-\u9fa5]', filename):
                issues.append("包含中文字符")

            # 检查空格
            if ' ' in filename:
                issues.append("包含空格")

            # 检查特殊字符
            if re.search(r'[^a-zA-Z0-9._-]', filename):
                issues.append("包含特殊字符")

            # 检查大写字母（推荐kebab-case）
            if re.search(r'[A-Z]', filename):
                issues.append("包含大写字母（推荐使用kebab-case）")

            # 检查目录名
            for part in rel_path.parts[:-1]:
                if re.search(r'[\u4e00-\u9fa5]', part):
                    issues.append(f"目录名包含中文: {part}")

                if re.search(r'[A-Z]', part):
                    issues.append(f"目录名包含大写字母: {part}")

                # 检查数字前缀（不推荐）
                if re.match(r'^\d+[-_.]', part):
                    issues.append(f"目录名有数字前缀: {part}")

            if issues:
                self.issues["naming"].append({
                    "file": str(rel_path),
                    "issues": issues
                })

        print(f"  ✅ 发现 {len(self.issues['naming'])} 个命名问题")

    def check_empty_dirs(self):
        """检查空目录"""
        print("📁 检查空目录...")

        for dir_path in self.root_path.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                rel_path = dir_path.relative_to(self.root_path)
                self.issues["empty_dirs"].append(str(rel_path))

        print(f"  ✅ 发现 {len(self.issues['empty_dirs'])} 个空目录")

    def check_duplicates(self):
        """检查重复文档"""
        print("🔄 检查重复文档...")

        file_hashes = defaultdict(list)

        # 计算所有文件的哈希值
        for md_file in self.root_path.rglob("*.md"):
            try:
                with open(md_file, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                rel_path = md_file.relative_to(self.root_path)
                file_hashes[file_hash].append(str(rel_path))
            except Exception as e:
                print(f"  ⚠️  无法读取文件: {md_file}")

        # 找出重复的文件
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.issues["duplicates"].append({
                    "hash": file_hash,
                    "files": files
                })

        print(f"  ✅ 发现 {len(self.issues['duplicates'])} 组重复文档")

    def check_deep_nesting(self):
        """检查深层嵌套"""
        print("📂 检查深层嵌套...")

        max_depth = 3
        for md_file in self.root_path.rglob("*.md"):
            rel_path = md_file.relative_to(self.root_path)
            depth = len(rel_path.parts) - 1  # 减1是因为包含文件名

            if depth > max_depth:
                self.issues["deep_nesting"].append({
                    "file": str(rel_path),
                    "depth": depth
                })

        print(f"  ✅ 发现 {len(self.issues['deep_nesting'])} 个深层嵌套文件（>{max_depth}层）")

    def check_missing_index(self):
        """检查缺失的索引文件"""
        print("📋 检查缺失的索引文件...")

        # 检查所有子目录是否有INDEX.md或README.md
        for dir_path in self.root_path.rglob("*"):
            if dir_path.is_dir():
                # 检查是否有索引文件
                has_index = (dir_path / "INDEX.md").exists()
                has_readme = (dir_path / "README.md").exists()

                # 如果目录包含子目录或文件，建议有索引
                contents = list(dir_path.iterdir())
                if len(contents) > 5 and not (has_index or has_readme):
                    rel_path = dir_path.relative_to(self.root_path)
                    self.issues["missing_index"].append({
                        "dir": str(rel_path),
                        "item_count": len(contents)
                    })

        print(f"  ✅ 发现 {len(self.issues['missing_index'])} 个目录缺失索引")

    def print_report(self):
        """打印检查报告"""
        print("\n" + "=" * 80)
        print("📊 文档规范检查报告".center(80))
        print("=" * 80)

        total_issues = (
            len(self.issues["naming"]) +
            len(self.issues["empty_dirs"]) +
            len(self.issues["duplicates"]) +
            len(self.issues["deep_nesting"]) +
            len(self.issues["missing_index"])
        )

        if total_issues == 0:
            print("\n✅ 未发现任何问题！文档规范完全符合要求。")
            return

        print(f"\n⚠️  总共发现 {total_issues} 个问题\n")

        # 命名问题
        if self.issues["naming"]:
            print(f"\n🔤 命名问题 ({len(self.issues['naming'])}个):")
            for item in self.issues["naming"][:20]:  # 只显示前20个
                print(f"  ❌ {item['file']}")
                for issue in item["issues"]:
                    print(f"     - {issue}")
            if len(self.issues["naming"]) > 20:
                print(f"  ... 还有 {len(self.issues['naming']) - 20} 个")

        # 空目录
        if self.issues["empty_dirs"]:
            print(f"\n📁 空目录 ({len(self.issues['empty_dirs'])}个):")
            for dir_path in self.issues["empty_dirs"][:20]:
                print(f"  📂 {dir_path}")
            if len(self.issues["empty_dirs"]) > 20:
                print(f"  ... 还有 {len(self.issues['empty_dirs']) - 20} 个")

        # 重复文档
        if self.issues["duplicates"]:
            print(f"\n🔄 重复文档 ({len(self.issues['duplicates'])}组):")
            for item in self.issues["duplicates"][:10]:
                print(f"  📋 {len(item['files'])} 个文件内容相同:")
                for file in item["files"]:
                    print(f"     - {file}")

        # 深层嵌套
        if self.issues["deep_nesting"]:
            print(f"\n📂 深层嵌套 ({len(self.issues['deep_nesting'])}个):")
            for item in self.issues["deep_nesting"][:20]:
                print(f"  📁 {item['file']} ({item['depth']}层)")
            if len(self.issues["deep_nesting"]) > 20:
                print(f"  ... 还有 {len(self.issues['deep_nesting']) - 20} 个")

        # 缺失索引
        if self.issues["missing_index"]:
            print(f"\n📋 缺失索引 ({len(self.issues['missing_index'])}个):")
            for item in self.issues["missing_index"][:20]:
                print(f"  📂 {item['dir']} ({item['item_count']}个文件)")
            if len(self.issues["missing_index"]) > 20:
                print(f"  ... 还有 {len(self.issues['missing_index']) - 20} 个")

        print("\n" + "=" * 80)
        print("💡 建议:")
        print("  1. 使用 kebab-case 命名（小写+连字符）")
        print("  2. 删除空目录")
        print("  3. 保留最新版本，删除重复文档")
        print("  4. 调整目录结构，避免超过3层嵌套")
        print("  5. 为包含多个文件的目录创建 INDEX.md")
        print("=" * 80 + "\n")

    def save_report(self, output_path: str):
        """保存检查报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 文档规范检查报告\n\n")
            f.write(f"**检查时间**: {Path(output_path).stem}\n\n")

            total_issues = sum(len(v) for v in self.issues.values())

            if total_issues == 0:
                f.write("✅ 未发现任何问题！\n")
                return

            f.write(f"⚠️  总共发现 {total_issues} 个问题\n\n")

            # 详细问题
            for category, items in self.issues.items():
                if not items:
                    continue

                f.write(f"## {category.replace('_', ' ').title()}\n\n")

                if category == "naming":
                    for item in items:
                        f.write(f"- ❌ `{item['file']}`\n")
                        for issue in item["issues"]:
                            f.write(f"  - {issue}\n")

                elif category == "duplicates":
                    for item in items:
                        f.write(f"- 📋 {len(item['files'])} 个文件内容相同:\n")
                        for file in item["files"]:
                            f.write(f"  - `{file}`\n")

                else:
                    for item in items:
                        f.write(f"- {item}\n")

                f.write("\n")

        print(f"✅ 报告已保存到: {output_path}")

    def fix_empty_dirs(self):
        """自动修复：删除空目录"""
        print("\n🔧 自动删除空目录...")

        deleted_count = 0
        for dir_path in self.issues["empty_dirs"]:
            full_path = self.root_path / dir_path
            try:
                full_path.rmdir()
                print(f"  ✅ 删除: {dir_path}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {dir_path} - {e}")

        print(f"\n✅ 成功删除 {deleted_count} 个空目录")

    def suggest_renames(self) -> List[Tuple[str, str]]:
        """建议文件重命名"""
        renames = []

        for item in self.issues["naming"]:
            old_path = item["file"]

            # 生成新文件名
            old_name = Path(old_path).name
            new_name = self._fix_filename(old_name)
            new_path = str(Path(old_path).parent / new_name)

            if old_path != new_path:
                renames.append((old_path, new_path))

        return renames

    def _fix_filename(self, filename: str) -> str:
        """修复文件名"""
        # 转换为小写
        name = filename.lower()

        # 替换空格和下划线为连字符
        name = re.sub(r'[\s_]+', '-', name)

        # 移除特殊字符（保留字母、数字、连字符、点）
        name = re.sub(r'[^a-z0-9.-]', '', name)

        # 移除多个连续连字符
        name = re.sub(r'-+', '-', name)

        # 移除开头和结尾的连字符
        name = name.strip('-')

        return name


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文档规范检查工具")
    parser.add_argument("--path", default="docs/", help="文档目录路径（默认: docs/）")
    parser.add_argument("--output", help="输出报告文件路径")
    parser.add_argument("--fix-empty-dirs", action="store_true",
                       help="自动删除空目录")
    parser.add_argument("--suggest-renames", action="store_true",
                       help="建议文件重命名")

    args = parser.parse_args()

    # 创建检查器
    checker = DocsChecker(args.path)

    # 执行检查
    checker.check_all()

    # 打印报告
    checker.print_report()

    # 保存报告
    if args.output:
        checker.save_report(args.output)

    # 自动修复
    if args.fix_empty_dirs:
        checker.fix_empty_dirs()

    # 建议重命名
    if args.suggest_renames:
        renames = checker.suggest_renames()
        if renames:
            print("\n💡 建议的文件重命名:")
            for old_path, new_path in renames[:20]:
                print(f"  git mv '{old_path}' '{new_path}'")
            if len(renames) > 20:
                print(f"  ... 还有 {len(renames) - 20} 个")
        else:
            print("\n✅ 没有需要重命名的文件")

    # 返回退出码
    total_issues = sum(len(v) for v in checker.issues.values())
    return 1 if total_issues > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
