import json
from pathlib import Path


def test_api_smoke_endpoints_cover_trading_runtime_read_chain():
    path = Path("tests/performance/api_smoke_endpoints.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload
    assert all(item["method"] == "GET" for item in payload)
    assert {item["endpoint"] for item in payload} >= {
        "/api/trading/status",
        "/api/trading/market/snapshot",
        "/api/trading/risk/metrics",
    }
