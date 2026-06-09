# Batch Audit Report: data-batch-18

## Scope
- Module: data
- Pages:
  - /data/indicator
- Batch rationale: repair the canonical `/data/indicator` route so category-owned indicator detail context cannot remain visible after a same-instance `趋势指标 -> 动量指标` switch without a newly selected indicator

## Agent Summary

### route-inventory
- `/data/indicator` remains the canonical routed analysis workspace at `web/frontend/src/views/data/Advanced.vue`.

### data-state-audit
- One high-severity selector-owned detail defect remained: the route trusted one route-global `selectedIndicator`, so a same-instance category switch could reopen the editor with stale detail content from the earlier category.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed workbench pages can already expose local selector-owned detail panels whose context is still stored route-globally instead of by the active selector shell.
- Occurrence basis:
  - `/data/indicator` already exposed a persistent `指标详情` tab and a local `activeCategory` selector
  - the route allowed the editor to reopen after a category switch without reconciling `selectedIndicator` against the current category
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.71 + v1.68` to routed workbench/detail pages whose local detail panels can reopen under a new selector without a fresh selection.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` selector-owned detail-context issue
- priority order applied: selector-owned detail truth > page-local containment > routed verification hardening
- primary owners selected:
  - `web/frontend/src/composables/market/useDataAnalysis.ts`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `data-indicator-issue-05`
- deferred items: none

## Fix Summary
- Added a page-local category mismatch watcher in `useDataAnalysis` so `selectedIndicator` is cleared when the active category changes away from the selected indicator's category.
- Preserved the neutral editor empty state when a same-instance category switch occurs without a freshly selected indicator in the new category.
- Strengthened owner and Phase 2 routed regressions to lock the `趋势指标 -> 动量指标` editor-reopen path.
- Reused existing `myweb-audit v1.71` and `v1.68` selector-owned snapshot guidance; no new skill version was needed in this batch.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-18-repair-approval.yaml`
- Approved issue ids:
  - `data-indicator-issue-05`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-18`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/views/data-advanced-screening-truth.spec.ts -t "clears the previous selected indicator context when the user switches the active category before reopening the editor"` -> first failed as expected, then passed `1/1`
  - `npx vitest run tests/unit/views/data-advanced-screening-truth.spec.ts src/views/data/__tests__/Advanced.spec.ts tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-cutover.spec.ts` -> passed `11/11`
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `29` structurally valid tests including the strengthened `/data/indicator` category-switch assertion
  - targeted system-Chrome browser verification confirmed:
    - the controlled route first shows `selected indicator / 移动平均线 / MA`
    - after returning to the library and switching to `动量指标`, reopening the editor reaches `从指标库选择一个指标`
    - the stale prior `selected indicator / 移动平均线 / MA` copy no longer remains visible after the category switch
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Type-check note:
  - `timeout 180s npm run type-check` failed only on pre-existing unrelated dirty-worktree errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`; no new type errors were introduced by this batch
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-18-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-18-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-18-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-18-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-18-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/composables/market/useDataAnalysis.ts web/frontend/tests/unit/views/data-advanced-screening-truth.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-18-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-18-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-18-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-18-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/data-indicator-category-selector-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/data-batch-18-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.71 + v1.68 + v1.66` to routed workbench/detail pages whose local detail/editor panels can reopen under a new selector, category, or query shell without a fresh selector-owned snapshot.
