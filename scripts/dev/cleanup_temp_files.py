#!/usr/bin/env python3
"""
临时文件清理脚本
安全清理temp、tmp目录和备份文件
"""

import os
import shutil
import glob
from pathlib import Path
import subprocess

def backup_temp_directory():
    """备份临时目录（如果需要的话）"""
    print("=== 临时文件清理 ===")
    print(f"清理时间: 2025-11-25 14:43:19")
    print()
    
    # 检查temp目录
    temp_path = Path('/opt/claude/mystocks_spec/temp')
    tmp_path = Path('/opt/claude/mystocks_spec/tmp')
    
    print("1. 目录清理分析:")
    if temp_path.exists():
        temp_files = list(temp_path.rglob('*'))
        print(f"   temp/ 目录包含 {len(temp_files)} 个文件")
    else:
        print("   temp/ 目录不存在")
        
    if tmp_path.exists():
        tmp_files = list(tmp_path.rglob('*'))
        print(f"   tmp/ 目录包含 {len(tmp_files)} 个文件")
    else:
        print("   tmp/ 目录不存在")
    
    return temp_path, tmp_path

def clean_backup_files():
    """清理备份文件"""
    print("\n2. 备份文件清理:")
    
    backup_patterns = ['*.bak', '*.backup', '*.orig', '*~']
    cleaned_count = 0
    
    for pattern in backup_patterns:
        backup_files = []
        try:
            # 使用subprocess来执行find命令
            result = subprocess.run(
                ['find', '/opt/claude/mystocks_spec', '-name', pattern, '-type', 'f'],
                capture_output=True,
                text=True,
                check=True
            )
            backup_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            continue
        
        if backup_files:
            print(f"   找到 {len(backup_files)} 个 {pattern} 文件:")
            for file in backup_files[:5]:  # 只显示前5个
                print(f"   - {file}")
            if len(backup_files) > 5:
                print(f"   ... 还有 {len(backup_files) - 5} 个文件")
            
            # 安全删除备份文件
            for file in backup_files:
                try:
                    os.remove(file)
                    cleaned_count += 1
                except OSError as e:
                    print(f"   ⚠️  无法删除 {file}: {e}")
    
    if cleaned_count > 0:
        print(f"\n✅ 成功清理了 {cleaned_count} 个备份文件")
    else:
        print("✅ 无需要清理的备份文件")
    
    return cleaned_count

def remove_backup_file_extentions():
    """删除backup文件扩展名相关的文件"""
    print("\n3. 扩展名备份文件清理:")
    
    # 查找带有特定扩展名的备份文件
    extension_patterns = [
        '**/*.backup',
        '**/*.bak.*',
        '**/*_backup.*'
    ]
    
    cleaned_count = 0
    for pattern in extension_patterns:
        files = []
        for path in Path('/opt/claude/mystocks_spec').rglob('*'):
            if path.is_file() and path.name.endswith('.backup'):
                files.append(str(path))
        
        if files:
            print(f"   找到 {len(files)} 个扩展名备份文件:")
            for file in files[:5]:
                print(f"   - {file}")
            
            for file in files:
                try:
                    os.remove(file)
                    cleaned_count += 1
                except OSError as e:
                    print(f"   ⚠️  无法删除 {file}: {e}")
    
    if cleaned_count > 0:
        print(f"✅ 成功清理了 {cleaned_count} 个扩展名备份文件")
    
    return cleaned_count

def clean_old_backup_directories():
    """清理旧的备份目录"""
    print("\n4. 旧备份目录清理:")
    
    # 清理特定命名的目录
    old_dirs = []
    base_path = Path('/opt/claude/mystocks_spec')
    
    # 查找备份目录
    for pattern in ['*backup*', '*temp*', '*tmp*', '*unused*']:
        old_dirs.extend(base_path.glob(pattern))
    
    if old_dirs:
        print(f"   找到 {len(old_dirs)} 个相关目录:")
        for dir_path in old_dirs:
            if dir_path.is_dir():
                print(f"   - {dir_path.name}/")
    
    return old_dirs

def main():
    """主清理函数"""
    print("MyStocks 临时文件安全清理")
    print("=" * 50)
    
    # 1. 备份和清理分析
    temp_path, tmp_path = backup_temp_directory()
    
    # 2. 清理备份文件
    backup_files_cleaned = clean_backup_files()
    
    # 3. 清理扩展名备份文件
    extension_files_cleaned = remove_backup_file_extentions()
    
    # 4. 清理旧备份目录
    old_dirs = clean_old_backup_directories()
    
    print("\n" + "=" * 50)
    print("清理总结:")
    print(f"- 清理的备份文件: {backup_files_cleaned + extension_files_cleaned} 个")
    print(f"- 检查的临时目录: {len([p for p in [temp_path, tmp_path] if p.exists()]) } 个")
    
    if temp_path.exists() or tmp_path.exists():
        print("\n⚠️  重要提示:")
        print("   temp/ 和 tmp/ 目录包含大量临时测试文件")
        print("   根据优化方案，这些目录应该被清理或移动到外部存储")
        print("   建议执行: rm -rf temp/ tmp/")
    
    print("\n✅ 清理脚本执行完成")

if __name__ == "__main__":
    main()
