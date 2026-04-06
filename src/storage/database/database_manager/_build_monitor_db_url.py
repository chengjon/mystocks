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

import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any

import sqlalchemy as sa
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
)
from sqlalchemy.orm import declarative_base, relationship

# Create declarative base for SQLAlchemy models
Base = declarative_base()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseTableManager")


def _safe_load_dotenv() -> None:
    """导入期仅做非阻塞环境加载，避免因本地 .env 权限导致模块不可导入。"""
    try:
        load_dotenv()
    except OSError as error:
        logger.warning("skip load_dotenv during import: %s", error)


_safe_load_dotenv()

def _build_monitor_db_url() -> str:
    monitor_url = os.getenv("MONITOR_DB_URL")
    if monitor_url:
        return monitor_url

    host = os.getenv("MONITOR_DB_HOST") or os.getenv("POSTGRESQL_HOST", "localhost")
    port = os.getenv("MONITOR_DB_PORT") or os.getenv("POSTGRESQL_PORT", "5432")
    user = os.getenv("MONITOR_DB_USER") or os.getenv("POSTGRESQL_USER", "postgres")
    password = os.getenv("MONITOR_DB_PASSWORD") or os.getenv("POSTGRESQL_PASSWORD", "")
    database = os.getenv("MONITOR_DB_DATABASE") or os.getenv("POSTGRESQL_DATABASE", "mystocks")

    if password:
        auth = f"{user}:{password}"
    else:
        auth = user

    return f"postgresql+psycopg2://{auth}@{host}:{port}/{database}"


class DatabaseType(Enum):
    TDENGINE = "TDengine"
    POSTGRESQL = "PostgreSQL"
    REDIS = "Redis"


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
    operation_type: Any = Column(
        SQLEnum("CREATE", "ALTER", "DROP", "VALIDATE", native_enum=False),
        nullable=False,
    )
    operation_time = Column(DateTime, default=datetime.utcnow)
    operation_status: Any = Column(
        SQLEnum("success", "failed", "processing", native_enum=False),
        nullable=False,
    )
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

