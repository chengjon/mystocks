# Weekly Governance Cadence

## Purpose

This document defines the recurring operating cadence for the 2026Q1 technical debt governance baseline.

## Cadence

- Monday: board review and owner/DDL refresh
- Wednesday: conflict triage and blocker review
- Friday: weekly rollup publication in `governance/technical-debt/TASK-REPORT.md`

## Required Inputs

- `governance/technical-debt/ARCHITECTURE_SOURCE_OF_TRUTH.md`
- `governance/technical-debt/SPEC_CONFLICT_MATRIX.md`
- `governance/technical-debt/DEBT_REGISTER.md`
- `governance/technical-debt/TASK.md`
- `reports/analysis/tech-debt-baseline.json`
- `reports/governance/` evidence records when a governance task closes

## Required Outputs

- Updated `governance/technical-debt/TASK-REPORT.md`
- Task-specific updates in `governance/technical-debt/TASK-T01-REPORT.md` through `TASK-T10-REPORT.md`
- Bridge updates only when operational docs or indexes would otherwise point at stale governance truth

## Friday Rollup Structure

Each Friday rollup should keep one explicit block per metric class:

- `measured`
  - command output, CI result, generated report, or current machine-readable registry state
  - each line should cite either the command used or the evidence path
- `inferred`
  - conclusions or prioritization derived from the measured inputs above
  - each line should name the measured source it depends on
- `historical_baseline`
  - frozen comparison points such as `reports/analysis/tech-debt-baseline.json`
  - each line must remain dated or clearly labeled as baseline-only
- `target`
  - optional future-state goal, kept separate from measured or baseline facts

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
3. Temporary entrypoints, mechanical splits, and backup files must be tracked as governance debt until retired or formally accepted, using `governance/technical-debt/TEMPORARY_ARTIFACT_INVENTORY.md` as the canonical class-level inventory.

## Migration Closure Checklist

When a governance review covers migration or compatibility retirement, the record must keep these fields explicit:

- canonical source after convergence
- retained compatibility surface, if any
- current callers or consumers
- verification command set
- old-path exit condition

If any field is unknown, the migration remains open and the report must say so directly.

## Current Evidence Examples

The following records already exercise the governance rules above and can be cited as working examples:

- metric taxonomy in active governance reports:
  - `reports/governance/2026-04-07-reports-retirement-readiness-matrix.md`
  - `reports/governance/2026-04-07-reports-cli-retirement-readiness-audit.md`
  - `reports/governance/2026-04-07-reports-data-cleaning-retirement-readiness-audit.md`
- compatibility and migration-exit reporting:
  - `reports/governance/README.md`
  - `reports/governance/2026-04-06-directory-entrypoint-completeness-audit.md`
  - `reports/governance/2026-04-07-reports-cli-retirement-readiness-audit.md`
- two-layer cleanup judgment before deletion:
  - `reports/governance/2026-04-07-reports-retirement-readiness-matrix.md`
  - `reports/governance/2026-04-07-reports-data-cleaning-retirement-readiness-audit.md`
  - `reports/governance/2026-04-07-reports-quant-retirement-readiness-audit.md`

## Ownership Rules

1. Each open task in `governance/technical-debt/TASK.md` must have one owner and one DDL.
2. Any overdue task must appear in the Friday rollup with a blocker or recovery action.
3. If a historical artifact conflicts with a canonical artifact, the rollup must state which path is canonical.
