# Batch Audit Report: dashboard-batch-05

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: apply the new `v1.62` retained-primary-slice aggregate-truth rule so the canonical dashboard route keeps the verified industry slice visible on later refresh failure while degrading aggregate route provenance and alerting

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- Route-level industry slice truth and aggregate provenance are owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### functional-audit
- No separate interaction-path defect required an independent repair wave once the industry-slice later-failure branch was corrected.

### data-state-audit
- One high-severity route-truth defect remained: a later industry refresh failure reset the verified industry slice to fallback truth and did not cleanly express retained-slice aggregate degradation.
- Before repair, the route could fall back to `0↑/0↓` and empty heat surfaces even though the correct dashboard behavior was to preserve the last verified industry snapshot with degraded aggregate shell semantics.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a multi-slice routed dashboard may preserve or replace later-failed primary slices incorrectly if it does not distinguish first-load fallback from retained verified-slice truth.
- Occurrence basis:
  - `/dashboard` already had aggregate route meta, route alerts, and multiple primary slices
  - the industry branch previously used one catch path for both first-load failure and later refresh failure
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- Suggested follow-up scope: continue applying `v1.62` anywhere a routed dashboard or multi-slice workbench retains or resets a later-failed primary slice while exposing aggregate `DATA / SYNC` shell truth.

## Main Skill Decisions
- duplicates merged: yes; market breadth, heat-map, sector-radar, and aggregate `DATA / SYNC` drift were merged into one dashboard later-industry-refresh issue because they all came from the same route-local failure branch
- priority order applied: visible primary-slice truth > aggregate provenance truth > shared-state containment
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- shared-impact review items: none
- fixes applied:
  - `dashboard-home-issue-05`
- deferred items: none

## Fix Summary
- Added a verified industry-slice boundary so later industry refresh failures no longer clear the visible market breadth, heat-map, or sector-radar surfaces.
- Degraded the aggregate dashboard shell to `DATA: MIXED`, `SYNC: DEGRADED`, and a route-level industry alert whenever a later industry refresh fails after prior success.
- Added owner and routed regressions that lock the `success -> later industry refresh fail` truth path.
- Upgraded `myweb-audit` to `v1.62` with retained-primary-slice aggregate-truth guidance.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-05-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-05`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-05`.

## Reasons Not Fixed
- The repair intentionally stayed inside the dashboard route family and did not widen into shared global dashboard helpers because the current blast radius was already low and page-local repair was sufficient.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used to isolate the later industry refresh failure while leaving other core slices verified
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "keeps the last verified industry slice visible when a later industry refresh fails"` -> reproduced the expected red failure and then passed `1/1`
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `15/15`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `32` structurally valid tests including the new dashboard retained-industry-slice assertion
  - targeted routed-page verification confirmed the settled later-industry-failure path now renders:
    - `DATA: MIXED`
    - `SYNC: DEGRADED`
    - route alert `行业热度数据暂不可用`
    - visible market breadth `2↑/0↓`
    - no `.heat-map-card .chart-state-note`
    - no `.sector-radar-card .chart-state-note`
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path

## Next Batch Plan
- Continue applying `v1.62` to other canonical routed dashboards or multi-slice workbenches that must preserve a later-failed primary slice while degrading aggregate route-shell truth.
