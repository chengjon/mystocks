# System Data Pending Count Truth Audit

## Scope
- `/system/data`

## Routed Defect Closed
- The top-level system-data stats strip rendered config-dependent count cards as `0 / 0 / ON / N/A` before any verified config snapshot existed.
- Because the route shell stayed visibly pending, those counts looked like a real empty inventory instead of an unresolved first-load config sync.

## Repair
- Updated `web/frontend/src/views/system/DataSource.vue` so config-dependent count cards and visible count meta are now gated on a verified config snapshot.
- Kept static capability truth (`写回能力`) visible because it does not depend on the config payload itself.
- Added owner regression coverage for the unresolved-first-load state and the later success transition.
- Added routed Phase 4 coverage for the same delayed config shell.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts` passed
- Routed browser verification:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "System-Data keeps stats-strip counts unresolved while the first config snapshot is still pending"` passed on the repo default Playwright `chromium` runner
- Controlled browser proof confirmed:
  - while the first `/api/v1/data-sources/config/` request was unresolved, `/system/data` showed `REQ_ID: N/A`
  - the stats strip stayed at `-- / -- / ON / N/A`
  - after the delayed request resolved, the same shell promoted to `3 / 2 / ON / req-phase4-system-data-pending-late`

## Rule Feedback
- Reused the existing `numeric truth` family in `myweb-audit v2.0`.
- Future system-governance audits should treat top-level count cards as defects when they mirror empty arrays before any verified payload exists, even if the route also exposes a truthful pending runtime message.
