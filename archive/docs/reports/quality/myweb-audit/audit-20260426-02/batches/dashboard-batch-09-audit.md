# Batch Audit Report: dashboard-batch-09

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: apply existing selector-scoped verified-snapshot truth to the canonical dashboard capital-flow tab so same-instance local tab switches no longer keep the previous tab's verified ranking rows visible under a new unresolved tab shell

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The affected selector-owned ranking slice is route-owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### data-state-audit
- One high-severity selector truth defect remained: the capital-flow ranking card still treated one route-global verified array as proof for all local flow tabs.
- The defect appeared when the same mounted route switched from a verified `1day` tab to another tab whose first load had not verified yet.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed dashboard or workbench can already own local tab selectors but still keep one route-global verified row set, so same-instance tab switches leak old rows into a newly requested tab before that tab verifies.
- Occurrence basis:
  - `/dashboard` owned the tab selector in the route itself
  - the ranking fetch read live `activeFlowTab` again at resolve time
  - the visible rows and degraded-state copy were therefore not truly tab-scoped
- Shared component or helper involved:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- Suggested follow-up scope: continue applying existing selector-scoped verified-snapshot truth to routed dashboards or workbenches that can switch local tabs without remounting.

## Main Skill Decisions
- duplicates merged: no
- priority order applied: selector-scoped verified-snapshot truth > local tab row provenance > pending-tab honesty
- primary owner selected:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- shared-impact review items:
  - none beyond the canonical dashboard route
- fixes applied:
  - `dashboard-home-issue-09`
- deferred items: none

## Fix Summary
- Captured ranking request ownership by `requestTab` instead of re-reading live `activeFlowTab` at settle time.
- Stored verified capital-flow rows per tab and scoped degraded-state copy per tab.
- Rendered active tab rows and heatmap input only from the current tab's own verified snapshot.
- Added owner and routed regressions that lock the `1day -> 3day` same-instance unresolved-switch proof.
- Reused existing `myweb-audit v1.71` / `v1.68` selector rule without adding a new version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-09-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-09`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-09`.

## Reasons Not Fixed
- The repair intentionally stayed inside the canonical dashboard owner and route-owned composable; no shared dashboard-shell or shared chart-state abstraction was introduced.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` isolated the `1day -> 3day` unresolved tab-switch proof on `/dashboard`
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `23/23`
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "capital-flow rows into a different tab"` -> passed `1/1` after first reproducing the expected red failure
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed the new dashboard capital-flow tab selector assertion in a structurally valid matrix
  - `timeout 180s npm run type-check` -> failed only on pre-existing unrelated errors in `src/components/technical/composables/useKLinePatternOverlays.ts`; no new type errors were introduced by this batch's touched files
  - targeted routed-page verification confirmed:
    - `/dashboard` first shows verified `1day` rows `贵州茅台 / 宁德时代`
    - after switching to active `3日` while the `3day` request is unresolved, the card no longer shows those old `1day` rows
    - the unresolved `3day` path does not misreport `资金流向持续排名暂不可用`
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path

## Next Batch Plan
- Continue applying selector-scoped verified-snapshot truth to routed dashboards and workbenches that switch local tabs, watchlists, periods, or other secondary selectors without remounting.
