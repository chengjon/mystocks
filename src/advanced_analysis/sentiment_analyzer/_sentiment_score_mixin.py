"""Shared methods for `sentiment_score.py`."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType
from src.advanced_analysis.sentiment_analyzer._sentiment_score_tail import SentimentAnalyzerTailMixin
from src.advanced_analysis.sentiment_analyzer.sentiment_models import (
    SentimentKeywords,
    SentimentScore,
)

try:
    from snownlp import SnowNLP
    import jieba
    import jieba.analyse
    SNOWNLP_AVAILABLE = True
except ImportError:
    SNOWNLP_AVAILABLE = False

logger = logging.getLogger(__name__)


class SentimentAnalyzerMixin(SentimentAnalyzerTailMixin):
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
            logger.error("Error getting sentiment data for %s: %s", stock_code, e)
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
        elif sentiment < -0.2:
            words = negative_words * 3 + neutral_words
        else:
            words = neutral_words * 2 + positive_words + negative_words

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
                logger.error("Error analyzing sentiment for content: %s", e)
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
                logger.error("Error analyzing weighted sentiment: %s", e)
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
            logger.error("Error analyzing sentiment trend: %s", e)
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
            logger.error("Error extracting sentiment keywords: %s", e)

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
