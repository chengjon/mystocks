# System Config Source Tab Contract Truth Audit

## Scope
- `/system/config`

## Routed Defect Closed
- The default `数据源` tab was still showing embedded sample KPI cards and sample inventory rows instead of the real system data-source config contract.
- The same tab also inherited sibling-slice provenance, so the header reported `DATA: SUMMARY` even though the source-tab surface had not loaded any source-config truth.

## Repair
- Updated `web/frontend/src/views/system/Settings.vue` so the default source tab calls `monitoringApi.getDataSourceConfig()` during page load.
- Reused the existing endpoint normalizer from `dataManagementData.ts` to render live endpoint descriptions plus stable `endpoint_name` values.
- Replaced sample source-tab KPI cards and sample `priority / latency / quota` table columns with honest route-local values and endpoint-oriented columns.
- Switched the source-tab header and runtime message to tab-local provenance so the page reports `REAL`, `PENDING`, or `UNAVAILABLE` for the active tab instead of inheriting monitor-slice state.
- Added regression coverage for the canonical page, wrapper page, and routed E2E matrix.

## Verification Evidence
- Unit regression:
  - `npx vitest run src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` passed
- Extended system regression:
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` passed
- Live browser verification with Playwright-library + system `google-chrome`:
  - `/system/config` now shows `DATA: REAL`
  - the source-tab strip now shows `19 / 19 / ON / <REQ_ID>` with `0` `.artdeco-stat-change` nodes
  - the routed table now shows live endpoint rows such as `AKShare龙虎榜详情数据` and `akshare.stock_lhb_detail_em`
  - sample values `4.00`, `3/4`, `28,412`, `2.00` and sample source rows such as `Wind` are absent
  - actual PM2 requests reached `http://localhost:3020/api/v1/data-sources/config/` with `200`

## Rule Feedback
- This batch promoted `myweb-audit v1.34` tab-slice contract truth.
- Future multi-tab routed-page audits should treat leftover sample tab slices as route-truth defects whenever the route already exposes a real contract for that tab.
