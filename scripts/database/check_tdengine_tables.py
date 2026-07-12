#!/usr/bin/env python3
"""检查TDengine中的表"""

import os
import sys


# 添加项目路径到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.storage.database.database_manager import DatabaseTableManager


def create_tdengine_database():
    """创建TDengine数据库"""
    try:
        import taosrest

        # 获取TDengine连接信息
        db_name = os.getenv("TDENGINE_DATABASE", "market_data")
        print(f"正在创建TDengine数据库: {db_name}")

        # 使用REST API方式连接（不指定数据库）
        conn = taosrest.connect(
            url=f"http://{os.getenv('TDENGINE_HOST', 'localhost')}:{os.getenv('TDENGINE_REST_PORT', '6041')}",
            user=os.getenv("TDENGINE_USER", "root"),
            password=os.getenv("TDENGINE_PASSWORD", ""),
        )

        # 创建数据库
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"  ✓ TDengine数据库 {db_name} 已创建或已存在")
        return True

    except Exception as e:
        print(f"❌ 创建TDengine数据库时出错: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🔍 检查TDengine中的数据库和表...")

    try:
        # 创建数据库管理器实例
        manager = DatabaseTableManager()

        # 获取TDengine连接信息
        db_name = os.getenv("TDENGINE_DATABASE", "market_data")
        print(f"目标数据库: {db_name}")

        # 首先尝试创建数据库
        if not create_tdengine_database():
            print("❌ 无法创建TDengine数据库")
            return False

        # 使用REST API方式连接（不指定数据库）
        import taosrest

        conn = taosrest.connect(
            url=f"http://{os.getenv('TDENGINE_HOST', 'localhost')}:{os.getenv('TDENGINE_REST_PORT', '6041')}",
            user=os.getenv("TDENGINE_USER", "root"),
            password=os.getenv("TDENGINE_PASSWORD", ""),
        )

        # 查询所有数据库
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()

        print("\nTDengine中的数据库:")
        print("-" * 30)
        existing_databases = []
        if databases:
            for row in databases:
                print(row[0])  # 数据库名通常在第一列
                existing_databases.append(row[0])
        else:
            print("未找到任何数据库")

        # 检查目标数据库是否存在
        if db_name not in existing_databases:
            print(f"\n❌ 数据库 {db_name} 不存在")
            return False
        print(f"\n✅ 数据库 {db_name} 存在，继续检查表")

        # 直接在SQL语句中指定数据库名，因为REST API是无状态的
        # 先检查超级表（STABLES）
        cursor.execute(f"SHOW {db_name}.STABLES")
        stables_result = cursor.fetchall()

        # 再检查普通表（tables）
        cursor.execute(f"SHOW {db_name}.tables")
        tables_result = cursor.fetchall()

        print(f"\nTDengine数据库 {db_name} 中的超级表:")
        print("-" * 50)
        if stables_result:
            for row in stables_result:
                print(row)
        else:
            print("未找到任何超级表")

        print(f"\nTDengine数据库 {db_name} 中的普通表:")
        print("-" * 50)
        if tables_result:
            for row in tables_result:
                print(row)
        else:
            print("未找到任何普通表")

        total_count = len(stables_result) + len(tables_result)
        print(
            f"\n总共找到 {total_count} 个表 ({len(stables_result)} 个超级表, {len(tables_result)} 个普通表)",
        )

    except Exception as e:
        print(f"❌ 检查TDengine时出错: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
