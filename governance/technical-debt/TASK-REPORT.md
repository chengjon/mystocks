# Tech Debt Governance Rollup (2026Q1)

## Week Window

- Start: 2026-04-08
- End: 2026-04-11
- Owner: main

## Summary

- Completed: 10 / 10
- In Progress: 0
- Blocked: 0
- Overdue: 0

## Task Snapshot

| ID | Status | Progress This Week | Risks/Blockers | Next Action |
| --- | --- | --- | --- | --- |
| T01 | done | Published canonical architecture source map | None | Keep source map current when governance entrypoints change |
| T02 | done | Seeded `SC-001`..`SC-020` with owners and statuses | None | Triage open and in-review conflicts during the next cadence window |
| T03 | done | Seeded `TD-001`..`TD-015` with owner, DDL, status, and next action | None | Refresh status on the next Friday rollup |
| T04 | done | Published canonical board, rollup, and per-task report pack | None | Keep future governance execution evidence in this directory |
| T05 | done | Added bridge references from root task docs and historical indexes | None | Extend bridges only if another stale entrypoint appears |
| T06 | done | Codified the rollup metric template and confirmed live governance audits already separate measured, inferred, and historical-baseline facts | None | Keep future rollups using the same evidence-labeled metric blocks |
| T07 | done | Linked migration and compatibility retirement rules into governance artifacts and pointed at reports that carry canonical-source, compatibility-surface, and exit-condition fields | None | Keep future convergence audits citing `architecture/STANDARDS.md` and the migration checklist |
| T08 | done | Confirmed governed cleanup audits already record both code-path and function-tree verdicts before any deletion recommendation | None | Keep future cleanup reviews citing both verdict layers before approval |
| T09 | done | Published initial weekly rollup to start the cadence | Cadence is seeded but not yet repeated | Publish the next weekly update on schedule |
| T10 | done | Archived `tech-debt-governance-2026q1` and promoted `architecture-governance` into live spec truth | None | Keep future governance spec changes landing in `openspec/specs/architecture-governance/spec.md` |

## Metrics

- `measured`
  - `openspec validate tech-debt-governance-2026q1 --strict` passed on 2026-04-08
  - `openspec archive tech-debt-governance-2026q1 --yes` promoted `openspec/specs/architecture-governance/spec.md` on 2026-04-08
  - `reports/governance/2026-04-07-reports-retirement-readiness-matrix.md` separates `measured`, `historical_baseline`, `inferred`, and `target`
  - `reports/governance/2026-04-07-reports-cli-retirement-readiness-audit.md` and `reports/governance/2026-04-07-reports-data-cleaning-retirement-readiness-audit.md` record both `code_path_verdict` and `function_tree_verdict`
  - `docs/reports/tasks/INDEX.md`, `docs/reports/tasks/TASK.md`, and `docs/reports/tasks/TASK-T01-REPORT.md` through `TASK-T04-REPORT.md` now carry explicit retirement notes that redirect historical `technical_debt/governance/*` citations to `governance/technical-debt/*`
  - `governance/technical-debt/TEMPORARY_ARTIFACT_INVENTORY.md` now defines the canonical class-level inventory for temporary entrypoints, mechanical splits, and backup files
  - `governance/technical-debt/WEEKLY_GOVERNANCE_CADENCE.md` and `reports/governance/README.md` now require explicit evidence sources for progress and closeout claims
  - `docs/reports/tasks/TASK.md` and `docs/reports/tasks/TASK-T05-REPORT.md` through `TASK-T10-REPORT.md` now mark blank-evidence drafts as unverified historical context only
  - `docs/guides/governance/DELETION_EVIDENCE_GATE.md` and `reports/governance/README.md` now explicitly subordinate deletion guidance to `openspec/specs/directory-governance/spec.md` plus the machine-truth registries
- `inferred`
  - Historical task snapshots and root mainline snapshots had overlapping discoverability and needed an explicit bridge
  - Archived sidecar governance artifacts were partially implemented but not canonical
- `historical_baseline`
  - `reports/analysis/tech-debt-baseline.json` remains the frozen debt baseline for comparison

## Decisions Needed

1. Confirm whether cleanup-readiness references need another explicit registry-path bridge in templates or reports (`SC-018`).
