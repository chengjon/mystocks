# Phase 7 Monitoring Artifacts

## Status

This directory is a retained phase-specific collaboration-monitoring artifact slice.

It currently contains text snapshots from a historical Phase 7 multi-CLI monitoring line.

It is not a directory-wide proof of current worker activity, current repo progress, or current coordination state.

## Single Source of Truth

Use the narrowest canonical source that matches the coordination question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- current coordination workflow rules:
  - `docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`
  - `docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`
- current live coordination truth:
  - current worktree state, current task artifacts, and fresh monitoring output from the active workflow
- current adopted historical evidence:
  - the exact file cited by the active task or governance record

Do not cite `reports/phase7_monitoring/` generically as if the whole directory were one current progress dashboard.

## Reading Rules

### 1. "latest" is still historical inside this directory

Observed files include:

- `hourly_2025-12-30.txt`
- `latest_progress.txt`
- `latest_progress_enhanced.txt`

Here, `latest_*` means the latest file within that historical monitoring line, not the latest current repo status.

### 2. Historical monitoring snapshots do not prove current worker state

- A file showing active workers at one historical timestamp does not prove those workers or file paths are active today.
- A file showing empty progress sections does not prove the current workflow is inactive.

If current coordination status matters, inspect the active worktrees, current task artifacts, and fresh monitoring output instead of inheriting these files as live truth.

### 3. Do not build a second live coordination control plane here

- Do not add hand-written "current progress" files here unless an active workflow explicitly establishes one as canonical.
- Do not mirror live manager-worker status here when that truth already belongs to the active task system and fresh monitoring output.
- If a historical monitoring snapshot still matters, its adoption should be recorded in the active task or governance record.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- dated monitoring snapshots:
  - `hourly_2025-12-30.txt`
- historical relative-entry snapshots:
  - `latest_progress.txt`
  - `latest_progress_enhanced.txt`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, governance reports, coordination workflows, or historical audits
- function-tree verdict:
  - classify it as `historical phase-monitor snapshot`, `adopted coordination evidence`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a monitoring artifact.

## Temporary Artifact Guard

- Do not normalize ad hoc progress dumps into a permanent second coordination dashboard without an owning workflow.
- If a specific monitoring artifact must remain tracked for governance reasons, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current worker activity
- replace live coordination inspection
- define a current repo-wide progress dashboard
- authorize deletion or merging of existing artifacts
