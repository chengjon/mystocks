from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "readiness_contract_gate.py"


def test_readiness_contract_gate_passes_for_current_repo_state() -> None:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"

    completed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr

    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checks"]["backend_ready_probe"]["passed"] is True
    assert payload["checks"]["app_startup_readiness"]["passed"] is True
    assert payload["checks"]["app_non_blank_fallback"]["passed"] is True

