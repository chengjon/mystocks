import json
from pathlib import Path


def test_monitoring_auth_endpoints_are_read_only():
    path = Path("tests/performance/monitoring_auth_endpoints.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload
    assert all(item["method"] == "GET" for item in payload)
    assert {item["endpoint"] for item in payload} == {
        "/api/v1/monitoring/alert-rules",
        "/api/v1/monitoring/alerts",
    }
