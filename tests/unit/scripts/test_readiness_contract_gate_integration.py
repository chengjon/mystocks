from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_code_quality_workflow_runs_readiness_contract_gate() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")

    assert "Observability Readiness Gate" in content
    assert "python scripts/compliance/readiness_contract_gate.py --format json" in content
    assert "readiness-contract-gate-report.json" in content

