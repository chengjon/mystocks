from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType
from datetime import datetime


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.alternative_data", None)
    return importlib.import_module("app.api.alternative_data")


def test_get_news_service_uses_real_database_manager():
    fake_news_module = ModuleType("src.alternative_data.news_sentiment_analyzer")
    fake_db_pool_module = ModuleType("src.core.database_pool")
    fake_audit_module = ModuleType("src.infrastructure.logging.audit_system")

    class FakeDatabaseConnectionManager:
        pass

    class FakeNewsSentimentService:
        def __init__(self, db_manager):
            self.db_manager = db_manager
            self.collector = type("Collector", (), {"db_manager": db_manager})()

    class FakeAuditEvent:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class FakeAuditManager:
        async def log_audit_event(self, event):
            return event

    fake_news_module.NewsSentimentService = FakeNewsSentimentService
    fake_db_pool_module.DatabaseConnectionManager = FakeDatabaseConnectionManager
    fake_audit_module.AuditEvent = FakeAuditEvent
    fake_audit_module.get_audit_manager = lambda: FakeAuditManager()

    previous_news = sys.modules.get("src.alternative_data.news_sentiment_analyzer")
    previous_db_pool = sys.modules.get("src.core.database_pool")
    previous_audit = sys.modules.get("src.infrastructure.logging.audit_system")

    sys.modules["src.alternative_data.news_sentiment_analyzer"] = fake_news_module
    sys.modules["src.core.database_pool"] = fake_db_pool_module
    sys.modules["src.infrastructure.logging.audit_system"] = fake_audit_module

    try:
        module = _load_module()
        module._news_service = None
        service = module.get_news_service()
    finally:
        if previous_news is None:
            sys.modules.pop("src.alternative_data.news_sentiment_analyzer", None)
        else:
            sys.modules["src.alternative_data.news_sentiment_analyzer"] = previous_news

        if previous_db_pool is None:
            sys.modules.pop("src.core.database_pool", None)
        else:
            sys.modules["src.core.database_pool"] = previous_db_pool

        if previous_audit is None:
            sys.modules.pop("src.infrastructure.logging.audit_system", None)
        else:
            sys.modules["src.infrastructure.logging.audit_system"] = previous_audit

    assert service.db_manager is not None
    assert service.db_manager.__class__.__name__ == "FakeDatabaseConnectionManager"
    assert service.collector.db_manager is service.db_manager


async def test_get_recent_news_uses_service_collector_and_filters_results():
    fake_news_module = ModuleType("src.alternative_data.news_sentiment_analyzer")
    fake_db_pool_module = ModuleType("src.core.database_pool")
    fake_audit_module = ModuleType("src.infrastructure.logging.audit_system")

    class FakeDatabaseConnectionManager:
        pass

    class FakeArticle:
        def __init__(self, article_id, title, content, symbols, source):
            self.article_id = article_id
            self.title = title
            self.content = content
            self.url = f"https://example.com/{article_id}"
            self.source = source
            self.published_at = datetime(2026, 4, 15, 9, 0, 0)
            self.symbols = symbols
            self.relevance_score = 0.75

    class FakeCollector:
        def __init__(self, db_manager):
            self.db_manager = db_manager

        async def collect_news(self, hours_back):
            assert hours_back == 24
            return [
                FakeArticle("news-1", "利好公告", "业绩增长并分红", ["600519"], "测试源A"),
                FakeArticle("news-2", "风险提示", "处罚与下滑风险", ["000001"], "测试源B"),
            ]

    class FakeSentiment:
        def __init__(self, score, label, confidence):
            self.sentiment_score = score
            self.sentiment_label = label
            self.confidence = confidence

    class FakeAnalyzer:
        async def analyze_sentiment(self, text):
            if "增长" in text:
                return FakeSentiment(0.6, "positive", 0.88)
            return FakeSentiment(-0.4, "negative", 0.81)

    class FakeNewsSentimentService:
        def __init__(self, db_manager):
            self.db_manager = db_manager
            self.collector = FakeCollector(db_manager)
            self.analyzer = FakeAnalyzer()

    class FakeAuditEvent:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class FakeAuditManager:
        async def log_audit_event(self, event):
            return event

    fake_news_module.NewsSentimentService = FakeNewsSentimentService
    fake_db_pool_module.DatabaseConnectionManager = FakeDatabaseConnectionManager
    fake_audit_module.AuditEvent = FakeAuditEvent
    fake_audit_module.get_audit_manager = lambda: FakeAuditManager()

    previous_news = sys.modules.get("src.alternative_data.news_sentiment_analyzer")
    previous_db_pool = sys.modules.get("src.core.database_pool")
    previous_audit = sys.modules.get("src.infrastructure.logging.audit_system")

    sys.modules["src.alternative_data.news_sentiment_analyzer"] = fake_news_module
    sys.modules["src.core.database_pool"] = fake_db_pool_module
    sys.modules["src.infrastructure.logging.audit_system"] = fake_audit_module

    try:
        module = _load_module()
        module._news_service = None
        response = await module.get_recent_news(limit=10, sentiment_filter="positive", symbol="600519", hours_back=24)
    finally:
        if previous_news is None:
            sys.modules.pop("src.alternative_data.news_sentiment_analyzer", None)
        else:
            sys.modules["src.alternative_data.news_sentiment_analyzer"] = previous_news

        if previous_db_pool is None:
            sys.modules.pop("src.core.database_pool", None)
        else:
            sys.modules["src.core.database_pool"] = previous_db_pool

        if previous_audit is None:
            sys.modules.pop("src.infrastructure.logging.audit_system", None)
        else:
            sys.modules["src.infrastructure.logging.audit_system"] = previous_audit

    assert len(response) == 1
    assert response[0].article_id == "news-1"
    assert response[0].sentiment_label == "positive"
    assert response[0].symbols == ["600519"]
