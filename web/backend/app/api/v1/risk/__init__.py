"""
风险管理领域聚合路由 - V3.1

聚合以下子领域:
- core: 风险指标核心计算
- stop_loss: 止损管理
- alerts: 风险告警管理
- rules: 告警规则引擎
- position: 持仓风险评估

Author: Claude Code
Version: 3.1.0
Date: 2026-01-10
"""

from fastapi import APIRouter
from . import core, stop_loss, alerts, rules, position

router = APIRouter(prefix="/api/v1/risk", tags=["风险管理"])

router.include_router(core.router)
router.include_router(stop_loss.router)
router.include_router(alerts.router)
router.include_router(rules.router)
router.include_router(position.router)
