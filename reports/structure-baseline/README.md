# Structure Baseline Artifacts

## Status

This directory is a retained repository-structure baseline slice.

It currently contains textual snapshots of directory trees and structure reports captured at specific times.

It is not a directory-wide proof of the current repository structure.

## Single Source of Truth

Use the narrowest canonical source that matches the structure question:

- shared governance and migration rules:
  - `architecture/STANDARDS.md`
- current repository structure truth:
  - the current filesystem and current tracked files
- current adopted structure baseline:
  - the exact baseline artifact cited by the active task or governance record

Do not cite `reports/structure-baseline/` generically as if the whole directory were one current structure truth source.

## Reading Rules

### 1. Baseline files are snapshots, not live structure

Observed files include:

- `directory-structure-report.txt`
- `docs-tree-baseline.txt`
- `scripts-tree-baseline.txt`
- `src-tree-baseline.txt`

These files are retained structure snapshots. They must be read as dated baselines or comparison points, not as the live state of the repository.

### 2. Historical tree snapshots do not prove current layout

- A path present in a historical baseline may have changed, moved, or been removed since that snapshot.
- A path missing from a historical baseline may exist today.

If current structure matters, inspect the current repo tree instead of inheriting the snapshot as current truth.

### 3. Do not create a second live structure index here

- Do not add hand-written “current repo structure” summaries here unless an active task explicitly establishes one as canonical.
- Do not duplicate current filesystem truth in another parallel index layer under this directory.
- If a structure baseline still matters, adoption should be recorded in the current task or governance record.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- repo-wide or slice-specific structure snapshots:
  - `directory-structure-report.txt`
  - `docs-tree-baseline.txt`
  - `scripts-tree-baseline.txt`
  - `src-tree-baseline.txt`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, governance reports, or comparison workflows
- function-tree verdict:
  - classify it as `historical structure baseline`, `adopted baseline input`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a structure-baseline artifact.

## Temporary Artifact Guard

- Do not normalize ad hoc tree dumps into a permanent second baseline layer without an owning task.
- If a specific baseline file must stay for governance reasons, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current repository structure
- replace current filesystem inspection
- create a live structure dashboard
- authorize deletion or merging of existing artifacts
