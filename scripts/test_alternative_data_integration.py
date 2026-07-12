"""测试另类数据集成
Test Alternative Data Integration

验证新闻采集、情感分析、社交媒体监控等功能的正确性。
Validates news collection, sentiment analysis, social media monitoring functions.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch


# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.alternative_data.news_sentiment_analyzer import (
    NewsArticle,
    NewsCollector,
    NewsSentimentService,
    SentimentAnalyzer,
)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockDatabaseConnection:
    """模拟数据库连接"""

    def __init__(self):
        self.executed_queries = []

    async def fetch(self, query: str, *args):
        """模拟查询"""
        # 返回模拟的新闻文章数据
        if "news_articles" in query:
            return [
                {
                    "article_id": "test_article_1",
                    "title": "测试新闻标题",
                    "content": "这是测试新闻内容，包含积极的市场信息。",
                    "sentiment_score": 0.3,
                    "sentiment_label": "positive",
                    "confidence": 0.8,
                    "symbols": ["600519"],
                    "published_at": datetime.now(),
                },
            ]
        return []

    async def fetchval(self, query: str, *args):
        """模拟单个值查询"""
        return 5

    async def execute(self, query: str, *args):
        """模拟执行"""
        self.executed_queries.append((query, args))
        return 1

    async def executemany(self, query: str, values: list):
        """模拟批量执行"""
        self.executed_queries.append((query, values))
        return len(values)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def test_news_collector():
    """测试新闻采集器"""
    logger.info("🧪 测试新闻采集器...")

    # 创建模拟数据库管理器
    mock_db_manager = MagicMock()
    mock_conn = MockDatabaseConnection()
    mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_conn
    mock_db_manager.get_connection.return_value.__aexit__.return_value = None

    collector = NewsCollector(mock_db_manager)

    # 测试股票识别
    text = "茅台股价上涨5%，市场反应积极。平安银行业绩稳健。"
    symbols = collector._identify_related_symbols(text)

    assert "600519" in symbols, "应该识别出茅台(600519)"
    assert "000001" in symbols, "应该识别出平安银行(000001)"

    # 测试HTML清理
    html_content = "<p>这是<strong>测试</strong>内容</p><script>alert('test')</script>"
    clean_content = collector._clean_html(html_content)

    assert "<" not in clean_content, "HTML标签应该被清理"
    assert "script" not in clean_content, "脚本标签应该被清理"
    assert "这是测试内容" in clean_content, "文本内容应该保留"

    # 测试文章去重
    articles = [
        NewsArticle(title="标题1", content="内容1", url="url1"),
        NewsArticle(title="标题1", content="内容1", url="url1"),  # 重复
        NewsArticle(title="标题2", content="内容2", url="url2"),
    ]

    unique_articles = collector._deduplicate_articles(articles)
    assert len(unique_articles) == 2, "应该去重为2篇文章"

    logger.info("✅ 新闻采集器测试通过")


async def test_sentiment_analyzer():
    """测试情感分析器"""
    logger.info("🧪 测试情感分析器...")

    analyzer = SentimentAnalyzer()

    # 测试积极文本
    positive_text = "股价大幅上涨，市场前景乐观，投资者信心增强"
    positive_result = await analyzer.analyze_sentiment(positive_text)

    assert positive_result.sentiment_label == "positive", "应该识别为积极情感"
    assert positive_result.sentiment_score > 0, "积极文本得分应该为正"

    # 测试消极文本
    negative_text = "股价暴跌，市场恐慌，投资者损失惨重"
    negative_result = await analyzer.analyze_sentiment(negative_text)

    assert negative_result.sentiment_label == "negative", "应该识别为消极情感"
    assert negative_result.sentiment_score < 0, "消极文本得分应该为负"

    # 测试中性文本
    neutral_text = "今天天气不错，市场交易正常"
    neutral_result = await analyzer.analyze_sentiment(neutral_text)

    assert neutral_result.sentiment_label == "neutral", "应该识别为中性情感"
    assert abs(neutral_result.sentiment_score) < 0.1, "中性文本得分应该接近0"

    # 测试空文本
    empty_result = await analyzer.analyze_sentiment("")
    assert empty_result.sentiment_label == "neutral", "空文本应该返回中性"

    logger.info("✅ 情感分析器测试通过")


async def test_news_sentiment_service():
    """测试新闻情感分析服务"""
    logger.info("🧪 测试新闻情感分析服务...")

    # 创建模拟数据库管理器
    mock_db_manager = MagicMock()
    mock_conn = MockDatabaseConnection()
    mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_conn
    mock_db_manager.get_connection.return_value.__aexit__.return_value = None

    service = NewsSentimentService(mock_db_manager)

    # 测试情感指标获取
    indicators = await service.get_sentiment_indicators("600519", 24)

    assert "symbol" in indicators, "应该包含股票代码"
    assert "sentiment_score" in indicators, "应该包含情感分数"
    assert "sentiment_trend" in indicators, "应该包含情感趋势"
    assert "confidence" in indicators, "应该包含置信度"
    assert "article_count" in indicators, "应该包含文章数量"

    # 测试市场情感概览
    overview = await service.get_market_sentiment_overview(24)

    assert "market_sentiment_score" in overview, "应该包含市场情感分数"
    assert "market_trend" in overview, "应该包含市场趋势"
    assert "analyzed_symbols" in overview, "应该包含分析的股票数量"
    assert "symbol_sentiments" in overview, "应该包含各股票情感数据"

    # 验证股票数量
    assert overview["analyzed_symbols"] >= 0, "分析股票数量应该>=0"
    assert overview["total_symbols"] >= overview["analyzed_symbols"], "总股票数量应该>=分析数量"

    logger.info("✅ 新闻情感分析服务测试通过")


async def test_integration_flow():
    """测试集成流程"""
    logger.info("🧪 测试集成流程...")

    # 创建模拟数据库管理器
    mock_db_manager = MagicMock()
    mock_conn = MockDatabaseConnection()
    mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_conn
    mock_db_manager.get_connection.return_value.__aexit__.return_value = None

    service = NewsSentimentService(mock_db_manager)

    # Mock新闻采集器以返回测试数据
    test_articles = [
        NewsArticle(
            title="茅台股价上涨，市场乐观",
            content="贵州茅台今日股价上涨5%，投资者对白酒板块前景乐观。",
            url="https://test.com/article1",
            source="Test News",
            published_at=datetime.now(),
            symbols=["600519"],
        ),
        NewsArticle(
            title="平安银行业绩稳健",
            content="平安银行公布业绩，净利润同比增长15%。",
            url="https://test.com/article2",
            source="Test News",
            published_at=datetime.now(),
            symbols=["000001"],
        ),
    ]

    with patch.object(service.collector, "collect_news", return_value=test_articles):
        # 执行完整流程
        analyzed_articles = await service.collect_and_analyze_news(24)

        # 验证结果
        assert len(analyzed_articles) == 2, "应该处理2篇文章"

        for article in analyzed_articles:
            assert hasattr(article, "sentiment_score"), "文章应该有情感分数"
            assert hasattr(article, "sentiment_label"), "文章应该有情感标签"
            assert hasattr(article, "confidence"), "文章应该有置信度"
            assert article.sentiment_label in ["positive", "negative", "neutral"], "情感标签应该有效"

        # 验证茅台相关文章的情感应该是积极的
        maotai_article = next((a for a in analyzed_articles if "600519" in a.symbols), None)
        if maotai_article:
            assert maotai_article.sentiment_score >= -0.1, "茅台上涨新闻情感应该不消极"

        logger.info("✅ 集成流程测试通过")


async def test_error_handling():
    """测试错误处理"""
    logger.info("🧪 测试错误处理...")

    # 创建模拟数据库管理器
    mock_db_manager = MagicMock()
    mock_db_manager.get_connection.side_effect = Exception("Database connection failed")

    service = NewsSentimentService(mock_db_manager)

    # 测试数据库连接失败的情况
    indicators = await service.get_sentiment_indicators("600519", 24)

    # 应该返回错误信息而不是崩溃
    assert "error" in indicators, "应该包含错误信息"
    assert indicators["symbol"] == "600519", "应该保留股票代码"

    # 测试市场概览错误处理
    overview = await service.get_market_sentiment_overview(24)
    assert "error" in overview, "应该包含错误信息"

    logger.info("✅ 错误处理测试通过")


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 运行另类数据集成完整测试套件...")

    results = []

    # 测试1: 新闻采集器
    logger.info("\n" + "=" * 50)
    logger.info("TEST 1: 新闻采集器")
    logger.info("=" * 50)
    result1 = await test_news_collector()
    results.append(("News Collector", result1))

    # 测试2: 情感分析器
    logger.info("\n" + "=" * 50)
    logger.info("TEST 2: 情感分析器")
    logger.info("=" * 50)
    result2 = await test_sentiment_analyzer()
    results.append(("Sentiment Analyzer", result2))

    # 测试3: 新闻情感分析服务
    logger.info("\n" + "=" * 50)
    logger.info("TEST 3: 新闻情感分析服务")
    logger.info("=" * 50)
    result3 = await test_news_sentiment_service()
    results.append(("News Sentiment Service", result3))

    # 测试4: 集成流程
    logger.info("\n" + "=" * 50)
    logger.info("TEST 4: 集成流程")
    logger.info("=" * 50)
    result4 = await test_integration_flow()
    results.append(("Integration Flow", result4))

    # 测试5: 错误处理
    logger.info("\n" + "=" * 50)
    logger.info("TEST 5: 错误处理")
    logger.info("=" * 50)
    result5 = await test_error_handling()
    results.append(("Error Handling", result5))

    # 总结
    logger.info("\n" + "=" * 50)
    logger.info("📊 测试结果汇总")
    logger.info("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info("%s: %s", test_name, status)
        if success:
            passed += 1

    logger.info("总体: %d/%d 测试通过", passed, total)

    if passed == total:
        logger.info("🎉 所有测试通过! 另类数据集成已准备就绪。")
        logger.info("新闻采集、情感分析、数据存储等功能均正常工作。")
        return True
    logger.warning("⚠️ 某些测试失败。请检查实现。")
    return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
