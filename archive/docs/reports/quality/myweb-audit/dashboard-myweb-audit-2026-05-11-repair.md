# Dashboard MyWeb Audit Repair Verification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Date**: 2026-05-11
> **Skill**: `myweb-audit` v2.1
> **Source audit**: `docs/reports/quality/myweb-audit/dashboard-myweb-audit-2026-05-11.md`
> **Scope**: DA-01 through DA-08 verification and follow-up repair
> **Mode**: code-review verification plus targeted command checks

## Verification Summary

| ID | Severity | Issue | Verification Status | Notes |
| --- | --- | --- | --- | --- |
| DA-01 | High | Dashboard tab ARIA relationships incomplete | Verified fixed by code review | Flow and pool tabs now have ids, `aria-controls`, selected-aware `tabindex`, and labelled panels. |
| DA-02 | High | `ArtDecoCollapsible` unbound `headerId` | Verified fixed by code review | Header now binds `:id="headerId"`, matching content `aria-labelledby`. |
| DA-03 | High | `ArtDecoChart` lacks accessible chart naming | Verified fixed by code review | Shared prop, dashboard root charts, and `DashboardMarketPanorama.vue` chart call sites now have specific labels. |
| DA-04 | Medium | `ArtDecoHeader` ignores `statusType` | Verified fixed by code review and token lint | Prop/class/status styling was added and fallback hex colors were removed. |
| DA-05 | Medium | Non-clickable dashboard cards imply false interactivity | Verified fixed by code review and token lint | Dashboard informational cards pass `:hoverable="false"` and `ArtDecoCard` now scopes hover lift/glow to the `artdeco-card--hoverable` modifier. |
| DA-06 | Medium | Stress test lacks live/local-estimate semantics | Verified fixed by code review | Copy now states local estimate/non-backend analysis and metrics use `aria-live="polite"`. |
| DA-07 | Low | Sub-1280 media queries | Verified fixed by code review | Dashboard route-local SCSS now keeps the desktop baseline at `--artdeco-breakpoint-lg` and removes lower-width media branches. |
| DA-08 | Low | Broad `transition: all` cleanup | Verified fixed by code review and token lint | Dashboard route-local transitions and touched shared primitives now list concrete transition properties. |

## Code Review Evidence

### DA-01: Dashboard tabs ARIA relationships

Verified in `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`:

- Flow tab buttons now use ids such as `flow-tab-1day`.
- Flow tab buttons now set `aria-controls="flow-tabpanel"` and selected-aware `tabindex`.
- Flow tabpanel now uses `id="flow-tabpanel"` and `:aria-labelledby="'flow-tab-' + activeFlowTab"`.
- Pool tab buttons now use ids such as `pool-tab-watchlist`.
- Pool tab buttons now set `aria-controls="pool-tabpanel"` and selected-aware `tabindex`.
- Pool tabpanel now uses `id="pool-tabpanel"` and `:aria-labelledby="'pool-tab-' + activePoolTab"`.

Status: **fixed by code review**.

### DA-02: ArtDecoCollapsible unbound header id

Verified in `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue`:

- `.artdeco-collapsible-header` now binds `:id="headerId"`.
- Existing content region still references `:aria-labelledby="headerId"`.

Status: **fixed by code review**.

Shared-impact note: this touches a shared primitive. The change is additive and should improve all consumers that rely on the content region label.

### DA-03: ArtDecoChart accessible name

Verified in `web/frontend/src/components/artdeco/charts/ArtDecoChart.vue`:

- Added `accessibleLabel` prop.
- Root container now has `role="img"` and `:aria-label="accessibleLabel || 'Chart'"`.

Verified in `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`:

- Market heatmap now passes `accessible-label="市场热度板块热力图"`.
- Capital-flow heatmap now passes `accessible-label="资金流向热力图"`.
- Sector radar now passes `accessible-label="行业轮动雷达图"`.

- `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue` now passes `accessible-label="市场资金流向折线图"` for the fund-flow chart.
- `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue` now passes `accessible-label="上证指数分时趋势图"` for the market trend chart.

Status: **fixed by code review**.

Shared-impact note: replacing the generic fallback `"Chart"` with a required/localized policy is a separate shared-component policy decision and was not included in this dashboard repair.

### DA-04: ArtDecoHeader status type

Verified in `web/frontend/src/components/artdeco/core/ArtDecoHeader.vue`:

- Added `statusType?: 'success' | 'warning' | 'danger' | 'error' | 'info'`.
- Status indicator now binds `status--${statusType}`.
- Status dot styling was added for `success`, `danger`, `error`, `warning`, and `info`.

- Fallback hardcoded hex values were removed from the new `status--success`, `status--danger/error`, and `status--info` rules.
- Targeted ArtDeco token lint now passes for the dashboard repair target set.

Status: **fixed by code review and token lint**.

### DA-05: Non-clickable card hover affordance

Observed changes in `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`:

- The following informational chart cards now explicitly pass `:hoverable="false"`:
  - `heat-map-card`
  - `capital-heatmap-card`
  - `sector-radar-card`

Shared primitive repair in `web/frontend/src/components/artdeco/base/ArtDecoCard.vue`:

- GitNexus impact analysis for `ArtDecoCard.vue` returned **CRITICAL** risk with 34 direct importers.
- The repair preserves the existing default `hoverable: true` behavior for current consumers.
- `@include artdeco-hover-lift-glow` was moved from the base `.artdeco-card` rule to `.artdeco-card--hoverable`.
- Decorative frame hover styles were also scoped to `.artdeco-card--hoverable:hover`.
- Existing hardcoded spacing literals in `ArtDecoCard.vue` were replaced with ArtDeco spacing tokens so the touched shared target passes token lint.

Status: **fixed by code review and token lint**.

### DA-06: Stress-test live/local-estimate semantics

Verified in `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`:

- Pre-execution copy now says the action performs a local estimate and is not backend risk analysis.
- After execution, a visible disclaimer states the result is based on current page data and is not backend-verified risk analysis.
- `.stress-test-metrics` now has `aria-live="polite"`.

Status: **fixed by code review**.

### DA-07: Low-width media branches below desktop baseline

Verified in `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss`:

- The route-local responsive branch now uses `@media (width <= var(--artdeco-breakpoint-lg))`, matching the supported 1280 desktop baseline.
- The previous sub-1280 branches for 1024, 768, and narrower widths were removed from this route-local dashboard stylesheet.

Status: **fixed by code review**.

### DA-08: Broad transition cleanup

Verified in `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss`:

- Route-local `transition: all` usages were replaced with concrete property transitions for `border-color`, `box-shadow`, `transform`, `color`, `background-color`, and `opacity` as appropriate.

Verified in touched shared primitives:

- `web/frontend/src/components/artdeco/base/ArtDecoCard.vue` now lists concrete transition properties on the base card.
- `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue` now lists concrete transition properties for the wrapper, header, decoration, and collapse animation.

Status: **fixed by code review and token lint**.

## Commands Run

| Command | Result | Notes |
| --- | --- | --- |
| `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` | Passed | `23/23` tests passed. Test stderr includes expected simulated fetch-failure logs from the unavailable-slice cases. |
| `npx vitest run src/components/artdeco/base/__tests__/ArtDecoCard.spec.ts` | Passed | `5/5` tests passed, including a regression assertion that `hoverable=false` omits the `artdeco-card--hoverable` class. |
| `npx vitest run src/api/services/__tests__/dashboardService.spec.ts` | Passed | `8/8` tests passed, covering the service file touched by the type cleanup. |
| `npm run type-check` | Passed | Type-check now completes with 0 errors. Previous errors in `DashboardMarketPanorama.vue`, `dashboardService.ts`, and `useKLinePatternOverlays.ts` are cleared. |
| `npm run lint:artdeco -- --target-file ...` | Passed | Targeted ArtDeco lint passed for `ArtDecoCard.vue`, `ArtDecoCollapsible.vue`, `ArtDecoDashboard.vue`, `ArtDecoDashboard.scss`, `DashboardMarketPanorama.vue`, `ArtDecoChart.vue`, and `ArtDecoHeader.vue`. |
| `rg "transition:\\s*all|@media ..."` over dashboard repair targets | Passed | No remaining `transition: all` or sub-1280 dashboard media-branch patterns were found in the scoped target set. |
| `rg "accessible-label|aria-controls|aria-labelledby|aria-live|hoverable|status-type"` over dashboard repair targets | Passed | Confirmed the repaired ARIA, accessible chart labels, non-hoverable informational cards, live region, and header status type hooks are present in the scoped target set. |
| `npx playwright test tests/smoke/02-page-loading.spec.ts --project=chromium` | Failed | `3/6` passed, `3/6` failed because unauthenticated `/dashboard` access redirects to the login page; failure snapshots show `LOGIN`, not a dashboard render crash. |
| `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --project=chromium -g "dashboard renders shell and core cards under mock data"` | Passed | `1/1` Chromium E2E passed with seeded auth and mocked dashboard APIs. |
| `pm2 jlist` | Passed | `mystocks-backend` and `mystocks-frontend` are both `online`. |
| `git diff --check -- <dashboard repair target files>` | Passed | Scoped whitespace/conflict-marker check passed for the 12 files touched by this repair. |
| `gitnexus_detect_changes(scope="staged")` | Passed | Staged micro-batch covers 12 files; GitNexus reported `risk_level: low`, `changed_count: 59`, and `affected_processes: []`. |

## Type-Check Details

`npm run type-check` now passes with 0 errors.

Type cleanup performed in this follow-up:

- `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue`: `fundFlowChartOption` and `marketTrendOption` props now accept the unwrapped chart option values used by the template.
- `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue`: `variant="outlined"` was changed to the existing `ArtDecoCard` variant `bordered`.
- `web/frontend/src/api/services/dashboardService.ts`: the technical-indicator response branch now checks `response.success === false` for known `UnifiedResponse` values, avoiding an impossible false branch from the broader `isErrorEnvelope` guard.
- `web/frontend/src/components/technical/composables/useChartOverlays.ts`: chart overlay creation now uses `OverlayCreate`, matching the klinecharts `createOverlay` contract.
- `web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts`: custom overlay figure callbacks return empty arrays instead of `null`, and automatic overlay construction is typed as `AutomaticOverlayDefinition[]`.


## ArtDeco Token Lint Details

Targeted command:

```bash
npm run lint:artdeco -- --target-file src/components/artdeco/base/ArtDecoCard.vue --target-file src/components/artdeco/base/ArtDecoCollapsible.vue --target-file src/views/artdeco-pages/ArtDecoDashboard.vue --target-file src/views/artdeco-pages/styles/ArtDecoDashboard.scss --target-file src/views/artdeco-pages/components/DashboardMarketPanorama.vue --target-file src/components/artdeco/charts/ArtDecoChart.vue --target-file src/components/artdeco/core/ArtDecoHeader.vue
```

Result:

- Passed after removing hardcoded fallback color literals from `ArtDecoHeader.vue`, replacing existing hardcoded spacing literals in the touched `ArtDecoCard.vue` target with ArtDeco spacing tokens, and including `ArtDecoDashboard.scss` in the target set.

## Runtime Verification Details

An unauthenticated smoke suite was attempted first:

```bash
npx playwright test tests/smoke/02-page-loading.spec.ts --project=chromium
```

Result:

- `3/6` passed.
- `3/6` failed because the suite expected dashboard shell selectors immediately after navigating to `/#/dashboard`.
- Current route guard redirects unauthenticated users to `LOGIN`; the Playwright error snapshots show the login screen and seeded test-account copy.

Authenticated dashboard runtime proof:

```bash
npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --project=chromium -g "dashboard renders shell and core cards under mock data"
```

Result:

- `1/1` passed on Chromium.
- The test seeds auth, stubs dashboard APIs, navigates to `/dashboard`, and verifies the dashboard shell plus core cards.

## Required Quality Status Confirmation

| Check | Status | Evidence |
| --- | --- | --- |
| Structural syntax errors | `0` blocking errors | `npm run type-check` passed with 0 errors. |
| Type inference errors | `0` current errors in this target verification | `npm run type-check` passed; no new type regression was observed. |
| PM2 backend service | Online | `mystocks-backend` is online at `http://localhost:8020`. |
| PM2 frontend service | Online | `mystocks-frontend` is online at `http://localhost:3020`. |
| E2E verification | Passed for authenticated dashboard route proof | `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --project=chromium -g "dashboard renders shell and core cards under mock data"` passed `1/1` on Chromium. |
| Smoke caveat | Environment/auth mismatch, documented | `tests/smoke/02-page-loading.spec.ts --project=chromium` passed `3/6` and failed `3/6` because unauthenticated `/dashboard` redirects to `LOGIN`. |

## Diff Hygiene Notes

- Scoped `git diff --check` passed for the dashboard repair target files.
- Full-worktree `git diff --check` was not usable as a repair verdict because the dirty worktree contains unrelated files and stopped on `scripts/ai-collaboration-setup.sh` permission denial, with additional unrelated CRLF/blank-line warnings.
- `gitnexus_detect_changes(scope="staged")` was rerun after staging only the 12 dashboard repair target files.
- Staged GitNexus result: `changed_files: 12`, `changed_count: 59`, `risk_level: low`, `affected_processes: []`.

## Function Tree Mapping

This dashboard repair does not add a new user-facing capability, retire an entrypoint, change a canonical route, or change a function-tree status. Therefore `docs/FUNCTION_TREE.md` does not require a status update in this repair batch.

Current route truth:

- Route: `/dashboard`
- Canonical component: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Route role: Phase 1 frontend mainline dashboard / market overview entry

Function-tree placement:

- Primary domain: `01-市场数据与行情 {#domain-01}`
- Primary nodes:
  - `1.1 实时行情监控 {#domain-01-node-01}`
  - `1.2 资金流向分析 {#domain-01-node-02}`
- Secondary touched domain: `02-技术分析与指标 {#domain-02}`, limited to KLine overlay type cleanup.
- Read-only aggregation context: strategy, trading, and monitoring summaries are displayed on dashboard but were not functionally changed by this repair.

## Next Work Plan

1. If this line is prepared for commit, stage only the 12 dashboard repair target files and keep unrelated dirty worktree changes out of the index.
2. After staging, rerun `gitnexus_detect_changes(scope="staged")` to produce the precise micro-batch impact verdict.
3. Rerun the minimum verification set before committing: type-check, targeted ArtDeco lint, dashboard logic unit test, `ArtDecoCard` unit test, `dashboardService` unit test, and authenticated dashboard Chromium E2E.
4. If the staged GitNexus verdict and verification remain clean, prepare a focused commit for the dashboard `myweb-audit` repair line.
5. For the next `myweb-audit` page batch, prefer the Phase 1 market route chain, starting with `/market/realtime` or `/market/technical`.

## Current Closeout Verdict

This repair is **code-review and targeted-command verified** for DA-01 through DA-08.

Verified fixed:

- DA-01
- DA-02
- DA-03
- DA-04
- DA-05
- DA-06
- DA-07
- DA-08

*Dashboard MyWeb Audit Repair Verification | 2026-05-11 | DA-01 through DA-08 targeted verified*
