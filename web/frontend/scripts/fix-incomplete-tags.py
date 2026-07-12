#!/usr/bin/env python3
"""批量修复 Vue 文件中不完整的标签

检测并删除：
1. 不完整的 <ArtDecoStatCard 标签（没有属性和闭合）
2. 其他类似的自闭合标签问题
"""

import re
from pathlib import Path


def fix_incomplete_tags(file_path):
    """修复单个文件中的不完整标签"""
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    fixed_count = 0
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测不完整的标签（只有开始，没有属性和闭合）
        # 模式：<ComponentName 后面直接跟换行或注释
        incomplete_pattern = r"^\s*<[A-Z][a-zA-Z0-9]*\s*$"

        if re.match(incomplete_pattern, stripped):
            # 检查下一行是否是注释
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("<!--"):
                print(f"  Line {i+1}: Found incomplete tag '{stripped}' followed by comment")
                fixed_count += 1
                # 跳过这一行（删除不完整标签）
                i += 1
                continue

        new_lines.append(line)
        i += 1

    if fixed_count > 0:
        # 写回文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Fixed {fixed_count} incomplete tags in {file_path.name}")
        return fixed_count

    return 0

def main():
    """主函数：扫描并修复所有 Vue 文件"""
    src_dir = Path("/opt/claude/mystocks_spec/web/frontend/src/views")

    print("🔍 扫描 Vue 文件中的不完整标签...")
    total_fixed = 0
    fixed_files = 0

    # 查找所有 Vue 文件
    vue_files = list(src_dir.rglob("*.vue"))

    for vue_file in vue_files:
        try:
            fixed = fix_incomplete_tags(vue_file)
            if fixed > 0:
                fixed_files += 1
                total_fixed += fixed
        except Exception as e:
            print(f"❌ Error processing {vue_file}: {e}")

    print("\n📊 Summary:")
    print(f"   - Files fixed: {fixed_files}")
    print(f"   - Total tags removed: {total_fixed}")

if __name__ == "__main__":
    main()
