#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime


# 配置文件数量阈值
MAX_NEW_FILES = 10

# 记录每次提交的文件数量基线
BASELINE_FILE = "scripts/dev/file_count_baseline.json"


def count_python_files(directory):
    """统计目录中的Python文件数量"""
    count = 0
    for root, _, files in os.walk(directory):
        # 忽略特定目录
        if any(
            ignore_dir in root
            for ignore_dir in [
                ".git",
                "__pycache__",
                ".pytest_cache",
                "node_modules",
                ".mypy_cache",
            ]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                count += 1
    return count


def update_baseline(count):
    """更新基线文件"""
    baseline = {}
    if os.path.exists(BASELINE_FILE):
        with open(BASELINE_FILE) as f:
            baseline = json.load(f)

    baseline["last_count"] = count
    baseline["last_update"] = str(datetime.now())

    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f)


def get_baseline():
    """获取基线数量"""
    if not os.path.exists(BASELINE_FILE):
        return None

    with open(BASELINE_FILE) as f:
        baseline = json.load(f)
        return baseline.get("last_count")


if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    current_count = count_python_files(directory)
    baseline_count = get_baseline()

    if baseline_count is None:
        print(f"📝 首次运行，保存当前文件数量为基线: {current_count}")
        update_baseline(current_count)
        sys.exit(0)

    new_files = current_count - baseline_count
    if new_files > MAX_NEW_FILES:
        print(f"❌ 新增文件数量({new_files})超过限制({MAX_NEW_FILES})")
        print(f"当前文件总数: {current_count}")
        print(f"基线文件总数: {baseline_count}")
        sys.exit(1)

    if new_files > 0:
        print(f"ℹ️ 本次提交新增 {new_files} 个Python文件")
        print(f"当前文件总数: {current_count}")
        print(f"基线文件总数: {baseline_count}")
        update_baseline(current_count)
    else:
        print(f"✅ Python文件数量检查通过: {current_count}")
