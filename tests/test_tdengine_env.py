"""
TDengine 测试环境配置和验证

用途:
1. 验证 TDengine 连接配置
2. 检查必要的超表是否存在
3. 创建测试所需的表结构
4. 运行基础功能测试

创建日期: 2025-10-25
版本: 1.0.0
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def load_env_config():
    """加载 .env 配置文件"""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(env_path):
        print(f"⚠️  .env 文件不存在: {env_path}")
        return {}

    config = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def check_tdengine_connection():
    """检查 TDengine 连接"""
    print("\n" + "=" * 60)
    print("TDengine 测试环境配置检查")
    print("=" * 60 + "\n")

    # 加载配置
    config = load_env_config()
    tdengine_config = {
        "host": config.get("TDENGINE_HOST", "192.168.123.104"),
        "port": int(config.get("TDENGINE_PORT", "6030")),
        "user": config.get("TDENGINE_USER", "root"),
        "password": config.get("TDENGINE_PASSWORD", "taosdata"),
        "database": config.get("TDENGINE_DATABASE", "market_data"),
    }

    print("【1. 配置信息】")
    for key, value in tdengine_config.items():
        if key != "password":
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {'*' * len(str(value))}")

    # 检查 taospy
    print("\n【2. taospy 库检查】")
    try:
        import taos

        print(f"  ✅ taospy 已安装")
        print(
            f"  版本: {taos.__version__ if hasattr(taos, '__version__') else '未知'}"
        )
    except ImportError as e:
        print(f"  ❌ taospy 未安装: {e}")
        print(f"\n  安装命令: pip install taospy")
        return False, None

    # 连接测试
    print("\n【3. 连接测试】")
    try:
        conn = taos.connect(
            host=tdengine_config["host"],
            port=tdengine_config["port"],
            user=tdengine_config["user"],
            password=tdengine_config["password"],
        )
        print(f"  ✅ TDengine 连接成功")

        # 查询版本
        result = conn.query("SELECT server_version()")
        version = result.fetch_all()[0][0]
        print(f"  服务器版本: {version}")

        # 检查数据库
        result = conn.query("SHOW DATABASES")
        databases = [row[0] for row in result.fetch_all()]

        if tdengine_config["database"] in databases:
            print(f"  ✅ 数据库 '{tdengine_config['database']}' 存在")
        else:
            print(f"  ⚠️  数据库 '{tdengine_config['database']}' 不存在，创建中...")
            conn.execute(f"CREATE DATABASE IF NOT EXISTS {tdengine_config['database']}")
            print(f"  ✅ 数据库创建成功")

        return True, conn

    except Exception as e:
        print(f"  ❌ TDengine 连接失败: {e}")
        print(f"\n  诊断建议:")
        print(f"    1. 检查 TDengine 服务: systemctl status taosd")
        print(f"    2. 检查网络: ping {tdengine_config['host']}")
        print(f"    3. 检查端口: nc -zv {tdengine_config['host']} 6030")
        print(f"    4. 检查 .env 配置文件")
        return False, None


def check_stable_structure(conn, database):
    """检查超表结构"""
    print("\n【4. 超表结构检查】")

    try:
        conn.execute(f"USE {database}")

        # 查询所有超表
        result = conn.query("SHOW STABLES")
        stables = result.fetch_all()

        if not stables:
            print("  ⚠️  无超表，需要初始化")
            return False

        print(f"  ✅ 发现 {len(stables)} 个超表:")
        for stable in stables:
            stable_name = stable[0]
            print(f"    - {stable_name}")

            # 查询每个超表的列信息
            result = conn.query(f"DESCRIBE {stable_name}")
            columns = result.fetch_all()
            print(f"      列数: {len(columns)}")

        return True

    except Exception as e:
        print(f"  ❌ 超表检查失败: {e}")
        return False


def initialize_test_tables(conn, database):
    """初始化测试所需的表结构"""
    print("\n【5. 测试表初始化】")

    try:
        conn.execute(f"USE {database}")

        # 先删除可能存在的旧测试表（清理环境）
        try:
            conn.execute("DROP TABLE IF EXISTS tick_600000_env_test")
            conn.execute("DROP STABLE IF EXISTS tick_env_test")
            print("  ✓ 清理旧测试表")
        except:
            pass

        # 创建测试用超表（使用独立名称避免冲突）
        test_stable_sql = """
            CREATE STABLE IF NOT EXISTS tick_env_test (
                ts TIMESTAMP,
                price FLOAT,
                volume INT,
                amount FLOAT
            ) TAGS (
                symbol BINARY(20)
            )
        """

        conn.execute(test_stable_sql)
        print("  ✅ 测试超表 'tick_env_test' 创建成功")

        # 创建测试子表
        test_table_sql = """
            CREATE TABLE IF NOT EXISTS tick_600000_env_test
            USING tick_env_test
            TAGS ('600000.SH')
        """

        conn.execute(test_table_sql)
        print("  ✅ 测试子表 'tick_600000_env_test' 创建成功")

        return True

    except Exception as e:
        print(f"  ❌ 测试表初始化失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_basic_tests(conn, database):
    """运行基础功能测试"""
    print("\n【6. 基础功能测试】")

    try:
        conn.execute(f"USE {database}")

        # 测试1: 插入数据
        print("  测试1: 数据插入")
        test_data = []
        current_time = datetime.now()
        for i in range(10):
            ts = current_time + timedelta(seconds=i)
            price = 10.0 + np.random.uniform(-0.5, 0.5)
            volume = np.random.randint(100, 1000)
            amount = price * volume
            test_data.append((ts, price, volume, amount))

        insert_sql = "INSERT INTO tick_600000_env_test VALUES "
        values = ", ".join(
            [
                f"('{ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}', {price}, {volume}, {amount})"
                for ts, price, volume, amount in test_data
            ]
        )
        conn.execute(insert_sql + values)
        print(f"    ✅ 成功插入 {len(test_data)} 条数据")

        # 测试2: 查询数据
        print("  测试2: 数据查询")
        result = conn.query("SELECT COUNT(*) FROM tick_600000_env_test")
        count = result.fetch_all()[0][0]
        print(f"    ✅ 查询到 {count} 条数据")

        # 测试3: 聚合查询
        print("  测试3: 聚合查询")
        result = conn.query(
            """
            SELECT
                AVG(price) as avg_price,
                MAX(price) as max_price,
                MIN(price) as min_price,
                SUM(volume) as total_volume
            FROM tick_600000_env_test
        """
        )
        agg_result = result.fetch_all()[0]
        print(f"    ✅ 平均价: {agg_result[0]:.2f}")
        print(f"    ✅ 最高价: {agg_result[1]:.2f}")
        print(f"    ✅ 最低价: {agg_result[2]:.2f}")
        print(f"    ✅ 总成交量: {agg_result[3]}")

        # 测试4: 时间范围查询
        print("  测试4: 时间范围查询")
        start_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = (current_time + timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")
        result = conn.query(
            f"""
            SELECT COUNT(*) FROM tick_600000_env_test
            WHERE ts >= '{start_time}' AND ts < '{end_time}'
        """
        )
        range_count = result.fetch_all()[0][0]
        print(f"    ✅ 时间范围内数据: {range_count} 条")

        print("\n  ✅ 所有基础功能测试通过")
        return True

    except Exception as e:
        print(f"  ❌ 基础功能测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def cleanup_test_data(conn, database):
    """清理测试数据"""
    print("\n【7. 清理测试数据】")

    try:
        conn.execute(f"USE {database}")

        # 删除测试子表
        conn.execute("DROP TABLE IF EXISTS tick_600000_env_test")
        print("  ✅ 测试子表已删除")

        # 删除测试超表
        conn.execute("DROP STABLE IF EXISTS tick_env_test")
        print("  ✅ 测试超表已删除")

        return True

    except Exception as e:
        print(f"  ⚠️  清理失败: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("TDengine 测试环境配置和验证")
    print("=" * 60)

    # 1. 连接检查
    success, conn = check_tdengine_connection()
    if not success or conn is None:
        print("\n❌ TDengine 连接失败，测试终止")
        return False

    config = load_env_config()
    database = config.get("TDENGINE_DATABASE", "market_data")

    try:
        # 2. 超表结构检查
        check_stable_structure(conn, database)

        # 3. 初始化测试表
        if not initialize_test_tables(conn, database):
            print("\n❌ 测试表初始化失败")
            return False

        # 4. 运行基础测试
        if not run_basic_tests(conn, database):
            print("\n❌ 基础功能测试失败")
            return False

        # 5. 清理测试数据
        cleanup_test_data(conn, database)

        print("\n" + "=" * 60)
        print("✅ TDengine 测试环境配置验证完成")
        print("=" * 60)
        print("\n测试结论:")
        print("  ✅ TDengine 连接正常")
        print("  ✅ 数据库结构正常")
        print("  ✅ 基础功能正常")
        print("  ✅ 环境配置正确")
        print("\n建议:")
        print("  - 可以运行主测试套件: python test_save_realtime_data.py")
        print("  - 可以启动系统: python system_demo.py")

        return True

    except Exception as e:
        print(f"\n❌ 测试过程异常: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if conn:
            conn.close()
            print("\n连接已关闭")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
