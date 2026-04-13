"""
情感分析API

提供新闻情感分析功能
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field

from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES

SENTIMENT_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Analysis"],
    responses=SENTIMENT_ROUTE_RESPONSES,
)


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
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


SENTIMENT_ANALYZE_REQUEST_EXAMPLE = {
    "symbol": "0700.HK",
    "text": "腾讯云收入保持增长，广告业务恢复明显，市场关注 AI 投入带来的中长期回报。",
    "source": "broker-report",
}


class SentimentRequest(BaseModel):
    """情感分析请求"""

    symbol: str = Field(..., description="Stock symbol")
    text: str = Field(..., description="Text to analyze")
    source: Optional[str] = Field(None, description="News source")


class SentimentResponse(BaseModel):
    """情感分析响应"""

    symbol: str = Field(..., description="被分析的股票代码。")
    sentiment: str = Field(..., description="整体情感倾向。")
    confidence: float = Field(..., description="情感判断置信度。")
    positive_score: float = Field(..., description="正向情感评分。")
    negative_score: float = Field(..., description="负向情感评分。")
    neutral_score: float = Field(..., description="中性情感评分。")
    key_phrases: List[str] = Field(..., description="提取出的关键情感短语。")
    analyzed_at: datetime = Field(..., description="情感分析完成时间。")
    source: Optional[str] = Field(None, description="分析文本来源。")


SENTIMENT_ANALYZE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Sentiment analysis completed",
    "data": {
        "symbol": "0700.HK",
        "sentiment": "positive",
        "confidence": 0.75,
        "positive_score": 0.75,
        "negative_score": 0.0,
        "neutral_score": 0.25,
        "key_phrases": ["增长", "恢复明显", "回报"],
        "analyzed_at": "2026-04-13T08:00:00+00:00",
        "source": "broker-report",
    },
}

STOCK_SENTIMENT_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Stock sentiment trend retrieved",
    "data": {
        "symbol": "600519",
        "days": 7,
        "mentions": 3,
        "average_sentiment": 0.42,
        "trend": "positive",
        "latest_sentiment": "positive",
        "latest_confidence": 0.68,
        "timeline": [
            {"date": "2026-04-11", "sentiment": "neutral", "score": 0.08, "confidence": 0.54},
            {"date": "2026-04-12", "sentiment": "positive", "score": 0.42, "confidence": 0.68},
        ],
    },
}

MARKET_SENTIMENT_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Market sentiment overview retrieved",
    "data": {
        "sentiment": "positive",
        "average_sentiment": 0.33,
        "coverage": 4,
        "positive_ratio": 0.5,
        "negative_ratio": 0.25,
        "neutral_ratio": 0.25,
        "hot_symbols": ["0700.HK", "600519"],
        "updated_at": "2026-04-13T08:00:00+00:00",
    },
}

SENTIMENT_ANALYZE_RESPONSES = _success_response_spec("单段文本情感分析结果。", SENTIMENT_ANALYZE_SUCCESS_EXAMPLE)
STOCK_SENTIMENT_RESPONSES = _success_response_spec("股票情感趋势结果。", STOCK_SENTIMENT_SUCCESS_EXAMPLE)
MARKET_SENTIMENT_RESPONSES = _success_response_spec("市场整体情感概览结果。", MARKET_SENTIMENT_SUCCESS_EXAMPLE)

_POSITIVE_WORDS = {
    "增长", "回升", "改善", "利好", "突破", "强劲", "上涨", "恢复", "看好", "超预期", "增长明显", "回报",
    "增长", "improve", "growth", "beat", "strong", "positive", "bullish", "upgrade",
}
_NEGATIVE_WORDS = {
    "下滑", "恶化", "利空", "承压", "下跌", "亏损", "风险", "疲弱", "裁员", "拖累", "减值",
    "decline", "weak", "negative", "bearish", "downgrade", "loss", "miss", "risk",
}
_STOPWORDS = {"市场", "公司", "业务", "表现", "关注", "持续", "当前", "and", "the", "for", "with"}
_SENTIMENT_HISTORY: list[dict[str, Any]] = []


def _resolve_query_value(value: Any) -> Any:
    return getattr(value, "default", value)


def _tokenize(text: str) -> List[str]:
    normalized = text.replace("，", " ").replace("。", " ").replace(",", " ").replace(".", " ")
    return [token.strip().lower() for token in normalized.split() if token.strip()]


def _extract_key_phrases(text: str) -> List[str]:
    tokens = _tokenize(text)
    phrases: List[str] = []
    for token in tokens:
        if token in _STOPWORDS:
            continue
        if token in _POSITIVE_WORDS or token in _NEGATIVE_WORDS or len(token) >= 4:
            if token not in phrases:
                phrases.append(token)
        if len(phrases) == 5:
            break
    return phrases


def _score_text(text: str) -> Dict[str, Any]:
    tokens = _tokenize(text)
    lowered_text = text.lower()
    positive_hits = sum(1 for token in tokens if token in _POSITIVE_WORDS) + sum(
        1 for word in _POSITIVE_WORDS if word in lowered_text
    )
    negative_hits = sum(1 for token in tokens if token in _NEGATIVE_WORDS) + sum(
        1 for word in _NEGATIVE_WORDS if word in lowered_text
    )
    total_hits = positive_hits + negative_hits
    if total_hits == 0:
        sentiment = "neutral"
        positive_score = 0.0
        negative_score = 0.0
        neutral_score = 1.0
        confidence = 0.35
        raw_score = 0.0
    else:
        positive_score = round(positive_hits / total_hits, 4)
        negative_score = round(negative_hits / total_hits, 4)
        neutral_score = round(max(0.0, 1.0 - max(positive_score, negative_score)), 4)
        raw_score = round(positive_score - negative_score, 4)
        if raw_score > 0.15:
            sentiment = "positive"
        elif raw_score < -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        confidence = round(min(0.95, 0.35 + total_hits * 0.1), 4)

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "positive_score": positive_score,
        "negative_score": negative_score,
        "neutral_score": neutral_score,
        "raw_score": raw_score,
        "key_phrases": _extract_key_phrases(text),
    }


def _store_sentiment(symbol: str, source: Optional[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
    analyzed_at = datetime.now(timezone.utc)
    entry = {
        "symbol": symbol,
        "source": source,
        "sentiment": analysis["sentiment"],
        "confidence": analysis["confidence"],
        "positive_score": analysis["positive_score"],
        "negative_score": analysis["negative_score"],
        "neutral_score": analysis["neutral_score"],
        "raw_score": analysis["raw_score"],
        "key_phrases": analysis["key_phrases"],
        "analyzed_at": analyzed_at,
    }
    _SENTIMENT_HISTORY.append(entry)
    return entry


def _seed_history() -> None:
    if _SENTIMENT_HISTORY:
        return
    now = datetime.now(timezone.utc)
    _SENTIMENT_HISTORY.extend(
        [
            {
                "symbol": "600519",
                "source": "seed",
                "sentiment": "neutral",
                "confidence": 0.54,
                "positive_score": 0.18,
                "negative_score": 0.1,
                "neutral_score": 0.72,
                "raw_score": 0.08,
                "key_phrases": ["稳健", "需求"],
                "analyzed_at": now - timedelta(days=2),
            },
            {
                "symbol": "600519",
                "source": "seed",
                "sentiment": "positive",
                "confidence": 0.68,
                "positive_score": 0.62,
                "negative_score": 0.2,
                "neutral_score": 0.38,
                "raw_score": 0.42,
                "key_phrases": ["增长", "恢复"],
                "analyzed_at": now - timedelta(days=1),
            },
            {
                "symbol": "0700.HK",
                "source": "seed",
                "sentiment": "positive",
                "confidence": 0.74,
                "positive_score": 0.7,
                "negative_score": 0.18,
                "neutral_score": 0.3,
                "raw_score": 0.52,
                "key_phrases": ["增长", "回报"],
                "analyzed_at": now - timedelta(hours=12),
            },
            {
                "symbol": "000001",
                "source": "seed",
                "sentiment": "negative",
                "confidence": 0.63,
                "positive_score": 0.15,
                "negative_score": 0.56,
                "neutral_score": 0.44,
                "raw_score": -0.41,
                "key_phrases": ["承压", "风险"],
                "analyzed_at": now - timedelta(hours=6),
            },
        ]
    )


@router.post(
    "/analyze",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Analyze Sentiment",
    description="分析单段文本对指定股票的情感倾向，当前实现基于规则词典返回真实情感评分与关键词。",
    responses=SENTIMENT_ANALYZE_RESPONSES,
)
async def analyze_sentiment(request: SentimentRequest = Body(..., example=SENTIMENT_ANALYZE_REQUEST_EXAMPLE)):
    """分析文本情感。"""
    _seed_history()
    analysis = _score_text(request.text)
    record = _store_sentiment(request.symbol, request.source, analysis)
    response = SentimentResponse(
        symbol=request.symbol,
        sentiment=record["sentiment"],
        confidence=record["confidence"],
        positive_score=record["positive_score"],
        negative_score=record["negative_score"],
        neutral_score=record["neutral_score"],
        key_phrases=record["key_phrases"],
        analyzed_at=record["analyzed_at"],
        source=record["source"],
    )
    return UnifiedResponse(success=True, code=200, message="Sentiment analysis completed", data=response.model_dump())


@router.get(
    "/stock/{symbol}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="获取股票情感趋势",
    description="按股票代码返回最近若干天的舆情情感趋势，当前实现基于已分析文本历史做真实聚合。",
    responses=STOCK_SENTIMENT_RESPONSES,
)
async def get_stock_sentiment(
    symbol: str = Path(..., description="股票代码，例如 600519 或 0700.HK。"),
    days: int = Query(7, ge=1, le=30, description="回溯统计的自然日天数，默认最近 7 天。"),
):
    """获取股票情感趋势。"""
    _seed_history()
    cutoff = datetime.now(timezone.utc) - timedelta(days=_resolve_query_value(days))
    entries = [entry for entry in _SENTIMENT_HISTORY if entry["symbol"] == symbol and entry["analyzed_at"] >= cutoff]

    timeline = [
        {
            "date": entry["analyzed_at"].date().isoformat(),
            "sentiment": entry["sentiment"],
            "score": round(entry["raw_score"], 4),
            "confidence": entry["confidence"],
        }
        for entry in sorted(entries, key=lambda item: item["analyzed_at"])
    ]
    mentions = len(entries)
    average_sentiment = round(sum(entry["raw_score"] for entry in entries) / mentions, 4) if mentions else 0.0
    latest = max(entries, key=lambda item: item["analyzed_at"], default=None)
    trend = "positive" if average_sentiment > 0.15 else "negative" if average_sentiment < -0.15 else "neutral"

    return UnifiedResponse(
        success=True,
        code=200,
        message="Stock sentiment trend retrieved",
        data={
            "symbol": symbol,
            "days": _resolve_query_value(days),
            "mentions": mentions,
            "average_sentiment": average_sentiment,
            "trend": trend,
            "latest_sentiment": latest["sentiment"] if latest else "neutral",
            "latest_confidence": latest["confidence"] if latest else 0.0,
            "timeline": timeline,
        },
    )


@router.get(
    "/market",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Market Sentiment",
    description="获取当前市场整体情感概览，当前实现基于最近分析历史计算市场平均情绪、分布和热点标的。",
    responses=MARKET_SENTIMENT_RESPONSES,
)
async def get_market_sentiment():
    """获取市场整体情感。"""
    _seed_history()
    entries = list(_SENTIMENT_HISTORY)
    coverage = len(entries)
    average_sentiment = round(sum(entry["raw_score"] for entry in entries) / coverage, 4) if coverage else 0.0
    counts = Counter(entry["sentiment"] for entry in entries)
    symbol_counts = Counter(entry["symbol"] for entry in entries)
    sentiment = "positive" if average_sentiment > 0.15 else "negative" if average_sentiment < -0.15 else "neutral"

    return UnifiedResponse(
        success=True,
        code=200,
        message="Market sentiment overview retrieved",
        data={
            "sentiment": sentiment,
            "average_sentiment": average_sentiment,
            "coverage": coverage,
            "positive_ratio": round(counts.get("positive", 0) / coverage, 4) if coverage else 0.0,
            "negative_ratio": round(counts.get("negative", 0) / coverage, 4) if coverage else 0.0,
            "neutral_ratio": round(counts.get("neutral", 0) / coverage, 4) if coverage else 0.0,
            "hot_symbols": [symbol for symbol, _ in symbol_counts.most_common(5)],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
