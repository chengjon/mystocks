#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查文件大小脚本

用于检查Python文件是否超过2000行，并报告违反《代码文件长度优化规范》的文件。

使用方法:
    python check_file_sizes.py
    python check_file_sizes.py --limit 1500  # 设置自定义限制
    python check_file_sizes.py --exclude-dir temp  # 排除特定目录

作者: MyStocks开发团队
日期: 2025-11-25
"""

import os
import sys
import argparse
import json
from pathlib import Path


def find_python_files(root_dir, exclude_dirs=None, exclude_files=None):
    """查找Python文件，排除指定目录和文件"""
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
    
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # 排除指定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py') and file not in exclude_files:
                python_files.append(os.path.join(root, file))
    
    return python_files


def get_file_line_count(file_path):
    """获取文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except (IOError, UnicodeDecodeError):
        try:
            # 尝试使用其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                return sum(1 for _ in f)
        except (IOError, UnicodeDecodeError):
            return 0


def check_file_sizes(root_dir, limit=2000, exclude_dirs=None, exclude_files=None):
    """检查文件大小"""
    python_files = find_python_files(root_dir, exclude_dirs, exclude_files)
    
    oversized_files = []
    total_files = len(python_files)
    oversized_count = 0
    
    for file_path in python_files:
        line_count = get_file_line_count(file_path)
        
        if line_count > limit:
            oversized_files.append({
                'path': file_path,
                'lines': line_count
            })
            oversized_count += 1
    
    return {
        'total_files': total_files,
        'oversized_files': oversized_files,
        'oversized_count': oversized_count,
        'limit': limit
    }


def print_report(report, output_format='text'):
    """打印报告"""
    if output_format == 'json':
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"\n文件大小检查报告")
        print(f"=====================")
        print(f"检查限制: {report['limit']} 行")
        print(f"总文件数: {report['total_files']}")
        print(f"超过限制的文件数: {report['oversized_count']}")
        
        if report['oversized_files']:
            print("\n超过限制的文件:")
            for file_info in sorted(report['oversized_files'], key=lambda x: x['lines'], reverse=True):
                print(f"  - {file_info['path']}: {file_info['lines']} 行")
        else:
            print("\n没有文件超过限制。")
        
        print("\n建议:")
        if report['oversized_files']:
            print("  - 根据《代码文件长度优化规范》，建议对这些文件进行模块化拆分")
            print("  - 参考 'docs/guides/MODULAR_CODE_USAGE_GUIDE.md' 了解拆分最佳实践")
        else:
            print("  - 所有文件都符合《代码文件长度优化规范》")


def main():
    parser = argparse.ArgumentParser(description='检查Python文件大小')
    parser.add_argument('--limit', type=int, default=2000,
                        help='文件行数限制，默认为2000')
    parser.add_argument('--exclude-dir', action='append', default=[],
                        help='排除的目录名称，可以多次使用')
    parser.add_argument('--exclude-file', action='append', default=[],
                        help='排除的文件名，可以多次使用')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='输出格式，默认为文本格式')
    parser.add_argument('--root-dir', type=str, default='.',
                        help='检查的根目录，默认为当前目录')
    
    args = parser.parse_args()
    
    # 默认排除目录
    exclude_dirs = ['.git', '__pycache__', '.pytest_cache', '.mypy_cache', 'node_modules']
    exclude_dirs.extend(args.exclude_dir)
    
    # 默认排除文件
    exclude_files = []
    exclude_files.extend(args.exclude_file)
    
    # 执行检查
    report = check_file_sizes(args.root_dir, args.limit, exclude_dirs, exclude_files)
    
    # 打印报告
    print_report(report, args.format)
    
    # 返回状态码
    if report['oversized_files']:
        return 1  # 有超过限制的文件
    else:
        return 0  # 所有文件都符合规范


if __name__ == '__main__':
    sys.exit(main())
