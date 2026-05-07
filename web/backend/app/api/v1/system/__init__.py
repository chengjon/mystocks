"""
系统管理API模块

提供系统健康检查和数据路由功能

子模块:
- health.py: 数据库健康检查、数据分类统计
- resources.py: 单节点 host / process / dependency 资源快照
- routing.py: 智能数据路由
- settings.py: 系统级 general/security 配置契约
"""

from .health import router as health_router
from .resources import router as resources_router
from .routing import router as routing_router
from .settings import router as settings_router

__all__ = ["health_router", "resources_router", "routing_router", "settings_router"]
