# Monitoring Reports

## Status

This directory is a retained monitoring-topic container.

It currently contains:

- a monitoring guide and configuration explainer
- a dated monitoring verification report

It is not a live monitoring control plane or a directory-wide proof of current operational health.

## Single Source of Truth

Use the narrowest canonical source that matches the monitoring question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- current implementation truth:
  - current monitoring configuration, current code, and current running services
- current live monitoring status:
  - fresh service checks, fresh metrics, and current operational verification output
- current historical evidence:
  - the exact report file cited by the active task or governance record

Do not treat `reports/monitoring/INDEX.md` as a current repo-wide operational truth source.

## Reading Rules

### 1. Index metadata is navigation metadata, not a live verdict

Fields such as `最后更新` or `文档数量` describe the index snapshot itself. They do not certify the current health of the monitoring stack.

### 2. The tracked files in this directory serve different roles

Observed files on `2026-04-07`:

- [CLAUDE_MONITORING](CLAUDE_MONITORING.md)
  - monitoring architecture and configuration guidance
- [MONITORING_VERIFICATION_REPORT](MONITORING_VERIFICATION_REPORT.md)
  - dated Phase 6 verification evidence

These files should not be collapsed into one live operational verdict.

### 3. Historical verification does not replace current monitoring checks

- A historical verification pass does not prove the same stack is healthy today.
- A historical incomplete item does not prove the same gap still exists today.

If current monitoring state matters, rerun the relevant checks on current services and cite that exact output.

### 4. Do not build a second live monitoring dashboard here

- Do not add hand-written "current stack status" summaries here unless an active workflow explicitly makes this directory canonical.
- Do not mirror live metrics or service state here when that truth already belongs to the current monitoring stack and fresh verification output.

## Current Tracked Artifacts

Examples observed on `2026-04-07`:

- monitoring guide:
  - [CLAUDE_MONITORING](CLAUDE_MONITORING.md)
- dated verification report:
  - [MONITORING_VERIFICATION_REPORT](MONITORING_VERIFICATION_REPORT.md)
- directory entrypoint:
  - `INDEX.md`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, governance reports, verification workflows, or operational runbooks
- function-tree verdict:
  - classify it as `monitoring guide`, `historical verification report`, `directory entrypoint`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a monitoring artifact.

## Non-Goals

This index does not:

- certify current monitoring health
- replace live monitoring verification
- define a current repo-wide operational dashboard
- authorize deletion or merging of existing artifacts
