> Publication hold: do not publish this issue body as originally drafted.
> G-line implementation evidence already records the canonical health/status path
> decisions. Retain this file for audit or reclassify it into a residual OpenAPI
> documentation stabilization / PM2 approval follow-up before publishing.

## What to decide

Approve canonical liveness, readiness, services health, and status endpoint
boundaries, including compatibility and deprecation timing.

## OpenSpec requirement

- G tasks 2.1-2.7

## Acceptance criteria

- Decision record names canonical liveness, readiness, services health, and
  status paths.
- Compatibility paths and deprecation timing are explicit.
- PM2, monitoring, CI, frontend, and test consumers are preserved or migration
  is explicitly approved.
- Rollback trigger per endpoint category is named.
- Decision record states whether `web/backend/CONTEXT.md`,
  `docs/FUNCTION_TREE.md`,
  or related governance documents require updates.

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.

BLOCKED_BY_TODO: issue 2 route/OpenAPI evidence.

BLOCKED_BY_TODO: issue 8 health/status taxonomy.
