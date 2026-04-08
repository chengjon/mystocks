from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "deletion-waiver-audit.yml"


def test_deletion_waiver_audit_workflow_has_daily_schedule_and_manual_dispatch() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "name: Deletion Waiver Audit" in workflow
    assert "workflow_dispatch:" in workflow
    assert "cron: '0 2 * * *'" in workflow


def test_deletion_waiver_audit_workflow_reuses_shared_engine_and_publishes_outputs() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "python scripts/compliance/deletion_evidence_gate.py" in workflow
    assert "--audit-waivers" in workflow
    assert "--warning-window-days 7" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "GITHUB_STEP_SUMMARY" in workflow
    assert "python -c 'import json, os; from pathlib import Path;" in workflow
    assert "python - <<'PY'" not in workflow
