#!/usr/bin/env python3
"""
自动化修复测试文件导入路径

修复旧的导入路径为新的 src/ 结构:
- from unified_manager import → from src.core.unified_manager import
- from core import → from src.core import
- from db_manager import → from src.db_manager import
- from adapters import → from src.adapters import
- from interfaces import → from src.interfaces import

创建日期: 2026-01-03
用途: Task 1.3 - 批量修复测试导入路径
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 导入路径映射规则
IMPORT_REPLACEMENTS = [
    # 核心模块
    (r'\bfrom unified_manager import', 'from src.core.unified_manager import'),
    (r'\bfrom core import', 'from src.core import'),
    (r'\bfrom core\.(\w+) import', r'from src.core.\1 import'),

    # 数据库管理
    (r'\bfrom db_manager import', 'from src.db_manager import'),
    (r'\bfrom db_manager\.(\w+) import', r'from src.db_manager.\1 import'),

    # 适配器
    (r'\bfrom adapters import', 'from src.adapters import'),
    (r'\bfrom adapters\.(\w+) import', r'from src.adapters.\1 import'),

    # 接口
    (r'\bfrom interfaces import', 'from src.interfaces import'),
    (r'\bfrom interfaces\.(\w+) import', r'from src.interfaces.\1 import'),

    # 存储层
    (r'\bfrom storage import', 'from src.storage import'),
    (r'\bfrom storage\.(\w+) import', r'from src.storage.\1 import'),

    # 监控
    (r'\bfrom monitoring import', 'from src.monitoring import'),
    (r'\bfrom monitoring\.(\w+) import', r'from src.monitoring.\1 import'),
]


def find_test_files(root_dir: Path) -> List[Path]:
    """
    查找所有测试文件

    Args:
        root_dir: 项目根目录

    Returns:
        测试文件路径列表
    """
    test_files = []

    # 查找tests/目录下的所有.py文件
    tests_dir = root_dir / "tests"
    if tests_dir.exists():
        test_files.extend(tests_dir.rglob("test_*.py"))
        test_files.extend(tests_dir.rglob("*_test.py"))

    # 查找根目录的test_*.py文件
    test_files.extend(root_dir.glob("test_*.py"))

    return sorted(set(test_files))


def fix_imports_in_file(file_path: Path, dry_run: bool = False) -> Tuple[int, int]:
    """
    修复单个文件的导入路径

    Args:
        file_path: 文件路径
        dry_run: 是否为演练模式（不实际修改文件）

    Returns:
        (替换数量, 错误数量)
    """
    try:
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        replacements_count = 0

        # 应用所有替换规则
        for pattern, replacement in IMPORT_REPLACEMENTS:
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                replacements_count += count
                content = new_content

        # 如果有修改且不是演练模式，写回文件
        if replacements_count > 0 and not dry_run:
            file_path.write_text(content, encoding='utf-8')

        return replacements_count, 0

    except Exception as e:
        return 0, 1


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='修复测试文件导入路径')
    parser.add_argument('--dry-run', action='store_true', help='演练模式，不实际修改文件')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    args = parser.parse_args()

    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent

    print("=" * 80)
    print("测试文件导入路径修复工具")
    print("=" * 80)
    print(f"项目根目录: {project_root}")
    print(f"演练模式: {'是' if args.dry_run else '否'}")
    print()

    # 查找所有测试文件
    test_files = find_test_files(project_root)
    print(f"找到 {len(test_files)} 个测试文件")

    if args.verbose:
        print("\n测试文件列表:")
        for i, f in enumerate(test_files, 1):
            print(f"  {i}. {f.relative_to(project_root)}")
        print()

    # 修复每个文件
    total_replacements = 0
    total_errors = 0
    modified_files = []

    print("\n开始处理...")
    for i, test_file in enumerate(test_files, 1):
        replacements, errors = fix_imports_in_file(test_file, args.dry_run)

        if replacements > 0:
            modified_files.append(test_file)
            total_replacements += replacements
            print(f"  [{i}/{len(test_files)}] {test_file.relative_to(project_root)} - {replacements} 处替换")

        if errors > 0:
            total_errors += errors
            print(f"  [{i}/{len(test_files)}] {test_file.relative_to(project_root)} - 错误!")

    # 输出统计
    print()
    print("=" * 80)
    print("处理完成")
    print("=" * 80)
    print(f"处理文件数: {len(test_files)}")
    print(f"修改文件数: {len(modified_files)}")
    print(f"总替换数: {total_replacements}")
    print(f"错误数: {total_errors}")
    print()

    if modified_files and args.verbose:
        print("修改的文件:")
        for f in modified_files:
            print(f"  - {f.relative_to(project_root)}")
        print()

    if args.dry_run and total_replacements > 0:
        print("⚠️  演练模式: 未实际修改文件")
        print("   使用不带 --dry-run 参数重新运行以应用修改")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    exit(main())
