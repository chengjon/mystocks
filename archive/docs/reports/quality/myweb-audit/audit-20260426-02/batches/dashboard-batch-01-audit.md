# Batch Audit Report: dashboard-batch-01

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: apply the new `v1.40` aggregate-provenance and resolved-error-envelope truth rules, together with the existing `v1.39` browser-context interception rule, so the canonical dashboard route stops hardcoding optimistic `REAL / READY` meta and preserves partial-failure truth from core-slice `success: false` envelopes

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- Route-level aggregate truth is owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`, while core-slice transport normalization lives in `web/frontend/src/api/services/dashboardService.ts`.

### functional-audit
- No separate interaction-path defect required an independent repair wave once the dashboard aggregate provenance state machine was restored.

### data-state-audit
- One high-severity route-truth defect remained: the dashboard request-meta bar and core-slice error handling did not faithfully represent the combined state of quotes, fund-flow, and industry.
- Before repair, resolved transport failures could collapse into empty-success rendering, hiding partial dashboard degradation behind optimistic aggregate meta.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a multi-request routed dashboard can keep optimistic aggregate header semantics even after one primary slice has failed if the route treats `success: false` envelopes as ordinary values instead of explicit failure truth.
- Occurrence basis:
  - `/dashboard` previously hardcoded optimistic top-level provenance while core slices were still pending or partially failed
  - the same route-local service plus state-owner pair previously swallowed fund-flow and industry failure envelopes into empty-success rendering
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - `web/frontend/src/api/services/dashboardService.ts`
- Suggested follow-up scope: continue applying `v1.40` to other canonical routed dashboards or workbenches that expose aggregate route provenance and depend on transport layers that normalize HTTP failures into resolved error envelopes.

## Main Skill Decisions
- duplicates merged: yes; hardcoded aggregate header truth and swallowed error-envelope truth were merged into one dashboard provenance issue because they distorted the same route-level state machine
- priority order applied: aggregate provenance truth > transport-envelope truth > cosmetic dashboard cleanup
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- shared-impact review items: none
- fixes applied:
  - `dashboard-aggregate-provenance-issue-01`
- deferred items:
  - natural PM2 dashboard success-path verification remains deferred as environment evidence because live AkShare fund-flow endpoints currently return `401` and redirect the route to `/login`

## Fix Summary
- Replaced hardcoded dashboard request-meta semantics with aggregate route state derived from the primary core slices.
- Restored failure semantics for core dashboard `success: false` transport envelopes in the dashboard service.
- Added a mock-compatible dashboard response guard so unit transport doubles cannot be more permissive than the real runtime contract.
- Strengthened routed dashboard unit and phase1 matrix coverage around pending, success, and degraded aggregate provenance.
- Introduced `myweb-audit v1.40` aggregate-provenance and resolved-error-envelope truth guidance.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-01-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-aggregate-provenance-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - widening the repair into shared global transport wrappers remains deferred because the current blast radius is larger than needed for this dashboard-family fix

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-01`.

## Reasons Not Fixed
- Natural PM2 `/dashboard` success-state verification was not used as route-success proof because the live environment currently redirects the route to `/login` after repeated `401` responses from AkShare fund-flow endpoints. This is recorded as environment evidence rather than a dashboard-family functional regression.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used to isolate pending, success, and partial-failure aggregate provenance states
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `8/8`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `14` structurally valid tests including the strengthened dashboard pending and industry-failure assertions
  - targeted routed-page verification confirmed:
    - browser-context pending verification rendered `DATA: PENDING`, `SYNC: PENDING`, and no route alerts while the first core dashboard slices were intentionally hung
    - browser-context success verification rendered `DATA: REAL`, `SYNC: READY`, and no route alerts when quotes, fund-flow, and industry all resolved successfully
    - browser-context industry-failure verification rendered `DATA: MIXED`, `SYNC: DEGRADED`, and `行业热度数据暂不可用`
    - browser-context fund-flow-failure verification rendered `DATA: MIXED`, `SYNC: DEGRADED`, and `资金流向数据暂不可用`
    - natural PM2 observation confirmed `/dashboard` currently redirects to `/login` after repeated `401` responses from live `/api/akshare/market/fund-flow/hsgt-summary` and `/api/akshare/market/fund-flow/big-deal`, so the route's success proof must remain browser-context controlled in this environment
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser paths
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 77`, `changed_count: 260`, `affected_count: 0`)

## Next Batch Plan
- Continue applying `v1.40` to other canonical routed dashboards or workbenches that aggregate multiple primary slices and still risk optimistic all-green header semantics or swallowed `success: false` envelope truth.
