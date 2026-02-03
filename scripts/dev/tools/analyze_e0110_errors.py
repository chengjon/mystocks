#!/usr/bin/env python3
"""
快速分析abstract-class-instantiated错误分布

用法:
python scripts/tools/analyze_e0110_errors.py
"""

import subprocess
import re
from collections import defaultdict
from pathlib import Path

def main():
    """主函数"""
    print("🔍 分析E0110错误分布...")
    print()

    # 运行Pylint扫描
    cmd = [
        "pylint",
        "src/",
        "web/backend/app/",
        "--rcfile=.pylintrc",
        "--output-format=text",
        "--reports=n"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )

        # 解析输出
        output = result.stdout + result.stderr

        # 提取E0110错误
        e0110_pattern = r"^(.+?):(\d+):\d+:\s+E0110:\s+(.+?)\(abstract-class-instantiated\)"
        errors = re.findall(e0110_pattern, output, re.MULTILINE)

        if not errors:
            print("✅ 未发现E0110错误！")
            return

        # 按文件分组
        file_errors = defaultdict(list)
        for file_path, line_num, message in errors:
            file_errors[file_path].append((line_num, message))

        # 统计
        total_errors = len(errors)
        total_files = len(file_errors)

        print(f"📊 E0110错误统计:")
        print(f"   总错误数: {total_errors}")
        print(f"   涉及文件: {total_files}")
        print()

        # 按目录分组
        dir_stats = defaultdict(int)
        for file_path in file_errors.keys():
            # 提取目录
            if "/" in file_path:
                parts = file_path.split("/")
                if len(parts) >= 2:
                    # 取前两级作为目录
                    dir_name = "/".join(parts[:2])
                    dir_stats[dir_name] += 1
                else:
                    dir_stats[file_path] += 1
            else:
                dir_stats[file_path] += 1

        print("📁 按目录分布:")
        for dir_name, count in sorted(dir_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {dir_name}: {count}个错误")
        print()

        # 详细文件列表（前10个）
        print("📄 错误最多的文件 (Top 10):")
        sorted_files = sorted(file_errors.items(), key=lambda x: len(x[1]), reverse=True)
        for file_path, errors_list in sorted_files[:10]:
            print(f"   {file_path}: {len(errors_list)}个错误")
            # 显示前3个错误
            for line_num, message in errors_list[:3]:
                print(f"      Line {line_num}: {message}")
            if len(errors_list) > 3:
                print(f"      ... 还有 {len(errors_list)-3}个错误")
            print()

    except subprocess.TimeoutExpired:
        print("⏱️ Pylint扫描超时（10分钟）")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
