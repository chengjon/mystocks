"""
RBAC (Role-Based Access Control) Models
======================================

This module defines the database models for Role-Based Access Control
including users, roles, permissions, and their relationships.
"""

import uuid
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)  # Hashed password
    avatar_url = Column(String(500), nullable=True)

    # OAuth2 related fields
    oauth_provider = Column(String(50), nullable=True)  # google, github, microsoft
    oauth_user_id = Column(String(255), nullable=True)
    oauth_token_data = Column(Text, nullable=True)  # JSON string for OAuth tokens

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Security fields
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_user_oauth", "oauth_provider", "oauth_user_id"),
        Index("idx_user_active", "is_active"),
        Index("idx_user_created", "created_at"),
    )

    def get_roles(self, db_session) -> List[str]:
        """获取用户所有角色"""
        return [ur.role.name for ur in self.user_roles if ur.is_active]

    def get_permissions(self, db_session) -> List[str]:
        """获取用户所有权限"""
        permissions = set()
        for user_role in self.user_roles:
            if user_role.is_active:
                for role_permission in user_role.role.role_permissions:
                    if role_permission.is_active:
                        permissions.add(role_permission.permission.name)
        return list(permissions)

    def has_permission(self, db_session, permission_name: str) -> bool:
        """检查用户是否有特定权限"""
        return permission_name in self.get_permissions(db_session)

    def has_role(self, db_session, role_name: str) -> bool:
        """检查用户是否有特定角色"""
        return role_name in self.get_roles(db_session)


class Role(Base):
    """角色模型"""

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Role hierarchy
    parent_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)

    # Role status
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System roles cannot be deleted

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    child_roles = relationship("Role", backref="parent_role", remote_side=[id])

    # Indexes
    __table_args__ = (
        Index("idx_role_active", "is_active"),
        Index("idx_role_system", "is_system"),
    )

    def get_permissions(self, db_session) -> List[str]:
        """获取角色所有权限（包括继承的权限）"""
        permissions = set()

        # Add direct permissions
        for rp in self.role_permissions:
            if rp.is_active:
                permissions.add(rp.permission.name)

        # Add inherited permissions from parent role
        if self.parent_role_id:
            parent_role = db_session.query(Role).filter(Role.id == self.parent_role_id).first()
            if parent_role and parent_role.is_active:
                permissions.update(parent_role.get_permissions(db_session))

        return list(permissions)


class Permission(Base):
    """权限模型"""

    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Permission categorization
    resource = Column(String(50), nullable=False, index=True)  # e.g., 'user', 'market', 'system'
    action = Column(String(50), nullable=False, index=True)  # e.g., 'read', 'write', 'delete'

    # Permission status
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System permissions cannot be deleted

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_permission_resource_action", "resource", "action"),
        Index("idx_permission_active", "is_active"),
    )


class UserRole(Base):
    """用户角色关联模型"""

    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)

    # Assignment details
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        Index("idx_user_role_active", "is_active"),
        Index("idx_user_role_expires", "expires_at"),
    )


class RolePermission(Base):
    """角色权限关联模型"""

    __tablename__ = "role_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False)

    # Assignment details
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        Index("idx_role_permission_active", "is_active"),
    )


class UserSession(Base):
    """用户会话模型"""

    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True, index=True)

    # Session details
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)

    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="user_sessions")

    # Indexes
    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
        Index("idx_session_token", "session_token"),
        Index("idx_session_expires", "expires_at"),
        Index("idx_session_last_activity", "last_activity"),
    )


class AuditLog(Base):
    """审计日志模型"""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., 'login', 'create_user', 'delete_role'
    resource_type = Column(String(50), nullable=False, index=True)  # e.g., 'user', 'role', 'permission'
    resource_id = Column(String(255), nullable=True)  # ID of affected resource

    # Request details
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)

    # Result
    status = Column(String(20), nullable=False, index=True)  # 'success', 'failure', 'error'
    error_message = Column(Text, nullable=True)

    # Additional data (JSON)
    additional_data = Column(Text, nullable=True)  # JSON string for additional context

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_status", "status"),
        Index("idx_audit_created", "created_at"),
        Index("idx_audit_ip", "ip_address"),
    )


class SecurityEvent(Base):
    """安全事件模型"""

    __tablename__ = "security_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Event details
    event_type = Column(
        String(50), nullable=False, index=True
    )  # e.g., 'failed_login', 'rate_limit', 'suspicious_activity'
    severity = Column(String(20), nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'

    # Event description
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Request details
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)

    # Event data (JSON)
    event_data = Column(Text, nullable=True)  # JSON string for detailed event information

    # Resolution
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])

    # Indexes
    __table_args__ = (
        Index("idx_security_event_type", "event_type"),
        Index("idx_security_severity", "severity"),
        Index("idx_security_resolved", "resolved"),
        Index("idx_security_created", "created_at"),
        Index("idx_security_ip", "ip_address"),
    )
