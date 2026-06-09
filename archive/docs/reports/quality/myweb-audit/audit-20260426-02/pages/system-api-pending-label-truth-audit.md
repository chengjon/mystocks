# System API Pending Label Truth Audit

## Scope
- `/system/api`

## Routed Defect Closed
- The system observability deck leaked faux summary labels for service name, version, and middleware count before the visible route had any verified system probe snapshot.
- Because the hero already displayed `REQ_ID: N/A / STATUS: UNKNOWN`, the old stats strip and content-shell meta looked like current probe truth instead of a pending first-load shell.

## Repair
- Updated `web/frontend/src/views/system/API.vue` so service name, version, and middleware count now stay at `-- / -- / --` until a verified system probe snapshot exists.
- Updated the same route so the `content-shell-meta` and backend status card reuse the same verified summary labels instead of leaking `N/A / 3` during the first unresolved probe.
- Added owner regression coverage for the delayed-first-load pending-label path.
- Extended the routed Phase 4 Chromium proof so `/system/api` now explicitly verifies the unresolved shell before the delayed system probe resolves.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/system/__tests__/API.spec.ts` passed
- Extended system regression:
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/Resources.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` passed
- Routed browser verification:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts:2591` passed on the repo default Playwright `chromium` runner
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` now lists `43` tests
- Controlled browser proof confirmed:
  - initial pending shell showed `REQ_ID: N/A`, `STATUS: UNKNOWN`, and stats-strip values `UNKNOWN / -- / -- / --`
  - `content-shell-meta` showed `REQ_ID: N/A / MIDDLEWARE: --`
  - after releasing the delayed system probe response, the same route promoted to `REQ_ID: req-phase4-system-api-pending-late`, `STATUS: HEALTHY`, and stats-strip values `HEALTHY / mystocks-backend / 2.0.0 / 3`

## Rule Feedback
- Reused the existing `numeric truth` and `request-provenance truth` families in `myweb-audit v2.0`.
- Future system-observability audits should treat summary labels and shell meta as one verified-snapshot contract whenever the route has not yet verified its primary probe payload.
