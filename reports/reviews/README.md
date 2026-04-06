# Review Artifacts

## Status

This directory is an archive-style review-output slice.

It currently contains timestamped review documents produced for specific review sessions.

It is not a current backlog, not a current bug queue, and not a current prioritization board by itself.

## Single Source of Truth

Use the narrowest canonical source that matches the question:

- shared governance and migration rules:
  - `architecture/STANDARDS.md`
- current code truth:
  - current code and fresh verification output
- current active tasks or ownership:
  - repository-root `TASK.md`
  - repository-root `TASK-REPORT.md`
- current approved plan or change context:
  - the relevant file under `docs/plans/` or `openspec/changes/`

Files under `reports/reviews/` are retained review artifacts for traceability. They do not automatically define the current repo-wide issue priority or acceptance state.

## Reading Rules

### 1. Review findings are historical unless re-verified

Observed files in this directory are timestamped review outputs, for example:

- `review-20260223-031831-9e70a2.md`
- `review-20260223-202118-558dc1.md`

Any finding, severity, or recommendation in these files must be read as historical analysis unless it has been freshly re-verified against current code.

### 2. Severity in a review file is not a standing global truth

- A `critical`, `high`, or `medium` finding in a historical review file does not automatically mean the issue is still present today.
- A “no issues found” statement in a historical review file does not prove the area remains healthy today.

If current risk matters, rerun verification on current code instead of inheriting old review severities.

### 3. Review artifacts do not replace issue tracking or execution tracking

- Do not treat this directory as the current remediation queue.
- Do not infer current ownership from the author or agent name inside a review file.
- Do not mirror current task state here with follow-up shim documents.

If a review finding is still relevant, it should be linked from the current task, plan, or governance record that has adopted it.

### 4. Do not spawn duplicate review summary layers

- Do not add a second index that re-summarizes every historical review result.
- Do not create a “current open findings” file here unless an active task explicitly establishes it as the canonical source.
- If context is needed, prefer one directory-level README over many repeated per-file disclaimers.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- timestamped consolidated review outputs:
  - `review-20260223-031831-9e70a2.md`
  - `review-20260223-202118-558dc1.md`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, governance reports, or review workflows
- function-tree verdict:
  - classify it as `historical review`, `adopted review input`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a review artifact.

## Temporary / Compatibility Guard

- Do not use this directory for temporary remediation notes, shim documents, or backup copies.
- If a review output still drives current work, the adoption should be recorded in the current task or governance artifact rather than turning this directory into a live control plane.

## Non-Goals

This README does not:

- confirm whether any historical finding is still open
- replace fresh review or testing on current code
- create a live issue register
- authorize deletion or merging of existing review artifacts
