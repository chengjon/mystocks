## 1. Spec Reconciliation
- [x] 1.1 Update `frontend-routing` spec with canonical dashboard route truth and DealingRoom compatibility semantics
  - Evidence: `specs/frontend-routing/spec.md` defines `/dashboard` as canonical, keeps `/dealing-room` as legacy compatibility, and preserves `/trade/terminal` separation.
- [x] 1.2 Update `file-organization` spec to block deprecating active route-bound pages
  - Evidence: `specs/file-organization/spec.md` blocks moving live route shells into `deprecated/` while router truth, generated page-config truth, or governed inventory still bind the page.

## 2. Repo Truth Alignment
- [x] 2.1 Update governed frontend page inventory so `/dashboard` is canonical and `DealingRoom` is treated as a legacy alias or display label
  - Evidence: `docs/plans/frontend-page-optimization-list.md` now tracks `Dashboard` at `/dashboard` and explicitly marks `DealingRoom` as legacy compatibility only.
- [x] 2.2 If compatibility is required, add or preserve a `/dealing-room` alias/redirect to the canonical dashboard shell
  - Evidence: router compatibility behavior remains covered by `web/frontend/tests/unit/config/dashboard-route-canonical-truth.spec.ts`, which asserts the legacy redirect, and by Playwright login smoke for `/dealing-room`.
- [x] 2.3 Align generated page-config truth with the reconciled canonical naming
  - Evidence: `web/frontend/src/config/__tests__/pageConfig.home.spec.ts` now asserts `dashboard` is canonical and `dealing-room` is not exposed as a separate page-config route name.

## 3. Restructure Unblock
- [x] 3.1 Update `restructure-frontend-directory` task `8.6` to remove the unsafe deprecation assumption
  - Evidence: `openspec/changes/restructure-frontend-directory/tasks.md` task `8.6` now records the completed reconciliation and blocks deprecating `ArtDecoDashboard.vue` under the current scope.
- [x] 3.2 Confirm `TradingDashboard.vue` remains exclusive to `/trade/terminal` until a separate approved change says otherwise
  - Evidence: `web/frontend/tests/unit/config/dashboard-route-canonical-truth.spec.ts` asserts `trade-terminal` remains distinct from dashboard / DealingRoom semantics.
- [x] 3.3 Run route smoke validation for `/`, `/dashboard`, and any retained `/dealing-room` alias
  - Evidence:
    - `cd web/frontend && npx vitest run src/config/__tests__/pageConfig.home.spec.ts tests/unit/config/dashboard-route-canonical-truth.spec.ts`
    - `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test tests/e2e/auth-login.spec.ts --config playwright.config.js --project chromium`
