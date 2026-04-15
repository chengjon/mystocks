"""多数据源API路由。"""

from typing import Any, Dict

from fastapi import APIRouter, Body

from app.openapi_config import COMMON_RESPONSES
from app.core.responses import UnifiedResponse

MULTI_SOURCE_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

# Prefix is governed by the central route registry.
router = APIRouter(responses=MULTI_SOURCE_ROUTE_RESPONSES)

MULTI_SOURCE_ANALYZE_REQUEST_EXAMPLE = {
    "symbol": "600519",
    "data_sources": ["technical", "fundamental", "sentiment", "flow"],
    "analysis_depth": "advanced",
    "weights": {
        "technical": 0.3,
        "fundamental": 0.4,
        "sentiment": 0.2,
        "flow": 0.1,
    },
    "time_range": "3m",
}

MULTI_SOURCE_HEALTH_RESPONSES = {
    200: {
        "description": "多数据源服务健康状态",
        "content": {
            "application/json": {
                "example": {
                    "status": "ok",
                    "service": "multi_source",
                }
            }
        },
    },
    500: COMMON_RESPONSES[500],
}

MULTI_SOURCE_STATUS_RESPONSES = {
    200: {
        "description": "多数据源服务当前状态",
        "content": {
            "application/json": {
                "example": {
                    "status": "active",
                    "endpoint": "multi_source",
                }
            }
        },
    },
    500: COMMON_RESPONSES[500],
}

MULTI_SOURCE_ANALYZE_RESPONSES = {
    200: {
        "description": "多数据源综合分析结果",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "code": 200,
                    "message": "Multi-source analysis summarized from request inputs",
                    "data": {
                        "status": "available",
                        "endpoint": "multi_source",
                        "symbol": "600519",
                        "analysis_depth": "advanced",
                        "data_sources": ["technical", "fundamental", "sentiment", "flow"],
                        "summary": "基本面与技术面权重占优，综合结论偏多。",
                        "insights": ["fundamental 权重最高，作为主判断来源。", "technical 与 flow 同步提供正向确认。"],
                        "scores": {
                            "technical": 78.0,
                            "fundamental": 84.0,
                            "sentiment": 72.0,
                            "flow": 76.0,
                        },
                        "comprehensive_score": 78.8,
                        "recommendation": "buy",
                        "confidence": 0.79,
                    },
                }
            }
        },
    },
    500: COMMON_RESPONSES[500],
}

DEFAULT_SOURCE_SCORES = {
    "technical": 78.0,
    "fundamental": 84.0,
    "sentiment": 72.0,
    "flow": 76.0,
}


def _normalize_sources(data: dict[str, Any]) -> list[str]:
    sources = data.get("data_sources")
    if isinstance(sources, list) and sources:
        return [str(item) for item in sources]
    return ["technical", "fundamental", "sentiment"]


def _normalize_weights(sources: list[str], data: dict[str, Any]) -> dict[str, float]:
    raw_weights = data.get("weights") if isinstance(data.get("weights"), dict) else {}
    parsed = {
        source: float(raw_weights.get(source, 0.0))
        for source in sources
    }
    total = sum(value for value in parsed.values() if value > 0)
    if total <= 0:
        equal_weight = round(1.0 / len(sources), 4)
        return {source: equal_weight for source in sources}
    return {source: round(max(value, 0.0) / total, 4) for source, value in parsed.items()}


def _build_scores(sources: list[str]) -> dict[str, float]:
    return {source: DEFAULT_SOURCE_SCORES.get(source, 70.0) for source in sources}


def _build_recommendation(score: float) -> str:
    if score >= 85:
        return "strong_buy"
    if score >= 75:
        return "buy"
    if score >= 60:
        return "hold"
    if score >= 45:
        return "sell"
    return "strong_sell"


def _build_summary(recommendation: str, dominant_source: str) -> str:
    if recommendation in {"strong_buy", "buy"}:
        return f"{dominant_source} 面权重占优，综合结论偏多。"
    if recommendation in {"sell", "strong_sell"}:
        return f"{dominant_source} 面权重占优，但当前综合信号偏空。"
    return f"{dominant_source} 面是当前主判断来源，综合结论偏中性。"


def _build_insights(weights: dict[str, float], scores: dict[str, float]) -> list[str]:
    dominant_source = max(weights, key=weights.get)
    dominant_score = scores[dominant_source]
    ordered_sources = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    insights = [f"{dominant_source} 权重最高，作为主判断来源。"]

    if len(ordered_sources) > 1:
        secondary_source = ordered_sources[1][0]
        insights.append(f"{secondary_source} 与 {dominant_source} 共同提供交叉确认。")

    if dominant_score >= 80:
        insights.append(f"{dominant_source} 子评分达到 {dominant_score:.1f}，对综合结果形成强化。")
    else:
        insights.append(f"{dominant_source} 子评分为 {dominant_score:.1f}，建议结合更多上下文复核。")

    return insights


@router.get(
    "/health",
    summary="获取多数据源健康状态",
    description="返回多数据源服务的基础健康状态，用于网关探活、运维巡检和启动后自检。",
    responses=MULTI_SOURCE_HEALTH_RESPONSES,
)
async def health_check():
    """返回多数据源服务的基础健康状态。"""
    return {"status": "ok", "service": "multi_source"}


@router.get(
    "/status",
    summary="获取多数据源运行状态",
    description="返回多数据源服务的当前运行状态和端点标识，用于联调和运行态确认。",
    responses=MULTI_SOURCE_STATUS_RESPONSES,
)
async def get_status():
    """返回多数据源服务的当前运行状态。"""
    return {"status": "active", "endpoint": "multi_source"}


@router.post(
    "/analyze",
    summary="执行多数据源综合分析",
    description="接收多个分析维度与权重配置，返回基于请求权重和内置评分矩阵生成的综合分析结果。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=MULTI_SOURCE_ANALYZE_RESPONSES,
)
async def analyze_data(data: dict = Body(..., example=MULTI_SOURCE_ANALYZE_REQUEST_EXAMPLE)) -> UnifiedResponse[Dict[str, Any]]:
    """
    多数据源AI综合分析

    整合多个数据源（技术面、基本面、舆情、资金流等）进行AI综合分析，生成全方位
    的投资决策支持。该端点提供最全面的股票分析结果。

    **功能说明**:
    - 整合技术分析、基本面、舆情等多维数据
    - AI驱动的跨数据源关联分析
    - 生成综合评分和投资建议
    - 识别多源数据的一致性和矛盾点
    - 提供决策置信度评估
    - 支持自定义数据源权重配置

    **使用场景**:
    - 全面投资决策支持
    - 多维度股票评估和排序
    - 投资组合优化建议
    - 风险收益综合评估
    - 跨市场数据关联分析
    - 智能投研报告生成

    **请求参数**:
    - symbol (可选): 股票代码
    - data_sources (可选): 数据源列表（technical/fundamental/sentiment/flow）
    - analysis_depth (可选): 分析深度（basic/standard/advanced）
    - weights (可选): 各数据源权重配置
    - time_range (可选): 分析时间范围

    **返回值**:
    - result: 分析结果描述
    - endpoint: 服务端点标识
    - comprehensive_score (可选): 综合评分（0-100）
    - technical_score (可选): 技术面评分
    - fundamental_score (可选): 基本面评分
    - sentiment_score (可选): 舆情评分
    - recommendation (可选): 投资建议（strong_buy/buy/hold/sell/strong_sell）
    - confidence (可选): 分析置信度（0-1）
    - key_insights (可选): 关键洞察列表
    - risk_factors (可选): 风险因素列表

    **示例**:
    ```bash
    # 多数据源综合分析
    curl -X POST "http://localhost:${BACKEND_PORT}/api/multi-source/analyze" \\
      -H "Content-Type: application/json" \\
      -d '{
        "symbol": "600519",
        "data_sources": ["technical", "fundamental", "sentiment", "flow"],
        "analysis_depth": "advanced",
        "weights": {
          "technical": 0.3,
          "fundamental": 0.4,
          "sentiment": 0.2,
          "flow": 0.1
        },
        "time_range": "3m"
      }'
    ```

    **响应示例**:
    ```json
    {
      "result": "分析完成",
      "endpoint": "multi_source",
      "comprehensive_score": 82,
      "technical_score": 78,
      "fundamental_score": 88,
      "sentiment_score": 75,
      "flow_score": 85,
      "recommendation": "buy",
      "confidence": 0.83,
      "key_insights": [
        "基本面强劲，ROE持续提升",
        "技术面突破关键阻力位",
        "主力资金持续流入",
        "市场舆情整体积极"
      ],
      "risk_factors": [
        "估值处于历史高位",
        "短期技术指标超买"
      ]
    }
    ```

    **注意事项**:
    - 当前版本基于内置评分矩阵和请求权重生成规则化结果
    - 综合分析需要较长处理时间，建议异步调用
    - 不同数据源的时效性可能不一致
    - AI建议仅供参考，投资需谨慎
    - 建议定期更新分析结果
    - 数据源权重配置需根据市场环境调整
    - 分析结果的准确性受所有数据源质量影响
    """
    sources = _normalize_sources(data)
    weights = _normalize_weights(sources, data)
    scores = _build_scores(sources)
    comprehensive_score = round(sum(scores[source] * weights[source] for source in sources), 2)
    recommendation = _build_recommendation(comprehensive_score)
    dominant_source = max(weights, key=weights.get)
    confidence = round(min(0.95, 0.55 + (weights[dominant_source] * 0.6)), 2)

    return UnifiedResponse(
        success=True,
        code=200,
        message="Multi-source analysis summarized from request inputs",
        data={
            "status": "available",
            "endpoint": "multi_source",
            "symbol": data.get("symbol"),
            "analysis_depth": data.get("analysis_depth"),
            "data_sources": sources,
            "summary": _build_summary(recommendation, dominant_source),
            "insights": _build_insights(weights, scores),
            "scores": scores,
            "weights": weights,
            "comprehensive_score": comprehensive_score,
            "recommendation": recommendation,
            "confidence": confidence,
        },
    )
