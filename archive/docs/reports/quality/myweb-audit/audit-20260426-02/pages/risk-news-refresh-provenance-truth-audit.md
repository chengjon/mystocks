# Page Audit: /risk/news

## Scope
- Route: `/risk/news`
- Canonical entry: `web/frontend/src/views/risk/News.vue`
- Batch: `risk-batch-11`

## Defect Summary
- The routed risk news page aggregated announcements through a single `useArtDecoApi` shell but still bound hero `REQ_ID` and sibling count surfaces directly to the latest request attempt.
- As a result, first-load failures could leak the failed announcements request id and fabricate `TODAY: 0`, `ANNOUNCEMENTS: 0`, `LINKED: 0`, and top-strip zero counts before any verified snapshot existed, while later refresh failures cleared verified announcements to empty arrays instead of preserving the current visible shell.

## Repair
- Added page-local verified snapshot state so hero `REQ_ID` now follows the currently visible verified announcements snapshot rather than the latest failed refresh attempt.
- Added first-load placeholder gating for `TODAY`, `ANNOUNCEMENTS`, `LINKED`, and the top stats strip, so unresolved or failed first loads render `--` instead of faux zero counts or empty-success copy.
- Added stale-refresh handling so refresh-after-success failures keep verified announcements visible with stale-copy messaging instead of clearing the route to empty-state truth.

## Verification
- Component regression:
  - `npx vitest run src/views/risk/__tests__/News.spec.ts` passed `3/3`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `22` tests including the new risk-news first-load and stale-refresh assertions
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first-load failure now renders `REQ_ID: N/A`, `TODAY: --`, `ANNOUNCEMENTS: --`, `LINKED: --`, top-strip `-- / -- / -- / --`, and `获取公告失败，当前暂无已验证公告快照。`
  - the same first-load failure path no longer leaks the failed request id anywhere in the visible route shell
  - controlled success-then-refresh-fail now keeps `REQ_ID: req-live-risk-news-success`, preserves visible announcement rows, and renders `获取公告失败，当前仍显示上次成功同步的公告快照。`
  - natural PM2 `/risk/news` now reaches the route and renders a real request id plus honest live empty-state `0 / 0 / 0 / 0`

## Skill Feedback
- This page did not require a new skill-version bump. It reused existing `myweb-audit v1.43` request-provenance retention rules together with the already-promoted first-load placeholder rules from earlier batches.
