from __future__ import annotations

import warnings

from fastapi.routing import APIRoute

from app.main import app


def _matching_routes(path: str, method: str = "GET") -> list[APIRoute]:
    normalized_method = method.upper()
    return [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == path
        and normalized_method in (route.methods or set())
    ]


def test_health_routes_are_unique_and_domain_scoped() -> None:
    api_health_routes = _matching_routes("/api/health")
    signal_health_routes = _matching_routes("/api/signals/health")
    metrics_health_routes = _matching_routes("/api/metrics/health")

    assert len(api_health_routes) == 1
    assert len(signal_health_routes) == 1
    assert len(metrics_health_routes) == 1

    app.openapi_schema = None
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        schema = app.openapi()

    duplicate_warnings = [
        str(item.message)
        for item in captured
        if "Duplicate Operation ID" in str(item.message)
    ]

    assert not duplicate_warnings
    assert "/api/health" in schema["paths"]
    assert "/api/signals/health" in schema["paths"]
    assert "/api/metrics/health" in schema["paths"]


def test_root_and_socketio_status_have_documented_examples_and_errors() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/", "/api/socketio-status"]:
        operation = schema["paths"][path]["get"]
        responses = operation["responses"]
        success_json = responses["200"]["content"]["application/json"]

        assert operation.get("tags")
        assert len(operation.get("description", "")) >= 20
        assert "example" in success_json or "examples" in success_json
        assert any(status.startswith("5") for status in responses)


def test_health_and_csrf_endpoints_have_tags_examples_and_error_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    csrf_operation = schema["paths"]["/api/csrf-token"]["get"]
    csrf_responses = csrf_operation["responses"]
    csrf_success_json = csrf_responses["200"]["content"]["application/json"]

    assert csrf_operation.get("tags")
    assert len(csrf_operation.get("description", "")) >= 20
    assert "example" in csrf_success_json or "examples" in csrf_success_json
    assert any(status.startswith("5") for status in csrf_responses)

    health_operation = schema["paths"]["/health"]["get"]
    health_responses = health_operation["responses"]

    assert len(health_operation.get("description", "")) >= 20
    assert any(status.startswith("5") for status in health_responses)


def test_prometheus_exporter_endpoints_have_error_docs_and_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    metrics_operation = schema["paths"]["/metrics"]["get"]
    assert metrics_operation.get("tags")
    assert any(status.startswith("5") for status in metrics_operation["responses"])

    for path in ["/metrics/health", "/metrics/list"]:
        operation = schema["paths"][path]["get"]
        responses = operation["responses"]
        success_json = responses["200"]["content"]["application/json"]

        assert operation.get("tags")
        assert "example" in success_json or "examples" in success_json
        assert any(status.startswith("5") for status in responses)


def test_gpu_monitoring_endpoints_have_parameter_docs_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/gpu/status", "/api/gpu/performance"]:
        operation = schema["paths"][path]["get"]
        responses = operation["responses"]
        success_json = responses["200"]["content"]["application/json"]
        parameters = operation.get("parameters", [])

        assert any(param["name"] == "device_id" and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(status.startswith("5") for status in responses)

    metrics_operation = schema["paths"]["/api/gpu/metrics"]["get"]
    assert any(status.startswith("5") for status in metrics_operation["responses"])


def test_governance_dashboard_endpoints_have_parameter_docs_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/v1/governance/quality/overview", "/api/v1/governance/dashboard/summary"]:
        operation = schema["paths"][path]["get"]
        assert any(status.startswith("5") for status in operation["responses"])

    expected_parameters = {
        "/api/v1/governance/lineage/stats": {"days"},
        "/api/v1/governance/assets/catalog": {"page", "page_size", "asset_type"},
        "/api/v1/governance/compliance/metrics": {"days", "limit"},
    }

    for path, parameter_names in expected_parameters.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])

        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_v1_health_endpoints_have_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/v1/health/database", "/api/v1/health/classification/stats"]:
        operation = schema["paths"][path]["get"]
        assert any(status.startswith("5") for status in operation["responses"])


def test_v1_system_settings_endpoints_have_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/v1/system/settings/general", "/api/v1/system/settings/security"]:
        get_operation = schema["paths"][path]["get"]
        post_operation = schema["paths"][path]["post"]

        assert len(get_operation.get("description", "")) >= 20
        assert any(status.startswith("5") for status in get_operation["responses"])
        get_success_content = get_operation["responses"]["200"]["content"]["application/json"]
        assert "example" in get_success_content or "examples" in get_success_content
        assert len(post_operation.get("description", "")) >= 20
        assert any(status.startswith("5") for status in post_operation["responses"])
        post_success_content = post_operation["responses"]["200"]["content"]["application/json"]
        assert "example" in post_success_content or "examples" in post_success_content

        post_json = post_operation["requestBody"]["content"]["application/json"]
        assert "example" in post_json or "examples" in post_json


def test_notification_endpoints_have_error_docs_and_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/notification/status", "/api/notification/test-email"]:
        operation = schema["paths"][path]["post" if path.endswith("test-email") else "get"]
        success_json = operation["responses"]["200"]["content"]["application/json"]
        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in success_json or "examples" in success_json
        assert any(status.startswith("5") for status in operation["responses"])

    get_preferences = schema["paths"]["/api/notification/preferences"]["get"]
    post_preferences = schema["paths"]["/api/notification/preferences"]["post"]
    get_preferences_success_json = get_preferences["responses"]["200"]["content"]["application/json"]

    assert len(get_preferences.get("description", "")) >= 20
    assert "example" in get_preferences_success_json or "examples" in get_preferences_success_json
    assert any(status.startswith("5") for status in get_preferences["responses"])
    assert len(post_preferences.get("description", "")) >= 20
    assert any(status.startswith("5") for status in post_preferences["responses"])

    for path in [
        "/api/notification/email/send",
        "/api/notification/email/welcome",
        "/api/notification/email/newsletter",
        "/api/notification/email/price-alert",
        "/api/notification/preferences",
    ]:
        operation = schema["paths"][path]["post"]
        json_content = operation["requestBody"]["content"]["application/json"]
        assert "example" in json_content or "examples" in json_content

    for path in ["/api/notification/email/newsletter", "/api/notification/email/price-alert"]:
        operation = schema["paths"][path]["post"]
        assert len(operation.get("description", "")) >= 20


def test_contract_management_endpoints_have_examples_and_error_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/contracts/versions",
        "/api/contracts/diff",
        "/api/contracts/validate",
        "/api/contracts/sync",
    ]:
        operation = schema["paths"][path]["post"]
        json_content = operation["requestBody"]["content"]["application/json"]
        assert "example" in json_content or "examples" in json_content

    sync_report = schema["paths"]["/api/contracts/sync/report"]["get"]
    assert any(status.startswith("5") for status in sync_report["responses"])

    versions_get = schema["paths"]["/api/contracts/versions"]["get"]
    assert len(versions_get.get("description", "")) >= 20
    for parameter_name in ["name", "limit", "offset"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in versions_get["parameters"])

    version_get = schema["paths"]["/api/contracts/versions/{version_id}"]["get"]
    assert len(version_get.get("description", "")) >= 20
    assert any(param["name"] == "version_id" and param.get("description") for param in version_get["parameters"])

    active_get = schema["paths"]["/api/contracts/versions/{name}/active"]["get"]
    assert len(active_get.get("description", "")) >= 20
    assert any(param["name"] == "name" and param.get("description") for param in active_get["parameters"])

    version_put = schema["paths"]["/api/contracts/versions/{version_id}"]["put"]
    put_json = version_put["requestBody"]["content"]["application/json"]
    assert len(version_put.get("description", "")) >= 20
    assert any(param["name"] == "version_id" and param.get("description") for param in version_put["parameters"])
    assert "example" in put_json or "examples" in put_json

    activate_post = schema["paths"]["/api/contracts/versions/{version_id}/activate"]["post"]
    assert len(activate_post.get("description", "")) >= 20
    assert any(param["name"] == "version_id" and param.get("description") for param in activate_post["parameters"])

    delete_operation = schema["paths"]["/api/contracts/versions/{version_id}"]["delete"]
    assert len(delete_operation.get("description", "")) >= 20
    assert any(param["name"] == "version_id" and param.get("description") for param in delete_operation["parameters"])

    contracts_get = schema["paths"]["/api/contracts/contracts"]["get"]
    assert len(contracts_get.get("description", "")) >= 20
    assert any(status.startswith("5") for status in contracts_get["responses"])


def test_contract_read_and_control_endpoints_have_success_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/contracts/versions", "get"): {"name", "limit", "offset"},
        ("/api/contracts/versions/{version_id}", "get"): {"version_id"},
        ("/api/contracts/versions/{name}/active", "get"): {"name"},
        ("/api/contracts/versions/{version_id}/activate", "post"): {"version_id"},
        ("/api/contracts/versions/{version_id}", "delete"): {"version_id"},
        ("/api/contracts/contracts", "get"): set(),
        ("/api/contracts/sync/report", "get"): set(),
    }

    for (path, method), expected_params in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_code = next(code for code in operation["responses"] if code.startswith("2"))
        success_json = operation["responses"][success_code]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_pool_monitoring_endpoints_have_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/pool-monitoring/postgresql/stats",
        "/api/pool-monitoring/tdengine/stats",
        "/api/pool-monitoring/health",
        "/api/pool-monitoring/alerts",
    ]:
        operation = schema["paths"][path]["get"]
        assert any(status.startswith("5") for status in operation["responses"])


def test_metrics_endpoints_have_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method in [
        ("/api/status", "get"),
        ("/api/basic", "get"),
        ("/api/performance", "get"),
        ("/api/detailed", "get"),
        ("/api/reset", "post"),
    ]:
        operation = schema["paths"][path][method]
        assert any(status.startswith("5") for status in operation["responses"])


def test_system_management_endpoints_have_error_docs_and_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/system/health",
        "/api/v1/system/adapters/health",
        "/api/v1/system/datasources",
        "/api/v1/system/logs",
        "/api/v1/system/logs/summary",
    ]:
        operation = schema["paths"][path]["get"]
        assert any(status.startswith("5") for status in operation["responses"])
        success_content = operation["responses"]["200"]["content"]["application/json"]
        assert "example" in success_content or "examples" in success_content

    test_connection = schema["paths"]["/api/v1/system/test-connection"]["post"]
    assert any(status.startswith("5") for status in test_connection["responses"])
    json_content = test_connection["requestBody"]["content"]["application/json"]
    success_content = test_connection["responses"]["200"]["content"]["application/json"]
    assert "example" in json_content or "examples" in json_content
    assert "example" in success_content or "examples" in success_content


def test_announcement_endpoints_have_examples_parameter_docs_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/announcement/announcement/health",
        "/api/v1/announcement/announcement/status",
    ]:
        operation = schema["paths"][path]["get"]
        assert len(operation.get("description", "")) >= 20
        assert any(status.startswith("5") for status in operation["responses"])

    analyze_operation = schema["paths"]["/api/v1/announcement/announcement/analyze"]["post"]
    analyze_json = analyze_operation["requestBody"]["content"]["application/json"]
    assert len(analyze_operation.get("description", "")) >= 20
    assert "example" in analyze_json or "examples" in analyze_json

    stats_operation = schema["paths"]["/api/v1/announcement/announcement/stats"]["get"]
    assert any(status.startswith("5") for status in stats_operation["responses"])

    monitor_rules_get = schema["paths"]["/api/v1/announcement/announcement/monitor-rules"]["get"]
    assert any(status.startswith("5") for status in monitor_rules_get["responses"])

    monitor_rules_post = schema["paths"]["/api/v1/announcement/announcement/monitor-rules"]["post"]
    monitor_rules_post_json = monitor_rules_post["requestBody"]["content"]["application/json"]
    assert "example" in monitor_rules_post_json or "examples" in monitor_rules_post_json

    update_operation = schema["paths"]["/api/v1/announcement/announcement/monitor-rules/{rule_id}"]["put"]
    update_json = update_operation["requestBody"]["content"]["application/json"]
    assert any(param["name"] == "rule_id" and param.get("description") for param in update_operation["parameters"])
    assert "example" in update_json or "examples" in update_json

    delete_operation = schema["paths"]["/api/v1/announcement/announcement/monitor-rules/{rule_id}"]["delete"]
    assert any(param["name"] == "rule_id" and param.get("description") for param in delete_operation["parameters"])

    evaluate_operation = schema["paths"]["/api/v1/announcement/announcement/monitor/evaluate"]["post"]
    assert any(status.startswith("5") for status in evaluate_operation["responses"])


def test_signal_history_endpoint_has_query_parameter_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/signals/history"]["get"]
    parameters = operation.get("parameters", [])

    for parameter_name in [
        "strategy_id",
        "symbol",
        "signal_type",
        "status",
        "start_date",
        "end_date",
        "limit",
        "offset",
    ]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_monitoring_alerts_endpoint_has_query_parameter_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/monitoring/alerts"]["get"]
    parameters = operation.get("parameters", [])

    for parameter_name in [
        "symbol",
        "alert_type",
        "alert_level",
        "is_read",
        "start_date",
        "end_date",
        "limit",
        "offset",
    ]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_kline_data_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/v1/data/stocks/daily": {"symbol", "start_date", "end_date", "limit"},
        "/api/v1/data/kline": {"symbol", "start_date", "end_date", "limit"},
        "/api/v1/data/stocks/kline": {"symbol", "start_date", "end_date", "period"},
        "/api/v1/data/stocks/intraday": {"symbol", "date"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_financial_data_endpoint_has_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/data/financial"]["get"]
    parameters = operation.get("parameters", [])
    success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
        "content"
    ]["application/json"]

    assert operation.get("summary")
    assert len(operation.get("description", "")) >= 20
    for parameter_name in ["symbol", "report_type", "period", "limit"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
    assert "example" in success_json or "examples" in success_json
    assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_dragon_tiger_data_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, expected_params in [
        ("/api/v1/data/dragon-tiger/detail", ["start_date", "end_date", "limit"]),
        ("/api/v1/data/dragon-tiger/institution-stats", ["period", "limit"]),
    ]:
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_futures_index_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/v1/data/futures/index/daily": {"symbol", "start_date", "end_date"},
        "/api/v1/data/futures/index/realtime": {"symbol"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_cache_data_endpoints_have_descriptions_examples_and_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    get_operation = schema["paths"]["/api/cache/{symbol}/{data_type}"]["get"]
    get_parameters = get_operation.get("parameters", [])
    assert len(get_operation.get("description", "")) >= 20
    for parameter_name in ["symbol", "data_type", "timeframe"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in get_parameters)

    post_operation = schema["paths"]["/api/cache/{symbol}/{data_type}"]["post"]
    post_parameters = post_operation.get("parameters", [])
    post_json = post_operation["requestBody"]["content"]["application/json"]
    assert len(post_operation.get("description", "")) >= 20
    for parameter_name in ["symbol", "data_type", "timeframe", "ttl_days"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in post_parameters)
    assert "example" in post_json or "examples" in post_json

    fresh_operation = schema["paths"]["/api/cache/{symbol}/{data_type}/fresh"]["get"]
    fresh_parameters = fresh_operation.get("parameters", [])
    assert len(fresh_operation.get("description", "")) >= 20
    for parameter_name in ["symbol", "data_type", "max_age_days"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in fresh_parameters)


def test_cache_management_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params in [
        ("/api/cache", "delete", ["confirm"]),
        ("/api/cache/status", "get", []),
        ("/api/cache/{symbol}", "delete", ["symbol"]),
        ("/api/cache/evict/manual", "post", []),
        ("/api/cache/eviction/stats", "get", []),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_cache_prewarming_and_monitoring_endpoints_have_descriptions_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method in [
        ("/api/cache/prewarming/trigger", "post"),
        ("/api/cache/prewarming/status", "get"),
        ("/api/cache/monitoring/metrics", "get"),
        ("/api/cache/monitoring/health", "get"),
    ]:
        operation = schema["paths"][path][method]
        success_json = operation["responses"]["200"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_indicator_cache_statistics_endpoint_has_description_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/indicators/cache/stats"]["get"]
    success_json = operation["responses"]["200"]["content"]["application/json"]

    assert operation.get("summary")
    assert len(operation.get("description", "")) >= 20
    assert "example" in success_json or "examples" in success_json
    assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_v1_indicator_endpoints_have_examples_parameter_docs_and_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    registry_operation = schema["paths"]["/api/v1/indicators/registry/{category}"]["get"]
    registry_parameters = registry_operation.get("parameters", [])

    assert registry_operation.get("summary")
    assert len(registry_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "category" and param["in"] == "path" and param.get("description")
        for param in registry_parameters
    )
    assert any(code.startswith(("4", "5")) for code in registry_operation["responses"])

    for path in ["/api/v1/indicators/calculate", "/api/v1/indicators/calculate/batch"]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])

    clear_cache_operation = schema["paths"]["/api/v1/indicators/cache/clear"]["post"]
    clear_cache_parameters = clear_cache_operation.get("parameters", [])

    assert clear_cache_operation.get("summary")
    assert len(clear_cache_operation.get("description", "")) >= 20
    assert any(param["name"] == "pattern" and param.get("description") for param in clear_cache_parameters)
    assert any(code.startswith(("4", "5")) for code in clear_cache_operation["responses"])


def test_tdx_and_metrics_endpoints_have_parameter_docs_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    quote_operation = schema["paths"]["/api/v1/tdx/quote/{symbol}"]["get"]
    quote_parameters = quote_operation.get("parameters", [])

    assert quote_operation.get("summary")
    assert len(quote_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "symbol" and param["in"] == "path" and param.get("description")
        for param in quote_parameters
    )
    assert any(code.startswith(("4", "5")) for code in quote_operation["responses"])

    index_kline_operation = schema["paths"]["/api/v1/tdx/index/kline"]["get"]
    assert index_kline_operation.get("summary")
    assert len(index_kline_operation.get("description", "")) >= 20
    assert any(code.startswith(("4", "5")) for code in index_kline_operation["responses"])

    metrics_operation = schema["paths"]["/api/metrics"]["get"]
    metrics_success_content = metrics_operation["responses"]["200"]["content"]
    assert "text/plain" in metrics_success_content
    assert "example" in metrics_success_content["text/plain"] or "examples" in metrics_success_content["text/plain"]
    assert any(code.startswith(("4", "5")) for code in metrics_operation["responses"])


def test_ml_endpoints_have_request_examples_and_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    market_operation = schema["paths"]["/api/ml/tdx/stocks/{market}"]["get"]
    market_parameters = market_operation.get("parameters", [])

    assert market_operation.get("summary")
    assert len(market_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "market" and param["in"] == "path" and param.get("description")
        for param in market_parameters
    )
    assert any(code.startswith(("4", "5")) for code in market_operation["responses"])

    for path in [
        "/api/ml/tdx/data",
        "/api/ml/features/generate",
        "/api/ml/models/train",
        "/api/ml/models/predict",
        "/api/ml/models/hyperparameter-search",
        "/api/ml/models/evaluate",
    ]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_multi_source_endpoints_have_descriptions_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/multi-source/health", "/api/multi-source/status"]:
        operation = schema["paths"][path]["get"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert any(code.startswith(("4", "5")) for code in operation["responses"])

    analyze_operation = schema["paths"]["/api/multi-source/analyze"]["post"]
    analyze_json = analyze_operation["requestBody"]["content"]["application/json"]

    assert analyze_operation.get("summary")
    assert len(analyze_operation.get("description", "")) >= 20
    assert "example" in analyze_json or "examples" in analyze_json
    assert any(code.startswith(("4", "5")) for code in analyze_operation["responses"])


def test_data_quality_overview_endpoints_have_descriptions_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/data-quality/alerts",
        "/api/data-quality/metrics",
        "/api/data-quality/metrics/trends",
    ]:
        operation = schema["paths"][path]["get"]
        success_json = operation["responses"]["200"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_realtime_quote_endpoints_have_descriptions_examples_and_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    quote_operation = schema["paths"]["/api/api/realtime/quote/{symbol}"]["get"]
    quote_parameters = quote_operation.get("parameters", [])
    quote_success_json = quote_operation["responses"]["200"]["content"]["application/json"]

    assert quote_operation.get("summary")
    assert len(quote_operation.get("description", "")) >= 20
    assert any(param["name"] == "symbol" and param.get("description") for param in quote_parameters)
    assert "example" in quote_success_json or "examples" in quote_success_json
    assert any(code.startswith(("4", "5")) for code in quote_operation["responses"])

    quotes_operation = schema["paths"]["/api/api/realtime/quotes"]["get"]
    quotes_success_json = quotes_operation["responses"]["200"]["content"]["application/json"]

    assert quotes_operation.get("summary")
    assert len(quotes_operation.get("description", "")) >= 20
    assert "example" in quotes_success_json or "examples" in quotes_success_json
    assert any(code.startswith(("4", "5")) for code in quotes_operation["responses"])


def test_indicator_registry_endpoints_have_request_examples_and_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    calculate_operation = schema["paths"]["/api/indicator-registry/calculate"]["post"]
    calculate_json = calculate_operation["requestBody"]["content"]["application/json"]

    assert calculate_operation.get("summary")
    assert len(calculate_operation.get("description", "")) >= 20
    assert "example" in calculate_json or "examples" in calculate_json

    detail_operation = schema["paths"]["/api/indicator-registry/indicators/{indicator_id}"]["get"]
    detail_parameters = detail_operation.get("parameters", [])

    assert detail_operation.get("summary")
    assert len(detail_operation.get("description", "")) >= 20
    assert any(param["name"] == "indicator_id" and param.get("description") for param in detail_parameters)


def test_sentiment_and_technical_pattern_endpoints_have_docs_examples_and_parameter_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    sentiment_operation = schema["paths"]["/api/v1/sentiment/stock/{symbol}"]["get"]
    sentiment_parameters = sentiment_operation.get("parameters", [])
    sentiment_success_json = sentiment_operation["responses"]["200"]["content"]["application/json"]

    assert sentiment_operation.get("summary")
    assert len(sentiment_operation.get("description", "")) >= 20
    for parameter_name in ["symbol", "days"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in sentiment_parameters)
    assert "example" in sentiment_success_json or "examples" in sentiment_success_json
    assert any(code.startswith(("4", "5")) for code in sentiment_operation["responses"])

    patterns_operation = schema["paths"]["/api/v1/technical/patterns/{symbol}"]["get"]
    patterns_parameters = patterns_operation.get("parameters", [])
    patterns_success_json = patterns_operation["responses"]["200"]["content"]["application/json"]

    assert patterns_operation.get("summary")
    assert len(patterns_operation.get("description", "")) >= 20
    for parameter_name in ["symbol", "period"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in patterns_parameters)
    assert "example" in patterns_success_json or "examples" in patterns_success_json
    assert any(code.startswith(("4", "5")) for code in patterns_operation["responses"])


def test_audit_endpoints_have_parameter_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    logs_operation = schema["paths"]["/api/v1/audit/logs"]["get"]
    logs_success_json = logs_operation["responses"]["200"]["content"]["application/json"]
    assert logs_operation.get("summary")
    assert len(logs_operation.get("description", "")) >= 20
    for parameter_name in ["user_id", "action", "resource_type", "start_date", "end_date", "limit"]:
        assert any(
            param["name"] == parameter_name and param.get("description")
            for param in logs_operation.get("parameters", [])
        )
    assert "example" in logs_success_json or "examples" in logs_success_json
    assert any(code.startswith(("4", "5")) for code in logs_operation["responses"])

    log_detail_operation = schema["paths"]["/api/v1/audit/logs/{log_id}"]["get"]
    log_detail_success_json = log_detail_operation["responses"]["200"]["content"]["application/json"]
    assert log_detail_operation.get("summary")
    assert len(log_detail_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "log_id" and param.get("description")
        for param in log_detail_operation.get("parameters", [])
    )
    assert "example" in log_detail_success_json or "examples" in log_detail_success_json
    assert any(code.startswith(("4", "5")) for code in log_detail_operation["responses"])

    statistics_operation = schema["paths"]["/api/v1/audit/statistics"]["get"]
    statistics_success_json = statistics_operation["responses"]["200"]["content"]["application/json"]
    assert statistics_operation.get("summary")
    assert len(statistics_operation.get("description", "")) >= 20
    for parameter_name in ["start_date", "end_date"]:
        assert any(
            param["name"] == parameter_name and param.get("description")
            for param in statistics_operation.get("parameters", [])
        )
    assert "example" in statistics_success_json or "examples" in statistics_success_json
    assert any(code.startswith(("4", "5")) for code in statistics_operation["responses"])


def test_positions_endpoints_have_examples_parameter_docs_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/v1/positions", "get"): {"symbol", "session_id"},
        ("/api/v1/positions/{position_id}", "get"): {"position_id"},
        ("/api/v1/positions/{position_id}", "delete"): {"position_id"},
    }

    for (path, method), parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_backtest_results_endpoint_has_description_and_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/strategy/backtest/results"]["get"]
    parameters = operation.get("parameters", [])

    assert len(operation.get("description", "")) >= 20
    for parameter_name in ["strategy_id", "page", "page_size"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_risk_metrics_history_endpoint_has_description_and_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/risk/metrics/history"]["get"]
    parameters = operation.get("parameters", [])

    assert len(operation.get("description", "")) >= 20
    for parameter_name in ["entity_type", "entity_id", "start_date", "end_date"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_ml_model_management_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    list_operation = schema["paths"]["/api/ml/models"]["get"]
    list_success_json = list_operation["responses"]["200"]["content"]["application/json"]

    assert list_operation.get("summary")
    assert len(list_operation.get("description", "")) >= 20
    assert "example" in list_success_json or "examples" in list_success_json
    assert any(code.startswith(("4", "5")) for code in list_operation["responses"])

    detail_operation = schema["paths"]["/api/ml/models/{model_name}"]["get"]
    detail_parameters = detail_operation.get("parameters", [])
    detail_success_json = detail_operation["responses"]["200"]["content"]["application/json"]

    assert detail_operation.get("summary")
    assert len(detail_operation.get("description", "")) >= 20
    assert any(param["name"] == "model_name" and param.get("description") for param in detail_parameters)
    assert "example" in detail_success_json or "examples" in detail_success_json
    assert any(code.startswith(("4", "5")) for code in detail_operation["responses"])


def test_data_source_rollback_endpoint_has_description_parameter_docs_and_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/data-sources/config/{endpoint_name}/rollback/{version}"]["post"]
    parameters = operation.get("parameters", [])
    request_json = operation["requestBody"]["content"]["application/json"]

    assert len(operation.get("description", "")) >= 20
    for parameter_name in ["endpoint_name", "version"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
    assert "example" in request_json or "examples" in request_json


def test_monitoring_dragon_tiger_endpoint_has_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/monitoring/dragon-tiger"]["get"]
    parameters = operation.get("parameters", [])

    assert len(operation.get("description", "")) >= 20
    for parameter_name in ["trade_date", "symbol", "min_net_amount", "limit"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_monitoring_realtime_control_and_summary_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/v1/monitoring/realtime/{symbol}", "get"): {
            "parameters": {"symbol"},
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/realtime", "get"): {
            "parameters": {"symbols", "limit", "is_limit_up", "is_limit_down"},
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/realtime/fetch", "post"): {
            "parameters": set(),
            "requires_request_example": True,
        },
        ("/api/v1/monitoring/dragon-tiger/fetch", "post"): {
            "parameters": {"trade_date"},
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/analyze", "get"): {
            "parameters": set(),
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/summary", "get"): {
            "parameters": set(),
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/stats/today", "get"): {
            "parameters": set(),
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/control/start", "post"): {
            "parameters": set(),
            "requires_request_example": True,
        },
        ("/api/v1/monitoring/control/stop", "post"): {
            "parameters": set(),
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/control/status", "get"): {
            "parameters": set(),
            "requires_request_example": False,
        },
    }

    for (path, method), expectation in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expectation["parameters"]:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        if expectation["requires_request_example"]:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_realtime_mtm_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/api/mtm/portfolio/{portfolio_id}": {"portfolio_id"},
        "/api/api/mtm/position/{position_id}": {"position_id"},
        "/api/api/mtm/stats": set(),
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_margin_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/v1/data/margin/account-info": set(),
        "/api/v1/data/margin/detail/sse": {"date"},
        "/api/v1/data/margin/detail/szse": {"date"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_tdx_read_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/v1/tdx/health": set(),
        "/api/v1/tdx/quote/{symbol}": {"symbol"},
        "/api/v1/tdx/kline": {"symbol", "period"},
        "/api/v1/tdx/index/kline": {"symbol", "period"},
        "/api/v1/tdx/index/quote/{symbol}": {"symbol"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_lineage_upstream_and_downstream_endpoints_have_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/v1/lineage/{node_id}/upstream", "/api/v1/lineage/{node_id}/downstream"]:
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])

        assert len(operation.get("description", "")) >= 20
        for parameter_name in ["node_id", "max_depth"]:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_data_source_versions_endpoint_has_parameter_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/data-sources/config/{endpoint_name}/versions"]["get"]
    parameters = operation.get("parameters", [])

    assert len(operation.get("description", "")) >= 20
    for parameter_name in ["endpoint_name", "limit"]:
        assert any(param["name"] == parameter_name and param.get("description") for param in parameters)


def test_data_source_registry_read_endpoints_have_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/v1/data-sources/": {"data_category", "classification_level", "source_type", "only_healthy", "keyword", "status"},
        "/api/v1/data-sources/categories": set(),
        "/api/v1/data-sources/{endpoint_name}": {"endpoint_name"},
        "/api/v1/data-sources/{endpoint_name}/health-check": {"endpoint_name", "Authorization"},
        "/api/v1/data-sources/health-check/all": {"Authorization"},
    }

    for path, expected_params in endpoint_expectations.items():
        operation = schema["paths"][path]["get" if path.endswith("/") or "health-check" not in path else "post"]
        parameters = operation.get("parameters", [])
        success_code = next(code for code in operation["responses"] if code.startswith("2"))
        success_json = operation["responses"][success_code]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_data_source_item_crud_endpoints_have_path_and_auth_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    get_operation = schema["paths"]["/api/v1/data-sources/config/{endpoint_name}"]["get"]
    assert len(get_operation.get("description", "")) >= 20
    assert any(param["name"] == "endpoint_name" and param.get("description") for param in get_operation["parameters"])

    for method in ["put", "delete"]:
        operation = schema["paths"]["/api/v1/data-sources/config/{endpoint_name}"][method]
        parameters = operation.get("parameters", [])

        assert len(operation.get("description", "")) >= 20
        assert any(param["name"] == "endpoint_name" and param.get("description") for param in parameters)
        assert any(param["name"] == "Authorization" and param.get("description") for param in parameters)


def test_data_source_config_read_endpoints_have_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params in [
        ("/api/v1/data-sources/config/", "get", {"data_category", "source_type", "status"}),
        ("/api/v1/data-sources/config/{endpoint_name}", "get", {"endpoint_name"}),
        ("/api/v1/data-sources/config/{endpoint_name}", "delete", {"endpoint_name", "Authorization"}),
        ("/api/v1/data-sources/config/{endpoint_name}/versions", "get", {"endpoint_name", "limit"}),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_code = next(code for code in operation["responses"] if code.startswith("2"))
        success_json = operation["responses"][success_code]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_data_source_write_endpoints_have_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method in [
        ("/api/v1/data-sources/config/", "post"),
        ("/api/v1/data-sources/config/{endpoint_name}", "put"),
        ("/api/v1/data-sources/config/batch", "post"),
        ("/api/v1/data-sources/config/reload", "post"),
    ]:
        operation = schema["paths"][path][method]
        request_json = operation["requestBody"]["content"]["application/json"]
        assert "example" in request_json or "examples" in request_json


def test_risk_metric_write_endpoints_have_descriptions_and_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/risk/var-cvar",
        "/api/v1/risk/beta",
        "/api/v1/risk/metrics/calculate",
    ]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json


def test_risk_alert_update_and_acknowledge_endpoints_have_docs_and_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method in [
        ("/api/v1/risk/alerts/{alert_id}", "put"),
        ("/api/v1/risk/v31/alerts/{alert_id}/acknowledge", "post"),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert any(param["name"] == "alert_id" and param.get("description") for param in parameters)
        assert "example" in request_json or "examples" in request_json


def test_task_start_endpoint_has_docs_and_request_example() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/tasks/{task_id}/start"]["post"]
    parameters = operation.get("parameters", [])
    request_json = operation["requestBody"]["content"]["application/json"]

    assert len(operation.get("description", "")) >= 20
    assert any(param["name"] == "task_id" and param.get("description") for param in parameters)
    assert "example" in request_json or "examples" in request_json


def test_strategy_update_endpoint_has_docs_and_request_example() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/strategy/strategies/{strategy_id}"]["put"]
    parameters = operation.get("parameters", [])
    request_json = operation["requestBody"]["content"]["application/json"]

    assert len(operation.get("description", "")) >= 20
    assert any(param["name"] == "strategy_id" and param.get("description") for param in parameters)
    assert "example" in request_json or "examples" in request_json


def test_risk_v31_broadcast_endpoint_has_docs_and_request_example() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/risk/v31/ws/broadcast/{topic}"]["post"]
    parameters = operation.get("parameters", [])
    request_json = operation["requestBody"]["content"]["application/json"]

    assert len(operation.get("description", "")) >= 20
    assert any(param["name"] == "topic" and param.get("description") for param in parameters)
    assert "example" in request_json or "examples" in request_json


def test_trading_runtime_add_strategy_endpoint_has_docs_and_request_example() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    operation = schema["paths"]["/api/trading/strategies/add"]["post"]
    parameters = operation.get("parameters", [])
    request_json = operation["requestBody"]["content"]["application/json"]

    assert len(operation.get("description", "")) >= 20
    assert any(param["name"] == "Authorization" and param.get("description") for param in parameters)
    assert "example" in request_json or "examples" in request_json


def test_strategy_mgmt_write_endpoints_have_docs_and_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method in [
        ("/api/strategy-mgmt/strategies", "post"),
        ("/api/strategy-mgmt/strategies/{strategy_id}", "put"),
        ("/api/strategy-mgmt/backtest/execute", "post"),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert any(param["name"] == "Authorization" and param.get("description") for param in parameters)
        assert "example" in request_json or "examples" in request_json


def test_strategy_mgmt_legacy_endpoints_have_success_examples_and_error_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params, expects_success_example in [
        ("/api/strategy-mgmt/strategies", "post", ["Authorization"], True),
        ("/api/strategy-mgmt/strategies", "get", ["user_id", "status", "page", "page_size"], True),
        ("/api/strategy-mgmt/strategies/{strategy_id}", "get", ["strategy_id"], True),
        ("/api/strategy-mgmt/strategies/{strategy_id}", "put", ["strategy_id", "Authorization"], True),
        ("/api/strategy-mgmt/strategies/{strategy_id}", "delete", ["strategy_id", "Authorization"], False),
        ("/api/strategy-mgmt/backtest/execute", "post", ["Authorization"], True),
        ("/api/strategy-mgmt/backtest/results/{backtest_id}", "get", ["backtest_id"], True),
        ("/api/strategy-mgmt/backtest/results", "get", ["user_id", "strategy_id", "page", "page_size"], True),
        ("/api/strategy-mgmt/health", "get", [], True),
        ("/api/strategy-mgmt/backtest/status/{backtest_id}", "get", ["backtest_id"], True),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)

        if expects_success_example:
            success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
                "content"
            ]["application/json"]
            assert "example" in success_json or "examples" in success_json

        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_trading_runtime_session_and_delete_endpoints_have_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/trading/start", "/api/trading/stop"]:
        operation = schema["paths"][path]["post"]
        parameters = operation.get("parameters", [])

        assert len(operation.get("description", "")) >= 20
        assert any(param["name"] == "Authorization" and param.get("description") for param in parameters)

    delete_operation = schema["paths"]["/api/trading/strategies/{strategy_name}"]["delete"]
    delete_parameters = delete_operation.get("parameters", [])

    assert len(delete_operation.get("description", "")) >= 20
    assert any(param["name"] == "strategy_name" and param.get("description") for param in delete_parameters)
    assert any(param["name"] == "Authorization" and param.get("description") for param in delete_parameters)


def test_trading_runtime_read_endpoints_have_success_examples_and_error_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/trading/status",
        "/api/trading/strategies/performance",
        "/api/trading/market/snapshot",
        "/api/trading/risk/metrics",
    ]:
        operation = schema["paths"][path]["get"]
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_tradingview_body_config_endpoints_have_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/tradingview/chart/config", "/api/tradingview/ticker-tape/config"]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json


def test_task_stop_import_and_export_endpoints_have_docs_and_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    stop_operation = schema["paths"]["/api/tasks/{task_id}/stop"]["post"]
    stop_parameters = stop_operation.get("parameters", [])
    stop_success_json = stop_operation["responses"]["200"]["content"]["application/json"]

    assert len(stop_operation.get("description", "")) >= 20
    assert any(param["name"] == "task_id" and param.get("description") for param in stop_parameters)
    assert "example" in stop_success_json or "examples" in stop_success_json

    for path in ["/api/tasks/import", "/api/tasks/export"]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json


def test_task_register_and_cleanup_endpoints_have_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    register_operation = schema["paths"]["/api/tasks/register"]["post"]
    register_request_json = register_operation["requestBody"]["content"]["application/json"]

    assert len(register_operation.get("description", "")) >= 20
    assert "example" in register_request_json or "examples" in register_request_json

    cleanup_operation = schema["paths"]["/api/tasks/executions/cleanup"]["delete"]
    cleanup_parameters = cleanup_operation.get("parameters", [])
    cleanup_success_json = cleanup_operation["responses"]["200"]["content"]["application/json"]

    assert cleanup_operation.get("summary")
    assert len(cleanup_operation.get("description", "")) >= 20
    assert any(param["name"] == "days" and param.get("description") for param in cleanup_parameters)
    assert "example" in cleanup_success_json or "examples" in cleanup_success_json
    assert any(code.startswith(("4", "5")) for code in cleanup_operation["responses"])


def test_task_read_endpoints_have_parameter_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, expected_params in [
        ("/api/tasks/", ["task_type", "tags", "status", "enabled", "limit", "offset"]),
        ("/api/tasks/{task_id}", ["task_id"]),
        ("/api/tasks/executions/", ["task_id", "limit"]),
        ("/api/tasks/executions/{execution_id}", ["execution_id"]),
        ("/api/tasks/statistics/", []),
        ("/api/tasks/health", []),
    ]:
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_task_admin_endpoints_have_response_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/tasks/{task_id}", "delete"): ["task_id"],
        ("/api/tasks/audit/logs", "get"): ["limit", "operation", "username"],
        ("/api/tasks/cleanup/audit", "post"): ["days"],
    }

    for (path, method), expected_params in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"]["200"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_data_quality_hotspot_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params, expects_request_example in [
        ("/api/data-quality/health", "get", [], False),
        ("/api/data-quality/alerts/{alert_id}/acknowledge", "post", ["alert_id"], False),
        ("/api/data-quality/alerts/{alert_id}/resolve", "post", ["alert_id"], False),
        ("/api/data-quality/config/mode", "get", [], False),
        ("/api/data-quality/status/overview", "get", [], False),
        ("/api/data-quality/test/quality", "post", ["source"], True),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)

        if expects_request_example:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json

        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_stock_reference_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, expected_params in [
        (
            "/api/v1/data/stocks/basic",
            ["limit", "offset", "search", "industry", "concept", "market", "sort_field", "sort_order"],
        ),
        ("/api/v1/data/stocks/industries", []),
        ("/api/v1/data/stocks/concepts", []),
        ("/api/v1/data/stocks/search", ["keyword", "limit"]),
        ("/api/v1/data/stocks/{symbol}/detail", ["symbol"]),
    ]:
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_market_overview_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/v1/data/markets/overview": set(),
        "/api/v1/data/markets/price-distribution": set(),
        "/api/v1/data/markets/hot-industries": {"limit"},
        "/api/v1/data/markets/hot-concepts": {"limit"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_market_health_and_refresh_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/v1/market/health", "get"): set(),
        ("/api/v1/market/heatmap", "get"): {"market", "limit"},
        ("/api/v1/market/fund-flow", "get"): {"symbol", "timeframe", "start_date", "end_date"},
        ("/api/v1/market/fund-flow/refresh", "post"): {"symbol", "timeframe"},
        ("/api/v1/market/etf/list", "get"): {"symbol", "keyword", "market", "category", "limit", "offset"},
        ("/api/v1/market/etf/refresh", "post"): set(),
        ("/api/v1/market/chip-race", "get"): {"race_type", "trade_date", "min_race_amount", "limit"},
        ("/api/v1/market/chip-race/refresh", "post"): {"race_type", "trade_date"},
        ("/api/v1/market/lhb", "get"): {"symbol", "start_date", "end_date", "min_net_amount", "limit"},
        ("/api/v1/market/lhb/refresh", "post"): {"trade_date"},
        ("/api/v1/market/quotes", "get"): {"symbols"},
        ("/api/v1/market/stocks", "get"): {"limit", "search", "exchange", "security_type"},
        ("/api/v1/market/kline", "get"): {"stock_code", "period", "adjust", "start_date", "end_date"},
        ("/api/v2/market/fund-flow", "get"): {"symbol", "timeframe", "start_date", "end_date"},
        ("/api/v2/market/fund-flow/refresh", "post"): {"symbol", "timeframe"},
        ("/api/v2/market/etf/list", "get"): {"symbol", "keyword", "limit"},
        ("/api/v2/market/etf/refresh", "post"): set(),
        ("/api/v2/market/lhb", "get"): {"symbol", "start_date", "end_date", "min_net_amount", "limit"},
        ("/api/v2/market/lhb/refresh", "post"): {"trade_date"},
        ("/api/v2/market/sector/fund-flow", "get"): {"sector_type", "timeframe", "limit"},
        ("/api/v2/market/sector/fund-flow/refresh", "post"): {"sector_type", "timeframe"},
        ("/api/v2/market/dividend", "get"): {"symbol", "limit"},
        ("/api/v2/market/dividend/refresh", "post"): {"symbol"},
        ("/api/v2/market/blocktrade", "get"): {"symbol", "start_date", "end_date", "limit"},
        ("/api/v2/market/blocktrade/refresh", "post"): {"trade_date"},
        ("/api/v2/market/refresh-all", "post"): set(),
    }

    for (path, method), parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_akshare_exchange_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/akshare/market/sse/overview": set(),
        "/api/akshare/market/sse/daily-deal": {"date"},
        "/api/akshare/market/szse/overview": {"date"},
        "/api/akshare/market/szse/area-trading": {"date"},
        "/api/akshare/market/szse/sector-trading": {"symbol", "date"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_akshare_fund_flow_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/akshare/market/fund-flow/north-stock/{symbol}": {"symbol"},
        "/api/akshare/market/fund-flow/south-stock/{symbol}": {"symbol"},
        "/api/akshare/market/fund-flow/hsgt-holdings/{symbol}": {"symbol"},
        "/api/akshare/market/fund-flow/big-deal": set(),
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_akshare_analysis_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/akshare/market/chip-distribution/{symbol}": {"symbol"},
        "/api/akshare/market/forecast/profit/em/{symbol}": {"symbol"},
        "/api/akshare/market/forecast/profit/ths/{symbol}": {"symbol"},
        "/api/akshare/market/technical/indicators/em/{symbol}": {"symbol"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_akshare_board_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/akshare/market/board/concept/cons/{symbol}": {"symbol"},
        "/api/akshare/market/board/concept/history/{symbol}": {"symbol", "start_date", "end_date"},
        "/api/akshare/market/board/concept/minute/{symbol}": {"symbol"},
        "/api/akshare/market/board/industry/cons/{symbol}": {"symbol"},
        "/api/akshare/market/board/industry/history/{symbol}": {"symbol", "start_date", "end_date"},
        "/api/akshare/market/board/industry/minute/{symbol}": {"symbol"},
        "/api/akshare/market/sector/hot-ranking": set(),
        "/api/akshare/market/sector/fund-flow-ranking": set(),
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_auth_support_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/v1/auth/logout", "post"): {"parameters": set(), "requires_request_example": False},
        ("/api/v1/auth/me", "get"): {"parameters": set(), "requires_request_example": False},
        ("/api/v1/auth/refresh", "post"): {"parameters": set(), "requires_request_example": False},
        ("/api/v1/auth/register", "post"): {"parameters": set(), "requires_request_example": True},
        ("/api/v1/auth/reset-password/request", "post"): {"parameters": set(), "requires_request_example": True},
        ("/api/v1/auth/reset-password/confirm", "post"): {"parameters": set(), "requires_request_example": True},
    }

    for (path, method), expectation in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expectation["parameters"]:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        if expectation["requires_request_example"]:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_auth_login_endpoints_have_form_example_and_error_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/v1/auth/login", "/api/auth/login"]:
        operation = schema["paths"][path]["post"]
        form_content = operation["requestBody"]["content"]["application/x-www-form-urlencoded"]
        success_json = operation["responses"]["200"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in form_content or "examples" in form_content
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_operational_health_endpoints_have_descriptions_and_error_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    detailed_operation = schema["paths"]["/api/health/detailed"]["get"]
    dashboard_operation = schema["paths"]["/api/dashboard/health"]["get"]

    assert len(detailed_operation.get("description", "")) >= 20
    assert any(code.startswith("5") for code in detailed_operation["responses"])

    assert len(dashboard_operation.get("description", "")) >= 20
    assert any(code.startswith(("4", "5")) for code in dashboard_operation["responses"])


def test_trade_endpoints_have_examples_parameter_docs_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    health_operation = schema["paths"]["/api/v1/trade/health"]["get"]
    signals_operation = schema["paths"]["/api/v1/trade/signals"]["get"]
    execute_operation = schema["paths"]["/api/v1/trade/execute"]["post"]

    assert len(health_operation.get("description", "")) >= 20
    assert any(code.startswith("5") for code in health_operation["responses"])

    assert any(
        param["name"] == "limit" and param.get("description")
        for param in signals_operation.get("parameters", [])
    )
    assert any(code.startswith("5") for code in signals_operation["responses"])

    execute_json = execute_operation["requestBody"]["content"]["application/json"]
    assert "example" in execute_json or "examples" in execute_json
    assert any(code.startswith(("4", "5")) for code in execute_operation["responses"])


def test_technical_symbol_routes_have_path_parameter_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/technical/{symbol}/momentum",
        "/api/v1/technical/{symbol}/volatility",
        "/api/v1/technical/{symbol}/volume",
        "/api/v1/technical/{symbol}/signals",
        "/api/v1/technical/{symbol}/history",
    ]:
        operation = schema["paths"][path]["get"]
        assert any(
            param["name"] == "symbol" and param["in"] == "path" and param.get("description")
            for param in operation.get("parameters", [])
        )


def test_monitoring_alert_management_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/v1/monitoring/alert-rules", "get"): {
            "parameters": {"rule_type", "is_active"},
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/alert-rules", "post"): {
            "parameters": set(),
            "requires_request_example": True,
        },
        ("/api/v1/monitoring/alert-rules/{rule_id}", "put"): {
            "parameters": {"rule_id"},
            "requires_request_example": True,
        },
        ("/api/v1/monitoring/alert-rules/{rule_id}", "delete"): {
            "parameters": {"rule_id"},
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/alerts/{alert_id}/mark-read", "post"): {
            "parameters": {"alert_id"},
            "requires_request_example": False,
        },
        ("/api/v1/monitoring/alerts/mark-all-read", "post"): {
            "parameters": set(),
            "requires_request_example": False,
        },
    }

    for (path, method), expectation in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expectation["parameters"]:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        if expectation["requires_request_example"]:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_stock_search_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        "/api/stock-search/search": {"q", "market", "page", "page_size", "sort_by", "sort_order"},
        "/api/stock-search/quote/{symbol}": {"symbol", "market"},
        "/api/stock-search/profile/{symbol}": {"symbol", "market"},
    }

    for path, parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_stock_search_support_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    endpoint_expectations = {
        ("/api/stock-search/news/{symbol}", "get"): {"symbol", "market", "days"},
        ("/api/stock-search/news/market/{category}", "get"): {"category", "market"},
        ("/api/stock-search/recommendation/{symbol}", "get"): {"symbol"},
        ("/api/stock-search/rate-limits/status", "get"): {"user_id"},
        ("/api/stock-search/cache/clear", "post"): set(),
        ("/api/stock-search/analytics/searches", "get"): {"limit", "operation", "username"},
        ("/api/stock-search/analytics/cleanup", "post"): {"days"},
    }

    for (path, method), parameter_names in endpoint_expectations.items():
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in parameter_names:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_watchlist_write_endpoints_have_docs_and_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params in [
        ("/api/watchlist/add", "post", []),
        ("/api/watchlist/groups", "post", []),
        ("/api/watchlist/groups/{group_id}", "put", ["group_id"]),
        ("/api/watchlist/move", "put", []),
        ("/api/watchlist/notes/{symbol}", "put", ["symbol"]),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in request_json or "examples" in request_json


def test_watchlist_read_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params in [
        ("/api/watchlist/", "get", []),
        ("/api/watchlist/symbols", "get", []),
        ("/api/watchlist/remove/{symbol}", "delete", ["symbol"]),
        ("/api/watchlist/check/{symbol}", "get", ["symbol"]),
        ("/api/watchlist/count", "get", []),
        ("/api/watchlist/clear", "delete", []),
        ("/api/watchlist/groups", "get", []),
        ("/api/watchlist/groups/{group_id}", "delete", ["group_id"]),
        ("/api/watchlist/group/{group_id}", "get", ["group_id"]),
        ("/api/watchlist/with-groups", "get", []),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])
        success_json = operation["responses"][next(code for code in operation["responses"] if code.startswith("2"))][
            "content"
        ]["application/json"]

        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_wencai_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params, expects_request_example, expects_success_example in [
        ("/api/market/wencai/queries", "get", [], False, True),
        ("/api/market/wencai/queries/{query_name}", "get", ["query_name"], False, True),
        ("/api/market/wencai/query", "post", [], True, False),
        ("/api/market/wencai/results/{query_name}", "get", ["query_name"], False, True),
        ("/api/market/wencai/refresh/{query_name}", "post", ["query_name"], False, True),
        ("/api/market/wencai/history/{query_name}", "get", ["query_name"], False, True),
        ("/api/market/wencai/custom-query", "post", [], True, False),
        ("/api/market/wencai/health", "get", [], False, True),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])

        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)

        if expects_request_example:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json

        if expects_success_example:
            success_json = operation["responses"]["200"]["content"]["application/json"]
            assert "example" in success_json or "examples" in success_json

        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_monitoring_analysis_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params, expects_request_example in [
        ("/api/v1/monitoring/analysis/calculate", "post", ["use_gpu"], True),
        ("/api/v1/monitoring/analysis/calculate/batch", "post", ["use_gpu"], True),
        ("/api/v1/monitoring/analysis/results/{stock_code}", "get", ["stock_code", "days"], False),
        (
            "/api/v1/monitoring/analysis/portfolio/{watchlist_id}",
            "get",
            ["watchlist_id", "user_id", "include_risk_metrics"],
            False,
        ),
        ("/api/v1/monitoring/analysis/market-regime", "get", ["index_code"], False),
        ("/api/v1/monitoring/analysis/engine/status", "get", [], False),
        ("/api/v1/monitoring/analysis/portfolio/{watchlist_id}/summary", "get", ["watchlist_id", "user_id"], False),
        (
            "/api/v1/monitoring/analysis/portfolio/{watchlist_id}/alerts",
            "get",
            ["watchlist_id", "user_id", "level"],
            False,
        ),
        (
            "/api/v1/monitoring/analysis/portfolio/{watchlist_id}/rebalance",
            "get",
            ["watchlist_id", "user_id"],
            False,
        ),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)

        if expects_request_example:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json

        success_json = operation["responses"]["200"]["content"]["application/json"]
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_analysis_backtest_and_stress_test_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params, expects_request_example in [
        ("/api/v1/backtest/monte-carlo", "post", [], True),
        ("/api/v1/backtest/stress-test", "post", [], True),
        ("/api/v1/backtest/equity-curve/{strategy_id}", "get", ["strategy_id", "start_date", "end_date"], False),
        ("/api/v1/stress-test/run", "post", ["portfolio_id", "initial_capital"], True),
        ("/api/v1/stress-test/scenarios", "get", [], False),
        ("/api/v1/stress-test/history", "get", ["portfolio_id", "limit"], False),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)

        if expects_request_example:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json

        success_code = next(code for code in operation["responses"] if code.startswith("2"))
        success_json = operation["responses"][success_code]["content"]["application/json"]
        assert "example" in success_json or "examples" in success_json
        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_monitoring_watchlist_endpoints_have_docs_examples_and_error_responses() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path, method, expected_params, requires_request_example in [
        ("/api/v1/monitoring/watchlists", "post", ["user_id"], True),
        ("/api/v1/monitoring/watchlists", "get", ["user_id"], False),
        ("/api/v1/monitoring/watchlists/{watchlist_id}", "get", ["watchlist_id", "user_id"], False),
        ("/api/v1/monitoring/watchlists/{watchlist_id}", "put", ["watchlist_id", "user_id"], True),
        ("/api/v1/monitoring/watchlists/{watchlist_id}", "delete", ["watchlist_id", "user_id"], False),
        ("/api/v1/monitoring/watchlists/{watchlist_id}/stocks", "post", ["watchlist_id", "user_id"], True),
        ("/api/v1/monitoring/watchlists/{watchlist_id}/stocks", "get", ["watchlist_id", "user_id"], False),
        (
            "/api/v1/monitoring/watchlists/{watchlist_id}/stocks/{stock_code}",
            "delete",
            ["watchlist_id", "stock_code", "user_id"],
            False,
        ),
    ]:
        operation = schema["paths"][path][method]
        parameters = operation.get("parameters", [])

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        for parameter_name in expected_params:
            assert any(param["name"] == parameter_name and param.get("description") for param in parameters)

        if requires_request_example:
            request_json = operation["requestBody"]["content"]["application/json"]
            assert "example" in request_json or "examples" in request_json

        assert any(code.startswith(("4", "5")) for code in operation["responses"])


def test_ml_strategy_endpoints_have_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/strategies/train",
        "/api/v1/strategies/predict",
        "/api/v1/strategies/backtest",
    ]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json


def test_risk_v31_stop_loss_write_endpoints_have_docs_and_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/risk/v31/stop-loss/add-position",
        "/api/v1/risk/v31/stop-loss/update-price",
        "/api/v1/risk/v31/stop-loss/batch-update",
        "/api/v1/risk/v31/stop-loss/calculate",
        "/api/v1/risk/v31/stop-loss/trigger",
    ]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json


def test_risk_v31_alert_write_endpoints_have_docs_and_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/risk/v31/alert/send",
        "/api/v1/risk/v31/rules/evaluate",
        "/api/v1/risk/v31/rules/add",
    ]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json


def test_risk_alert_management_write_endpoints_have_docs_and_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    paths = [
        ("/api/v1/risk/v31/rules/remove/{rule_id}", "delete"),
        ("/api/v1/risk/alerts", "post"),
        ("/api/v1/risk/alerts/{alert_id}", "delete"),
        ("/api/v1/risk/notifications/test", "post"),
        ("/api/v1/risk/alerts/generate", "post"),
    ]

    for path, method in paths:
        operation = schema["paths"][path][method]
        assert len(operation.get("description", "")) >= 20

        if "requestBody" not in operation:
            continue

        request_json = operation["requestBody"]["content"]["application/json"]
        assert "example" in request_json or "examples" in request_json


def test_risk_remaining_write_endpoints_have_docs_and_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    paths = [
        ("/api/v1/risk/position/assess", "post"),
        ("/api/v1/risk/v31/stop-loss/remove-position/{position_id}", "delete"),
    ]

    for path, method in paths:
        operation = schema["paths"][path][method]
        assert len(operation.get("description", "")) >= 20

        if "requestBody" not in operation:
            continue

        request_json = operation["requestBody"]["content"]["application/json"]
        assert "example" in request_json or "examples" in request_json


def test_v1_lineage_write_endpoints_have_request_examples() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in [
        "/api/v1/lineage/record",
        "/api/v1/lineage/graph",
        "/api/v1/lineage/impact",
    ]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json


def test_v1_strategy_backtest_endpoints_have_request_examples_and_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    run_operation = schema["paths"]["/api/v1/strategy/backtest/run"]["post"]
    run_request_json = run_operation["requestBody"]["content"]["application/json"]
    assert run_operation.get("summary")
    assert len(run_operation.get("description", "")) >= 20
    assert "example" in run_request_json or "examples" in run_request_json

    for path in [
        "/api/v1/strategy/backtest/results/{backtest_id}",
        "/api/v1/strategy/backtest/status/{backtest_id}",
    ]:
        operation = schema["paths"][path]["get"]
        parameters = operation.get("parameters", [])

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert any(param["name"] == "backtest_id" and param.get("description") for param in parameters)


def test_v1_data_route_sentiment_strategy_and_optimization_endpoints_have_docs() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    for path in ["/api/v1/data/route", "/api/v1/sentiment/analyze"]:
        operation = schema["paths"][path]["post"]
        request_json = operation["requestBody"]["content"]["application/json"]

        assert operation.get("summary")
        assert len(operation.get("description", "")) >= 20
        assert "example" in request_json or "examples" in request_json

    strategies_operation = schema["paths"]["/api/v1/strategies"]["get"]
    strategies_parameters = strategies_operation.get("parameters", [])
    assert strategies_operation.get("summary")
    assert len(strategies_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "strategy_type" and param.get("description")
        for param in strategies_parameters
    )

    slow_queries_operation = schema["paths"]["/api/v1/optimization/slow-queries"]["get"]
    slow_queries_parameters = slow_queries_operation.get("parameters", [])
    assert slow_queries_operation.get("summary")
    assert len(slow_queries_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "limit" and param.get("description")
        for param in slow_queries_parameters
    )


def test_remaining_signal_health_and_task_endpoints_have_parameter_docs_and_descriptions() -> None:
    app.openapi_schema = None
    schema = app.openapi()

    health_report_operation = schema["paths"]["/api/reports/health/{timestamp}"]["get"]
    health_report_parameters = health_report_operation.get("parameters", [])
    assert health_report_operation.get("summary")
    assert len(health_report_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "timestamp" and param["in"] == "path" and param.get("description")
        for param in health_report_parameters
    )

    signal_quality_operation = schema["paths"]["/api/signals/quality-report"]["get"]
    signal_quality_parameters = signal_quality_operation.get("parameters", [])
    assert signal_quality_operation.get("summary")
    assert len(signal_quality_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "strategy_id" and param.get("description")
        for param in signal_quality_parameters
    )

    realtime_operation = schema["paths"]["/api/strategies/{strategy_id}/realtime"]["get"]
    realtime_parameters = realtime_operation.get("parameters", [])
    assert realtime_operation.get("summary")
    assert len(realtime_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "strategy_id" and param["in"] == "path" and param.get("description")
        for param in realtime_parameters
    )

    task_operation = schema["paths"]["/api/tasks/{task_id}"]["get"]
    task_parameters = task_operation.get("parameters", [])
    assert task_operation.get("summary")
    assert len(task_operation.get("description", "")) >= 20
    assert any(
        param["name"] == "task_id" and param["in"] == "path" and param.get("description")
        for param in task_parameters
    )
