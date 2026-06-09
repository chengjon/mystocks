# Page Audit: /risk/alerts

## Scope
- Route: `/risk/alerts`
- Canonical entry: `web/frontend/src/views/risk/Alerts.vue`
- Batch: `risk-batch-10`

## Defect Summary
- The routed risk alerts page aggregated `alert-rules` and `alerts` through a single `useArtDecoApi` shell but still bound hero `REQ_ID` and sibling count surfaces directly to the latest request attempt.
- As a result, first-load failures could leak the failed alerts request id and fabricate `UNREAD: 0`, `RULES: 0`, `ALERTS: 0`, and top-strip zero counts before any verified snapshot existed, while later refresh failures cleared verified rules and alerts to empty arrays instead of preserving the current visible shell.

## Repair
- Added page-local verified snapshot state so hero `REQ_ID` now follows the currently visible verified alerts snapshot rather than the latest failed refresh attempt.
- Added first-load placeholder gating for `UNREAD`, `RULES`, `ALERTS`, and the top stats strip, so unresolved or failed first loads render `--` instead of faux zero counts or empty-success copy.
- Added stale-refresh handling so refresh-after-success failures keep verified rules and alerts visible with stale-copy messaging instead of clearing the route to empty-state truth.

## Verification
- Component regression:
  - `npx vitest run src/views/risk/__tests__/Alerts.spec.ts` passed `3/3`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `20` tests including the new risk-alerts first-load and stale-refresh assertions
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first-load failure now renders `REQ_ID: N/A`, `UNREAD: --`, `RULES: --`, `ALERTS: --`, top-strip `-- / -- / -- / --`, and `获取告警记录失败，当前暂无已验证告警快照。`
  - the same first-load failure path no longer leaks the failed request id anywhere in the visible route shell
  - controlled success-then-refresh-fail now keeps `REQ_ID: req-live-risk-alerts-success`, preserves visible rule and alert rows, and renders `获取告警记录失败，当前仍显示上次成功同步的告警快照。`
  - natural PM2 `/risk/alerts` headless observation still falls back to `/dashboard -> /login` under the same auth-timing artifact, so natural-route success proof is not claimed for this batch

## Skill Feedback
- This page did not require a new skill-version bump. It reused existing `myweb-audit v1.43` request-provenance retention rules together with the already-promoted first-load placeholder rules from earlier batches.
