# 正常执行（不删除已有表）：python execute_sql_with_env.py
# 强制删除并重建表：python execute_sql_with_env.py --drop-existing

import argparse
import os
import time

import sqlalchemy
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# 配置 loguru 日志
logger.remove()  # 移除默认处理器
logger.add(
    "logs/db_monitor_init_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    encoding="utf-8",
)
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> | {message}",
)


def find_env_file(default_path="mystocks/.env"):
    """
    智能查找环境变量文件，支持多种工作目录

    Args:
        default_path (str): 默认相对路径

    Returns:
        str: 找到的环境文件绝对路径

    Raises:
        FileNotFoundError: 如果所有路径都找不到文件
    """
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 定义多个可能的路径（按优先级排序）
    possible_paths = [
        # 1. 当前工作目录的相对路径
        default_path,
        # 2. 当前目录的 .env 文件
        ".env",
        # 3. 上级目录的 mystocks/.env
        "../mystocks/.env",
        # 4. 从脚本目录向上找到项目根目录
        os.path.join(script_dir, "../../../mystocks/.env"),
        os.path.join(script_dir, "../../.env"),
        os.path.join(script_dir, "../.env"),
        # 5. 固定的已知路径
        r"D:\MyData\GITHUB\mystocks\.env",
        # 6. 脚本目录的兄弟目录
        os.path.join(os.path.dirname(script_dir), ".env"),
    ]

    logger.debug("🔍 开始智能搜索环境文件，默认路径: %s", default_path)
    logger.debug("📁 脚本所在目录: %s", script_dir)
    logger.debug("📂 当前工作目录: %s", os.getcwd())

    for i, path in enumerate(possible_paths, 1):
        try:
            # 转换为绝对路径
            abs_path = os.path.abspath(path)
            logger.debug("📋 [%s/%s] 检查路径: %s", i, len(possible_paths), abs_path)

            if os.path.exists(abs_path):
                logger.success(f"✅ 找到环境文件: {abs_path}")
                return abs_path
            else:
                logger.debug("❌ 路径不存在: %s", abs_path)

        except Exception as e:
            logger.debug("⚠️ 检查路径时出错: %s - %s", path, str(e))
            continue

    # 如果所有路径都找不到，抛出详细错误
    error_msg = f"""
环境变量文件未找到！已尝试以下路径：
{"".join([f"  {i}. {os.path.abspath(path)}\n" for i, path in enumerate(possible_paths, 1)])}
请确保：
1. .env 文件存在于正确位置
2. 当前工作目录正确 (当前: {os.getcwd()})
3. 文件路径权限正确
"""

    logger.error(error_msg)
    raise FileNotFoundError(error_msg)


def load_env_config(env_file=None):
    """从环境变量文件加载配置"""
    # 如果没有指定路径，使用智能搜索
    if env_file is None:
        env_file = find_env_file()
    else:
        # 如果指定了路径，先检查是否存在，不存在则使用智能搜索
        if not os.path.exists(env_file):
            logger.warning("⚠️ 指定的环境文件不存在: %s，尝试智能搜索...", env_file)
            env_file = find_env_file()
        else:
            env_file = os.path.abspath(env_file)

    logger.info("🔍 开始加载环境配置文件: %s", env_file)
    config = {}
    start_time = time.time()

    try:
        logger.success(f"✓ 环境文件存在: {env_file}")

        # 读取文件内容
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            logger.info("📄 读取到 %s 行配置", len(lines))

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith("#"):
                    continue

                # 解析键值对
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
                    logger.debug("第%s行: 加载配置 %s", line_num, key.strip())

        host = config.get("MONITOR_DB_HOST") or config.get("POSTGRESQL_HOST")
        user = config.get("MONITOR_DB_USER") or config.get("POSTGRESQL_USER")
        password = config.get("MONITOR_DB_PASSWORD") or config.get("POSTGRESQL_PASSWORD")
        port = config.get("MONITOR_DB_PORT") or config.get("POSTGRESQL_PORT")

        missing_keys = []
        if not host:
            missing_keys.append("MONITOR_DB_HOST/POSTGRESQL_HOST")
        if not user:
            missing_keys.append("MONITOR_DB_USER/POSTGRESQL_USER")
        if not password:
            missing_keys.append("MONITOR_DB_PASSWORD/POSTGRESQL_PASSWORD")
        if not port:
            missing_keys.append("MONITOR_DB_PORT/POSTGRESQL_PORT")

        if missing_keys:
            raise ValueError(f"环境变量文件缺少必要配置: {', '.join(missing_keys)}")

        # 构建数据库配置
        db_config = {
            "user": user,
            "password": password,
            "host": host,
            "port": int(port),
            "database": config.get("MONITOR_DB_DATABASE") or "mystocks_monitoring",
            "admin_database": config.get("MONITOR_DB_ADMIN_DB") or config.get("POSTGRESQL_ADMIN_DB") or "postgres",
        }

        load_time = time.time() - start_time
        logger.success(f"✓ 环境配置加载成功! 耗时: {load_time:.3f}s")
        logger.info("🔗 数据库连接信息: %s@%s:%s", db_config["user"], db_config["host"], db_config["port"])

        return db_config

    except Exception as e:
        load_time = time.time() - start_time
        logger.error("❌ 加载配置失败 (耗时: %ss): %s", load_time, str(e))
        raise


def get_sql_commands(drop_existing=False):
    """生成PostgreSQL SQL命令，支持删除已有表选项"""
    drop_commands = ""
    if drop_existing:
        drop_commands = """
        DROP TABLE IF EXISTS table_validation_log;
        DROP TABLE IF EXISTS table_operation_log;
        DROP TABLE IF EXISTS column_definition_log;
        DROP TABLE IF EXISTS table_creation_log;
        """

    create_table_prefix = "CREATE TABLE IF NOT EXISTS" if not drop_existing else "CREATE TABLE"

    return f"""
{drop_commands}

{create_table_prefix} table_creation_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    database_type VARCHAR(20) NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    creation_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modification_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL,
    table_parameters JSONB NOT NULL,
    ddl_command TEXT NOT NULL,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_table_creation_db_type ON table_creation_log (database_type);
CREATE INDEX IF NOT EXISTS idx_table_creation_time ON table_creation_log (creation_time);

{create_table_prefix} column_definition_log (
    id SERIAL PRIMARY KEY,
    table_log_id INT NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    col_length INT,
    col_precision INT,
    col_scale INT,
    is_nullable BOOLEAN DEFAULT TRUE,
    is_primary_key BOOLEAN DEFAULT FALSE,
    default_value VARCHAR(255),
    comment TEXT,
    CONSTRAINT fk_table_log FOREIGN KEY (table_log_id) REFERENCES table_creation_log(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_column_table_log_id ON column_definition_log (table_log_id);

{create_table_prefix} table_operation_log (
    id SERIAL PRIMARY KEY,
    operation_id VARCHAR(100) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    database_type VARCHAR(20) NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    operation_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    operation_status VARCHAR(20) NOT NULL,
    operation_details JSONB NOT NULL,
    ddl_command TEXT,
    error_message TEXT,
    data_count INT DEFAULT 0,
    duration_seconds NUMERIC(10,3) DEFAULT 0,
    end_time TIMESTAMPTZ NULL,
    UNIQUE (operation_id)
);

CREATE INDEX IF NOT EXISTS idx_operation_time ON table_operation_log (operation_time);
CREATE INDEX IF NOT EXISTS idx_operation_type ON table_operation_log (operation_type);

{create_table_prefix} table_validation_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    database_type VARCHAR(20) NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    validation_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    validation_status VARCHAR(10) NOT NULL,
    validation_details JSONB NOT NULL,
    issues_found TEXT
);

CREATE INDEX IF NOT EXISTS idx_validation_time ON table_validation_log (validation_time);
"""


def create_database_and_tables(drop_existing=False):
    """创建数据库和表结构"""
    logger.info("🚀 开始创建数据库和表结构 (drop_existing=%s)", drop_existing)
    start_time = time.time()

    try:
        # 从 env 文件加载配置
        db_config = load_env_config()

        def is_safe_identifier(name: str) -> bool:
            import re

            return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))

        if not is_safe_identifier(db_config["database"]):
            raise ValueError(f"非法数据库名称: {db_config['database']}")

        # 连接到管理库，创建监控数据库（如不存在）
        admin_connection_str = (
            f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['admin_database']}"
        )

        logger.info("🔗 连接管理库: %s@%s:%s", db_config["user"], db_config["host"], db_config["port"])

        admin_engine = sqlalchemy.create_engine(admin_connection_str)
        with admin_engine.connect() as admin_connection:
            admin_connection = admin_connection.execution_options(autocommit=True)
            logger.success("✓ 管理库连接成功")

            exists = admin_connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_config["database"]},
            ).fetchone()
            if not exists:
                admin_connection.execute(text(f'CREATE DATABASE "{db_config["database"]}"'))
                logger.info("📁 创建数据库: %s", db_config["database"])
            else:
                logger.info("📁 数据库已存在: %s", db_config["database"])

        # 连接监控数据库
        connection_str = (
            f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )

        logger.info("🔗 连接监控数据库: %s@%s:%s", db_config["user"], db_config["host"], db_config["port"])

        engine = sqlalchemy.create_engine(connection_str)
        with engine.connect() as connection:
            logger.success("✓ 数据库连接成功")

            # 获取 SQL 命令
            sql_commands = get_sql_commands(drop_existing=drop_existing).split(";")

            # 统计信息
            total_commands = len([cmd for cmd in sql_commands if cmd.strip()])
            executed_commands = 0
            failed_commands = 0

            logger.info("📄 将执行 %s 条 SQL 命令", total_commands)

            # 执行 SQL 命令
            for i, cmd in enumerate(sql_commands, 1):
                cmd = cmd.strip()
                if cmd:  # 跳过空命令
                    cmd_start_time = time.time()
                    try:
                        # 判断命令类型
                        if "CREATE TABLE" in cmd:
                            table_name = extract_table_name(cmd)
                            logger.info("📊 [%s/%s] 创建表: %s", i, total_commands, table_name)
                        elif "DROP TABLE" in cmd:
                            logger.warning("🗑️ [%s/%s] 删除表", i, total_commands)
                        else:
                            logger.debug("📋 [%s/%s] 执行 SQL: %s...", i, total_commands, cmd[:100])

                        connection.execute(text(cmd))
                        cmd_time = time.time() - cmd_start_time
                        executed_commands += 1

                        if cmd_time > 0.1:  # 只记录较慢的命令
                            logger.debug("⏱️ 命令执行时间: %ss", cmd_time)

                    except Exception as cmd_error:
                        cmd_time = time.time() - cmd_start_time
                        failed_commands += 1
                        logger.error(
                            "❌ [%s/%s] SQL执行失败 (耗时: %ss): %s", i, total_commands, cmd_time, str(cmd_error)
                        )
                        logger.debug("失败的SQL: %s...", cmd[:200])

        total_time = time.time() - start_time

        # 输出成功统计
        logger.success("✓ 数据库初始化完成!")
        logger.info("📊 执行统计: 成功 %s / 失败 %s / 总计 %s", executed_commands, failed_commands, total_commands)
        logger.info("⏱️ 总执行时间: %ss", total_time)

        # 输出创建的资源汇总
        logger.info("📦 创建的资源汇总:")
        logger.info("  • 数据库: %s", db_config["database"])
        logger.info("  • 表结构:")
        tables = [
            "table_creation_log - 表创建日志表",
            "column_definition_log - 列定义日志表",
            "table_operation_log - 表操作日志表",
            "table_validation_log - 表结构验证日志表",
        ]
        for table in tables:
            logger.info("    ▫ %s", table)

        return True

    except SQLAlchemyError as e:
        total_time = time.time() - start_time
        logger.error("❌ 执行 SQL 时发生错误 (耗时: %ss): %s", total_time, str(e))
        return False
    except Exception as e:
        total_time = time.time() - start_time
        logger.error("❌ 发生意外错误 (耗时: %ss): %s", total_time, str(e))
        return False


def init_monitoring_database(drop_existing=False):
    """
    初始化监控数据库（专用于 Jupyter 环境调用）

    Args:
        drop_existing (bool): 是否删除已存在的表

    Returns:
        bool: 初始化是否成功

    Examples:
        # 在 Jupyter 中使用
        success = init_monitoring_database()

        # 删除已存在的表并重建
        success = init_monitoring_database(drop_existing=True)
    """
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)

    logger.info("=" * 60)
    logger.info("🎯 数据库监控初始化程序启动 (Jupyter API)")
    logger.info("⚙️ 参数设置: drop_existing=%s", drop_existing)
    logger.info("=" * 60)

    # 执行数据库初始化
    success = create_database_and_tables(drop_existing=drop_existing)

    # 程序结束记录
    if success:
        logger.success("🎉 数据库监控初始化程序执行成功!")
    else:
        logger.error("💥 数据库监控初始化程序执行失败!")

    logger.info("=" * 60)
    return success


def extract_table_name(sql_cmd):
    """从 CREATE TABLE 命令中提取表名"""
    try:
        # 匹配 CREATE TABLE [IF NOT EXISTS] table_name
        import re

        pattern = r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)"
        match = re.search(pattern, sql_cmd, re.IGNORECASE)
        return match.group(1) if match else "未知表"
    except Exception:
        return "未知表"


if __name__ == "__main__":
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)

    # 检测是否在 Jupyter 环境中运行
    in_jupyter = False
    try:
        # 检查是否存在 ipykernel
        from IPython import get_ipython

        if get_ipython() is not None:
            in_jupyter = True
    except ImportError:
        pass

    if in_jupyter:
        # 在 Jupyter 环境中，使用默认参数
        logger.info("🔬 检测到 Jupyter 环境，使用默认参数")
        drop_existing = False
    else:
        # 在命令行环境中，解析命令行参数
        parser = argparse.ArgumentParser(description="创建监控数据库和表结构")
        parser.add_argument("--drop-existing", action="store_true", help="删除已存在的表（如果存在）")
        args = parser.parse_args()
        drop_existing = args.drop_existing

    # 记录程序启动
    logger.info("=" * 60)
    logger.info("🎯 数据库监控初始化程序启动")
    logger.info("⚙️ 参数设置: drop_existing=%s", drop_existing)
    logger.info("🌐 运行环境: %s", "Jupyter" if in_jupyter else "Command Line")
    logger.info("=" * 60)

    # 执行数据库初始化
    success = create_database_and_tables(drop_existing=drop_existing)

    # 程序结束记录
    if success:
        logger.success("🎉 数据库监控初始化程序执行成功!")
    else:
        logger.error("💥 数据库监控初始化程序执行失败!")

    logger.info("=" * 60)
