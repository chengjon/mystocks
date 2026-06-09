# System Data Refresh Request Provenance Audit

## Scope
- Route: `/system/data`
- Canonical entry: `web/frontend/src/views/system/DataSource.vue`
- Batch: `system-batch-10`

## Finding
- Before repair, the routed page synthesized `cfg-<timestamp>` whenever a verified config payload arrived without request metadata.
- The same route could also replace the visible `REQ_ID` with a failed refresh request id even while the previous verified config rows remained on screen.

## Repair
- Moved visible request provenance to page-local verified snapshot state in `DataSource.vue`.
- Missing request metadata on a verified config payload now degrades to `REQ_ID: N/A`.
- Failed refresh after a verified sync now preserves the last verified `REQ_ID` and visible config rows while showing stale-refresh copy.

## Verification
- Component regression:
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts` passed `4/4`
- System-family regression:
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/API.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` passed `23/23`
- Type check:
  - `timeout 180s npm run type-check` passed
- Routed E2E structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `26` tests including two new `/system/data` provenance assertions
- Targeted live verification with Playwright-library + system `google-chrome`:
  - success without request metadata now renders `REQ_ID: N/A` and `当前请求 N/A`
  - success-then-refresh-fail keeps `REQ_ID: req-live-system-data-success`, preserves visible `AKShare 行情 / TDX 实时深度` rows, and renders `获取数据源配置失败，当前仍显示上次成功同步的数据源配置快照。`
  - natural PM2 `/system/data` still renders a real request id and `19` live config rows
