> Superseded body: do not publish this issue body directly.
> Its scope is merged into `15-decide-post-approval-plan.md`.

## What to decide

Select exactly one low-risk representative DI pilot and define override,
teardown, compatibility getter, rollback, and verification expectations.

## OpenSpec requirement

- E tasks 2.1-2.5

## Acceptance criteria

- Only one pilot candidate is selected.
- If the pilot touches Core modules, F matrix dependency is resolved.
- Dependency override strategy is named.
- Teardown artifact type is named.
- Rollback path is named.
- Decision record states whether `web/backend/CONTEXT.md`,
  `docs/FUNCTION_TREE.md`,
  or related governance documents require updates.
- This issue does not implement the pilot.

## Blocked by

BLOCKED_BY_TODO: issue 10 Core import matrix.

BLOCKED_BY_TODO: issue 11 singleton/getter lifecycle inventory.
