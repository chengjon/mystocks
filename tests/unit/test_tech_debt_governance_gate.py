from __future__ import annotations

import json
from datetime import date

from scripts.dev.quality_gate.tech_debt_governance_gate import (
    build_baseline_drift_report,
    compute_hotspot_scores,
    evaluate_baseline_review,
    evaluate_no_new_debt,
    flatten_numeric_metrics,
    get_metric_value,
    load_baseline_review_exceptions,
    parse_ttl,
)


def test_parse_ttl_accepts_iso_date() -> None:
    assert parse_ttl("ttl=2026-03-31") == date(2026, 3, 31)


def test_parse_ttl_returns_none_for_invalid_text() -> None:
    assert parse_ttl("no ttl marker") is None


def test_evaluate_no_new_debt_detects_regression() -> None:
    baseline = {
        "frontend_type_errors": 100,
        "frontend_suppressions_count": 20,
        "skip_xfail_count": 10,
        "backend_api_documentation": {
            "documented_endpoints": 10,
            "documented_percentage": 1.0,
            "endpoints_with_examples": 8,
            "example_percentage": 0.8,
            "endpoints_with_errors": 10,
            "error_response_percentage": 1.0,
            "total_issues": 0,
            "schema_issue_count": 0,
            "authentication_issue_count": 0,
            "json_success_missing_examples": 0,
        },
    }
    current = {
        "frontend_type_errors": 101,
        "frontend_suppressions_count": 20,
        "skip_xfail_count": 12,
        "backend_api_documentation": {
            "documented_endpoints": 10,
            "documented_percentage": 1.0,
            "endpoints_with_examples": 7,
            "example_percentage": 0.7,
            "endpoints_with_errors": 10,
            "error_response_percentage": 1.0,
            "total_issues": 1,
            "schema_issue_count": 0,
            "authentication_issue_count": 0,
            "json_success_missing_examples": 1,
        },
    }

    violations = evaluate_no_new_debt(current=current, baseline=baseline)

    assert any("frontend_type_errors" in item for item in violations)
    assert any("skip_xfail_count" in item for item in violations)
    assert any("backend_api_documentation.endpoints_with_examples" in item for item in violations)
    assert any("backend_api_documentation.total_issues" in item for item in violations)
    assert any("backend_api_documentation.json_success_missing_examples" in item for item in violations)


def test_evaluate_baseline_review_only_allows_non_increase() -> None:
    previous = {
        "frontend_type_errors": 200,
        "frontend_suppressions_count": 50,
        "skip_xfail_count": 30,
        "backend_api_documentation": {
            "documented_endpoints": 20,
            "documented_percentage": 1.0,
            "endpoints_with_examples": 15,
            "example_percentage": 0.75,
            "endpoints_with_errors": 20,
            "error_response_percentage": 1.0,
            "total_issues": 0,
            "schema_issue_count": 0,
            "authentication_issue_count": 0,
            "json_success_missing_examples": 0,
        },
    }
    proposed = {
        "frontend_type_errors": 190,
        "frontend_suppressions_count": 50,
        "skip_xfail_count": 31,
        "backend_api_documentation": {
            "documented_endpoints": 19,
            "documented_percentage": 0.95,
            "endpoints_with_examples": 15,
            "example_percentage": 0.75,
            "endpoints_with_errors": 20,
            "error_response_percentage": 1.0,
            "total_issues": 0,
            "schema_issue_count": 0,
            "authentication_issue_count": 0,
            "json_success_missing_examples": 0,
        },
    }

    violations = evaluate_baseline_review(previous_baseline=previous, proposed_baseline=proposed)

    assert "baseline metric skip_xfail_count increased: proposed=31 > previous=30" in violations
    assert "baseline metric backend_api_documentation.documented_endpoints decreased: proposed=19 < previous=20" in violations
    assert "baseline metric backend_api_documentation.documented_percentage decreased: proposed=0.95 < previous=1.0" in violations


def test_evaluate_baseline_review_allows_approved_rebaseline_exception() -> None:
    previous = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 0,
    }
    proposed = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 102,
    }
    exceptions = {
        "skip_xfail_count": {
            "approved_value": 102,
            "owner": "governance",
            "issue": "baseline-2026-04-08",
            "ttl": "2026-04-30",
            "reason": "replace historical placeholder baseline with measured value",
        }
    }

    violations = evaluate_baseline_review(
        previous_baseline=previous,
        proposed_baseline=proposed,
        review_exceptions=exceptions,
        as_of=date(2026, 4, 8),
    )

    assert violations == []


def test_evaluate_baseline_review_rejects_expired_rebaseline_exception() -> None:
    previous = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 0,
    }
    proposed = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 102,
    }
    exceptions = {
        "skip_xfail_count": {
            "approved_value": 102,
            "owner": "governance",
            "issue": "baseline-2026-04-08",
            "ttl": "2026-04-01",
            "reason": "replace historical placeholder baseline with measured value",
        }
    }

    violations = evaluate_baseline_review(
        previous_baseline=previous,
        proposed_baseline=proposed,
        review_exceptions=exceptions,
        as_of=date(2026, 4, 8),
    )

    assert "baseline metric skip_xfail_count increased: proposed=102 > previous=0" in violations


def test_load_baseline_review_exceptions_reads_json_file(tmp_path) -> None:
    manifest = tmp_path / "baseline-exceptions.json"
    manifest.write_text(
        json.dumps(
            {
                "exceptions": [
                    {
                        "path": "skip_xfail_count",
                        "approved_value": 102,
                        "owner": "governance",
                        "issue": "baseline-2026-04-08",
                        "ttl": "2026-04-30",
                        "reason": "replace historical placeholder baseline with measured value",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exceptions = load_baseline_review_exceptions(manifest)

    assert exceptions["skip_xfail_count"]["approved_value"] == 102


def test_flatten_numeric_metrics_flattens_nested_paths() -> None:
    payload = {
        "frontend_type_errors": 0,
        "backend_api_documentation": {
            "documented_endpoints": 491,
            "json_success_missing_examples": 0,
        },
        "generated_at": "2026-04-09T00:00:00Z",
    }

    flattened = flatten_numeric_metrics(payload)

    assert flattened == {
        "frontend_type_errors": 0,
        "backend_api_documentation.documented_endpoints": 491,
        "backend_api_documentation.json_success_missing_examples": 0,
    }


def test_build_baseline_drift_report_marks_gated_and_observed_drifts() -> None:
    baseline = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 102,
        "backend_todo_count": 0,
        "backend_api_documentation": {
            "documented_endpoints": 491,
            "json_success_missing_examples": 0,
        },
    }
    current = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 102,
        "backend_todo_count": 50,
        "backend_api_documentation": {
            "documented_endpoints": 491,
            "json_success_missing_examples": 0,
        },
    }

    report = build_baseline_drift_report(baseline=baseline, current=current)
    by_path = {item["path"]: item for item in report}

    assert by_path["skip_xfail_count"]["status"] == "match"
    assert by_path["skip_xfail_count"]["gated"] is True
    assert by_path["backend_todo_count"]["status"] == "drifted"
    assert by_path["backend_todo_count"]["gated"] is False
    assert by_path["backend_todo_count"]["baseline"] == 0
    assert by_path["backend_todo_count"]["current"] == 50


def test_get_metric_value_supports_nested_paths() -> None:
    payload = {"backend_api_documentation": {"json_success_missing_examples": 0}}

    assert get_metric_value(payload, "backend_api_documentation.json_success_missing_examples") == 0
    assert get_metric_value(payload, "backend_api_documentation.nonexistent") is None


def test_compute_hotspot_scores_sorts_by_score_desc() -> None:
    scores = compute_hotspot_scores(
        large_files=[
            {"path": "a.py", "lines": 3000},
            {"path": "b.py", "lines": 2500},
        ],
        touch_counts={"a.py": 2, "b.py": 10},
        top_n=2,
    )

    assert [item["path"] for item in scores] == ["b.py", "a.py"]
