# Planning Artifacts

## Status

This directory is a retained planning-artifact slice.

It currently contains a combination of:

- historical workplans
- backlog or queue-style TSV artifacts
- generated inventory files used to support planning

It is not a current execution board by itself.

## Single Source of Truth

Use the narrowest canonical source that matches the planning question:

- shared governance and migration rules:
  - `architecture/STANDARDS.md`
- debt-governance execution rules:
  - `docs/standards/technical-debt-governance-charter-v1.md`
- active proposal or spec truth:
  - the relevant change under `openspec/changes/`
- approved implementation-plan truth:
  - the specific file under `docs/plans/` that the active task references
- current execution or ownership state:
  - repository-root `TASK.md`
  - repository-root `TASK-REPORT.md`

Files under `reports/plans/` may support planning traceability, but they do not automatically become current plan truth for unrelated work.

## Reading Rules

### 1. Historical plan vs current execution must stay separate

- A plan file describes intended work at a specific time.
- A backlog or inventory file describes candidate scope.
- Neither is enough to prove current execution status unless an active task explicitly adopts it.

If current execution state is needed, read the active execution source instead of inferring from stale plan artifacts.

### 2. Inventory files are scan outputs, not a second governance layer

Observed inventory files in this directory include:

- `reports/plans/inventory/python_source_gt800.tsv`
- `reports/plans/inventory/python_test_gt1000.tsv`
- `reports/plans/inventory/ts_gt500.tsv`
- `reports/plans/inventory/vue_gt500.tsv`

These files are planning inputs.

They must not be treated as:

- current implementation status for the whole repo
- deletion authorization
- proof that a planned split is still required today without re-verification

### 3. Backlog tables require fresh adoption before reuse

Observed backlog-style artifact:

- `reports/plans/large_file_splitting_backlog.tsv`

Before reusing rows from a backlog file as current work truth, confirm:

- the target path still exists
- the current code shape still matches the old planning assumption
- the active owner or task has explicitly adopted that row

### 4. Do not spawn parallel planning layers

- Do not add another summary file here that mirrors current roadmap or active execution state.
- Do not use this directory as a live substitute for `docs/plans/`, OpenSpec, or current task boards.
- If a historical planning artifact needs context, add context at the directory-entry level or the current canonical source, not via repeated per-file shim notes.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- historical or retained planning narrative:
  - `large_file_splitting_workplan.md`
- backlog queue artifact:
  - `large_file_splitting_backlog.tsv`
- generated inventory inputs:
  - `inventory/*.tsv`

This list is illustrative, not a full registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current tasks, docs, audits, exporters, or governance workflows
- function-tree verdict:
  - classify it as `active adopted plan`, `historical plan`, `planning input`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a planning artifact.

## Migration / Compatibility Guard

- Do not introduce shim plans, `*_new.py` notes, temporary entry files, or mechanical split artifacts here as a long-lived pattern.
- If a migration plan temporarily points to compatibility layers or backup paths, the owning governance record must still state canonical source, compatibility surface, verification command, and exit condition outside this directory.

## Non-Goals

This README does not:

- mark every plan here as still active
- replace the current roadmap, spec, or execution board
- authorize cleanup of any plan artifact
- serve as a generated index of all planning files
