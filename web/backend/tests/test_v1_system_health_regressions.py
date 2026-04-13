from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.system.health", None)
    return importlib.import_module("app.api.v1.system.health")


async def test_v1_database_health_returns_runtime_response():
    module = _load_module()

    payload = await module.get_database_health()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["overall_status"] in {"healthy", "degraded", "unhealthy", "unknown"}
    assert len(payload.data["databases"]) == 2
    assert {item["database_type"] for item in payload.data["databases"]} == {"postgresql", "tdengine"}


async def test_v1_classification_stats_returns_runtime_response():
    module = _load_module()

    payload = await module.get_data_classification_stats()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["total_classifications"] > 0
    assert "market_data" in payload.data["stats"]
    assert payload.data["stats"]["market_data"]["record_count"] > 0
