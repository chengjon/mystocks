#!/usr/bin/env python3
"""
数据库连接测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, '/opt/claude/mystocks_spec')

from src.storage.database.connection_manager import get_connection_manager

def test_connections():
    """测试数据库连接"""
    print("正在测试数据库连接...")
    
    manager = get_connection_manager()
    
    # 测试TDengine连接
    print("\n1. 测试TDengine连接...")
    try:
        conn = manager.get_tdengine_connection()
        print("✅ TDengine连接成功")
    except Exception as e:
        print(f"❌ TDengine连接失败: {e}")
    
    # 测试PostgreSQL连接
    print("\n2. 测试PostgreSQL连接...")
    try:
        pool = manager.get_postgresql_connection()
        conn = pool.getconn()
        pool.putconn(conn)
        print("✅ PostgreSQL连接成功")
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")

if __name__ == "__main__":
    test_connections()