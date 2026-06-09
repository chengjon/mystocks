# Page Audit: /risk/overview

## Scope
- Route: `/risk/overview`
- Canonical entry: `web/frontend/src/views/risk/Overview.vue`
- Batch: `risk-batch-09`

## Defect Summary
- The routed risk overview page aggregated `alert-rules` and `alerts` through a single `useArtDecoApi` shell but still bound hero `REQ_ID` and sibling count surfaces directly to the latest request attempt.
- As a result, first-load failures could leak the failed alerts request id and fabricate `ALERTS: 0` plus top-strip zero counts before any verified snapshot existed, while later refresh failures cleared verified rules and alerts to empty arrays instead of preserving the current visible shell.

## Repair
- Added page-local verified snapshot state so hero `REQ_ID` now follows the currently visible verified overview snapshot rather than the latest failed refresh attempt.
- Added first-load placeholder gating for `ALERTS`, `RULES`, and the top stats strip, so unresolved or failed first loads render `--` instead of faux zero counts.
- Added stale-refresh handling so refresh-after-success failures keep verified rules and alerts visible with stale-copy messaging instead of clearing the route to empty-state truth.

## Verification
- Component regression:
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts` passed `6/6`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `18` tests including the new risk-overview first-load and stale-refresh assertions
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first-load failure now renders `REQ_ID: N/A`, `ALERTS: --`, `RULES: --`, top-strip `-- / -- / -- / --`, and `获取预警记录失败，当前暂无已验证风险概览快照。`
  - the same first-load failure path no longer leaks the failed request id anywhere in the visible route shell
  - controlled success-then-refresh-fail routed proof is now pinned by component and Phase 4 regressions; the equivalent headless browser reproduction remained auth/reload observation-only on this machine and is therefore recorded as verification residual rather than overclaimed as live success
  - natural PM2 `/risk/overview` headless observation currently falls back to `/login` under the same auth-timing artifact, so natural-route success proof is not claimed for this batch

## Skill Feedback
- This page did not require a new skill-version bump. It reused existing `myweb-audit v1.43` request-provenance retention rules together with the already-promoted first-load numeric placeholder rules from earlier batches.
