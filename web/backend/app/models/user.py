#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# 功能：user模块
# 作者：JohnC (ninjas@sina.com) & Claude
# 日期：2025-11-18
# 版本：1.0.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：模块功能实现
# 版权：© 2025 MyStocks Project

"""
User models - 数据库模型

"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """用户模型 - 对应数据库中的 users 表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(100), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # user, admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', role='{self.role}')>"


class UserToken(Base):
    """用户令牌模型 - 用于令牌管理"""

    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    token = Column(String(200), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False)  # access, refresh
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserToken(user_id='{self.user_id}', token_type='{self.token_type}')>"
