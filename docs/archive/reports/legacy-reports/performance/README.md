# Performance Artifacts

## Status

This directory is a mixed performance-artifact slice, not a directory-wide live gate by itself.

It currently contains a combination of:

- baseline-like artifacts
- sampled timing outputs
- historical migration or experiment reports

Do not treat the directory name alone as proof that every file is a current performance truth source.

## Single Source of Truth

Use the narrowest canonical source that matches the performance question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- debt-governance execution rules:
  - `docs/standards/technical-debt-governance-charter-v1.md`
- current measured performance truth:
  - the fresh command output or report file explicitly cited by the active task
- current baseline truth:
  - the exact baseline artifact that the active task or report names, with date and command context

This directory does not, by itself, establish one universal current baseline for all performance work.

## Reading Rules

### 1. Separate measured, baseline, inferred, and historical

When reusing any number from this directory, classify it first:

- measured:
  - a value produced by a dated command, benchmark run, or captured sample
- baseline:
  - a frozen comparison point kept for later deltas
- inferred:
  - a conclusion drawn from measured data
- historical:
  - any older report, sample, or migration output not freshly re-verified

Historical files must not be restated as current measured truth without a fresh rerun.

### 2. Baseline files require file-level citation

Observed files include:

- `performance_baseline.json`
- `baseline.txt`
- `test_timing.csv`
- `gpu_migration_report.json`

If a task references one of these files as a baseline or evidence source, it must cite:

- exact file path
- measurement date or creation time
- command or producer context when known

Do not cite `reports/performance/` generically as if the whole directory were one baseline.

### 3. Sample outputs are not automatic merge gates

- `baseline.txt` is a retained text sample.
- `test_timing.csv` is a retained timing artifact.
- `gpu_migration_report.json` is a historical migration result.

None of these, by themselves, prove current release fitness for unrelated changes.

### 4. Do not create parallel performance scoreboards here

- Do not add another "current performance overall status" file here unless a task explicitly establishes it as the canonical measured output.
- Do not duplicate numbers from active CI, benchmark jobs, or current reports into a second summary layer.
- If a file needs interpretation, add that interpretation to the file itself or to the active report that cites it.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- baseline-like machine-readable artifact:
  - `performance_baseline.json`
- sampled text output:
  - `baseline.txt`
- sampled timing dataset:
  - `test_timing.csv`
- historical migration report:
  - `gpu_migration_report.json`

This list is illustrative, not an exhaustive inventory contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by tests, scripts, docs, audits, or performance comparison workflows
- function-tree verdict:
  - classify it as `active baseline`, `historical sample`, `historical report`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a performance artifact.

## Temporary / Backup Guard

- If future benchmark runs emit temporary files, do not normalize them into a permanent parallel baseline layer by default.
- If a retained backup, migration residue, or ad hoc sample must stay, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current repo performance
- replace fresh benchmark execution
- define a repo-wide universal performance gate
- authorize deletion or merging of any existing artifact
