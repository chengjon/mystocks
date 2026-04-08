## Context

The deletion evidence governance rollout introduced one canonical waiver registry:

- `governance/waivers/deletion-evidence-waivers.yaml`

and one shared enforcement engine:

- `scripts/compliance/deletion_evidence_gate.py`

Today that engine checks waiver validity only when a deletion action is already being evaluated.

## Goals

- Surface expired and soon-expiring deletion waivers proactively.
- Reuse the existing shared engine as the single logic source.
- Keep debt findings non-blocking.
- Publish one GitHub Actions summary and one uploaded artifact.
- Avoid writing versioned audit reports into the repository.

## Non-Goals

- Creating a second parser or expiry classifier inside workflow YAML
- Blocking ordinary PRs because of waiver age alone
- Auto-opening Issues
- Refactoring the shared engine into separate modules in this batch

## Decisions

### 1. Add one audit mode to the existing CLI

The shared engine will gain a dedicated waiver audit mode rather than a second standalone script.
This preserves one waiver validation implementation and one source of truth.

### 2. Audit the canonical HEAD registry only

The audit reads:

- `HEAD:governance/waivers/deletion-evidence-waivers.yaml`

This keeps audit semantics aligned with the hard deletion gate and prevents staged or worktree-only
edits from masquerading as committed truth.

### 3. Use three health states for valid waivers

Valid waivers classify into:

- `expired`
- `expiring_soon`
- `healthy`

`expiring_soon` uses a default 7-day inclusive warning window.

### 4. Keep debt findings green, fail only for broken governance artifacts

- expired and expiring-soon findings produce success exit codes
- unreadable YAML, malformed registry structure, or invalid waiver entries produce failure exit codes

This keeps the workflow advisory without hiding broken machine-readable governance data.

### 5. Keep reporting ephemeral

The workflow will write its JSON report to a runtime path, upload it as an artifact, and render a
summary in `GITHUB_STEP_SUMMARY`.

No new committed report file will be added under `governance/mainline/reports/` or another versioned
location.

## Risks / Trade-offs

- The shared engine CLI becomes slightly broader, but still remains the least duplicative design.
- Treating invalid waiver entries as failing conditions is stricter than simple advisory mode, but that
  strictness applies to broken governance truth, not to normal debt findings.

## Rollout

1. Land the OpenSpec change for waiver audit and workflow alerting.
2. Implement audit mode in `scripts/compliance/deletion_evidence_gate.py`.
3. Add the new scheduled/manual workflow.
4. Add unit tests and workflow registration tests.
5. Update the operator guide with the new audit mode.
