# Batch Audit Report: trade-batch-06

## Scope
- Module: trade
- Pages:
  - /trade/portfolio
  - /risk/pnl
- Batch rationale: reuse the existing `v1.32 + v1.38 + v1.39` rules so canonical portfolio summary surfaces distinguish verified empty holdings truth from unavailable or unresolved-first-load states, while the shared risk wrapper stays aligned with the repaired owner route

## Agent Summary

### route-inventory
- `/trade/portfolio` remains the canonical routed portfolio workbench at `web/frontend/src/views/trade/Portfolio.vue`.
- `/risk/pnl` remains a thin routed wrapper at `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`.
- Both routes reuse the same canonical owner page family, so first-load summary drift must be treated as one shared routed-surface issue rather than two independent bugs.

### functional-audit
- No new routed interaction-path defect required a separate repair wave beyond restoring honest first-load summary semantics on the canonical portfolio owner route.

### data-state-audit
- One high-severity summary-truth defect remained: before repair, the canonical portfolio owner reused default zero-valued totals, counts, and dependent empty-state branches even when the first positions payload was still unresolved or had failed, so the route looked like a verified zero-balance portfolio before any verified holdings snapshot existed.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed holdings page can accidentally collapse unresolved, unavailable, and verified-empty states into the same zero-valued summary surfaces when a default mapper payload is treated as real data before any verified snapshot exists.
- Occurrence basis:
  - `/trade/portfolio` previously showed zero-valued summary cards, hero totals, and real-empty copy before the first `/api/v1/trade/positions` response had been verified
  - `/risk/pnl` inherited the same false summary truth because it is a thin wrapper over the canonical portfolio owner
- Shared component or token involved:
  - `web/frontend/src/views/trade/Portfolio.vue`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue applying the existing first-load and count-kpi rules to other routed holdings or summary pages that still derive empty-state or zero-valued summary truth from unresolved payload defaults.

## Main Skill Decisions
- duplicates merged: yes; the canonical trade route and the risk wrapper symptoms were merged into one owner-route summary-truth issue
- priority order applied: first-load summary truth > cosmetic card cleanup
- primary owners selected:
  - `web/frontend/src/views/trade/Portfolio.vue`
- shared-impact review items:
  - `trade-portfolio-issue-02`
- fixes applied:
  - `trade-portfolio-issue-02`
- deferred items:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current batch only needed owner-route repairs

## Fix Summary
- Reworked the canonical portfolio owner so it tracks whether a verified holdings snapshot has ever resolved.
- Converted top summary cards, hero meta, and hero totals to placeholder-aware display values until a verified portfolio snapshot exists.
- Split positions, attribution, and rebalance panels into verified-empty, unavailable, and unresolved-first-load branches.
- Strengthened routed component regression and Phase 3 route-matrix assertions to guard against faux zero balances and false real-empty copy on the affected route family.
- Reused the existing `myweb-audit v1.32 + v1.38 + v1.39` rule set; no new skill-version branch was needed.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `trade-portfolio-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `trade-portfolio-issue-02`
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is wider than needed for this owner-route repair

## Unresolved Items
- No approved repair remains unimplemented in `trade-batch-06`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used to isolate unavailable and unresolved-first-load portfolio states
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/Portfolio.spec.ts` -> passed `3/3`
  - `npx vitest run src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `12/12`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `24` structurally valid tests including the strengthened portfolio success, failure, and hanging-first-load assertions
  - targeted routed-page verification confirmed:
    - the natural PM2 `/trade/portfolio` route issued `/api/v1/trade/positions`, rendered `REQ: 3e92c541-d31a-435a-801a-1424852036ac`, `POSITIONS: 0`, `REBALANCE: 待接入`, stat values `0.00 / +0 / 0 / 待接入`, and zero `.artdeco-stat-change` nodes when the backend returned a verified empty portfolio snapshot in this environment
    - the browser-context failure route rendered `POSITIONS: --`, `REBALANCE: --`, stat values `-- / -- / -- / --`, and `positions unavailable，当前暂无已验证组合快照。` instead of faux zero balances
    - the browser-context hanging-first-load route rendered `POSITIONS: --`, `REBALANCE: --`, stat values `-- / -- / -- / --`, and `组合资产同步中...` plus pending section copy instead of real-empty copy
    - the natural PM2 `/risk/pnl` wrapper route issued the same live positions request, rendered a distinct live `REQ` id, and preserved the same honest empty-state summary semantics with zero `.artdeco-stat-change` nodes
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
- Continue applying the existing first-load summary truth and count-kpi rules to remaining canonical routed holdings or summary pages that still collapse unresolved, unavailable, and verified-empty states into the same zero-valued surfaces.
