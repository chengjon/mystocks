# Change: Reconcile dashboard and DealingRoom route truth

## Why
`ArtDecoDashboard.vue` is still the live home shell in current router truth and generated page-config truth, but the governed frontend page inventory still describes the same page as `DealingRoom` at `/dealing-room`. That drift now blocks `restructure-frontend-directory` task `8.6` and makes it unsafe to deprecate a page that is still live.

## What Changes
- Canonicalize `/dashboard` as the single route truth for the home / trading-room shell backed by `ArtDecoDashboard.vue`.
- Reclassify `DealingRoom` as a legacy compatibility alias or documentation label instead of a separate active page truth.
- Keep `/trade/terminal` and `TradingDashboard.vue` separate from dashboard / DealingRoom semantics.
- Block deprecation of `ArtDecoDashboard.vue` until route truth, page-inventory truth, and generated config truth are reconciled.

## Impact
- Affected specs: `frontend-routing`, `file-organization`
- Affected code: `web/frontend/src/router/index.ts`, generated page-config inputs and outputs, governed page-inventory docs, `restructure-frontend-directory` task ledger
- Risk: Low to medium. The change is mostly semantic reconciliation, but it touches the P0 home shell and compatibility routes.
