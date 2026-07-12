# Bug Artifacts

## Status

This directory is a retained bug-artifact slice.

It currently contains backup-style or exported bug records rather than a live issue tracker.

It is not a current bug queue by itself.

## Single Source of Truth

Use the narrowest canonical source that matches the question:

- shared governance and migration rules:
  - `architecture/STANDARDS.md`
- current implementation truth:
  - current code and fresh verification output
- current active remediation state:
  - repository-root `TASK.md`
  - repository-root `TASK-REPORT.md`
- current approved plan or governance adoption:
  - the owning task, report, or plan that explicitly cites the bug artifact

Files in `reports/bugs/` are retained records for traceability. They do not automatically define the current open-bug list or current severity register.

## Reading Rules

### 1. Backup or export files are historical by default

Observed file:

- `bug-reports-backup.jsonl`

This is a retained bug record artifact. Entries inside it must be read as historical imported or exported data unless a current task explicitly adopts a specific entry.

### 2. Status inside a bug artifact does not replace current verification

- A `FIXED` field inside a historical bug export does not prove the issue is fixed in current code.
- A `high` or `medium` severity inside a retained bug record does not automatically define today's issue priority.

If current bug state matters, verify against current code and current task context instead of inheriting the export verbatim.

### 3. Do not turn this directory into a second tracker

- Do not mirror active issue tracking here with hand-written status files.
- Do not create another “current open bugs” layer here unless an active task explicitly establishes one as canonical.
- If a retained bug artifact still matters, adoption should be recorded in the current task or governance record rather than in repeated wrapper files here.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- retained bug export or backup:
  - `bug-reports-backup.jsonl`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, governance reports, import/export workflows, or forensic needs
- function-tree verdict:
  - classify it as `historical bug export`, `adopted bug input`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a bug artifact.

## Temporary / Backup Guard

- Backup-style bug records should not be multiplied into additional parallel backup layers without an owning task.
- If future bug snapshots must be retained, document why they remain and what would allow later retirement.

## Non-Goals

This README does not:

- certify current open bug count
- replace fresh verification of any issue
- create a live issue tracker
- authorize deletion or merging of existing artifacts
