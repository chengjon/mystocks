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
    sys.modules.pop("app.services.system_resource_metrics", None)
    return importlib.import_module("app.services.system_resource_metrics")


async def test_collect_resource_metrics_returns_host_process_dependency_sections(monkeypatch):
    module = _load_module()

    monkeypatch.setattr(module.psutil, "cpu_percent", lambda interval=None: 82.5)
    monkeypatch.setattr(
        module.psutil,
        "virtual_memory",
        lambda: SimpleNamespace(percent=68.0, used=8 * 1024**3, total=16 * 1024**3),
    )
    monkeypatch.setattr(
        module.psutil,
        "disk_usage",
        lambda _path: SimpleNamespace(percent=91.0, used=910 * 1024**3, total=1000 * 1024**3),
    )
    monkeypatch.setattr(module.os, "getloadavg", lambda: (3.2, 2.1, 1.4))
    monkeypatch.setattr(module.os, "cpu_count", lambda: 8)
    monkeypatch.setattr(
        module,
        "_sample_processes",
        lambda sampled_at: [
            {
                "process_key": "mystocks-backend",
                "display_name": "mystocks-backend",
                "status": "normal",
                "pid": 1234,
                "cpu_percent": 14.2,
                "memory_mb": 512.0,
                "memory_percent": 5.0,
                "sampled_at": sampled_at,
            },
            {
                "process_key": "mystocks-frontend",
                "display_name": "mystocks-frontend",
                "status": "warning",
                "pid": 2345,
                "cpu_percent": 45.0,
                "memory_mb": 256.0,
                "memory_percent": 3.2,
                "sampled_at": sampled_at,
            },
        ],
    )

    async def _fake_dependencies(sampled_at):
        return [
            {
                "dependency_key": "postgresql",
                "display_name": "PostgreSQL",
                "status": "normal",
                "summary": "pool healthy",
                "sampled_at": sampled_at,
                "metrics": {"active_connections": 2, "usage_percentage": 20.0},
            },
            {
                "dependency_key": "redis",
                "display_name": "Redis",
                "status": "warning",
                "summary": "memory pressure",
                "sampled_at": sampled_at,
                "metrics": {"used_memory_mb": 256.0},
            },
        ]

    monkeypatch.setattr(module, "_sample_dependencies", _fake_dependencies)

    payload = await module.collect_resource_metrics(
        window_minutes=60,
        include_processes=True,
        include_dependencies=True,
    )

    assert payload["node"]["scope"] == "single-node"
    assert payload["node"]["window_minutes"] == 60
    assert payload["host"]["cpu"]["status"] == "warning"
    assert payload["host"]["memory"]["status"] == "normal"
    assert payload["host"]["disk"]["status"] == "critical"
    assert payload["host"]["load"]["status"] == "normal"
    assert payload["processes"][0]["process_key"] == "mystocks-backend"
    assert payload["dependencies"][0]["dependency_key"] == "postgresql"
    assert payload["thresholds"]["host.cpu_percent"] == {
        "warning": 70.0,
        "critical": 90.0,
        "unit": "%",
    }


async def test_collect_resource_metrics_appends_short_window_series(monkeypatch):
    module = _load_module()

    cpu_values = iter([10.0, 20.0])
    monkeypatch.setattr(module.psutil, "cpu_percent", lambda interval=None: next(cpu_values))
    monkeypatch.setattr(
        module.psutil,
        "virtual_memory",
        lambda: SimpleNamespace(percent=30.0, used=3 * 1024**3, total=16 * 1024**3),
    )
    monkeypatch.setattr(
        module.psutil,
        "disk_usage",
        lambda _path: SimpleNamespace(percent=40.0, used=400 * 1024**3, total=1000 * 1024**3),
    )
    monkeypatch.setattr(module.os, "getloadavg", lambda: (1.0, 0.8, 0.5))
    monkeypatch.setattr(module.os, "cpu_count", lambda: 8)
    monkeypatch.setattr(module, "_sample_processes", lambda sampled_at: [])

    async def _fake_dependencies(sampled_at):
        return []

    monkeypatch.setattr(module, "_sample_dependencies", _fake_dependencies)

    await module.collect_resource_metrics(window_minutes=60, include_processes=False, include_dependencies=False)
    payload = await module.collect_resource_metrics(window_minutes=60, include_processes=False, include_dependencies=False)

    cpu_series = payload["host"]["cpu"]["series"]

    assert cpu_series[-2]["value"] == 10.0
    assert cpu_series[-1]["value"] == 20.0
    assert payload["processes"] == []
    assert payload["dependencies"] == []
