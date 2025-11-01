#!/usr/bin/env python3
"""
数据库健康检查脚本

验证4个数据库的连接状态，为修复Web页面问题做准备
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_mysql_connection():
    """验证MySQL连接"""
    print("\n" + "="*60)
    print("【1/4】MySQL 连接测试")
    print("="*60)

    try:
        import pymysql
        from web.backend.app.core.config import settings

        conn = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            connect_timeout=5
        )

        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL连接成功")
        print(f"   版本: {version[0]}")
        print(f"   数据库: {settings.mysql_database}")

        # 检查关键表
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   表数量: {len(tables)}")
        if tables:
            print(f"   示例表: {', '.join(tables[:5])}")

        cursor.close()
        conn.close()
        return True, None

    except Exception as e:
        print(f"❌ MySQL连接失败")
        print(f"   错误: {str(e)}")
        return False, str(e)


def check_postgresql_connection():
    """验证PostgreSQL连接"""
    print("\n" + "="*60)
    print("【2/4】PostgreSQL 连接测试")
    print("="*60)

    try:
        import psycopg2
        from web.backend.app.core.config import settings

        # 测试mystocks数据库
        conn = psycopg2.connect(
            host=settings.postgresql_host,
            port=settings.postgresql_port,
            user=settings.postgresql_user,
            password=settings.postgresql_password,
            database=settings.postgresql_database,
            connect_timeout=5
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL连接成功 (mystocks)")
        print(f"   版本: {version[0][:50]}...")
        print(f"   数据库: {settings.postgresql_database}")

        # 检查关键表
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   表数量: {len(tables)}")
        if tables:
            print(f"   示例表: {', '.join(tables[:5])}")

        cursor.close()
        conn.close()

        # 测试mystocks_monitoring数据库
        try:
            conn_monitor = psycopg2.connect(
                host=settings.postgresql_host,
                port=settings.postgresql_port,
                user=settings.postgresql_user,
                password=settings.postgresql_password,
                database='mystocks_monitoring',
                connect_timeout=5
            )
            cursor_monitor = conn_monitor.cursor()
            cursor_monitor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public'
            """)
            monitor_tables = [table[0] for table in cursor_monitor.fetchall()]
            print(f"✅ PostgreSQL监控数据库连接成功")
            print(f"   数据库: mystocks_monitoring")
            print(f"   表数量: {len(monitor_tables)}")
            cursor_monitor.close()
            conn_monitor.close()
        except Exception as e:
            print(f"⚠️  PostgreSQL监控数据库连接失败: {str(e)}")

        return True, None

    except Exception as e:
        print(f"❌ PostgreSQL连接失败")
        print(f"   错误: {str(e)}")
        return False, str(e)


def check_tdengine_connection():
    """验证TDengine连接"""
    print("\n" + "="*60)
    print("【3/4】TDengine 连接测试")
    print("="*60)

    try:
        import taos
        from web.backend.app.core.config import settings

        conn = taos.connect(
            host=settings.tdengine_host,
            port=settings.tdengine_port,
            user=settings.tdengine_user,
            password=settings.tdengine_password,
            timeout=5000
        )

        cursor = conn.cursor()

        # 检查服务器版本 (使用SELECT CLIENT_VERSION()替代)
        try:
            cursor.execute("SELECT CLIENT_VERSION()")
            version_result = cursor.fetchone()
            version = version_result[0] if version_result else "Unknown"
        except:
            # 如果CLIENT_VERSION()失败，尝试获取服务器信息
            cursor.execute("SHOW VARIABLES")
            version = "Connected"

        print(f"✅ TDengine连接成功")
        print(f"   版本: {version}")
        print(f"   主机: {settings.tdengine_host}:{settings.tdengine_port}")

        # 切换到目标数据库并检查
        try:
            cursor.execute(f"USE {settings.tdengine_database}")
            print(f"   数据库: {settings.tdengine_database} ✅")

            # 检查超级表
            cursor.execute("SHOW STABLES")
            stables = cursor.fetchall()
            print(f"   超级表数量: {len(stables)}")
            if stables:
                print(f"   示例超级表: {', '.join([s[0] for s in stables[:5]])}")
        except Exception as db_e:
            print(f"   数据库: {settings.tdengine_database} ❌ (不存在或无权限)")
            print(f"   建议: 创建数据库 - CREATE DATABASE {settings.tdengine_database}")

        cursor.close()
        conn.close()
        return True, None

    except Exception as e:
        print(f"❌ TDengine连接失败")
        print(f"   错误: {str(e)}")
        print(f"   检查项:")
        print(f"   1. TDengine服务是否启动: systemctl status taosd")
        print(f"   2. 端口是否正确: {settings.tdengine_port}")
        print(f"   3. 防火墙是否开放")
        return False, str(e)


def check_redis_connection():
    """验证Redis连接"""
    print("\n" + "="*60)
    print("【4/4】Redis 连接测试")
    print("="*60)

    try:
        import redis
        from web.backend.app.core.config import settings

        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password if settings.redis_password else None,
            db=settings.redis_db,
            socket_connect_timeout=5
        )

        # 测试连接
        r.ping()
        info = r.info()
        print(f"✅ Redis连接成功")
        print(f"   版本: {info.get('redis_version', 'Unknown')}")
        print(f"   数据库: DB{settings.redis_db}")
        print(f"   内存使用: {info.get('used_memory_human', 'Unknown')}")
        print(f"   键数量: {r.dbsize()}")

        return True, None

    except Exception as e:
        print(f"❌ Redis连接失败")
        print(f"   错误: {str(e)}")
        return False, str(e)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("MyStocks 数据库健康检查")
    print("="*60)

    results = {}

    # 测试所有数据库
    results['mysql'], mysql_error = check_mysql_connection()
    results['postgresql'], pg_error = check_postgresql_connection()
    results['tdengine'], td_error = check_tdengine_connection()
    results['redis'], redis_error = check_redis_connection()

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    total = len(results)
    passed = sum(results.values())

    print(f"\n总计: {passed}/{total} 个数据库连接成功")
    print(f"通过率: {passed/total*100:.1f}%\n")

    for db, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {db.upper()}: {'通过' if status else '失败'}")

    # 修复建议
    if passed < total:
        print("\n" + "="*60)
        print("修复建议")
        print("="*60)

        if not results['mysql']:
            print("\n【MySQL修复】")
            print("1. 检查MySQL服务是否启动: systemctl status mysql")
            print("2. 验证配置文件: web/backend/app/core/config.py")
            print("3. 确认.env文件中的MYSQL_*配置正确")

        if not results['postgresql']:
            print("\n【PostgreSQL修复】")
            print("1. 检查PostgreSQL服务是否启动: systemctl status postgresql")
            print("2. 验证端口配置 (当前: 5438, 标准: 5432)")
            print("3. 确认.env文件中的POSTGRESQL_*配置正确")

        if not results['tdengine']:
            print("\n【TDengine修复】")
            print("1. 检查TDengine服务是否启动: systemctl status taosd")
            print("2. 验证端口配置 (当前: 6030)")
            print("3. 确认.env文件中的TDENGINE_*配置正确")

        if not results['redis']:
            print("\n【Redis修复】")
            print("1. 检查Redis服务是否启动: systemctl status redis")
            print("2. 验证端口配置 (当前: 6379)")
            print("3. 确认.env文件中的REDIS_*配置正确")

    print("\n" + "="*60)

    # 返回退出码
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
