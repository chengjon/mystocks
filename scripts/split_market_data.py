#!/usr/bin/env python3
"""
拆分 src/adapters/akshare/market_data.py (2,256行) 为6个模块

目标结构:
src/adapters/akshare/
├── __init__.py
├── base.py                          # 抽象基类 + 重试装饰器（~200行）
├── market_overview.py               # 市场总貌（~400行）
├── stock_info.py                    # 个股信息（~400行）
├── fund_flow.py                     # 资金流向（~400行）
└── standardization.py               # 数据标准化（~200行）
"""

import re
import sys
from pathlib import Path

# 源文件和目标目录
SOURCE_FILE = Path("src/adapters/akshare/market_data.py")
TARGET_DIR = Path("src/adapters/akshare/")

# 目标模块文件和它们应该包含的关键字
MODULES = {
    "base.py": {
        "keywords": ["_retry_api_call", "# Helper Functions"],
        "description": "抽象基类 + 重试装饰器"
    },
    "market_overview.py": {
        "keywords": ["get_market_overview_sse", "get_market_overview_szse", "get_szse_area_trading_summary"],
        "description": "市场总貌数据获取"
    },
    "stock_info.py": {
        "keywords": ["get_stock_industry_concept", "get_stock_individual_info_em", "get_stock_individual_basic_info_xq"],
        "description": "个股信息查询"
    },
    "fund_flow.py": {
        "keywords": ["get_stock_hsgt_fund_flow_summary_em", "get_stock_hsgt_fund_flow_detail_em"],
        "description": "沪深港通资金流向数据"
    },
    "standardization.py": {
        "keywords": ["Standardization", "ColumnMapper", "标准化的列名"],
        "description": "数据标准化工具"
    },
}

def extract_module(content: str, module_name: str, module_info: dict) -> str:
    """
    从大文件中提取特定模块的代码
    
    Args:
        content: 原文件内容
        module_name: 模块名称
        module_info: 模块信息，包含关键词和描述
    
    Returns:
        str: 提取的模块代码
    """
    lines = content.split('\n')
    
    # 找到起始行
    start_line = None
    for i, line in enumerate(lines):
        # 检查是否匹配任何关键词
        for keyword in module_info["keywords"]:
            if keyword in line or line.startswith(f'    def {keyword}') or line.startswith(f'    class {keyword}'):
                start_line = i
                break
        if start_line is not None:
            break
    
    if start_line is None:
        print(f"⚠️  未找到模块 {module_name} 的起始行")
        return ""
    
    # 找到结束行（下一个模块的起始行或文件结束）
    end_line = len(lines)
    
    # 查找下一个模块的起始标记
    next_module_markers = [
        "# Helper Functions",
        "# Legacy Functions", 
        "# AkShare Market Data Adapter",
        "# Phase 2", 
        "# Phase 3",
        "# ============================================================================"
    ]
    
    for i in range(start_line + 1, len(lines)):
        line = lines[i]
        for marker in next_module_markers:
            if marker in line:
                end_line = i
                break
        if end_line < len(lines):
            break
    
    # 提取模块代码
    module_lines = lines[start_line:end_line]
    
    # 添加文件头
    header = f'''"""
{module_info["description"]}

从原文件 {SOURCE_FILE.name} 提取
"""
    module_content = header + '\n'.join(module_lines)
    
    return module_content

def main():
    print("=" * 80)
    print("拆分市场数据适配器")
    print(f"源文件: {SOURCE_FILE}")
    print(f"目标目录: {TARGET_DIR}")
    print("=" * 80)
    
    # 读取源文件
    if not SOURCE_FILE.exists():
        print(f"❌ 错误: 源文件不存在: {SOURCE_FILE}")
        sys.exit(1)
    
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    total_lines = len(content.split('\n'))
    print(f"源文件总行数: {total_lines:,}")
    print(f"计划拆分为 {len(MODULES)} 个模块")
    print()
    
    # 创建目标模块内容
    modules_content = {}
    for module_name, module_info in MODULES.items():
        print(f"🔍 提取模块: {module_name}")
        print(f"   关键词: {module_info['keywords'][:2]}...")
        print(f"   描述: {module_info['description']}")
        
        module_content = extract_module(content, module_name, module_info)
        
        if module_content:
            module_lines = module_content.split('\n')
            modules_content[module_name] = module_content
            print(f"   ✅ 提取完成: {len(module_lines):,} 行")
        else:
            print(f"   ⚠️  未找到模块内容")
        print()
    
    # 生成 __init__.py
    print("=" * 80)
    print("生成 __init__.py 文件...")
    
    init_content = \"\"\"\nMarket Data Adapter Modules\n\n本目录包含从原 market_data.py 拆分的模块\n\"\"\"\n\n# 导入各个模块\nfrom .base import _retry_api_call\nfrom .market_overview import get_market_overview_sse, get_market_overview_szse\nfrom .stock_info import get_stock_industry_concept\n\n# 导出列表\n__all__ = [\n    \"_retry_api_call\",\n    \"get_market_overview_sse\",\n    \"get_market_overview_szse\",\n    \"get_szse_area_trading_summary\",\n    \"get_szse_sector_trading_summary\",\n    \"get_stock_industry_concept\",\n]\n\"\"\"
    
    modules_content["__init__.py"] = init_content
    print(f"   ✅ __init__.py 生成完成: {len(init_content.split('\\n')):,} 行")
    print()
    
    # 写入文件到临时目录
    temp_dir = Path("src/adapters/akshare_split")
    temp_dir.mkdir(exist_ok=True)
    
    total_written = 0
    for module_name, module_content in modules_content.items():
        file_path = temp_dir / module_name
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(module_content)
        
        lines = len(module_content.split('\n'))
        total_written += lines
        print(f"   ✅ 写入 {module_name}: {lines:,} 行")
    
    print()
    print("=" * 80)
    print(f"✅ 拆分完成!")
    print(f"   总文件数: {len(modules_content)}")
    print(f"   总行数: {total_written:,}")
    print(f"   平均行数: {total_written // len(modules_content):,}")
    print()
    print("📋 下一步:")
    print(f"   1. 审查临时目录: {temp_dir}")
    print(f"   2. 验证每个模块的代码完整性")
    print(f"   3. 更新导入路径")
    print(f"   4. 运行测试")
    print(f"   5. 删除原文件并替换为新目录")
    print()
    print(f"⚠️  注意: 目前仅完成了初步提取，请手动审查后再执行后续步骤")
    sys.exit(0)

if __name__ == "__main__":
    main()
