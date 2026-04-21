from scripts.dev.quality_gate.summarize_metrics_snapshot import build_snapshot


def test_build_snapshot_extracts_observability_summary():
    metrics_text = """
# HELP http_requests_total HTTP请求总数
http_requests_total{endpoint="/health",method="GET",status_code="200"} 21
http_requests_total{endpoint="/metrics",method="GET",status_code="200"} 5
# HELP slow_http_requests_total 慢请求计数(>300ms)
slow_http_requests_total{endpoint="/api/health/ready",method="GET"} 2
# HELP http_requests_active 当前活跃HTTP请求数
http_requests_active{endpoint="/health",method="GET"} 0
http_requests_active{endpoint="/metrics",method="GET"} 1
# HELP http_requests_in_progress 当前处理中的请求数
http_requests_in_progress{endpoint="/metrics",method="GET"} 1
# HELP mystocks_api_health_status API health status (1=healthy, 0=unhealthy)
mystocks_api_health_status{service="backend"} 1
mystocks_api_health_status{service="database"} 1
# HELP mystocks_db_connections_active Active database connections
mystocks_db_connections_active{database="postgresql"} 8
mystocks_db_connections_active{database="redis"} 1
# HELP mystocks_cache_hits_total Total cache hits
mystocks_cache_hits_total 10
# HELP mystocks_cache_misses_total Total cache misses
mystocks_cache_misses_total 5
process_resident_memory_bytes 123456
process_cpu_seconds_total 8.5
""".strip()
    health_payload = {"status": "healthy", "timestamp": 1, "version": "1.0.0"}

    baseline_metrics_text = """
# HELP http_requests_total HTTP请求总数
http_requests_total{endpoint="/health",method="GET",status_code="200"} 20
http_requests_total{endpoint="/metrics",method="GET",status_code="200"} 4
# HELP slow_http_requests_total 慢请求计数(>300ms)
slow_http_requests_total{endpoint="/api/health/ready",method="GET"} 1
""".strip()

    snapshot = build_snapshot(metrics_text, health_payload, baseline_metrics_text=baseline_metrics_text)

    assert snapshot["metrics_health"]["status"] == "healthy"
    prometheus = snapshot["prometheus_snapshot"]
    assert prometheus["http_requests_total"] == 26.0
    assert prometheus["http_requests_total_delta"] == 2.0
    assert prometheus["slow_http_requests_total"] == 2.0
    assert prometheus["slow_http_requests_total_delta"] == 1.0
    assert prometheus["active_requests_max"] == 1.0
    assert prometheus["requests_in_progress_max"] == 1.0
    assert prometheus["cache_hits_total"] == 10.0
    assert prometheus["cache_misses_total"] == 5.0
    assert prometheus["cache_hit_ratio"] == 0.6667
    assert prometheus["slow_request_endpoints"] == [
        {"endpoint": "/api/health/ready", "method": "GET", "count": 2.0}
    ]
    assert prometheus["slow_request_endpoints_delta"] == [
        {"endpoint": "/api/health/ready", "method": "GET", "count": 1.0}
    ]
    assert prometheus["api_health_status"]["backend"] == 1.0
    assert prometheus["db_connections_active"]["postgresql"] == 8.0
