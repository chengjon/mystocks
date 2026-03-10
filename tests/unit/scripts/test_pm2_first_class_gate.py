from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "pm2_first_class_gate.py"


def run_guard(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--root-dir", str(project_root), "--format", "json", *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def test_passes_for_canonical_pm2_runner_script(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "scripts" / "run_e2e_pm2.sh"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
#!/bin/bash
pm2 start ecosystem.test.config.js
npx playwright test tests/navigation.spec.ts
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "scripts/run_e2e_pm2.sh")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["mode"] == "canonical-pm2-runner"


def test_passes_for_explicit_pm2_orchestration(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / ".github" / "workflows" / "e2e.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
jobs:
  e2e:
    steps:
      - run: |
          pm2 start ecosystem.playwright.config.js
          pm2 list
          npx playwright test tests/smoke.spec.ts
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", ".github/workflows/e2e.yml")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["mode"] == "explicit-pm2-orchestration"


def test_fails_for_raw_uvicorn_and_dev_startup_without_pm2(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / ".github" / "workflows" / "legacy-e2e.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
jobs:
  e2e:
    steps:
      - run: |
          python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          npm run dev &
          npx playwright test tests/smoke.spec.ts
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", ".github/workflows/legacy-e2e.yml")

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["path"] == ".github/workflows/legacy-e2e.yml"
    assert payload["errors"][0]["rule_id"] == "pm2-first-class-orchestration"
    assert "python -m uvicorn" in payload["errors"][0]["raw_startup_markers"]


def test_acceptance_without_local_startup_is_not_blocked(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / ".github" / "workflows" / "frontend.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
jobs:
  frontend:
    steps:
      - run: npm run test:e2e
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", ".github/workflows/frontend.yml")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["mode"] == "acceptance-without-local-orchestration"


def test_ignores_non_scoped_files(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "docs" / "e2e-notes.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("python -m uvicorn\nnpx playwright test\n", encoding="utf-8")

    completed = run_guard(project_root, "--path", "docs/e2e-notes.md")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 0
    assert payload["summary"]["errors"] == 0


def test_supports_positional_filenames_from_pre_commit(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "scripts" / "ci" / "legacy.sh"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
#!/bin/bash
vite preview &
npx playwright test tests/smoke.spec.ts
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "scripts/ci/legacy.sh")

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["summary"]["errors"] == 1


def test_incremental_mode_passes_when_no_paths_are_provided() -> None:
    completed = run_guard(PROJECT_ROOT)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 0
    assert payload["summary"]["errors"] == 0


def test_passes_for_current_repo_pm2_runner() -> None:
    completed = run_guard(PROJECT_ROOT, "--path", "scripts/run_e2e_pm2.sh")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["mode"] == "canonical-pm2-runner"
