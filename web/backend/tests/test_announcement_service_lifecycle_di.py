from __future__ import annotations

import inspect
from datetime import date
from types import SimpleNamespace

import pytest

from app.api.announcement import routes
from app.services import announcement_service


def test_announcement_service_dependency_installs_app_state_when_missing(monkeypatch):
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(announcement_service, "AnnouncementService", lambda: fake_service)

    assert announcement_service.get_announcement_service_dependency(request) is fake_service
    assert getattr(fake_app.state, announcement_service.ANNOUNCEMENT_SERVICE_STATE_KEY) is fake_service


def test_announcement_routes_accept_injected_announcement_service():
    for function_name in [
        "fetch_announcements",
        "get_announcements",
        "get_today_announcements",
        "get_important_announcements",
        "get_announcement_stats",
        "get_monitor_rules",
        "create_monitor_rule",
        "update_monitor_rule",
        "delete_monitor_rule",
        "get_triggered_records",
        "evaluate_monitor_rules",
    ]:
        signature = inspect.signature(getattr(routes, function_name))
        assert "service" in signature.parameters


@pytest.mark.asyncio
async def test_fetch_announcements_uses_injected_announcement_service():
    class FakeAnnouncementService:
        def __init__(self):
            self.fetch_kwargs = None

        def fetch_and_save_announcements(self, **kwargs):
            self.fetch_kwargs = kwargs
            return {"success": True, "saved": 1}

    fake_service = FakeAnnouncementService()
    start = date(2026, 5, 1)
    end = date(2026, 5, 2)

    response = await routes.fetch_announcements(
        symbol="000001",
        start_date=start,
        end_date=end,
        category="all",
        service=fake_service,
    )

    assert response == {"success": True, "saved": 1}
    assert fake_service.fetch_kwargs == {
        "symbol": "000001",
        "start_date": start,
        "end_date": end,
        "category": "all",
    }
