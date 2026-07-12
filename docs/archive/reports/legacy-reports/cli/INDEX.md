# CLI Coordination Artifacts

## Status

This directory is a retained legacy CLI-coordination slice.

In the current tracked repo state observed on `2026-04-07`, it contains only this `INDEX.md`.

It is not a current CLI coordination dashboard or a current work-assignment truth source.

## Single Source of Truth

Use the narrowest canonical source that matches the coordination question:

- shared governance rules:
  - `architecture/STANDARDS.md`
- current multi-CLI workflow rules:
  - `docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`
  - `docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`
- current live coordination truth:
  - active worktree state
  - current `TASK.md` and `TASK-REPORT.md` artifacts
  - fresh manager or workflow output from the active run

Do not treat `reports/cli/INDEX.md` as a current repo-wide coordination truth source.

## Reading Rules

### 1. Historical index metadata is not current truth

Previous values such as `最后更新` or `文档数量` described an older index snapshot, not the current repo state.

### 2. Previously cataloged report targets are not present in the current tracked slice

Measured on `2026-04-07`:

- `reports/cli/` contains only `INDEX.md`

That means prior entries such as:

- `CLI_2_URGENT_FIX_PRIORITY`
- `CLI_2_WORK_GUIDANCE`
- `CLI_2_WORK_GUIDANCE_UPDATED`
- `CLI_3_FRONTEND_PROGRESS`

must now be read as historical catalog labels, not as current tracked files under `reports/cli/`.

### 3. Do not build a second coordination control plane here

- Do not add hand-written "current CLI status" summaries here unless an active workflow explicitly establishes this directory as canonical.
- Do not mirror live worker or manager state here when that truth already belongs to the active task system and current worktrees.

## Current Tracked Artifacts

Examples observed on `2026-04-07`:

- legacy directory index:
  - `INDEX.md`

This list is illustrative, not an exhaustive contract for future coordination artifacts.

## Historical References Previously Cataloged Here

The following labels appeared in a previous form of this index:

- `CLI_2_URGENT_FIX_PRIORITY`
- `CLI_2_WORK_GUIDANCE`
- `CLI_2_WORK_GUIDANCE_UPDATED`
- `CLI_3_FRONTEND_PROGRESS`

As of `2026-04-07`, these names are retained only as historical catalog references. They are not current tracked files under `reports/cli/`.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, governance records, workflow tooling, or historical audit chains
- function-tree verdict:
  - classify it as `legacy CLI index`, `historical coordination reference`, `duplicate redundant`, or `pending classification`

Absence of active linked files is not enough to delete this directory entrypoint.

## Non-Goals

This index does not:

- certify current worker status
- replace live worktree inspection
- create a current CLI dashboard
- authorize deletion or merging of existing artifacts
