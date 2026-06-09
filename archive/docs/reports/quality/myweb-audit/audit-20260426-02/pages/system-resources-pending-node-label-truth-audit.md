# System Resources Pending Node Label Truth Audit

## Scope
- `/system/resources`

## Routed Defect Closed
- The system resources workspace leaked a faux resolved node label before the visible route had any verified resource snapshot.
- Because the hero already displayed `REQ_ID: N/A / STATUS: UNKNOWN`, the old `NODE: N/A` hero meta and `监控节点: N/A` stats card looked like current node truth instead of a pending first-load shell.

## Repair
- Updated `web/frontend/src/views/system/composables/useSystemResourcesPage.ts` so resource-dependent node labels now stay at `--` until a verified resource snapshot exists.
- Updated `web/frontend/src/views/system/Resources.vue` so both hero metadata and the stats strip consume the same unresolved node-label truth.
- Added owner regression coverage for the delayed-first-load pending-node-label path.
- Extended the routed Phase 4 Chromium proof so `/system/resources` now explicitly verifies `NODE: --` before the delayed resource request resolves.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/system/__tests__/Resources.spec.ts -t "keeps stats-strip counts unresolved while the first resource snapshot is still pending"` passed `1/1`
- Extended system regression:
  - `npx vitest run src/views/system/__tests__/Resources.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` passed `30/30`
- Routed browser verification:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "System-Resources keeps stats-strip counts unresolved while the first resource snapshot is still pending"` passed on the repo default Playwright `chromium` runner
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` now lists `43` tests
- Controlled browser proof confirmed:
  - initial pending shell showed `REQ_ID: N/A`, `STATUS: UNKNOWN`, `NODE: --`, and stats-strip values `UNKNOWN / -- / -- / -- / --`
  - after releasing the delayed resource response, the same route promoted to `REQ_ID: req-phase4-system-resources-late`, `STATUS: WARNING`, `NODE: local-runtime`, and stats-strip values `WARNING / local-runtime / 1 / 1 / 1`

## Rule Feedback
- Reused the existing `numeric truth`, `request-provenance truth`, and `freshness truth` families in `myweb-audit v2.0`.
- Future system-observability audits should treat unresolved node/service labels the same way they treat unresolved sibling count cards whenever the route has not yet verified its primary snapshot.
