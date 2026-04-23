from scripts.runtime.validate_runtime_child_gate_closeouts import validate_closeouts


def test_validate_closeouts_passes_for_completed_child_gate_closeouts() -> None:
    report = validate_closeouts(
        {
            "frontend_runtime_gate": {
                "status": "completed",
                "episode_uuid": "ep-frontend",
                "group_id": "mystocks_spec_quality_gates",
                "ingest_status": "warming",
            },
            "api_performance_gate": {
                "status": "completed",
                "episode_uuid": "ep-api",
                "group_id": "mystocks_spec_quality_gates",
                "ingest_status": "completed",
            },
            "docker_runtime_smoke": {
                "status": "completed",
                "episode_uuid": "ep-docker",
                "group_id": "mystocks_spec_quality_gates",
                "ingest_status": "warming",
            },
        }
    )

    assert report["pass"] is True
    assert report["valid_count"] == 3
    assert report["invalid_count"] == 0
    assert [item["reason"] for item in report["items"]] == ["ok", "ok", "ok"]


def test_validate_closeouts_flags_missing_and_invalid_child_gate_closeouts() -> None:
    report = validate_closeouts(
        {
            "frontend_runtime_gate": {
                "status": "invalid_payload",
                "ingest_status": "not_loaded",
            },
            "api_performance_gate": {
                "status": "completed",
                "episode_uuid": "ep-api",
                "group_id": "wrong-group",
                "ingest_status": "warming",
            },
        }
    )

    items = {item["key"]: item for item in report["items"]}

    assert report["pass"] is False
    assert report["valid_count"] == 0
    assert report["invalid_count"] == 3
    assert items["frontend_runtime_gate"]["reason"] == "status=invalid_payload"
    assert items["api_performance_gate"]["reason"] == "group_id=wrong-group"
    assert items["docker_runtime_smoke"]["reason"] == "missing_closeout"
