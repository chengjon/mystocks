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

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis.sentiment_analyzer._generate_sentiment_signals import (
    _assess_sentiment_risk,
    _create_error_result,
    _generate_sentiment_recommendations,
    _generate_sentiment_signals,
    _initialize_sentiment_classifier,
    _load_sentiment_lexicon,
    _load_stop_words,
)
from src.advanced_analysis.sentiment_analyzer._sentiment_score_mixin import SentimentAnalyzerMixin


class SentimentAnalyzer(SentimentAnalyzerMixin, BaseAnalyzer):
    """
    舆情分析器

    提供全面的舆情分析功能，包括：
    - 新闻和研报情感提取
    - 社交媒体情感监控
    - 情感趋势分析和相关性
    - 市场情绪影响评估
    - 多源情感聚合
    """


SentimentAnalyzer._generate_sentiment_signals = _generate_sentiment_signals
SentimentAnalyzer._generate_sentiment_recommendations = _generate_sentiment_recommendations
SentimentAnalyzer._assess_sentiment_risk = _assess_sentiment_risk
SentimentAnalyzer._load_sentiment_lexicon = _load_sentiment_lexicon
SentimentAnalyzer._load_stop_words = _load_stop_words
SentimentAnalyzer._initialize_sentiment_classifier = _initialize_sentiment_classifier
SentimentAnalyzer._create_error_result = _create_error_result

__init__ = SentimentAnalyzer.__init__
analyze = SentimentAnalyzer.analyze
_get_sentiment_data = SentimentAnalyzer._get_sentiment_data
_generate_mock_sentiment_data = SentimentAnalyzer._generate_mock_sentiment_data
_generate_mock_content = SentimentAnalyzer._generate_mock_content
_analyze_news_sentiment = SentimentAnalyzer._analyze_news_sentiment
_analyze_social_sentiment = SentimentAnalyzer._analyze_social_sentiment
_analyze_research_sentiment = SentimentAnalyzer._analyze_research_sentiment
_calculate_sentiment_score = SentimentAnalyzer._calculate_sentiment_score
_calculate_weighted_sentiment_score = SentimentAnalyzer._calculate_weighted_sentiment_score
_simple_sentiment_analysis = SentimentAnalyzer._simple_sentiment_analysis
_tokenize_text = SentimentAnalyzer._tokenize_text
_aggregate_sentiment = SentimentAnalyzer._aggregate_sentiment
_analyze_sentiment_trend = SentimentAnalyzer._analyze_sentiment_trend
_extract_sentiment_keywords = SentimentAnalyzer._extract_sentiment_keywords
_analyze_market_sentiment_impact = SentimentAnalyzer._analyze_market_sentiment_impact
_generate_sentiment_alerts = SentimentAnalyzer._generate_sentiment_alerts
_calculate_sentiment_scores = SentimentAnalyzer._calculate_sentiment_scores
