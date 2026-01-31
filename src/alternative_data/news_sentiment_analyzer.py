"""
# pylint: disable=no-member  # TODO: 修复异常类的 to_dict 方法
新闻数据采集和情感分析
News Data Collection and Sentiment Analysis

从多个新闻源采集金融新闻，进行情感分析并生成情感指标。
Collect financial news from multiple sources, perform sentiment analysis, and generate sentiment indicators.
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import feedparser
from bs4 import BeautifulSoup

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available, using fallback sentiment analysis")

from src.core.database import DatabaseConnectionManager

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """新闻文章数据结构"""

    title: str
    content: str
    summary: str = ""
    url: str = ""
    source: str = ""
    published_at: datetime = field(default_factory=datetime.now)
    symbols: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    confidence: float = 0.0
    relevance_score: float = 0.0
    article_id: str = ""


def __post_init__(self):
    if not self.article_id:
        # 生成文章唯一ID
        content_hash = hashlib.md5(f"{self.title}{self.url}{self.published_at}".encode()).hexdigest()[:16]
        self.article_id = f"{self.source}_{content_hash}"


@dataclass
class SentimentResult:
    """情感分析结果"""

    text: str
    sentiment_score: float  # -1 到 1 之间的分数
    sentiment_label: str  # positive, negative, neutral
    confidence: float  # 置信度 0-1
    aspects: Dict[str, float] = field(default_factory=dict)  # 方面级情感


class NewsCollector:
    """新闻收集器"""

    def __init__(self, db_manager: DatabaseConnectionManager):
        self.db_manager = db_manager
        self.sources = {
            "sina_finance": {
                "url": "http://rss.sina.com.cn/news/china/focus15.xml",
                "name": "新浪财经",
                "type": "rss",
            },
            "eastmoney": {
                "url": "http://finance.eastmoney.com/rss/yaowen.xml",
                "name": "东方财富",
                "type": "rss",
            },
            "yicai": {
                "url": "https://www.yicai.com/rss/feed.xml",
                "name": "第一财经",
                "type": "rss",
            },
            "cnstock": {
                "url": "http://www.cnstock.com/rss/gnxw.xml",
                "name": "中国证券网",
                "type": "rss",
            },
        }

        # 股票关键词映射
        self.stock_keywords = {
            "600000": ["浦发银行", "浦发", "PFYH"],
            "000002": ["万科A", "万科", "WKA"],
            "600036": ["招商银行", "招行", "ZSYH"],
            "000858": ["五粮液", "五粮", "WLY"],
            "600519": ["贵州茅台", "茅台", "GZM"],
            "000568": ["泸州老窖", "老窖", "LZLJ"],
            "600276": ["恒瑞医药", "恒瑞", "HRYY"],
            "000001": ["上证指数", "上证", "沪指"],
            "399001": ["深证成指", "深成指", "深圳"],
            "399006": ["创业板指", "创业板", "GEM"],
        }


async def collect_news(self, hours_back: int = 24) -> List[NewsArticle]:
    """采集新闻数据"""
    logger.info("开始采集过去%(hours_back)s小时的新闻数据...")

    all_articles = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    async with aiohttp.ClientSession() as session:
        for source_key, source_config in self.sources.items():
            try:
                articles = await self._collect_from_source(session, source_key, source_config, cutoff_time)
                all_articles.extend(articles)
                logger.info("从 {source_config['name']} 采集到 {len(articles)} 篇文章")

            except Exception as e:
                logger.error("从 {source_config['name']} 采集失败: %(e)s")
                continue

    # 去重和过滤
    unique_articles = self._deduplicate_articles(all_articles)

    logger.info("新闻采集完成，共 {len(unique_articles)} 篇有效文章")
    return unique_articles


async def _collect_from_source(
    self,
    session: aiohttp.ClientSession,
    source_key: str,
    source_config: Dict[str, Any],
    cutoff_time: datetime,
) -> List[NewsArticle]:
    """从单个源采集新闻"""
    articles = []

    if source_config["type"] == "rss":
        articles = await self._collect_rss_feed(session, source_config, cutoff_time)

    # 设置来源
    for article in articles:
        article.source = source_config["name"]

    return articles


async def _collect_rss_feed(
    self,
    session: aiohttp.ClientSession,
    source_config: Dict[str, Any],
    cutoff_time: datetime,
) -> List[NewsArticle]:
    """采集RSS新闻源"""
    articles = []

    try:
        async with session.get(source_config["url"], timeout=30) as response:
            if response.status != 200:
                logger.warning("RSS源 {source_config['url']} 返回状态码 {response.status")
                return articles

            content = await response.text()
            feed = feedparser.parse(content)

            for entry in feed.entries:
                try:
                    # 解析发布时间
                    published_time = self._parse_published_time(entry)
                    if published_time and published_time < cutoff_time:
                        continue

                    # 提取标题和内容
                    title = entry.title if hasattr(entry, "title") else ""
                    content = entry.description if hasattr(entry, "description") else ""
                    url = entry.link if hasattr(entry, "link") else ""

                    if not title or not content:
                        continue

                    # 创建文章对象
                    article = NewsArticle(
                        title=title,
                        content=self._clean_html(content),
                        url=url,
                        published_at=published_time or datetime.now(),
                    )

                    # 识别相关股票
                    article.symbols = self._identify_related_symbols(title + " " + content)

                    articles.append(article)

                except Exception as e:
                    logger.warning("解析RSS条目失败: %(e)s")
                    continue

    except Exception as e:
        logger.error("采集RSS源失败: %(e)s")

    return articles


def _parse_published_time(self, entry) -> Optional[datetime]:
    """解析发布时间"""
    time_fields = ["published_parsed", "updated_parsed", "created_parsed"]

    for field in time_fields:
        if hasattr(entry, field) and getattr(entry, field):
            try:
                time_tuple = getattr(entry, field)
                if len(time_tuple) >= 6:
                    return datetime(*time_tuple[:6])
            except Exception:
                continue

    # 尝试解析字符串时间
    time_strings = []
    if hasattr(entry, "published"):
        time_strings.append(entry.published)
    if hasattr(entry, "updated"):
        time_strings.append(entry.updated)

    for time_str in time_strings:
        try:
            # 这里可以添加更复杂的日期解析逻辑
            # 暂时返回当前时间
            return datetime.now()
        except Exception:
            continue

    return None


def _clean_html(self, html_content: str) -> str:
    """清理HTML内容"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        # 清理多余空格
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    except Exception:
        return html_content


def _identify_related_symbols(self, text: str) -> List[str]:
    """识别文本中提到的相关股票"""
    related_symbols = []

    for symbol, keywords in self.stock_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                if symbol not in related_symbols:
                    related_symbols.append(symbol)
                break  # 找到一个关键词就够了

    return related_symbols


def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
    """去重文章"""
    seen_ids = set()
    unique_articles = []

    for article in articles:
        if article.article_id not in seen_ids:
            seen_ids.add(article.article_id)
            unique_articles.append(article)

    return unique_articles


class SentimentAnalyzer:
    """情感分析器"""


def __init__(self):
    self.model = None
    self.tokenizer = None
    self.fallback_analyzer = self._create_fallback_analyzer()

    if TRANSFORMERS_AVAILABLE:
        try:
            # 加载中文情感分析模型
            model_name = "IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            logger.info("情感分析模型加载成功")
        except Exception as e:
            logger.warning("情感分析模型加载失败: %(e)s，使用fallback分析器")


def _create_fallback_analyzer(self):
    """创建fallback情感分析器"""
    positive_words = [
        "上涨",
        "增长",
        "盈利",
        "利好",
        "乐观",
        "积极",
        "突破",
        "创新",
        "合作",
        "投资",
        "并购",
        "重组",
        "回购",
        "分红",
        "业绩",
        "增长",
        "振兴",
        "复苏",
        "繁荣",
        "发展",
        "进步",
        "提升",
        "改善",
        "增强",
    ]

    negative_words = [
        "下跌",
        "亏损",
        "利空",
        "悲观",
        "消极",
        "暴跌",
        "崩盘",
        "危机",
        "债务",
        "违约",
        "退市",
        "处罚",
        "调查",
        "丑闻",
        "事故",
        "损失",
        "下滑",
        "下降",
        "减少",
        "衰退",
        "萧条",
        "困难",
        "挑战",
        "风险",
    ]

    return {
        "positive_words": set(positive_words),
        "negative_words": set(negative_words),
    }


async def analyze_sentiment(self, text: str) -> SentimentResult:
    """分析文本情感"""
    try:
        if self.model and self.tokenizer:
            return await self._analyze_with_model(text)
        else:
            return self._analyze_with_fallback(text)

    except Exception as e:
        logger.error("情感分析失败: %(e)s")
        return SentimentResult(text=text, sentiment_score=0.0, sentiment_label="neutral", confidence=0.5)


async def _analyze_with_model(self, text: str) -> SentimentResult:
    """使用深度学习模型进行情感分析"""
    try:
        # 分句处理长文本
        sentences = self._split_into_sentences(text)
        if not sentences:
            return SentimentResult(
                text=text,
                sentiment_score=0.0,
                sentiment_label="neutral",
                confidence=0.5,
            )

        sentence_scores = []

        for sentence in sentences[:5]:  # 限制处理前5句
            inputs = self.tokenizer(
                sentence,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=1)

                # 假设模型输出格式：[负面概率, 中性概率, 正面概率]
                negative_prob = probabilities[0][0].item()
                neutral_prob = probabilities[0][1].item()
                positive_prob = probabilities[0][2].item()

                # 计算情感分数 (-1 到 1)
                sentiment_score = positive_prob - negative_prob

                sentence_scores.append(
                    {
                        "score": sentiment_score,
                        "confidence": max(positive_prob, negative_prob, neutral_prob),
                    }
                )

        # 平均所有句子的情感
        if sentence_scores:
            avg_score = sum(s["score"] for s in sentence_scores) / len(sentence_scores)
            avg_confidence = sum(s["confidence"] for s in sentence_scores) / len(sentence_scores)

            # 确定情感标签
            if avg_score > 0.1:
                label = "positive"
            elif avg_score < -0.1:
                label = "negative"
            else:
                label = "neutral"

            return SentimentResult(
                text=text,
                sentiment_score=avg_score,
                sentiment_label=label,
                confidence=avg_confidence,
            )
        else:
            return SentimentResult(
                text=text,
                sentiment_score=0.0,
                sentiment_label="neutral",
                confidence=0.5,
            )

    except Exception as e:
        logger.error("模型情感分析失败: %(e)s")
        return self._analyze_with_fallback(text)


def _analyze_with_fallback(self, text: str) -> SentimentResult:
    """使用关键词匹配进行情感分析"""
    try:
        text_lower = text.lower()

        positive_count = sum(1 for word in self.fallback_analyzer["positive_words"] if word in text_lower)
        negative_count = sum(1 for word in self.fallback_analyzer["negative_words"] if word in text_lower)

        total_words = len(text.split())
        if total_words == 0:
            return SentimentResult(
                text=text,
                sentiment_score=0.0,
                sentiment_label="neutral",
                confidence=0.5,
            )

        # 计算情感密度
        positive_density = positive_count / total_words
        negative_density = negative_count / total_words

        # 计算情感分数
        sentiment_score = (positive_density - negative_density) * 10  # 放大差异
        sentiment_score = max(-1.0, min(1.0, sentiment_score))  # 限制范围

        # 确定情感标签
        if sentiment_score > 0.05:
            label = "positive"
        elif sentiment_score < -0.05:
            label = "negative"
        else:
            label = "neutral"

        # 计算置信度
        total_emotional_words = positive_count + negative_count
        confidence = min(0.9, total_emotional_words / max(1, total_words * 0.1))  # 基于情感词密度

        return SentimentResult(
            text=text,
            sentiment_score=sentiment_score,
            sentiment_label=label,
            confidence=confidence,
        )

    except Exception as e:
        logger.error("Fallback情感分析失败: %(e)s")
        return SentimentResult(text=text, sentiment_score=0.0, sentiment_label="neutral", confidence=0.5)


def _split_into_sentences(self, text: str) -> List[str]:
    """将文本分割为句子"""
    # 简单的句子分割（可以改进）
    sentences = re.split(r"[。！？.!?]+", text)
    return [s.strip() for s in sentences if s.strip()]


class NewsSentimentService:
    """新闻情感分析服务"""

    def __init__(self, db_manager: DatabaseConnectionManager):
        self.db_manager = db_manager
        self.collector = NewsCollector(db_manager)
        self.analyzer = SentimentAnalyzer()


async def collect_and_analyze_news(self, hours_back: int = 24) -> List[NewsArticle]:
    """采集并分析新闻"""
    logger.info("开始新闻采集和情感分析流程...")

    # 1. 采集新闻
    articles = await self.collector.collect_news(hours_back)

    # 2. 情感分析
    analyzed_articles = []
    for article in articles:
        try:
            # 分析标题情感
            title_sentiment = await self.analyzer.analyze_sentiment(article.title)

            # 分析内容情感
            content_sentiment = await self.analyzer.analyze_sentiment(article.content)

            # 综合情感分析结果
            combined_score = title_sentiment.sentiment_score * 0.6 + content_sentiment.sentiment_score * 0.4
            combined_confidence = (title_sentiment.confidence + content_sentiment.confidence) / 2

            # 确定最终情感标签
            if combined_score > 0.05:
                final_label = "positive"
            elif combined_score < -0.05:
                final_label = "negative"
            else:
                final_label = "neutral"

            # 更新文章
            article.sentiment_score = combined_score
            article.sentiment_label = final_label
            article.confidence = combined_confidence

            # 计算相关性得分（基于情感强度和股票提及次数）
            article.relevance_score = abs(combined_score) * len(article.symbols) * combined_confidence

            analyzed_articles.append(article)

        except Exception as e:
            logger.error("分析文章失败 '{article.title}': %(e)s")
            analyzed_articles.append(article)  # 仍然添加文章，即使分析失败

    # 3. 保存到数据库
    await self._save_articles_to_db(analyzed_articles)

    logger.info("新闻采集和分析完成，共处理 {len(analyzed_articles)} 篇文章")
    return analyzed_articles


async def _save_articles_to_db(self, articles: List[NewsArticle]):
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

    except Exception as e:
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

        # 计算综合情感指标
        scores = [row["sentiment_score"] for row in rows]
        confidences = [row["confidence"] for row in rows]
        relevance_scores = [row["relevance_score"] for row in rows]

        # 加权平均（基于相关性和置信度）
        weights = [conf * rel for conf, rel in zip(confidences, relevance_scores)]
        if sum(weights) > 0:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            weighted_score = sum(scores) / len(scores) if scores else 0.0

        # 确定趋势
        if weighted_score > 0.1:
            trend = "positive"
        elif weighted_score < -0.1:
            trend = "negative"
        else:
            trend = "neutral"

        # 计算平均置信度
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

        # 计算市场整体情感
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
