from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.api import watchlist as routes
from app.services import watchlist_service


def test_watchlist_service_dependency_installs_app_state_when_missing(monkeypatch):
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(watchlist_service, "get_watchlist_service", lambda: fake_service)

    assert watchlist_service.get_watchlist_service_dependency(request) is fake_service
    assert getattr(fake_app.state, watchlist_service.WATCHLIST_SERVICE_STATE_KEY) is fake_service


def test_watchlist_group_routes_accept_injected_watchlist_service():
    for function_name in [
        "get_user_groups",
        "create_group",
        "update_group",
        "delete_group",
        "get_watchlist_by_group",
        "move_stock_to_group",
        "get_watchlist_with_groups",
    ]:
        signature = inspect.signature(getattr(routes, function_name))
        assert "service" in signature.parameters


@pytest.mark.asyncio
async def test_get_user_groups_uses_injected_watchlist_service():
    class FakeWatchlistService:
        def __init__(self):
            self.user_id = None

        def get_user_groups(self, user_id):
            self.user_id = user_id
            return [{"id": 1, "group_name": "默认分组"}]

    fake_service = FakeWatchlistService()
    current_user = SimpleNamespace(id=42)

    response = await routes.get_user_groups(
        current_user=current_user,
        service=fake_service,
    )

    assert response == [{"id": 1, "group_name": "默认分组"}]
    assert fake_service.user_id == 42
