#!/usr/bin/env python3
"""
文件清理分析脚本
用于分析未纳入版本控制的文件、长期未访问文件和备份文件
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

def get_git_untracked_files():
    """获取未纳入版本控制的文件"""
    try:
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            cwd='/opt/claude/mystocks_spec',
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []

def get_long_unused_files(days=90):
    """获取指定天数未访问的文件"""
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    unused_files = []
    
    for root, _, files in os.walk('/opt/claude/mystocks_spec'):
        for file in files:
            file_path = os.path.join(root, file)
            # 检查文件最后修改时间
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                if mtime < cutoff_time:
                    unused_files.append(file_path)
    
    return unused_files

def get_backup_files():
    """获取备份文件"""
    backup_patterns = ['*.bak', '*.backup', '*.orig', '*~']
    backup_files = []
    
    for pattern in backup_patterns:
        try:
            result = subprocess.run(
                ['find', '/opt/claude/mystocks_spec', '-name', pattern, '-type', 'f'],
                capture_output=True,
                text=True,
                check=True
            )
            backup_files.extend([f.strip() for f in result.stdout.split('\n') if f.strip()])
        except subprocess.CalledProcessError:
            pass
    
    return backup_files

def analyze_temp_directory():
    """分析temp目录"""
    temp_dirs = []
    temp_path = Path('/opt/claude/mystocks_spec')
    
    for item in temp_path.iterdir():
        if item.name.lower() in ['temp', 'tmp', 'test', 'unused', 'old', 'archive']:
            temp_dirs.append(item)
    
    return temp_dirs

def generate_cleanup_report():
    """生成清理报告"""
    print("=== MyStocks 文件清理分析报告 ===")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 分析未纳入版本控制的文件
    print("1. 未纳入版本控制的文件:")
    untracked = get_git_untracked_files()
    if untracked:
        print(f"   找到 {len(untracked)} 个未跟踪文件")
        for file in untracked[:10]:  # 只显示前10个
            print(f"   - {file}")
        if len(untracked) > 10:
            print(f"   ... 还有 {len(untracked) - 10} 个文件")
    else:
        print("   ✅ 无未跟踪文件")
    print()
    
    # 2. 分析长期未访问文件
    print("2. 长期未访问文件 (超过90天):")
    unused = get_long_unused_files()
    if unused:
        print(f"   找到 {len(unused)} 个长期未访问文件")
        for file in unused[:10]:
            print(f"   - {file}")
        if len(unused) > 10:
            print(f"   ... 还有 {len(unused) - 10} 个文件")
    else:
        print("   ✅ 无长期未访问文件")
    print()
    
    # 3. 分析备份文件
    print("3. 备份文件:")
    backups = get_backup_files()
    if backups:
        print(f"   找到 {len(backups)} 个备份文件")
        for file in backups:
            print(f"   - {file}")
    else:
        print("   ✅ 无备份文件")
    print()
    
    # 4. 分析临时目录
    print("4. 临时目录:")
    temp_dirs = analyze_temp_directory()
    if temp_dirs:
        for temp_dir in temp_dirs:
            if temp_dir.is_dir():
                file_count = len(list(temp_dir.rglob('*')))
                print(f"   - {temp_dir.name}/: {file_count} 个项目")
    else:
        print("   ✅ 无需要清理的临时目录")
    print()
    
    # 5. 建议
    print("5. 清理建议:")
    if untracked or unused or backups or temp_dirs:
        print("   ⚠️  建议进行清理:")
        if untracked:
            print("   - 清理未跟踪的文件或使用 git add 将其纳入版本控制")
        if unused:
            print("   - 确认长期未访问文件是否需要，删除不需要的文件")
        if backups:
            print("   - 删除不需要的备份文件")
        if temp_dirs:
            print("   - 清理临时目录中的内容")
    else:
        print("   ✅ 当前项目文件状况良好")
    print()
    
    return {
        'untracked': untracked,
        'unused': unused,
        'backups': backups,
        'temp_dirs': [str(d) for d in temp_dirs]
    }

if __name__ == "__main__":
    report = generate_cleanup_report()
