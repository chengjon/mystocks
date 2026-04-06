# Legacy Task Archives

## Status

This directory is an archive-only slice of historical task artifacts.

- It is not a current execution board.
- It is not a current handoff queue.
- It is not a parallel source of truth for active planning, ownership, or acceptance.

## Single Source of Truth

For current task state, use only:

- repository-root `TASK.md`
- repository-root `TASK-REPORT.md`
- `reports/governance/` focused closeout records

Files in this directory are retained only for historical traceability.

## Archive Rules

### 1. No duplicate active layer

- Do not restate active task status here.
- Do not create a second planning layer here to mirror current work.
- If a historical document needs context, add that context at the directory entry level or current canonical source, not by spawning repeated per-file shims.

### 2. Compatibility / shim / transition rule

- This directory is not a compatibility layer for live workflow.
- Do not place `*_new.py`, shim notes, temporary migration wrappers, or transitional task boards here.
- If a migration artifact still needs to exist, its canonical source, compatibility surface, and exit condition must be documented outside this archive slice.

### 3. Migration completion / exit condition

- A task document may remain here only as an archive record.
- It is considered fully retired from active workflow once:
  - no current process uses it as the execution entry,
  - current truth has a canonical replacement,
  - readers are redirected to that canonical replacement.
- Deleting or relocating an archived item still requires explicit governance review.

### 4. Deletion guard

Before deleting any file in this directory, complete both checks:

- code-path verdict:
  - confirm it is not linked from active indexes, guides, scripts, task exporters, or other runtime/documentation entry points
- function-tree verdict:
  - classify it as `historical archive`, `duplicate archive`, or another explicit archival state

Absence of recent edits is not enough to delete it.

### 5. Metric wording

Any numbers inside archived documents must be read as one of:

- historical measured value
- historical target / plan
- historical inference

Do not reuse archived numbers as current measured status unless they are freshly re-verified in the current canonical source.

### 6. Mechanical splits / temp files / backups

- Do not expand this directory with mechanical splits, temporary entry files, or backup copies.
- If archival grouping is needed, prefer one directory-level README or index note over multiple duplicated explainers.

## Current Members

- `FRONTEND_HISTORY_MIGRATION.md`
- `PHASE_2_SAGA_ROLLOUT.md`
- `TEST_CLI_TASK.md`
