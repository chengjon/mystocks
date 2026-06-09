# B4.005 system/risk route package preflight

Date: 2026-06-06
Mode: `no-source`
Scope: system/risk route dirty inventory after B4.004 handoff

## Governance boundary

This node inventories system/risk route dirty items only. It does not edit, restore, stage, or commit frontend source, tests, styles, or assets.

Primary references:

- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-004-data-market-route-package-preflight-2026-06-06.md`
- `docs/guides/frontend-structure.md`
- `web/frontend/src/router/index.ts`

Inherited constraints:

- Keep B4.002 deletion-retirement candidates out of this package.
- Keep FundFlow route-header items and LHB deferred items out of this package.
- Keep data/market package candidates out of this package.
- Keep trade-specific rows for B4.006.
- Stale OPENDOG evidence remains non-blocking for this no-source inventory, but any later source-authorized package must refresh evidence or explicitly accept the stale caveat.

## Scan method

Read-only checks:

- Parsed targeted `git status --porcelain=v1 -uall` for:
  - `web/frontend/src/views/risk`
  - `web/frontend/src/views/system`
  - `web/frontend/src/views/artdeco-pages/risk-tabs`
  - `web/frontend/src/views/artdeco-pages/system-tabs`
  - `web/frontend/tests/unit/views`
- Mapped canonical active risk/system routes from `web/frontend/src/router/index.ts`.
- Parsed current `web/frontend/src` import declarations for dependency signals.
- Classified out-of-scope data/route-header/trade rows separately.

No build, type-check, Vitest, E2E, PM2, or source mutation was performed.

## Summary

Targeted rows observed:

- Total classified rows: `55`
- System/risk package candidates: `48`
- Out-of-scope rows: `7`

Classification:

| Class | Count | Disposition |
| --- | ---: | --- |
| `risk-active-route` | 4 | Candidate canonical risk route source package. |
| `risk-test-or-support` | 5 | Risk page tests and noncanonical risk sidecar views. |
| `risk-test-support` | 2 | B4.004 handoff tests for risk wrapper/template retention. |
| `system-active-route` | 5 | Candidate canonical system route source package. |
| `system-test-or-support` | 14 | System tests, sidecar views, styles, and support contracts. |
| `system-test-support` | 1 | B4.004 handoff system wrapper retention test. |
| `artdeco-risk-tab-support` | 14 | ArtDeco risk tab support package, separate from canonical risk routes. |
| `artdeco-system-tab-support` | 3 | ArtDeco system tab support package, separate from canonical system routes. |
| `out-of-scope-B4.004-or-route-header` | 6 | Data/route-header rows; do not process in B4.005. |
| `out-of-scope-B4.006` | 1 | Trade row; do not process in B4.005. |

Risk split:

| Risk | Count | Meaning |
| --- | ---: | --- |
| Medium | 28 | Canonical route source, imported support, or ArtDeco support surface. |
| Low | 27 | Test-only, sidecar view, or out-of-scope row. |

No high-risk dependency blocker was detected in B4.005 no-source inventory. Medium-risk items still require source-authorized package gates before editing.

## Canonical risk routes

Current active dirty risk route pages:

| Route | Path | Status | Risk | Dependency signal |
| --- | --- | --- | --- | --- |
| `/risk/center` | `web/frontend/src/views/risk/Center.vue` | modified | Medium | Imported by router and related tests. |
| `/risk/overview` | `web/frontend/src/views/risk/Overview.vue` | modified | Medium | Imported by router and ArtDeco wrapper references. |
| `/risk/stop-loss` | `web/frontend/src/views/risk/StopLoss.vue` | modified | Medium | Imported by router and tests. |
| `/risk/news` | `web/frontend/src/views/risk/News.vue` | modified | Medium | Imported by router and tests. |

Related risk test/support rows:

| Path | Status | Risk | Proposed package |
| --- | --- | --- | --- |
| `web/frontend/src/views/risk/__tests__/Center.spec.ts` | untracked | Low | `SR-1 risk canonical route package` |
| `web/frontend/src/views/risk/__tests__/News.spec.ts` | modified | Low | `SR-1 risk canonical route package` |
| `web/frontend/src/views/risk/__tests__/StopLoss.spec.ts` | untracked | Low | `SR-1 risk canonical route package` |
| `web/frontend/tests/unit/views/risk-center-template-retention.spec.ts` | modified | Low | `SR-1 risk canonical route package` or risk test-only evidence |
| `web/frontend/tests/unit/views/risk-wrapper-retention.spec.ts` | modified | Low | `SR-1 risk canonical route package` or risk test-only evidence |

Risk sidecar/noncanonical views:

| Path | Status | Risk | Disposition |
| --- | --- | --- | --- |
| `web/frontend/src/views/risk/Portfolio.vue` | modified | Low | Not a current router import; review as sidecar/legacy view before source edits. |
| `web/frontend/src/views/risk/Positions.vue` | modified | Low | Not a current router import; review as sidecar/legacy view before source edits. |

Notes:

- `/risk/alerts` maps to `web/frontend/src/views/risk/Alerts.vue`, but that page was not dirty in this targeted scan.
- `/risk/pnl` maps to an ArtDeco portfolio tab, not `risk/Portfolio.vue`.

## Canonical system routes

Current active dirty system route pages:

| Route | Path | Status | Risk | Dependency signal |
| --- | --- | --- | --- | --- |
| `/system/config` | `web/frontend/src/views/system/Settings.vue` | modified | Medium | Imported by router and tests/wrappers. |
| `/system/api` | `web/frontend/src/views/system/API.vue` | modified | Medium | Imported by router; imports system health contract support. |
| `/system/datasource` | `web/frontend/src/views/system/DataSource.vue` | modified | Medium | Imported by router and tests. |
| `/system/health` | `web/frontend/src/views/system/Health.vue` | modified | Medium | Imported by router and tests. |
| `/system/resources` | `web/frontend/src/views/system/Resources.vue` | modified | Medium | Imported by router; uses `useSystemResourcesPage.ts`. |

Related system test/support rows:

| Path | Status | Risk | Proposed package |
| --- | --- | --- | --- |
| `web/frontend/src/views/system/__tests__/API.spec.ts` | untracked | Low | `SR-2 system canonical route package` |
| `web/frontend/src/views/system/__tests__/DataSource.spec.ts` | untracked | Low | `SR-2 system canonical route package` |
| `web/frontend/src/views/system/__tests__/Health.spec.ts` | untracked | Low | `SR-2 system canonical route package` |
| `web/frontend/src/views/system/__tests__/Resources.spec.ts` | modified | Low | `SR-2 system canonical route package` |
| `web/frontend/src/views/system/__tests__/Settings.spec.ts` | modified | Low | `SR-2 system canonical route package` |
| `web/frontend/tests/unit/views/system-wrapper-retention.spec.ts` | modified | Low | `SR-2 system canonical route package` or system test-only evidence |
| `web/frontend/src/views/system/composables/useSystemResourcesPage.ts` | modified | Medium | Pair with `/system/resources`. |
| `web/frontend/src/views/system/healthProbeContract.ts` | untracked | Medium | Imported by system API/health/resource surfaces; pair with system health/API package. |
| `web/frontend/src/views/system/styles/API.scss` | modified | Low | Pair only if `API.vue` still imports or requires it after source preflight. |

System sidecar/noncanonical views:

| Path | Status | Risk | Disposition |
| --- | --- | --- | --- |
| `web/frontend/src/views/system/Architecture.vue` | modified | Low | Not a current canonical route import; paired test exists. |
| `web/frontend/src/views/system/DatabaseMonitor.vue` | modified | Low | Not a current canonical route import; paired test exists. |
| `web/frontend/src/views/system/PerformanceMonitor.vue` | modified | Low | Not a current canonical route import; paired test exists. |
| `web/frontend/src/views/system/__tests__/Architecture.spec.ts` | untracked | Low | Pair only after sidecar route-truth decision. |
| `web/frontend/src/views/system/__tests__/DatabaseMonitor.spec.ts` | untracked | Low | Pair only after sidecar route-truth decision. |
| `web/frontend/src/views/system/__tests__/PerformanceMonitor.spec.ts` | untracked | Low | Pair only after sidecar route-truth decision. |

## ArtDeco risk/system support

These are risk/system domain files, but they live under `views/artdeco-pages/**`. They should not be staged inside the canonical route page package unless the source-authorized package explicitly includes ArtDeco support.

### ArtDeco risk tabs

| Path | Status | Risk | Notes |
| --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue` | modified | Medium | Imported by ArtDeco trading center. |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue` | modified | Medium | Imported by templates/ArtDeco risk surfaces. |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStatsGrid.vue` | modified | Medium | Imported by templates/ArtDeco risk surfaces. |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStockPanel.vue` | modified | Medium | Imported by templates/ArtDeco risk surfaces. |
| `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts` | modified | Medium | Imported by risk tab tests/support. |
| `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementHelpers.ts` | modified | Medium | Imported by multiple ArtDeco risk surfaces. |
| `web/frontend/src/views/artdeco-pages/risk-tabs/stopLossMonitorData.ts` | modified | Medium | Imported by stop-loss monitor support/tests. |
| Risk tab tests under `__tests__` and `__node_tests__` | mixed modified/untracked | Medium | Pair with ArtDeco risk support package only. |

### ArtDeco system tabs

| Path | Status | Risk | Notes |
| --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts` | modified | Medium | Imported by ArtDeco data/system tab support. |
| `web/frontend/src/views/artdeco-pages/system-tabs/__node_tests__/dataManagementData.test.ts` | modified | Medium | Pair with ArtDeco system support package. |
| `web/frontend/src/views/artdeco-pages/system-tabs/__tests__/ArtDecoDataManagement.spec.ts` | modified | Medium | Pair with ArtDeco system support package. |

## Out-of-scope rows

These rows were visible in the broad unit-view sweep but must not be processed in B4.005:

| Path | Destination |
| --- | --- |
| `web/frontend/tests/unit/views/data-advanced-cutover.spec.ts` | B4.004 data/market. |
| `web/frontend/tests/unit/views/data-advanced-screening-truth.spec.ts` | B4.004 data/market. |
| `web/frontend/tests/unit/views/data-concept-refresh-fallback.spec.ts` | B4.003 route-header evidence residue. |
| `web/frontend/tests/unit/views/data-fund-flow-partial-state.spec.ts` | B4.003 FundFlow route-header line. |
| `web/frontend/tests/unit/views/data-indicator-details.spec.ts` | B4.004 data/market. |
| `web/frontend/tests/unit/views/data-industry-refresh-fallback.spec.ts` | B4.003 route-header evidence residue. |
| `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts` | B4.006 strategy/trade preflight. |

## Proposed package order

1. `SR-1 risk canonical route package`
   - Candidate files: `Center.vue`, `Overview.vue`, `StopLoss.vue`, `News.vue`, paired route tests, and risk wrapper/template retention tests if still relevant.
   - Risk: Medium.
   - Gate: source-authorized package, GitNexus impact before editing route page symbols, route config/static tests, focused unit/component tests.

2. `SR-2 system canonical route package`
   - Candidate files: `Settings.vue`, `API.vue`, `DataSource.vue`, `Health.vue`, `Resources.vue`, paired tests, `useSystemResourcesPage.ts`, `healthProbeContract.ts`, and optionally `API.scss`.
   - Risk: Medium.
   - Gate: source-authorized package, import/dependency review for health/API contracts, route config/static tests, focused unit/component tests.

3. `SR-3 ArtDeco risk support package`
   - Candidate files: ArtDeco risk tab components, support modules, and paired tests.
   - Risk: Medium because imported by ArtDeco trading/templates.
   - Gate: ArtDeco support package authorization; do not mix with canonical route page edits unless explicitly authorized.

4. `SR-4 ArtDeco system support package`
   - Candidate files: ArtDeco system data management support and paired tests.
   - Risk: Medium.
   - Gate: ArtDeco support package authorization; keep separate from canonical `views/system/**` route pages unless explicitly authorized.

5. `SR-5 sidecar route-truth review`
   - Candidate files: `risk/Portfolio.vue`, `risk/Positions.vue`, `system/Architecture.vue`, `system/DatabaseMonitor.vue`, `system/PerformanceMonitor.vue`, and paired tests.
   - Risk: Low to medium.
   - Gate: route-truth decision first. Do not treat as active route work until canonical status is confirmed.

## B4.006 handoff

B4.006 should start strategy/trade route package preflight / no-source.

Carry forward to B4.006:

- `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts`

Do not carry into B4.006:

- B4.005 risk/system package candidates.
- ArtDeco risk/system support candidates.
- B4.004 data/market candidates.
- B4.003 route-header residue.
- B4.002 deletion-retirement candidates.

## Verification performed

Read-only checks only:

- Targeted dirty status parse.
- Router truth mapping.
- Import declaration dependency scan for current `web/frontend/src`.
- Risk and package classification.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.005 is a no-source preflight and does not modify or accept frontend source/test changes.
