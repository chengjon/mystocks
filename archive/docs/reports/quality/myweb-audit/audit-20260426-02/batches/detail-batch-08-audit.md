# Batch Audit Report: detail-batch-08

## Scope
- Module: detail
- Pages:
  - /detail/graphics/:symbol
- Batch rationale: close the canonical `/detail/graphics/:symbol` selector-scoped period truth gap so a same-instance `1d -> 1w` switch cannot inherit the previous verified period snapshot, reusing existing `myweb-audit v1.71`.

## Agent Summary

### route-inventory
- `/detail/graphics/:symbol` remains the canonical routed graphics detail page at `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: the primary K-line and indicator slices were not keyed to the current `symbol + period` selector context, so a new period could inherit the previous verified `1d` snapshot under the same routed page instance.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-driven detail workbenches must treat the full active selector context, not just route params, as primary snapshot provenance.
- Occurrence basis:
  - `/detail/graphics/:symbol` could let `PERIOD: 1w` inherit the verified `1d` K-line points, request id, and indicator workspace when the first `1w` load failed before its own verified snapshot existed
- Shared component or token involved:
  - the direct K-line request helper `web/frontend/src/views/market/marketKlineData.ts`
- Suggested follow-up scope: continue applying current selector-context truth guidance to canonical routes where local selector dimensions can drift away from the visible primary or enrichment slices.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed selector-period issue
- priority order applied: current `symbol + period` selector truth > current period primary snapshot truth > no cross-period indicator leakage
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
  - `web/frontend/src/views/market/marketKlineData.ts`
- shared-impact review items:
  - `buildMarketKlineParams` direct callers stayed limited to `/market/technical` and `/detail/graphics`
- fixes applied:
  - `detail-graphics-issue-08`
- deferred items: none

## Fix Summary
- Updated the route-owned K-line analysis page so verified K-line and indicator slices are now tracked per `symbol + period` scope key.
- Updated the K-line request helper so the selected period is sent explicitly instead of being hard-coded.
- Ensured a new period first-load failure clears the previous period trend snapshot, request provenance, and indicator workspace.
- Added owner regressions, helper node coverage, and a new Phase 1 routed selector-switch assertion.
- Reused existing `myweb-audit v1.71` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-08-repair-approval.yaml`
- Approved issue ids:
  - `detail-graphics-issue-08`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-08`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` -> passed `8/8`
  - `node --test web/frontend/src/views/market/__node_tests__/marketKlineData.test.ts` -> passed `4/4`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `42` tests including the new detail/graphics period-switch assertion
  - targeted system-Chrome browser verification confirmed:
    - the natural PM2 route still loaded at `/detail/graphics/600519`
    - the same page instance updated `.module-meta` from `PERIOD: 1d` to `PERIOD: 1w` after the selector switch
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - the PM2 `/detail/graphics` request path on this machine again remained outside browser-network interception during live verification, so controlled period-failure proof stayed in the owner regressions plus routed matrix assertion rather than a browser-fulfilled failure harness
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
