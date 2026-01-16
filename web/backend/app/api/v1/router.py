"""
MyStocks API v1 聚合路由

按业务领域组织API端点：
- system: 系统健康检查、数据路由
- strategy: ML策略、技术指标
- trading: 交易会话、持仓管理
- admin: 认证、审计、优化
- analysis: 情感分析、回测、压力测试

Usage:
    from web.backend.app.api.v1.router import api_v1_router

    app.include_router(api_v1_router)
"""

from fastapi import APIRouter
from .system import health_router, routing_router
from .strategy import ml_router, indicators_router
from .trading import session_router, positions_router
from .admin import auth_router, audit_router, optimization_router
from .analysis import sentiment_router, backtest_router, stress_test_router

api_v1_router = APIRouter(
    prefix="/api/v1",
    tags=["MyStocks API v1"],
)

# 系统管理路由
api_v1_router.include_router(health_router)
api_v1_router.include_router(routing_router)

# 策略路由
api_v1_router.include_router(ml_router)
api_v1_router.include_router(indicators_router)

# 交易路由
api_v1_router.include_router(session_router)
api_v1_router.include_router(positions_router)

# 管理路由
api_v1_router.include_router(auth_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(optimization_router)

# 分析路由
api_v1_router.include_router(sentiment_router)
api_v1_router.include_router(backtest_router)
api_v1_router.include_router(stress_test_router)

__all__ = ["api_v1_router"]
