from web.backend.app.core.middleware.performance import get_endpoint_name


def test_get_endpoint_name_preserves_static_health_ready_route():
    assert get_endpoint_name("/api/health/ready") == "/api/health/ready"


def test_get_endpoint_name_normalizes_numeric_resource_id():
    assert get_endpoint_name("/api/monitoring/alerts/123") == "/api/monitoring/alerts/{id}"


def test_get_endpoint_name_normalizes_uuid_resource_id():
    assert (
        get_endpoint_name("/api/tasks/550e8400-e29b-41d4-a716-446655440000")
        == "/api/tasks/{id}"
    )
