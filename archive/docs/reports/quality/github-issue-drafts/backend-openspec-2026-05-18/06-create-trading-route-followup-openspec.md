> Superseded body: do not publish this issue body directly.
> Its scope is merged into `15-decide-post-approval-plan.md`.

## What to decide

Create a follow-up OpenSpec proposal for `trading_runtime.py` versus
`trading_monitor.py` route ownership, or intentionally fold trading into a
broader route ownership proposal.

## OpenSpec requirement

- C tasks 1.9 and 2.4
- Orchestration blocking matrix: Trading router implementation

## Acceptance criteria

- Follow-up OpenSpec change ID is recorded.
- Proposal cites route table evidence for trading duplicate paths.
- Implementation remains blocked until the follow-up is approved.
- C does not accidentally migrate or delete trading routes.

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.

BLOCKED_BY_TODO: issue 2 route/OpenAPI evidence.
