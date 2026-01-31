"""
管理模块API

提供认证、审计和数据库优化功能

子模块:
- auth.py: 用户认证
- audit.py: 审计日志
- optimization.py: 数据库优化
"""

from .audit import router as audit_router
from .auth import router as auth_router
from .optimization import router as optimization_router

__all__ = ["auth_router", "audit_router", "optimization_router"]
