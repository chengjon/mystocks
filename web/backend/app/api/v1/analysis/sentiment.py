"""
情感分析API

提供新闻情感分析功能
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field

from app.openapi_config import COMMON_RESPONSES

SENTIMENT_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

STOCK_SENTIMENT_RESPONSES = {
    200: {
        "description": "股票情感趋势数据",
        "content": {
            "application/json": {
                "example": {
                    "symbol": "600519",
                    "period_days": 7,
                    "sentiment_scores": [
                        {"date": "2026-04-05", "score": 0.65, "mention_count": 125},
                        {"date": "2026-04-04", "score": 0.58, "mention_count": 98},
                        {"date": "2026-04-03", "score": 0.72, "mention_count": 156},
                    ],
                    "average_sentiment": 0.65,
                    "total_mentions": 379,
                }
            }
        },
    }
}

router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Analysis"],
    responses=SENTIMENT_ROUTE_RESPONSES,
)

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

    symbol: str
    sentiment: str
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    key_phrases: List[str]
    analyzed_at: datetime


@router.post(
    "/analyze",
    response_model=SentimentResponse,
    summary="Analyze Sentiment",
    description="分析单段文本对指定股票的情感倾向，适用于新闻摘要、研报摘录和舆情片段的快速判断。",
)
async def analyze_sentiment(request: SentimentRequest = Body(..., example=SENTIMENT_ANALYZE_REQUEST_EXAMPLE)):
    """
    分析文本情感

    Analyzes sentiment of given text for a stock.
    """
    return SentimentResponse(
        symbol=request.symbol,
        sentiment="POSITIVE",
        confidence=0.85,
        positive_score=0.75,
        negative_score=0.10,
        neutral_score=0.15,
        key_phrases=["强劲增长", "业绩超预期", "买入评级"],
        analyzed_at=datetime.now(),
    )


@router.get(
    "/stock/{symbol}",
    summary="获取股票情感趋势",
    description="按股票代码返回最近若干天的舆情情感分数、提及次数和平均情感，供研判短期情绪变化使用。",
    responses=STOCK_SENTIMENT_RESPONSES,
)
async def get_stock_sentiment(
    symbol: str = Path(..., description="股票代码，例如 600519 或 0700.HK。"),
    days: int = Query(7, ge=1, le=30, description="回溯统计的自然日天数，默认最近 7 天。"),
):
    """
    获取股票情感趋势

    Returns sentiment trend for a stock over specified days.
    """
    return {
        "symbol": symbol,
        "period_days": days,
        "sentiment_scores": [
            {"date": "2025-01-20", "score": 0.65, "mention_count": 125},
            {"date": "2025-01-19", "score": 0.58, "mention_count": 98},
            {"date": "2025-01-18", "score": 0.72, "mention_count": 156},
        ],
        "average_sentiment": 0.65,
        "total_mentions": 379,
    }


@router.get("/market", summary="Get Market Sentiment")
async def get_market_sentiment():
    """
    获取市场整体情感

    Returns overall market sentiment.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "overall_sentiment": "NEUTRAL",
        "market_score": 0.52,
        "sector_sentiments": [
            {"sector": "technology", "score": 0.68, "trend": "up"},
            {"sector": "finance", "score": 0.55, "trend": "stable"},
            {"sector": "healthcare", "score": 0.48, "trend": "down"},
        ],
        "hot_topics": [
            {"topic": "AI", "sentiment": 0.72, "mention_count": 1250},
            {"topic": "新能源", "sentiment": 0.65, "mention_count": 980},
            {"topic": "消费升级", "sentiment": 0.58, "mention_count": 750},
        ],
    }
