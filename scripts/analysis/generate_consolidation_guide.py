#!/usr/bin/env python3
"""
模块合并指南生成器 - 提供模块合并建议

基于重复分析和功能相似性，提供模块合并策略。

作者: MyStocks Team
日期: 2025-10-19

使用方法:
    python scripts/analysis/generate_consolidation_guide.py
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    MergeRecommendation,
    ConsolidationGuide,
    ModuleInventory,
    CategoryEnum,
)
from generate_docs import load_inventory


def analyze_similar_modules(inventory: ModuleInventory) -> List[MergeRecommendation]:
    """
    识别功能相似的模块

    Args:
        inventory: 模块清单

    Returns:
        合并建议列表
    """
    print("\n正在分析功能相似的模块...")

    recommendations = []

    # 按类别分组
    by_category = {}
    for cat in CategoryEnum:
        by_category[cat] = inventory.get_modules_by_category(cat)

    # 在每个类别中查找相似模块
    for category, modules in by_category.items():
        if len(modules) < 2:
            continue

        # 按目录分组
        by_directory = defaultdict(list)
        for module in modules:
            directory = str(Path(module.file_path).parent)
            by_directory[directory].append(module)

        # 在同目录下查找相似模块
        for directory, dir_modules in by_directory.items():
            if len(dir_modules) < 2:
                continue

            # 查找名称相似的模块
            similar_groups = find_similar_module_names(dir_modules)

            for group in similar_groups:
                if len(group) >= 2:
                    rec = create_merge_recommendation_for_group(group, category)
                    if rec:
                        recommendations.append(rec)

    print(f"  发现 {len(recommendations)} 个合并机会")

    return recommendations


def find_similar_module_names(modules: List) -> List[List]:
    """找出名称相似的模块组"""
    groups = []

    # 提取模块名称关键词
    module_keywords = defaultdict(list)

    for module in modules:
        name = Path(module.file_path).stem
        # 提取关键词（假设使用下划线分隔）
        keywords = name.split("_")

        for keyword in keywords:
            if keyword not in ["test", "simple", "new", "old", "tmp"]:
                module_keywords[keyword].append(module)

    # 找出包含相同关键词的模块组（至少 2 个模块）
    for keyword, module_list in module_keywords.items():
        if len(module_list) >= 2:
            groups.append(module_list)

    return groups


def create_merge_recommendation_for_group(
    modules: List, category: CategoryEnum
) -> MergeRecommendation:
    """为模块组创建合并建议"""

    if len(modules) < 2:
        return None

    # 分析共同特征
    all_classes = set()
    all_functions = set()

    for module in modules:
        for cls in module.classes:
            all_classes.add(cls.name)
        for func in module.functions:
            all_functions.add(func.name)

    # 生成建议
    module_paths = [m.file_path for m in modules]
    base_names = [Path(p).stem for p in module_paths]

    # 建议的新模块名
    common_prefix = find_common_prefix(base_names)
    new_name = common_prefix if common_prefix else "merged_module"

    rec = MergeRecommendation(
        id=f"MERGE-{category.value.upper()}-{len(module_paths):02d}",
        title=f"合并 {len(modules)} 个 {category.value} 模块",
        modules_to_merge=module_paths,
        common_functionality=f"这些模块都属于 {category.value} 类别，"
        f"包含 {len(all_classes)} 个类和 {len(all_functions)} 个函数。"
        f"它们位于同一目录下，功能相关。",
        merge_strategy=generate_merge_strategy(modules, new_name),
        new_module_name=new_name + ".py",
        migration_steps=generate_migration_steps(modules, new_name),
        risk_level=assess_risk_level(modules),
        effort_estimate=estimate_merge_effort(modules),
    )

    return rec


def find_common_prefix(names: List[str]) -> str:
    """找出名称的公共前缀"""
    if not names:
        return ""

    prefix = names[0]
    for name in names[1:]:
        while not name.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""

    return prefix.rstrip("_")


def generate_merge_strategy(modules: List, new_name: str) -> str:
    """生成合并策略"""
    return f"""
**合并方法**:

1. **创建新统一模块** (`{new_name}.py`)
   - 合并所有类定义
   - 统一导入语句
   - 整合文档字符串

2. **处理命名冲突**
   - 如果有同名类或函数，使用命名空间或重命名
   - 保留原有的公共 API

3. **更新导入**
   - 在原模块位置创建兼容层（临时）
   - 从新模块重新导出所有公共 API
   - 添加 DeprecationWarning

4. **测试验证**
   - 运行所有相关测试
   - 确保向后兼容性
   - 验证性能没有下降

5. **逐步迁移**
   - 更新项目内部的导入语句
   - 更新文档
   - 在一段时间后移除旧模块
"""


def generate_migration_steps(modules: List, new_name: str) -> List[str]:
    """生成迁移步骤"""
    return [
        f"创建新模块 {new_name}.py",
        f"合并 {len(modules)} 个模块的代码到新模块",
        "解决命名冲突（如有）",
        "在原模块位置添加弃用警告和导入重定向",
        "更新所有内部导入语句",
        "运行完整测试套件",
        "更新文档和注释",
        "审查并合并代码",
        "监控 1-2 周确保稳定",
        "移除旧模块",
    ]


def assess_risk_level(modules: List) -> str:
    """评估合并风险"""
    total_lines = sum(m.lines_of_code for m in modules)
    total_functions = sum(
        len(m.functions) + sum(len(c.methods) for c in m.classes) for m in modules
    )

    if total_lines > 1000 or total_functions > 50:
        return "high"
    elif total_lines > 500 or total_functions > 20:
        return "medium"
    else:
        return "low"


def estimate_merge_effort(modules: List) -> str:
    """估算合并工作量"""
    total_lines = sum(m.lines_of_code for m in modules)

    if total_lines > 1000:
        return "3-5 天"
    elif total_lines > 500:
        return "2-3 天"
    elif total_lines > 200:
        return "1-2 天"
    else:
        return "4-8 小时"


def analyze_duplicate_based_merges(
    duplication_index_path: Path,
) -> List[MergeRecommendation]:
    """
    基于重复分析提供合并建议

    Args:
        duplication_index_path: 重复索引文件路径

    Returns:
        合并建议列表
    """
    print("\n正在分析基于重复的合并机会...")

    recommendations = []

    if not duplication_index_path.exists():
        print("  警告: 重复索引文件不存在，跳过此分析")
        return recommendations

    with open(duplication_index_path, "r", encoding="utf-8") as f:
        dup_data = json.load(f)

    # 找出涉及相同文件组的高严重性重复
    file_groups = defaultdict(list)

    for dup in dup_data["duplications"]:
        if dup["severity"] in ["critical", "high"]:
            files = tuple(sorted(dup["affected_files"]))
            if len(files) >= 2:
                file_groups[files].append(dup)

    # 为每个文件组创建合并建议
    for files, dups in file_groups.items():
        if len(dups) >= 3:  # 至少 3 个重复案例
            rec = MergeRecommendation(
                id=f"MERGE-DUP-{len(recommendations)+1:03d}",
                title=f"基于重复合并 {len(files)} 个模块",
                modules_to_merge=list(files),
                common_functionality=f"这些模块之间存在 {len(dups)} 个高严重性代码重复。"
                f"重复的代码模式表明它们有共同的功能。",
                merge_strategy=f"""
**基于重复的合并策略**:

1. **识别重复代码**
   - 已检测到 {len(dups)} 处重复

2. **提取公共功能**
   - 将重复代码提取到新的基类或工具函数
   - 保留特定于模块的差异

3. **重构现有代码**
   - 用公共函数替换重复代码
   - 参数化差异部分

4. **考虑完全合并**
   - 如果差异很小，考虑完全合并模块
   - 使用配置或参数处理差异
""",
                migration_steps=[
                    "分析所有重复案例",
                    "提取公共代码到新模块",
                    "重构每个模块使用公共代码",
                    "测试所有模块",
                    "评估是否需要完全合并",
                ],
                risk_level="medium",
                effort_estimate="2-4 天",
                related_duplications=[d["id"] for d in dups],
            )
            recommendations.append(rec)

    print(f"  发现 {len(recommendations)} 个基于重复的合并机会")

    return recommendations


def analyze_utility_consolidation(
    inventory: ModuleInventory,
) -> List[MergeRecommendation]:
    """
    分析工具类模块的合并机会

    Args:
        inventory: 模块清单

    Returns:
        合并建议列表
    """
    print("\n正在分析工具类模块合并机会...")

    recommendations = []

    utility_modules = inventory.get_modules_by_category(CategoryEnum.UTILITY)

    if len(utility_modules) > 10:  # 工具模块过多
        # 按功能分组
        date_utils = []
        string_utils = []
        validation_utils = []
        other_utils = []

        for module in utility_modules:
            name = Path(module.file_path).stem.lower()
            if "date" in name or "time" in name:
                date_utils.append(module)
            elif "string" in name or "text" in name or "symbol" in name:
                string_utils.append(module)
            elif "valid" in name or "check" in name:
                validation_utils.append(module)
            else:
                other_utils.append(module)

        # 为每组创建合并建议
        groups = [
            ("date_time_utils", date_utils, "日期和时间"),
            ("string_utils", string_utils, "字符串和符号"),
            ("validation_utils", validation_utils, "数据验证"),
        ]

        for new_name, modules, desc in groups:
            if len(modules) >= 2:
                rec = MergeRecommendation(
                    id=f"MERGE-UTIL-{new_name.upper()}",
                    title=f"整合{desc}工具模块",
                    modules_to_merge=[m.file_path for m in modules],
                    common_functionality=f"这 {len(modules)} 个模块都提供{desc}相关的工具函数，"
                    f"可以合并为单一的工具模块。",
                    merge_strategy=f"""
**工具模块整合策略**:

1. **创建统一工具模块** (`{new_name}.py`)
   - 按功能组织函数
   - 添加清晰的注释分隔不同功能区

2. **保持简洁**
   - 只保留公共 API
   - 移除内部使用的辅助函数到私有模块

3. **向后兼容**
   - 在原位置保留别名导入
   - 逐步迁移使用方

4. **文档化**
   - 为每个工具函数添加清晰文档
   - 提供使用示例
""",
                    new_module_name=f"{new_name}.py",
                    migration_steps=[
                        f"创建新的 {new_name}.py",
                        "合并所有工具函数",
                        "添加完整文档",
                        "在原位置添加导入重定向",
                        "更新所有导入语句",
                        "移除旧模块",
                    ],
                    risk_level="low",
                    effort_estimate="1-2 天",
                )
                recommendations.append(rec)

    print(f"  发现 {len(recommendations)} 个工具模块合并机会")

    return recommendations


def save_consolidation_guide(guide: ConsolidationGuide, output_path: str):
    """保存合并指南到 JSON"""

    data = {
        "total_recommendations": len(guide.recommendations),
        "by_risk_level": {
            "low": len(guide.get_by_risk_level("low")),
            "medium": len(guide.get_by_risk_level("medium")),
            "high": len(guide.get_by_risk_level("high")),
        },
        "high_impact": len(guide.get_high_impact()),
        "recommendations": [
            {
                "id": rec.id,
                "title": rec.title,
                "modules_to_merge": rec.modules_to_merge,
                "common_functionality": rec.common_functionality,
                "merge_strategy": rec.merge_strategy,
                "new_module_name": rec.new_module_name,
                "migration_steps": rec.migration_steps,
                "risk_level": rec.risk_level,
                "effort_estimate": rec.effort_estimate,
            }
            for rec in guide.recommendations
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 合并指南已保存: {output_path}")


def main():
    """主函数"""
    print("MyStocks 模块合并指南生成器")
    print("=" * 60)

    # 加载清单
    inventory_path = (
        PROJECT_ROOT
        / "docs/function-classification-manual/metadata/module-inventory.json"
    )

    if not inventory_path.exists():
        print(f"\n✗ 错误: 清单文件不存在: {inventory_path}")
        return

    print(f"\n加载清单: {inventory_path}")
    inventory = load_inventory(str(inventory_path))
    print(f"✓ 加载完成，共 {len(inventory.modules)} 个模块")

    # 创建合并指南
    guide = ConsolidationGuide()

    # 分析相似模块
    similar_recs = analyze_similar_modules(inventory)
    for rec in similar_recs:
        guide.add_recommendation(rec)

    # 基于重复的合并
    dup_index_path = (
        PROJECT_ROOT
        / "docs/function-classification-manual/metadata/duplication-index.json"
    )
    dup_recs = analyze_duplicate_based_merges(dup_index_path)
    for rec in dup_recs:
        guide.add_recommendation(rec)

    # 工具模块整合
    util_recs = analyze_utility_consolidation(inventory)
    for rec in util_recs:
        guide.add_recommendation(rec)

    # 统计
    print("\n" + "=" * 60)
    print("合并指南生成完成")
    print("=" * 60)
    print(f"\n总合并建议: {len(guide.recommendations)}")
    print(f"\n按风险级别:")
    print(f"  低风险: {len(guide.get_by_risk_level('low'))}")
    print(f"  中风险: {len(guide.get_by_risk_level('medium'))}")
    print(f"  高风险: {len(guide.get_by_risk_level('high'))}")
    print(f"\n高影响合并（3+ 模块）: {len(guide.get_high_impact())}")

    # 保存结果
    output_dir = PROJECT_ROOT / "docs/function-classification-manual/metadata"
    output_path = output_dir / "consolidation-guide.json"
    save_consolidation_guide(guide, str(output_path))

    # 生成 Markdown 文档
    from src.utils.markdown_writer import MarkdownWriter

    writer = MarkdownWriter(str(PROJECT_ROOT / "docs/function-classification-manual"))
    doc_path = writer.generate_consolidation_guide(guide)
    print(f"✓ 完整文档已生成: {doc_path}")

    print("\n✓ 合并指南生成完成!")

    return guide


if __name__ == "__main__":
    main()
