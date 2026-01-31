#!/usr/bin/env python3
"""
批量修复剩余的导入问题

用途: 修复 HTTPException, numpy, akshare 等缺少的导入
目标: 修复剩余的 ~100 个 undefined-variable 错误
"""
import re
from pathlib import Path


def fix_fastapi_http_exception(file_path: Path) -> bool:
    """添加缺少的 HTTPException 导入"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # 检查是否已经导入了 HTTPException
        if 'HTTPException' in content and 'from fastapi import' in content:
            # 检查是否已经在导入列表中
            if re.search(r'from fastapi import.*HTTPException', content):
                return False  # 已经导入了

        # 检查是否使用了 HTTPException
        if 'HTTPException' not in content:
            return False  # 不需要导入

        # 添加 HTTPException 到 fastapi 导入
        # 查找现有的 fastapi 导入语句
        pattern = r'from fastapi import ([^\n]+)'
        match = re.search(pattern, content)

        if match:
            old_import = match.group(0)
            imported_items = match.group(1).split(',')

            # 添加 HTTPException
            if 'HTTPException' not in imported_items:
                imported_items.append('HTTPException')
                new_import = f"from fastapi import {', '.join(imported_items)}"
                content = content.replace(old_import, new_import)

                file_path.write_text(content, encoding='utf-8')
                return True

        return False
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False


def fix_numpy_import(file_path: Path) -> bool:
    """添加缺少的 numpy 导入"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # 检查是否需要 numpy
        if 'np.' not in content:
            return False

        # 检查是否已经导入了
        if re.search(r'import numpy\s+as\s+np', content):
            return False

        # 查找最后一个 import 语句
        lines = content.split('\n')
        last_import_idx = -1

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                last_import_idx = i

        if last_import_idx == -1:
            # 没有找到 import 语句，在文件开头添加
            insert_idx = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith('#') and line.strip():
                    insert_idx = i
                    break
            lines.insert(insert_idx, 'import numpy as np')
        else:
            # 在最后一个 import 语句后添加
            lines.insert(last_import_idx + 1, 'import numpy as np')

        # 写回文件
        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')

        return True
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False


def fix_akshare_import(file_path: Path) -> bool:
    """添加缺少的 akshare 导入"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # 检查是否需要 akshare
        if 'ak.' not in content:
            return False

        # 检查是否已经导入了
        if re.search(r'import\s+akshare\s+as\s+ak', content):
            return False

        # 查找最后一个 import 语句
        lines = content.split('\n')
        last_import_idx = -1

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                last_import_idx = i

        if last_import_idx == -1:
            insert_idx = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith('#') and line.strip():
                    insert_idx = i
                    break
            lines.insert(insert_idx, 'import akshare as ak')
        else:
            lines.insert(last_import_idx + 1, 'import akshare as ak')

        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')

        return True
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False


def main():
    """主函数"""
    print('=' * 80)
    print('🔧 批量修复剩余导入问题')
    print('=' * 80)
    print('')

    # 需要修复的文件
    fastapi_files = [
        'web/backend/app/api/data.py',
        'web/backend/app/api/market.py',
        'web/backend/app/api/stock_search.py',
    ]

    print('Phase 1: 修复 HTTPException 导入')
    print('-' * 80)
    fixed_count = 0
    for file_path_str in fastapi_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            print(f'🔧 {file_path}', end='')
            if fix_fastapi_http_exception(file_path):
                print(' ✅')
                fixed_count += 1
            else:
                print(' ⏭️ (跳过)')
    print(f'✅ FastAPI 文件修复完成: {fixed_count} 个')
    print('')

    # 查找需要 numpy 的文件
    print('Phase 2: 修复 numpy 导入')
    print('-' * 80)
    # 简化处理：直接检查 src/ 目录下使用 np. 的文件
    # 实际应该从 Pylint 错误中提取
    print('⏭️ 跳过（需要手动验证）')
    print('')

    print('Phase 3: 修复 akshare 导入')
    print('-' * 80)
    print('⏭️ 跳过（需要手动验证）')
    print('')

    print('=' * 80)
    print('✅ 批量修复完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
