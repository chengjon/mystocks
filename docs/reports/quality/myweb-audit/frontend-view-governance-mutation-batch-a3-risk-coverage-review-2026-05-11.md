# Frontend View Governance A3 Risk Coverage Review

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: next-batch selection evidence for `openspec/changes/update-frontend-view-governance` after `A3-alert-rules-archive`.

This review does not move files, edit runtime code, update tests, or change routes.

## Decision

Select the next narrow batch as:

```text
A3-risk-coverage-review
```

Do not approve a direct runtime absorption from `web/frontend/src/views/monitoring/RiskDashboard.vue`.

Reason: the legacy monitoring risk dashboard is not an active route owner, and its remaining business surfaces are either already covered by canonical `/risk/*` routes with verified snapshot semantics or are explicitly unsafe to absorb because they are fallback-derived, pseudo-live, or backed by stale API paths.

## Function Tree Position

Primary function-tree domains:

- `04-风险管理与监控`: legacy source path is `web/frontend/src/views/monitoring/RiskDashboard.vue`, under the old monitoring view family but functionally overlaps current risk routes.
- `03-自选与持仓基础数据`: legacy `watchlistId`-scoped portfolio analysis depends on watchlist/position substrate, but the current page does not receive a valid `watchlistId` from an active route context.

Canonical frontend successors:

- `/risk/overview` -> `web/frontend/src/views/risk/Overview.vue`
- `/risk/alerts` -> `web/frontend/src/views/risk/Alerts.vue`
- `/risk/stop-loss` -> `web/frontend/src/views/risk/StopLoss.vue`
- `/risk/management` -> `web/frontend/src/views/risk/Center.vue`
- `/risk/pnl` -> `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`

## Coverage Matrix

| Legacy capability in `monitoring/RiskDashboard.vue` | Current canonical coverage | Decision |
| --- | --- | --- |
| Critical/warning/info alert lists | Covered by `/risk/overview` and `/risk/alerts` through `monitoringApi.getAlerts()` with verified snapshot and request-id retention | Covered |
| Alert rule/risk governance context | Covered by `/risk/overview` and `/risk/alerts`; CRUD was absorbed in the prior A3 alert-rules batch | Covered |
| Stop-loss distance monitoring | Covered by `/risk/stop-loss` using watchlists, quotes, selector-key isolation, verified snapshot retention, and honest pending/unavailable states | Covered |
| Position/risk management overview | Partially covered by `/risk/management` via canonical risk helper transforms over `/v1/trade/positions` | Covered enough for current route truth; no old-page absorption |
| Sector allocation | Partially covered by canonical risk management helper transforms; legacy sector allocation is just summary payload display | Do not absorb separately |
| Portfolio health score and risk score gauge | Legacy-only summary fields from `/api/monitoring/analysis/portfolio/*`; no current route-level verified truth | Do not absorb; would create faux live metrics |
| Active/inactive position counts | Derived as a hard-coded 80/20 split from `position_count` | Do not absorb |
| Trend percentage | Generated with `Math.random()` in `getScoreChange()` | Do not absorb |
| Rebalancing suggestions | Legacy summary/rebalance endpoint display without canonical execution workflow | Do not absorb unless a later trade/portfolio spec defines real truth |
| Sharpe, Sortino, drawdown, volatility | `/risk/overview` intentionally marks risk metrics as `未校验/待接入`; legacy renders `N/A`/fallback values | Do not absorb |
| Export/apply/acknowledge actions | Legacy handlers only show messages and do not persist domain changes | No absorption needed |
| Local composable `useRiskDashboard.ts` | Single-consumer helper for the legacy page; also expects `watchlistId` options while the page calls `useRiskDashboard()` without arguments | Move or retire with page after archive approval |
| Style asset `RiskDashboard.scss` | Page-local style guarded by monitoring style specs | Move with owning page only after direct guard retirement |

## Current Active Blockers

Active code/test references still include:

- `web/frontend/src/views/monitoring/RiskDashboard.vue`
- `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts`
- `web/frontend/src/views/monitoring/styles/RiskDashboard.scss`
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`

Historical E2E and docs references may still mention `/monitoring/risk`, but current active route truth in `web/frontend/src/router/index.ts` does not expose that route.

## Recommended Next Profile

Prepare an archive-prep batch:

```text
A3-risk-dashboard-archive-prep
```

Proposed scope:

- Confirm no active route/menu/page-config/package references to `monitoring/RiskDashboard`.
- Retire only direct active config guard entries for `RiskDashboard.vue` and `RiskDashboard.scss`.
- Move only the legacy page, its local composable, and its page-local style into `archive/web/frontend/src/views/monitoring/risk-dashboard/`.
- Do not modify canonical `/risk/*` runtime behavior in the archive batch.
- Do not absorb random trend, hard-coded active/inactive split, old summary score, stale rebalance suggestions, or unverified risk metrics.

## Required Pre-Mutation Checks For Any Later Archive

```bash
rg -n "RiskDashboard|useRiskDashboard|RiskDashboard.scss|monitoring/RiskDashboard|src/views/monitoring/RiskDashboard" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "risk_score|total_score|alert_summary|rebalance|sharpe_ratio|sortino_ratio|max_drawdown|volatility|monitoring/analysis/portfolio" web/frontend/src/views/risk web/frontend/src/views/artdeco-pages/risk-tabs web/frontend/src/stores web/frontend/tests --glob '!**/.claude/**'
openspec validate update-frontend-view-governance --strict
```

If a later archive batch edits direct test guards, run:

```bash
cd web/frontend && npx vitest run tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/StopLoss.spec.ts
```

## Approval Needed

Recommended approval wording:

```text
批准准备 A3-risk-dashboard-archive-prep，只确认 monitoring/RiskDashboard 的 successor coverage、直接 guard 退休方案与归档验证门禁；不吸收旧页伪实时指标，不修改 canonical /risk/* runtime。
```

Without explicit approval, no runtime code or archive move should occur.
