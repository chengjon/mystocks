"""
# 功能：数据库管理器，负责连接管理、表创建和结构验证
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import json
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import psycopg2
import pymysql
import redis
import sqlalchemy as sa
import yaml
from dotenv import load_dotenv
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseTableManager")

# 尝试导入TDengine，如果失败则设置为None
try:
    # 优先尝试原生连接方式 (native)
    try:
        import taos

        TAOS_MODULE_TYPE = "taos"
        TAOS_AVAILABLE = True
    except ImportError:
        try:
            import taosws as taos

            TAOS_MODULE_TYPE = "taosws"
            TAOS_AVAILABLE = True
        except ImportError:
            try:
                import taosrest as taos

                TAOS_MODULE_TYPE = "taosrest"
                TAOS_AVAILABLE = True
            except ImportError:
                taos = None
                TAOS_MODULE_TYPE = ""
                TAOS_AVAILABLE = False
except Exception:
    taos = None
    TAOS_MODULE_TYPE = ""
    TAOS_AVAILABLE = False

if TAOS_AVAILABLE:
    logger.info("TDengine客户端已加载: %s", TAOS_MODULE_TYPE)
else:
    logger.warning("TDengine client library not available")

# 从环境变量获取监控数据库连接
MONITOR_DB_URL = os.getenv("MONITOR_DB_URL", "mysql+pymysql://user:password@localhost/db_monitor")

Base: Any = declarative_base()


class DatabaseType(Enum):
    TDENGINE = "TDengine"
    POSTGRESQL = "PostgreSQL"
    REDIS = "Redis"
    MYSQL = "MySQL"
    MARIADB = "MariaDB"


# ORM模型
class TableCreationLog(Base):
    __tablename__ = "table_creation_log"

    id = Column(Integer, primary_key=True)
    table_name = Column(String(255), nullable=False)
    database_type = Column(String(20), nullable=False)
    database_name = Column(String(255), nullable=False)
    creation_time = Column(DateTime, default=datetime.utcnow)
    modification_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(10), nullable=False)
    table_parameters = Column(JSON, nullable=False)
    ddl_command = Column(Text, nullable=False)
    error_message = Column(Text)

    # 关系
    columns = relationship("ColumnDefinitionLog", backref="table_log", cascade="all, delete-orphan")


class ColumnDefinitionLog(Base):
    __tablename__ = "column_definition_log"

    id = Column(Integer, primary_key=True)
    table_log_id = Column(Integer, sa.ForeignKey("table_creation_log.id"))
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    col_length = Column(Integer)  # 避免使用关键字 length
    col_precision = Column(Integer)  # 避免使用关键字 precision
    col_scale = Column(Integer)  # 避免使用关键字 scale
    is_nullable = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    default_value = Column(String(255))
    comment = Column(Text)


class TableOperationLog(Base):
    __tablename__ = "table_operation_log"

    id = Column(Integer, primary_key=True)
    table_name = Column(String(255), nullable=False)
    database_type = Column(String(20), nullable=False)
    database_name = Column(String(255), nullable=False)
    operation_type: Any = Column(SQLEnum("CREATE", "ALTER", "DROP", "VALIDATE"), nullable=False)
    operation_time = Column(DateTime, default=datetime.utcnow)
    operation_status: Any = Column(SQLEnum("success", "failed", "processing"), nullable=False)
    operation_details = Column(JSON, nullable=False)
    ddl_command = Column(Text)
    error_message = Column(Text)


class TableValidationLog(Base):
    __tablename__ = "table_validation_log"

    id = Column(Integer, primary_key=True)
    table_name = Column(String(255), nullable=False)
    database_type = Column(String(20), nullable=False)
    database_name = Column(String(255), nullable=False)
    validation_time = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(String(10), nullable=False)
    validation_details = Column(JSON, nullable=False)
    issues_found = Column(Text)


class DatabaseTableManager:
    def __init__(self) -> None:
        # 初始化监控数据库连接
        self.monitor_engine = create_engine(MONITOR_DB_URL)
        Base.metadata.create_all(self.monitor_engine)
        Session = sessionmaker(bind=self.monitor_engine)
        self.monitor_session = Session()

        # 从环境变量加载各数据库连接配置，不提供默认值以确保安全性
        self.db_configs = {
            DatabaseType.TDENGINE: {
                "host": os.getenv("TDENGINE_HOST"),
                "user": os.getenv("TDENGINE_USER"),
                "password": os.getenv("TDENGINE_PASSWORD"),
                "port": int(os.getenv("TDENGINE_PORT", "6041")),
            },
            DatabaseType.POSTGRESQL: {
                "host": os.getenv("POSTGRESQL_HOST"),
                "user": os.getenv("POSTGRESQL_USER"),
                "password": os.getenv("POSTGRESQL_PASSWORD"),
                "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
            },
            DatabaseType.REDIS: {
                "host": os.getenv("REDIS_HOST"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "password": os.getenv("REDIS_PASSWORD"),
                "db": int(os.getenv("REDIS_DB", "0")),
            },
            DatabaseType.MYSQL: {
                "host": os.getenv("MYSQL_HOST"),
                "user": os.getenv("MYSQL_USER"),
                "password": os.getenv("MYSQL_PASSWORD"),
                "port": int(os.getenv("MYSQL_PORT", "3306")),
            },
            DatabaseType.MARIADB: {
                "host": os.getenv("MARIADB_HOST"),
                "user": os.getenv("MARIADB_USER"),
                "password": os.getenv("MARIADB_PASSWORD"),
                "port": int(os.getenv("MARIADB_PORT", "3307")),
            },
        }

        # 各数据库连接池
        self.db_connections: Dict[str, Any] = {}

    def get_connection(self, db_type: DatabaseType, db_name: str, **kwargs):
        """获取数据库连接"""
        conn_key = f"{db_type.value}_{db_name}"
        if conn_key in self.db_connections:
            return self.db_connections[conn_key]

        # 获取默认配置并更新用户提供的参数
        config = self.db_configs[db_type].copy()
        config.update(kwargs)

        # 验证必要的连接参数
        required_params = ["host"]
        if db_type != DatabaseType.REDIS:
            required_params.extend(["user", "password"])

        missing_params = [param for param in required_params if not config.get(param)]
        if missing_params:
            raise ValueError(f"{db_type.value} 连接参数不完整，缺少: {', '.join(missing_params)}。请检查.env文件配置")

        try:
            if db_type == DatabaseType.TDENGINE:
                # 检查TDengine是否可用
                if not TAOS_AVAILABLE:
                    raise ValueError("TDengine client library is not available. Please install TDengine client.")

                # 根据不同模块类型使用不同连接方式
                if TAOS_MODULE_TYPE == "taosws":
                    # WebSocket连接方式
                    dsn = f"ws://{config['user']}:{config['password']}@{config['host']}:{config.get('port', 6041)}"
                    if db_name:
                        dsn += f"/{db_name}"
                    conn = taos.connect(dsn)
                elif TAOS_MODULE_TYPE == "taosrest":
                    # REST API连接方式
                    conn = taos.connect(
                        url=f"http://{config['host']}:{config.get('rest_port', 6041)}",
                        user=config["user"],
                        password=config["password"],
                        database=db_name,
                    )
                else:
                    # 原生连接方式
                    conn = taos.connect(
                        host=config["host"],
                        user=config["user"],
                        password=config["password"],
                        port=config.get("port", 6030),
                        database=db_name,
                    )
            elif db_type == DatabaseType.POSTGRESQL:
                # PostgreSQL连接
                conn = psycopg2.connect(
                    host=config["host"],
                    user=config["user"],
                    password=config["password"],
                    port=config["port"],
                    database=db_name,
                )
            elif db_type == DatabaseType.REDIS:
                # Redis连接 (项目当前未使用)
                redis_port = config.get("port", 6379)
                redis_db = config.get("db", 0)
                conn = redis.Redis(
                    host=str(config.get("host", "localhost")),
                    port=int(redis_port) if redis_port is not None else 6379,
                    db=int(redis_db) if redis_db is not None else 0,
                    password=str(config.get("password")) if config.get("password") else None,
                    decode_responses=True,
                )
            elif db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
                # MySQL/MariaDB连接
                conn = pymysql.connect(
                    host=config["host"],
                    user=config["user"],
                    password=config["password"],
                    port=config["port"],
                    database=db_name,
                    charset="utf8mb4",
                )
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            self.db_connections[conn_key] = conn
            return conn

        except Exception as e:
            logger.error("Failed to connect to %s database %s: %s", db_type.value, db_name, str(e))
            raise

    def _log_operation(
        self,
        table_name: str,
        db_type: DatabaseType,
        db_name: str,
        operation_type: str,
        operation_details: Dict,
        ddl_command: str = "",
        status: str = "success",
        error_message: str = "",
    ):
        """记录操作日志到监控数据库"""
        log_entry = TableOperationLog(
            table_name=table_name,
            database_type=db_type.value,
            database_name=db_name,
            operation_type=operation_type,
            operation_status=status,
            operation_details=operation_details,
            ddl_command=ddl_command,
            error_message=error_message,
        )
        self.monitor_session.add(log_entry)
        self.monitor_session.commit()
        return log_entry.id

    def create_table(
        self,
        db_type: DatabaseType,
        db_name: str,
        table_name: str,
        columns: List[Dict],
        **kwargs,
    ) -> bool:
        """在指定数据库中创建表"""
        # 记录开始信息到监控表
        self._log_operation(
            table_name,
            db_type,
            db_name,
            "CREATE",
            {"columns": columns, "kwargs": kwargs},
            status="processing",
        )

        try:
            # 获取数据库连接
            conn = self.get_connection(db_type, db_name, **kwargs)

            # 生成DDL语句
            if db_type == DatabaseType.TDENGINE:
                ddl = self._generate_tdengine_ddl(table_name, columns, kwargs.get("tags", []), **kwargs)
                cursor = conn.cursor()
                cursor.execute(ddl)
            elif db_type == DatabaseType.POSTGRESQL:
                ddl = self._generate_postgresql_ddl(table_name, columns, **kwargs)
                cursor = conn.cursor()
                cursor.execute(ddl)
                conn.commit()
            elif db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
                ddl = self._generate_mysql_ddl(table_name, columns, **kwargs)
                cursor = conn.cursor()
                cursor.execute(ddl)
                conn.commit()
            elif db_type == DatabaseType.REDIS:
                # Redis没有表结构，这里可以创建一些初始结构
                ddl = f"REDIS INIT for {table_name}"
                self._initialize_redis_structure(conn, table_name, columns)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            # 记录表创建日志
            log_entry = TableCreationLog(
                table_name=table_name,
                database_type=db_type.value,
                database_name=db_name,
                status="success",
                table_parameters=json.dumps({"columns": columns, "kwargs": kwargs}),
                ddl_command=ddl,
            )
            self.monitor_session.add(log_entry)
            self.monitor_session.flush()  # 获取ID但不提交

            # 记录列定义
            for col_def in columns:
                col_log = ColumnDefinitionLog(
                    table_log_id=log_entry.id,
                    column_name=col_def["name"],
                    data_type=col_def["type"],
                    col_length=col_def.get("length"),
                    col_precision=col_def.get("precision"),
                    col_scale=col_def.get("scale"),
                    is_nullable=col_def.get("nullable", True),
                    is_primary_key=col_def.get("primary_key", False),
                    default_value=col_def.get("default"),
                    comment=col_def.get("comment"),
                )
                self.monitor_session.add(col_log)

            # 提交所有更改
            self.monitor_session.commit()

            # 更新操作日志
            self._log_operation(
                table_name,
                db_type,
                db_name,
                "CREATE",
                {"columns": columns, "kwargs": kwargs},
                ddl,
                "success",
            )

            # 验证表结构
            self.validate_table_structure(db_type, db_name, table_name, columns)

            return True

        except Exception as e:
            # 记录错误信息
            error_msg = str(e)
            logger.error("Failed to create table %s: %s", table_name, error_msg)

            # 更新操作日志
            self._log_operation(
                table_name,
                db_type,
                db_name,
                "CREATE",
                {"columns": columns, "kwargs": kwargs},
                "",
                "failed",
                error_msg,
            )

            self.monitor_session.rollback()
            return False

    def alter_table(
        self,
        db_type: DatabaseType,
        db_name: str,
        table_name: str,
        alterations: List[Dict],
        **kwargs,
    ) -> bool:
        """修改表结构"""
        # 记录开始信息
        self._log_operation(
            table_name,
            db_type,
            db_name,
            "ALTER",
            {"alterations": alterations, "kwargs": kwargs},
            status="processing",
        )

        try:
            conn = self.get_connection(db_type, db_name, **kwargs)
            cursor = conn.cursor()

            # 生成ALTER语句
            ddl = self._generate_alter_ddl(db_type, table_name, alterations)

            # 执行ALTER语句
            cursor.execute(ddl)
            if db_type != DatabaseType.REDIS:  # Redis不需要commit
                conn.commit()

            # 更新操作日志
            self._log_operation(
                table_name,
                db_type,
                db_name,
                "ALTER",
                {"alterations": alterations, "kwargs": kwargs},
                ddl,
                "success",
            )

            # 更新表创建日志中的修改时间
            table_log = (
                self.monitor_session.query(TableCreationLog)
                .filter_by(
                    table_name=table_name,
                    database_type=db_type.value,
                    database_name=db_name,
                )
                .first()
            )

            if table_log:
                table_log.modification_time = datetime.utcnow()  # type: ignore[assignment]
                self.monitor_session.commit()

            return True

        except Exception as e:
            error_msg = str(e)
            logger.error("Failed to alter table %s: %s", table_name, error_msg)

            self._log_operation(
                table_name,
                db_type,
                db_name,
                "ALTER",
                {"alterations": alterations, "kwargs": kwargs},
                "",
                "failed",
                error_msg,
            )

            return False

    def drop_table(self, db_type: DatabaseType, db_name: str, table_name: str, **kwargs) -> bool:
        """删除表"""
        # 记录开始信息
        self._log_operation(
            table_name,
            db_type,
            db_name,
            "DROP",
            {"kwargs": kwargs},
            status="processing",
        )

        try:
            conn = self.get_connection(db_type, db_name, **kwargs)
            cursor = conn.cursor()

            # 生成DROP语句
            if db_type == DatabaseType.TDENGINE:
                ddl = f"DROP TABLE IF EXISTS {table_name}"
            elif db_type == DatabaseType.POSTGRESQL:
                ddl = f"DROP TABLE IF EXISTS {table_name} CASCADE"
            elif db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
                ddl = f"DROP TABLE IF EXISTS {table_name}"
            elif db_type == DatabaseType.REDIS:
                # Redis没有表的概念，删除相关的所有键
                ddl = f"Redis keys deletion for pattern: {table_name}:*"
                keys = conn.keys(f"{table_name}:*")
                if keys:
                    conn.delete(*keys)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            # 执行DROP语句（Redis除外）
            if db_type != DatabaseType.REDIS:
                cursor.execute(ddl)
                conn.commit()

            # 更新操作日志
            self._log_operation(table_name, db_type, db_name, "DROP", {"kwargs": kwargs}, ddl, "success")

            # 从监控表中删除相关记录
            table_log = (
                self.monitor_session.query(TableCreationLog)
                .filter_by(
                    table_name=table_name,
                    database_type=db_type.value,
                    database_name=db_name,
                )
                .first()
            )

            if table_log:
                # 删除相关的列定义记录（由于外键约束，会级联删除）
                self.monitor_session.delete(table_log)
                self.monitor_session.commit()

            return True

        except Exception as e:
            error_msg = str(e)
            logger.error("Failed to drop table %s: %s", table_name, error_msg)

            self._log_operation(
                table_name,
                db_type,
                db_name,
                "DROP",
                {"kwargs": kwargs},
                "",
                "failed",
                error_msg,
            )

            return False

    def validate_table_structure(
        self,
        db_type: DatabaseType,
        db_name: str,
        table_name: str,
        expected_columns: List[Dict],
        **kwargs,
    ) -> Dict:
        """验证表结构是否符合预期"""
        validation_details: Dict[str, Any] = {
            "expected_columns": expected_columns,
            "actual_columns": [],
            "matches": False,
            "issues": [],
        }
        issues: List[str] = validation_details["issues"]

        try:
            # 获取实际表结构
            actual_structure = self.get_table_info(db_type, db_name, table_name, **kwargs)

            if not actual_structure:
                issues.append("Table does not exist or cannot be accessed")
                validation_status = "fail"
            else:
                validation_details["actual_columns"] = actual_structure.get("columns", [])

                # 验证列匹配
                expected_cols = {col["name"]: col for col in expected_columns}
                actual_cols = {col["name"]: col for col in actual_structure.get("columns", [])}

                # 检查缺失的列
                for col_name in expected_cols:
                    if col_name not in actual_cols:
                        issues.append(f"Missing column: {col_name}")

                # 检查多余的列
                for col_name in actual_cols:
                    if col_name not in expected_cols:
                        issues.append(f"Extra column: {col_name}")

                # 检查列属性
                for col_name in expected_cols:
                    if col_name in actual_cols:
                        expected = expected_cols[col_name]
                        actual = actual_cols[col_name]

                        # 检查数据类型
                        if expected.get("type") and actual.get("type"):
                            if expected["type"].lower() != actual["type"].lower():
                                issues.append(
                                    f"Column {col_name} type mismatch: "
                                    f"expected {expected['type']}, got {actual['type']}"
                                )

                        # 检查是否允许为空
                        if "nullable" in expected and "nullable" in actual:
                            if expected["nullable"] != actual["nullable"]:
                                issues.append(
                                    f"Column {col_name} nullable mismatch: "
                                    f"expected {expected['nullable']}, got {actual['nullable']}"
                                )

                # 确定验证状态
                validation_details["matches"] = len(issues) == 0
                validation_status = "pass" if validation_details["matches"] else "fail"

        except Exception as e:
            error_msg = str(e)
            logger.error("Failed to validate table %s: %s", table_name, error_msg)
            issues.append(f"Validation error: {error_msg}")
            validation_status = "fail"

        # 记录验证结果
        validation_log = TableValidationLog(
            table_name=table_name,
            database_type=db_type.value,
            database_name=db_name,
            validation_status=validation_status,
            validation_details=validation_details,
            issues_found=("; ".join(issues) if issues else None),
        )
        self.monitor_session.add(validation_log)
        self.monitor_session.commit()

        return validation_details

    def batch_create_tables(self, config_file: str) -> Dict:
        """通过配置文件table_config.yaml批量创建表,若yaml格式修改，这个函数也要改
        连接参数将从环境变量中自动获取，无需在YAML中配置
        """
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            results = {}
            for table_config in config.get("tables", []):
                db_type = DatabaseType[table_config["database_type"].upper()]
                db_name = table_config["database_name"]
                table_name = table_config["table_name"]
                columns = table_config["columns"]
                # 获取kwargs，如果没有则使用空字典（将使用环境变量默认值）
                kwargs = table_config.get("kwargs", {})

                result = self.create_table(db_type, db_name, table_name, columns, **kwargs)
                results[table_name] = result

            return results

        except Exception as e:
            logger.error("Failed to batch create tables: %s", str(e))
            return {"error": str(e)}

    def _generate_alter_ddl(self, db_type: DatabaseType, table_name: str, alterations: List[Dict]) -> str:
        """生成ALTER TABLE语句"""
        ddl_parts = []

        for alteration in alterations:
            operation = alteration.get("operation")  # ADD, DROP, MODIFY, RENAME

            if operation == "ADD":
                col_def = self._generate_column_definition(alteration)
                ddl_parts.append(f"ADD COLUMN {col_def}")
            elif operation == "DROP":
                ddl_parts.append(f"DROP COLUMN {alteration['column_name']}")
            elif operation == "MODIFY":
                col_def = self._generate_column_definition(alteration)
                ddl_parts.append(f"MODIFY COLUMN {col_def}")
            elif operation == "RENAME":
                ddl_parts.append(f"RENAME COLUMN {alteration['old_name']} TO {alteration['new_name']}")

        return f"ALTER TABLE {table_name} {', '.join(ddl_parts)}"

    def _generate_column_definition(self, col_def: Dict) -> str:
        """生成列定义字符串"""
        definition = f"{col_def['name']} {col_def['type']}"

        # 处理长度/精度
        if col_def.get("length") and col_def["type"].lower() in ["varchar", "char"]:
            definition += f"({col_def['length']})"
        elif col_def.get("precision") and col_def["type"].lower() in [
            "numeric",
            "decimal",
        ]:
            if col_def.get("scale"):
                definition += f"({col_def['precision']}, {col_def['scale']})"
            else:
                definition += f"({col_def['precision']})"

        # 处理约束
        if not col_def.get("nullable", True):
            definition += " NOT NULL"

        if col_def.get("default") is not None:
            definition += f" DEFAULT {col_def['default']}"

        if col_def.get("comment"):
            definition += f" COMMENT '{col_def['comment']}'"

        return definition

    # 其他方法 (_generate_tdengine_ddl, _generate_postgresql_ddl, _generate_mysql_ddl,
    # _initialize_redis_structure, get_table_info, close_all_connections) 保持不变
    # 但需要更新以使用新的列名 (col_length, col_precision, col_scale)
    def _generate_tdengine_ddl(self, table_name: str, columns: List[Dict], tags: List[Dict], **kwargs) -> str:
        """生成TDengine的DDL语句"""
        # 分离普通字段和标签字段
        normal_cols = [col for col in columns if not col.get("is_tag", False)]
        tag_cols = [col for col in columns if col.get("is_tag", False)]

        # 如果没有提供tags参数，但列中有标记为tag的，使用这些列作为tags
        if not tags and tag_cols:
            tags = tag_cols

        # 构建列定义字符串
        col_defs = []
        for col in normal_cols:
            col_def = f"{col['name']} {col['type']}"
            if col.get("length"):
                col_def += f"({col['length']})"
            col_defs.append(col_def)

        # 构建标签定义字符串
        tag_defs = []
        for tag in tags:
            tag_def = f"{tag['name']} {tag['type']}"
            if tag.get("length"):
                tag_def += f"({tag['length']})"
            tag_defs.append(tag_def)

        # 判断是否是超级表
        is_super_table = kwargs.get("is_super_table", False)

        if is_super_table:
            # 创建超级表
            ddl = f"CREATE STABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)}) TAGS ({', '.join(tag_defs)})"
        else:
            # 创建普通表
            ddl = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs + tag_defs)})"

        return ddl

    def _generate_postgresql_ddl(self, table_name: str, columns: List[Dict], **kwargs) -> str:
        """生成PostgreSQL的DDL语句"""
        col_defs = []
        primary_keys = []

        for col in columns:
            col_def = f"{col['name']} {col['type']}"

            # 处理长度/精度
            if col.get("length") and col["type"].lower() in ["varchar", "char"]:
                col_def += f"({col['length']})"
            elif col.get("precision") and col["type"].lower() in ["numeric", "decimal"]:
                if col.get("scale"):
                    col_def += f"({col['precision']}, {col['scale']})"
                else:
                    col_def += f"({col['precision']})"

            # 处理约束
            if not col.get("nullable", True):
                col_def += " NOT NULL"

            if col.get("primary_key", False):
                primary_keys.append(col["name"])

            if col.get("default") is not None:
                col_def += f" DEFAULT {col['default']}"

            col_defs.append(col_def)

        # 添加主键约束
        if primary_keys:
            col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

        ddl = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"

        # 如果是TimescaleDB超表
        if kwargs.get("is_timescale_hypertable", False):
            time_column = kwargs.get("time_column", "ts")
            ddl += f"; SELECT create_hypertable('{table_name}', '{time_column}')"

        return ddl

    def _generate_mysql_ddl(self, table_name: str, columns: List[Dict], **kwargs) -> str:
        """生成MySQL的DDL语句"""
        col_defs = []
        primary_keys = []

        for col in columns:
            col_def = f"{col['name']} {col['type']}"

            # 处理长度/精度
            if col.get("length") and col["type"].lower() in ["varchar", "char"]:
                col_def += f"({col['length']})"
            elif col.get("precision") and col["type"].lower() in ["numeric", "decimal"]:
                if col.get("scale"):
                    col_def += f"({col['precision']}, {col['scale']})"
                else:
                    col_def += f"({col['precision']})"

            # 处理约束
            if not col.get("nullable", True):
                col_def += " NOT NULL"

            if col.get("primary_key", False):
                primary_keys.append(col["name"])

            if col.get("default") is not None:
                col_def += f" DEFAULT {col['default']}"

            if col.get("comment"):
                col_def += f" COMMENT '{col['comment']}'"

            col_defs.append(col_def)

        # 添加主键约束
        if primary_keys:
            col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

        ddl = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"

        # 添加表注释
        if kwargs.get("comment"):
            ddl += f" COMMENT='{kwargs['comment']}'"

        # 添加存储引擎设置
        engine = kwargs.get("engine", "InnoDB")
        ddl += f" ENGINE={engine}"

        # 添加字符集设置
        charset = kwargs.get("charset", "utf8mb4")
        ddl += f" DEFAULT CHARSET={charset}"

        return ddl

    def _initialize_redis_structure(self, conn, key_prefix: str, columns: List[Dict]):
        """初始化Redis数据结构"""
        # 这里可以根据列定义创建一些初始的Redis结构
        # 例如，为每个列创建一个Hash字段的模板
        template_key = f"{key_prefix}:template"
        template_data = {}

        for col in columns:
            # 设置默认值
            default_value = col.get("default", "")
            if default_value is None:
                default_value = ""
            template_data[col["name"]] = str(default_value)

        # 存储模板
        conn.hmset(template_key, template_data)

        # 记录所有已创建的键
        index_key = f"{key_prefix}:index"
        conn.sadd(index_key, template_key)

    def get_table_info(self, db_type: DatabaseType, db_name: str, table_name: str, **kwargs) -> Optional[Dict]:
        """获取表结构信息"""
        try:
            conn = self.get_connection(db_type, db_name, **kwargs)
            cursor = conn.cursor()

            columns = []

            if db_type == DatabaseType.TDENGINE:
                cursor.execute(f"DESCRIBE {table_name}")
                result = cursor.fetchall()
                for row in result:
                    col_info = {
                        "name": row[0],
                        "type": row[1],
                        "length": row[2],
                        "nullable": row[4] == "YES",
                    }
                    columns.append(col_info)

            elif db_type == DatabaseType.POSTGRESQL:
                cursor.execute(
                    f"""
                    SELECT column_name, data_type, is_nullable, column_default,
                           character_maximum_length, numeric_precision, numeric_scale
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """
                )
                result = cursor.fetchall()
                for row in result:
                    col_info = {
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "default": row[3],
                        "length": row[4],
                        "precision": row[5],
                        "scale": row[6],
                    }
                    columns.append(col_info)

            elif db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
                cursor.execute(f"SHOW FULL COLUMNS FROM {table_name}")
                result = cursor.fetchall()
                for row in result:
                    col_info = {
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "default": row[4],
                        "comment": row[8],
                    }

                    # 解析类型中的长度和精度信息
                    type_str = row[1]
                    if "(" in type_str and ")" in type_str:
                        params = type_str[type_str.find("(") + 1 : type_str.find(")")]
                        if "," in params:
                            parts = params.split(",")
                            col_info["precision"] = int(parts[0])
                            col_info["scale"] = int(parts[1])
                        else:
                            col_info["length"] = int(params)

                    columns.append(col_info)

            else:
                return None

            return {"table_name": table_name, "columns": columns}

        except Exception as e:
            logger.error("Failed to get table info for %s: %s", table_name, str(e))
            return None

    def close_all_connections(self) -> None:
        """关闭所有数据库连接"""
        for conn_key, conn in self.db_connections.items():
            try:
                if hasattr(conn, "close"):
                    conn.close()
                elif isinstance(conn, redis.Redis):
                    conn.close()
            except Exception as e:
                logger.warning("Error closing connection %s: %s", conn_key, str(e))
        self.db_connections = {}

        # 关闭监控会话
        if hasattr(self, "monitor_session"):
            self.monitor_session.close()

    def close(self) -> None:
        """关闭连接的别名，用于兼容性"""
        self.close_all_connections()

    def get_tdengine_connection(self, db_name: str = "market_data", **kwargs):
        """获取TDengine连接（兼容测试）"""
        return self.get_connection(DatabaseType.TDENGINE, db_name, **kwargs)

    def get_postgresql_connection(self, db_name: str = "postgres", **kwargs):
        """获取PostgreSQL连接（兼容测试）"""
        return self.get_connection(DatabaseType.POSTGRESQL, db_name, **kwargs)

    def get_tdx_connection(self, db_name: str = "market_data", **kwargs):
        """获取TDengine连接（兼容测试）"""
        return self.get_connection(DatabaseType.TDENGINE, db_name, **kwargs)

    def __enter__(self):
        """Context manager entry - 返回自身实例"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - 确保关闭所有连接"""
        self.close_all_connections()
        return False  # 不抑制异常


# 使用示例
if __name__ == "__main__":
    # 注意：在实际使用中，所有连接参数都应该从环境变量中获取
    # 这里仅作为API使用示例，请勿硬编码敏感信息

    manager = DatabaseTableManager()

    # 批量创建表示例
    results = manager.batch_create_tables("tables_config.yaml")
    print("Batch create results:", results)

    # 修改表示例 - 所有连接参数从环境变量自动获取
    alterations = [
        {
            "operation": "ADD",
            "name": "new_column",
            "type": "VARCHAR",
            "col_length": 100,
            "nullable": True,
            "comment": "New column added by alter operation",
        }
    ]

    success = manager.alter_table(
        DatabaseType.MYSQL,
        "test_db",
        "test_table",
        alterations,
        # 注意：不再传递host, user, password等参数
        # 这些将从环境变量中自动获取
    )

    print(f"Alter table {'成功' if success else '失败'}")

    # 删除表示例 - 所有连接参数从环境变量自动获取
    success = manager.drop_table(
        DatabaseType.MYSQL,
        "test_db",
        "test_table",
        # 注意：不再传递host, user, password等参数
        # 这些将从环境变量中自动获取
    )

    print(f"Drop table {'成功' if success else '失败'}")

    manager.close_all_connections()
