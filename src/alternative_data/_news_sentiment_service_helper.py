"""Service helpers for `news_sentiment_analyzer.py`."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from src.alternative_data.news_sentiment_analyzer import NewsArticle

logger = logging.getLogger(__name__)


async def collect_and_analyze_news(self, hours_back: int = 24) -> List["NewsArticle"]:
    """采集并分析新闻"""
    logger.info("开始新闻采集和情感分析流程...")

    articles = await self.collector.collect_news(hours_back)
    analyzed_articles = []
    for article in articles:
        try:
            title_sentiment = await self.analyzer.analyze_sentiment(article.title)
            content_sentiment = await self.analyzer.analyze_sentiment(article.content)

            combined_score = title_sentiment.sentiment_score * 0.6 + content_sentiment.sentiment_score * 0.4
            combined_confidence = (title_sentiment.confidence + content_sentiment.confidence) / 2

            if combined_score > 0.05:
                final_label = "positive"
            elif combined_score < -0.05:
                final_label = "negative"
            else:
                final_label = "neutral"

            article.sentiment_score = combined_score
            article.sentiment_label = final_label
            article.confidence = combined_confidence
            article.relevance_score = abs(combined_score) * len(article.symbols) * combined_confidence
            analyzed_articles.append(article)
        except Exception:
            logger.error("分析文章失败 '{article.title}': %(e)s")
            analyzed_articles.append(article)

    await self._save_articles_to_db(analyzed_articles)
    logger.info("新闻采集和分析完成，共处理 {len(analyzed_articles)} 篇文章")
    return analyzed_articles


async def _save_articles_to_db(self, articles: List["NewsArticle"]):
    """保存文章到数据库"""
    try:
        async with self.db_manager.get_connection() as conn:
            for article in articles:
                await conn.execute(
                    """
                        INSERT INTO news_articles (
                            article_id, title, content, summary, url, source,
                            published_at, symbols, sentiment_score, sentiment_label,
                            confidence, relevance_score, created_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
                        ON CONFLICT (article_id) DO UPDATE SET
                            sentiment_score = EXCLUDED.sentiment_score,
                            sentiment_label = EXCLUDED.sentiment_label,
                            confidence = EXCLUDED.confidence,
                            relevance_score = EXCLUDED.relevance_score
                    """,
                    article.article_id,
                    article.title,
                    article.content,
                    article.summary,
                    article.url,
                    article.source,
                    article.published_at,
                    json.dumps(article.symbols),
                    article.sentiment_score,
                    article.sentiment_label,
                    article.confidence,
                    article.relevance_score,
                )

        logger.info("成功保存 {len(articles)} 篇新闻文章到数据库")
    except Exception:
        logger.error("保存新闻文章到数据库失败: %(e)s")


async def get_sentiment_indicators(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
    """获取股票的情感指标"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)

        async with self.db_manager.get_connection() as conn:
            rows = await conn.fetch(
                """
                    SELECT
                        sentiment_score,
                        confidence,
                        relevance_score,
                        published_at
                    FROM news_articles
                    WHERE $1 = ANY(symbols)
                    AND published_at >= $2
                    ORDER BY published_at DESC
                """,
                symbol,
                cutoff_time,
            )

        if not rows:
            return {
                "symbol": symbol,
                "sentiment_score": 0.0,
                "sentiment_trend": "neutral",
                "confidence": 0.0,
                "article_count": 0,
                "time_range_hours": hours,
            }

        scores = [row["sentiment_score"] for row in rows]
        confidences = [row["confidence"] for row in rows]
        relevance_scores = [row["relevance_score"] for row in rows]

        weights = [conf * rel for conf, rel in zip(confidences, relevance_scores)]
        if sum(weights) > 0:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            weighted_score = sum(scores) / len(scores) if scores else 0.0

        if weighted_score > 0.1:
            trend = "positive"
        elif weighted_score < -0.1:
            trend = "negative"
        else:
            trend = "neutral"

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "symbol": symbol,
            "sentiment_score": weighted_score,
            "sentiment_trend": trend,
            "confidence": avg_confidence,
            "article_count": len(rows),
            "time_range_hours": hours,
            "latest_update": max(row["published_at"] for row in rows).isoformat() if rows else None,
        }
    except Exception as e:
        logger.error("获取情感指标失败: %(e)s")
        return {
            "symbol": symbol,
            "error": str(e),
            "sentiment_score": 0.0,
            "sentiment_trend": "neutral",
            "confidence": 0.0,
            "article_count": 0,
            "time_range_hours": hours,
        }


async def get_market_sentiment_overview(self, hours: int = 24) -> Dict[str, Any]:
    """获取市场整体情感概览"""
    try:
        key_symbols = ["000001", "399001", "399006", "600519", "000858", "600036"]

        sentiment_data = {}
        for symbol in key_symbols:
            sentiment_data[symbol] = await self.get_sentiment_indicators(symbol, hours)

        valid_scores = [data["sentiment_score"] for data in sentiment_data.values() if "error" not in data]
        if valid_scores:
            market_sentiment = sum(valid_scores) / len(valid_scores)
            if market_sentiment > 0.05:
                market_trend = "bullish"
            elif market_sentiment < -0.05:
                market_trend = "bearish"
            else:
                market_trend = "neutral"
        else:
            market_sentiment = 0.0
            market_trend = "neutral"

        return {
            "market_sentiment_score": market_sentiment,
            "market_trend": market_trend,
            "analyzed_symbols": len([s for s in sentiment_data.values() if "error" not in s]),
            "total_symbols": len(key_symbols),
            "time_range_hours": hours,
            "symbol_sentiments": sentiment_data,
            "generated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error("获取市场情感概览失败: %(e)s")
        return {
            "error": str(e),
            "market_sentiment_score": 0.0,
            "market_trend": "neutral",
            "analyzed_symbols": 0,
            "total_symbols": 0,
            "time_range_hours": hours,
        }
