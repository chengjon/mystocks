from scripts.dev.quality_gate.tech_debt_governance_gate import build_closeout_validation_report


def test_build_closeout_validation_report_marks_all_expected_closeouts_valid() -> None:
    report = build_closeout_validation_report(
        {
            "runtime_delivery_gate": {
                "status": "completed",
                "episode_uuid": "ep-runtime",
                "group_id": "mystocks_spec_runtime_delivery_gates",
                "ingest_status": "warming",
            },
            "frontend_runtime_gate": {
                "status": "completed",
                "episode_uuid": "ep-frontend",
                "group_id": "mystocks_spec_quality_gates",
                "ingest_status": "completed",
            },
            "api_performance_gate": {
                "status": "completed",
                "episode_uuid": "ep-api",
                "group_id": "mystocks_spec_quality_gates",
                "ingest_status": "warming",
            },
            "monitoring_auth_performance_gate": {
                "status": "completed",
                "episode_uuid": "ep-monitoring",
                "group_id": "mystocks_spec_quality_gates",
                "ingest_status": "warming",
            },
            "docker_runtime_smoke": {
                "status": "completed",
                "episode_uuid": "ep-docker",
                "group_id": "mystocks_spec_quality_gates",
                "ingest_status": "warming",
            },
        }
    )

    assert len(report) == 5
    assert all(item["valid"] for item in report)
    assert [item["reason"] for item in report] == ["ok", "ok", "ok", "ok", "ok"]


def test_build_closeout_validation_report_flags_missing_and_invalid_closeouts() -> None:
    report = build_closeout_validation_report(
        {
            "runtime_delivery_gate": {
                "status": "completed",
                "episode_uuid": "ep-runtime",
                "group_id": "wrong-group",
                "ingest_status": "warming",
            },
            "frontend_runtime_gate": {
                "status": "invalid_payload",
                "ingest_status": "not_loaded",
            },
        }
    )

    by_key = {item["key"]: item for item in report}

    assert by_key["runtime_delivery_gate"]["valid"] is False
    assert by_key["runtime_delivery_gate"]["reason"] == "group_id=wrong-group"
    assert by_key["frontend_runtime_gate"]["valid"] is False
    assert by_key["frontend_runtime_gate"]["reason"] == "status=invalid_payload"
    assert by_key["monitoring_auth_performance_gate"]["present"] is False
    assert by_key["monitoring_auth_performance_gate"]["reason"] == "missing_closeout"
    assert by_key["api_performance_gate"]["present"] is False
    assert by_key["api_performance_gate"]["reason"] == "missing_closeout"
    assert by_key["docker_runtime_smoke"]["present"] is False
    assert by_key["docker_runtime_smoke"]["reason"] == "missing_closeout"
