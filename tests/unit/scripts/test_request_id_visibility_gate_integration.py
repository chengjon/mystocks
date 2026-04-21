from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_frontend_testing_workflow_runs_request_id_visibility_gate() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "frontend-testing.yml").read_text(encoding="utf-8")

    assert "Request ID Visibility Gate" in content
    assert "python ../../scripts/compliance/request_id_visibility_gate.py --format json" in content
    assert "request-id-visibility-gate-report.json" in content
