> Superseded body: do not publish this issue body directly.
> Its scope is merged into `15-decide-post-approval-plan.md`.

## What to decide

Create a follow-up OpenSpec proposal for `backup_recovery.py` versus
`backup_recovery_secure/` route ownership and security boundary.

## OpenSpec requirement

- C tasks 1.9 and 2.5
- G tasks 2.6
- Orchestration blocking matrix: Backup router implementation

## Acceptance criteria

- Follow-up OpenSpec change ID is recorded.
- Proposal cites route table evidence for backup duplicate paths.
- `backup_recovery_secure/cleanup_old_backups.py` is classified as domain route
  ownership, health/status taxonomy, or both with a clear owner.
- Implementation remains blocked until the follow-up is approved.

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.

BLOCKED_BY_TODO: issue 2 route/OpenAPI evidence.
