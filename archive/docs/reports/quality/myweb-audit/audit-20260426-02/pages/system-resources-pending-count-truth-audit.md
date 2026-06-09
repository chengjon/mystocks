# System Resources Pending Count Truth Audit

## Scope
- `/system/resources`

## Routed Defect Closed
- The system resources workspace leaked faux-zero process, alert, and dependency counts before the visible route had any verified resource snapshot.
- Because the hero already displayed `REQ_ID: N/A / STATUS: UNKNOWN`, the old `0 / 0 / 0` strip and `0 tracked` section headers looked like current node truth instead of a pending first-load shell.

## Repair
- Updated `web/frontend/src/views/system/Resources.vue` so resource-dependent stats-strip counts now stay at `-- / -- / --` until a verified resource snapshot exists.
- Updated the same route so `运行进程` and `依赖摘要` section headers stay at `-- tracked` until the first verified resource snapshot lands.
- Added owner regression coverage for the delayed-first-load pending-count path.
- Extended the routed Phase 4 Chromium proof so `/system/resources` now explicitly verifies the unresolved shell before the delayed resource request resolves.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/system/__tests__/Resources.spec.ts` passed `3/3`
- Extended system regression:
  - `npx vitest run src/views/system/__tests__/Resources.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` passed `28/28`
- Routed browser verification:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "System-Resources keeps stats-strip counts unresolved while the first resource snapshot is still pending"` passed on the repo default Playwright `chromium` runner
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` now lists `41` tests
- Controlled browser proof confirmed:
  - initial pending shell showed `REQ_ID: N/A`, `STATUS: UNKNOWN`, and stats-strip values `UNKNOWN / N/A / -- / -- / --`
  - both resource section headers showed `-- tracked`
  - after releasing the delayed resource response, the same route promoted to `REQ_ID: req-phase4-system-resources-late`, `STATUS: WARNING`, and stats-strip values `WARNING / local-runtime / 1 / 1 / 1`

## Rule Feedback
- Reused the existing `numeric truth`, `request-provenance truth`, and `freshness truth` families in `myweb-audit v2.0`.
- Future system-observability audits should treat section-header counters as part of the same visible summary contract as the top-level stats strip whenever the route has not yet verified its primary snapshot.
