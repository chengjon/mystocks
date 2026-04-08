# Technical Debt Governance

This directory is the canonical home for the `tech-debt-governance-2026q1` baseline artifacts.

## Scope

- Architecture source-of-truth references for governance work
- Spec conflict matrix with explicit owner and status fields
- Debt register with owner, DDL, and next action fields
- Governance execution board and weekly rollup artifacts

## What Is Canonical

- `ARCHITECTURE_SOURCE_OF_TRUTH.md`
- `SPEC_CONFLICT_MATRIX.md`
- `DEBT_REGISTER.md`
- `TEMPORARY_ARTIFACT_INVENTORY.md`
- `WEEKLY_GOVERNANCE_CADENCE.md`
- `TASK.md`
- `TASK-REPORT.md`
- `TASK-T01-REPORT.md` through `TASK-T10-REPORT.md`

## What Is Not Canonical

- `docs/reports/tasks/*`
  These are historical task-board snapshots and report samples. They remain for audit history only.
- `archive/legacy-root-archived/technical_debt/governance/*`
  These are superseded sidecar artifacts kept for traceability.
- Repository-root `TASK.md` and `TASK-REPORT.md`
  These remain the operational mainline coordination snapshots and are not the canonical 2026Q1 governance board.

## Operating Rules

1. Do not create parallel governance boards in other directories.
2. When a governance document is superseded, bridge to this directory instead of forking a new source.
3. Metrics in governance reports must label whether they are `measured`, `inferred`, or `historical_baseline`.
4. Cleanup or retirement decisions must cite both code-path and function-tree verdict sources before deletion approval.

## Key References

- Repo-wide rules: `architecture/STANDARDS.md`
- OpenSpec workflow: `openspec/AGENTS.md`
- Architecture governance capability: `openspec/specs/architecture-governance/spec.md`
- Technical debt charter: `docs/standards/technical-debt-governance-charter-v1.md`
- Baseline metrics: `reports/analysis/tech-debt-baseline.json`
- Deletion governance capability: `openspec/specs/directory-governance/spec.md`
- Deletion gate operations: `docs/guides/governance/DELETION_EVIDENCE_GATE.md`
