#!/usr/bin/env python3
"""文档清单生成工具

功能：
1. 扫描指定目录的所有Markdown文档
2. 统计文档数量、大小、年龄
3. 检测命名规范问题
4. 生成详细清单报告

使用方法：
    python scripts/tools/docs_inventory.py
    python scripts/tools/docs_inventory.py --path docs/
    python scripts/tools/docs_inventory.py --output inventory.json
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class DocsInventory:
    """文档清单生成器"""

    def __init__(self, root_path: str = "docs/"):
        self.root_path = Path(root_path)
        self.inventory = {
            "summary": {},
            "files": [],
            "issues": {
                "naming": [],
                "size": [],
                "age": [],
                "empty_dirs": [],
            },
            "statistics": {},
        }

    def scan(self) -> Dict:
        """扫描文档目录"""
        print(f"🔍 扫描目录: {self.root_path}")

        # 统计数据
        total_files = 0
        total_size = 0
        file_types = defaultdict(int)
        age_distribution = defaultdict(int)

        # 扫描所有Markdown文件
        for md_file in self.root_path.rglob("*.md"):
            total_files += 1

            # 获取文件信息
            stat = md_file.stat()
            file_size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime)
            age_days = (datetime.now() - mtime).days

            total_size += file_size

            # 相对路径
            rel_path = md_file.relative_to(self.root_path)

            # 检查命名规范
            naming_issues = self._check_naming(md_file)

            if naming_issues:
                self.inventory["issues"]["naming"].extend(
                    [{"file": str(rel_path), "issue": issue} for issue in naming_issues]
                )

            # 检查文件大小
            if file_size > 1024 * 1024:  # > 1MB
                self.inventory["issues"]["size"].append(
                    {
                        "file": str(rel_path),
                        "size_mb": round(file_size / (1024 * 1024), 2),
                    }
                )

            # 检查文件年龄
            if age_days > 180:  # > 6个月
                self.inventory["issues"]["age"].append(
                    {
                        "file": str(rel_path),
                        "age_days": age_days,
                        "last_modified": mtime.strftime("%Y-%m-%d"),
                    }
                )

            # 文件信息
            self.inventory["files"].append(
                {
                    "path": str(rel_path),
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2),
                    "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                    "age_days": age_days,
                }
            )

            # 统计
            file_types[md_file.suffix] += 1

            # 年龄分布
            if age_days < 30:
                age_distribution["< 30天"] += 1
            elif age_days < 90:
                age_distribution["30-90天"] += 1
            elif age_days < 180:
                age_distribution["90-180天"] += 1
            else:
                age_distribution["> 180天"] += 1

        # 扫描空目录
        for dir_path in self.root_path.rglob("*"):
            if dir_path.is_dir():
                if not any(dir_path.iterdir()):
                    rel_dir = dir_path.relative_to(self.root_path)
                    self.inventory["issues"]["empty_dirs"].append(str(rel_dir))

        # 汇总信息
        self.inventory["summary"] = {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "root_path": str(self.root_path),
        }

        # 统计信息
        self.inventory["statistics"] = {
            "file_types": dict(file_types),
            "age_distribution": dict(age_distribution),
            "issue_counts": {
                "naming_issues": len(self.inventory["issues"]["naming"]),
                "large_files": len(self.inventory["issues"]["size"]),
                "old_files": len(self.inventory["issues"]["age"]),
                "empty_dirs": len(self.inventory["issues"]["empty_dirs"]),
            },
        }

        return self.inventory

    def _check_naming(self, file_path: Path) -> List[str]:
        """检查文件命名规范"""
        issues = []
        filename = file_path.name

        # 检查中文字符
        if any("\u4e00" <= char <= "\u9fa5" for char in filename):
            issues.append("包含中文字符")

        # 检查空格
        if " " in filename:
            issues.append("包含空格")

        # 检查特殊字符（排除 . - _）
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_")
        if not all(c in allowed_chars for c in filename):
            issues.append("包含特殊字符")

        # 检查大写字母（推荐kebab-case）
        if any(c.isupper() for c in filename):
            issues.append("包含大写字母（推荐使用kebab-case）")

        return issues

    def print_report(self):
        """打印清单报告"""
        summary = self.inventory["summary"]
        stats = self.inventory["statistics"]
        issues = self.inventory["issues"]

        print("\n" + "=" * 80)
        print("📊 文档清单报告".center(80))
        print("=" * 80)

        # 汇总信息
        print(f"\n📁 扫描路径: {summary['root_path']}")
        print(f"📄 文档总数: {summary['total_files']:,}")
        print(f"💾 总大小: {summary['total_size_mb']} MB")
        print(f"⏰ 扫描时间: {summary['scan_time']}")

        # 统计信息
        print("\n📈 统计信息:")
        print(f"  文件类型: {stats['file_types']}")
        print("\n  年龄分布:")
        for age_range, count in stats["age_distribution"].items():
            percentage = count / summary["total_files"] * 100 if summary["total_files"] > 0 else 0
            print(f"    {age_range}: {count} ({percentage:.1f}%)")

        # 问题汇总
        print("\n⚠️  发现的问题:")
        print(f"  🔤 命名问题: {stats['issue_counts']['naming_issues']} 个")
        print(f"  📦 大文件(>1MB): {stats['issue_counts']['large_files']} 个")
        print(f"  📅 旧文件(>180天): {stats['issue_counts']['old_files']} 个")
        print(f"  📁 空目录: {stats['issue_counts']['empty_dirs']} 个")

        # 详细问题（仅显示前10个）
        if issues["naming"]:
            print("\n🔤 命名问题（前10个）:")
            for item in issues["naming"][:10]:
                print(f"  ❌ {item['file']}: {item['issue']}")

        if issues["size"]:
            print("\n📦 大文件（前10个）:")
            for item in issues["size"][:10]:
                print(f"  ⚠️  {item['file']}: {item['size_mb']} MB")

        if issues["age"]:
            print("\n📅 旧文件（前10个）:")
            for item in issues["age"][:10]:
                print(f"  🕰️  {item['file']}: {item['age_days']} 天 ({item['last_modified']})")

        if issues["empty_dirs"]:
            print("\n📁 空目录（前10个）:")
            for dir_path in issues["empty_dirs"][:10]:
                print(f"  📂 {dir_path}")

        print("\n" + "=" * 80)

    def save_json(self, output_path: str):
        """保存JSON格式清单"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.inventory, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON清单已保存到: {output_path}")

    def save_markdown(self, output_path: str):
        """保存Markdown格式清单"""
        summary = self.inventory["summary"]
        stats = self.inventory["statistics"]
        issues = self.inventory["issues"]

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 文档清单报告\n\n")
            f.write(f"**生成时间**: {summary['scan_time']}\n\n")
            f.write(f"**扫描路径**: `{summary['root_path']}`\n\n")

            # 汇总信息
            f.write("## 📊 汇总信息\n\n")
            f.write(f"- **文档总数**: {summary['total_files']:,}\n")
            f.write(f"- **总大小**: {summary['total_size_mb']} MB\n")
            f.write(f"- **文件类型**: {', '.join(f'{k}({v})' for k, v in stats['file_types'].items())}\n\n")

            # 统计信息
            f.write("## 📈 统计信息\n\n")
            f.write("### 年龄分布\n\n")
            f.write("| 年龄范围 | 数量 | 占比 |\n")
            f.write("|---------|------|------|\n")
            for age_range, count in stats["age_distribution"].items():
                percentage = count / summary["total_files"] * 100 if summary["total_files"] > 0 else 0
                f.write(f"| {age_range} | {count} | {percentage:.1f}% |\n")

            # 问题汇总
            f.write("\n## ⚠️  发现的问题\n\n")
            f.write(f"- 🔤 **命名问题**: {stats['issue_counts']['naming_issues']} 个\n")
            f.write(f"- 📦 **大文件(>1MB)**: {stats['issue_counts']['large_files']} 个\n")
            f.write(f"- 📅 **旧文件(>180天)**: {stats['issue_counts']['old_files']} 个\n")
            f.write(f"- 📁 **空目录**: {stats['issue_counts']['empty_dirs']} 个\n\n")

            # 详细问题
            if issues["naming"]:
                f.write("### 🔤 命名问题\n\n")
                f.writelines(f"- ❌ `{item['file']}`: {item['issue']}\n" for item in issues["naming"])

            if issues["size"]:
                f.write("\n### 📦 大文件\n\n")
                f.write("| 文件 | 大小 |\n")
                f.write("|------|------|\n")
                f.writelines(f"| `{item['file']}` | {item['size_mb']} MB |\n" for item in issues["size"])

            if issues["age"]:
                f.write("\n### 📅 旧文件\n\n")
                f.write("| 文件 | 天数 | 最后修改 |\n")
                f.write("|------|------|----------|\n")
                f.writelines(
                    f"| `{item['file']}` | {item['age_days']} | {item['last_modified']} |\n" for item in issues["age"]
                )

            if issues["empty_dirs"]:
                f.write("\n### 📁 空目录\n\n")
                f.writelines(f"- 📂 `{dir_path}`\n" for dir_path in issues["empty_dirs"])

        print(f"✅ Markdown清单已保存到: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文档清单生成工具")
    parser.add_argument("--path", default="docs/", help="文档目录路径（默认: docs/）")
    parser.add_argument("--output", help="输出文件路径（支持.json或.md）")
    parser.add_argument("--format", choices=["json", "markdown", "both"], default="both", help="输出格式（默认: both）")

    args = parser.parse_args()

    # 创建清单生成器
    inventory = DocsInventory(args.path)

    # 扫描目录
    inventory.scan()

    # 打印报告
    inventory.print_report()

    # 保存文件
    if args.output:
        if args.format in ["json", "both"]:
            if args.output.endswith(".json"):
                json_path = args.output
            else:
                json_path = f"{args.output}.json"
            inventory.save_json(json_path)

        if args.format in ["markdown", "both"]:
            if args.output.endswith(".md"):
                md_path = args.output
            else:
                md_path = f"{args.output}.md"
            inventory.save_markdown(md_path)
    else:
        # 默认保存到当前目录
        inventory.save_json("docs-inventory.json")
        inventory.save_markdown("docs-inventory.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
