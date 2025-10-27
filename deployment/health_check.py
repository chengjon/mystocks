#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境健康检查脚本

检查MyStocks系统的所有关键组件

使用方法:
    python deployment/health_check.py

创建日期: 2025-10-25
版本: 1.0.0
"""

import sys
import os
import requests
import psycopg2
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def check_api_service(base_url: str = "http://localhost:8000") -> bool:
    """检查API服务"""
    print("\n检查API服务...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ API服务运行正常")
            return True
        else:
            print(f"  ❌ API服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ API服务连接失败: {e}")
        return False


def check_postgresql() -> bool:
    """检查PostgreSQL数据库"""
    print("\n检查PostgreSQL数据库...")
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRESQL_HOST', 'localhost'),
            port=os.getenv('POSTGRESQL_PORT', 5432),
            user=os.getenv('POSTGRESQL_USER', 'postgres'),
            password=os.getenv('POSTGRESQL_PASSWORD', ''),
            database=os.getenv('POSTGRESQL_DATABASE', 'mystocks'),
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"  ✅ PostgreSQL连接正常")
        print(f"     版本: {version[:50]}...")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ PostgreSQL连接失败: {e}")
        return False


def check_tdengine() -> bool:
    """检查TDengine数据库"""
    print("\n检查TDengine数据库...")
    try:
        import taos
        conn = taos.connect(
            host=os.getenv('TDENGINE_HOST', 'localhost'),
            port=int(os.getenv('TDENGINE_PORT', 6030)),
            user=os.getenv('TDENGINE_USER', 'root'),
            password=os.getenv('TDENGINE_PASSWORD', 'taosdata'),
            database=os.getenv('TDENGINE_DATABASE', 'market_data')
        )
        result = conn.query("SELECT server_version()")
        version = result.fetch_all()[0][0]
        print(f"  ✅ TDengine连接正常")
        print(f"     版本: {version}")
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ TDengine连接失败: {e}")
        return False


def check_system_resources() -> bool:
    """检查系统资源"""
    print("\n检查系统资源...")
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        print(f"  CPU使用率: {cpu_percent}%")
        print(f"  内存使用率: {memory.percent}%")
        print(f"  磁盘使用率: {disk.percent}%")

        if cpu_percent > 90:
            print(f"  ⚠️  CPU使用率过高")
        if memory.percent > 90:
            print(f"  ⚠️  内存使用率过高")
        if disk.percent > 90:
            print(f"  ⚠️  磁盘使用率过高")

        if cpu_percent <= 90 and memory.percent <= 90 and disk.percent <= 90:
            print(f"  ✅ 系统资源使用正常")
            return True
        return False
    except Exception as e:
        print(f"  ⚠️  无法检查系统资源: {e}")
        return True  # 不作为关键错误


def main():
    """主函数"""
    print("=" * 70)
    print("MyStocks 生产环境健康检查")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "API服务": check_api_service(),
        "PostgreSQL": check_postgresql(),
        "TDengine": check_tdengine(),
        "系统资源": check_system_resources()
    }

    print("\n" + "=" * 70)
    print("检查摘要")
    print("=" * 70)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name:<20} {status}")

    print(f"\n总计: {passed}/{total} 项检查通过")

    if passed == total:
        print("\n🎉 所有健康检查通过！系统运行正常。\n")
        sys.exit(0)
    else:
        print("\n⚠️  部分检查失败，请检查日志并修复问题。\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
