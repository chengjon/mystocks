# Deletion Waiver Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the shared deletion evidence engine with a non-blocking waiver audit mode and add a daily plus manual GitHub Actions workflow that publishes summary and artifact output.

**Architecture:** Reuse `scripts/compliance/deletion_evidence_gate.py` as the only waiver parsing and classification engine. Add one audit-specific execution path inside that script, then wire a dedicated workflow and minimal docs/tests around that path without creating any second waiver logic source.

**Tech Stack:** Python 3.12, PyYAML, pytest, GitHub Actions YAML

---

### Task 1: Add failing waiver-audit engine tests

**Files:**
- Modify: `tests/unit/scripts/test_deletion_evidence_gate.py`

- [ ] **Step 1: Add failing audit-mode tests at the end of `tests/unit/scripts/test_deletion_evidence_gate.py`**

```python
def test_waiver_audit_reports_empty_registry_as_healthy_zero_state(tmp_path: Path) -> None:
    repo = bootstrap_repo(tmp_path)
    commit_all(repo, "bootstrap")

    completed = run_gate(repo, "--audit-waivers", "--today", "2026-04-08")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["mode"] == "waiver-audit"
    assert payload["summary"] == {
        "total": 0,
        "healthy": 0,
        "expiring_soon": 0,
        "expired": 0,
        "invalid": 0,
    }
    assert payload["findings"] == []
    assert payload["errors"] == []


def test_waiver_audit_flags_expired_and_expiring_entries_without_failing(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        waiver_entries=[
            {
                "path": "docs/legacy/old-a.md",
                "kind": "document",
                "reason": "Approved cleanup",
                "owner": "repo-governance",
                "approved_by_user": True,
                "approved_on": "2026-04-01",
                "expires_on": "2026-04-07",
                "ticket_or_context": "waiver-a",
            },
            {
                "path": "docs/legacy/old-b.md",
                "kind": "document",
                "reason": "Approved cleanup",
                "owner": "repo-governance",
                "approved_by_user": True,
                "approved_on": "2026-04-01",
                "expires_on": "2026-04-12",
                "ticket_or_context": "waiver-b",
            },
            {
                "path": "docs/legacy/old-c.md",
                "kind": "document",
                "reason": "Approved cleanup",
                "owner": "repo-governance",
                "approved_by_user": True,
                "approved_on": "2026-04-01",
                "expires_on": "2026-04-20",
                "ticket_or_context": "waiver-c",
            },
        ],
    )
    commit_all(repo, "bootstrap")

    completed = run_gate(repo, "--audit-waivers", "--today", "2026-04-08")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"] == {
        "total": 3,
        "healthy": 1,
        "expiring_soon": 1,
        "expired": 1,
        "invalid": 0,
    }
    statuses = {item["path"]: item["status"] for item in payload["findings"]}
    assert statuses == {
        "docs/legacy/old-a.md": "expired",
        "docs/legacy/old-b.md": "expiring_soon",
        "docs/legacy/old-c.md": "healthy",
    }


def test_waiver_audit_supports_warning_window_override(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        waiver_entries=[
            {
                "path": "docs/legacy/old-a.md",
                "kind": "document",
                "reason": "Approved cleanup",
                "owner": "repo-governance",
                "approved_by_user": True,
                "approved_on": "2026-04-01",
                "expires_on": "2026-04-12",
                "ticket_or_context": "waiver-a",
            }
        ],
    )
    commit_all(repo, "bootstrap")

    completed = run_gate(
        repo,
        "--audit-waivers",
        "--today",
        "2026-04-08",
        "--warning-window-days",
        "2",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["healthy"] == 1
    assert payload["summary"]["expiring_soon"] == 0
    assert payload["findings"][0]["status"] == "healthy"


def test_waiver_audit_fails_on_invalid_registry_entries(tmp_path: Path) -> None:
    repo = bootstrap_repo(
        tmp_path,
        waiver_entries=[
            {
                "path": "docs/*",
                "kind": "document",
                "reason": "Bad wildcard",
                "owner": "repo-governance",
                "approved_by_user": True,
                "approved_on": "2026-04-01",
                "expires_on": "2026-04-12",
                "ticket_or_context": "waiver-a",
            }
        ],
    )
    commit_all(repo, "bootstrap")

    completed = run_gate(repo, "--audit-waivers", "--today", "2026-04-08")

    assert completed.returncode == 1, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["invalid"] == 1
    assert payload["errors"][0]["status"] == "invalid"
    assert "wildcards are forbidden" in payload["errors"][0]["message"]
```

- [ ] **Step 2: Run the new audit tests to verify they fail**

Run:

```bash
pytest tests/unit/scripts/test_deletion_evidence_gate.py -q -o addopts='' -k "waiver_audit"
```

Expected: FAIL because `--audit-waivers` and `--warning-window-days` are not implemented yet and the JSON report does not contain audit fields.

- [ ] **Step 3: Commit the red-test checkpoint**

```bash
git add tests/unit/scripts/test_deletion_evidence_gate.py
git commit -m "test: add deletion waiver audit coverage"
```

### Task 2: Implement shared waiver-audit mode in the existing engine

**Files:**
- Modify: `scripts/compliance/deletion_evidence_gate.py`
- Test: `tests/unit/scripts/test_deletion_evidence_gate.py`

- [ ] **Step 1: Add audit-specific helper functions above `build_report()`**

Insert these helpers after `evaluate_target()` in `scripts/compliance/deletion_evidence_gate.py`:

```python
def classify_waiver_audit_status(expires_on: date, today: date, warning_window_days: int) -> tuple[str, int]:
    days_until_expiry = (expires_on - today).days
    if days_until_expiry < 0:
        return "expired", days_until_expiry
    if days_until_expiry <= warning_window_days:
        return "expiring_soon", days_until_expiry
    return "healthy", days_until_expiry


def build_waiver_audit_report(
    root_dir: str | Path = ".",
    *,
    ref: str = "HEAD",
    today: date | None = None,
    warning_window_days: int = 7,
) -> dict[str, Any]:
    root_path = Path(root_dir).resolve()
    today_value = today or date.today()

    waiver_entries, waiver_errors = load_waiver_entries(root_path, ref)
    findings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    internal_errors = [
        {
            "path": "",
            "kind": "waiver",
            "owner": "",
            "expires_on": None,
            "days_until_expiry": None,
            "status": "invalid",
            "message": message,
        }
        for message in waiver_errors
    ]

    for entry in waiver_entries:
        path_value = normalize_relative_path(str(entry.get("path", "")))
        kind = str(entry.get("kind", "")).strip()
        owner = str(entry.get("owner", "")).strip()
        expires_on = parse_iso_date(entry.get("expires_on"))
        validation_error = validate_waiver_entry(entry, today_value)

        if validation_error and validation_error.startswith("waiver expired on "):
            expires_on = parse_iso_date(entry.get("expires_on"))
            status, days_until_expiry = classify_waiver_audit_status(expires_on, today_value, warning_window_days)
            findings.append(
                {
                    "path": path_value,
                    "kind": kind,
                    "owner": owner,
                    "expires_on": expires_on.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "status": status,
                    "message": validation_error,
                }
            )
            continue

        if validation_error is not None:
            errors.append(
                {
                    "path": path_value,
                    "kind": kind,
                    "owner": owner,
                    "expires_on": entry.get("expires_on"),
                    "days_until_expiry": None,
                    "status": "invalid",
                    "message": validation_error,
                }
            )
            continue

        assert expires_on is not None
        status, days_until_expiry = classify_waiver_audit_status(expires_on, today_value, warning_window_days)
        findings.append(
            {
                "path": path_value,
                "kind": kind,
                "owner": owner,
                "expires_on": expires_on.isoformat(),
                "days_until_expiry": days_until_expiry,
                "status": status,
                "message": f"Waiver is {status.replace('_', ' ')}",
            }
        )

    all_errors = errors + internal_errors
    summary = {
        "total": len(findings) + len(all_errors),
        "healthy": sum(1 for item in findings if item["status"] == "healthy"),
        "expiring_soon": sum(1 for item in findings if item["status"] == "expiring_soon"),
        "expired": sum(1 for item in findings if item["status"] == "expired"),
        "invalid": len(all_errors),
    }

    return {
        "project_root": str(root_path),
        "mode": "waiver-audit",
        "evidence_ref": ref,
        "today": today_value.isoformat(),
        "warning_window_days": warning_window_days,
        "waiver_registry_path": WAIVER_REGISTRY_PATH,
        "findings": sorted(findings, key=lambda item: (item["expires_on"], item["path"])),
        "errors": all_errors,
        "summary": summary,
        "policy": {
            "head_only_authorization": True,
            "warning_window_days": warning_window_days,
            "waiver_registry_path": WAIVER_REGISTRY_PATH,
        },
    }
```

- [ ] **Step 2: Extend CLI parsing and main dispatch**

Replace the parser and dispatch section in `main()` with:

```python
    parser.add_argument("--audit-waivers", action="store_true")
    parser.add_argument("--warning-window-days", type=int, default=7)
```

and:

```python
    if args.warning_window_days < 0:
        raise SystemExit("--warning-window-days must be >= 0")

    if args.audit_waivers:
        report = build_waiver_audit_report(
            args.root_dir,
            ref=args.ref,
            today=today,
            warning_window_days=args.warning_window_days,
        )
        print_report(report, args.format)
        return 1 if report["errors"] else 0

    report = build_report(
        args.root_dir,
        scope=args.scope,
        ref=args.ref,
        paths=args.path,
        today=today,
    )
```

- [ ] **Step 3: Teach `print_report()` to render audit mode**

Update `print_report()` so the text branch handles audit mode before deletion mode:

```python
    if report.get("mode") == "waiver-audit":
        print("Deletion Waiver Audit")
        print("=====================")
        print(f"waiver_registry_path: {report['waiver_registry_path']}")
        print(f"today: {report['today']}")
        print(f"warning_window_days: {report['warning_window_days']}")
        print(f"total: {report['summary']['total']}")
        print(f"healthy: {report['summary']['healthy']}")
        print(f"expiring_soon: {report['summary']['expiring_soon']}")
        print(f"expired: {report['summary']['expired']}")
        print(f"invalid: {report['summary']['invalid']}")

        for item in report["findings"]:
            print(
                f"- {item['kind']} {item['path']}: {item['status']} "
                f"(expires_on={item['expires_on']}, days_until_expiry={item['days_until_expiry']})"
            )
        for item in report["errors"]:
            path_value = item.get("path", "")
            label = f"{item.get('kind', 'waiver')} {path_value}".strip()
            print(f"- {label}: invalid — {item['message']}")
        return
```

- [ ] **Step 4: Run the focused engine tests**

Run:

```bash
pytest tests/unit/scripts/test_deletion_evidence_gate.py -q -o addopts=''
```

Expected: PASS for existing deletion gate coverage plus the new waiver-audit cases.

- [ ] **Step 5: Commit the engine implementation**

```bash
git add scripts/compliance/deletion_evidence_gate.py tests/unit/scripts/test_deletion_evidence_gate.py
git commit -m "feat: add deletion waiver audit mode"
```

### Task 3: Add workflow coverage and the scheduled audit workflow

**Files:**
- Create: `tests/unit/scripts/test_deletion_waiver_audit_workflow.py`
- Create: `.github/workflows/deletion-waiver-audit.yml`

- [ ] **Step 1: Create the failing workflow registration test**

Create `tests/unit/scripts/test_deletion_waiver_audit_workflow.py` with:

```python
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
```

- [ ] **Step 2: Run the new workflow test to verify it fails**

Run:

```bash
pytest tests/unit/scripts/test_deletion_waiver_audit_workflow.py -q -o addopts=''
```

Expected: FAIL because `.github/workflows/deletion-waiver-audit.yml` does not exist yet.

- [ ] **Step 3: Add `.github/workflows/deletion-waiver-audit.yml`**

Create the workflow with:

```yaml
name: Deletion Waiver Audit

on:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  deletion-waiver-audit:
    name: Deletion Waiver Audit
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install audit dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml

      - name: Run deletion waiver audit
        run: |
          mkdir -p /tmp/deletion-waiver-audit
          python scripts/compliance/deletion_evidence_gate.py \
            --root-dir . \
            --format json \
            --audit-waivers \
            --warning-window-days 7 \
            > /tmp/deletion-waiver-audit/report.json

      - name: Upload waiver audit artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: deletion-waiver-audit-report
          path: /tmp/deletion-waiver-audit/report.json
          if-no-files-found: error

      - name: Add workflow summary
        if: always()
        run: |
          python -c 'import json, os; from pathlib import Path; report = json.loads(Path("/tmp/deletion-waiver-audit/report.json").read_text(encoding="utf-8")); summary_path = Path(os.environ["GITHUB_STEP_SUMMARY"]); findings = report.get("findings", []); earliest = findings[0]["expires_on"] if findings else "N/A"; affected = ", ".join(item["path"] for item in findings[:10]) or "none"; lines = ["# Deletion Waiver Audit", "", "- total: {}".format(report["summary"]["total"]), "- healthy: {}".format(report["summary"]["healthy"]), "- expiring_soon: {}".format(report["summary"]["expiring_soon"]), "- expired: {}".format(report["summary"]["expired"]), "- invalid: {}".format(report["summary"]["invalid"]), "- earliest_expires_on: {}".format(earliest), "- affected_paths: {}".format(affected)]; summary_path.write_text("\\n".join(lines), encoding="utf-8")'
```

- [ ] **Step 4: Run the workflow registration tests**

Run:

```bash
pytest \
  tests/unit/scripts/test_deletion_waiver_audit_workflow.py \
  tests/unit/scripts/test_github_actions_artifact_versions.py \
  tests/unit/scripts/test_ci_workflow_runtime_setup.py \
  -q -o addopts='' -k "deletion_waiver_audit_workflow or github_actions_workflows_do_not_use_deprecated_artifact_v3 or mainline_governance_summary_uses_single_line_python_command"
```

Expected: PASS, confirming the new workflow exists, uses `upload-artifact@v4`, and keeps summary generation parseable.

- [ ] **Step 5: Commit the workflow batch**

```bash
git add .github/workflows/deletion-waiver-audit.yml tests/unit/scripts/test_deletion_waiver_audit_workflow.py
git commit -m "test: cover deletion waiver audit workflow"
```

### Task 4: Update operator guide and run final verification

**Files:**
- Modify: `docs/guides/governance/DELETION_EVIDENCE_GATE.md`
- Modify: `openspec/changes/add-deletion-waiver-audit/tasks.md`

- [ ] **Step 1: Add a short waiver-audit section to the guide**

Append this section near the end of `docs/guides/governance/DELETION_EVIDENCE_GATE.md`:

````md
## Waiver 巡检与告警

仓库会通过 GitHub Actions 每日巡检 `HEAD:governance/waivers/deletion-evidence-waivers.yaml`，并支持手动触发。

巡检只做债务可见性告警，不阻塞普通开发流；但如果 waiver registry 本身结构损坏，workflow 会失败。

本地也可手动查看：

```bash
python scripts/compliance/deletion_evidence_gate.py \
  --root-dir . \
  --format text \
  --audit-waivers \
  --warning-window-days 7
```

输出会区分：

- `expired`
- `expiring_soon`
- `healthy`
````

- [ ] **Step 2: Mark the OpenSpec task checklist complete after implementation**

Update `openspec/changes/add-deletion-waiver-audit/tasks.md` from:

```md
- [ ] 1.1 Extend `scripts/compliance/deletion_evidence_gate.py` with a dedicated waiver audit mode
```

to:

```md
- [x] 1.1 Extend `scripts/compliance/deletion_evidence_gate.py` with a dedicated waiver audit mode
```

and mark every completed item in sections 1 through 3 as `[x]` only after the implementation and verification actually pass.

- [ ] **Step 3: Run the final verification set**

Run:

```bash
pytest \
  tests/unit/scripts/test_deletion_evidence_gate.py \
  tests/unit/scripts/test_deletion_evidence_gate_integration.py \
  tests/unit/scripts/test_stop_deletion_evidence_gate_hook.py \
  tests/unit/scripts/test_deletion_waiver_audit_workflow.py \
  tests/unit/scripts/test_github_actions_artifact_versions.py \
  -q -o addopts=''
```

Then run:

```bash
git diff --check
openspec validate add-deletion-waiver-audit --strict
```

Expected: all targeted tests pass, `git diff --check` is clean, and OpenSpec validation reports the change as valid.

- [ ] **Step 4: Commit the docs and checklist sync**

```bash
git add \
  docs/guides/governance/DELETION_EVIDENCE_GATE.md \
  openspec/changes/add-deletion-waiver-audit/tasks.md
git commit -m "docs: describe deletion waiver audit flow"
```
