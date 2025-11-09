#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财数据ORM模型

定义问财查询和结果的数据库模型

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    TIMESTAMP,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from app.core.database import Base


class WencaiQuery(Base):
    """
    问财查询定义表

    存储预定义的查询语句配置
    """

    __tablename__ = "wencai_queries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_name = Column(
        String(20), unique=True, nullable=False, index=True, comment="查询名称，如qs_1"
    )
    query_text = Column(Text, nullable=False, comment="查询语句（自然语言）")
    description = Column(String(255), nullable=True, comment="查询说明")
    is_active = Column(
        Boolean, default=True, nullable=False, index=True, comment="是否启用"
    )
    created_at = Column(
        TIMESTAMP, default=datetime.now, nullable=False, comment="创建时间"
    )
    updated_at = Column(
        TIMESTAMP,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="更新时间",
    )

    __table_args__ = (
        Index("idx_query_name", "query_name"),
        Index("idx_is_active", "is_active"),
        {
            "comment": "问财查询定义表",
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    def __repr__(self):
        return f"<WencaiQuery(id={self.id}, name='{self.query_name}', active={self.is_active})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "query_name": self.query_name,
            "query_text": self.query_text,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WencaiResultBase:
    """
    问财查询结果基类（抽象类）

    用于动态创建查询结果表（wencai_qs_1 ~ wencai_qs_9）
    注意：实际的结果表会根据问财API返回的数据动态创建，
          因为不同查询返回的字段不同

    共同字段：
    - id: 主键
    - fetch_time: 数据获取时间
    - 取数区间: 查询时间范围
    - 其他字段: 根据问财API返回动态添加
    """

    @declared_attr
    def __tablename__(cls):
        """动态表名"""
        # 子类需要实现此方法
        raise NotImplementedError("Subclasses must define __tablename__")

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fetch_time = Column(TIMESTAMP, nullable=False, index=True, comment="数据获取时间")

    @declared_attr
    def __table_args__(cls):
        """表配置"""
        return (
            Index(f"idx_{cls.__tablename__}_fetch_time", "fetch_time"),
            {
                "comment": f"{cls.__tablename__} 查询结果表",
                "mysql_engine": "InnoDB",
                "mysql_charset": "utf8mb4",
                "mysql_collate": "utf8mb4_unicode_ci",
            },
        )


# 注意：由于问财API返回的字段是动态的，实际的查询结果表
# 将通过 pandas.to_sql() 方法动态创建，而不是预先定义ORM模型

# 如果需要查询历史结果，可以使用原生SQL或动态构建ORM模型
