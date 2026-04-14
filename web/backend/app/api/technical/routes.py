"""
技术分析API路由
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Body

from app.core.responses import UnifiedResponse

# Prefix is governed by the central route registry.
router = APIRouter()

TECHNICAL_ANALYZE_EXAMPLE = {
    "symbol": "600519",
    "indicators": {
        "ma5": 1850.5,
        "ma20": 1820.3,
        "rsi": 65.5,
        "macd": 12.3,
    },
    "period": "daily",
    "model_type": "comprehensive",
    "confidence_threshold": 0.7,
}

TECHNICAL_ANALYZE_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 503,
    "message": "Technical AI analysis is not implemented yet",
    "data": {
        "status": "placeholder",
        "endpoint": "technical",
        "symbol": "600519",
        "period": "daily",
        "model_type": "comprehensive",
        "summary": None,
        "signals": [],
        "patterns": [],
        "trend": None,
    },
}


def _success_response_spec(description: str, example: object) -> dict[int, dict]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


TECHNICAL_HEALTH_RESPONSES = _success_response_spec("技术分析服务健康状态", {"status": "ok", "service": "technical"})
TECHNICAL_STATUS_RESPONSES = _success_response_spec("技术分析服务运行状态", {"status": "active", "endpoint": "technical"})
TECHNICAL_ANALYZE_RESPONSES = _success_response_spec("技术分析 AI 兼容占位结果", TECHNICAL_ANALYZE_RESPONSE_EXAMPLE)


@router.get("/health", responses=TECHNICAL_HEALTH_RESPONSES)
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "technical"}


@router.get("/status", responses=TECHNICAL_STATUS_RESPONSES)
async def get_status():
    """获取服务状态"""
    return {"status": "active", "endpoint": "technical"}


@router.post(
    "/analyze",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=TECHNICAL_ANALYZE_RESPONSES,
)
async def analyze_data(
    data: dict = Body(..., openapi_examples={"comprehensive_technical_analysis": {"value": TECHNICAL_ANALYZE_EXAMPLE}})
) -> UnifiedResponse[Dict[str, Any]]:
    """
    技术分析 AI 智能分析。

    当前运行时尚未接入真实技术分析引擎；为了避免继续伪装成功，
    该接口显式返回 503 风格业务码和占位状态。
    """
    return UnifiedResponse(
        success=False,
        code=503,
        message="Technical AI analysis is not implemented yet",
        data={
            "status": "placeholder",
            "endpoint": "technical",
            "symbol": data.get("symbol"),
            "period": data.get("period"),
            "model_type": data.get("model_type"),
            "summary": None,
            "signals": [],
            "patterns": [],
            "trend": None,
        },
    )
