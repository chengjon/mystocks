#!/usr/bin/env python3
"""文档索引生成工具

功能：
1. 自动扫描目录结构
2. 生成分类索引
3. 生成全局索引
4. 支持自定义模板

使用方法：
    python scripts/dev/tools/docs_indexer.py
    python scripts/dev/tools/docs_indexer.py --path docs/
    python scripts/dev/tools/docs_indexer.py --output INDEX.md
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class DocsIndexer:
    """文档索引生成器"""

    def __init__(self, root_path: str = "docs/"):
        self.root_path = Path(root_path)
        self.index_structure = {}

    def scan_directory(self, dir_path: Path, level: int = 0) -> Dict:
        """递归扫描目录结构"""
        if level > 5:  # 限制深度
            return {}

        result = {
            "name": dir_path.name,
            "path": str(dir_path.relative_to(self.root_path)),
            "readme": None,
            "index_files": [],
            "subdirs": {},
            "files": [],
        }

        # 查找README和INDEX
        for name in ["README.md", "INDEX.md", "index.md"]:
            if (dir_path / name).exists():
                result["readme"] = name
                break

        # 扫描子目录和文件
        try:
            for item in sorted(dir_path.iterdir()):
                if item.is_dir() and not item.name.startswith("."):
                    result["subdirs"][item.name] = self.scan_directory(item, level + 1)
                elif item.is_file() and item.suffix == ".md" and item.name not in ["README.md", "INDEX.md", "index.md"]:
                    rel_path = item.relative_to(self.root_path)
                    result["files"].append(
                        {"name": item.stem, "path": str(rel_path), "title": self._extract_title(item)},
                    )
        except PermissionError:
            pass

        return result

    def _extract_title(self, md_file: Path) -> str:
        """从Markdown文件中提取标题"""
        try:
            with open(md_file, encoding="utf-8") as f:
                first_line = f.readline()
                if first_line.startswith("#"):
                    return first_line.lstrip("#").strip()
        except Exception:
            pass
        return md_file.stem

    def generate_category_index(self, category: str, items: List[Dict], category_path: str) -> str:
        """生成分类索引"""
        lines = [
            f"# {category}\n",
            f"**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**文档数量**: {len(items)}\n",
            "\n---\n",
        ]

        # 按名称排序
        items_sorted = sorted(items, key=lambda x: x["name"])
        category_root = Path(category_path)

        for item in items_sorted:
            item_path = Path(item["path"])
            relative_item_path = item_path.relative_to(category_root).as_posix()
            lines.append(f"- [{item['name']}]({relative_item_path})")
            if item.get("title"):
                lines.append(f"  - *{item['title']}*")
            lines.append("")

        return "\n".join(lines)

    def generate_global_index(self, structure: Dict) -> str:
        """生成全局索引"""
        lines = ["# MyStocks 文档索引\n", f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "\n---\n"]

        # 快速导航
        lines.append("## 🚀 快速导航\n")

        categories = {
            "overview": "📖 项目概述",
            "guides": "📘 开发指南",
            "api": "🔌 API文档",
            "architecture": "🏗️  架构设计",
            "operations": "⚙️  运维文档",
            "testing": "🧪 测试文档",
            "reports": "📊 分析报告",
            "archive": "📦 归档文档",
        }

        for key, name in categories.items():
            if key in structure.get("subdirs", {}):
                lines.append(f"- [{name}](#{key})")

        lines.append("\n---\n")

        # 统计信息
        total_files = self._count_files(structure)
        total_dirs = self._count_dirs(structure)

        lines.append("## 📊 统计信息\n\n")
        lines.append(f"- **总文档数**: {total_files:,}")
        lines.append(f"- **总目录数**: {total_dirs:,}")
        lines.append(f"- **最后更新**: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("\n---\n")

        # 详细目录结构
        lines.extend(self._generate_structure_tree(structure))

        return "\n".join(lines)

    def _generate_structure_tree(self, structure: Dict, level: int = 0) -> List[str]:
        """生成目录树"""
        lines = []
        indent = "  " * level

        # 目录标题
        name = structure["name"]
        path = structure["path"]

        if level == 0:
            lines.append("\n## 📁 项目根目录\n")
        else:
            # 转换为标题
            title = self._dir_to_title(name)
            level_marker = "#" * (level + 2)
            lines.append(f"\n{level_marker} {title}\n")

        # README链接
        if structure["readme"]:
            lines.append(f"{indent}- 📄 [README]({path}/{structure['readme']})")

        # 子目录
        for subdir_name, subdir in sorted(structure["subdirs"].items()):
            subdir_title = self._dir_to_title(subdir_name)
            lines.append(f"{indent}- 📂 [{subdir_title}]({subdir['path']})")

            # 递归子目录
            if subdir["subdirs"] or subdir["files"]:
                lines.extend(self._generate_structure_tree(subdir, level + 2))

        # 文件
        for file_info in sorted(structure["files"], key=lambda x: x["name"]):
            lines.append(f"{indent}- 📄 [{file_info['name']}]({file_info['path']})")

        return lines

    def _dir_to_title(self, dir_name: str) -> str:
        """将目录名转换为标题"""
        # 移除数字前缀
        name = dir_name.lstrip("0123456789.-")

        # 替换连字符和下划线为空格
        name = name.replace("-", " ").replace("_", " ")

        # 首字母大写
        return name.title()

    def _count_files(self, structure: Dict) -> int:
        """递归统计文件数"""
        count = len(structure["files"])
        for subdir in structure["subdirs"].values():
            count += self._count_files(subdir)
        return count

    def _count_dirs(self, structure: Dict) -> int:
        """递归统计目录数"""
        count = len(structure["subdirs"])
        for subdir in structure["subdirs"].values():
            count += self._count_dirs(subdir)
        return count

    def generate(self) -> Dict:
        """生成索引"""
        print(f"🔍 扫描目录: {self.root_path}")

        # 扫描目录结构
        self.index_structure = self.scan_directory(self.root_path)

        # 生成全局索引
        global_index = self.generate_global_index(self.index_structure)

        # 生成统计信息
        stats = {
            "total_files": self._count_files(self.index_structure),
            "total_dirs": self._count_dirs(self.index_structure),
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        print("✅ 扫描完成:")
        print(f"  - 总文档数: {stats['total_files']:,}")
        print(f"  - 总目录数: {stats['total_dirs']:,}")

        return {"structure": self.index_structure, "global_index": global_index, "stats": stats}

    def save_global_index(self, output_path: str):
        """保存全局索引"""
        index_data = self.generate()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(index_data["global_index"])

        print(f"✅ 全局索引已保存到: {output_path}")

    def save_category_indices(self, _base_dir: Path):
        """为每个主目录生成索引"""
        index_data = self.generate()

        for category_name, category_data in index_data["structure"]["subdirs"].items():
            # 生成索引内容
            files = category_data["files"]

            # 递归收集子目录的文件
            def collect_files(structure: Dict) -> List[Dict]:
                files = structure["files"].copy()
                for subdir in structure["subdirs"].values():
                    files.extend(collect_files(subdir))
                return files

            all_files = collect_files(category_data)

            if not all_files:
                continue

            # 生成索引
            category_title = self._dir_to_title(category_name)
            index_content = self.generate_category_index(category_title, all_files, category_data["path"])

            # category_data["path"] is already relative to self.root_path, so category
            # indices must stay under the scanned subtree instead of its parent.
            index_path = self.root_path / category_data["path"] / "INDEX.md"
            index_path.parent.mkdir(parents=True, exist_ok=True)

            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)

            print(f"✅ 分类索引已保存: {index_path}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="文档索引生成工具")
    parser.add_argument("--path", default="docs/", help="文档目录路径（默认: docs/）")
    parser.add_argument("--output", default="docs/INDEX.md", help="全局索引输出路径（默认: docs/INDEX.md）")
    parser.add_argument("--categories", action="store_true", help="同时生成各分类的索引文件")

    args = parser.parse_args()

    # 创建索引生成器
    indexer = DocsIndexer(args.path)

    # 生成全局索引
    indexer.save_global_index(args.output)

    # 生成分类索引
    if args.categories:
        indexer.save_category_indices(Path(args.path).parent)

    return 0


if __name__ == "__main__":
    sys.exit(main())
