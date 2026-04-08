# Tech Debt Governance Rollup (2026Q1)

## Week Window

- Start: 2026-04-08
- End: 2026-04-11
- Owner: main

## Summary

- Completed: 7 / 10
- In Progress: 3
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
| T06 | doing | Codified metric taxonomy in the cadence document | First measured weekly dataset not yet attached | Apply taxonomy in the next recurring rollup |
| T07 | doing | Linked migration and compatibility retirement rules into governance artifacts | Rule adoption still depends on future task usage | Verify future cleanup work cites the references |
| T08 | doing | Linked cleanup readiness to code-path and function-tree evidence rules | First deletion-review usage still pending | Verify the next governed cleanup work cites both sources |
| T09 | done | Published initial weekly rollup to start the cadence | Cadence is seeded but not yet repeated | Publish the next weekly update on schedule |
| T10 | done | Archived `tech-debt-governance-2026q1` and promoted `architecture-governance` into live spec truth | None | Keep future governance spec changes landing in `openspec/specs/architecture-governance/spec.md` |

## Metrics

- `measured`
  - `openspec validate tech-debt-governance-2026q1 --strict` passed on 2026-04-08
  - `openspec archive tech-debt-governance-2026q1 --yes` promoted `openspec/specs/architecture-governance/spec.md` on 2026-04-08
- `inferred`
  - Historical task snapshots and root mainline snapshots had overlapping discoverability and needed an explicit bridge
  - Archived sidecar governance artifacts were partially implemented but not canonical
- `historical_baseline`
  - `reports/analysis/tech-debt-baseline.json` remains the frozen debt baseline for comparison

## Decisions Needed

1. Confirm whether temporary-entrypoint inventory should become a follow-up change or stay in T06-T08 governance follow-through.
2. Confirm whether archived sidecar governance notes need additional bridge text beyond the canonical index references.
