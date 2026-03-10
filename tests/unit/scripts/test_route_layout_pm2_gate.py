from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "route_layout_pm2_gate.py"


def run_gate(*paths: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--format", "json"]
    for path in paths:
        command.extend(["--path", path])
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def test_requires_pm2_gate_for_router_changes() -> None:
    completed = run_gate("web/frontend/src/router/index.ts")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["gate_required"] is True
    assert payload["matched_paths"][0]["path"] == "web/frontend/src/router/index.ts"
    assert "router" in payload["matched_paths"][0]["rules"]


def test_requires_pm2_gate_for_layout_changes() -> None:
    completed = run_gate("web/frontend/src/layouts/MainLayout.vue")

    payload = json.loads(completed.stdout)
    assert payload["gate_required"] is True
    assert payload["matched_paths"][0]["path"] == "web/frontend/src/layouts/MainLayout.vue"
    assert "layout" in payload["matched_paths"][0]["rules"]


def test_requires_pm2_gate_for_app_root_changes() -> None:
    completed = run_gate("web/frontend/src/App.vue")

    payload = json.loads(completed.stdout)
    assert payload["gate_required"] is True
    assert payload["matched_paths"][0]["path"] == "web/frontend/src/App.vue"
    assert "app-root" in payload["matched_paths"][0]["rules"]


def test_ignores_non_route_non_layout_frontend_changes() -> None:
    completed = run_gate("web/frontend/src/api/market.ts", "web/frontend/src/components/Charts/OscillatorChart.vue")

    payload = json.loads(completed.stdout)
    assert payload["gate_required"] is False
    assert payload["matched_paths"] == []

