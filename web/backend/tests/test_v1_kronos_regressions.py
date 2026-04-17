from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.analysis.kronos", None)
    return importlib.import_module("app.api.v1.analysis.kronos")


async def test_kronos_predict_normalizes_missing_amount_and_propagates_meta(monkeypatch):
    module = _load_module()

    captured_payload = {}

    class _FakeClient:
        async def predict_ohlcv(self, payload):
            captured_payload.update(payload)
            return {
                "data": {
                    "predictions": [
                        {
                            "timestamp": "2026-04-17T10:00:00+00:00",
                            "open": 10.4,
                            "high": 10.6,
                            "low": 10.2,
                            "close": 10.5,
                            "volume": 120000.0,
                            "amount": 1250000.0,
                        }
                    ],
                    "confidence": 0.81,
                },
                "meta": {
                    "model": "small",
                    "device": "cuda:0",
                    "degraded": False,
                    "cached": False,
                    "latency_ms": 250,
                    "queue_wait_ms": 12,
                },
                "request_id": "req-1",
            }

    monkeypatch.setattr(module, "get_kronos_client", lambda: _FakeClient())

    request = module.KronosPredictRequest(
        request_id="req-1",
        model=module.KronosModel.SMALL,
        candles=[
            module.KronosCandle(
                timestamp="2026-04-17T09:30:00+00:00",
                open=10.0,
                high=10.6,
                low=9.8,
                close=10.2,
                volume=1000,
            )
        ],
        pred_len=5,
        sample_count=2,
        top_p=0.9,
        temperature=1.0,
    )

    payload = await module.predict_with_kronos(request)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["meta"]["model"] == "small"
    assert payload.data["meta"]["latency_ms"] == 250
    assert captured_payload["candles"][0]["amount"] > 0
    assert captured_payload["candles"][0]["volume"] == 1000.0


async def test_kronos_encode_maps_service_unavailable_to_unified_error(monkeypatch):
    module = _load_module()

    class _FakeClient:
        async def encode_kline(self, payload):
            raise module.KronosServiceUnavailableError("remote timeout", code="TIMEOUT")

    monkeypatch.setattr(module, "get_kronos_client", lambda: _FakeClient())

    request = module.KronosEncodeRequest(
        request_id="req-2",
        model=module.KronosModel.SMALL,
        candles=[
            module.KronosCandle(
                timestamp="2026-04-17T09:30:00+00:00",
                open=10.0,
                high=10.6,
                low=9.8,
                close=10.2,
            )
        ],
    )

    payload = await module.encode_with_kronos(request)

    assert payload.success is False
    assert payload.code == 503
    assert payload.errors is not None
    assert payload.errors[0].code == "TIMEOUT"


async def test_kronos_predict_can_load_local_daily_kline_by_symbol(monkeypatch):
    module = _load_module()

    class _FakeDbService:
        def query_daily_kline(self, symbol, start_date, end_date):
            assert symbol == "600519"
            return pd.DataFrame(
                [
                    {
                        "trade_date": "2026-04-15",
                        "open": 10.0,
                        "high": 10.5,
                        "low": 9.8,
                        "close": 10.2,
                        "volume": 1000,
                        "amount": 10200,
                    },
                    {
                        "trade_date": "2026-04-16",
                        "open": 10.2,
                        "high": 10.7,
                        "low": 10.1,
                        "close": 10.6,
                        "volume": 1200,
                        "amount": 12720,
                    },
                ]
            )

    class _FakeClient:
        async def predict_ohlcv(self, payload):
            assert len(payload["candles"]) == 2
            assert payload["candles"][0]["timestamp"].endswith("+00:00")
            return {
                "data": {"predictions": [], "confidence": 0.4},
                "meta": {"model": "small", "cached": False, "degraded": False},
                "message": "ok",
            }

    monkeypatch.setattr(module, "db_service", _FakeDbService())
    monkeypatch.setattr(module, "get_kronos_client", lambda: _FakeClient())

    request = module.KronosPredictRequest(
        request_id="req-3",
        model=module.KronosModel.SMALL,
        symbol="600519",
        lookback=2,
        pred_len=2,
    )

    payload = await module.predict_with_kronos(request)

    assert payload.success is True
    assert payload.code == 200


async def test_kronos_predict_can_load_local_daily_kline_by_date_range(monkeypatch):
    module = _load_module()

    captured_dates = {}

    class _FakeDbService:
        def query_daily_kline(self, symbol, start_date, end_date):
            captured_dates["symbol"] = symbol
            captured_dates["start_date"] = start_date
            captured_dates["end_date"] = end_date
            return pd.DataFrame(
                [
                    {
                        "trade_date": "2026-04-10",
                        "open": 9.9,
                        "high": 10.1,
                        "low": 9.7,
                        "close": 10.0,
                        "volume": 900,
                    },
                    {
                        "trade_date": "2026-04-11",
                        "open": 10.0,
                        "high": 10.3,
                        "low": 9.9,
                        "close": 10.2,
                        "volume": 1100,
                    },
                ]
            )

    class _FakeClient:
        async def predict_ohlcv(self, payload):
            assert len(payload["candles"]) == 2
            return {
                "data": {"predictions": [], "confidence": 0.55},
                "meta": {"model": "small", "cached": False, "degraded": False},
                "message": "ok",
            }

    monkeypatch.setattr(module, "db_service", _FakeDbService())
    monkeypatch.setattr(module, "get_kronos_client", lambda: _FakeClient())

    request = module.KronosPredictRequest(
        request_id="req-range",
        model=module.KronosModel.SMALL,
        symbol="000001",
        start_date="2026-04-10",
        end_date="2026-04-11",
        pred_len=2,
    )

    payload = await module.predict_with_kronos(request)

    assert payload.success is True
    assert payload.code == 200
    assert captured_dates == {
        "symbol": "000001",
        "start_date": "2026-04-10",
        "end_date": "2026-04-11",
    }


def test_kronos_request_rejects_custom_lookback_when_date_range_is_used():
    module = _load_module()

    try:
        module.KronosPredictRequest(
            symbol="000001",
            start_date="2026-04-10",
            end_date="2026-04-11",
            lookback=30,
            pred_len=2,
        )
    except Exception as exc:
        assert "lookback cannot be customized" in str(exc)
    else:
        raise AssertionError("Expected validation error for mixed range and lookback mode")


async def test_kronos_status_returns_normalized_runtime_state(monkeypatch):
    module = _load_module()

    class _FakeClient:
        async def get_status(self):
            return {
                "data": {
                    "health": "healthy",
                    "active_model": "small",
                    "loaded_models": ["small"],
                    "queue_depth": 0,
                },
                "meta": {
                    "model": "small",
                    "device": "cuda:0",
                    "degraded": False,
                    "cached": False,
                    "latency_ms": 3,
                    "queue_wait_ms": 0,
                },
                "request_id": "req-status",
            }

    monkeypatch.setattr(module, "get_kronos_client", lambda: _FakeClient())

    payload = await module.get_kronos_status()

    assert payload.success is True
    assert payload.code == 200
    assert payload.request_id == "req-status"
    assert payload.data["health"] == "healthy"
    assert payload.data["meta"]["device"] == "cuda:0"


async def test_kronos_status_maps_service_unavailable_to_unified_error(monkeypatch):
    module = _load_module()

    class _FakeClient:
        async def get_status(self):
            raise module.KronosServiceUnavailableError("status timeout", code="TIMEOUT")

    monkeypatch.setattr(module, "get_kronos_client", lambda: _FakeClient())

    payload = await module.get_kronos_status()

    assert payload.success is False
    assert payload.code == 503
    assert payload.errors is not None
    assert payload.errors[0].code == "TIMEOUT"
