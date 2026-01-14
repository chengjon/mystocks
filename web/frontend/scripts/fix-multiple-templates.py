#!/usr/bin/env python3
"""
批量修复 Vue 文件中的多个 <template> 标签问题

Vue 单文件组件只能有一个 <template> 标签。
此脚本删除第一个 <template> 块之后的所有内容。
"""

import os
import re
from pathlib import Path

def fix_multiple_templates(file_path):
    """修复单个文件中的多个模板标签"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找所有 <template> 标签的位置
    template_matches = list(re.finditer(r'<template>', content))

    if len(template_matches) <= 1:
        return 0  # 没有问题

    print(f"  {file_path.name}: Found {len(template_matches)} <template> tags")

    # 保留第一个 <template> 之前的内容
    first_template_end = template_matches[0].end()

    # 查找对应的 </template> 标签
    template_depth = 1
    pos = first_template_end
    first_template_close = -1

    while pos < len(content) and template_depth > 0:
        next_open = content.find('<template>', pos)
        next_close = content.find('</template>', pos)

        if next_close == -1:
            print(f"  ERROR: No closing </template> found!")
            return 0

        if next_open != -1 and next_open < next_close:
            template_depth += 1
            pos = next_open + len('<template>')
        else:
            template_depth -= 1
            if template_depth == 0:
                first_template_close = next_close + len('</template>')
                break
            pos = next_close + len('</template>')

    if first_template_close == -1:
        print(f"  ERROR: Could not find end of first template block")
        return 0

    # 截断文件，保留到第一个 </template> 结束
    # 但需要保留可能的 <script> 和 <style> 块
    remaining_content = content[first_template_close:]

    # 检查是否有 <script> 或 <style> 块
    script_match = re.search(r'<script', remaining_content)
    style_match = re.search(r'<style', remaining_content)

    new_content = content[:first_template_close]

    if script_match:
        # 添加 <script> 块
        script_start = script_match.start()
        remaining_from_script = remaining_content[script_start:]

        # 查找 </script> 结束
        script_end = remaining_from_script.find('</script>')
        if script_end != -1:
            script_end += len('</script>')
            new_content += remaining_from_script[:script_end]
            remaining_from_script = remaining_from_script[script_end:]

            # 查找 <style> 块
            style_match_in_remaining = re.search(r'<style', remaining_from_script)
            if style_match_in_remaining:
                style_start = style_match_in_remaining.start()
                remaining_from_style = remaining_from_script[style_start:]

                style_end = remaining_from_style.find('</style>')
                if style_end != -1:
                    style_end += len('</style>')
                    new_content += remaining_from_style[:style_end]

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  ✅ Fixed: Removed extra templates, kept only first")
    return 1

def main():
    """主函数"""
    src_dir = Path('/opt/claude/mystocks_spec/web/frontend/src/views')

    print("🔍 扫描并修复多个 <template> 标签的问题...")
    fixed_count = 0

    # 查找所有 Vue 文件
    vue_files = list(src_dir.rglob('*.vue'))

    for vue_file in vue_files:
        try:
            fixed = fix_multiple_templates(vue_file)
            if fixed > 0:
                fixed_count += 1
        except Exception as e:
            print(f"❌ Error processing {vue_file}: {e}")

    print(f"\n📊 Summary:")
    print(f"   - Files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
