# Batch Audit Report: data-batch-10

## Scope
- Module: data
- Pages:
  - /data/indicator
- Batch rationale: reuse the existing `v1.32 + v1.38` rules on the canonical data-indicator route so unverified summary surfaces stop leaking fake freshness metadata, zero-initialized tallies, and shared stat-card delta chrome.

## Agent Summary

### route-inventory
- `/data/indicator` remains the canonical routed analysis workspace at `web/frontend/src/views/data/Advanced.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond honest summary presentation on the selected route.

### data-state-audit
- One high-severity routed summary-truth cluster remained: the page mixed unverified freshness metadata and shared tally cards from default summary state, without distinguishing verified analysis summary from unresolved or failed first-load state.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: canonical analysis routes can leak fake route truth when header freshness metadata and count-only KPI cards are both driven by default local state before any verified summary exists.
- Occurrence basis:
  - `/data/indicator` previously rendered `UPDATED: <local current time>` and five `0.00 ● +0%` summary cards under unverified summary states
  - the same route also rendered verified tally cards through shared flat-change chrome and exact-decimal formatting
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue applying the existing `v1.32 + v1.38` rules to routed pages that combine freshness metadata with count-only summary cards.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed summary-state issue
- priority order applied: routed truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/data/Advanced.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained an observation-only candidate; the approved repair stayed page-local
- fixes applied:
  - `data-indicator-issue-01`
- deferred items: none

## Fix Summary
- Added page-local `showSummaryPlaceholders` gating to the canonical data-indicator route.
- Converted unverified header freshness and all five summary cards to explicit `--` placeholders.
- Converted verified tally cards to honest string values with `show-change=false`.
- Added a routed component regression for summary-state truth.
- Strengthened the Phase 2 matrix registry-failure assertion so the route cannot silently regress back to `0.00 / +0%`.
- Reused existing `myweb-audit v1.32 + v1.38` without a new skill-version bump because the defect matched the current count-kpi and unverified-summary rules exactly.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-10-repair-approval.yaml`
- Approved issue ids:
  - `data-indicator-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is higher than this micro-batch warrants

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-10`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/data/__tests__/Advanced.spec.ts tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-screening-truth.spec.ts tests/unit/views/data-advanced-cutover.spec.ts` -> passed `6/6`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `14` structurally valid tests including the strengthened `/data/indicator` failure assertion
  - targeted routed-page verification confirmed:
    - browser-context failure verification now shows `STATUS: 同步中` or `同步异常` with `UPDATED: --`, five `--` summary values, and zero `.artdeco-stat-change` nodes while no verified summary exists
    - browser-context success verification now shows verified tally strings `3 / 2 / 0 / 0 / 0` with zero `.artdeco-stat-change` nodes and no `+0%` or `x.00`
    - natural PM2 requests in this environment still reached `/api/health/ready` and `/api/health`, while `/api/v1/indicators/registry` and `/api/v1/data/stocks/basic` returned `401`, so verified-success route truth had to be confirmed via browser-context fulfillment instead of direct backend responses
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
- Continue applying the existing `v1.32 + v1.38 + v1.39` rules to canonical routes that mix freshness metadata, count-only KPI strips, and first-load unverified states.
