# System Health-Family Probe And KPI Truth Audit

## Scope
- `/system/health`
- `/system/api`

## Routed Defects Closed
- Successful plain `/api/health` payloads were being discarded by generic wrapper expectations, which left both routed pages in `UNKNOWN / N/A / N/A / 3` despite live `200` probe responses.
- Both routed KPI strips were inheriting shared `ArtDecoStatCard` delta chrome and pseudo precision even though the visible cards only exposed status, labels, and a plain middleware count.

## Repair
- Added `web/frontend/src/views/system/healthProbeContract.ts` so system-family health probes can normalize plain payloads into a `UnifiedResponse` shape before `useArtDecoApi.exec` applies generic success or error handling.
- Updated `/system/health` and `/system/api` to use the page-family adapter.
- Updated both routed KPI strips to pass plain string values and `show-change=false`.
- Tightened component tests so the `useArtDecoApi` mock now preserves real wrapper-envelope behavior instead of silently accepting plain payloads that runtime code would reject.

## Verification Evidence
- Unit regression:
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts` passed
- Live browser verification with Playwright-library + system `google-chrome`:
  - `/system/health` now shows `HEALTHY / N/A / 1.0.0 / 3`
  - `/system/api` now shows `HEALTHY / N/A / 1.0.0 / 3`
  - both routed strips have `0` `.artdeco-stat-change` nodes
  - both routed strips no longer contain `+0%`, `3.00`, `2.00`, `1.00`, or `0.00`
  - actual PM2 requests reached `http://localhost:3020/api/health` and `http://localhost:3020/api/health/ready` with `200`

## Rule Feedback
- This batch promoted `myweb-audit v1.33` probe-envelope truth.
- The batch also proved that permissive test doubles can hide route-truth defects; future system audits should keep wrapper-contract mocks faithful to runtime behavior.
