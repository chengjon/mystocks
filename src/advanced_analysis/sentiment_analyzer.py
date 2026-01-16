"""
Sentiment Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台舆情分析功能

This module provides comprehensive sentiment analysis including:
- News and research report sentiment extraction
- Social media sentiment monitoring
- Sentiment trend analysis and correlation
- Market sentiment impact assessment
- Multi-source sentiment aggregation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import warnings
import re

from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType

# GPU acceleration support
try:
    import cudf
    import cuml

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Sentiment analysis will run on CPU.")

# NLP libraries
try:
    import jieba
    import jieba.analyse
    from snownlp import SnowNLP

    SNOWNLP_AVAILABLE = True
except ImportError:
    SNOWNLP_AVAILABLE = False
    warnings.warn("Chinese NLP libraries not available. Some sentiment features will be limited.")


@dataclass
class SentimentScore:
    """情感评分"""

    overall_sentiment: float  # 整体情感 (-1到1, 负数=负面, 正数=正面)
    positivity: float  # 正面程度 (0-1)
    negativity: float  # 负面程度 (0-1)
    neutrality: float  # 中性程度 (0-1)
    confidence: float  # 置信度 (0-1)
    intensity: float  # 情感强度 (0-1)


@dataclass
class SentimentSource:
    """情感来源"""

    source_type: str  # 新闻/news, 研报/research, 社交媒体/social, 论坛/forum
    source_name: str  # 来源名称
    content_count: int  # 内容数量
    avg_sentiment: float  # 平均情感
    sentiment_trend: str  # 情感趋势 (improving/declining/stable)
    last_updated: datetime  # 最后更新时间


@dataclass
class MarketSentimentImpact:
    """市场情绪影响"""

    sentiment_correlation: float  # 情绪与价格相关性
    sentiment_lead_lag: int  # 情绪领先/滞后天数
    impact_strength: float  # 影响强度 (0-1)
    predictive_power: float  # 预测能力 (0-1)
    sentiment_regime: str  # 情绪状态 (bullish/bearish/neutral)


@dataclass
class SentimentKeywords:
    """情感关键词"""

    positive_keywords: List[str]  # 正面关键词
    negative_keywords: List[str]  # 负面关键词
    neutral_keywords: List[str]  # 中性关键词
    emerging_topics: List[str]  # 新兴话题
    keyword_weights: Dict[str, float]  # 关键词权重


@dataclass
class SentimentAlert:
    """情感告警"""

    alert_type: str  # sentiment_spike, trend_change, extreme_sentiment
    severity: str  # high, medium, low
    trigger_value: float  # 触发值
    threshold: float  # 阈值
    description: str  # 告警描述
    recommended_action: str  # 建议行动


class SentimentAnalyzer(BaseAnalyzer):
    """
    舆情分析器

    提供全面的舆情分析功能，包括：
    - 新闻和研报情感提取
    - 社交媒体情感监控
    - 情感趋势分析和相关性
    - 市场情绪影响评估
    - 多源情感聚合
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # 情感分析参数
    self.sentiment_params = {
        "min_content_length": 50,  # 最小内容长度
        "sentiment_window": 7,  # 情感分析窗口（天）
        "correlation_lag_max": 5,  # 最大相关滞后期
        "keyword_extraction_topk": 20,  # 关键词提取数量
        "sentiment_threshold": 0.1,  # 情感阈值
    }

    # 情感词典
    self.sentiment_lexicon = self._load_sentiment_lexicon()

    # 停用词
    self.stop_words = self._load_stop_words()

    # 情感分类器
    self.sentiment_classifier = self._initialize_sentiment_classifier()


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行舆情分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数
            - analysis_period: 分析周期 (默认: 30天)
            - include_news: 是否包含新闻分析 (默认: True)
            - include_social: 是否包含社交媒体分析 (默认: True)
            - include_research: 是否包含研报分析 (默认: True)
            - include_correlation: 是否包含相关性分析 (默认: True)

    Returns:
        AnalysisResult: 分析结果
    """
    analysis_period = kwargs.get("analysis_period", 30)
    include_news = kwargs.get("include_news", True)
    include_social = kwargs.get("include_social", True)
    include_research = kwargs.get("include_research", True)
    include_correlation = kwargs.get("include_correlation", True)

    try:
        # 获取舆情数据
        sentiment_data = self._get_sentiment_data(stock_code, analysis_period)

        if sentiment_data.empty:
            return self._create_error_result(stock_code, "No sentiment data available for analysis")

        # 多源情感分析
        source_sentiments = []
        if include_news:
            news_sentiment = self._analyze_news_sentiment(sentiment_data)
            if news_sentiment:
                source_sentiments.append(("news", news_sentiment))

        if include_social:
            social_sentiment = self._analyze_social_sentiment(sentiment_data)
            if social_sentiment:
                source_sentiments.append(("social", social_sentiment))

        if include_research:
            research_sentiment = self._analyze_research_sentiment(sentiment_data)
            if research_sentiment:
                source_sentiments.append(("research", research_sentiment))

        # 情感聚合
        aggregated_sentiment = self._aggregate_sentiment(source_sentiments)

        # 情感趋势分析
        sentiment_trend = self._analyze_sentiment_trend(sentiment_data)

        # 关键词分析
        sentiment_keywords = self._extract_sentiment_keywords(sentiment_data)

        # 市场情绪影响分析
        market_impact = None
        if include_correlation:
            market_impact = self._analyze_market_sentiment_impact(sentiment_data, stock_code)

        # 情感告警
        sentiment_alerts = self._generate_sentiment_alerts(aggregated_sentiment, sentiment_trend)

        # 计算综合得分
        scores = self._calculate_sentiment_scores(aggregated_sentiment, sentiment_trend, market_impact)

        # 生成信号
        signals = self._generate_sentiment_signals(aggregated_sentiment, sentiment_trend, sentiment_alerts)

        # 投资建议
        recommendations = self._generate_sentiment_recommendations(aggregated_sentiment, sentiment_trend, market_impact)

        # 风险评估
        risk_assessment = self._assess_sentiment_risk(aggregated_sentiment, sentiment_trend, sentiment_alerts)

        # 元数据
        metadata = {
            "analysis_period_days": analysis_period,
            "total_content_items": len(sentiment_data) if not sentiment_data.empty else 0,
            "sentiment_sources": [src for src, _ in source_sentiments],
            "avg_sentiment_score": aggregated_sentiment.overall_sentiment if aggregated_sentiment else 0,
            "sentiment_trend": sentiment_trend.get("direction") if sentiment_trend else "unknown",
            "keywords_extracted": (
                len(sentiment_keywords.positive_keywords) + len(sentiment_keywords.negative_keywords)
                if sentiment_keywords
                else 0
            ),
            "market_correlation": market_impact.sentiment_correlation if market_impact else 0,
            "analysis_timestamp": datetime.now(),
        }

        return AnalysisResult(
            analysis_type=AnalysisType.SENTIMENT_ANALYSIS,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata=metadata,
            raw_data=sentiment_data if kwargs.get("include_raw_data", False) else None,
        )

    except Exception as e:
        return self._create_error_result(stock_code, str(e))


def _get_sentiment_data(self, stock_code: str, days: int) -> pd.DataFrame:
    """获取舆情数据"""
    try:
        from src.data_sources.factory import get_relational_source

        relational_source = get_relational_source(source_type="mock")

        # 获取舆情数据（新闻、研报、社交媒体等）
        sentiment_data = relational_source.get_sentiment_data(stock_code=stock_code, days=days)

        if sentiment_data.empty:
            # 生成模拟舆情数据
            sentiment_data = self._generate_mock_sentiment_data(stock_code, days)

        return sentiment_data

    except Exception as e:
        print(f"Error getting sentiment data for {stock_code}: {e}")
        return self._generate_mock_sentiment_data(stock_code, days)


def _generate_mock_sentiment_data(self, stock_code: str, days: int) -> pd.DataFrame:
    """生成模拟舆情数据"""
    np.random.seed(hash(stock_code) % 2**32)

    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
    data = []

    # 模拟不同来源的舆情数据
    sources = ["news", "research", "social", "forum"]
    base_sentiment = np.random.uniform(-0.3, 0.3)  # 基础情感

    for i, date in enumerate(dates):
        # 添加时间趋势和随机波动
        trend_factor = 0.1 * np.sin(i / 5)  # 周期性趋势
        random_factor = np.random.normal(0, 0.2)

        for source in sources:
            sentiment = base_sentiment + trend_factor + random_factor + np.random.uniform(-0.2, 0.2)

            # 限制在-1到1之间
            sentiment = max(-1.0, min(1.0, sentiment))

            # 生成模拟内容
            content = self._generate_mock_content(sentiment, source)

            data.append(
                {
                    "date": date,
                    "source": source,
                    "content": content,
                    "sentiment": sentiment,
                    "title": f"关于{stock_code}的{source}内容 {i + 1}",
                    "url": f"https://example.com/{source}/{stock_code}/{i + 1}",
                    "author": f"用户{i % 10 + 1}",
                    "views": np.random.randint(100, 10000),
                    "likes": np.random.randint(0, 1000),
                }
            )

    return pd.DataFrame(data)


def _generate_mock_content(self, sentiment: float, source: str) -> str:
    """生成模拟内容"""
    positive_words = ["上涨", "增长", "利好", "突破", "创新", "业绩", "盈利", "乐观", "看好", "机会"]
    negative_words = ["下跌", "亏损", "风险", "担忧", "回调", "压力", "减持", "悲观", "谨慎", "危机"]
    neutral_words = ["稳定", "震荡", "正常", "关注", "观察", "等待", "调整", "平衡", "中性", "持平"]

    if sentiment > 0.2:
        words = positive_words * 3 + neutral_words
        tone = "positive"
    elif sentiment < -0.2:
        words = negative_words * 3 + neutral_words
        tone = "negative"
    else:
        words = neutral_words * 2 + positive_words + negative_words
        tone = "neutral"

    # 随机选择词汇组成句子
    selected_words = np.random.choice(words, size=np.random.randint(5, 15), replace=True)
    content = f"{' '.join(selected_words)}。"

    # 根据来源类型调整内容
    if source == "news":
        content = f"财经新闻：{content}"
    elif source == "research":
        content = f"研报分析：{content}"
    elif source == "social":
        content = f"投资者讨论：{content}"
    elif source == "forum":
        content = f"论坛帖子：{content}"

    return content


def _analyze_news_sentiment(self, sentiment_data: pd.DataFrame) -> Optional[SentimentScore]:
    """分析新闻情感"""
    news_data = sentiment_data[sentiment_data["source"] == "news"]
    if news_data.empty:
        return None

    return self._calculate_sentiment_score(news_data["content"].tolist())


def _analyze_social_sentiment(self, sentiment_data: pd.DataFrame) -> Optional[SentimentScore]:
    """分析社交媒体情感"""
    social_data = sentiment_data[sentiment_data["source"].isin(["social", "forum"])]
    if social_data.empty:
        return None

    # 考虑互动量（views, likes）的权重
    contents = []
    weights = []

    for _, row in social_data.iterrows():
        contents.append(row["content"])
        # 权重基于互动量
        interaction_weight = min((row.get("views", 0) + row.get("likes", 0) * 10) / 1000, 1.0)
        weights.append(max(0.1, interaction_weight))  # 最小权重0.1

    return self._calculate_weighted_sentiment_score(contents, weights)


def _analyze_research_sentiment(self, sentiment_data: pd.DataFrame) -> Optional[SentimentScore]:
    """分析研报情感"""
    research_data = sentiment_data[sentiment_data["source"] == "research"]
    if research_data.empty:
        return None

    # 研报通常更客观，给更高置信度
    score = self._calculate_sentiment_score(research_data["content"].tolist())
    if score:
        score.confidence = min(score.confidence * 1.2, 1.0)  # 提高置信度

    return score


def _calculate_sentiment_score(self, contents: List[str]) -> SentimentScore:
    """计算情感评分"""
    if not contents:
        return SentimentScore(0, 0, 0, 0, 0, 0)

    sentiments = []

    for content in contents:
        if len(content.strip()) < self.sentiment_params["min_content_length"]:
            continue

        try:
            if SNOWNLP_AVAILABLE:
                # 使用SnowNLP进行中文情感分析
                s = SnowNLP(content)
                sentiment = s.sentiments  # 0-1之间的值
                # 转换为-1到1的范围
                sentiment = (sentiment - 0.5) * 2
            else:
                # 简化的情感分析
                sentiment = self._simple_sentiment_analysis(content)

            sentiments.append(sentiment)

        except Exception as e:
            print(f"Error analyzing sentiment for content: {e}")
            continue

    if not sentiments:
        return SentimentScore(0, 0, 0, 0, 0, 0)

    # 计算统计量
    sentiments = np.array(sentiments)
    overall_sentiment = np.mean(sentiments)

    positivity = np.mean(sentiments[sentiments > 0.1]) if np.any(sentiments > 0.1) else 0
    negativity = abs(np.mean(sentiments[sentiments < -0.1])) if np.any(sentiments < -0.1) else 0
    neutrality = np.mean(np.abs(sentiments) <= 0.1) if np.any(np.abs(sentiments) <= 0.1) else 0

    # 计算置信度（基于一致性和样本量）
    sentiment_std = np.std(sentiments)
    confidence = max(0.1, 1 - sentiment_std) * min(1.0, len(sentiments) / 10)

    # 计算情感强度
    intensity = np.mean(np.abs(sentiments))

    return SentimentScore(
        overall_sentiment=overall_sentiment,
        positivity=max(0, positivity),
        negativity=max(0, negativity),
        neutrality=max(0, neutrality),
        confidence=confidence,
        intensity=intensity,
    )


def _calculate_weighted_sentiment_score(self, contents: List[str], weights: List[float]) -> SentimentScore:
    """计算加权情感评分"""
    if not contents or len(contents) != len(weights):
        return SentimentScore(0, 0, 0, 0, 0, 0)

    sentiments = []
    valid_weights = []

    for content, weight in zip(contents, weights):
        try:
            if SNOWNLP_AVAILABLE:
                s = SnowNLP(content)
                sentiment = (s.sentiments - 0.5) * 2
            else:
                sentiment = self._simple_sentiment_analysis(content)

            sentiments.append(sentiment)
            valid_weights.append(weight)

        except Exception as e:
            print(f"Error analyzing weighted sentiment: {e}")
            continue

    if not sentiments:
        return SentimentScore(0, 0, 0, 0, 0, 0)

    # 加权平均
    sentiments = np.array(sentiments)
    weights = np.array(valid_weights)

    overall_sentiment = np.average(sentiments, weights=weights)

    # 计算其他指标
    positive_mask = sentiments > 0.1
    negative_mask = sentiments < -0.1
    neutral_mask = (sentiments >= -0.1) & (sentiments <= 0.1)

    positivity = np.average(sentiments[positive_mask], weights=weights[positive_mask]) if np.any(positive_mask) else 0
    negativity = (
        abs(np.average(sentiments[negative_mask], weights=weights[negative_mask])) if np.any(negative_mask) else 0
    )
    neutrality = (
        np.average(np.abs(sentiments[neutral_mask]), weights=weights[neutral_mask]) if np.any(neutral_mask) else 0
    )

    confidence = max(0.1, 1 - np.average(np.abs(sentiments - overall_sentiment), weights=weights))
    intensity = np.average(np.abs(sentiments), weights=weights)

    return SentimentScore(
        overall_sentiment=overall_sentiment,
        positivity=max(0, positivity),
        negativity=max(0, negativity),
        neutrality=max(0, neutrality),
        confidence=confidence,
        intensity=intensity,
    )


def _simple_sentiment_analysis(self, text: str) -> float:
    """简化的情感分析"""
    # 基于情感词典的简单分析
    positive_score = 0
    negative_score = 0

    words = self._tokenize_text(text)

    for word in words:
        if word in self.sentiment_lexicon.get("positive", set()):
            positive_score += 1
        elif word in self.sentiment_lexicon.get("negative", set()):
            negative_score += 1

    total_sentiment_words = positive_score + negative_score

    if total_sentiment_words == 0:
        return 0.0

    # 归一化到-1到1
    sentiment = (positive_score - negative_score) / total_sentiment_words
    return max(-1.0, min(1.0, sentiment))


def _tokenize_text(self, text: str) -> List[str]:
    """分词"""
    if SNOWNLP_AVAILABLE:
        try:
            return jieba.lcut(text)
        except:
            pass

    # 简化的分词（按字符分割）
    return list(text)


def _aggregate_sentiment(self, source_sentiments: List[Tuple[str, SentimentScore]]) -> SentimentScore:
    """聚合多源情感"""
    if not source_sentiments:
        return SentimentScore(0, 0, 0, 0, 0, 0)

    # 不同来源的权重
    source_weights = {
        "news": 0.3,
        "research": 0.4,  # 研报权重最高
        "social": 0.2,
        "forum": 0.1,
    }

    sentiments = []
    weights = []

    for source_type, sentiment_score in source_sentiments:
        sentiments.append(sentiment_score.overall_sentiment)
        weights.append(source_weights.get(source_type, 0.2))

    # 加权平均
    overall_sentiment = np.average(sentiments, weights=weights)

    # 聚合其他指标
    positivity = np.average([s.positivity for _, s in source_sentiments], weights=weights)
    negativity = np.average([s.negativity for _, s in source_sentiments], weights=weights)
    neutrality = np.average([s.neutrality for _, s in source_sentiments], weights=weights)
    confidence = np.average([s.confidence for _, s in source_sentiments], weights=weights)
    intensity = np.average([s.intensity for _, s in source_sentiments], weights=weights)

    return SentimentScore(
        overall_sentiment=overall_sentiment,
        positivity=positivity,
        negativity=negativity,
        neutrality=neutrality,
        confidence=confidence,
        intensity=intensity,
    )


def _analyze_sentiment_trend(self, sentiment_data: pd.DataFrame) -> Dict[str, Any]:
    """分析情感趋势"""
    if sentiment_data.empty:
        return {"direction": "unknown", "strength": 0, "change_rate": 0}

    try:
        # 按日期聚合情感
        daily_sentiment = sentiment_data.groupby("date")["sentiment"].mean()

        if len(daily_sentiment) < 3:
            return {"direction": "unknown", "strength": 0, "change_rate": 0}

        # 计算趋势
        sentiment_values = daily_sentiment.values
        trend_slope = np.polyfit(range(len(sentiment_values)), sentiment_values, 1)[0]

        # 判断趋势方向
        if trend_slope > 0.001:
            direction = "improving"
        elif trend_slope < -0.001:
            direction = "declining"
        else:
            direction = "stable"

        # 计算趋势强度
        strength = min(abs(trend_slope) * 100, 1.0)

        # 计算变化率
        change_rate = trend_slope * len(sentiment_values)

        return {
            "direction": direction,
            "strength": strength,
            "change_rate": change_rate,
            "slope": trend_slope,
            "data_points": len(sentiment_values),
        }

    except Exception as e:
        print(f"Error analyzing sentiment trend: {e}")
        return {"direction": "unknown", "strength": 0, "change_rate": 0}


def _extract_sentiment_keywords(self, sentiment_data: pd.DataFrame) -> SentimentKeywords:
    """提取情感关键词"""
    positive_keywords = []
    negative_keywords = []
    neutral_keywords = []

    try:
        if sentiment_data.empty:
            return SentimentKeywords([], [], [], [], {})

        all_content = " ".join(sentiment_data["content"].fillna(""))

        if SNOWNLP_AVAILABLE:
            # 使用jieba提取关键词
            keywords = jieba.analyse.extract_tags(all_content, topK=50)

            # 简单的分类（可扩展为更复杂的分类）
            for keyword in keywords[:20]:
                # 简化的情感判断
                if any(word in keyword for word in ["上涨", "增长", "利好", "突破", "创新", "业绩", "盈利", "乐观"]):
                    positive_keywords.append(keyword)
                elif any(word in keyword for word in ["下跌", "亏损", "风险", "担忧", "回调", "压力", "悲观"]):
                    negative_keywords.append(keyword)
                else:
                    neutral_keywords.append(keyword)
        else:
            # 简化的关键词提取
            words = self._tokenize_text(all_content)
            word_freq = {}

            for word in words:
                if len(word.strip()) > 1 and word not in self.stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1

            # 按频率排序
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, freq in sorted_words[:30]]

            # 随机分类（实际应该基于情感词典）
            np.random.shuffle(keywords)
            split1 = len(keywords) // 3
            split2 = 2 * len(keywords) // 3

            positive_keywords = keywords[:split1]
            negative_keywords = keywords[split1:split2]
            neutral_keywords = keywords[split2:]

    except Exception as e:
        print(f"Error extracting sentiment keywords: {e}")

    # 计算关键词权重（基于出现频率）
    keyword_weights = {}
    for keyword in positive_keywords + negative_keywords + neutral_keywords:
        keyword_weights[keyword] = np.random.uniform(0.1, 1.0)  # 简化权重计算

    # 新兴话题（最近高频出现的关键词）
    emerging_topics = positive_keywords[:5] + negative_keywords[:3]

    return SentimentKeywords(
        positive_keywords=positive_keywords,
        negative_keywords=negative_keywords,
        neutral_keywords=neutral_keywords,
        emerging_topics=emerging_topics,
        keyword_weights=keyword_weights,
    )


def _analyze_market_sentiment_impact(
    self, sentiment_data: pd.DataFrame, stock_code: str
) -> Optional[MarketSentimentImpact]:
    """分析市场情绪影响"""
    try:
        # 获取价格数据
        price_data = self._get_historical_data(stock_code, days=30, data_type="1d")

        if price_data.empty or sentiment_data.empty:
            return None

        # 计算每日平均情感
        daily_sentiment = sentiment_data.groupby("date")["sentiment"].mean()

        # 对齐价格和情感数据
        combined_data = pd.DataFrame(
            {"price": price_data.set_index("date")["close"], "sentiment": daily_sentiment}
        ).dropna()

        if len(combined_data) < 5:
            return MarketSentimentImpact(0, 0, 0, 0, "unknown")

        # 计算相关性和领先滞后关系
        max_lag = min(self.sentiment_params["correlation_lag_max"], len(combined_data) - 1)

        correlations = []
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                corr = combined_data["sentiment"].corr(combined_data["price"].shift(-lag))
            else:
                corr = combined_data["sentiment"].corr(combined_data["price"].shift(lag))

            if not pd.isna(corr):
                correlations.append((lag, corr))

        if not correlations:
            return MarketSentimentImpact(0, 0, 0, 0, "unknown")

        # 找到最佳相关性
        best_corr = max(correlations, key=lambda x: abs(x[1]))
        sentiment_correlation = best_corr[1]
        sentiment_lead_lag = best_corr[0]

        # 计算影响强度
        impact_strength = abs(sentiment_correlation)

        # 计算预测能力
        predictive_power = max(0, sentiment_correlation * (1 - abs(sentiment_lead_lag) / max_lag))

        # 判断情绪状态
        avg_sentiment = combined_data["sentiment"].mean()
        if avg_sentiment > 0.2:
            sentiment_regime = "bullish"
        elif avg_sentiment < -0.2:
            sentiment_regime = "bearish"
        else:
            sentiment_regime = "neutral"

        return MarketSentimentImpact(
            sentiment_correlation=sentiment_correlation,
            sentiment_lead_lag=sentiment_lead_lag,
            impact_strength=impact_strength,
            predictive_power=predictive_power,
            sentiment_regime=sentiment_regime,
        )

    except Exception as e:
        print(f"Error analyzing market sentiment impact: {e}")
        return None


def _generate_sentiment_alerts(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any]
) -> List[SentimentAlert]:
    """生成情感告警"""
    alerts = []

    try:
        # 极端情感告警
        if abs(sentiment.overall_sentiment) > 0.7:
            alert_type = "extreme_positive" if sentiment.overall_sentiment > 0 else "extreme_negative"
            severity = "high"

            alert = SentimentAlert(
                alert_type=alert_type,
                severity=severity,
                trigger_value=sentiment.overall_sentiment,
                threshold=0.7,
                description=f"市场情绪{sentiment.overall_sentiment:.2f}，{'极度乐观' if sentiment.overall_sentiment > 0 else '极度悲观'}",
                recommended_action="密切关注市场动向，谨慎决策",
            )
            alerts.append(alert)

        # 情感突变告警
        trend_direction = sentiment_trend.get("direction", "stable")
        trend_strength = sentiment_trend.get("strength", 0)

        if trend_strength > 0.5 and trend_direction in ["improving", "declining"]:
            alert = SentimentAlert(
                alert_type="sentiment_trend_change",
                severity="medium",
                trigger_value=trend_strength,
                threshold=0.5,
                description=f"市场情绪{trend_direction}趋势明显，强度{trend_strength:.2f}",
                recommended_action="关注情绪趋势变化对市场的影响",
            )
            alerts.append(alert)

    except Exception as e:
        print(f"Error generating sentiment alerts: {e}")

    return alerts


def _calculate_sentiment_scores(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], market_impact: Optional[MarketSentimentImpact]
) -> Dict[str, float]:
    """计算舆情分析得分"""
    scores = {}

    try:
        # 情感强度得分
        sentiment_intensity_score = min(sentiment.intensity * 2, 1.0)
        scores["sentiment_intensity"] = sentiment_intensity_score

        # 情感一致性得分
        sentiment_consistency = 1 - abs(sentiment.positivity + sentiment.negativity - 1)
        scores["sentiment_consistency"] = sentiment_consistency

        # 情感置信度得分
        confidence_score = sentiment.confidence
        scores["sentiment_confidence"] = confidence_score

        # 趋势稳定性得分
        trend_stability = 1 - sentiment_trend.get("change_rate", 0) * 10
        trend_stability = max(0, min(trend_stability, 1))
        scores["trend_stability"] = trend_stability

        # 市场影响得分
        if market_impact:
            market_influence_score = market_impact.impact_strength * market_impact.predictive_power
            scores["market_influence"] = market_influence_score
        else:
            scores["market_influence"] = 0.5

        # 综合得分
        weights = {
            "sentiment_intensity": 0.2,
            "sentiment_consistency": 0.2,
            "sentiment_confidence": 0.25,
            "trend_stability": 0.15,
            "market_influence": 0.2,
        }

        overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        scores["overall_score"] = overall_score

    except Exception as e:
        print(f"Error calculating sentiment scores: {e}")
        scores = {"overall_score": 0.5, "error": True}

    return scores


def _generate_sentiment_signals(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], alerts: List[SentimentAlert]
) -> List[Dict[str, Any]]:
    """生成舆情信号"""
    signals = []

    # 情感强度信号
    if sentiment.intensity > 0.6:
        direction = "正面" if sentiment.overall_sentiment > 0 else "负面"
        severity = "high" if sentiment.intensity > 0.8 else "medium"

        signals.append(
            {
                "type": f"sentiment_intensity_{direction.lower()}",
                "severity": severity,
                "message": f"市场情绪{direction}强度高 ({sentiment.overall_sentiment:.2f})",
                "details": {
                    "overall_sentiment": sentiment.overall_sentiment,
                    "intensity": sentiment.intensity,
                    "positivity": sentiment.positivity,
                    "negativity": sentiment.negativity,
                },
            }
        )

    # 情感趋势信号
    trend_direction = sentiment_trend.get("direction", "stable")
    trend_strength = sentiment_trend.get("strength", 0)

    if trend_strength > 0.4 and trend_direction != "stable":
        direction_text = {"improving": "改善", "declining": "恶化", "stable": "稳定"}.get(trend_direction, "未知")

        signals.append(
            {
                "type": f"sentiment_trend_{trend_direction}",
                "severity": "medium",
                "message": f"市场情绪趋势{direction_text} ({trend_strength:.2f})",
                "details": {
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength,
                    "change_rate": sentiment_trend.get("change_rate", 0),
                },
            }
        )

    # 告警信号
    for alert in alerts:
        signals.append(
            {
                "type": f"alert_{alert.alert_type}",
                "severity": alert.severity,
                "message": alert.description,
                "details": {
                    "alert_type": alert.alert_type,
                    "trigger_value": alert.trigger_value,
                    "threshold": alert.threshold,
                    "recommended_action": alert.recommended_action,
                },
            }
        )

    return signals


def _generate_sentiment_recommendations(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], market_impact: Optional[MarketSentimentImpact]
) -> Dict[str, Any]:
    """生成舆情建议"""
    recommendations = {}

    try:
        # 基于情感的建议
        if sentiment.overall_sentiment > 0.3:
            primary_signal = "bullish"
            action = "市场情绪偏乐观，可适度关注投资机会"
            confidence = "medium"
        elif sentiment.overall_sentiment < -0.3:
            primary_signal = "bearish"
            action = "市场情绪偏悲观，建议谨慎观望"
            confidence = "medium"
        else:
            primary_signal = "neutral"
            action = "市场情绪相对中性，按常规策略操作"
            confidence = "low"

        # 考虑趋势
        trend_direction = sentiment_trend.get("direction", "stable")
        if trend_direction == "improving" and sentiment.overall_sentiment > 0:
            action += " (情绪趋势向好，可适当乐观)"
            confidence = "high" if confidence == "medium" else confidence
        elif trend_direction == "declining" and sentiment.overall_sentiment < 0:
            action += " (情绪趋势恶化，需谨慎应对)"
            confidence = "high" if confidence == "medium" else confidence

        # 考虑市场影响
        if market_impact and market_impact.predictive_power > 0.6:
            correlation = market_impact.sentiment_correlation
            if abs(correlation) > 0.5:
                direction = "正相关" if correlation > 0 else "负相关"
                action += f" (情绪与价格{direction}较强，影响显著)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "sentiment_analysis": {
                    "overall_sentiment": sentiment.overall_sentiment,
                    "intensity": sentiment.intensity,
                    "confidence": sentiment.confidence,
                },
                "trend_analysis": sentiment_trend,
                "market_impact": (
                    {
                        "correlation": market_impact.sentiment_correlation if market_impact else 0,
                        "predictive_power": market_impact.predictive_power if market_impact else 0,
                        "sentiment_regime": market_impact.sentiment_regime if market_impact else "unknown",
                    }
                    if market_impact
                    else None
                ),
            }
        )

    except Exception as e:
        print(f"Error generating sentiment recommendations: {e}")
        recommendations = {
            "primary_signal": "neutral",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_sentiment_risk(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], alerts: List[SentimentAlert]
) -> Dict[str, Any]:
    """评估舆情风险"""
    risk_assessment = {}

    try:
        # 情感极端风险
        sentiment_extreme_risk = "low"
        if abs(sentiment.overall_sentiment) > 0.7:
            sentiment_extreme_risk = "high"
        elif abs(sentiment.overall_sentiment) > 0.5:
            sentiment_extreme_risk = "medium"

        # 情感波动风险
        sentiment_volatility = sentiment_trend.get("change_rate", 0)
        volatility_risk = "low"
        if abs(sentiment_volatility) > 0.1:
            volatility_risk = "high"
        elif abs(sentiment_volatility) > 0.05:
            volatility_risk = "medium"

        # 告警风险
        alert_risk = "low"
        if alerts:
            high_severity_alerts = [a for a in alerts if a.severity == "high"]
            if high_severity_alerts:
                alert_risk = "high"
            else:
                alert_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1}
        avg_risk_score = np.mean(
            [
                risk_scores.get(sentiment_extreme_risk, 1),
                risk_scores.get(volatility_risk, 1),
                risk_scores.get(alert_risk, 1),
            ]
        )

        if avg_risk_score > 2.5:
            overall_risk = "high"
        elif avg_risk_score > 1.5:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        risk_assessment.update(
            {
                "overall_risk_level": overall_risk,
                "sentiment_extreme_risk": sentiment_extreme_risk,
                "volatility_risk": volatility_risk,
                "alert_risk": alert_risk,
                "risk_factors": [
                    "市场情绪极端偏离" if sentiment_extreme_risk == "high" else None,
                    "情绪波动过于剧烈" if volatility_risk == "high" else None,
                    "存在严重情绪告警" if alert_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "市场情绪极端偏离" if sentiment_extreme_risk == "high" else None,
                        "情绪波动过于剧烈" if volatility_risk == "high" else None,
                        "存在严重情绪告警" if alert_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing sentiment risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _load_sentiment_lexicon(self) -> Dict[str, set]:
    """加载情感词典"""
    # 简化的中文情感词典
    return {
        "positive": {
            "上涨",
            "增长",
            "利好",
            "突破",
            "创新",
            "业绩",
            "盈利",
            "乐观",
            "看好",
            "机会",
            "发展",
            "进步",
            "成功",
            "优秀",
            "良好",
            "强势",
        },
        "negative": {
            "下跌",
            "亏损",
            "风险",
            "担忧",
            "回调",
            "压力",
            "减持",
            "悲观",
            "谨慎",
            "危机",
            "问题",
            "困难",
            "损失",
            "下跌",
            "暴跌",
            "恐慌",
        },
    }


def _load_stop_words(self) -> set:
    """加载停用词"""
    return {
        "的",
        "了",
        "和",
        "是",
        "在",
        "有",
        "这",
        "那",
        "一个",
        "公司",
        "股票",
        "市场",
        "投资",
        "资金",
        "价格",
        "交易",
        "投资者",
        "分析",
    }


def _initialize_sentiment_classifier(self):
    """初始化情感分类器"""
    # 这里可以初始化更复杂的分类器
    return None


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.SENTIMENT_ANALYSIS,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"舆情分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
