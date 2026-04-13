from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.gpu_monitoring", None)
    return importlib.import_module("app.api.gpu_monitoring")


async def test_gpu_status_returns_placeholder_state():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-status"))

    payload = await module.get_gpu_status(request, device_id=1)

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "device_id": 1,
        "gpus": [],
    }


async def test_gpu_performance_returns_placeholder_metrics():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-performance"))

    payload = await module.get_gpu_performance(request, device_id=None)

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "device_id": None,
        "metrics": [],
    }


async def test_gpu_history_returns_placeholder_history_payload():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-history"))

    payload = await module.get_gpu_history(request, device_id=0, start_time=None, end_time=None, limit=10)

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "device_id": 0,
        "records": [],
        "total": 0,
    }


async def test_gpu_metrics_returns_unavailable_text():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-metrics"))

    response = await module.get_prometheus_metrics(request)

    assert response.media_type == "text/plain"
    assert response.body.decode() == "GPU metrics exporter unavailable\n"
