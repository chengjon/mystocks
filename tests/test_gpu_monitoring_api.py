import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture
def app():
    app = FastAPI()
    from src.api.gpu_monitoring_routes import router

    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_get_gpu_metrics_api(client):
    response = client.get("/api/gpu/metrics/0")
    assert response.status_code == 200
    data = response.json()
    assert "gpu_utilization" in data
    assert "temperature" in data
    assert "memory_used" in data


def test_get_all_gpu_metrics_api(client):
    response = client.get("/api/gpu/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_gpu_processes_api(client):
    response = client.get("/api/gpu/processes/0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_performance_metrics_api(client):
    response = client.get("/api/gpu/performance")
    assert response.status_code == 200
    data = response.json()
    assert "matrix_gflops" in data
    assert "overall_speedup" in data
    assert "cache_hit_rate" in data
    assert "success_rate" in data


def test_gpu_history_api(client):
    response = client.get("/api/gpu/history/0?hours=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_gpu_stats_api(client):
    response = client.get("/api/gpu/stats/0?hours=24")
    assert response.status_code == 200
    data = response.json()
    assert "avg_utilization" in data
    assert "max_utilization" in data
    assert "avg_temperature" in data
    assert "max_temperature" in data
    assert "avg_gflops" in data
    assert "peak_gflops" in data


def test_optimization_recommendations_api(client):
    response = client.get("/api/gpu/recommendations?device_id=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_sse_stream_api(client):
    with client.stream("GET", "/api/gpu/stream/0") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        first_chunk = next(response.iter_bytes())
        assert b"data:" in first_chunk


def test_full_monitoring_flow(client):
    gpu_metrics = client.get("/api/gpu/metrics/0").json()
    perf_metrics = client.get("/api/gpu/performance").json()

    assert gpu_metrics["gpu_utilization"] >= 0
    assert perf_metrics["matrix_gflops"] >= 0

    stats = client.get("/api/gpu/stats/0?hours=1").json()
    assert "avg_utilization" in stats

    recommendations = client.get("/api/gpu/recommendations?device_id=0").json()
    assert isinstance(recommendations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
