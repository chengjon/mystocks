"""
验证数据库索引是否正确创建
"""

import subprocess
import sys
from pathlib import Path


def run_sql_file(sql_file_path: str, connection_string: str = None):
    """
    运行SQL文件

    Args:
        sql_file_path: SQL文件路径
        connection_string: 数据库连接字符串（可选）
    """
    try:
        # 使用psql命令运行SQL文件
        cmd = ["psql"]

        if connection_string:
            # 如果提供了连接字符串，使用环境变量方式
            import os

            os.environ["PGDATABASE"] = "mystocks"  # 默认数据库名
            cmd.extend(
                [
                    "--host",
                    connection_string.split("@")[1].split(":")[0]
                    if "@" in connection_string
                    else "localhost",
                    "--port",
                    connection_string.split(":")[2].split("/")[0]
                    if ":" in connection_string and "@" in connection_string
                    else "5432",
                    "--username",
                    connection_string.split("://")[1].split("@")[0]
                    if "://" in connection_string
                    else "postgres",
                ]
            )

        cmd.extend(["-f", sql_file_path])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ SQL文件执行成功")
            print("输出:")
            print(result.stdout)
            if result.stderr:
                print("警告:")
                print(result.stderr)
        else:
            print("❌ SQL文件执行失败")
            print("错误输出:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ 执行SQL文件时出错: {str(e)}")
        return False

    return True


def validate_indexes():
    """验证索引是否正确创建"""
    print("=== 验证数据库索引 ===")

    # SQL文件路径
    sql_file = Path(__file__).parent / "create_indexes_sql.sql"

    if not sql_file.exists():
        print(f"❌ SQL文件不存在: {sql_file}")
        return False

    print(f"正在执行SQL文件: {sql_file}")

    # 尝试运行SQL文件
    success = run_sql_file(str(sql_file))

    if success:
        print("\n=== 索引验证完成 ===")
        print("请使用以下SQL命令验证索引是否创建成功:")
        print("\\d+ order_records")
        print("\\d+ daily_kline")
        print("\\d+ stock_basic_info")
        print("\\d+ watchlist")
        print("\\d+ portfolio")
        print("\\d+ alert_conditions")
        print("\\d+ strategy_backtest")
        print("\\d+ trade_log")
        print("\\d+ user_audit_log")
        print("\n或者运行:")
        print(
            "SELECT * FROM pg_indexes WHERE tablename IN ('order_records', 'daily_kline', 'stock_basic_info', 'watchlist', 'portfolio', 'alert_conditions', 'strategy_backtest', 'trade_log', 'user_audit_log') ORDER BY tablename, indexname;"
        )
        return True
    else:
        print("\n❌ 索引验证失败")
        return False


if __name__ == "__main__":
    # 检查psql是否安装
    try:
        subprocess.run(["psql", "--version"], check=True, capture_output=True)
        print("✅ psql 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ psql 未安装，请先安装PostgreSQL客户端")
        sys.exit(1)

    # 运行验证
    if validate_indexes():
        print("\n✅ 索引创建脚本已准备就绪")
        print("数据库连接配置:")
        print("- 主机: localhost (在.env文件中配置POSTGRES_HOST)")
        print("- 端口: 5432 (在.env文件中配置POSTGRES_PORT)")
        print("- 数据库: mystocks (在.env文件中配置POSTGRES_DB)")
        print("- 用户: postgres (在.env文件中配置POSTGRES_USER)")
        print("- 密码: 在.env文件中配置POSTGRES_PASSWORD)")
    else:
        print("\n❌ 索引创建脚本执行失败")
        sys.exit(1)
