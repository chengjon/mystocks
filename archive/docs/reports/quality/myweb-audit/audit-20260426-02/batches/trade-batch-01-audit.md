# Batch Audit Report: trade-batch-01

## Scope
- Module: trade
- Pages:
  - /trade/portfolio
  - /risk/pnl
- Batch rationale: close the routed portfolio policy-truth gap so live holdings data cannot fabricate rebalance targets or action amounts on either the canonical trade route or the risk wrapper route when target-weight inputs are absent

## Agent Summary

### route-inventory
- `/trade/portfolio` remains the canonical routed portfolio workbench at `src/views/trade/Portfolio.vue`.
- `/risk/pnl` remains a thin routed wrapper at `src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`.
- Both routes reuse the same canonical portfolio page family, so policy-truth drift must be treated as a shared routed-surface issue rather than two independent bugs.

### functional-audit
- No new routed interaction defect required a repair wave beyond restoring truthful rebalance-policy behavior.

### data-state-audit
- One medium-severity policy-derived action truth defect remained: the canonical portfolio page generated equal-weight rebalance targets and amount advice from holdings-only payloads that did not expose any real `target_weight` or portfolio-constraint inputs.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed holdings page can accidentally escalate descriptive live holdings data into fabricated strategy advice when a secondary panel assumes policy inputs that the current payload never actually returned.
- Occurrence basis:
  - `/trade/portfolio` previously fetched real `/api/v1/trade/positions` data but still showed equal-weight rebalance targets such as `目标 25%`
  - `/risk/pnl` inherited the same synthetic advice because it is a thin wrapper over the canonical trade portfolio page
- Shared component or token involved:
  - `web/frontend/src/views/trade/Portfolio.vue`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- Suggested follow-up scope: extend future routed portfolio, risk, and strategy audits to verify that action-oriented policy surfaces never borrow credibility from nearby live holdings data when target weights or constraints are absent.

## Main Skill Decisions
- duplicates merged: yes; the trade-route and risk-wrapper symptoms were merged into one canonical policy-truth issue
- priority order applied: policy-derived action truth > cosmetic rebalance copy cleanup
- primary owners selected:
  - `web/frontend/src/views/trade/Portfolio.vue`
- shared-impact review items:
  - `trade-portfolio-issue-01`
- fixes applied:
  - `trade-portfolio-issue-01`
- deferred items: none

## Fix Summary
- Extended the shared portfolio mapper so routed portfolio data now carries `target_weight` and an explicit `rebalance_policy_ready` flag.
- Reworked the canonical trade portfolio page so rebalance counts and rows only render when real target-weight inputs are present.
- Degraded both `/trade/portfolio` and `/risk/pnl` to `待接入` plus explicit pending-policy copy when the live positions payload lacks policy inputs.
- Updated unit, route-family, and wrapper-route regression coverage to encode the new policy-derived action truth behavior.
- Extended `myweb-audit` with a `v1.24` policy-derived action truth rule so future audits catch synthetic rebalance advice earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-01-repair-approval.yaml`
- Approved issue ids:
  - `trade-portfolio-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `trade-portfolio-issue-01`
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-01`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - route-level policy-truth verification blocked service workers and fulfilled `/api/v1/trade/positions` directly to isolate the rebalance surface
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts src/views/trade/__tests__/Portfolio.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts src/views/trade/__tests__/Portfolio.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts tests/unit/config/trade-route-canonical-paths.spec.ts` -> passed `14/14`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/risk-pnl.spec.ts tests/e2e/phase3-mainline-matrix.spec.ts tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `25` structurally valid tests including the strengthened portfolio and risk-pnl assertions
  - targeted routed-page verification confirmed:
    - `/trade/portfolio` issued the intercepted `http://localhost:3020/api/v1/trade/positions` request, showed `REBALANCE: 待接入`, displayed `贵州茅台` and `宁德时代`, and rendered `再平衡策略待接入，当前持仓数据未提供目标仓位或组合约束。`
    - `/risk/pnl` issued the same intercepted request and rendered the same pending-policy state
    - the fabricated advice strings `目标 25%` and `建议减仓约` are absent on both routes after repair
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser paths
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-01-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-01-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-01-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-01-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-01-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 130`, `changed_count: 409`, `affected_count: 0`)

## Next Batch Plan
- If the user continues the trade or adjacent risk audit, apply the strengthened policy-derived action truth rule to other routed holdings, allocation, or strategy-advice surfaces before trusting any recommendation math.
