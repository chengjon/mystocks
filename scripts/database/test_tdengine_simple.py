#!/usr/bin/env python3
"""
简化版 TDengine 验证脚本
绕过导入问题，直接测试TDengine连接和基本功能
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 加载 .env 文件
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
    # 手动加载 .env 文件 (不依赖 python-dotenv)
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value

# 环境变量 (优先从 .env 文件读取，其次使用默认值)
TDENGINE_HOST = os.getenv("TDENGINE_HOST", "127.0.0.1")
TDENGINE_PORT = os.getenv("TDENGINE_PORT", "6030")
TDENGINE_USER = os.getenv("TDENGINE_USER", "root")
TDENGINE_PASSWORD = os.getenv("TDENGINE_PASSWORD", "your-tdengine-password")
TDENGINE_DATABASE = os.getenv("TDENGINE_DATABASE", "market_data")


def print_header(text):
    """打印分隔线标题"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}")


def print_check(status, message, detail=""):
    """打印检查结果"""
    symbols = {"✅": "✅", "❌": "❌", "⚠️": "⚠️"}
    status_symbol = symbols.get(status, status)
    print(f"{status_symbol} {message}")
    if detail:
        print(f"   → {detail}")


def check_docker_status():
    """检查Docker和容器状态"""
    print_header("1. 检查Docker和TDengine容器状态")

    # 检查Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_check("✅", "Docker已安装", result.stdout.strip())
        else:
            print_check("❌", "Docker未找到")
            return False
    except:
        print_check("❌", "Docker命令不可用")
        return False

    # 检查TDengine容器
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=tdengine", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
        )
        if "Up" in result.stdout:
            print_check("✅", "TDengine容器正在运行", result.stdout.strip())
            return True
        else:
            print_check("❌", "TDengine容器未运行")
            print_check(
                "⚠️", "启动命令", "docker-compose -f docker-compose.tdengine.yml up -d"
            )
            return False
    except Exception as e:
        print_check("❌", "无法检查容器状态", str(e))
        return False


def test_taos_connection():
    """测试taos-py连接"""
    print_header("2. 测试TDengine连接")

    try:
        import taos

        print_check("✅", "taos-py已安装")
    except ImportError:
        print_check("❌", "taos-py未安装")
        print_check("⚠️", "安装命令", "pip install taospy")
        return False

    try:
        from taos import connect

        # 尝试连接
        conn = connect(
            host=TDENGINE_HOST,
            port=int(TDENGINE_PORT),
            user=TDENGINE_USER,
            password=TDENGINE_PASSWORD,
        )
        print_check("✅", "成功连接TDengine", f"{TDENGINE_HOST}:{TDENGINE_PORT}")

        # 获取版本
        cursor = conn.cursor()
        cursor.execute("SELECT SERVER_VERSION()")
        version = cursor.fetchone()
        print_check("✅", "TDengine版本", str(version[0]) if version else "未知")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print_check("❌", "连接失败", str(e))
        return False


def test_database_operations():
    """测试数据库基本操作"""
    print_header("3. 测试数据库操作")

    try:
        from taos import connect

        conn = connect(
            host=TDENGINE_HOST,
            port=int(TDENGINE_PORT),
            user=TDENGINE_USER,
            password=TDENGINE_PASSWORD,
        )
        cursor = conn.cursor()

        # 创建数据库
        try:
            cursor.execute(f"CREATE DATABASE {TDENGINE_DATABASE}")
            print_check("✅", f"数据库 {TDENGINE_DATABASE} 创建成功")
        except Exception as e:
            if "already exists" in str(e):
                print_check("⚠️", f"数据库 {TDENGINE_DATABASE} 已存在")
            else:
                print_check("❌", "创建数据库失败", str(e))
                cursor.close()
                conn.close()
                return False

        # 选择数据库
        cursor.execute(f"USE {TDENGINE_DATABASE}")
        print_check("✅", f"切换到数据库 {TDENGINE_DATABASE}")

        # 创建超表 (缓存表) - 使用 TDengine 3.x 的 STABLE 语法
        create_super_table = """
        CREATE STABLE IF NOT EXISTS cache_data (
            ts TIMESTAMP,
            cache_data VARCHAR(1024)
        ) TAGS (
            symbol VARCHAR(20),
            data_type VARCHAR(50),
            timeframe VARCHAR(10)
        )
        """

        try:
            cursor.execute(create_super_table)
            print_check("✅", "超表 cache_data 创建成功")
        except Exception as e:
            if "already exists" in str(e):
                print_check("⚠️", "超表 cache_data 已存在")
            else:
                print_check("❌", "创建超表失败", str(e))

        # 创建普通表
        create_table = """
        CREATE TABLE IF NOT EXISTS stock_tick (
            ts TIMESTAMP,
            symbol VARCHAR(20),
            price DOUBLE,
            volume BIGINT,
            amount DOUBLE
        )
        """

        try:
            cursor.execute(create_table)
            print_check("✅", "普通表 stock_tick 创建成功")
        except Exception as e:
            if "already exists" in str(e):
                print_check("⚠️", "普通表 stock_tick 已存在")
            else:
                print_check("❌", "创建普通表失败", str(e))

        # 查询表列表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print_check("✅", f"数据库中有 {len(tables)} 个表")
        for table in tables[:5]:
            print(f"     - {table[0]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print_check("❌", "数据库操作失败", str(e))
        import traceback

        traceback.print_exc()
        return False


def test_write_read_operations():
    """测试数据写入和读取"""
    print_header("4. 测试数据写入和读取")

    try:
        from taos import connect
        from datetime import datetime, timedelta

        conn = connect(
            host=TDENGINE_HOST,
            port=int(TDENGINE_PORT),
            user=TDENGINE_USER,
            password=TDENGINE_PASSWORD,
        )
        cursor = conn.cursor()

        # 使用数据库
        cursor.execute(f"USE {TDENGINE_DATABASE}")

        # 插入数据
        current_time = datetime.now()
        test_data = [
            (current_time, "000001", 100.5, 1000000, 10000000),
            (current_time - timedelta(minutes=1), "000001", 100.3, 950000, 9500000),
        ]

        try:
            # TDengine 使用直接 SQL 字符串，不使用参数化查询
            for row in test_data:
                ts_str = row[0].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 格式化时间戳
                insert_sql = f"INSERT INTO stock_tick (ts, symbol, price, volume, amount) VALUES ('{ts_str}', '{row[1]}', {row[2]}, {row[3]}, {row[4]})"
                cursor.execute(insert_sql)
            print_check("✅", "数据插入成功", f"插入 {len(test_data)} 条记录")
        except Exception as e:
            print_check("❌", "数据插入失败", str(e))
            cursor.close()
            conn.close()
            return False

        # 查询数据
        try:
            cursor.execute(
                "SELECT * FROM stock_tick WHERE symbol='000001' ORDER BY ts DESC LIMIT 5"
            )
            results = cursor.fetchall()
            print_check("✅", "数据查询成功", f"查询到 {len(results)} 条记录")
            for row in results[:3]:
                print(f"     → {row}")
        except Exception as e:
            print_check("❌", "数据查询失败", str(e))

        # 测试聚合查询
        try:
            # TDengine 3.x 聚合查询
            cursor.execute("SELECT COUNT(*) FROM stock_tick")
            count_result = cursor.fetchone()
            if count_result and count_result[0] is not None:
                print_check("✅", "聚合查询成功", f"表中总记录数: {count_result[0]}")
            else:
                print_check("⚠️", "聚合查询返回空结果")
        except Exception as e:
            print_check("⚠️", "聚合查询可能失败", str(e))

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print_check("❌", "写入/读取操作失败", str(e))
        import traceback

        traceback.print_exc()
        return False


def print_summary(results):
    """打印总结"""
    print_header("检查总结")

    passed = sum(1 for r in results if r)
    failed = len(results) - passed

    print(f"\n  ✅ 通过: {passed}/{len(results)}")
    print(f"  ❌ 失败: {failed}/{len(results)}")

    if failed == 0:
        print("\n  🎉 所有检查通过! TDengine 已准备好使用。")
        print("\n  下一步:")
        print(
            "  1. 检查数据库日志: docker-compose -f docker-compose.tdengine.yml logs tdengine"
        )
        print(
            "  2. 启动后端服务: cd web/backend && python -m uvicorn app.main:app --reload"
        )
        print("  3. 运行集成测试: pytest scripts/tests/test_tdengine_integration.py -v")
    else:
        print(f"\n  ⚠️  {failed} 个检查失败。请查看上述错误信息。")
        print("\n  故障排除:")
        print("  1. 确保TDengine容器正在运行:")
        print("     docker-compose -f docker-compose.tdengine.yml up -d")
        print("  2. 检查环境变量:")
        print(f"     TDENGINE_HOST={TDENGINE_HOST}")
        print(f"     TDENGINE_PORT={TDENGINE_PORT}")
        print(f"     TDENGINE_DATABASE={TDENGINE_DATABASE}")
        print("  3. 查看容器日志:")
        print("     docker-compose -f docker-compose.tdengine.yml logs -f tdengine")

    print(f"\n  完成时间: {datetime.now().isoformat()}\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  TDengine 简化版验证脚本")
    print("=" * 70)
    print(f"  开始时间: {datetime.now().isoformat()}")
    print(f"  TDengine 地址: {TDENGINE_HOST}:{TDENGINE_PORT}")
    print(f"  数据库: {TDENGINE_DATABASE}")

    results = [
        check_docker_status(),
        test_taos_connection(),
        test_database_operations(),
        test_write_read_operations(),
    ]

    print_summary(results)

    sys.exit(0 if all(results) else 1)
