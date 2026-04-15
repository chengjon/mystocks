"""技术分析API路由。"""

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
    "success": True,
    "code": 200,
    "message": "Technical analysis completed from provided indicators",
    "data": {
        "status": "available",
        "endpoint": "technical",
        "symbol": "600519",
        "period": "daily",
        "model_type": "comprehensive",
        "summary": "短期趋势强于中期趋势，指标组合偏多头。",
        "signals": ["ma_bullish_cross", "macd_positive", "rsi_neutral"],
        "patterns": ["trend_following_setup"],
        "trend": "bullish",
        "confidence": 0.77,
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


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _analyze_trend(indicators: dict[str, Any]) -> str:
    ma5 = _safe_float(indicators.get("ma5"))
    ma20 = _safe_float(indicators.get("ma20"))
    macd = _safe_float(indicators.get("macd"))

    bullish_votes = sum(
        (
            1 if ma5 is not None and ma20 is not None and ma5 > ma20 else 0,
            1 if macd is not None and macd > 0 else 0,
        )
    )
    bearish_votes = sum(
        (
            1 if ma5 is not None and ma20 is not None and ma5 < ma20 else 0,
            1 if macd is not None and macd < 0 else 0,
        )
    )

    if bullish_votes > bearish_votes:
        return "bullish"
    if bearish_votes > bullish_votes:
        return "bearish"
    return "neutral"


def _build_signals(indicators: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    ma5 = _safe_float(indicators.get("ma5"))
    ma20 = _safe_float(indicators.get("ma20"))
    macd = _safe_float(indicators.get("macd"))
    rsi = _safe_float(indicators.get("rsi"))

    if ma5 is not None and ma20 is not None:
        signals.append("ma_bullish_cross" if ma5 >= ma20 else "ma_bearish_cross")
    if macd is not None:
        signals.append("macd_positive" if macd >= 0 else "macd_negative")
    if rsi is not None:
        if rsi >= 70:
            signals.append("rsi_overbought")
        elif rsi <= 30:
            signals.append("rsi_oversold")
        else:
            signals.append("rsi_neutral")
    return signals


def _build_patterns(trend: str, signals: list[str]) -> list[str]:
    patterns: list[str] = []
    if trend == "bullish" and "rsi_overbought" not in signals:
        patterns.append("trend_following_setup")
    if trend == "bearish" and "rsi_oversold" not in signals:
        patterns.append("downtrend_pressure")
    if "rsi_oversold" in signals or "rsi_overbought" in signals:
        patterns.append("mean_reversion_watch")
    return patterns


def _build_summary(trend: str, signals: list[str]) -> str:
    if trend == "bullish":
        return "短期趋势强于中期趋势，指标组合偏多头。"
    if trend == "bearish":
        return "短期趋势弱于中期趋势，指标组合偏空头。"
    if "rsi_overbought" in signals or "rsi_oversold" in signals:
        return "趋势信号不一致，当前更适合观察均值回归条件。"
    return "趋势与动量信号较为中性，暂未形成明确方向。"


def _build_confidence(signals: list[str], patterns: list[str]) -> float:
    confidence = 0.45 + (0.1 * len(signals)) + (0.05 * len(patterns))
    return round(min(confidence, 0.95), 2)


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
    技术分析智能分析。

    当前实现基于请求中传入的技术指标做规则驱动分析，
    返回趋势、信号和模式摘要，避免继续保留占位成功壳。
    """
    indicators = data.get("indicators") if isinstance(data.get("indicators"), dict) else {}
    trend = _analyze_trend(indicators)
    signals = _build_signals(indicators)
    patterns = _build_patterns(trend, signals)
    summary = _build_summary(trend, signals)

    return UnifiedResponse(
        success=True,
        code=200,
        message="Technical analysis completed from provided indicators",
        data={
            "status": "available",
            "endpoint": "technical",
            "symbol": data.get("symbol"),
            "period": data.get("period"),
            "model_type": data.get("model_type"),
            "summary": summary,
            "signals": signals,
            "patterns": patterns,
            "trend": trend,
            "confidence": _build_confidence(signals, patterns),
        },
    )
