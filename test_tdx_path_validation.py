#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX路径验证和功能测试脚本
测试修改后的TDX路径配置和各项功能
"""

import os
import sys
import pandas as pd
from datetime import datetime

# 添加项目路径
sys.path.append('/opt/claude/mystocks_spec')

from adapters.tdx.tdx_read import XgTdx

def test_path_validation():
    """测试路径验证功能"""
    print("=" * 60)
    print("测试1: 路径验证")
    print("=" * 60)
    
    # 测试默认路径
    tdx_api = XgTdx()
    print(f"默认路径: {tdx_api.path}")
    
    # 检查路径是否存在
    if os.path.exists(tdx_api.path):
        print(f"✓ 路径存在: {tdx_api.path}")
        
        # 列出目录内容
        try:
            files = os.listdir(tdx_api.path)
            print(f"✓ 目录可访问，包含 {len(files)} 个文件/目录")
            if files:
                print("前5个文件/目录:")
                for i, file in enumerate(files[:5]):
                    print(f"  {i+1}. {file}")
        except Exception as e:
            print(f"✗ 目录访问失败: {e}")
    else:
        print(f"✗ 路径不存在: {tdx_api.path}")
        print("将尝试创建目录...")
        try:
            os.makedirs(tdx_api.path, exist_ok=True)
            print(f"✓ 目录创建成功: {tdx_api.path}")
        except Exception as e:
            print(f"✗ 目录创建失败: {e}")

def test_basic_operations():
    """测试基础操作功能"""
    print("\n" + "=" * 60)
    print("测试2: 基础操作功能")
    print("=" * 60)
    
    tdx_api = XgTdx()
    
    # 测试读取所有板块文件
    print("2.1 读取所有板块文件...")
    try:
        all_files = tdx_api.read_all_tdx_stock()
        print(f"✓ 成功读取板块文件，共 {len(all_files)} 个")
        if all_files:
            print("前5个板块文件:")
            for i, file in enumerate(all_files[:5]):
                print(f"  {i+1}. {file}")
        else:
            print("  当前没有板块文件")
    except Exception as e:
        print(f"✗ 读取板块文件失败: {e}")

def test_stock_code_adjustment():
    """测试股票代码格式调整功能"""
    print("\n" + "=" * 60)
    print("测试3: 股票代码格式调整")
    print("=" * 60)
    
    tdx_api = XgTdx()
    
    # 测试股票代码调整
    test_codes = [
        '600519',      # 沪市股票
        '000001',      # 深市股票
        '600519.SH',   # 带后缀的沪市股票
        '000001.SZ',   # 带后缀的深市股票
        '688001',      # 科创板
        '300001',      # 创业板
    ]
    
    print("3.1 测试通达信内部格式调整 (adjust_stock):")
    for code in test_codes:
        try:
            adjusted = tdx_api.adjust_stock(code)
            print(f"  {code:12} → {adjusted}")
        except Exception as e:
            print(f"  {code:12} → 错误: {e}")
    
    print("\n3.2 测试外部标准格式调整 (adjust_stock_1):")
    for code in test_codes:
        try:
            adjusted = tdx_api.adjust_stock_1(code)
            print(f"  {code:12} → {adjusted}")
        except Exception as e:
            print(f"  {code:12} → 错误: {e}")

def test_block_operations():
    """测试板块操作功能"""
    print("\n" + "=" * 60)
    print("测试4: 板块操作功能")
    print("=" * 60)
    
    tdx_api = XgTdx()
    test_block_name = 'TEST_BLOCK'
    
    # 测试创建板块
    print("4.1 创建测试板块...")
    try:
        tdx_api.creat_tdx_user_def_stock(test_block_name)
        print(f"✓ 板块 {test_block_name} 创建成功")
    except Exception as e:
        print(f"✗ 板块创建失败: {e}")
    
    # 测试添加股票
    print("\n4.2 添加股票到板块...")
    test_stocks = ['600519', '000001', '688001']
    try:
        for stock in test_stocks:
            tdx_api.add_tdx_stock(test_block_name, stock)
        print(f"✓ 成功添加 {len(test_stocks)} 只股票")
    except Exception as e:
        print(f"✗ 添加股票失败: {e}")
    
    # 测试读取板块
    print("\n4.3 读取板块内容...")
    try:
        df_internal = tdx_api.read_tdx_stock(test_block_name)
        print(f"✓ 内部格式读取成功，共 {len(df_internal)} 只股票")
        if not df_internal.empty:
            print("股票列表 (内部格式):")
            for idx, row in df_internal.iterrows():
                print(f"  {idx+1}. {row['证券代码']}")
        
        df_standard = tdx_api.read_tdx_stock_1(test_block_name)
        print(f"✓ 标准格式读取成功，共 {len(df_standard)} 只股票")
        if not df_standard.empty:
            print("股票列表 (标准格式):")
            for idx, row in df_standard.iterrows():
                print(f"  {idx+1}. {row['证券代码']}")
    except Exception as e:
        print(f"✗ 读取板块失败: {e}")
    
    # 测试删除股票
    print("\n4.4 删除股票...")
    try:
        tdx_api.del_tdx_stock(test_block_name, '600519')
        print("✓ 删除股票 600519 成功")
    except Exception as e:
        print(f"✗ 删除股票失败: {e}")
    
    # 测试批量操作
    print("\n4.5 批量添加股票...")
    try:
        batch_stocks = ['600036', '000002']
        tdx_api.add_tdx_stock_list(test_block_name, batch_stocks)
        print(f"✓ 批量添加 {len(batch_stocks)} 只股票成功")
    except Exception as e:
        print(f"✗ 批量添加失败: {e}")
    
    # 测试清空板块
    print("\n4.6 清空板块...")
    try:
        tdx_api.del_all_tdx_stock(test_block_name)
        print("✓ 板块清空成功")
    except Exception as e:
        print(f"✗ 清空板块失败: {e}")
    
    # 测试删除板块
    print("\n4.7 删除测试板块...")
    try:
        tdx_api.del_tdx_user_def_stock(test_block_name)
        print("✓ 测试板块删除成功")
    except Exception as e:
        print(f"✗ 删除板块失败: {e}")

def test_error_handling():
    """测试错误处理功能"""
    print("\n" + "=" * 60)
    print("测试5: 错误处理功能")
    print("=" * 60)
    
    tdx_api = XgTdx()
    
    # 测试读取不存在的板块
    print("5.1 读取不存在的板块...")
    try:
        df = tdx_api.read_tdx_stock('NON_EXISTENT_BLOCK')
        if df.empty:
            print("✓ 正确处理不存在的板块，返回空DataFrame")
        else:
            print("✗ 应该返回空DataFrame")
    except Exception as e:
        print(f"✗ 异常处理不当: {e}")
    
    # 测试删除不存在的板块
    print("\n5.2 删除不存在的板块...")
    try:
        tdx_api.del_tdx_user_def_stock('NON_EXISTENT_BLOCK')
        print("✓ 正确处理不存在的板块删除")
    except Exception as e:
        print(f"✗ 异常处理不当: {e}")

def main():
    """主测试函数"""
    print("TDX路径验证和功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    
    try:
        # 运行各项测试
        test_path_validation()
        test_basic_operations()
        test_stock_code_adjustment()
        test_block_operations()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
