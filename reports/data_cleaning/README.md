# Data-Cleaning Artifacts

## Status

This directory is a retained data-cleaning artifact slice.

It currently contains dated run outputs from specific cleaning or checking runs.

It is not a directory-wide proof of current data quality or current data-cleaning health.

## Single Source of Truth

Use the narrowest canonical source that matches the data-cleaning question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- current implementation and data state:
  - current code, current database state, and fresh verification output
- current adopted data-cleaning evidence:
  - the exact artifact file cited by the active task, report, or governance record

Do not cite `reports/data_cleaning/` generically as if the whole directory were one current cleaning verdict.

## Reading Rules

### 1. Dated files are point-in-time snapshots

Observed files include:

- `daily_20260107.json`

These files are retained outputs from a specific run window. Their counts, warnings, and table states must be read as dated snapshots, not as the current repo truth.

### 2. Historical cleaning results do not prove current data state

- A warning or zero-count result in one retained artifact does not prove the same condition still exists today.
- A clean historical run does not prove the current database state is still clean.

If current data-cleaning status matters, rerun the relevant check on current code and current data, then cite that exact run.

### 3. Do not build a second live data-quality dashboard here

- Do not add hand-written "current data cleaning status" summaries here unless an active task explicitly establishes one as canonical.
- Do not mirror current database-health or repair status here when that truth already belongs to fresh verification output and the owning task.
- If a retained artifact still matters, its current use should be recorded in the active task or governance record.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- dated machine-readable cleaning outputs:
  - `daily_20260107.json`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, governance reports, repair workflows, or follow-up validation work
- function-tree verdict:
  - classify it as `historical data-cleaning snapshot`, `adopted cleaning evidence`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a data-cleaning artifact.

## Temporary Artifact Guard

- Do not normalize ad hoc cleaning reruns into a permanent parallel history layer without an owning task.
- If a specific cleaning artifact must remain tracked for governance reasons, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current data quality
- replace fresh data-cleaning verification
- create a live repo-wide data-quality board
- authorize deletion or merging of existing artifacts
