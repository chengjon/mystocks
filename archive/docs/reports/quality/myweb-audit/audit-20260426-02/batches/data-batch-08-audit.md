# Batch Audit Report: data-batch-08

## Scope
- Module: data
- Pages:
  - /data/fund-flow
- Batch rationale: close the routed fund-flow numeric-truth cluster so the canonical page no longer leaks zero-initialized first-load KPI cards or ordinal pseudo decimals, and fold the unresolved first-load numeric truth rule back into `myweb-audit v1.38`

## Agent Summary

### route-inventory
- `/data/fund-flow` continues to resolve directly to canonical `web/frontend/src/views/data/FundFlow.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity routed numeric-truth cluster remained: the page mixed unresolved first-load shared stat cards with a shared ranking table, so both the KPI strip and the `rank` column misrepresented route truth on the same primary surface.

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
- Repeated issue pattern: shared numeric renderers can leak in two phases on the same route, first as unresolved loading-state zero metrics and then as ordinal pseudo decimals on the resolved table surface.
- Occurrence basis:
  - `/data/fund-flow` previously rendered top loading-state KPI cards as `0.00 / +0%`
  - the same route previously rendered ranking rows as `1.00 / 2.00`
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
  - `web/frontend/src/components/artdeco/trading/ArtDecoTable.vue`
- Suggested follow-up scope: apply `v1.36 + v1.37 + v1.38` to remaining canonical numeric routes such as `/market/lhb`.

## Main Skill Decisions
- duplicates merged: `2` raw findings into `1` numeric-coherence cluster issue
- priority order applied: routed live truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/data/FundFlow.vue`
- shared-impact review items:
  - `ArtDecoStatCard.vue` and `ArtDecoTable.vue` remained observation-only candidates; the approved repair stayed page-local
- fixes applied:
  - `data-fund-flow-issue-01`
- deferred items: none

## Fix Summary
- Converted the unresolved first-load fund-flow KPI strip to explicit placeholders with `show-change=false`.
- Added a page-local formatter for the discrete ranking `rank` field.
- Added a routed component regression that mounts the real `ArtDecoStatCard` and `ArtDecoTable` path.
- Strengthened the Phase 2 matrix assertion for honest ordinal rendering on the ranking table.
- Upgraded `myweb-audit` to `v1.38` so future audits treat zero-initialized first-load numeric surfaces as explicit route-truth defects.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-08-repair-approval.yaml`
- Approved issue ids:
  - `data-fund-flow-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - `ArtDecoStatCard.vue`
  - `ArtDecoTable.vue`

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-08`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/data/__tests__/FundFlow.spec.ts tests/unit/views/data-fund-flow-partial-state.spec.ts` -> passed `3/3`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `13` structurally valid tests including the strengthened `/data/fund-flow` rank assertion
  - `git diff --check -- web/frontend/src/views/data/FundFlow.vue web/frontend/src/views/data/__tests__/FundFlow.spec.ts web/frontend/tests/unit/views/data-fund-flow-partial-state.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md .claude/skills/myweb-audit/references/CHANGELOG.md` -> passed
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
  - targeted system-Chrome browser verification against the real PM2 route confirmed:
    - `/data/fund-flow` now renders unresolved KPI placeholders as `-- / -- / -- / --`
    - the same route now has `0` `.artdeco-stat-change` nodes on the top strip while unresolved
    - the route no longer shows `+0%` or `0.00` on the affected loading-state KPI surface
    - live PM2 requests still reached `/api/health/ready`, `/api/health`, and `/api/akshare/market/fund-flow/hsgt-summary?...` with `200`
    - the resolved ranking-table ordinal proof remained covered by routed regression because the live PM2 route did not complete the ranking-table surface within the verification window
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
- Apply the strengthened `v1.36 + v1.37 + v1.38` numeric-surface rules to remaining canonical rank-table and KPI routes, prioritizing `/market/lhb`.
