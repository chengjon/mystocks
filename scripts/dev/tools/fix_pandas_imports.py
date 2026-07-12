#!/usr/bin/env python3
"""批量修复 pandas 导入问题

用途: 为缺少 pandas 导入的文件添加 import pandas as pd
目标: 修复 247 个 undefined-variable 'pd' 错误
"""

import re
from pathlib import Path


def has_pandas_import(file_path: Path) -> bool:
    """检查文件是否已经导入了 pandas"""
    try:
        content = file_path.read_text(encoding="utf-8")

        # 检查各种 pandas 导入形式
        patterns = [
            r"import pandas",
            r"import pandas as pd",
            r"from pandas import",
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                return True

        return False
    except Exception as e:
        print(f"⚠️  读取文件失败 {file_path}: {e}")
        return False


def uses_pandas(file_path: Path) -> bool:
    """检查文件是否使用了 pandas (pd.)"""
    try:
        content = file_path.read_text(encoding="utf-8")
        return bool(re.search(r"\bpd\.", content))
    except Exception:
        return False


def add_pandas_import(file_path: Path) -> bool:
    """在文件中添加 pandas 导入"""
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # 找到最后一个 import 语句的位置
        last_import_idx = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_idx = i

        if last_import_idx == -1:
            # 没有找到 import 语句，在文件开头添加
            insert_idx = 0
            # 跳过文件开头的注释和文档字符串
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # 跳过文档字符串
                    continue
                if not line.strip().startswith("#") and line.strip():
                    insert_idx = i
                    break

            lines.insert(insert_idx, "import pandas as pd")
        else:
            # 在最后一个 import 语句后添加
            lines.insert(last_import_idx + 1, "import pandas as pd")

        # 写回文件
        new_content = "\n".join(lines)
        file_path.write_text(new_content, encoding="utf-8")

        return True
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False


def main():
    """主函数"""
    # 需要修复的文件列表
    files_to_fix = [
        "src/adapters/akshare/adapter_base.py",
        "src/adapters/akshare/base.py",
        "src/adapters/akshare/misc_data.py",
        "src/interfaces/adapters/akshare/base.py",
        "src/interfaces/adapters/akshare/financial_data.py",
        "src/interfaces/adapters/akshare/index_daily.py",
        "src/interfaces/adapters/akshare/industry_data.py",
        "src/interfaces/adapters/akshare/misc_data.py",
        "src/interfaces/adapters/akshare/realtime_data.py",
        "src/interfaces/adapters/akshare/stock_basic.py",
        "src/interfaces/adapters/akshare/stock_daily.py",
        "src/interfaces/adapters/financial/financial_data.py",
        "src/interfaces/adapters/financial/index_components.py",
        "src/interfaces/adapters/financial/market_calendar.py",
        "src/interfaces/adapters/financial/news_data.py",
        "src/interfaces/adapters/financial/realtime_data.py",
        "src/interfaces/adapters/financial/stock_basic.py",
    ]

    print("=" * 80)
    print("🔧 批量修复 pandas 导入问题")
    print("=" * 80)
    print(f"目标文件数: {len(files_to_fix)}")
    print()

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for file_path_str in files_to_fix:
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            error_count += 1
            continue

        # 检查是否已经导入了 pandas
        if has_pandas_import(file_path):
            print(f"✅ 跳过 (已有导入): {file_path}")
            skipped_count += 1
            continue

        # 检查是否使用了 pandas
        if not uses_pandas(file_path):
            print(f"⚠️  跳过 (未使用pd): {file_path}")
            skipped_count += 1
            continue

        # 添加 pandas 导入
        print(f"🔧 修复中: {file_path}", end="")
        if add_pandas_import(file_path):
            print(" ✅")
            fixed_count += 1
        else:
            print(" ❌")
            error_count += 1

    print()
    print("=" * 80)
    print("📊 修复统计")
    print("=" * 80)
    print(f"✅ 成功修复: {fixed_count} 个文件")
    print(f"⏭️  跳过: {skipped_count} 个文件")
    print(f"❌ 错误: {error_count} 个文件")
    print()
    print(f"🎉 预计修复: ~{fixed_count * 15} 个 undefined-variable 错误")


if __name__ == "__main__":
    main()
