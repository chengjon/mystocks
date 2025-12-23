#!/usr/bin/env python3
"""
代码库扫描器 - 扫描整个 MyStocks 项目

扫描所有 Python 文件并提取结构化元数据。

作者: MyStocks Team
日期: 2025-10-19

使用方法:
    python scripts/analysis/scan_codebase.py
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from models import ModuleInventory, ManualMetadata, CategoryEnum
from src.utils.ast_parser import ASTParser
from classifier import ModuleClassifier


def scan_project(project_root: str, exclude_patterns: list = None) -> ModuleInventory:
    """
    扫描整个项目

    Args:
        project_root: 项目根目录
        exclude_patterns: 要排除的路径模式

    Returns:
        ModuleInventory 对象
    """
    if exclude_patterns is None:
        exclude_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            "build",
            "dist",
            ".eggs",
            "temp",
            "temp_docs",
            ".specify",
            "inside",
            "specs",  # 排除规范文档目录
        ]

    print(f"开始扫描项目: {project_root}")
    print(f"排除模式: {exclude_patterns}\n")

    # 创建解析器
    parser = ASTParser(project_root)

    # 扫描目录
    project_path = Path(project_root)
    modules = parser.scan_directory(project_path, exclude_patterns)

    print(f"✓ 扫描完成，发现 {len(modules)} 个 Python 模块\n")

    # 分类模块
    print("开始模块分类...")
    classifier = ModuleClassifier()
    categorized = classifier.classify_batch(modules)

    print("\n分类统计:")
    for category, module_list in categorized.items():
        print(f"  {category.value:15} : {len(module_list):3} 个模块")

    # 创建清单
    inventory = ModuleInventory(modules=modules)

    # 生成元数据
    metadata = ManualMetadata(
        version="1.0.0",
        generation_date=datetime.now(),
        total_modules=len(modules),
        total_classes=inventory.get_total_classes(),
        total_functions=inventory.get_total_functions(),
        total_lines=sum(m.lines_of_code for m in modules),
    )

    # 按类别统计
    for category in CategoryEnum:
        cat_modules = inventory.get_modules_by_category(category)
        if cat_modules:
            metadata.category_stats[category.value] = {
                "modules": len(cat_modules),
                "classes": sum(len(m.classes) for m in cat_modules),
                "functions": sum(
                    len(m.functions) + sum(len(c.methods) for c in m.classes)
                    for m in cat_modules
                ),
                "lines": sum(m.lines_of_code for m in cat_modules),
            }

    # 计算平均复杂度
    all_functions = []
    for module in modules:
        all_functions.extend(module.functions)
        for cls in module.classes:
            all_functions.extend(cls.methods)

    if all_functions:
        complexities = [f.complexity for f in all_functions]
        metadata.avg_function_complexity = sum(complexities) / len(complexities)
        metadata.max_function_complexity = max(complexities)

    inventory.metadata = metadata

    return inventory


def save_inventory(inventory: ModuleInventory, output_path: str):
    """
    保存清单到 JSON 文件

    Args:
        inventory: 模块清单
        output_path: 输出文件路径
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 转换为可序列化的字典
    data = {
        "metadata": {
            "version": inventory.metadata.version,
            "generation_date": inventory.metadata.generation_date.isoformat(),
            "total_modules": inventory.metadata.total_modules,
            "total_classes": inventory.metadata.total_classes,
            "total_functions": inventory.metadata.total_functions,
            "total_lines": inventory.metadata.total_lines,
            "avg_function_complexity": inventory.metadata.avg_function_complexity,
            "max_function_complexity": inventory.metadata.max_function_complexity,
            "category_stats": inventory.metadata.category_stats,
        },
        "modules": [],
    }

    for module in inventory.modules:
        module_dict = {
            "file_path": module.file_path,
            "module_name": module.module_name,
            "category": module.category.value,
            "docstring": module.docstring,
            "lines_of_code": module.lines_of_code,
            "blank_lines": module.blank_lines,
            "comment_lines": module.comment_lines,
            "last_modified": (
                module.last_modified.isoformat() if module.last_modified else None
            ),
            "imports": module.imports,
            "classes": [],
            "functions": [],
        }

        # 添加类
        for cls in module.classes:
            class_dict = {
                "name": cls.name,
                "line_number": cls.line_number,
                "base_classes": cls.base_classes,
                "docstring": cls.docstring,
                "decorators": cls.decorators,
                "is_abstract": cls.is_abstract,
                "methods": [],
            }

            for method in cls.methods:
                method_dict = {
                    "name": method.name,
                    "line_number": method.line_number,
                    "return_type": method.return_type,
                    "docstring": method.docstring,
                    "is_async": method.is_async,
                    "decorators": method.decorators,
                    "body_lines": method.body_lines,
                    "complexity": method.complexity,
                    "parameters": [
                        {
                            "name": p.name,
                            "type_annotation": p.type_annotation,
                            "default_value": p.default_value,
                            "is_required": p.is_required,
                        }
                        for p in method.parameters
                    ],
                }
                class_dict["methods"].append(method_dict)

            module_dict["classes"].append(class_dict)

        # 添加函数
        for func in module.functions:
            func_dict = {
                "name": func.name,
                "line_number": func.line_number,
                "return_type": func.return_type,
                "docstring": func.docstring,
                "is_async": func.is_async,
                "decorators": func.decorators,
                "body_lines": func.body_lines,
                "complexity": func.complexity,
                "parameters": [
                    {
                        "name": p.name,
                        "type_annotation": p.type_annotation,
                        "default_value": p.default_value,
                        "is_required": p.is_required,
                    }
                    for p in func.parameters
                ],
            }
            module_dict["functions"].append(func_dict)

        data["modules"].append(module_dict)

    # 写入 JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 清单已保存到: {output_file}")


def print_summary(inventory: ModuleInventory):
    """打印扫描摘要"""
    print("\n" + "=" * 60)
    print("扫描摘要")
    print("=" * 60)

    metadata = inventory.metadata

    print("\n总体统计:")
    print(f"  模块数量: {metadata.total_modules}")
    print(f"  类数量: {metadata.total_classes}")
    print(f"  函数数量: {metadata.total_functions}")
    print(f"  总代码行: {metadata.total_lines:,}")
    print(f"  平均函数复杂度: {metadata.avg_function_complexity:.2f}")
    print(f"  最大函数复杂度: {metadata.max_function_complexity}")

    print("\n分类统计:")
    category_names = {
        "core": "核心功能",
        "auxiliary": "辅助功能",
        "infrastructure": "基础设施",
        "monitoring": "监控功能",
        "utility": "工具功能",
        "unknown": "未分类",
    }

    for cat_key, cat_name in category_names.items():
        if cat_key in metadata.category_stats:
            stats = metadata.category_stats[cat_key]
            print(
                f"  {cat_name:10} : {stats['modules']:3} 模块, "
                f"{stats['functions']:4} 函数, {stats['lines']:6,} 行"
            )

    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("MyStocks 代码库扫描器")
    print("=" * 60)

    # 扫描项目
    inventory = scan_project(str(PROJECT_ROOT))

    # 打印摘要
    print_summary(inventory)

    # 保存清单
    output_path = (
        PROJECT_ROOT
        / "docs/function-classification-manual/metadata/module-inventory.json"
    )
    save_inventory(inventory, str(output_path))

    print("\n✓ 扫描完成!")
    print(f"  清单文件: {output_path}")
    print(f"  模块数量: {len(inventory.modules)}")

    return inventory


if __name__ == "__main__":
    main()
