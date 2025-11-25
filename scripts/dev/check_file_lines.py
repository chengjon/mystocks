#!/usr/bin/env python3
import os
import sys
import re
import fnmatch
from pathlib import Path

# 配置文件大小阈值
MAX_FILE_LINES = 2000
MIN_FILE_LINES = 50

# 例外文件：允许超行数的特殊文件（需注释原因）
EXCEPTION_FILES = [
    "src/common/large_config.py",  # 配置类文件，需集中管理所有配置项
    "src/auto_gen/*.py",  # 自动生成的代码，无法拆分
    "*/archive/*",  # 归档目录中的历史文件
    "*/.archive/*"  # 归档目录中的历史文件
]

# 小文件合理性校验：自动标记为"合理小文件"不触发警告
REASONABLE_SMALL_FILES = [
    "*/constants.py",
    "*/enums.py",
    "*/config/*.py",
    "*/hooks/*.py"
]

def is_exception_file(file_path):
    """检查文件是否为例外文件"""
    file_path = file_path.replace('\\', '/')
    for pattern in EXCEPTION_FILES:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def is_reasonable_small_file(file_path):
    """检查文件是否为合理小文件"""
    file_path = file_path.replace('\\', '/')
    for pattern in REASONABLE_SMALL_FILES:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def check_files(directory):
    """检查目录中的Python文件行数"""
    large_files = []
    small_files = []
    skipped_files = []
    
    for root, _, files in os.walk(directory):
        # 忽略特定目录
        if any(ignore_dir in root for ignore_dir in ['.git', '__pycache__', '.pytest_cache', 'node_modules', 'node_modules', 'node_modules', 'node_modules', 'node_modules']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = sum(1 for line in f if line.strip())  # 只统计非空行
                        
                    if is_exception_file(file_path):
                        skipped_files.append(f"{file_path}: {lines} lines (例外文件)")
                    elif lines > MAX_FILE_LINES:
                        large_files.append(f"{file_path}: {lines} lines")
                    elif lines < MIN_FILE_LINES and not is_reasonable_small_file(file_path):
                        small_files.append(f"{file_path}: {lines} lines")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return large_files, small_files, skipped_files

if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    large_files, small_files, skipped_files = check_files(directory)
    
    # 输出跳过的例外文件
    if skipped_files:
        print("ℹ️ 跳过的例外文件:")
        for file in skipped_files:
            print(f"  {file}")
    
    if large_files:
        print("❌ 以下文件超过行数限制:")
        for file in large_files:
            print(f"  {file}")
        print("💡 处理建议: 请按功能拆分该文件，参考拆分规范")
        sys.exit(1)
    
    if small_files:
        print("⚠️ 以下文件少于最小行数限制:")
        for file in small_files:
            print(f"  {file}")
        print("💡 处理建议: 考虑合并相关小文件或提供独立存在的理由")
        # 小文件不影响检查结果，只给出警告
    
    print("✅ 所有文件行数检查通过")