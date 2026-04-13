from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.system.routing", None)
    return importlib.import_module("app.api.v1.system.routing")


async def test_v1_data_route_returns_runtime_routing_decision():
    module = _load_module()
    request = module.DataRoutingRequest(
        data_category="market_data",
        symbol="IF9999.CCFX",
        date_range={"start": "2025-03-01", "end": "2025-03-31"},
    )

    payload = await module.get_data_route(request)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "route_selected": "tdengine",
        "estimated_records": 44640,
        "query_complexity": "high_frequency",
        "recommended_strategy": "time_series_scan",
        "classification": "minute_kline",
    }


async def test_v1_data_route_resolves_reference_data_to_postgresql():
    module = _load_module()
    request = module.DataRoutingRequest(data_category="reference_data", symbol="600519.SH")

    payload = await module.get_data_route(request)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "route_selected": "postgresql",
        "estimated_records": 1,
        "query_complexity": "lookup",
        "recommended_strategy": "indexed_lookup",
        "classification": "symbols_info",
    }
