# Batch Audit Report: risk-batch-07

## Scope
- Module: risk
- Pages:
  - /risk/overview
- Batch rationale: apply the strengthened `v1.36` ordinal-precision truth rule so the canonical risk-overview rules tab stops rendering live integer priorities as faux decimal metrics

## Agent Summary

### route-inventory
- `/risk/overview` continues to resolve directly to canonical `web/frontend/src/views/risk/Overview.vue`.

### data-state-audit
- The live alert-rules contract exposed discrete integer priorities, but the routed rules tab rendered those values through shared exact-decimal table formatting as if they were fractional metrics.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed table can correctly load live data while still misrepresenting discrete policy fields if it delegates those values to a shared exact-decimal formatter intended for continuous metrics.
- Occurrence basis:
  - `/risk/overview` previously loaded real alert rules but rendered their `priority` values as `4.00`, `3.00`, and `2.00`
  - the same route semantically uses `priority` as rule ordering, not as a fractional metric
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/trading/ArtDecoTable.vue` provides the generic two-decimal numeric formatter, but the approved repair stayed page-local because changing shared defaults would have broader risk
- Suggested follow-up scope: continue applying `v1.36` to other canonical routed tables that surface discrete priority, rank, step, or sequence fields through shared numeric formatters.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: live ordinal truth > shared-default containment > cosmetic cleanup
- primary owners selected:
  - `web/frontend/src/views/risk/Overview.vue`
- shared-impact review items:
  - `ArtDecoTable.vue` default exact-decimal numeric formatting observed but not changed in this batch
- fixes applied:
  - `risk-overview-issue-04`
- deferred items: none

## Fix Summary
- Added a page-local `priority` formatter on the canonical risk-overview rules table so live alert-rule priorities render as ordinal integers instead of inheriting shared two-decimal formatting.
- Updated the routed component regression to mount the real `ArtDecoTable` path and fail if `1.00` leaks back into the priority column.
- Strengthened the phase4 structural route assertion and verified the real PM2 route with Playwright-library plus system `google-chrome`.
- Upgraded `myweb-audit` to `v1.36` so future audits explicitly catch ordinal fields that inherit fabricated fixed-decimal precision from shared formatters.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-07-repair-approval.yaml`
- Approved issue ids:
  - `risk-overview-issue-04`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-07`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/StopLoss.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `11/11`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `12` structurally valid tests including the strengthened risk-overview rules-tab assertion
  - targeted routed-page verification confirmed:
    - the real PM2 `/risk/overview` route issued `200` responses for `/api/health/ready`, `/api/health`, `/api/v1/monitoring/alert-rules`, and `/api/v1/monitoring/alerts?page=1&page_size=50`
    - the same route now renders live rules such as `龙虎榜上榜`
    - the `优先级` column now shows `4`, `3`, and `2` rather than `4.00`, `3.00`, and `2.00`
    - the rules tab no longer leaks fabricated exact-decimal precision onto this discrete policy field
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.36` to remaining canonical routed tables, prioritizing pages that render discrete priority, rank, step, or sequence fields through shared numeric formatters.
