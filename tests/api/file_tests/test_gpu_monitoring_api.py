"""
File-level route and model contract tests for gpu_monitoring.py.

这里覆盖当前真实的 GPU 监控路由、Pydantic 模型和 mock 响应行为。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def gpu_monitoring_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.gpu_monitoring")


class TestGpuMonitoringAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_gpu_routes(self, gpu_monitoring_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in gpu_monitoring_module.router.routes}

        assert gpu_monitoring_module.router.prefix == "/api/gpu"
        assert gpu_monitoring_module.router.tags == ["gpu-monitoring"]
        assert ("/api/gpu/status", ("GET",)) in route_methods
        assert ("/api/gpu/performance", ("GET",)) in route_methods
        assert ("/api/gpu/metrics", ("GET",)) in route_methods
        assert ("/api/gpu/history", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_routes(self, gpu_monitoring_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in gpu_monitoring_module.router.routes]

        assert len(route_pairs) == 4
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_gpu_status_model_fields_and_ranges_are_stable(self, gpu_monitoring_module):
        fields = gpu_monitoring_module.GPUStatus.model_fields

        assert set(fields) == {
            "device_id",
            "name",
            "gpu_utilization",
            "memory_used",
            "memory_total",
            "memory_utilization",
            "temperature",
            "power_usage",
            "sm_clock",
            "memory_clock",
        }
        assert any(getattr(meta, "ge", None) == 0 for meta in fields["gpu_utilization"].metadata)
        assert any(getattr(meta, "le", None) == 100 for meta in fields["gpu_utilization"].metadata)
        assert any(getattr(meta, "ge", None) == 0 for meta in fields["memory_utilization"].metadata)
        assert any(getattr(meta, "le", None) == 100 for meta in fields["memory_utilization"].metadata)

    @pytest.mark.file_test
    def test_gpu_performance_model_fields_are_stable(self, gpu_monitoring_module):
        fields = set(gpu_monitoring_module.GPUPerformanceMetrics.model_fields)

        assert fields == {
            "device_id",
            "matrix_gflops",
            "matrix_speedup",
            "memory_gflops",
            "memory_speedup",
            "throughput",
            "timestamp",
        }

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_get_gpu_status_returns_unified_response_payload(self, gpu_monitoring_module):
        request = SimpleNamespace(state=SimpleNamespace(request_id="req-1"))

        payload = await gpu_monitoring_module.get_gpu_status(request, device_id=None)

        assert payload.success is False
        assert payload.code == 503
        assert payload.message == "GPU监控服务未接入"
        assert payload.request_id == "req-1"
        assert payload.data == {"status": "placeholder", "device_id": None, "gpus": []}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_get_gpu_performance_returns_unified_response_payload(self, gpu_monitoring_module):
        request = SimpleNamespace(state=SimpleNamespace(request_id="req-2"))

        payload = await gpu_monitoring_module.get_gpu_performance(request, device_id=0)

        assert payload.success is False
        assert payload.code == 503
        assert payload.message == "GPU监控服务未接入"
        assert payload.data == {"status": "placeholder", "device_id": 0, "metrics": []}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_get_prometheus_metrics_returns_plain_text_response(self, gpu_monitoring_module):
        request = SimpleNamespace(state=SimpleNamespace(request_id="req-3"))

        response = await gpu_monitoring_module.get_prometheus_metrics(request)

        assert response.media_type == "text/plain"
        assert response.body.decode() == "GPU metrics exporter unavailable\n"

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_get_gpu_history_returns_empty_history_structure(self, gpu_monitoring_module):
        request = SimpleNamespace(state=SimpleNamespace(request_id="req-4"))

        payload = await gpu_monitoring_module.get_gpu_history(request, device_id=0, start_time=None, end_time=None, limit=10)

        assert payload.success is False
        assert payload.code == 503
        assert payload.message == "GPU监控服务未接入"
        assert payload.data == {"status": "placeholder", "device_id": 0, "records": [], "total": 0}

    @pytest.mark.file_test
    def test_route_names_remain_stable(self, gpu_monitoring_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in gpu_monitoring_module.router.routes}

        assert route_names[("/api/gpu/status", ("GET",))] == "get_gpu_status"
        assert route_names[("/api/gpu/performance", ("GET",))] == "get_gpu_performance"
        assert route_names[("/api/gpu/metrics", ("GET",))] == "get_prometheus_metrics"
        assert route_names[("/api/gpu/history", ("GET",))] == "get_gpu_history"

    @pytest.mark.file_test
    def test_module_docstring_mentions_prometheus_and_hardware_monitoring(self, gpu_monitoring_module):
        doc = gpu_monitoring_module.__doc__ or ""

        assert "Prometheus" in doc
        assert "GPU实时状态查询" in doc
