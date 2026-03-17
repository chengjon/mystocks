import importlib.util
import sys
from pathlib import Path

import pandas as pd


BACKEND_PATH = Path(__file__).resolve().parents[3] / "web" / "backend"
sys.path.insert(0, str(BACKEND_PATH))

MODULE_PATH = Path(__file__).resolve().parents[3] / "web" / "backend" / "app" / "api" / "dashboard_data_source.py"
MODULE_SPEC = importlib.util.spec_from_file_location("dashboard_data_source_module", MODULE_PATH)
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError(f"Unable to load dashboard data source module from {MODULE_PATH}")
dashboard_data_source_module = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(dashboard_data_source_module)

RealBusinessDataSource = dashboard_data_source_module.RealBusinessDataSource


def test_get_market_overview_data_returns_raw_market_payload(monkeypatch):
    source = object.__new__(RealBusinessDataSource)
    payload = {
        "indices": [{"symbol": "510300"}],
        "up_count": 1,
        "down_count": 0,
        "flat_count": 0,
        "total_volume": 1000,
        "total_turnover": 2000,
        "top_gainers": [],
        "top_losers": [],
        "most_active": [],
    }

    monkeypatch.setattr(source, "_get_market_overview_data", lambda: payload)

    result = source.get_market_overview_data()

    assert result == payload
    assert "market_overview" not in result


def test_get_market_overview_data_prefers_market_service_over_self_http(monkeypatch):
    source = object.__new__(RealBusinessDataSource)

    class _FakeMarketDataService:
        def query_etf_spot(self, limit=50, **kwargs):
            assert limit == 100
            return [
                {
                    "symbol": "510300",
                    "name": "沪深300ETF",
                    "latest_price": 3.21,
                    "change_percent": 1.5,
                    "volume": 1000,
                    "amount": 2000,
                    "trade_date": "2026-03-11",
                }
            ]

    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_market_data_service_v2",
        lambda: _FakeMarketDataService(),
        raising=False,
    )

    class _FakeTdxService:
        def get_index_quote(self, symbol: str):
            payload = {
                "000001": {"symbol": "000001", "name": "上证指数", "price": 4106.96, "change_pct": -0.64},
                "399001": {"symbol": "399001", "name": "深证成指", "price": 14270.35, "change_pct": -1.35},
                "399006": {"symbol": "399006", "name": "创业板指", "price": 3293.49, "change_pct": -1.67},
            }
            return payload[symbol]

    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_tdx_service",
        lambda: _FakeTdxService(),
        raising=False,
    )

    def _forbidden_requests_get(*args, **kwargs):
        raise AssertionError("requests.get should not be used for market overview")

    import requests

    monkeypatch.setattr(requests, "get", _forbidden_requests_get)

    result = source._get_market_overview_data()

    assert [item["symbol"] for item in result["indices"]] == ["000001", "399001", "399006"]
    assert result["top_gainers"][0]["symbol"] == "510300"
    assert result["up_count"] == 1


def test_get_market_overview_data_prefers_major_index_quotes_over_etf_semantics(monkeypatch):
    source = object.__new__(RealBusinessDataSource)

    class _FakeMarketDataService:
        def query_etf_spot(self, limit=50, **kwargs):
            assert limit == 100
            return [
                {
                    "symbol": "159260",
                    "name": "证券指数ETF",
                    "latest_price": 1.001,
                    "change_percent": 3.41,
                    "volume": 242247,
                    "amount": 24119971.68,
                    "trade_date": "2026-03-11",
                }
            ]

    class _FakeTdxService:
        def get_index_quote(self, symbol: str):
            payload = {
                "000001": {
                    "symbol": "000001",
                    "name": "上证指数",
                    "price": 3320.15,
                    "change_pct": 0.86,
                    "volume": 285000000,
                    "amount": 3120000000,
                    "timestamp": "2026-03-11T15:00:00",
                },
                "399001": {
                    "symbol": "399001",
                    "name": "深证成指",
                    "price": 10580.42,
                    "change_pct": -0.32,
                    "volume": 198000000,
                    "amount": 2450000000,
                    "timestamp": "2026-03-11T15:00:00",
                },
                "399006": {
                    "symbol": "399006",
                    "name": "创业板指",
                    "price": 2156.88,
                    "change_pct": 1.24,
                    "volume": 120000000,
                    "amount": 1650000000,
                    "timestamp": "2026-03-11T15:00:00",
                },
            }
            return payload[symbol]

    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_market_data_service_v2",
        lambda: _FakeMarketDataService(),
        raising=False,
    )
    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_tdx_service",
        lambda: _FakeTdxService(),
        raising=False,
    )

    result = source._get_market_overview_data()

    assert [item["symbol"] for item in result["indices"]] == ["000001", "399001", "399006"]
    assert [item["name"] for item in result["indices"]] == ["上证指数", "深证成指", "创业板指"]
    assert result["top_gainers"][0]["symbol"] == "159260"


def test_get_market_overview_data_prefers_realtime_market_snapshot_for_breadth_and_rankings(monkeypatch):
    source = object.__new__(RealBusinessDataSource)

    class _Row:
        def __init__(self, payload):
            self._mapping = payload

    class _Result:
        def __init__(self, rows):
            self._rows = rows

        def fetchone(self):
            return self._rows[0] if self._rows else None

        def fetchall(self):
            return self._rows

    class _Connection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, statement):
            sql = str(statement)
            if "SUM(CASE WHEN pct_chg > 0" in sql:
                return _Result(
                    [
                        _Row(
                            {
                                "up_count": 3200,
                                "down_count": 1450,
                                "flat_count": 180,
                                "total_volume": 880000000,
                                "total_turnover": 128960000000,
                            }
                        )
                    ]
                )
            if "ORDER BY pct_chg DESC" in sql:
                return _Result(
                    [
                        _Row(
                            {
                                "symbol": "600000",
                                "name": "浦发银行",
                                "current_price": 12.31,
                                "change_percent": 9.91,
                                "volume": 1200000,
                                "turnover": 321000000,
                                "update_time": "2026-03-11T15:00:00",
                            }
                        )
                    ]
                )
            if "ORDER BY pct_chg ASC" in sql:
                return _Result(
                    [
                        _Row(
                            {
                                "symbol": "000002",
                                "name": "万科A",
                                "current_price": 8.21,
                                "change_percent": -9.87,
                                "volume": 980000,
                                "turnover": 215000000,
                                "update_time": "2026-03-11T15:00:00",
                            }
                        )
                    ]
                )
            if "ORDER BY amount DESC" in sql:
                return _Result(
                    [
                        _Row(
                            {
                                "symbol": "300750",
                                "name": "宁德时代",
                                "current_price": 188.2,
                                "change_percent": 2.45,
                                "volume": 3500000,
                                "turnover": 1980000000,
                                "update_time": "2026-03-11T15:00:00",
                            }
                        )
                    ]
                )
            raise AssertionError(f"Unexpected SQL: {sql}")

    class _Engine:
        def connect(self):
            return _Connection()

    class _FakeMarketDataService:
        engine = _Engine()

        def query_etf_spot(self, limit=50, **kwargs):
            assert limit == 100
            return [
                {
                    "symbol": "159260",
                    "name": "证券指数ETF",
                    "latest_price": 1.001,
                    "change_percent": 3.41,
                    "volume": 242247,
                    "amount": 24119971.68,
                    "trade_date": "2026-03-11",
                }
            ]

    class _FakeTdxService:
        def get_index_quote(self, symbol: str):
            payload = {
                "000001": {"symbol": "000001", "name": "上证指数", "price": 4106.96, "change_pct": -0.64},
                "399001": {"symbol": "399001", "name": "深证成指", "price": 14270.35, "change_pct": -1.35},
                "399006": {"symbol": "399006", "name": "创业板指", "price": 3293.49, "change_pct": -1.67},
            }
            return payload[symbol]

    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_market_data_service_v2",
        lambda: _FakeMarketDataService(),
        raising=False,
    )
    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_tdx_service",
        lambda: _FakeTdxService(),
        raising=False,
    )

    result = source._get_market_overview_data()

    assert result["up_count"] == 3200
    assert result["down_count"] == 1450
    assert result["flat_count"] == 180
    assert result["total_turnover"] == 128960000000
    assert result["top_gainers"][0]["symbol"] == "600000"
    assert result["top_losers"][0]["symbol"] == "000002"
    assert result["most_active"][0]["symbol"] == "300750"


def test_get_market_overview_data_prefers_live_market_snapshot_over_persisted_snapshot(monkeypatch):
    source = object.__new__(RealBusinessDataSource)

    class _FakeMarketDataService:
        def query_etf_spot(self, limit=50, **kwargs):
            assert limit == 100
            return []

    class _FakeTdxService:
        def get_index_quote(self, symbol: str):
            payload = {
                "000001": {"symbol": "000001", "name": "上证指数", "price": 4106.96, "change_pct": -0.64},
                "399001": {"symbol": "399001", "name": "深证成指", "price": 14270.35, "change_pct": -1.35},
                "399006": {"symbol": "399006", "name": "创业板指", "price": 3293.49, "change_pct": -1.67},
            }
            return payload[symbol]

    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_market_data_service_v2",
        lambda: _FakeMarketDataService(),
        raising=False,
    )
    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_tdx_service",
        lambda: _FakeTdxService(),
        raising=False,
    )
    monkeypatch.setattr(
        source,
        "_get_realtime_market_snapshot",
        lambda market_service: {
            "up_count": 111,
            "down_count": 222,
            "flat_count": 3,
            "total_volume": 444,
            "total_turnover": 555,
            "top_gainers": [{"symbol": "OLD"}],
            "top_losers": [{"symbol": "OLD"}],
            "most_active": [{"symbol": "OLD"}],
        },
    )
    monkeypatch.setattr(
        source,
        "_get_live_market_snapshot",
        lambda: {
            "up_count": 3200,
            "down_count": 1450,
            "flat_count": 180,
            "total_volume": 880000000,
            "total_turnover": 128960000000,
            "top_gainers": [{"symbol": "LIVE-UP"}],
            "top_losers": [{"symbol": "LIVE-DOWN"}],
            "most_active": [{"symbol": "LIVE-ACTIVE"}],
        },
        raising=False,
    )

    result = source._get_market_overview_data()

    assert result["up_count"] == 3200
    assert result["down_count"] == 1450
    assert result["flat_count"] == 180
    assert result["top_gainers"][0]["symbol"] == "LIVE-UP"
    assert result["top_losers"][0]["symbol"] == "LIVE-DOWN"
    assert result["most_active"][0]["symbol"] == "LIVE-ACTIVE"


def test_get_market_overview_data_prefers_tdx_live_snapshot_over_persisted_snapshot(monkeypatch):
    source = object.__new__(RealBusinessDataSource)

    class _FakeMarketDataService:
        def query_etf_spot(self, limit=50, **kwargs):
            assert limit == 100
            return []

    class _FakeTdxService:
        def get_index_quote(self, symbol: str):
            payload = {
                "000001": {"symbol": "000001", "name": "上证指数", "price": 4106.96, "change_pct": -0.64},
                "399001": {"symbol": "399001", "name": "深证成指", "price": 14270.35, "change_pct": -1.35},
                "399006": {"symbol": "399006", "name": "创业板指", "price": 3293.49, "change_pct": -1.67},
            }
            return payload[symbol]

    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_market_data_service_v2",
        lambda: _FakeMarketDataService(),
        raising=False,
    )
    monkeypatch.setattr(
        dashboard_data_source_module,
        "get_tdx_service",
        lambda: _FakeTdxService(),
        raising=False,
    )
    monkeypatch.setattr(source, "_get_live_market_snapshot", lambda: None, raising=False)
    monkeypatch.setattr(
        source,
        "_get_tdx_live_market_snapshot",
        lambda market_service: {
            "up_count": 4200,
            "down_count": 900,
            "flat_count": 120,
            "total_volume": 990000000,
            "total_turnover": 1660000000000,
            "top_gainers": [{"symbol": "TDX-UP"}],
            "top_losers": [{"symbol": "TDX-DOWN"}],
            "most_active": [{"symbol": "TDX-ACTIVE"}],
        },
        raising=False,
    )
    monkeypatch.setattr(
        source,
        "_get_realtime_market_snapshot",
        lambda market_service: {
            "up_count": 111,
            "down_count": 222,
            "flat_count": 3,
            "total_volume": 444,
            "total_turnover": 555,
            "top_gainers": [{"symbol": "OLD"}],
            "top_losers": [{"symbol": "OLD"}],
            "most_active": [{"symbol": "OLD"}],
        },
        raising=False,
    )

    result = source._get_market_overview_data()

    assert result["up_count"] == 4200
    assert result["down_count"] == 900
    assert result["flat_count"] == 120
    assert result["top_gainers"][0]["symbol"] == "TDX-UP"
    assert result["top_losers"][0]["symbol"] == "TDX-DOWN"
    assert result["most_active"][0]["symbol"] == "TDX-ACTIVE"


def test_get_live_market_snapshot_skips_repeated_live_source_attempts_during_cooldown(monkeypatch):
    import src.adapters.financial_adapter as financial_adapter_module

    source = object.__new__(RealBusinessDataSource)
    attempts = {"count": 0}

    class _FailingFinancialDataSource:
        def get_real_time_data(self):
            attempts["count"] += 1
            raise RuntimeError("live snapshot unavailable")

    monkeypatch.setattr(financial_adapter_module, "FinancialDataSource", _FailingFinancialDataSource)
    monkeypatch.setattr(dashboard_data_source_module, "_LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL", None, raising=False)

    assert source._get_live_market_snapshot() is None
    assert source._get_live_market_snapshot() is None
    assert attempts["count"] == 1


def test_get_major_index_quotes_uses_short_ttl_cache(monkeypatch):
    source = object.__new__(RealBusinessDataSource)
    calls = {"count": 0}

    class _FakeTdxService:
        def get_index_quote(self, symbol: str):
            calls["count"] += 1
            return {
                "symbol": symbol,
                "name": {"000001": "上证指数", "399001": "深证成指", "399006": "创业板指"}[symbol],
                "price": 100.0,
                "change_pct": 1.0,
                "amount": 10.0,
                "timestamp": "2026-03-12T12:00:00",
            }

    monkeypatch.setattr(dashboard_data_source_module, "get_tdx_service", lambda: _FakeTdxService(), raising=False)
    monkeypatch.setattr(dashboard_data_source_module, "_MAJOR_INDEX_QUOTES_CACHE", None, raising=False)
    monkeypatch.setattr(dashboard_data_source_module, "_MAJOR_INDEX_QUOTES_CACHE_AT", None, raising=False)

    first = source._get_major_index_quotes()
    second = source._get_major_index_quotes()

    assert [item["symbol"] for item in first] == ["000001", "399001", "399006"]
    assert second == first
    assert calls["count"] == 3


def test_prewarm_dashboard_market_overview_cache_only_warms_tdx_paths(monkeypatch):
    calls = {"major": 0, "tdx": 0}

    class _FakeSource:
        def _get_major_index_quotes(self):
            calls["major"] += 1
            return [{"symbol": "000001"}]

        def _get_tdx_live_market_snapshot(self, market_service):
            calls["tdx"] += 1
            return {"up_count": 1}

        def _get_live_market_snapshot(self):
            raise AssertionError("live market snapshot should not be prewarmed at startup")

        def _get_realtime_market_snapshot(self, market_service):
            raise AssertionError("persisted snapshot should not be prewarmed at startup")

    monkeypatch.setattr(dashboard_data_source_module, "RealBusinessDataSource", _FakeSource, raising=False)
    monkeypatch.setattr(dashboard_data_source_module, "get_market_data_service_v2", lambda: object(), raising=False)

    assert dashboard_data_source_module.prewarm_dashboard_market_overview_cache() is True
    assert calls == {"major": 1, "tdx": 1}
