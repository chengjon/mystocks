"""
系统管理API模块

提供系统健康检查和数据路由功能

子模块:
- health.py: 数据库健康检查、数据分类统计
- routing.py: 智能数据路由
"""

from .health import router as health_router
from .routing import router as routing_router

__all__ = ["health_router", "routing_router"]
