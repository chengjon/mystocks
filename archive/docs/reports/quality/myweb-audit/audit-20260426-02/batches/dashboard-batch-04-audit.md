# Batch Audit Report: dashboard-batch-04

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: close the retained fund-flow summary delta-chrome gap on the canonical dashboard route so description-only summary cards no longer inherit shared `● +0%` surfaces, and fold that numeric-surface pattern back into myweb-audit as `v1.57`

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.

### functional-audit
- No new interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity route-truth defect remained: the two description-only fund-flow summary cards inherited shared stat-card change chrome and rendered faux flat-change surfaces.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed live summary slices can legitimately reuse shared stat-card primitives, but description-only cards still need page-local `show-change=false` when the current live contract proves no comparison baseline.
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Suggested follow-up scope: continue applying `v1.57` anywhere a routed live summary slice mixes real delta cards with description-only totals or ratios on the same shared stat-card family.

## Main Skill Decisions
- duplicates merged: yes; the extra change nodes and faux `+0%` surfaces on `北向资金总额` and `主力净流入` were merged into one route-local summary-card delta-chrome issue because they came from the same shared default leaking through the page template
- priority order applied: visible route truth > numeric-surface honesty > shared-component containment
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- shared-impact review items: none
- fixes applied:
  - `dashboard-home-issue-04`
- deferred items: none

## Fix Summary
- Explicitly disabled shared change chrome on the description-only `北向资金总额` and `主力净流入` cards.
- Added a targeted dashboard logic regression proving `.enhanced-fund-flow` now renders `2` change nodes instead of `4`.
- Added a routed phase-1 matrix assertion that the canonical `/dashboard` route keeps only the two verified delta cards as change-bearing surfaces.
- Upgraded `myweb-audit` to `v1.57` with summary-card delta-chrome checks.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-04`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-04`.

## Reasons Not Fixed
- Shared `ArtDecoStatCard.vue` defaults were intentionally left untouched because this batch only needed a route-local honest-surface override on `/dashboard`.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "does not render default change chrome for description-only fund-flow summary cards"` -> reproduced the expected red failure and then passed `1/1`
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `14/14`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `29` structurally valid tests
  - controlled browser verification confirmed `.enhanced-fund-flow` now renders exactly `2` `.artdeco-stat-change` nodes
  - the same controlled browser verification confirmed the routed fund-flow overview no longer shows `+0%` on `北向资金总额` or `主力净流入`
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch continued to use system-`google-chrome` Playwright-library verification

## Next Batch Plan
- Continue scanning routed live summary slices that mix true delta cards with description-only totals or ratios on the same shared stat-card family.
- Revisit `/dashboard` only if another distinct aggregate or sibling-slice truth defect appears; the retained fund-flow summary delta-chrome gap is now closed.
