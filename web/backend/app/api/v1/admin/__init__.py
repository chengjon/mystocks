"""
管理模块API

提供审计和数据库优化功能。

说明:
- `/api/v1/auth/*` 的 canonical 入口由 `app.api.auth` 通过版本映射动态注册。
- 本 v1 admin 聚合面不再导出平行的 auth router，避免形成重复真相源。
"""

from .audit import router as audit_router
from .optimization import router as optimization_router

__all__ = ["audit_router", "optimization_router"]
