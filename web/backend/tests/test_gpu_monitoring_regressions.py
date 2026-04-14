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


async def test_gpu_status_returns_runtime_availability_snapshot():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-status"))

    async def fake_snapshot(device_id=None):
        return {
            "status": "available",
            "reason": None,
            "device_id": device_id,
            "gpus": [
                {
                    "device_id": 1,
                    "name": "RTX Test",
                    "gpu_utilization": 55.0,
                    "memory_used": 2048,
                    "memory_total": 8192,
                    "memory_utilization": 25.0,
                    "temperature": 0.0,
                    "power_usage": 0.0,
                    "health_status": "healthy",
                    "allocated_strategies": 2,
                    "timestamp": 123.0,
                }
            ],
        }

    module._get_gpu_runtime_snapshot = fake_snapshot

    payload = await module.get_gpu_status(request, device_id=1)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["status"] == "available"
    assert payload.data["gpus"][0]["device_id"] == 1


async def test_gpu_performance_returns_runtime_metrics():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-performance"))

    async def fake_snapshot(device_id=None):
        return {
            "status": "available",
            "reason": None,
            "device_id": device_id,
            "gpus": [
                {
                    "device_id": 0,
                    "name": "RTX Test",
                    "gpu_utilization": 61.5,
                    "memory_used": 4096,
                    "memory_total": 8192,
                    "memory_utilization": 50.0,
                    "temperature": 0.0,
                    "power_usage": 0.0,
                    "health_status": "warning",
                    "allocated_strategies": 1,
                    "timestamp": 456.0,
                }
            ],
        }

    module._get_gpu_runtime_snapshot = fake_snapshot

    payload = await module.get_gpu_performance(request, device_id=None)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["metrics"] == [
        {
            "device_id": 0,
            "gpu_utilization": 61.5,
            "memory_utilization": 50.0,
            "temperature": 0.0,
            "power_usage": 0.0,
            "timestamp": 456.0,
            "health_status": "warning",
        }
    ]


async def test_gpu_history_returns_runtime_snapshot_only_payload():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-history"))

    async def fake_snapshot(device_id=None):
        return {
            "status": "available",
            "reason": None,
            "device_id": device_id,
            "gpus": [
                {
                    "device_id": 0,
                    "name": "RTX Test",
                    "gpu_utilization": 12.5,
                    "memory_used": 1024,
                    "memory_total": 8192,
                    "memory_utilization": 12.5,
                    "temperature": 0.0,
                    "power_usage": 0.0,
                    "health_status": "healthy",
                    "allocated_strategies": 0,
                    "timestamp": 100.0,
                }
            ],
        }

    module._get_gpu_runtime_snapshot = fake_snapshot

    payload = await module.get_gpu_history(request, device_id=0, start_time=None, end_time=None, limit=10)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "status": "runtime_snapshot_only",
        "device_id": 0,
        "records": [
            {
                "timestamp": 100.0,
                "device_id": 0,
                "gpu_utilization": 12.5,
                "memory_utilization": 12.5,
                "temperature": 0.0,
                "power_usage": 0.0,
                "source": "runtime_snapshot",
            }
        ],
        "total": 1,
        "reason": None,
    }


async def test_gpu_metrics_returns_runtime_prometheus_text():
    module = _load_module()
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-gpu-metrics"))

    async def fake_snapshot(device_id=None):
        return {
            "status": "available",
            "reason": None,
            "device_id": device_id,
            "gpus": [
                {
                    "device_id": 0,
                    "name": "RTX Test",
                    "gpu_utilization": 88.0,
                    "memory_used": 2048,
                    "memory_total": 8192,
                    "memory_utilization": 25.0,
                    "temperature": 0.0,
                    "power_usage": 0.0,
                    "health_status": "healthy",
                    "allocated_strategies": 3,
                    "timestamp": 789.0,
                }
            ],
        }

    module._get_gpu_runtime_snapshot = fake_snapshot

    response = await module.get_prometheus_metrics(request)
    body = response.body.decode()

    assert response.media_type == "text/plain"
    assert "mystocks_gpu_available 1" in body
    assert 'mystocks_gpu_utilization_percent{device_id="0"} 88.0' in body
    assert 'mystocks_gpu_allocated_strategies{device_id="0"} 3' in body
