# Batch Audit Report: data-batch-12

## Scope
- Module: data
- Pages:
  - /data/fund-flow
- Batch rationale: reuse the existing `v1.38 + v1.40` rules so the canonical fund-flow route no longer collapses first-load pending or failed ranking-meta states into faux zero-row and leaked request-id truth.

## Agent Summary

### route-inventory
- `/data/fund-flow` continues to resolve directly to canonical `web/frontend/src/views/data/FundFlow.vue`.
- The owner route is still reused by `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue`, so the current repair keeps wrapper consumers aligned without widening into shared layers.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the fund-flow route treated unresolved and failed first-load ranking states as if they were verified empty loads, surfacing `ROWS: 0` and a leaked failed request id before any verified ranking snapshot existed.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed workbench can already have honest first-load summary cards yet still leak verified-empty semantics through top-level row metadata if hero `ROWS / REQ` surfaces are not gated on the same verified-snapshot boundary.
- Occurrence basis:
  - `/data/fund-flow` previously rendered `ROWS: 0` while the first summary payload was still unresolved
  - the same route previously rendered `ROWS: 0` plus a failed request id when the first summary and ranking requests both failed before any verified snapshot existed
- Shared component or token involved:
  - `web/frontend/src/views/data/FundFlow.vue`
  - `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue`
- Suggested follow-up scope: continue applying the existing first-load numeric and route-provenance rules to canonical routes that still mix hero row/count metadata with unverified first-load shells.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: first-load route provenance > row-meta placeholder honesty
- primary owners selected:
  - `web/frontend/src/views/data/FundFlow.vue`
- shared-impact review items:
  - `FundFlowAnalysis.vue` was reviewed as a route-family consumer but did not require a separate fix
- fixes applied:
  - `data-fund-flow-issue-02`
- deferred items:
  - no new shared-layer redesign was approved for this batch

## Fix Summary
- Added page-local first-load placeholder gating for hero `ROWS` and `REQ` metadata.
- Reused the same row-meta placeholder on the ranking-summary sentence so success-only row counts stay aligned with the hero surface.
- Extended routed component regression to cover both unresolved and first-load failure fund-flow states.
- Strengthened the Phase 2 matrix with pending and failed `/data/fund-flow` hero-row assertions.
- Reused existing `myweb-audit` rules instead of creating a new skill-version branch.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-12-repair-approval.yaml`
- Approved issue ids:
  - `data-fund-flow-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-12`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - authenticated browser contexts plus readiness stubs and browser-context interception with `serviceWorkers: block` were used to isolate pending, unavailable, and verified-success fund-flow states
- Regression checks completed:
  - `npx vitest run src/views/data/__tests__/FundFlow.spec.ts tests/unit/views/data-fund-flow-partial-state.spec.ts` -> passed `5/5`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `17` structurally valid tests including the strengthened `/data/fund-flow` pending and failed first-load assertions
  - targeted routed-page verification confirmed:
    - the browser-context unresolved-first-load route rendered `ROWS: --`, `REQ: N/A`, summary values `-- / -- / -- / --`, and `资金流向同步中`
    - the browser-context first-load failure route rendered `ROWS: --`, `REQ: N/A`, placeholder summary values, and `资金流向加载失败`
    - the browser-context success route rendered `ROWS: 2`, `REQ: REQ-FUND-FLOW-RANKING`, and ranking summary `当前按主力流入额重排 2 条排行，趋势窗口为今日。`
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
  - because the natural PM2 route passes through readiness and login shells in this environment, route proof for this batch used authenticated browser contexts and ready/healthy stubs before interception was applied
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 77`, `changed_count: 260`, `affected_count: 0`)

## Next Batch Plan
- Apply the existing first-load numeric and route-provenance rules to the next canonical page that still mixes top-level row/count metadata with unverified first-load shells.
