# Page Audit Report: /watchlist/signals

## Purpose
Signal timeline surface for reviewing recent strategy actions and their execution ordering.

## Agent Findings

### route-inventory
- Routed entrypoint resolves to `web/frontend/src/views/watchlist/Signals.vue`, which wraps `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`.

### functional-audit
- No primary functional interaction issue was selected for this page in the current batch.

### data-state-audit
- Timeline sorting depended only on `HH:MM:SS` parsing and could misorder cross-day entries.

### visual-artdeco-audit
- No primary visual defect was selected for this page in the current batch.

### responsive-a11y-audit
- No primary responsive issue was selected for this page in the current batch.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- [Medium] Watchlist signals timeline sort loses date context and can misorder cross-day entries.
- Source roles: data-state-audit
- Why consolidated: one discrete timeline ordering issue for the signals route
- Primary owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger: inspect the normalization and sort path when signals span more than one trading day
- Expected: ordering should preserve full temporal context
- Actual: sort order fell back to seconds parsed from `HH:MM:SS`, dropping day-level ordering context

## Shared Impact
- Shared component or layout involved: none
- Impact basis: page-local timeline logic with a paired data normalizer
- Potentially affected related pages: none selected in this batch
- Follow-up check needed: no
- Decision timing: pre-repair
- Staged-scope follow-up needed: no isolated staged check was created for this page

## Repair Plan
- Fix now: add sortable timestamp normalization and prefer it in timeline ordering
- Fix with shared-impact review: none
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-01-repair-approval.yaml`
- Manifest resume cursor after approval: `partial-closeout-recorded`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts` added `sortTimestamp` normalization from direct timestamp fields and date-plus-time combinations
- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` now prefers `sortTimestamp` and falls back to `HH:MM:SS` parsing only when normalized timestamps are absent

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse: Chromium reused the existing PM2 frontend via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Verified at: 2026-04-26
- Checked routes:
  - `/watchlist/signals`
- Checked states:
  - default
  - empty
  - error
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes: node-level normalization tests passed, and targeted Chromium route regression passed after aligning the trading signals store endpoint to `/v1/trade/signals`

## Residual Risks
- [Low] Cross-day ordering is repaired in code, node-tested, and route-verified, but browser proof currently covers the stubbed watchlist timeline rather than a live backend payload.
- Reason: runtime closure for this batch used controlled Chromium mock regression
- Next action: no immediate repair needed; expand to backend-backed route verification only if a later batch requires live-data proof
