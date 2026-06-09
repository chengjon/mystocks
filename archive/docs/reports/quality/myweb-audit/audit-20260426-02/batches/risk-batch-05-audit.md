# Batch Audit Report: risk-batch-05

## Scope
- Module: risk
- Pages:
  - /risk/overview
  - /risk/stop-loss
- Batch rationale: reuse the strengthened `v1.32` count-kpi delta truth rule on remaining canonical risk routes so plain tally or label-only KPI cards stop inheriting fabricated delta chrome and decimal precision

## Agent Summary

### route-inventory
- `/risk/overview` continues to resolve directly to canonical `web/frontend/src/views/risk/Overview.vue`.
- `/risk/stop-loss` continues to resolve directly to canonical `web/frontend/src/views/risk/StopLoss.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond honest KPI-strip presentation on the selected risk routes.

### data-state-audit
- Two high-severity routed count-kpi truth defects remained: both canonical risk pages exposed count or label-only KPI cards without a verified comparison baseline, yet still inherited shared stat-card flat-delta chrome and pseudo precision.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 2
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed count or label-only KPI strips can accidentally impersonate movement metrics when shared stat-card defaults inject flat dots, `+0%`, and exact-decimal formatting without a real comparison baseline.
- Occurrence basis:
  - `/risk/overview` previously rendered `规则总数`, `启用规则`, and `今日告警` as exact-decimal values with flat-change chrome
  - `/risk/stop-loss` previously rendered `观察标的`, `已触发`, and `临界标的` as exact-decimal values with the same shared chrome, even on honest empty or pending-policy states
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
  - `web/frontend/src/views/risk/Overview.vue`
  - `web/frontend/src/views/risk/StopLoss.vue`
- Suggested follow-up scope: continue applying the existing `v1.32` rule to remaining routed pages that still expose count or label-only KPI strips through shared stat-card defaults.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: count-kpi delta truth > cosmetic cleanup
- primary owners selected:
  - `web/frontend/src/views/risk/Overview.vue`
  - `web/frontend/src/views/risk/StopLoss.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained a HIGH-blast-radius candidate, so the batch intentionally stayed page-local
- fixes applied:
  - `risk-overview-issue-02`
  - `risk-stop-loss-issue-02`
- deferred items: none

## Fix Summary
- Updated the canonical risk overview KPI strip to pass string tallies and explicitly disable `show-change` on all four cards.
- Updated the canonical stop-loss KPI strip to pass string tallies where needed and explicitly disable `show-change` on all four cards.
- Strengthened routed component regressions and the Phase 4 route-matrix assertions to guard against `.artdeco-stat-change`, `+0%`, `1.00`, and `0.00`.
- Reused `myweb-audit v1.32` count-kpi delta truth as the governing rule for this batch; no new skill-version branch was needed.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-05-repair-approval.yaml`
- Approved issue ids:
  - `risk-overview-issue-02`
  - `risk-stop-loss-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is HIGH

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-05`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `11/11`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `11` structurally valid tests including the new risk overview and stop-loss count-kpi assertions
  - targeted routed-page verification confirmed:
    - the real PM2 `/risk/overview` route issued `/api/v1/monitoring/alert-rules` and `/api/v1/monitoring/alerts?page=1&page_size=50`
    - the same route now shows `风险概览工作台`, KPI values `8 / 8 / 0 / 未校验`, zero `.artdeco-stat-change` nodes, and no `+0%`, `1.00`, or `0.00`
    - the real PM2 `/risk/stop-loss` route issued `/api/v1/monitoring/watchlists` and `/api/v1/monitoring/watchlists/18/stocks`
    - the same route now shows `止损雷达工作台`, KPI values `0 / 0 / 0 / --`, zero `.artdeco-stat-change` nodes, and no `+0%`, `1.00`, or `0.00`
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
- Continue applying the existing count-kpi delta truth rule to remaining canonical routes in `trade`, `system`, and adjacent `risk` pages that still render count or label-only KPI strips through shared stat-card defaults.
