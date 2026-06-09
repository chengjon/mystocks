> Superseded body: do not publish this issue body directly.
> Its scope is merged into `14-build-shared-evidence-package.md`.

## What to build

Produce the Core import compatibility matrix with old import path, canonical
target path, wrapper/re-export strategy, lifecycle owner, monkeypatch consumers,
and rollback path. Do not move files in this issue.

## OpenSpec requirement

- F tasks 1.2-1.6
- F tasks 2.1-2.6

## Acceptance criteria

- Matrix covers high-risk Core paths including database, cache, security,
  socketio, and logger.
- Lifecycle-owned Core modules are identified and linked to E coordination.
- `app.core.logger` remains canonical.
- No file movement is performed.

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.
