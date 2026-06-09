> Publication hold: do not publish this issue body as originally drafted.
> G-line implementation evidence now covers the original taxonomy/canonical-path
> prerequisite work. Retain this file for audit or reclassify it into a residual
> OpenAPI documentation stabilization / PM2 approval follow-up before publishing.

## What to build

Build the health/status taxonomy and consumer matrix for PM2, monitoring, CI,
frontend, tests, scripts, and docs. This is evidence-only work unless a later
approved issue explicitly allows route mutation.

Existing P3 evidence to reuse:

- P3-A5 health/status taxonomy decision record in
  `docs/reports/quality/backend-audit-phase3-decision-records.md`.
- 52-route health/status inventory referenced by the P3 progress artifacts.

Remaining scope is to formalize that taxonomy inside OpenSpec G, reconcile it
with current route/OpenAPI evidence, and prepare the canonical health/status
path decision. Do not create a duplicate health proposal.

## OpenSpec requirement

- G tasks 1.6-1.8
- G tasks 2.1-2.7

## Acceptance criteria

- Each health/status endpoint is classified as platform liveness/readiness,
  system service health, platform status, domain smoke/status,
  metrics/observability, adapter/database diagnostic, example, or embedded app.
- Consumer matrix lists active, compatibility, and documentation-only consumers.
- `/health/readiness` absence is confirmed unless intentionally added by later
  approval.
- Existing P3-A5 taxonomy and 52-route inventory are cited or superseded with
  fresher evidence.
- The output identifies the canonical `/health` handler candidate and any
  remaining HITL decision needed for compatibility aliases.
- No route mutation is performed.

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.

BLOCKED_BY_TODO: issue 2 route/OpenAPI evidence.
