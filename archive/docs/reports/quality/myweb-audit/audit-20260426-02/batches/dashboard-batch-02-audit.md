# Batch Audit Report: dashboard-batch-02

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: apply the existing `v1.55` multi-slice refresh-retention rule to the canonical dashboard route so a later fund-flow refresh failure no longer replaces an already verified fund-flow slice with blocking inline error truth

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The route-local slice state owner remains `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### functional-audit
- No separate interaction-path fix was implemented in this batch.
- One out-of-scope observation was recorded: the visible dashboard `刷新数据` control did not trigger a second fund-flow request during natural PM2 browser observation on this machine.

### data-state-audit
- One high-severity route-truth defect remained: the dashboard still treated a later fund-flow refresh failure as blocking inline error truth even after the route had already rendered a verified fund-flow slice.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a multi-slice routed workbench can preserve raw slice data in memory but still replace the visible verified slice with blocking inline error truth on later refresh failures if the same error channel is reused for both first-load failure and stale-refresh degradation.
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Suggested follow-up scope: continue applying `v1.55` to other canonical routed dashboards or workbenches whose later slice refresh failures still override already verified visible slices.

## Main Skill Decisions
- duplicates merged: yes; the blocking inline error and the loss of visible verified fund-flow cards were merged into one dashboard slice-retention issue because they distort the same stale-refresh state transition on `/dashboard`
- priority order applied: verified slice retention truth > routed stale-refresh coverage > natural control-path observation logging
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- shared-impact review items: none
- fixes applied:
  - `dashboard-home-issue-02`
- deferred items:
  - follow-up investigation of the natural PM2 dashboard refresh control not triggering a second fund-flow request

## Fix Summary
- Split dashboard fund-flow failure semantics into blocking first-load errors vs later degraded refresh warnings.
- Preserved the verified fund-flow cards and chart after later refresh failures.
- Strengthened dashboard logic coverage with a composable harness for `success -> fund-flow refresh fail`.
- Strengthened routed phase1 coverage for the same dashboard stale-refresh case.
- Reused the existing `myweb-audit v1.55` multi-slice refresh-retention rule; no new skill version bump was required.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-02-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - the natural PM2 dashboard refresh-control observation remains deferred because it is adjacent but distinct from the repaired fund-flow stale-refresh defect

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-02`.

## Reasons Not Fixed
- The natural PM2 dashboard `刷新数据` control-path observation was not repaired in this batch because it is a separate interaction defect from the repaired fund-flow slice-retention issue.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "keeps the last verified fund-flow slice visible when a later fund-flow refresh fails"` -> passed `1/1` after reproducing the expected red failure first
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `12/12`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `28` structurally valid tests including the strengthened dashboard stale-refresh case
  - controlled browser verification confirmed `/dashboard` still renders the verified `沪股通净流入 / 18.5亿` slice on initial load
  - the same controlled browser verification recorded that clicking the visible `刷新数据` control did not trigger a second fund-flow request in the natural PM2 path on this machine, so the stale-refresh proof for the repaired route state relies on the strengthened dashboard logic harness and routed phase1 coverage instead of that control path
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch continued to use system-`google-chrome` Playwright-library verification

## Next Batch Plan
- Follow up on the natural dashboard refresh-control path so a second `/dashboard` request cycle can be reproduced directly through the visible PM2 route shell.
- Continue applying `v1.55` to other canonical routed dashboards or workbenches whose later slice refresh failures still override already verified visible slices.
