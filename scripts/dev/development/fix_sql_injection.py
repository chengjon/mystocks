#!/usr/bin/env python3
"""
SQL注入自动化修复脚本

自动扫描并修复src/data_access/目录中的SQL注入漏洞。

运行方式:
    python scripts/dev/fix_sql_injection.py --dry-run  # 预览修复
    python scripts/dev/fix_sql_injection.py --apply      # 应用修复

版本: 1.0.0
创建日期: 2026-01-10
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def find_sql_injections(file_path: str) -> List[Tuple[int, str, str]]:
    """
    扫描文件中的SQL注入点

    Args:
        file_path: 文件路径

    Returns:
        检测到的SQL注入列表 [(行号, 类型, 代码片段), ...]
    """
    injections = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # 检测f-string SQL注入模式
        patterns = [
            (r'f["\'].*INSERT INTO\s+\{', 'INSERT注入'),
            (r'f["\'].*DELETE FROM\s+\{', 'DELETE注入'),
            (r'f["\'].*SELECT.*WHERE.*\{', 'SELECT注入'),
            (r'f["\'].*UPDATE.*SET.*\{', 'UPDATE注入'),
        ]

        for pattern, injection_type in patterns:
            if re.search(pattern, line):
                # 提取代码片段（前后各2行）
                start = max(0, i - 3)
                end = min(len(lines), i + 2)
                snippet = ''.join(lines[start:end])

                injections.append((i, injection_type, snippet))
                break  # 一行只记录一次

    return injections


def fix_sql_injection_in_line(line: str) -> str:
    """
    修复单行中的SQL注入

    Args:
        line: 原始代码行

    Returns:
        修复后的代码行
    """
    # 模式1: INSERT INTO {table_name} -> INSERT INTO {safe_table_name}
    if 'INSERT INTO {table_name}' in line:
        line = line.replace('{table_name}', '{safe_table_name}')
        line = line.replace('f"', 'f"# safe_table_name已验证')
        return f"            # 验证表名\n            safe_table_name = validate_table_name(table_name)\n            {line}"

    # 模式2: WHERE txn_id = '{txn_id}' -> WHERE txn_id = '{safe_txn_id}'
    if "WHERE txn_id = '{txn_id}'" in line:
        line = line.replace("'{txn_id}'", "'{safe_txn_id}'")
        return f"            # 转义txn_id\n            safe_txn_id = str(txn_id).replace(\"'\", \"''\")\n            {line}"

    return line


def scan_directory(directory: str) -> dict:
    """
    扫描目录中的所有Python文件

    Args:
        directory: 目录路径

    Returns:
        检测结果字典 {文件路径: [(行号, 类型, 片段), ...]}
    """
    results = {}

    for root, dirs, files in os.walk(directory):
        # 跳过__pycache__和venv
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.venv']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                injections = find_sql_injections(file_path)

                if injections:
                    results[file_path] = injections

    return results


def print_report(results: dict):
    """打印扫描报告"""
    total_files = len(results)
    total_injections = sum(len(injections) for injections in results.values())

    print(f"\n{'='*80}")
    print(f"SQL注入扫描报告")
    print(f"{'='*80}")
    print(f"\n发现 {total_files} 个文件存在SQL注入漏洞，共 {total_injections} 个注入点\n")

    for file_path, injections in results.items():
        print(f"\n📁 {file_path}")
        print(f"   注入点数量: {len(injections)}")

        for line_no, injection_type, snippet in injections[:3]:  # 只显示前3个
            print(f"\n   ⚠️  行 {line_no}: {injection_type}")
            print(f"   代码片段:")
            for line in snippet.split('\n')[:5]:
                print(f"      {line}")


def main():
    parser = argparse.ArgumentParser(description='SQL注入自动化修复工具')
    parser.add_argument('--dry-run', action='store_true', help='预览修复（不修改文件）')
    parser.add_argument('--apply', action='store_true', help='应用修复')
    parser.add_argument('--dir', default='src/data_access', help='要扫描的目录')

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("请指定 --dry-run 或 --apply")
        return 1

    # 扫描目录
    print(f"正在扫描目录: {args.dir}")
    results = scan_directory(args.dir)

    # 打印报告
    print_report(results)

    # 询问是否继续
    if args.dry_run:
        print(f"\n{'='*80}")
        print("⚠️  这是预览模式，未修改任何文件")
        print("💡 使用 --apply 参数应用修复")
        print(f"{'='*80}\n")
    elif args.apply:
        print(f"\n{'='*80}")
        print("🔧 开始应用修复...")
        print(f"{'='*80}\n")

        # TODO: 实际应用修复（需要逐文件处理）
        print("⚠️  自动修复功能开发中")
        print("💡 请根据上述报告手动修复，或使用 sql_injection_fix_helper.py 模块")
        print(f"{'='*80}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
