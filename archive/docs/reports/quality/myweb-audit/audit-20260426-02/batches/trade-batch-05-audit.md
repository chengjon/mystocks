# Batch Audit Report: trade-batch-05

## Scope
- Module: trade
- Pages:
  - /trade/signals
  - /trade/history
- Batch rationale: reuse the strengthened `v1.32` count-kpi delta truth rule on remaining canonical trade routes so tally or label-only KPI cards stop inheriting fabricated delta chrome and decimal precision

## Agent Summary

### route-inventory
- `/trade/signals` remains the canonical routed signal workspace at `web/frontend/src/views/trade/Signals.vue`.
- `/trade/history` remains the canonical routed history workspace at `web/frontend/src/views/trade/History.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond honest stat-card presentation on the selected trade routes.

### data-state-audit
- Two high-severity routed count-kpi truth defects remained: both canonical trade pages exposed tally, cumulative, or label-only cards without a verified comparison baseline, yet still inherited shared stat-card flat-delta chrome and pseudo precision.

## Consolidated Issue Statistics
- Blocking: 0
- High: 2
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed count or label-only stat-card surfaces can accidentally impersonate movement metrics when shared stat-card defaults inject flat dots, `+0%`, and exact-decimal formatting without real comparison-baseline truth.
- Occurrence basis:
  - `/trade/signals` previously rendered the top tally strip and pending-analysis overview grid with shared flat-change chrome plus pseudo precision
  - `/trade/history` previously rendered `总笔数`, `已成交`, `待成交`, and `成交总额` with the same shared flat-change chrome despite having no comparison baseline
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
  - `web/frontend/src/views/trade/Signals.vue`
  - `web/frontend/src/views/trade/History.vue`
- Suggested follow-up scope: continue applying the existing `v1.32` rule to remaining canonical routes in `system` and any remaining `trade` surfaces that still expose count or label-only KPI strips through shared stat-card defaults.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: count-kpi delta truth > cosmetic cleanup
- primary owners selected:
  - `web/frontend/src/views/trade/Signals.vue`
  - `web/frontend/src/views/trade/History.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained a HIGH-blast-radius candidate, so the batch intentionally stayed page-local
- fixes applied:
  - `trade-signals-issue-02`
  - `trade-history-issue-02`
- deferred items: none

## Fix Summary
- Updated the canonical trade-signals route to pass string tallies and explicitly disable `show-change` on both the top KPI strip and the pending-analysis overview cards.
- Updated the canonical trade-history route to pass string tallies where needed and explicitly disable `show-change` on its top KPI strip.
- Strengthened routed component regressions and the Phase 3 route-matrix assertions to guard against `.artdeco-stat-change`, `+0%`, and pseudo precision on the affected routes.
- Reused `myweb-audit v1.32` count-kpi delta truth as the governing rule for this batch; no new skill-version branch was needed.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-05-repair-approval.yaml`
- Approved issue ids:
  - `trade-signals-issue-02`
  - `trade-history-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is HIGH

## Unresolved Items
- No approved repair remains unimplemented in `trade-batch-05`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts` -> passed `4/4`
  - `npx vitest run src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Portfolio.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `10/10`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `16` structurally valid tests including the strengthened trade-signals and trade-history assertions
  - targeted routed-page verification confirmed:
    - the real PM2 `/trade/signals` route issued `/api/v1/trade/signals?limit=20`
    - the same route now shows `交易信号工作台`, top KPI values `0 / 0 / 0 / 未校验`, zero `.artdeco-stat-change` nodes on both stat-card groups, and no `+0%`, `3.00`, `1.00`, or `0.00`
    - the real PM2 `/trade/history` route issued `/api/v1/trade/trades`
    - the same route now shows `交易历史工作台`, top KPI values `0 / 0 / 0 / ¥0`, zero `.artdeco-stat-change` nodes, and no `+0%`, `2.00`, or `1.00`
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying the existing count-kpi delta truth rule to remaining canonical `system` and `trade` routes that still render count or label-only KPI strips through shared stat-card defaults.
