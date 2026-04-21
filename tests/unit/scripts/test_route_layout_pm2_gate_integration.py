from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_frontend_testing_workflow_contains_route_layout_pm2_gate() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "frontend-testing.yml").read_text(encoding="utf-8")

    assert "route-layout-pm2-detect" in content
    assert "Route/Layout Runtime Baseline" in content
    assert "python scripts/compliance/route_layout_pm2_gate.py --format json" in content
    assert "scripts/run_frontend_runtime_baseline.sh" in content
    assert "route-layout-pm2-gate-report.json" in content
