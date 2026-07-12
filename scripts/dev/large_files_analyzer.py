#!/usr/bin/env python3
"""大文件分析脚本
分析项目中超过2000行的Python文件，提供拆分建议
"""

import os
from pathlib import Path
from typing import List, TypedDict


class FileInfo(TypedDict):
    path: str
    lines: int
    relative_path: str


def analyze_python_files(root_dir: str = "/opt/claude/mystocks_spec"):
    """分析Python文件大小和结构"""
    large_files: List[FileInfo] = []
    total_lines = 0

    print("=== MyStocks 大文件分析报告 ===")
    print("分析时间: 2025-11-25 14:43:19")
    print()

    for root, _, files in os.walk(root_dir):
        # 跳过某些目录
        if any(
            ignore in root
            for ignore in [
                ".git",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                "node_modules",
            ]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        lines = sum(1 for _ in f)
                        total_lines += lines

                    if lines > 2000:
                        large_files.append(
                            FileInfo(
                                path=file_path,
                                lines=lines,
                                relative_path=os.path.relpath(file_path, root_dir),
                            ),
                        )
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # 按行数排序
    large_files.sort(key=lambda x: x["lines"], reverse=True)

    print(f"总Python文件数: {len(list(Path(root_dir).rglob('*.py')))}")
    print(f"总代码行数: {total_lines:,}")
    print(f"超过2000行的文件: {len(large_files)}个")
    print()

    if large_files:
        print("超大文件列表 (建议拆分):")
        print("=" * 80)

        for i, file_info in enumerate(large_files, 1):
            print(f"{i}. {file_info['relative_path']}")
            print(f"   行数: {file_info['lines']:,}")
            print(f"   路径: {file_info['path']}")

            # 提供拆分建议
            suggest_split(file_info["path"], file_info["lines"])
            print()

    return large_files


def suggest_split(file_path, lines):
    """为文件提供拆分建议"""
    file_name = os.path.basename(file_path)

    # 基于文件名和路径提供拆分建议
    if "test_exchange.py" in file_name:
        print("   拆分建议:")
        print("   ├── test_exchange_core.py (核心测试)")
        print("   ├── test_exchange_pairs.py (货币对测试)")
        print("   ├── test_exchange_orders.py (订单测试)")
        print("   └── test_exchange_api.py (API测试)")

    elif "test_freqtradebot.py" in file_name:
        print("   拆分建议:")
        print("   ├── test_freqtradebot_core.py (核心机器人测试)")
        print("   ├── test_freqtradebot_strategies.py (策略测试)")
        print("   └── test_freqtradebot_rpc.py (RPC测试)")

    elif "exchange.py" in file_name:
        print("   拆分建议:")
        print("   ├── exchange_core.py (交易所核心类)")
        print("   ├── exchange_api.py (交易所API接口)")
        print("   ├── exchange_pairs.py (交易对处理)")
        print("   └── exchange_websocket.py (WebSocket连接)")

    elif "conftest.py" in file_name:
        print("   拆分建议:")
        print("   ├── conftest_base.py (基础配置)")
        print("   ├── conftest_fixtures.py (测试fixture)")
        print("   └── conftest_helpers.py (测试辅助函数)")

    else:
        print("   拆分建议: 按功能模块拆分，如:")
        print(f"   ├── {file_name[:-3]}_core.py (核心功能)")
        print(f"   ├── {file_name[:-3]}_utils.py (工具函数)")
        print(f"   └── {file_name[:-3]}_constants.py (常量定义)")


if __name__ == "__main__":
    large_files = analyze_python_files()

    if not large_files:
        print("✅ 所有Python文件都符合大小规范 (≤2000行)")
    else:
        print(
            f"\n📝 建议优先处理前{len([f for f in large_files if f['lines'] > 3000])}个超过3000行的文件",
        )
