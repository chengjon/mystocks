# Batch Audit Report: market-batch-02

## Scope
- Module: market
- Pages:
  - /market/lhb
- Batch rationale: close the routed LHB numeric-truth cluster so the canonical leaderboard page no longer leaks shared exact-decimal formatting onto count-only KPI cards or ordinal rank cells

## Agent Summary

### route-inventory
- `/market/lhb` continues to resolve directly to canonical `web/frontend/src/views/market/LHB.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity routed numeric-truth cluster remained: the page mixed a count-only shared stat card with a shared leaderboard table, so both the KPI strip and the `rank` column misrepresented route truth on the same primary surface.

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
- Repeated issue pattern: routed leaderboard workbenches that mix shared stat cards with shared tables often leak exact-decimal precision onto both count-only summary cards and ordinal rank fields.
- Occurrence basis:
  - `/market/lhb` previously rendered the top tally as `44.00`
  - the same route previously rendered rank values as `1.00 / 2.00 / 3.00`
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
  - `web/frontend/src/components/artdeco/trading/ArtDecoTable.vue`
- Suggested follow-up scope: continue using the existing `v1.32 + v1.36` rules on remaining leaderboard and tally routes rather than adding a new skill version for this batch.

## Main Skill Decisions
- duplicates merged: `2` raw findings into `1` numeric-truth cluster issue
- priority order applied: routed live truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/market/LHB.vue`
- shared-impact review items:
  - `ArtDecoStatCard.vue` and `ArtDecoTable.vue` remained observation-only candidates; the approved repair stayed page-local
- fixes applied:
  - `market-lhb-issue-02`
- deferred items: none

## Fix Summary
- Converted the count-only LHB tally card to an explicit plain string.
- Added a page-local formatter for the discrete leaderboard `rank` field.
- Added a routed component regression that mounts the real `ArtDecoStatCard` and `ArtDecoTable` path.
- Strengthened the Phase 1 matrix assertion for honest count and ordinal rendering on `/market/lhb`.
- Reused the existing `v1.32 + v1.36` rules instead of introducing a new `myweb-audit` version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-02-repair-approval.yaml`
- Approved issue ids:
  - `market-lhb-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - `ArtDecoStatCard.vue`
  - `ArtDecoTable.vue`

## Unresolved Items
- No approved repair remains unimplemented in `market-batch-02`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/market/__tests__/LHB.spec.ts` -> passed `2/2`
  - `node --test web/frontend/src/views/market/__node_tests__/dragonTigerData.test.ts` -> passed `4/4`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `10` structurally valid tests including the strengthened `/market/lhb` numeric-truth assertion
  - `git diff --check -- web/frontend/src/views/market/LHB.vue web/frontend/src/views/market/__tests__/LHB.spec.ts web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts` -> passed
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
  - targeted system-Chrome browser verification confirmed:
    - `/market/lhb` now renders top KPI values `44 / 今日 / 买入榜 / 74.41%`
    - the same route now has `0` `.artdeco-stat-change` nodes
    - the same route no longer shows `44.00`, `1.00`, or `2.00` on the affected surfaces
    - live PM2 requests still reached `/api/health/ready`, `/api/health`, and `/api/v2/market/lhb?limit=100` with `200`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue the market family on adjacent routed numeric surfaces or alternate date/filter branches, but reuse the existing numeric-truth rules rather than spinning a new skill version unless a genuinely new failure mode appears.
