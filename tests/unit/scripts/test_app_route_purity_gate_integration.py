from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_frontend_testing_workflow_runs_app_route_purity_gate() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "frontend-testing.yml").read_text(encoding="utf-8")

    assert "App Route Purity Gate" in content
    assert "python scripts/compliance/app_route_purity_gate.py --format json" in content
    assert "app-route-purity-gate-report.json" in content

