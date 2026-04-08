# Weekly Governance Cadence

## Purpose

This document defines the recurring operating cadence for the 2026Q1 technical debt governance baseline.

## Cadence

- Monday: board review and owner/DDL refresh
- Wednesday: conflict triage and blocker review
- Friday: weekly rollup publication in `technical_debt/governance/TASK-REPORT.md`

## Required Inputs

- `technical_debt/governance/ARCHITECTURE_SOURCE_OF_TRUTH.md`
- `technical_debt/governance/SPEC_CONFLICT_MATRIX.md`
- `technical_debt/governance/DEBT_REGISTER.md`
- `technical_debt/governance/TASK.md`
- `reports/analysis/tech-debt-baseline.json`
- `reports/governance/` evidence records when a governance task closes

## Required Outputs

- Updated `technical_debt/governance/TASK-REPORT.md`
- Task-specific updates in `technical_debt/governance/TASK-T01-REPORT.md` through `TASK-T10-REPORT.md`
- Bridge updates only when operational docs or indexes would otherwise point at stale governance truth

## Metric Taxonomy

Every metric in a governance report must be labeled as one of the following:

- `measured`
  Direct command output, CI result, generated report, or machine-produced registry state from the current reporting window
- `inferred`
  A conclusion derived from source inspection or cross-document comparison, not a direct measurement
- `historical_baseline`
  A frozen baseline value or historical snapshot used for comparison only

Do not merge these classes into one number or one verdict line.

## Cleanup and Retirement Review Rules

1. Before declaring a deletion-ready path, cite:
   - the code-path verdict source from `governance/deletion-evidence.yaml` or the active review evidence
   - the function-tree verdict source from `governance/function-tree/catalog.yaml`
2. Before declaring a compatibility layer, shim, or `*_new.py` removable, cite the migration completion and exit criteria from `architecture/STANDARDS.md`.
3. Temporary entrypoints, mechanical splits, and backup files must be tracked as governance debt until retired or formally accepted.

## Ownership Rules

1. Each open task in `technical_debt/governance/TASK.md` must have one owner and one DDL.
2. Any overdue task must appear in the Friday rollup with a blocker or recovery action.
3. If a historical artifact conflicts with a canonical artifact, the rollup must state which path is canonical.
