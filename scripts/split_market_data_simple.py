#!/usr/bin/env python3
"""
简单拆分脚本 - 将 market_data.py 拆分为模块
"""

import sys
from pathlib import Path

SOURCE_FILE = Path("src/adapters/akshare/market_data.py")
OUTPUT_DIR = Path("src/adapters/akshare_modules")

print("=" * 80)
print("拆分市场数据适配器 - 简化版本")
print(f"源文件: {SOURCE_FILE}")
print(f"输出目录: {OUTPUT_DIR}")
print("=" * 80)

# 读取源文件
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"源文件总行数: {total_lines:,}")

# 查找关键标记
markers = {
    'base': ['# Helper Functions', '# Legacy Functions'],
    'market_overview': ['def get_market_overview_sse', 'def get_market_overview_szse'],
    'stock_info': ['def get_stock_industry_concept'],
    'fund_flow': ['def get_stock_hsgt_fund_flow_summary_em'],
}

# 创建输出目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 简单拆分：按行范围分割
splits = [
    {
        'name': 'base.py',
        'start': 15,
        'end': 50
    },
    {
        'name': 'market_overview.py',
        'start': 100,
        'end': 300
    },
    {
        'name': 'stock_info.py',
        'start': 400,
        'end': 600
    },
    {
        'name': 'fund_flow.py',
        'start': 700,
        'end': 900
    },
]

for split in splits:
    output_file = OUTPUT_DIR / split['name']
    content = lines[split['start']:split['end']]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print(f"✅ 创建 {split['name']: {split['end'] - split['start']:,} 行")

print()
print("=" * 80)
print(f"✅ 简单拆分完成!")
print(f"   创建文件数: {len(splits)}")
print()
print("注意: 这是简化版本，仅按行范围分割")
print("完整拆分需要后续手动处理")
