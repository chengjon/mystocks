# Deletion Waiver Audit Design

## Context

The repository already enforces deletion governance through one shared engine:

- `scripts/compliance/deletion_evidence_gate.py`
- `.githooks/pre-commit`
- `.claude/hooks/stop-deletion-evidence-gate.sh`

That gate validates emergency waivers only when a governed deletion is attempted. This leaves one
operational blind spot: expired or soon-to-expire waivers can sit in
`governance/waivers/deletion-evidence-waivers.yaml` without any proactive visibility.

The approved scope for this batch is to add proactive, non-blocking waiver expiry audit and alerting
without creating a second governance logic source, without blocking ordinary PRs, and without writing
versioned report files back into the repository.

## Goals

- Reuse the existing shared deletion governance engine as the single logic source.
- Audit `HEAD:governance/waivers/deletion-evidence-waivers.yaml` proactively, even when no deletion is
  being attempted.
- Surface both expired waivers and waivers expiring within a default 7-day window.
- Run the audit daily and on manual `workflow_dispatch`.
- Publish GitHub Actions summary output plus one machine-readable artifact.
- Keep debt findings non-blocking for normal development flow.

## Non-Goals

- Introducing a second waiver parser in workflow YAML
- Blocking standard PRs or local commits because a waiver is old
- Auto-opening GitHub Issues
- Writing versioned audit reports into `governance/mainline/reports/` or another repository path
- Refactoring `deletion_evidence_gate.py` into multiple modules in this batch

## Decision Summary

### 1. Extend the existing shared engine instead of adding a parallel script

`scripts/compliance/deletion_evidence_gate.py` already owns:

- waiver registry loading
- exact-path validation
- expiry validation
- HEAD-only resolution

This batch extends that engine with a dedicated waiver audit mode instead of adding a new workflow-only
implementation or a second governance script.

### 2. Keep audit truth HEAD-only

The audit will inspect:

- `HEAD:governance/waivers/deletion-evidence-waivers.yaml`

This keeps audit semantics aligned with the existing deletion gate and prevents staged-but-unmerged
waiver edits from being treated as canonical truth.

### 3. Add one explicit audit mode to the existing CLI

The current CLI already supports deletion checking. The least disruptive extension is to add one audit
mode flag rather than reworking the script into subcommands.

Target shape:

```bash
python scripts/compliance/deletion_evidence_gate.py \
  --root-dir . \
  --format json \
  --audit-waivers \
  --warning-window-days 7
```

Design constraints:

- existing staged/worktree deletion flows remain unchanged
- audit mode bypasses deletion discovery logic entirely
- warning window defaults to `7`
- warning window can be overridden explicitly for deterministic tests or future tuning

### 4. Treat debt findings as non-blocking, registry corruption as blocking

Audit findings divide into two classes:

- Debt findings: `expired`, `expiring_soon`, `healthy`
- Registry failures: unreadable YAML, malformed registry structure, invalid waiver entries

Operational rule:

- expired and expiring-soon waivers return exit code `0`
- malformed registry content returns non-zero because the governance artifact itself is broken

This preserves the approved non-blocking posture while still catching broken machine-readable truth.

### 5. Use GitHub Actions summary plus artifact only

The workflow will not write a committed report into the repository. Instead it will:

- write the machine-readable report to a temporary runtime path
- upload that file as a GitHub Actions artifact
- write a compact human summary to `GITHUB_STEP_SUMMARY`

This keeps visibility high without creating a second long-lived report surface in the repo.

## Proposed Audit Output

The audit report should stay machine-readable and stable enough for CI summary generation.

```json
{
  "pass": true,
  "mode": "waiver-audit",
  "audit_date": "2026-04-08",
  "warning_window_days": 7,
  "waiver_registry_path": "governance/waivers/deletion-evidence-waivers.yaml",
  "summary": {
    "total": 0,
    "healthy": 0,
    "expiring_soon": 0,
    "expired": 0,
    "invalid": 0
  },
  "findings": [],
  "errors": []
}
```

Each finding should include enough context for summary rendering:

- `path`
- `kind`
- `owner`
- `expires_on`
- `days_until_expiry`
- `status` (`healthy`, `expiring_soon`, `expired`, or `invalid`)
- `message`

## Workflow Shape

Workflow name:

- `Deletion Waiver Audit`

Trigger policy:

- daily schedule
- `workflow_dispatch`

Execution pattern:

1. Checkout repository
2. Set up Python
3. Install only required runtime dependency (`pyyaml`)
4. Run the shared engine in waiver audit mode
5. Upload the generated JSON artifact
6. Render summary from that JSON artifact into `GITHUB_STEP_SUMMARY`

Proposed schedule baseline:

- once daily in UTC

The workflow remains green for debt findings and turns red only when the registry is structurally
invalid or unreadable.

## Test Strategy

Implementation should add:

1. Unit tests for audit mode
   - empty waiver registry
   - healthy waiver
   - waiver expiring within 7 days
   - expired waiver
   - warning-window override
   - malformed or invalid waiver entry handling
2. Workflow registration tests
   - daily schedule exists
   - `workflow_dispatch` exists
   - shared engine is invoked rather than inlined logic
   - summary and artifact steps are present

## Risks and Trade-offs

- Extending one script increases CLI responsibility slightly, but this is still preferable to creating
  a second logic source.
- A strict invalid-entry failure means malformed waiver rows will make the audit workflow red. That is
  intentional because broken machine-readable governance artifacts should not hide behind a
  non-blocking debt policy.
- Since the repository currently has an empty waiver table, the first rollout mostly proves plumbing.
  That is acceptable; the value is in having the alert path ready before waivers accumulate.

## Rollout

1. Add the approved OpenSpec change for waiver audit capability.
2. Implement audit mode inside the existing shared engine.
3. Add the dedicated GitHub Actions workflow with daily schedule and manual dispatch.
4. Add unit and workflow registration tests.
5. Update the deletion evidence guide with one small section for proactive waiver audit usage.
