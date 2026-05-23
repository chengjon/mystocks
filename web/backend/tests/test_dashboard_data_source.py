from pathlib import Path

import pytest

from app.api import dashboard as dashboard_routes
from app.api.dashboard_data_source import RealBusinessDataSource, prewarm_dashboard_market_overview_cache


class _FakeResponse:
    def __init__(self, payload: dict):
        self.status_code = 200
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _FakeMarketDataServiceV2:
    def __init__(self):
        self.query_etf_spot_calls = []

    def query_etf_spot(self, limit: int):
        self.query_etf_spot_calls.append(limit)
        return [
            {
                "symbol": "510300",
                "name": "沪深300ETF",
                "latest_price": 4.25,
                "change_percent": 1.2,
                "volume": 1000,
                "amount": 4250,
            }
        ]


def test_dashboard_source_uses_injected_market_data_service_v2(monkeypatch):
    monkeypatch.setenv("BACKEND_PORT", "8020")

    fake_service = _FakeMarketDataServiceV2()
    source = RealBusinessDataSource(market_service=fake_service)

    monkeypatch.setattr(source, "_get_live_market_snapshot", lambda: None)
    monkeypatch.setattr(source, "_get_tdx_live_market_snapshot", lambda market_service: None)
    monkeypatch.setattr(source, "_get_realtime_market_snapshot", lambda market_service: None)
    monkeypatch.setattr(source, "_get_major_index_quotes", lambda: [])

    result = source.get_market_overview_data()

    assert fake_service.query_etf_spot_calls == [100]
    assert result["indices"][0]["symbol"] == "510300"


def test_prewarm_dashboard_market_overview_cache_uses_injected_market_data_service_v2(monkeypatch):
    monkeypatch.setenv("BACKEND_PORT", "8020")

    fake_service = _FakeMarketDataServiceV2()
    tdx_calls = []

    monkeypatch.setattr(RealBusinessDataSource, "_get_major_index_quotes", lambda self: [])
    monkeypatch.setattr(
        RealBusinessDataSource,
        "_get_tdx_live_market_snapshot",
        lambda self, market_service: tdx_calls.append(market_service) or None,
    )

    assert prewarm_dashboard_market_overview_cache(fake_service) is True
    assert tdx_calls == [fake_service]


@pytest.mark.asyncio
async def test_dashboard_summary_uses_injected_data_source(monkeypatch):
    class FakeCacheManager:
        def get_cache_stats(self):
            return {"hit_rate": "test"}

    class FakeDashboardSource:
        def __init__(self):
            self.calls = []

        def get_dashboard_summary(self, user_id, trade_date):
            self.calls.append((user_id, trade_date))
            return {
                "data_source": "injected-test",
                "generated_at": "2026-05-23T00:00:00",
            }

    async def fake_cache_dashboard_data(*args, **kwargs):
        return None

    async def fake_get_cache_manager():
        return FakeCacheManager()

    fake_source = FakeDashboardSource()

    monkeypatch.setattr(dashboard_routes, "get_cache_manager", fake_get_cache_manager)
    monkeypatch.setattr(dashboard_routes, "cache_dashboard_data", fake_cache_dashboard_data)

    result = await dashboard_routes.get_dashboard_summary(
        user_id=42,
        trade_date=None,
        include_market=False,
        include_watchlist=False,
        include_portfolio=False,
        include_alerts=False,
        bypass_cache=True,
        data_source=fake_source,
    )

    assert fake_source.calls == [(42, None)]
    assert result.data_source == "injected-test"


def test_dashboard_data_source_has_no_direct_market_data_service_v2_getter_calls():
    source_path = Path(__file__).parents[1] / "app/api/dashboard_data_source.py"

    assert "get_market_data_service_v2()" not in source_path.read_text(encoding="utf-8")


def test_get_user_active_strategies_reads_canonical_items(monkeypatch):
    monkeypatch.setenv("BACKEND_PORT", "8020")

    calls = []

    def fake_get(url, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return _FakeResponse(
            {
                "success": True,
                "data": {
                    "items": [
                        {"strategy_id": 1, "status": "active"},
                        {"strategy_id": 2, "status": "draft"},
                        {"strategy_id": 3, "is_active": True},
                    ],
                    "total": 3,
                    "page": 1,
                    "page_size": 20,
                },
            }
        )

    monkeypatch.setattr("requests.get", fake_get)

    source = RealBusinessDataSource()
    active_strategies = source._get_user_active_strategies(user_id=42)

    assert active_strategies == [
        {"strategy_id": 1, "status": "active"},
        {"strategy_id": 3, "is_active": True},
    ]
    assert calls == [
        {
            "url": "http://localhost:8020/api/v1/strategy/strategies",
            "params": {"user_id": 42},
            "timeout": 5,
        }
    ]


async def test_strategy_list_accepts_user_id_filter(monkeypatch):
    import pandas as pd

    from app.api.strategy_management import _strategy_crud_router as strategy_crud_router

    captured_filters = {}

    class FakeManager:
        def load_data_by_classification(self, classification, table_name, filters):
            captured_filters.update(filters)
            return pd.DataFrame(
                [
                    {"strategy_id": 1, "user_id": 42, "status": "active"},
                    {"strategy_id": 2, "user_id": 7, "status": "active"},
                ]
            )

    class FakeMonitoringDb:
        def log_operation(self, **kwargs):
            return None

    monkeypatch.setattr(strategy_crud_router, "_is_strategy_management_mock_enabled", lambda: False)
    monkeypatch.setattr(strategy_crud_router, "_runtime_fallback_enabled", lambda: False)
    monkeypatch.setattr(strategy_crud_router, "get_monitoring_db", lambda: FakeMonitoringDb())
    monkeypatch.setattr(strategy_crud_router, "MyStocksUnifiedManager", FakeManager)

    await strategy_crud_router.list_strategies(user_id=42)

    assert captured_filters["user_id"] == 42


async def test_strategy_list_runtime_fallback_filters_by_user_id(monkeypatch):
    import pandas as pd

    from app.api.strategy_management import _strategy_crud_router as strategy_crud_router
    from app.api.strategy_management import _helpers as strategy_helpers

    class FakeManager:
        def load_data_by_classification(self, classification, table_name, filters):
            return pd.DataFrame()

    class FakeMonitoringDb:
        def log_operation(self, **kwargs):
            return None

    monkeypatch.setattr(strategy_crud_router, "_is_strategy_management_mock_enabled", lambda: False)
    monkeypatch.setattr(strategy_crud_router, "_runtime_fallback_enabled", lambda: True)
    monkeypatch.setattr(strategy_crud_router, "get_monitoring_db", lambda: FakeMonitoringDb())
    monkeypatch.setattr(strategy_crud_router, "MyStocksUnifiedManager", FakeManager)
    monkeypatch.setattr(
        strategy_helpers,
        "_runtime_strategy_store",
        [
            {"strategy_id": 1, "user_id": 42, "status": "active"},
            {"strategy_id": 2, "user_id": 7, "status": "active"},
            {"strategy_id": 3, "status": "active"},
            {"strategy_id": 4, "user_id": 42, "status": "draft"},
        ],
    )

    result = await strategy_crud_router.list_strategies(user_id=42, status="active", page=1, page_size=20)

    assert [item["strategy_id"] for item in result.data["items"]] == [1, 3]
