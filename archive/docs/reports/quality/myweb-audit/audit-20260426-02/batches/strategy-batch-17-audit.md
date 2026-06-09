# Batch Audit Report: strategy-batch-17

## Scope
- Module: strategy
- Pages:
  - /strategy/gpu
- Batch rationale: extend partial-sync banner truth auditing so the canonical strategy-gpu route no longer lets a one-slice refresh masquerade as a full recent route sync.

## Agent Summary

### route-inventory
- `/strategy/gpu` remains the canonical routed GPU monitoring surface through `web/frontend/src/views/strategy/BacktestGPU.vue`.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route-level runtime banner treated any partial primary-slice success as enough evidence to stamp generic `最近同步` wording, even when the companion primary slice was still unresolved.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: route-level runtime or freshness banners that summarize multiple primary slices must not present generic full-sync wording when only some slices refreshed.
- Occurrence basis:
  - `/strategy/gpu` owns one visible top runtime banner over both status and performance primary slices
  - a performance-only or status-only first-load path could still produce `最近同步 <time>` while the other slice stayed pending
- Shared component or token involved:
  - `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
  - `web/frontend/src/views/strategy/BacktestGPU.vue`
- Suggested follow-up scope: continue applying `v1.59` to routed runtime, monitoring, and workbench pages that collapse multi-slice freshness into one visible banner.

## Main Skill Decisions
- duplicates merged: performance-only and status-only partial-sync banner leaks were consolidated into one route-level freshness issue
- priority order applied: route-level partial-sync truth > page-local banner copy > slice visibility retention
- primary owners selected:
  - `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/BacktestGPU.vue` was reviewed as the canonical template owner and only needed the banner binding update
- fixes applied:
  - `strategy-gpu-issue-02`
- deferred items:
  - no backend GPU schema redesign or shared runtime-banner abstraction was approved for this batch

## Fix Summary
- Added route-local `partialSyncNotice` handling inside `useBacktestGPU`.
- Derived a page-owned `runtimeStatusMessage` so partial primary-slice refreshes render `部分同步` plus slice-specific pending or retained copy.
- Updated the canonical route template to consume the new route-owned banner message.
- Added owner-level regression coverage for both performance-only and status-only first-load partial-sync paths.
- Strengthened routed Phase 3 matrix coverage so `/strategy/gpu` keeps partial-sync wording honest in browser verification.
- Promoted `myweb-audit` to `v1.59` for route-level partial-sync banner truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-17-repair-approval.yaml`
- Approved issue ids:
  - `strategy-gpu-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-17`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context fulfillment isolated both partial-sync and full-success proofs on `/strategy/gpu`
- Regression checks completed:
  - `npx vitest run src/views/strategy/composables/__tests__/useBacktestGPU.spec.ts` -> passed `2/2`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `42` structurally valid tests including the strengthened `/strategy/gpu` partial-sync assertion
  - targeted routed-page verification confirmed:
    - the controlled performance-only path now renders `部分同步 ... · GPU 状态待同步`
    - the same path preserves `64x` on the visible performance card while the status card degrades to `待同步`
    - a controlled full-success path still renders generic `最近同步 ...`

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-17-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-17-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-17-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-17-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-gpu-partial-sync-banner-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
