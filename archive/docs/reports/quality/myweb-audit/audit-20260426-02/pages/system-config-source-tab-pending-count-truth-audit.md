# System Config Source-Tab Pending Count Truth Audit

## Scope
- `/system/config`

## Routed Defect Closed
- The default `数据源` tab rendered source-dependent stat cards as `0 / 0 / ON / N/A` before any verified source-config snapshot existed.
- Because `sources` is the default active tab, this unresolved-first-load shell looked like a real empty inventory rather than an in-flight source-config sync.

## Repair
- Updated `web/frontend/src/views/system/Settings.vue` so the source-tab count cards are now gated on a verified source-config snapshot.
- Kept static capability truth (`写回能力`) visible because it does not depend on the source-config payload itself.
- Added owner regression coverage for the unresolved-first-load state and the later success transition.
- Added routed Phase 4 coverage for the same delayed source-config shell.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/system/__tests__/Settings.spec.ts` passed
- Routed browser verification:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "System-Config keeps sources-tab counts unresolved while the first source-config snapshot is still pending"` passed on the repo default Playwright `chromium` runner
- Controlled browser proof confirmed:
  - while the first `/api/v1/data-sources/config/` request was unresolved, `/system/config` showed `DATA: PENDING`, `REQ_ID: N/A`, `TIME: N/A`
  - the default source-tab stat strip stayed at `-- / -- / ON / N/A`
  - after the delayed request resolved, the same shell promoted to `3 / 2 / ON / req-phase4-config-late`

## Rule Feedback
- Reused the existing `numeric truth` family in `myweb-audit v2.0`.
- Future default-tab audits should treat unresolved count cards as defects even when the page also exposes a truthful runtime message, because the stat strip remains the more visually dominant shell.
