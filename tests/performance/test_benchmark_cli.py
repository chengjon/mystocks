import json
from pathlib import Path

from tests.performance.benchmark import PerformanceBenchmark, load_endpoints, load_headers


def test_load_endpoints_reads_json_file(tmp_path: Path):
    endpoints_file = tmp_path / "endpoints.json"
    endpoints_file.write_text(json.dumps([{"endpoint": "/health", "method": "GET"}]), encoding="utf-8")

    endpoints = load_endpoints("http://localhost:8020", str(endpoints_file))

    assert endpoints == [{"endpoint": "/health", "method": "GET"}]


def test_load_headers_reads_json_file(tmp_path: Path):
    headers_file = tmp_path / "headers.json"
    headers_file.write_text(json.dumps({"Authorization": "Bearer token"}), encoding="utf-8")

    headers = load_headers(str(headers_file))

    assert headers == {"Authorization": "Bearer token"}


def test_generate_json_report_contains_summary():
    benchmark = PerformanceBenchmark("http://localhost:8020", concurrent_users=3, iterations=5)
    benchmark.results = {
        "/health": type("Result", (), {
            "endpoint": "/health",
            "method": "GET",
            "total_requests": 5,
            "successful_requests": 5,
            "failed_requests": 0,
            "avg_response_time": 0.01,
            "median_response_time": 0.01,
            "p95_response_time": 0.02,
            "p99_response_time": 0.02,
            "min_response_time": 0.009,
            "max_response_time": 0.021,
            "requests_per_second": 100.0,
            "error_rate": 0.0,
            "status_codes": {200: 5},
        })()
    }

    report = benchmark.generate_json_report()

    assert report["summary"]["endpoint_count"] == 1
    assert report["summary"]["overall_p95_ms"] == 20.0
    assert report["slo_status"]["compliant"] is True


def test_slo_status_fails_when_any_endpoint_exceeds_threshold():
    benchmark = PerformanceBenchmark("http://localhost:8020", concurrent_users=3, iterations=5)
    benchmark.results = {
        "/health": type("Result", (), {
            "endpoint": "/health",
            "method": "GET",
            "total_requests": 5,
            "successful_requests": 5,
            "failed_requests": 0,
            "avg_response_time": 0.1,
            "median_response_time": 0.1,
            "p95_response_time": 0.35,
            "p99_response_time": 0.35,
            "min_response_time": 0.09,
            "max_response_time": 0.36,
            "requests_per_second": 10.0,
            "error_rate": 0.0,
            "status_codes": {200: 5},
        })()
    }

    status = benchmark.get_slo_status()

    assert status["compliant"] is False
    assert any("Endpoints exceeding P95 target" in item for item in status["violations"])
