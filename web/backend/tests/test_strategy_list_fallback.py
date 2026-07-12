import importlib

import pytest


strategy_api = importlib.import_module("web.backend.app.api.strategy_management.get_monitoring_db")


class _ILoc:
    def __init__(self, rows):
        self._rows = rows

    def __getitem__(self, _slice):
        return _DataFrameSlice(self._rows)


class _DataFrameSlice:
    def __init__(self, rows):
        self._rows = rows

    def to_dict(self, orient):
        assert orient == "records"
        return self._rows


class _DataFrameLike:
    def __init__(self, rows):
        self._rows = rows
        self.iloc = _ILoc(rows)

    def __len__(self):
        return len(self._rows)


class _Manager:
    def load_data_by_classification(self, **_kwargs):
        return _DataFrameLike(
            [
                {"strategy_id": 1, "strategy_name": "fallback_strategy", "is_active": True},
            ]
        )


class _MonitoringNoop:
    def log_operation(self, *args, **kwargs):
        return True


@pytest.mark.asyncio
async def test_list_strategies_falls_back_to_real_when_mock_source_fails(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "true")
    monkeypatch.setattr(strategy_api, "get_mock_data_manager", lambda: (_ for _ in ()).throw(RuntimeError("mock down")))
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", _Manager)
    monkeypatch.setattr(strategy_api, "get_monitoring_db", lambda: _MonitoringNoop())

    result = await strategy_api.list_strategies(status=None, page=1, page_size=20)
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result

    assert payload["data"]["total"] == 1
    assert len(payload["data"]["items"]) == 1
    assert payload["data"]["items"][0]["strategy_name"] == "fallback_strategy"
