# Page Audit: /risk/stop-loss

## Scope
- Route: `/risk/stop-loss`
- Canonical entry: `web/frontend/src/views/risk/StopLoss.vue`
- Batch: `risk-batch-08`

## Defect Summary
- The routed stop-loss page was backed by shared watchlist Pinia stores whose transforms extracted row arrays but erased resolved `success:false` failure truth before the page could classify unavailable versus empty-success state.
- As a result, first-load watchlist-stock failures could collapse into empty monitoring success while still leaking failed request provenance, and later refresh failures could overwrite the hero request id even though the visible cards still belonged to an earlier verified snapshot.

## Repair
- Moved the routed owner onto page-local raw-contract fetching for watchlists, watchlist stocks, and quotes so resolved `success:false` envelopes stay visible to the route owner.
- Added verified-snapshot request provenance so `REQ_ID` now follows the currently visible verified stop-loss snapshot rather than the latest failed retry.
- Added first-load placeholders and stale-refresh preservation so unresolved or failed first loads render `N/A` and `--`, while refresh-after-success failures retain verified cards and show stale-copy messaging.

## Verification
- Component regression:
  - `npx vitest run src/views/risk/__tests__/StopLoss.spec.ts` passed `4/4`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `16` tests including the new stop-loss failure and stale-refresh paths
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first-load `success:false` watchlist-stock failure now renders `REQ_ID: N/A`, `CRITICAL: --`, `TRIGGERED: --`, top-strip `-- / -- / -- / --`, and `watchlist stocks unavailable，当前暂无已验证止损快照。`
  - the same first-load failure path no longer leaks `req-live-stoploss-first-fail` anywhere in the visible route shell
  - controlled success-then-refresh-fail now keeps `REQ_ID: req-live-stoploss-success`, preserves the visible `贵州茅台` and `宁德时代` cards, and shows `watchlist stocks refresh unavailable，当前仍显示上次成功同步的止损快照。`
  - natural PM2 `/risk/stop-loss` still loads and currently renders the honest live empty-state path with a real request id and `0 / 0 / 0 / --`

## Skill Feedback
- This page produced a new reusable audit rule for `myweb-audit v1.42`: if a shared Pinia-store transform or collection extractor erases resolved failure envelopes before the routed owner can classify them, the route must preserve failure truth before that transform boundary or switch to a page-local raw-contract path.
