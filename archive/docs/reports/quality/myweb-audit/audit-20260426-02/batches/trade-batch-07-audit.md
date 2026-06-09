# Batch Audit Report: trade-batch-07

## Scope
- Module: trade
- Pages:
  - /trade/signals
- Batch rationale: reuse the existing `v1.40` route-provenance rule and upgrade the audit method to `v1.41` so the canonical trade-signals route no longer collapses store-backed resolved `success: false` envelopes or unresolved first-load counts into faux REAL or EMPTY signal truth

## Agent Summary

### route-inventory
- `/trade/signals` remains the canonical routed signal workbench at `web/frontend/src/views/trade/Signals.vue`.
- The route is also reused by `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`, so page-local repairs must remain compatible with that wrapper surface.

### functional-audit
- No new routed interaction-path defect required a separate repair wave beyond restoring truthful first-load provenance on the canonical route owner.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the store-backed route collapsed unresolved first-load signal state into `COUNT: 0 / DATA: REAL`, and collapsed a resolved `success: false` signal envelope into `COUNT: 0 / DATA: EMPTY`, making the route look like verified real or verified empty signal truth before any verified snapshot existed.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: store-backed routed pages can receive resolved `success: false` envelopes as ordinary values and then silently map them into empty arrays, zero counts, or optimistic top-level provenance unless the page-local owner explicitly reclassifies the envelope as failure truth.
- Occurrence basis:
  - `/trade/signals` previously rendered `COUNT: 0 / DATA: REAL` while the first signal payload was still unresolved
  - the same route previously rendered `COUNT: 0 / DATA: EMPTY` when the first request resolved as `success: false` through the real transport interceptor
  - the original unit mock only modeled rejected-promise failures, so browser red evidence escaped the first test pass
- Shared component or token involved:
  - `web/frontend/src/views/trade/Signals.vue`
  - `web/frontend/src/stores/storeFactory.ts`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`
- Suggested follow-up scope: apply `v1.41` to other canonical store-backed routes whose route owners consume refresh results directly and may still treat resolved failure envelopes as empty-success data.

## Main Skill Decisions
- duplicates merged: yes; unresolved first-load and resolved-envelope failure were merged into one store-backed route-truth issue because they distorted the same canonical signal surface
- priority order applied: resolved-envelope failure truth > first-load route provenance > count-surface placeholder honesty
- primary owners selected:
  - `web/frontend/src/views/trade/Signals.vue`
- shared-impact review items:
  - `storeFactory.ts` remains observation-only for this batch because the current repair scope stayed page-local
- fixes applied:
  - `trade-signals-issue-03`
- deferred items:
  - shared store-factory redesign remains deferred because the current batch only needed one canonical route repair plus tighter verification logic

## Fix Summary
- Added page-local first-load placeholder gating for hero `COUNT`, route `DATA`, `REQ_ID`, `TIME`, top KPI counts, and content-shell `VISIBLE`.
- Added a page-local resolved-envelope failure guard so `success: false` signal payloads are reclassified as failure truth before row mapping.
- Tightened routed component regression to model resolved-envelope failures instead of reject-only failures.
- Strengthened the Phase 3 matrix with pending and unavailable `/trade/signals` route assertions.
- Upgraded `myweb-audit` to `v1.41` so future store-backed routed pages must verify resolved `success: false` transport behavior, not only thrown failures.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-07-repair-approval.yaml`
- Approved issue ids:
  - `trade-signals-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - `web/frontend/src/stores/storeFactory.ts`

## Unresolved Items
- No approved repair remains unimplemented in `trade-batch-07`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used to isolate unresolved, resolved-envelope failure, and verified-success signal states
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts` -> passed `8/8`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `26` structurally valid tests including the strengthened `/trade/signals` pending and unavailable provenance assertions
  - targeted routed-page verification confirmed:
    - the browser-context unresolved-first-load route rendered `COUNT: --`, `DATA: PENDING`, `REQ_ID: N/A`, `TIME: N/A`, `VISIBLE: --`, and top-strip `-- / -- / -- / --`
    - the browser-context resolved-envelope failure route rendered `COUNT: --`, `DATA: UNAVAILABLE`, `REQ_ID: N/A`, `TIME: N/A`, `VISIBLE: --`, and `trade signals unavailable`
    - the browser-context success route rendered `COUNT: 3`, `DATA: REAL`, `REQ_ID: REQ-TRADE-SIGNALS-LIVE`, `TIME: 42.00MS`, `VISIBLE: 3`, and live rows such as `贵州茅台`
    - all three browser-context paths had `0` `.artdeco-stat-change` nodes on the KPI strip
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 77`, `changed_count: 260`, `affected_count: 0`)

## Next Batch Plan
- Apply `v1.41` to the next canonical store-backed route whose owner consumes refresh results directly, prioritizing pages that still mix first-load count surfaces with route-level `DATA` or `REQ` meta and may receive resolved `success: false` envelopes from shared transport wrappers.
