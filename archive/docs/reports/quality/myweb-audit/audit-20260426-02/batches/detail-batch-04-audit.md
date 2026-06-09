# Batch Audit Report: detail-batch-04

## Scope
- Module: detail
- Pages:
  - /detail/graphics/:symbol
- Batch rationale: close the canonical `/detail/graphics/:symbol` indicators enrichment-slice truth gap so a failed indicators sibling slice no longer collapses into generic empty-state copy or clears previously verified indicators while the K-line primary snapshot remains visible, and codify that routed failure mode as `myweb-audit v1.60`.

## Agent Summary

### route-inventory
- `/detail/graphics/:symbol` remains the canonical routed technical-analysis detail page at `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: the detail graphics route treated indicators-slice failures like generic empty-state truth even when the K-line primary snapshot was already verified and visible.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a canonical detail route can correctly preserve its primary sample snapshot and still misrepresent route truth if a sibling enrichment slice collapses into generic empty copy or clears previously verified enrichment values after refresh failure.
- Occurrence basis:
  - `/detail/graphics/:symbol` kept the K-line trend snapshot visible while the indicators slice fell back to generic empty-state truth on first-load failure
  - the same route also cleared previously verified indicators after a later refresh failure instead of retaining them with stale-enrichment messaging
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.60 + v1.45` to detail routes that mix one primary snapshot with sibling enrichment slices such as indicators, annotations, or derived detail metrics.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed enrichment-slice issue
- priority order applied: preserve K-line primary truth > make indicators-slice failure explicit > retain previously verified indicators on later refresh failure
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-graphics-issue-04`
- deferred items: none

## Fix Summary
- Updated the routed detail owner to track indicators-slice verification and indicators-slice failure separately from the K-line primary snapshot.
- Replaced generic indicators empty copy with explicit first-load partial-failure copy when only the indicators slice fails.
- Preserved previously verified indicators on later refresh failure and added stale-enrichment runtime messaging.
- Added owner regressions and routed Phase 1 assertions for both indicators first-load failure and `success -> indicators refresh fail`.
- Introduced `myweb-audit v1.60` so future detail audits treat sibling enrichment-slice partial-failure truth as a routed data-state requirement.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `detail-graphics-issue-04`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-04`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` -> passed `5/5`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed the new `/detail/graphics/:symbol` indicators-slice assertions in a structurally valid matrix
  - targeted system-Chrome browser verification confirmed:
    - a controlled first-load indicators failure now keeps the K-line trend snapshot visible and renders `技术指标暂不可用，当前仅显示趋势数据。`
    - a controlled `success -> indicators refresh fail` path now keeps `RSI 61.2 偏强` visible
    - the same later-failure path now renders `技术指标部分加载失败：...，当前仍显示上次成功同步的技术指标快照。`
    - the route no longer falls back to `暂无技术指标结果。`
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
