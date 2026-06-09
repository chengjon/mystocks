# Page Audit: /risk/stop-loss selector pending card truth

## Page
- Route: `/risk/stop-loss`
- Canonical entry: `web/frontend/src/views/risk/StopLoss.vue`
- Audit focus: clear previous stop-loss cards when a new primary watchlist selector is still unresolved

## Finding
- Severity: High
- Issue id: `risk-stop-loss-issue-18`
- Summary: the routed owner previously switched hero provenance and summary counts to a new primary watchlist, but it kept the previous watchlist cards visible until the new stocks slice resolved.

## Repair
- Cleared visible stop-loss cards immediately when the resolved primary watchlist selector changes away from the last verified selector key.
- Kept the existing stale-retention behavior for same-selector refresh failures after success.
- Added owner and Phase 4 regressions for the unresolved selector-switch path.

## Verification
- Owner regression: `npx vitest run src/views/risk/__tests__/StopLoss.spec.ts`
- Routed matrix coverage: `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list`
- Controlled browser proof:
  - first shell shows verified `req-live-stoploss-101-success` and visible `贵州茅台 / 宁德时代`
  - after the primary selector switches to an unresolved watchlist, hero changes to `REQ_ID: N/A`
  - top-strip changes to `-- / -- / -- / --`
  - visible card count drops to `0`
  - stale `贵州茅台` no longer remains in the new selector shell
