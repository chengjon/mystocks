from __future__ import annotations

import os
from typing import Any

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_USER", "test")
os.environ.setdefault("POSTGRESQL_PASSWORD", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8020")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8021")
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DEVELOPMENT_MODE", "true")

from app.api.market import market_data_request
from app.core.security import User, get_current_user
from app.main import app
from app.services.openstock_client import OpenStockFetchResult


class _FakeOpenStockClient:
    def __init__(self, result: OpenStockFetchResult) -> None:
        self.result = result
        self.calls: list[dict[str, Any]] = []
        self.closed = False

    async def fetch(
        self,
        data_category: str,
        *,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> OpenStockFetchResult:
        self.calls.append(
            {
                "data_category": data_category,
                "params": dict(params or {}),
                "request_id": request_id,
            }
        )
        return self.result

    async def aclose(self) -> None:
        self.closed = True


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        username="test-user",
        email="test@example.com",
        role="admin",
        is_active=True,
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_market_quotes_route_fetches_realtime_quotes_from_openstock(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeOpenStockClient(
        OpenStockFetchResult(
            data=[
                {"symbol": "300750.SZ", "price": 165.5},
                {"symbol": "600519.SH", "price": 1450.0},
            ],
            source="openstock",
            endpoint_name="realtime_quotes",
            data_category="REALTIME_QUOTES",
            request_id="route-quotes",
            raw=None,
        )
    )

    async def _legacy_factory_should_not_be_called() -> object:
        raise AssertionError("legacy data_source_factory should not be called")

    monkeypatch.setattr(market_data_request, "get_openstock_market_client", lambda: fake, raising=False)
    monkeypatch.setattr(
        "app.services.data_source_factory.get_data_source_factory",
        _legacy_factory_should_not_be_called,
    )

    response = client.get("/api/v1/market/quotes?symbols=300750.SZ,600519.SH")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["quotes"] == [
        {"symbol": "300750.SZ", "price": 165.5},
        {"symbol": "600519.SH", "price": 1450.0},
    ]
    assert body["data"]["source"] == "openstock"
    assert body["data"]["endpoint"] == "realtime_quotes"
    assert fake.calls == [
        {
            "data_category": "REALTIME_QUOTES",
            "params": {"symbols": ["300750.SZ", "600519.SH"]},
            "request_id": None,
        }
    ]
    assert fake.closed is True


def test_market_kline_route_fetches_kline_from_openstock_and_preserves_response_shape(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = [
        {"date": f"2026-01-{day:02d}", "open": 10 + day, "close": 11 + day}
        for day in range(1, 11)
    ]
    fake = _FakeOpenStockClient(
        OpenStockFetchResult(
            data={
                "stock_code": "000001.SZ",
                "stock_name": "Ping An Bank",
                "period": "daily",
                "adjust": "qfq",
                "data": rows,
                "count": len(rows),
            },
            source="openstock",
            endpoint_name="kline",
            data_category="KLINES",
            request_id="route-kline",
            raw=None,
        )
    )

    def _legacy_service_should_not_be_called() -> object:
        raise AssertionError("legacy stock_search_service should not be called")

    monkeypatch.setattr(market_data_request, "get_openstock_market_client", lambda: fake, raising=False)
    monkeypatch.setattr(
        "app.services.stock_search_service.get_stock_search_service",
        _legacy_service_should_not_be_called,
    )

    response = client.get(
        "/api/v1/market/kline"
        "?stock_code=000001.SZ&period=daily&adjust=qfq&start_date=2026-01-01&end_date=2026-01-20"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["stock_code"] == "000001.SZ"
    assert body["stock_name"] == "Ping An Bank"
    assert body["period"] == "daily"
    assert body["adjust"] == "qfq"
    assert body["data"] == rows
    assert body["count"] == 10
    assert "timestamp" in body
    assert fake.calls == [
        {
            "data_category": "KLINES",
            "params": {
                "symbol": "000001.SZ",
                "period": "daily",
                "adjust": "qfq",
                "start_date": "2026-01-01",
                "end_date": "2026-01-20",
            },
            "request_id": None,
        }
    ]
    assert fake.closed is True
