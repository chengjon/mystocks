from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType


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
