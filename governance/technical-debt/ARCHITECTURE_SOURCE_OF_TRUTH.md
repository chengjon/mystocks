# Architecture Source of Truth

## Purpose

This document defines the authoritative references used by governance reviews so that task boards,
cleanup decisions, migration exit calls, and debt reports do not drift across parallel documents.

## Authoritative References by Domain

| Domain | Canonical Reference | Evidence Class | Owner | Notes |
| --- | --- | --- | --- | --- |
| Repo-wide engineering rules | `architecture/STANDARDS.md` | policy | main | Top-level source for approval gates, migration closure, deletion rules, and single-source-of-truth policy |
| OpenSpec workflow | `openspec/AGENTS.md` | policy | main | Authoritative workflow for proposal, implementation, and archive stages |
| OpenSpec project conventions | `openspec/project.md` | policy | main | Project-specific conventions that active changes must follow |
| Architecture governance capability | `openspec/specs/architecture-governance/spec.md` | policy | main | Live capability truth for governance SoT, conflict matrix, debt register, execution board, and cadence |
| Technical debt charter | `docs/standards/technical-debt-governance-charter-v1.md` | policy | main | Governs debt gates, exceptions, baselines, and weekly KPI language |
| Technical debt baseline metrics | `reports/analysis/tech-debt-baseline.json` | historical_baseline | main | Frozen baseline; do not mix with current measured results |
| Governance execution artifacts | `governance/technical-debt/` | operational | main | Canonical directory for this governance baseline |
| Mainline coordination snapshots | `TASK.md`, `TASK-REPORT.md`, `governance/mainline/task-cards/` | operational | main | Operational mainline coordination, not the canonical governance board |
| Deletion governance rules | `openspec/specs/directory-governance/spec.md` | policy | main | Capability truth for directory deletion and waiver audit behavior |
| Deletion evidence registries | `governance/deletion-evidence.yaml`, `governance/waivers/deletion-evidence-waivers.yaml` | machine_truth | main | Exact-path deletion authorization and waiver registry |
| Cleanup verdict inputs | `governance/function-tree/catalog.yaml` | machine_truth | main | Function-tree verdict source used before governed deletion |
| Deletion gate operations | `docs/guides/governance/DELETION_EVIDENCE_GATE.md` | runbook | main | Operator guide for the shared deletion evidence engine |

## Governance-Specific Interpretation Rules

1. `policy` sources define what is allowed.
2. `machine_truth` sources define exact governed inputs or baselines.
3. `operational` sources capture active work state and evidence links.
4. `historical_baseline` sources record frozen comparison points and must never be reported as current measurements.
5. `runbook` sources explain how to operate a system but do not override policy or machine truth.

## Migration and Retirement Hooks

- Compatibility layer, shim, and `*_new.py` retirement rules come from `architecture/STANDARDS.md`.
- Migration completion and exit criteria come from `architecture/STANDARDS.md` and must be cited before declaring a legacy path removable.
- Deletion approval requires both code-path and function-tree verdicts from the canonical governance sources above.

## Change Control

1. Every governance update must reference a task ID from `governance/technical-debt/TASK.md`.
2. If a historical report conflicts with this map, treat the historical report as context only.
3. New governance entrypoints must be added here instead of introduced as sidecar truth.
