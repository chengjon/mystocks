#!/usr/bin/env python3
"""
代码重复检测器 - 识别重复和相似代码

分析代码库中的函数和代码块，找出高度相似的部分。

作者: MyStocks Team
日期: 2025-10-19

使用方法:
    python scripts/analysis/detect_duplicates.py
"""

import sys
import json
from pathlib import Path
from typing import Dict
from collections import defaultdict

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from manual_paths import get_manual_metadata_dir, get_manual_root
from models import DuplicationIndex, SeverityEnum, ModuleInventory
from utils.similarity import SimilarityDetector
from utils.ast_parser import extract_code_block
from generate_docs import load_inventory


MANUAL_ROOT = get_manual_root(PROJECT_ROOT)
MANUAL_METADATA_DIR = get_manual_metadata_dir(PROJECT_ROOT)


def detect_function_duplicates(inventory: ModuleInventory) -> DuplicationIndex:
    """
    检测函数级别的重复

    Args:
        inventory: 模块清单

    Returns:
        重复索引
    """
    print("\n正在检测函数级别重复...")

    detector = SimilarityDetector(min_token_similarity=0.6, min_ast_similarity=0.5)
    dup_index = DuplicationIndex()

    # 收集所有函数
    all_functions = []
    for module in inventory.modules:
        # 模块级函数
        for func in module.functions:
            all_functions.append((module.file_path, func, None))

        # 类方法
        for cls in module.classes:
            for method in cls.methods:
                all_functions.append((module.file_path, method, cls.name))

    print(f"  总函数数: {len(all_functions)}")

    # 按函数名分组（相同名称的函数更可能重复）
    functions_by_name = defaultdict(list)
    for file_path, func, class_name in all_functions:
        # 跳过太短的函数
        if func.body_lines < 5:
            continue
        functions_by_name[func.name].append((file_path, func, class_name))

    # 检测每组中的重复
    checked_pairs = set()
    duplicates_found = 0

    for func_name, func_list in functions_by_name.items():
        if len(func_list) < 2:
            continue

        # 比较同名函数
        for i in range(len(func_list)):
            for j in range(i + 1, len(func_list)):
                file1, func1, cls1 = func_list[i]
                file2, func2, cls2 = func_list[j]

                pair_key = tuple(
                    sorted(
                        [f"{file1}:{func1.line_number}", f"{file2}:{func2.line_number}"]
                    )
                )

                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                # 提取代码
                full_path1 = str(PROJECT_ROOT / file1)
                full_path2 = str(PROJECT_ROOT / file2)

                code1 = extract_code_block(
                    full_path1, func1.line_number, func1.line_number + func1.body_lines
                )
                code2 = extract_code_block(
                    full_path2, func2.line_number, func2.line_number + func2.body_lines
                )

                if not code1 or not code2:
                    continue

                # 计算相似度
                token_sim = detector.calculate_token_similarity(code1, code2)
                ast_sim = detector.calculate_ast_similarity(code1, code2)

                # 如果相似度足够高
                if token_sim >= 0.6 and ast_sim >= 0.5:
                    func1_name = f"{cls1}.{func1.name}" if cls1 else func1.name
                    func2_name = f"{cls2}.{func2.name}" if cls2 else func2.name

                    description = f"函数 '{func_name}' 在多处实现中高度相似"

                    dup = detector.create_duplication_case(
                        [
                            (
                                file1,
                                func1.line_number,
                                func1.line_number + func1.body_lines,
                                code1,
                            ),
                            (
                                file2,
                                func2.line_number,
                                func2.line_number + func2.body_lines,
                                code2,
                            ),
                        ],
                        token_sim,
                        ast_sim,
                        description,
                    )

                    dup_index.add_duplication(dup)
                    duplicates_found += 1

    print(f"  ✓ 发现 {duplicates_found} 个重复案例")

    return dup_index


def detect_pattern_duplicates(inventory: ModuleInventory, dup_index: DuplicationIndex):
    """
    检测常见模式重复（如连接数据库的代码）

    Args:
        inventory: 模块清单
        dup_index: 重复索引（将添加新发现）
    """
    print("\n正在检测常见模式重复...")

    # 定义要检测的模式
    patterns = {
        "database_connection": [
            "get_connection",
            "connect",
            "cursor",
            "execute",
            "commit",
            "close",
        ],
        "error_handling": ["try", "except", "finally", "raise", "Exception"],
        "data_validation": ["if", "is None", "raise ValueError", "assert"],
        "logging": ["logger", "log", "info", "error", "warning", "debug"],
    }

    detector = SimilarityDetector(min_token_similarity=0.7, min_ast_similarity=0.6)

    # 按模式分组函数
    for pattern_name, keywords in patterns.items():
        matching_functions = []

        for module in inventory.modules:
            for func in module.functions:
                # 检查函数名或 docstring 是否包含关键词
                func_text = f"{func.name} {func.docstring or ''}".lower()
                if any(kw.lower() in func_text for kw in keywords):
                    matching_functions.append((module.file_path, func))

            for cls in module.classes:
                for method in cls.methods:
                    method_text = f"{method.name} {method.docstring or ''}".lower()
                    if any(kw.lower() in method_text for kw in keywords):
                        matching_functions.append((module.file_path, method))

        if len(matching_functions) >= 3:
            print(f"  模式 '{pattern_name}': {len(matching_functions)} 个匹配函数")

    print("  ✓ 模式分析完成")


def analyze_duplicate_clusters(dup_index: DuplicationIndex) -> Dict:
    """
    分析重复集群（多个文件中的重复）

    Args:
        dup_index: 重复索引

    Returns:
        集群分析结果
    """
    print("\n正在分析重复集群...")

    # 找出影响多个文件的重复
    clusters = defaultdict(list)

    for dup in dup_index.duplications:
        if len(dup.affected_files) >= 2:
            cluster_key = tuple(sorted(dup.affected_files))
            clusters[cluster_key].append(dup)

    # 统计
    multi_file_clusters = {k: v for k, v in clusters.items() if len(k) >= 2}

    print(f"  重复集群数: {len(multi_file_clusters)}")
    print(
        f"  最大集群: {max((len(files) for files in multi_file_clusters.keys()), default=0)} 个文件"
    )

    return {
        "total_clusters": len(multi_file_clusters),
        "clusters": [
            {
                "files": list(files),
                "duplication_count": len(dups),
                "severity_breakdown": {
                    "critical": sum(
                        1 for d in dups if d.severity == SeverityEnum.CRITICAL
                    ),
                    "high": sum(1 for d in dups if d.severity == SeverityEnum.HIGH),
                    "medium": sum(1 for d in dups if d.severity == SeverityEnum.MEDIUM),
                    "low": sum(1 for d in dups if d.severity == SeverityEnum.LOW),
                },
            }
            for files, dups in sorted(
                multi_file_clusters.items(), key=lambda x: len(x[1]), reverse=True
            )[:10]
        ],
    }


def generate_duplication_summary(dup_index: DuplicationIndex) -> str:
    """生成重复分析摘要"""
    lines = []

    lines.append("# 代码重复分析摘要\n")
    lines.append(f"**总重复案例**: {dup_index.total_cases}\n")

    # 严重性分布
    lines.append("## 严重性分布\n")
    lines.append(f"- CRITICAL: {len(dup_index.critical)} 案例")
    lines.append(f"- HIGH: {len(dup_index.high)} 案例")
    lines.append(f"- MEDIUM: {len(dup_index.medium)} 案例")
    lines.append(f"- LOW: {len(dup_index.low)} 案例\n")

    # Top 5 关键问题
    if dup_index.critical or dup_index.high:
        lines.append("## 🔴 需要立即处理的重复\n")

        critical_and_high = dup_index.critical + dup_index.high
        for i, dup in enumerate(critical_and_high[:5], 1):
            lines.append(f"### {i}. {dup.id}")
            lines.append(f"- **严重性**: {dup.severity.value.upper()}")
            lines.append(
                f"- **相似度**: Token {dup.token_similarity:.0%}, AST {dup.ast_similarity:.0%}"
            )
            lines.append(f"- **位置**: {len(dup.blocks)} 处")
            for block in dup.blocks[:3]:  # 只显示前3处
                lines.append(f"  - `{block.file_path}:{block.start_line}`")
            lines.append("")

    return "\n".join(lines)


def save_duplication_index(dup_index: DuplicationIndex, output_path: str):
    """保存重复索引到 JSON"""

    data = {
        "total_cases": dup_index.total_cases,
        "summary": {
            "critical": len(dup_index.critical),
            "high": len(dup_index.high),
            "medium": len(dup_index.medium),
            "low": len(dup_index.low),
        },
        "duplications": [],
    }

    for dup in dup_index.duplications:
        dup_data = {
            "id": dup.id,
            "severity": dup.severity.value,
            "token_similarity": dup.token_similarity,
            "ast_similarity": dup.ast_similarity,
            "description": dup.description,
            "merge_suggestion": dup.merge_suggestion,
            "affected_files": dup.affected_files,
            "blocks": [
                {
                    "file_path": block.file_path,
                    "start_line": block.start_line,
                    "end_line": block.end_line,
                    "function_name": block.function_name,
                    "class_name": block.class_name,
                }
                for block in dup.blocks
            ],
        }
        data["duplications"].append(dup_data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 重复索引已保存: {output_path}")


def main():
    """主函数"""
    print("MyStocks 代码重复检测器")
    print("=" * 60)

    # 加载清单
    inventory_path = MANUAL_METADATA_DIR / "module-inventory.json"

    if not inventory_path.exists():
        print(f"\n✗ 错误: 清单文件不存在: {inventory_path}")
        print("  请先运行: python scripts/analysis/scan_codebase.py")
        return

    print(f"\n加载清单: {inventory_path}")
    inventory = load_inventory(str(inventory_path))
    print(f"✓ 加载完成，共 {len(inventory.modules)} 个模块")

    # 检测函数重复
    dup_index = detect_function_duplicates(inventory)

    # 检测模式重复
    detect_pattern_duplicates(inventory, dup_index)

    # 分析集群
    cluster_analysis = analyze_duplicate_clusters(dup_index)

    # 生成摘要
    print("\n" + "=" * 60)
    print("重复分析结果")
    print("=" * 60)
    print(f"\n总重复案例: {dup_index.total_cases}")
    print(f"  CRITICAL: {len(dup_index.critical)}")
    print(f"  HIGH: {len(dup_index.high)}")
    print(f"  MEDIUM: {len(dup_index.medium)}")
    print(f"  LOW: {len(dup_index.low)}")
    print(f"\n重复集群: {cluster_analysis['total_clusters']}")

    # 保存结果
    output_dir = MANUAL_METADATA_DIR
    output_path = output_dir / "duplication-index.json"
    save_duplication_index(dup_index, str(output_path))

    # 生成摘要报告
    summary = generate_duplication_summary(dup_index)
    summary_path = MANUAL_ROOT / "duplication-summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"✓ 摘要报告已保存: {summary_path}")

    # 使用 markdown_writer 生成完整文档
    from utils.markdown_writer import MarkdownWriter

    writer = MarkdownWriter(str(MANUAL_ROOT))
    doc_path = writer.generate_duplication_analysis(dup_index)
    print(f"✓ 完整文档已生成: {doc_path}")

    print("\n✓ 重复检测完成!")

    return dup_index, cluster_analysis


if __name__ == "__main__":
    main()
