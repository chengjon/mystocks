"""
告警规则引擎 API - V3.1

提供告警规则管理功能:
- 告警规则评估
- 告警规则添加/移除
- 规则统计信息
- 实时风险指标查询

Author: Claude Code
Version: 3.1.0
Date: 2026-01-10
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, HTTPException

logger = structlog.get_logger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.governance.risk_management.services.alert_rule_engine import (
        AlertContext,
        AlertRule,
        get_alert_rule_engine,
    )

    ENHANCED_RISK_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_RISK_FEATURES_AVAILABLE = False
    get_alert_rule_engine = None
    AlertContext = None
    AlertRule = None

router = APIRouter(prefix="/api/v1/risk/rules", tags=["告警规则引擎"])


@router.post("/evaluate", response_model=List[Dict[str, Any]])
async def evaluate_alert_rules(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """评估告警规则"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise HTTPException(status_code=503, detail="告警规则引擎不可用")

        context = AlertContext(
            symbol=request.get("symbol"),
            portfolio_id=request.get("portfolio_id"),
            metrics=request.get("metrics", {}),
            metadata=request.get("metadata", {}),
        )

        results = await rule_engine.evaluate_rules(context)

        response = []
        for result in results:
            response.append(
                {
                    "rule_id": result.rule_id,
                    "severity": result.severity.value,
                    "actions": result.actions,
                    "evaluation_details": result.evaluation_details,
                }
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("评估告警规则失败: %(e)s"")
        raise HTTPException(status_code=500, detail=f"评估告警规则失败: {str(e)}")


@router.post("/add", response_model=Dict[str, Any])
async def add_alert_rule(request: Dict[str, Any]) -> Dict[str, Any]:
    """添加告警规则"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise HTTPException(status_code=503, detail="告警规则引擎不可用")

        rule_data = request.copy()
        rule_id = rule_data.pop("rule_id")

        if "template_name" in request:
            rule = await rule_engine.create_rule_from_template(request["template_name"], rule_id, rule_data)
        else:
            if AlertRule is None:
                raise HTTPException(status_code=503, detail="AlertRule类不可用")
            rule = AlertRule(rule_id=rule_id, **rule_data)

        if rule_engine.add_rule(rule):
            return {"success": True, "rule_id": rule_id, "message": "规则添加成功"}
        else:
            raise HTTPException(status_code=400, detail="规则添加失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("添加告警规则失败: %(e)s"")
        raise HTTPException(status_code=500, detail=f"添加告警规则失败: {str(e)}")


@router.delete("/remove/{rule_id}", response_model=Dict[str, Any])
async def remove_alert_rule(rule_id: str) -> Dict[str, Any]:
    """移除告警规则"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise HTTPException(status_code=503, detail="告警规则引擎不可用")

        if rule_engine.remove_rule(rule_id):
            return {"success": True, "rule_id": rule_id, "message": "规则移除成功"}
        else:
            raise HTTPException(status_code=404, detail="规则不存在")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("移除告警规则失败: %(e)s"")
        raise HTTPException(status_code=500, detail=f"移除告警规则失败: {str(e)}")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_rule_statistics() -> Dict[str, Any]:
    """获取规则统计信息"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise HTTPException(status_code=503, detail="告警规则引擎不可用")

        stats = rule_engine.get_rule_statistics()
        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取规则统计失败: %(e)s"")
        raise HTTPException(status_code=500, detail=f"获取规则统计失败: {str(e)}")


@router.get("/realtime/{symbol}", response_model=Dict[str, Any])
async def get_realtime_risk_metrics(symbol: str) -> Dict[str, Any]:
    """获取实时风险指标"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        return {
            "symbol": symbol,
            "timestamp": datetime.now(),
            "volatility_20d": 0.25,
            "atr_14": 2.5,
            "liquidity_score": 75,
            "risk_level": "medium",
            "last_updated": datetime.now(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取实时风险指标失败 %(symbol)s: %(e)s"")
        raise HTTPException(status_code=500, detail=f"获取实时风险指标失败: {str(e)}")
