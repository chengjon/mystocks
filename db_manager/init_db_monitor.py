#正常执行（不删除已有表）：python execute_sql_with_env.py
#强制删除并重建表：python execute_sql_with_env.py --drop-existing

import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import argparse
import os
import time
from loguru import logger

# 配置 loguru 日志
logger.remove()  # 移除默认处理器
logger.add(
    "logs/db_monitor_init_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    encoding="utf-8"
)
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> | {message}"
)

def find_env_file(default_path='mystocks/.env'):
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
        '.env',
        
        # 3. 上级目录的 mystocks/.env
        '../mystocks/.env',
        
        # 4. 从脚本目录向上找到项目根目录
        os.path.join(script_dir, '../../../mystocks/.env'),
        os.path.join(script_dir, '../../.env'),
        os.path.join(script_dir, '../.env'),
        
        # 5. 固定的已知路径
        r'D:\MyData\GITHUB\mystocks\.env',
        
        # 6. 脚本目录的兄弟目录
        os.path.join(os.path.dirname(script_dir), '.env'),
    ]
    
    logger.debug(f"🔍 开始智能搜索环境文件，默认路径: {default_path}")
    logger.debug(f"📁 脚本所在目录: {script_dir}")
    logger.debug(f"📂 当前工作目录: {os.getcwd()}")
    
    for i, path in enumerate(possible_paths, 1):
        try:
            # 转换为绝对路径
            abs_path = os.path.abspath(path)
            logger.debug(f"📋 [{i}/{len(possible_paths)}] 检查路径: {abs_path}")
            
            if os.path.exists(abs_path):
                logger.success(f"✅ 找到环境文件: {abs_path}")
                return abs_path
            else:
                logger.debug(f"❌ 路径不存在: {abs_path}")
                
        except Exception as e:
            logger.debug(f"⚠️ 检查路径时出错: {path} - {str(e)}")
            continue
    
    # 如果所有路径都找不到，抛出详细错误
    error_msg = f"""
环境变量文件未找到！已尝试以下路径：
{''.join([f"  {i}. {os.path.abspath(path)}\n" for i, path in enumerate(possible_paths, 1)])}
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
            logger.warning(f"⚠️ 指定的环境文件不存在: {env_file}，尝试智能搜索...")
            env_file = find_env_file()
        else:
            env_file = os.path.abspath(env_file)
    
    logger.info(f"🔍 开始加载环境配置文件: {env_file}")
    config = {}
    start_time = time.time()
    
    try:
        logger.success(f"✓ 环境文件存在: {env_file}")
        
        # 读取文件内容
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            logger.info(f"📄 读取到 {len(lines)} 行配置")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                
                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
                    logger.debug(f"第{line_num}行: 加载配置 {key.strip()}")
        
        # 验证必要的配置项
        required_keys = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_PORT']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            raise ValueError(f"环境变量文件缺少必要配置: {', '.join(missing_keys)}")
        
        # 构建数据库配置
        db_config = {
            'user': config['MYSQL_USER'],
            'password': config['MYSQL_PASSWORD'],
            'host': config['MYSQL_HOST'],
            'port': int(config['MYSQL_PORT']),
            'database': 'mysql',  # 初始连接使用的数据库
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        
        load_time = time.time() - start_time
        logger.success(f"✓ 环境配置加载成功! 耗时: {load_time:.3f}s")
        logger.info(f"🔗 数据库连接信息: {config['MYSQL_USER']}@{config['MYSQL_HOST']}:{config['MYSQL_PORT']}")
        
        return db_config
        
    except Exception as e:
        load_time = time.time() - start_time
        logger.error(f"❌ 加载配置失败 (耗时: {load_time:.3f}s): {str(e)}")
        raise

def get_sql_commands(drop_existing=False, charset='utf8mb4', collation='utf8mb4_unicode_ci'):
    """生成SQL命令，支持删除已有表选项"""
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
CREATE DATABASE IF NOT EXISTS db_monitor 
    CHARACTER SET {charset} 
    COLLATE {collation};

USE db_monitor;

{drop_commands}

{create_table_prefix} table_creation_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    table_name VARCHAR(255) NOT NULL COMMENT '表名',
    database_type ENUM('TDengine', 'PostgreSQL', 'Redis', 'MySQL', 'MariaDB') NOT NULL COMMENT '数据库类型',
    database_name VARCHAR(255) NOT NULL COMMENT '数据库名称',
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    modification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    status ENUM('success', 'failed') NOT NULL COMMENT '创建状态',
    table_parameters JSON NOT NULL COMMENT '表参数配置（JSON格式）',
    ddl_command TEXT NOT NULL COMMENT '执行的DDL命令',
    error_message TEXT COMMENT '错误信息（如有）',
    INDEX idx_database_type (database_type),
    INDEX idx_creation_time (creation_time)
) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT='表创建日志表';

{create_table_prefix} column_definition_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    table_log_id INT NOT NULL COMMENT '关联的表创建日志ID',
    column_name VARCHAR(255) NOT NULL COMMENT '列名',
    data_type VARCHAR(100) NOT NULL COMMENT '数据类型',
    col_length INT COMMENT '列长度',
    col_precision INT COMMENT '精度',
    col_scale INT COMMENT '小数位数',
    is_nullable BOOLEAN DEFAULT TRUE COMMENT '是否允许为空',
    is_primary_key BOOLEAN DEFAULT FALSE COMMENT '是否为主键',
    default_value VARCHAR(255) COMMENT '默认值',
    comment TEXT COMMENT '列备注',
    FOREIGN KEY (table_log_id) REFERENCES table_creation_log(id) ON DELETE CASCADE,
    INDEX idx_table_log_id (table_log_id)
) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT='列定义日志表';

-- 新增表操作日志表
{create_table_prefix} table_operation_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    table_name VARCHAR(255) NOT NULL COMMENT '表名',
    database_type ENUM('TDengine', 'PostgreSQL', 'Redis', 'MySQL', 'MariaDB') NOT NULL COMMENT '数据库类型',
    database_name VARCHAR(255) NOT NULL COMMENT '数据库名称',
    operation_type ENUM('CREATE', 'ALTER', 'DROP', 'VALIDATE') NOT NULL COMMENT '操作类型',
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    operation_status ENUM('success', 'failed', 'processing') NOT NULL COMMENT '操作状态',
    operation_details JSON NOT NULL COMMENT '操作详情（JSON格式）',
    ddl_command TEXT COMMENT '执行的DDL命令',
    error_message TEXT COMMENT '错误信息（如有）',
    INDEX idx_operation_time (operation_time),
    INDEX idx_operation_type (operation_type)
) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT='表操作日志表';

-- 新增表结构验证日志表
{create_table_prefix} table_validation_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    table_name VARCHAR(255) NOT NULL COMMENT '表名',
    database_type ENUM('TDengine', 'PostgreSQL', 'Redis', 'MySQL', 'MariaDB') NOT NULL COMMENT '数据库类型',
    database_name VARCHAR(255) NOT NULL COMMENT '数据库名称',
    validation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '验证时间',
    validation_status ENUM('pass', 'fail') NOT NULL COMMENT '验证状态',
    validation_details JSON NOT NULL COMMENT '验证详情（JSON格式）',
    issues_found TEXT COMMENT '发现的问题',
    INDEX idx_validation_time (validation_time)
) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT='表结构验证日志表';
"""

def create_database_and_tables(drop_existing=False):
    """创建数据库和表结构"""
    logger.info(f"🚀 开始创建数据库和表结构 (drop_existing={drop_existing})")
    start_time = time.time()
    
    try:
        # 从 env 文件加载配置
        db_config = load_env_config()
        
        # 创建数据库连接字符串
        connection_str = (
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}?"
            f"charset={db_config['charset']}"
        )
        
        logger.info(f"🔗 连接数据库: {db_config['user']}@{db_config['host']}:{db_config['port']}")
        
        # 建立数据库连接
        engine = sqlalchemy.create_engine(connection_str)
        with engine.connect() as connection:
            # 确保自动提交模式开启
            connection = connection.execution_options(autocommit=True)
            logger.success("✓ 数据库连接成功")
            
            # 获取 SQL 命令
            sql_commands = get_sql_commands(
                drop_existing=drop_existing,
                charset=db_config['charset'],
                collation=db_config['collation']
            ).split(';')
            
            # 统计信息
            total_commands = len([cmd for cmd in sql_commands if cmd.strip()])
            executed_commands = 0
            failed_commands = 0
            
            logger.info(f"📄 将执行 {total_commands} 条 SQL 命令")
            
            # 执行 SQL 命令
            for i, cmd in enumerate(sql_commands, 1):
                cmd = cmd.strip()
                if cmd:  # 跳过空命令
                    cmd_start_time = time.time()
                    try:
                        # 判断命令类型
                        if 'CREATE DATABASE' in cmd:
                            logger.info(f"📁 [{i}/{total_commands}] 创建数据库: db_monitor")
                        elif 'USE db_monitor' in cmd:
                            logger.info(f"🔄 [{i}/{total_commands}] 切换到数据库: db_monitor")
                        elif 'CREATE TABLE' in cmd:
                            table_name = extract_table_name(cmd)
                            logger.info(f"📊 [{i}/{total_commands}] 创建表: {table_name}")
                        elif 'DROP TABLE' in cmd:
                            logger.warning(f"🗑️ [{i}/{total_commands}] 删除表")
                        else:
                            logger.debug(f"📋 [{i}/{total_commands}] 执行 SQL: {cmd[:50]}...")
                        
                        connection.execute(text(cmd))
                        cmd_time = time.time() - cmd_start_time
                        executed_commands += 1
                        
                        if cmd_time > 0.1:  # 只记录较慢的命令
                            logger.debug(f"⏱️ 命令执行时间: {cmd_time:.3f}s")
                        
                    except Exception as cmd_error:
                        cmd_time = time.time() - cmd_start_time
                        failed_commands += 1
                        logger.error(f"❌ [{i}/{total_commands}] SQL执行失败 (耗时: {cmd_time:.3f}s): {str(cmd_error)}")
                        logger.debug(f"失败的SQL: {cmd[:100]}...")
        
        total_time = time.time() - start_time
        
        # 输出成功统计
        logger.success(f"✓ 数据库初始化完成!")
        logger.info(f"📊 执行统计: 成功 {executed_commands} / 失败 {failed_commands} / 总计 {total_commands}")
        logger.info(f"⏱️ 总执行时间: {total_time:.3f}s")
        
        # 输出创建的资源汇总
        logger.info("📦 创建的资源汇总:")
        logger.info("  • 数据库: db_monitor")
        logger.info("  • 表结构:")
        tables = [
            "table_creation_log - 表创建日志表",
            "column_definition_log - 列定义日志表",
            "table_operation_log - 表操作日志表",
            "table_validation_log - 表结构验证日志表"
        ]
        for table in tables:
            logger.info(f"    ▫ {table}")
        
        return True
        
    except SQLAlchemyError as e:
        total_time = time.time() - start_time
        logger.error(f"❌ 执行 SQL 时发生错误 (耗时: {total_time:.3f}s): {str(e)}")
        return False
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"❌ 发生意外错误 (耗时: {total_time:.3f}s): {str(e)}")
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
    
    logger.info("="*60)
    logger.info("🎯 数据库监控初始化程序启动 (Jupyter API)")
    logger.info(f"⚙️ 参数设置: drop_existing={drop_existing}")
    logger.info("="*60)
    
    # 执行数据库初始化
    success = create_database_and_tables(drop_existing=drop_existing)
    
    # 程序结束记录
    if success:
        logger.success("🎉 数据库监控初始化程序执行成功!")
    else:
        logger.error("💥 数据库监控初始化程序执行失败!")
    
    logger.info("="*60)
    return success

def extract_table_name(sql_cmd):
    """从 CREATE TABLE 命令中提取表名"""
    try:
        # 匹配 CREATE TABLE [IF NOT EXISTS] table_name
        import re
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)'
        match = re.search(pattern, sql_cmd, re.IGNORECASE)
        return match.group(1) if match else "未知表"
    except:
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
        parser = argparse.ArgumentParser(description='创建监控数据库和表结构')
        parser.add_argument('--drop-existing', action='store_true', 
                          help='删除已存在的表（如果存在）')
        args = parser.parse_args()
        drop_existing = args.drop_existing
    
    # 记录程序启动
    logger.info("="*60)
    logger.info("🎯 数据库监控初始化程序启动")
    logger.info(f"⚙️ 参数设置: drop_existing={drop_existing}")
    logger.info(f"🌐 运行环境: {'Jupyter' if in_jupyter else 'Command Line'}")
    logger.info("="*60)
    
    # 执行数据库初始化
    success = create_database_and_tables(drop_existing=drop_existing)
    
    # 程序结束记录
    if success:
        logger.success("🎉 数据库监控初始化程序执行成功!")
    else:
        logger.error("💥 数据库监控初始化程序执行失败!")
    
    logger.info("="*60)
    