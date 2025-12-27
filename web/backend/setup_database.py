#!/usr/bin/env python3
"""
MyStocks数据库初始化脚本
功能:
1. 验证TimescaleDB扩展
2. 创建所有PostgreSQL表
3. 创建所有MySQL表
"""

import os
import sys
from pathlib import Path
import psycopg2
import pymysql
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class DatabaseSetup:
    def __init__(self):
        # PostgreSQL配置
        self.pg_config = {
            "host": os.getenv("POSTGRESQL_HOST", "localhost"),
            "port": int(os.getenv("POSTGRESQL_PORT", 5432)),
            "user": os.getenv("POSTGRESQL_USER", "postgres"),
            "password": os.getenv("POSTGRESQL_PASSWORD", "your_password"),
            "database": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        }

        # MySQL配置
        self.mysql_config = {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", 3306)),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", "your_password"),
            "database": os.getenv("MYSQL_DATABASE", "quant_research"),
            "charset": "utf8mb4",
        }

    def verify_timescaledb(self):
        """验证TimescaleDB扩展是否已安装"""
        print("=" * 60)
        print("步骤1: 验证TimescaleDB扩展")
        print("=" * 60)

        try:
            conn = psycopg2.connect(**self.pg_config)
            cur = conn.cursor()

            # 检查TimescaleDB扩展
            cur.execute(
                """
                SELECT extname, extversion
                FROM pg_extension
                WHERE extname = 'timescaledb';
            """
            )

            result = cur.fetchone()

            if result:
                extname, extversion = result
                print(f"✅ TimescaleDB已安装: {extname} v{extversion}")

                # 获取TimescaleDB版本详细信息
                cur.execute("SELECT extversion FROM pg_extension WHERE extname='timescaledb';")
                version = cur.fetchone()[0]
                print(f"   版本: {version}")

                cur.close()
                conn.close()
                return True
            else:
                print("❌ TimescaleDB未安装")
                print("   请先安装TimescaleDB扩展:")
                print("   CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
                cur.close()
                conn.close()
                return False

        except Exception as e:
            print(f"❌ 连接PostgreSQL失败: {e}")
            return False

    def create_postgresql_tables(self):
        """创建PostgreSQL表"""
        print("\n" + "=" * 60)
        print("步骤2: 创建PostgreSQL表")
        print("=" * 60)

        try:
            conn = psycopg2.connect(**self.pg_config)
            conn.autocommit = True
            cur = conn.cursor()

            # 读取SQL脚本
            sql_file = Path(__file__).parent / "init_tables.sql"

            if not sql_file.exists():
                print(f"❌ SQL文件不存在: {sql_file}")
                return False

            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # 移除\echo命令(psql特有命令)
            sql_lines = []
            for line in sql_content.split("\n"):
                if not line.strip().startswith("\\echo"):
                    sql_lines.append(line)

            sql_content = "\n".join(sql_lines)

            # 执行SQL
            print("⏳ 正在执行SQL脚本...")
            cur.execute(sql_content)

            # 验证表是否创建成功
            tables = [
                "stock_fund_flow",
                "etf_spot_data",
                "chip_race_data",
                "stock_lhb_detail",
                "strategy_signals",
                "backtest_trades",
                "backtest_results",
            ]

            print("\n验证表创建状态:")
            for table in tables:
                cur.execute(
                    f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table}'
                    );
                """
                )
                exists = cur.fetchone()[0]
                status = "✅" if exists else "❌"
                print(f"   {status} {table}")

            # 检查hypertable
            print("\n验证TimescaleDB hypertable:")
            cur.execute(
                """
                SELECT hypertable_name
                FROM timescaledb_information.hypertables
                WHERE hypertable_schema = 'public';
            """
            )
            hypertables = cur.fetchall()

            if hypertables:
                for ht in hypertables:
                    print(f"   ✅ {ht[0]} (hypertable)")
            else:
                print("   ⚠️  未找到hypertable(可能需要手动创建)")

            cur.close()
            conn.close()
            print("\n✅ PostgreSQL表创建完成!")
            return True

        except Exception as e:
            print(f"❌ 创建PostgreSQL表失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def create_mysql_tables(self):
        """创建MySQL表"""
        print("\n" + "=" * 60)
        print("步骤3: 创建MySQL表")
        print("=" * 60)

        try:
            conn = pymysql.connect(**self.mysql_config)
            cur = conn.cursor()

            # 读取SQL脚本
            sql_file = Path(__file__).parent / "init_mysql_tables.sql"

            if not sql_file.exists():
                print(f"❌ SQL文件不存在: {sql_file}")
                return False

            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # 分割并执行每条SQL语句
            print("⏳ 正在执行SQL脚本...")

            # 执行USE语句
            cur.execute(f"USE {self.mysql_config['database']}")

            # 逐条执行SQL(跳过USE和SELECT语句)
            for statement in sql_content.split(";"):
                statement = statement.strip()
                if statement and not statement.startswith("USE") and not statement.startswith("SELECT"):
                    cur.execute(statement)

            conn.commit()

            # 验证表是否创建成功
            tables = ["strategy_configs", "dividend_data"]

            print("\n验证表创建状态:")
            for table in tables:
                cur.execute(f"SHOW TABLES LIKE '{table}'")
                exists = cur.fetchone()
                status = "✅" if exists else "❌"
                print(f"   {status} {table}")

            cur.close()
            conn.close()
            print("\n✅ MySQL表创建完成!")
            return True

        except Exception as e:
            print(f"❌ 创建MySQL表失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def run(self):
        """执行完整的数据库设置流程"""
        print("\n" + "=" * 60)
        print("MyStocks 数据库初始化")
        print("=" * 60 + "\n")

        # 步骤1: 验证TimescaleDB
        if not self.verify_timescaledb():
            print("\n❌ 初始化失败: TimescaleDB未安装")
            return False

        # 步骤2: 创建PostgreSQL表
        if not self.create_postgresql_tables():
            print("\n❌ 初始化失败: PostgreSQL表创建失败")
            return False

        # 步骤3: 创建MySQL表
        if not self.create_mysql_tables():
            print("\n❌ 初始化失败: MySQL表创建失败")
            return False

        print("\n" + "=" * 60)
        print("✅ 数据库初始化完成!")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 检查表结构: psql -d mystocks -c '\\dt'")
        print('  2. 检查hypertable: psql -d mystocks -c "SELECT * FROM timescaledb_information.hypertables;"')
        print("  3. 检查MySQL表: mysql -e 'USE quant_research; SHOW TABLES;'")

        return True


if __name__ == "__main__":
    setup = DatabaseSetup()
    success = setup.run()
    sys.exit(0 if success else 1)
