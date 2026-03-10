from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "app_route_purity_gate.py"


def run_gate(target_file: Path) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--format", "json", "--file", str(target_file)],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
    )


def test_app_route_purity_gate_passes_for_current_app() -> None:
    completed = run_gate(PROJECT_ROOT / "web" / "frontend" / "src" / "App.vue")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checks"]["router_view_required"]["passed"] is True
    assert payload["checks"]["forbidden_component_tags"]["passed"] is True
    assert payload["checks"]["forbidden_sfc_imports"]["passed"] is True


def test_app_route_purity_gate_fails_without_router_view(tmp_path: Path) -> None:
    app_file = tmp_path / "App.vue"
    app_file.write_text(
        """
<template>
  <div class="app-container">
    <section>plain shell only</section>
  </div>
</template>
""".strip(),
        encoding="utf-8",
    )

    completed = run_gate(app_file)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["checks"]["router_view_required"]["passed"] is False


def test_app_route_purity_gate_fails_for_business_component_tag(tmp_path: Path) -> None:
    app_file = tmp_path / "App.vue"
    app_file.write_text(
        """
<template>
  <div class="app-container">
    <ArtDecoDashboard />
    <router-view />
  </div>
</template>
""".strip(),
        encoding="utf-8",
    )

    completed = run_gate(app_file)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["checks"]["forbidden_component_tags"]["passed"] is False
    assert "ArtDecoDashboard" in payload["checks"]["forbidden_component_tags"]["matches"]

