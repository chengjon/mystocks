"""
用户模型 - SQLAlchemy ORM
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    LargeBinary,
    ARRAY,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class User(Base):
    """
    用户模型 - 对应PostgreSQL中的users表

    用于存储用户账户信息、认证凭证和账户状态
    """

    __tablename__ = "users"

    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)

    # 认证信息
    hashed_password = Column(String(255), nullable=True)  # 可选，OAuth2用户可能没有密码

    # 用户属性
    role = Column(
        String(50), default="user", nullable=False
    )  # user, analyst, trader, admin
    is_active = Column(Boolean, default=True, nullable=False)

    # 邮箱验证
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)

    # MFA/2FA
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_method = Column(String(20), nullable=True)  # 'totp', 'email', 'sms'

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv4 or IPv6

    # 用户详情
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # 账户安全
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)  # 账户被锁定的时间

    # 密码安全历史
    password_changed_at = Column(DateTime, nullable=True)

    # 用户偏好设置（JSON格式）
    preferences = Column(Text, nullable=True)  # JSON格式的用户偏好

    # 账户状态标记
    deletion_requested_at = Column(DateTime, nullable=True)  # 账户删除请求时间

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "mfa_enabled": self.mfa_enabled,
            "mfa_method": self.mfa_method,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class OAuth2Account(Base):
    """
    OAuth2 关联账户模型

    用于存储第三方OAuth2提供商（Google、GitHub等）的关联账户信息
    """

    __tablename__ = "oauth2_accounts"

    id = Column(Integer, primary_key=True, index=True)

    # 用户关联
    user_id = Column(Integer, nullable=False, index=True)  # 外键：users.id

    # OAuth2提供商信息
    provider = Column(
        String(50), nullable=False, index=True
    )  # 'google', 'github', 'microsoft'等
    provider_user_id = Column(
        String(255), nullable=False, index=True
    )  # OAuth2提供商中的用户ID

    # OAuth2令牌信息
    access_token = Column(String(1000), nullable=True)
    refresh_token = Column(String(1000), nullable=True)
    token_type = Column(String(50), default="Bearer", nullable=False)
    token_expires_at = Column(DateTime, nullable=True)

    # 用户信息（存储提供商返回的用户信息，便于更新）
    provider_email = Column(String(100), nullable=True)
    provider_name = Column(String(100), nullable=True)
    provider_avatar = Column(String(500), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_used_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<OAuth2Account(user_id={self.user_id}, provider={self.provider})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider": self.provider,
            "provider_email": self.provider_email,
            "provider_name": self.provider_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
        }


class MFASecret(Base):
    """
    MFA 密钥模型

    存储用户的MFA配置，包括TOTP密钥、备用码等
    """

    __tablename__ = "mfa_secrets"

    id = Column(Integer, primary_key=True, index=True)

    # 用户关联
    user_id = Column(Integer, nullable=False, index=True)  # 外键：users.id

    # MFA方法
    method = Column(String(20), nullable=False)  # 'totp', 'email', 'sms'

    # MFA密钥/凭���
    secret = Column(String(255), nullable=False)  # TOTP密钥或其他凭证

    # 备用码（comma-separated或JSON格式）
    backup_codes = Column(Text, nullable=True)  # JSON格式的备用码列表

    # 状态
    verified = Column(Boolean, default=False, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime, nullable=True)

    # 配置元数据（JSON格式）
    config = Column(Text, nullable=True)  # MFA特定的配置参数

    def __repr__(self):
        return f"<MFASecret(user_id={self.user_id}, method={self.method}, verified={self.verified})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "method": self.method,
            "verified": self.verified,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
        }


class PasswordResetToken(Base):
    """
    密码重置令牌模型

    用于存储密码重置请求及其令牌
    """

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)

    # 用户关联
    user_id = Column(Integer, nullable=False, index=True)  # 外键：users.id

    # 令牌信息
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)

    # 使用状态
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # IP和User Agent信息用于安全审计
    request_ip = Column(String(45), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, used={self.used})>"


class EmailVerificationToken(Base):
    """
    邮箱验证令牌模型

    用于存储邮箱验证请求及其令牌
    """

    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)

    # 用户关联
    user_id = Column(Integer, nullable=False, index=True)  # 外键：users.id
    email = Column(String(100), nullable=False)  # 要验证的邮箱地址

    # 令牌信息
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)

    # 使用状态
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # IP信息用于安全审计
    request_ip = Column(String(45), nullable=True)

    # 重试计数
    attempt_count = Column(Integer, default=0, nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<EmailVerificationToken(user_id={self.user_id}, email={self.email}, used={self.used})>"


class LoginAuditLog(Base):
    """
    登录审计日志模型

    记录所有登录尝试（成功和失败）用于安全审计
    """

    __tablename__ = "login_audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 用户信息
    user_id = Column(Integer, nullable=True, index=True)  # 失败的登录可能没有user_id
    username = Column(String(50), nullable=False)  # 记录尝试登录的用户名

    # 登录结果
    success = Column(Boolean, nullable=False)
    failure_reason = Column(
        String(100), nullable=True
    )  # 'invalid_password', 'user_not_found', 'account_locked'等

    # 请求信息
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)

    # MFA信息
    mfa_passed = Column(Boolean, nullable=True)  # 如果需要MFA，此字段记录MFA是否通过

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<LoginAuditLog(user_id={self.user_id}, username={self.username}, success={self.success})>"
