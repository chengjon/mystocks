# Batch Audit Report: detail-batch-07

## Scope
- Module: detail
- Pages:
  - /detail/graphics/:symbol
- Batch rationale: close the canonical `/detail/graphics/:symbol` selector-scoped snapshot truth gap so a new failing detail symbol cannot inherit the previous verified K-line or indicator slices, reusing existing `myweb-audit v1.66`.

## Agent Summary

### route-inventory
- `/detail/graphics/:symbol` remains the canonical routed graphics detail page at `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: the primary K-line and indicator enrichment slices were not selector-scoped, so a new detail symbol could inherit the previous verified symbol snapshot under the same routed page instance.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped canonical detail routes must treat the current route selector as part of primary snapshot provenance, not just header copy.
- Occurrence basis:
  - `/detail/graphics/:symbol` could let `/detail/graphics/000001` inherit the verified `600519` K-line or indicators when the first `000001` slice failed before its own verified snapshot existed
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.66` to selector-driven detail pages where the route selector and the visible primary or enrichment slices can drift apart.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed selector-snapshot issue
- priority order applied: current route selector truth > current symbol primary snapshot truth > enrichment retention only for the same verified selector
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-graphics-issue-07`
- deferred items: none

## Fix Summary
- Updated the route-owned K-line analysis page so verified K-line and indicator slices are now tracked per detail symbol.
- Ensured a new symbol first-load failure clears the previous symbol trend snapshot instead of leaking the old request provenance and point count.
- Ensured a new symbol enrichment failure keeps only the new symbol K-line snapshot and clears the previous symbol indicators.
- Added owner regressions plus two Phase 1 routed selector-switch assertions.
- Reused existing `myweb-audit v1.66` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-07-repair-approval.yaml`
- Approved issue ids:
  - `detail-graphics-issue-07`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-07`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` -> passed `7/7`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `41` tests including the new detail/graphics selector-switch assertions
  - targeted system-Chrome browser verification confirmed:
    - the same page instance moved from `/detail/graphics/600519` to `/detail/graphics/000001`
    - `.module-meta` updated to `SYMBOL: 000001` with a new request id instead of retaining the old `600519` header
    - `.indicators-card` remained in current-symbol unavailable state and did not render the previous symbol indicators after the route switch
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - the PM2 `/detail/graphics` request path on this machine remained outside browser-network interception during live verification, so controlled failure proof stayed in the owner regressions plus routed matrix assertions rather than a browser-fulfilled failure harness
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
