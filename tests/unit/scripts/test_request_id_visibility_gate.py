from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "request_id_visibility_gate.py"


def run_gate(*paths: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--format", "json"]
    for path in paths:
        command.extend(["--path", path])
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def test_ignores_non_scoped_files() -> None:
    completed = run_gate("web/frontend/src/App.vue")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 0
    assert payload["errors"] == []


def test_accepts_template_based_trace_id_display(tmp_path: Path) -> None:
    scoped_dir = tmp_path / "web" / "frontend" / "src" / "views" / "artdeco-pages" / "market-tabs"
    scoped_dir.mkdir(parents=True)
    target = scoped_dir / "TemplateBasedTab.vue"
    target.write_text(
        """
<template>
  <ArtDecoPageTemplate :page-config="pageConfig">
    <template #content>
      <div>ok</div>
    </template>
  </ArtDecoPageTemplate>
</template>

<script setup lang="ts">
import ArtDecoPageTemplate from '@/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue'
</script>
""".strip(),
        encoding="utf-8",
    )

    completed = run_gate(str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["errors"] == []


def test_accepts_explicit_request_id_display(tmp_path: Path) -> None:
    scoped_dir = tmp_path / "web" / "frontend" / "src" / "views" / "artdeco-pages" / "system-tabs"
    scoped_dir.mkdir(parents=True)
    target = scoped_dir / "ExplicitTraceTab.vue"
    target.write_text(
        """
<template>
  <div class="tab-root">
    <div class="trace-id" v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</div>
  </div>
</template>

<script setup lang="ts">
const lastRequestId = 'req-1'
</script>
""".strip(),
        encoding="utf-8",
    )

    completed = run_gate(str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["errors"] == []


def test_rejects_scoped_tab_without_request_id_display(tmp_path: Path) -> None:
    scoped_dir = tmp_path / "web" / "frontend" / "src" / "views" / "artdeco-pages" / "strategy-tabs"
    scoped_dir.mkdir(parents=True)
    target = scoped_dir / "MissingTraceTab.vue"
    target.write_text(
        """
<template>
  <div class="tab-root">
    <h2>策略面板</h2>
  </div>
</template>

<script setup lang="ts">
const title = 'test'
</script>
""".strip(),
        encoding="utf-8",
    )

    completed = run_gate(str(target))

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["errors"][0]["path"].endswith("MissingTraceTab.vue")

