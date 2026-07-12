#!/usr/bin/env python3
"""MyStocks 代码优化 - 小文件分析脚本
分析和处理小于50行的Python文件，提出合并建议

优化策略：
1. 小于10行的文件：直接合并到相关文件中
2. 10-30行的文件：评估是否需要独立文件
3. 30-50行的文件：根据复杂度决定是否保留

创建日期: 2025-11-25
版本: 1.0.0
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class SmallFileInfo:
    path: Path
    line_count: int
    class_count: int
    function_count: int
    is_init_file: bool
    complexity_score: int


class SmallFilesAnalyzer:
    def __init__(self):
        self.project_root = Path("/opt/claude/mystocks_spec")
        self.src_path = self.project_root / "src"

    def count_lines(self, file_path: Path) -> int:
        """计算文件的行数"""
        try:
            with open(file_path, encoding="utf-8") as f:
                return len(f.readlines())
        except Exception:
            return 0

    def count_elements(self, content: str) -> Tuple[int, int]:
        """计算类和函数的数量"""
        classes = len(re.findall(r"^class\s+\w+", content, re.MULTILINE))
        functions = len(re.findall(r"^def\s+\w+", content, re.MULTILINE))
        return classes, functions

    def calculate_complexity_score(
        self,
        line_count: int,
        class_count: int,
        function_count: int,
    ) -> int:
        """计算文件复杂度评分"""
        base_score = line_count

        # 每增加一个类，复杂度增加50分
        class_bonus = class_count * 50

        # 每增加一个函数，复杂度增加10分
        function_bonus = function_count * 10

        return base_score + class_bonus + function_bonus

    def analyze_small_files(self) -> List[SmallFileInfo]:
        """分析所有小文件"""
        print("=" * 60)
        print("MyStocks 小文件分析")
        print("=" * 60)

        small_files = []
        total_files = 0

        # 遍历所有Python文件
        for py_file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            total_files += 1
            line_count = self.count_lines(py_file)

            # 只分析小于50行的文件
            if line_count > 0 and line_count < 50:
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    class_count, function_count = self.count_elements(content)
                    is_init_file = py_file.name == "__init__.py"
                    complexity_score = self.calculate_complexity_score(
                        line_count,
                        class_count,
                        function_count,
                    )

                    file_info = SmallFileInfo(
                        path=py_file,
                        line_count=line_count,
                        class_count=class_count,
                        function_count=function_count,
                        is_init_file=is_init_file,
                        complexity_score=complexity_score,
                    )

                    small_files.append(file_info)

                except Exception as e:
                    print(f"   ⚠️  分析文件失败 {py_file}: {e}")

        print(f"📊 总文件数: {total_files}")
        print(f"📊 小文件数: {len(small_files)}")

        return small_files

    def categorize_small_files(
        self,
        small_files: List[SmallFileInfo],
    ) -> Dict[str, List[SmallFileInfo]]:
        """对小文件进行分类"""
        categories = {
            "tiny_files": [],  # < 10行
            "small_files": [],  # 10-20行
            "medium_files": [],  # 20-30行
            "large_files": [],  # 30-50行
            "init_files": [],  # __init__.py文件
        }

        for file_info in small_files:
            if file_info.is_init_file:
                categories["init_files"].append(file_info)
            elif file_info.line_count < 10:
                categories["tiny_files"].append(file_info)
            elif file_info.line_count < 20:
                categories["small_files"].append(file_info)
            elif file_info.line_count < 30:
                categories["medium_files"].append(file_info)
            else:
                categories["large_files"].append(file_info)

        return categories

    def print_category_analysis(self, categories: Dict[str, List[SmallFileInfo]]):
        """打印分类分析结果"""
        print("\n📋 小文件分类分析:")
        print("=" * 50)

        for category_name, files in categories.items():
            print(f"\n🔍 {category_name.upper()} ({len(files)} 个文件):")

            if not files:
                print("   (无)")
                continue

            # 按文件大小排序
            files.sort(key=lambda x: x.line_count)

            for file_info in files:
                relative_path = file_info.path.relative_to(self.project_root)
                print(f"   📄 {relative_path}")
                print(
                    f"      └─ {file_info.line_count} 行, {file_info.class_count} 类, {file_info.function_count} 函数",
                )

    def get_merge_recommendations(
        self,
        categories: Dict[str, List[SmallFileInfo]],
    ) -> List[Tuple[SmallFileInfo, str]]:
        """获取合并建议"""
        recommendations = []

        # 极小文件（< 10行）建议合并
        for file_info in categories["tiny_files"]:
            if not file_info.is_init_file:
                reason = f"极小文件（{file_info.line_count}行），建议合并到同级目录的相关文件中"
                recommendations.append((file_info, reason))

        # __init__.py文件保留，不建议合并
        for file_info in categories["init_files"]:
            if file_info.line_count < 5:  # 如果__init__.py太小，可以考虑简化
                reason = f"过小的__init__.py文件（{file_info.line_count}行），可考虑简化或移除"
                recommendations.append((file_info, reason))

        # 复杂小文件评估
        for file_info in categories["small_files"] + categories["medium_files"]:
            if file_info.complexity_score > 200:  # 高复杂度小文件应该保留
                reason = f"高复杂度小文件（{file_info.complexity_score}分），建议保留"
            else:
                reason = f"中等小文件（{file_info.line_count}行），可考虑合并到相关文件中"
                recommendations.append((file_info, reason))

        return recommendations

    def print_recommendations(self, recommendations: List[Tuple[SmallFileInfo, str]]):
        """打印合并建议"""
        print(f"\n💡 合并建议 ({len(recommendations)} 条):")
        print("=" * 50)

        for file_info, reason in recommendations:
            relative_path = file_info.path.relative_to(self.project_root)
            print(f"\n📄 文件: {relative_path}")
            print(
                f"   📊 大小: {file_info.line_count} 行, 复杂度: {file_info.complexity_score}",
            )
            print(f"   💭 建议: {reason}")

    def calculate_optimization_potential(
        self,
        categories: Dict[str, List[SmallFileInfo]],
    ) -> Dict:
        """计算优化潜力"""
        total_small_lines = sum(f.line_count for files in categories.values() for f in files)
        total_files = sum(len(files) for files in categories.values())

        optimization_potential = {
            "total_small_files": total_files,
            "total_small_lines": total_small_lines,
            "potential_file_reduction": 0,
            "potential_line_reduction": 0,
            "reduction_percentage": 0,
        }

        # 计算可以删除的文件数（主要是tiny files和过小的init文件）
        deletable_files = len(categories["tiny_files"])
        deletable_lines = sum(f.line_count for f in categories["tiny_files"])

        # 过小的__init__.py也可以考虑删除
        small_init_files = [f for f in categories["init_files"] if f.line_count < 5]
        deletable_files += len(small_init_files)
        deletable_lines += sum(f.line_count for f in small_init_files)

        optimization_potential["potential_file_reduction"] = deletable_files
        optimization_potential["potential_line_reduction"] = deletable_lines
        optimization_potential["reduction_percentage"] = (
            (deletable_lines / total_small_lines * 100) if total_small_lines > 0 else 0
        )

        return optimization_potential

    def print_optimization_summary(self, optimization_potential: Dict):
        """打印优化总结"""
        print("\n📈 优化潜力分析:")
        print("=" * 50)
        print(f"   📊 小文件总数: {optimization_potential['total_small_files']} 个")
        print(f"   📊 小文件行数: {optimization_potential['total_small_lines']} 行")
        print(
            f"   🎯 可减少文件: {optimization_potential['potential_file_reduction']} 个",
        )
        print(
            f"   🎯 可减少行数: {optimization_potential['potential_line_reduction']} 行",
        )
        print(f"   📈 减少比例: {optimization_potential['reduction_percentage']:.1f}%")

    def run_analysis(self):
        """运行完整分析"""
        small_files = self.analyze_small_files()
        categories = self.categorize_small_files(small_files)
        recommendations = self.get_merge_recommendations(categories)
        optimization_potential = self.calculate_optimization_potential(categories)

        self.print_category_analysis(categories)
        self.print_recommendations(recommendations)
        self.print_optimization_summary(optimization_potential)

        print("\n💡 下一步建议:")
        print("   1. 优先处理极小文件（<10行）的合并")
        print("   2. 评估并简化过小的__init__.py文件")
        print("   3. 考虑将相关功能合并到同一文件中")
        print("   4. 保持代码结构清晰，避免过度合并")

        return {
            "small_files": small_files,
            "categories": categories,
            "recommendations": recommendations,
            "optimization_potential": optimization_potential,
        }


if __name__ == "__main__":
    analyzer = SmallFilesAnalyzer()
    results = analyzer.run_analysis()
