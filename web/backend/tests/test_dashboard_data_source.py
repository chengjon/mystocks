from app.api.dashboard_data_source import RealBusinessDataSource


class _FakeResponse:
    def __init__(self, payload: dict):
        self.status_code = 200
        self._payload = payload

    def json(self) -> dict:
        return self._payload


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
