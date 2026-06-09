> Superseded body: do not publish this issue body directly.
> Its scope is merged into `15-decide-post-approval-plan.md`.

## What to build

Draft the first Core split batch from non-lifecycle-owned pure helpers,
including import smoke, targeted test scope, PM2 smoke, and rollback notes.
Do not move files in this issue.

## OpenSpec requirement

- F tasks 3.1-3.4
- F tasks 4.1-4.5

## Acceptance criteria

- Batch contains only one Core domain or a small pure-helper group.
- No lifecycle-owned module is included.
- Import smoke includes `from app.core.logger import logger`.
- PM2/backend smoke command is named.
- Rollback path is named.
- This issue does not move files unless a later implementation issue explicitly
  approves that movement.

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.

BLOCKED_BY_TODO: issue 10 Core import matrix.
