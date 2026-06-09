# Batch Audit Report: data-batch-17

## Scope
- Module: data
- Pages:
  - /data/indicator
- Batch rationale: close the canonical `/data/indicator` first-load action-triggered freshness gap so clicking `执行筛选` after an unverified first-load failure cannot fabricate local `UPDATED`, faux-ready status, or screening-count truth

## Agent Summary

### route-inventory
- `/data/indicator` remains the canonical routed analysis workspace at `web/frontend/src/views/data/Advanced.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond restoring truthful unresolved-context screening behavior on the selected route.

### data-state-audit
- One high-severity routed first-load action-triggered freshness defect remained: the page treated a local screening click as if it had produced a verified snapshot, even when the first load had already failed and no verified analysis context existed.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed workbench pages can already expose action buttons before any verified route snapshot exists, and a local manual action can incorrectly promote placeholder shells into visible freshness/count truth.
- Occurrence basis:
  - `/strategy/backtest` previously required `v1.54` because a rejected manual action could stamp hero freshness before any verified context existed
  - `/data/indicator` expressed the same class of bug through `runScreening()`, which promoted local counters and `UPDATED` from a failed-first-load shell
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.54 + v1.43 + v1.41` checks to routed workbench pages that expose manual actions before verified context exists.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed first-load action-triggered freshness issue
- priority order applied: verified-snapshot truth > page-local containment > verification hardening
- primary owners selected:
  - `web/frontend/src/composables/market/useDataAnalysis.ts`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `data-indicator-issue-04`
- deferred items: none

## Fix Summary
- Added a page-local unresolved-context guard in `useDataAnalysis.runScreening()` so local screening actions no longer mutate counters, status, results, or freshness before a verified analysis snapshot exists.
- Preserved the failed-first-load shell for `/data/indicator` when `执行筛选` is clicked after a first-load failure.
- Strengthened owner and routed regressions to pin the exact `first-load fail -> click 执行筛选` path.
- Reused existing `myweb-audit v1.54` action-triggered freshness guidance; no new skill version was needed in this batch.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-17-repair-approval.yaml`
- Approved issue ids:
  - `data-indicator-issue-04`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-17`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/views/data-advanced-screening-truth.spec.ts -t "does not promote local screening actions into verified updated-at or results after the first load failed"` -> passed `1/1` after reproducing the expected red failure
  - `npx vitest run tests/unit/views/data-advanced-screening-truth.spec.ts src/views/data/__tests__/Advanced.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/views/data-indicator-details.spec.ts` -> passed `8/8`
  - `npx vitest run src/views/data/__tests__/Advanced.spec.ts src/views/data/__tests__/Concepts.spec.ts src/views/data/__tests__/FundFlow.spec.ts tests/unit/views/data-advanced-screening-truth.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-industry-refresh-fallback.spec.ts tests/unit/views/data-concept-refresh-fallback.spec.ts tests/unit/views/data-fund-flow-partial-state.spec.ts` -> passed `19/19`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `25` structurally valid tests including the strengthened `/data/indicator` failed-first-load screening assertion
  - targeted system-Chrome browser verification confirmed:
    - before repair reproduction, clicking `执行筛选` from a failed-first-load shell produced `STATUS: 筛选已就绪 / UPDATED: 2026/5/3 11:20:00`
    - after repair, the same controlled path keeps `STATUS: 同步异常 / UPDATED: --`
    - the same controlled path keeps `-- / -- / -- / -- / --` visible and leaves the results panel unmounted
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
  - an auth-seeded natural PM2 deep-link attempt to `/data/indicator` settled on `/dashboard`, so no natural route success proof is claimed for this batch
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-17-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-17-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-17-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-17-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-17-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/composables/market/useDataAnalysis.ts web/frontend/tests/unit/views/data-advanced-screening-truth.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-17-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-17-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-17-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-17-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/data-indicator-action-triggered-first-load-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/data-batch-17-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.54 + v1.43 + v1.41` to routed workbench pages that expose manual actions before verified context exists, especially where action buttons can currently mutate hero freshness or sibling summary strips from unresolved shells.
