from __future__ import annotations

from datetime import date

from scripts.dev.quality_gate.tech_debt_governance_gate import (
    compute_hotspot_scores,
    evaluate_baseline_review,
    evaluate_no_new_debt,
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
    }
    current = {
        "frontend_type_errors": 101,
        "frontend_suppressions_count": 20,
        "skip_xfail_count": 12,
    }

    violations = evaluate_no_new_debt(current=current, baseline=baseline)

    assert any("frontend_type_errors" in item for item in violations)
    assert any("skip_xfail_count" in item for item in violations)


def test_evaluate_baseline_review_only_allows_non_increase() -> None:
    previous = {
        "frontend_type_errors": 200,
        "frontend_suppressions_count": 50,
        "skip_xfail_count": 30,
    }
    proposed = {
        "frontend_type_errors": 190,
        "frontend_suppressions_count": 50,
        "skip_xfail_count": 31,
    }

    violations = evaluate_baseline_review(previous_baseline=previous, proposed_baseline=proposed)

    assert violations == ["baseline metric skip_xfail_count increased: proposed=31 > previous=30"]


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
