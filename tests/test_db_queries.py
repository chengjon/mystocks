#!/usr/bin/env python3
"""
数据库连接和查询测试脚本
"""

import sys
import os

# 添加项目根目录和web/backend到Python路径
sys.path.insert(0, '/opt/claude/mystocks_spec')
sys.path.insert(0, '/opt/claude/mystocks_spec/web/backend')

from app.core.database import get_db_service

def test_database_queries():
    """测试数据库查询功能"""
    print("正在测试数据库查询功能...")
    
    try:
        # 获取数据库服务
        db_service = get_db_service()
        print("✅ 数据库服务获取成功")
        
        # 测试股票基本信息查询
        print("\n1. 测试股票基本信息查询...")
        stocks_df = db_service.query_stocks_basic(limit=5)
        print(f"✅ 股票基本信息查询成功，返回 {len(stocks_df)} 条记录")
        if len(stocks_df) > 0:
            print("前几条记录:")
            print(stocks_df.head())
        
        print("\n数据库连接和查询测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_queries()