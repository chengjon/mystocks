# B4.013-M1-D-FIX Dashboard Big-Deal Dependency Isolation Closeout

Date: 2026-06-16
Node: `artdeco-web-design-governance/b4-013-m1d-dashboard-aggregate-runtime-data-provenance-audit`
Authorization: source-authorized for frontend-only Dashboard aggregate data isolation

## Scope

Allowed paths used:

- `web/frontend/src/api/services/dashboardService.ts`
- `web/frontend/src/api/services/__node_tests__/dashboardServiceData.test.ts`
- `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `docs/reports/worklogs/claude-auto/b4-013-m1d-dashboard-big-deal-dependency-isolation-closeout-2026-06-16.md`

Allowed paths not changed:

- `web/frontend/src/api/services/dashboardServiceData.ts`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts`

Explicitly not touched:

- Backend/API/runtime code
- Router, store, view migration, OpenSpec, ST-HOLD, `marketKlineData`
- External dirty cards and unrelated residual dirty files

## Implementation Summary

`dashboardService.getFundFlow` now treats the HSGT summary endpoint as the required provenance-bearing source and treats the big-deal payload as optional auxiliary data.

The big-deal request is resolved through a bounded optional payload helper. If the request rejects, returns an error envelope, or does not resolve within the optional payload timeout, Dashboard fund-flow normalization receives an empty rows payload instead of failing the whole aggregate.

This preserves the existing `request_id` and `process_time` provenance from the summary response and keeps Dashboard aggregate readiness independent from the slow or unavailable big-deal endpoint.

## TDD Evidence

Red test added:

- `dashboardService.getFundFlow preserves summary snapshot when big-deal fails`
- Initial focused run failed with `Error: big-deal unavailable` from `dashboardService.ts`, proving the previous coupling.

Green tests after implementation:

- `cd web/frontend && npx tsx src/api/services/__node_tests__/dashboardServiceData.test.ts`
- Result: 8 tests, 8 pass, 0 fail.

Component provenance regression:

- `cd web/frontend && npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts`
- Result: 1 file passed, 25 tests passed.

Type gate:

- `cd web/frontend && npm run type-check`
- Result: `vue-tsc --noEmit` exit 0.

## Runtime Evidence

PM2 service health:

- `mystocks-backend`: online on `http://localhost:8020`
- `mystocks-frontend`: online on `http://localhost:3020`
- Backend `/api/health`: HTTP 200
- Frontend proxy `/api/health`: HTTP 200
- Frontend served `dashboardService.ts` contains `resolveOptionalDashboardPayload` and `OPTIONAL_DASHBOARD_PAYLOAD_TIMEOUT_MS`.

Dashboard browser smoke:

- Browser: Playwright Chromium, service workers blocked
- Auth: real login through `admin / admin123`
- Route: `http://127.0.0.1:3020/dashboard`
- Title: `交易室 - MyStocks`
- H1: `量化驾驶舱`
- Visible Dashboard meta: `DATA: REAL`, non-empty `REQ`, `SYNC: READY`
- Pending meta nodes: 0
- Dashboard-level alerts: 0
- Skeleton nodes: 0

Observed residual runtime condition:

- The backend big-deal request can still be slow or remain pending independently.
- This is now isolated from Dashboard aggregate readiness and should be handled as a separate backend/API performance or availability item if needed.

## GitNexus Impact Evidence

Pre-edit GitNexus impact:

- `getFundFlow`: LOW risk, 0 impacted symbols, 0 execution flows
- `getStockFlowRanking`: LOW risk, 0 impacted symbols, 0 execution flows
- `normalizeDashboardFundFlow`: LOW risk, 1 direct module, 0 execution flows

Staged GitNexus gates:

- `node .gitnexus/run.cjs verify-staged --repo mystocks --json`: ok
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks`: 7 files, 9 symbols, 0 affected processes, low risk

OPENDOG fresh verification:

- Focused frontend tests recorded as `status: passed`, exit code 0.
- Frontend type-check recorded as `status: passed`, exit code 0.
- Follow-up OPENDOG verification: `missing_kinds: []`, `refactor_blockers: []`, `safe_for_refactor: true`.

## Closeout Decision

The M1-D runtime blocker is reduced from a hard Dashboard aggregate dependency to an isolated auxiliary data dependency. Mainline Dashboard readiness is restored under the observed big-deal degradation mode without changing backend contracts, routing, stores, or view ownership.

Next recommended node:

- `B4.013-M1-E`: backend/API residual slow endpoint attribution, if the team wants to address the remaining big-deal latency or hanging request at its source.
