# Tech Debt Governance Execution Board (2026Q1)

This is the canonical governance execution board for `tech-debt-governance-2026q1`.

## Usage

- Status: `todo` | `doing` | `blocked` | `done`
- Priority: `P0` | `P1` | `P2`
- Root `TASK.md` remains the operational mainline coordination snapshot and is not replaced by this board.

| ID | Task | Priority | Owner | DDL | Dependencies | Status | Acceptance Criteria | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | Publish architecture source of truth | P0 | main | 2026-04-08 | - | done | Canonical source map published with governance domains and evidence classes | `technical_debt/governance/ARCHITECTURE_SOURCE_OF_TRUTH.md` |
| T02 | Seed spec conflict matrix | P0 | main | 2026-04-08 | T01 | done | `SC-001`..`SC-020` recorded with owner, status, and next action | `technical_debt/governance/SPEC_CONFLICT_MATRIX.md` |
| T03 | Seed debt register | P0 | main | 2026-04-08 | T01 | done | `TD-001`..`TD-015` recorded with owner, DDL, status, and next action | `technical_debt/governance/DEBT_REGISTER.md` |
| T04 | Publish governance board and report pack | P0 | main | 2026-04-08 | T01 | done | Canonical board, rollup, and T01..T10 report templates published | `technical_debt/governance/TASK.md`, `technical_debt/governance/TASK-REPORT.md`, `technical_debt/governance/TASK-T01-REPORT.md` |
| T05 | Bridge historical indexes and root task snapshots | P0 | main | 2026-04-08 | T01,T04 | done | Historical indexes and root task snapshots point to the canonical governance directory | `docs/INDEX.md`, `docs/reports/tasks/INDEX.md`, `docs/reports/technical_debt/INDEX.md`, `TASK.md`, `TASK-REPORT.md` |
| T06 | Enforce metric taxonomy in governance reporting | P1 | main | 2026-04-15 | T03,T04 | doing | Governance reports distinguish measured, inferred, and historical-baseline metrics | `technical_debt/governance/WEEKLY_GOVERNANCE_CADENCE.md` |
| T07 | Surface migration and compatibility retirement rules | P1 | main | 2026-04-16 | T01,T06 | doing | Governance artifacts cite migration exit rules and compatibility retirement requirements | `technical_debt/governance/ARCHITECTURE_SOURCE_OF_TRUTH.md`, `technical_debt/governance/WEEKLY_GOVERNANCE_CADENCE.md` |
| T08 | Tie cleanup readiness to code-path and function-tree verdicts | P1 | main | 2026-04-17 | T01,T06 | doing | Cleanup-related governance work cites both verdict sources before deletion approval | `technical_debt/governance/WEEKLY_GOVERNANCE_CADENCE.md`, `technical_debt/governance/DEBT_REGISTER.md` |
| T09 | Run the first recurring weekly governance review | P1 | main | 2026-04-11 | T01,T02,T03,T04,T05 | done | A weekly rollup is published with progress, blockers, and taxonomy-aware metrics | `technical_debt/governance/TASK-REPORT.md` |
| T10 | Prepare capability archive handoff | P2 | main | 2026-04-22 | T01,T02,T03,T04,T05,T09 | todo | Archive handoff notes are ready once adoption review concludes | `openspec/changes/tech-debt-governance-2026q1/` |
