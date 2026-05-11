# Dashboard MyWeb Audit Repair Verification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Date**: 2026-05-11
> **Skill**: `myweb-audit` v2.1
> **Source audit**: `docs/reports/quality/myweb-audit/dashboard-myweb-audit-2026-05-11.md`
> **Scope**: DA-01 through DA-06 verification and follow-up repair; DA-07/DA-08 remain deferred
> **Mode**: code-review verification plus targeted command checks

## Verification Summary

| ID | Severity | Issue | Verification Status | Notes |
| --- | --- | --- | --- | --- |
| DA-01 | High | Dashboard tab ARIA relationships incomplete | Verified fixed by code review | Flow and pool tabs now have ids, `aria-controls`, selected-aware `tabindex`, and labelled panels. |
| DA-02 | High | `ArtDecoCollapsible` unbound `headerId` | Verified fixed by code review | Header now binds `:id="headerId"`, matching content `aria-labelledby`. |
| DA-03 | High | `ArtDecoChart` lacks accessible chart naming | Verified fixed by code review | Shared prop, dashboard root charts, and `DashboardMarketPanorama.vue` chart call sites now have specific labels. |
| DA-04 | Medium | `ArtDecoHeader` ignores `statusType` | Verified fixed by code review and token lint | Prop/class/status styling was added and fallback hex colors were removed. |
| DA-05 | Medium | Non-clickable dashboard cards imply false interactivity | Partially improved, not fully closed | Dashboard informational cards now pass `:hoverable="false"`, but shared `ArtDecoCard` still applies the base hover mixin to all cards. |
| DA-06 | Medium | Stress test lacks live/local-estimate semantics | Verified fixed by code review | Copy now states local estimate/non-backend analysis and metrics use `aria-live="polite"`. |
| DA-07 | Low | Sub-1280 media queries | Deferred | No repair attempted. |
| DA-08 | Low | Broad `transition: all` cleanup | Deferred | No repair attempted. |

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

Remaining gap:

- `web/frontend/src/components/artdeco/base/ArtDecoCard.vue` still includes `@include artdeco-hover-lift-glow` in the base `.artdeco-card` rule.
- GitNexus impact analysis for `ArtDecoCard.vue` returned **CRITICAL** risk with 34 direct importers.
- Therefore this report does not silently change shared card hover semantics; closing the remaining false-affordance risk requires a separate shared-impact repair/approval batch.

Status: **partially improved, not fully closed**.

Recommended follow-up:

- Move the base hover lift/glow behavior under `.artdeco-card--hoverable` in a shared-impact repair batch after reviewing affected ArtDeco card consumers.

### DA-06: Stress-test live/local-estimate semantics

Verified in `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`:

- Pre-execution copy now says the action performs a local estimate and is not backend risk analysis.
- After execution, a visible disclaimer states the result is based on current page data and is not backend-verified risk analysis.
- `.stress-test-metrics` now has `aria-live="polite"`.

Status: **fixed by code review**.

## Commands Run

| Command | Result | Notes |
| --- | --- | --- |
| `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` | Passed | `23/23` tests passed. Test stderr includes expected simulated fetch-failure logs from the unavailable-slice cases. |
| `npm run type-check` | Failed | 7 TypeScript errors remain in `dashboardService.ts` and `useKLinePatternOverlays.ts`; the previous `DashboardMarketPanorama.vue` errors are cleared. |
| `npm run lint:artdeco -- --target-file ...` | Passed | Targeted ArtDeco lint passed for `ArtDecoDashboard.vue`, `DashboardMarketPanorama.vue`, `ArtDecoCollapsible.vue`, `ArtDecoChart.vue`, and `ArtDecoHeader.vue`. |

## Type-Check Details

`npm run type-check` still fails, but the dashboard-scope errors reported in the previous verification were cleared.

Remaining errors:

- `src/api/services/dashboardService.ts(331,43)` and `(331,66)`: `Property 'data' does not exist on type 'never'`.
- `src/components/technical/composables/useKLinePatternOverlays.ts`: multiple pre-existing overlay typing errors.

Dashboard-scope type cleanup performed in this follow-up:

- `fundFlowChartOption` and `marketTrendOption` props in `DashboardMarketPanorama.vue` now accept the unwrapped chart option values used by the template.
- `variant="outlined"` was changed to the existing `ArtDecoCard` variant `bordered`.

## ArtDeco Token Lint Details

Targeted command:

```bash
npm run lint:artdeco -- --target-file src/views/artdeco-pages/ArtDecoDashboard.vue --target-file src/views/artdeco-pages/components/DashboardMarketPanorama.vue --target-file src/components/artdeco/base/ArtDecoCollapsible.vue --target-file src/components/artdeco/charts/ArtDecoChart.vue --target-file src/components/artdeco/core/ArtDecoHeader.vue
```

Result:

- Passed after removing hardcoded fallback color literals from `ArtDecoHeader.vue`.

## Residual Items Before Closure

1. **DA-05 shared card hover semantics**: `ArtDecoCard.vue` base hover behavior requires a separate shared-impact repair batch because GitNexus reports CRITICAL impact.
2. **Type-check baseline clarity**: do not report the repository as type-clean while the remaining 7 non-dashboard-scope TypeScript errors persist.
3. **Runtime verification**: no live browser screenshot/keyboard pass was run in this verification.

## Current Closeout Verdict

This repair is **mostly verified**, with one shared-impact residual item.

Verified fixed:

- DA-01
- DA-02
- DA-03
- DA-04
- DA-06

Improved but not fully closed:

- DA-05

Deferred as intended:

- DA-07
- DA-08

*Dashboard MyWeb Audit Repair Verification | 2026-05-11 | mostly verified with DA-05 shared-impact residual*
