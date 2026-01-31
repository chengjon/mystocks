"""
持仓风险评估 API - V3.1

提供持仓风险评估功能:
- 仓位风险评估
- 集中度分析
- 风险等级判定
- 风险告警生成

Author: Claude Code
Version: 3.1.0
Date: 2026-01-10
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

import structlog
from fastapi import APIRouter, HTTPException

logger = structlog.get_logger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

router = APIRouter(prefix="/api/v1/risk/position", tags=["持仓风险评估"])


@router.post("/assess")
async def assess_position_risk(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    评估仓位风险

    请求示例:
    ```json
    {
      "positions": [
        {"symbol": "sh600000", "value": 150000, "sector": "金融"},
        {"symbol": "sh600036", "value": 120000, "sector": "金融"}
      ],
      "total_capital": 1000000,
      "config": {
        "max_position_size": 0.10,
        "daily_loss_limit": 0.05
      }
    }
    ```
    """
    try:
        positions = request.get("positions", [])
        total_capital = request.get("total_capital", 1000000)
        config = request.get("config", {})

        max_position_size = config.get("max_position_size", 0.10)

        total_position_value = sum(p.get("value", 0) for p in positions)
        position_ratio = total_position_value / total_capital if total_capital > 0 else 0
        cash_ratio = 1 - position_ratio

        position_concentration = []
        exceeded_positions = []
        sector_concentration = {}

        for pos in positions:
            symbol = pos.get("symbol", "UNKNOWN")
            value = pos.get("value", 0)
            sector = pos.get("sector", "UNKNOWN")

            concentration = value / total_capital if total_capital > 0 else 0
            exceeds_limit = concentration > max_position_size

            position_concentration.append(
                {
                    "symbol": symbol,
                    "concentration": concentration,
                    "exceeds_limit": exceeds_limit,
                }
            )

            if exceeds_limit:
                exceeded_positions.append({"symbol": symbol, "concentration": concentration})

            if sector not in sector_concentration:
                sector_concentration[sector] = 0
            sector_concentration[sector] += value

        position_sizes = [p["value"] / total_capital for p in positions if total_capital > 0]
        herfindahl_index = sum(p**2 for p in position_sizes) if position_sizes else 0

        if len(exceeded_positions) > 0 or herfindahl_index > 0.5:
            risk_level = "HIGH"
        elif herfindahl_index > 0.25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "status": "success",
            "risk_assessment": {
                "total_position_value": total_position_value,
                "position_ratio": position_ratio,
                "cash_ratio": cash_ratio,
                "position_concentration": position_concentration,
                "exceeded_positions": exceeded_positions,
                "high_concentration_risk": len(exceeded_positions) > 0,
                "sector_concentration": {
                    sector: value / total_capital if total_capital > 0 else 0
                    for sector, value in sector_concentration.items()
                },
                "herfindahl_index": herfindahl_index,
                "risk_level": risk_level,
            },
            "assessed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error("评估仓位风险失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"评估仓位风险失败: {str(e)}")


@router.post("/alerts/generate")
async def generate_risk_alerts(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成风险告警

    请求示例:
    ```json
    {
      "current_drawdown": -0.25,
      "daily_pnl": -60000,
      "total_capital": 1000000,
      "config": {
        "max_drawdown_threshold": 0.30,
        "daily_loss_limit": 0.05
      }
    }
    ```
    """
    try:
        current_drawdown = request.get("current_drawdown", 0)
        daily_pnl = request.get("daily_pnl", 0)
        total_capital = request.get("total_capital", 1000000)
        config = request.get("config", {})

        max_drawdown_threshold = config.get("max_drawdown_threshold", 0.30)
        daily_loss_limit = config.get("daily_loss_limit", 0.05)

        alerts = []
        alert_time = datetime.now().isoformat()

        if abs(current_drawdown) > max_drawdown_threshold:
            alerts.append(
                {
                    "type": "max_drawdown_exceeded",
                    "severity": "CRITICAL",
                    "message": (
                        f"最大回撤超限: {abs(current_drawdown) * 100:.2f}% > {max_drawdown_threshold * 100:.2f}%"
                    ),
                    "timestamp": alert_time,
                    "suggestion": "立即减仓或平仓，控制风险敞口",
                }
            )

        daily_loss_pct = daily_pnl / total_capital if total_capital > 0 else 0
        if daily_loss_pct < -daily_loss_limit:
            alerts.append(
                {
                    "type": "daily_loss_limit_exceeded",
                    "severity": "WARNING",
                    "message": (f"单日亏损超限: {daily_loss_pct * 100:.2f}% < {-daily_loss_limit * 100:.2f}%"),
                    "timestamp": alert_time,
                    "suggestion": "暂停开仓，检查策略执行情况",
                }
            )

        return {
            "status": "success" if alerts else "normal",
            "alerts": alerts,
            "generated_at": alert_time,
        }

    except Exception as e:
        logger.error("生成风险告警失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成风险告警失败: {str(e)}")
