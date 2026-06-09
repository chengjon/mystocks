# Batch Audit Report: risk-batch-13

## Scope
- Module: risk
- Pages:
  - /risk/management
- Batch rationale: close the canonical `/risk/management` summary-delta truth gap so holdings-derived totals no longer relabel aggregate PnL ratio or zero placeholders as per-card `%` change semantics

## Agent Summary

### route-inventory
- `/risk/management` remains the canonical routed risk-management workspace at `web/frontend/src/views/risk/Center.vue`.
- The visible stats-grid surface is owned by the shared risk-management family under `web/frontend/src/views/artdeco-pages/risk-tabs/`.

### functional-audit
- No new routed interaction-path defect required a separate repair wave beyond honest stats-grid summary semantics on the default overview tab.

### data-state-audit
- One high-severity routed summary-delta defect remained: the page reused aggregate PnL ratio as if it were verified per-card change truth for unrelated `总资产` and `今日收益` cards.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: holdings-backed routed pages may truthfully show absolute totals while still leaking faux secondary delta semantics if shared summary grids reuse aggregate PnL ratio or zero placeholders as card-level `%` change copy.
- Occurrence basis:
  - `/risk/management` positions contract proves `total_market_value`, `total_profit_loss`, and `total_profit_loss_percent`
  - `toRiskManagementMetrics()` reused that aggregate ratio for both `总资产` and `今日收益` secondary delta rows
  - `ArtDecoRiskStatsGrid.vue` then rendered those fields as if they were verified card-specific change baselines
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStatsGrid.vue`
- Suggested follow-up scope: continue applying `v1.49 + v1.32 + v1.23` checks to holdings/exposure routes that still show secondary change rows beneath absolute total cards.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed summary-delta truth issue
- priority order applied: live summary truth > shared risk-family containment > routed verification hardening
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue` inherits the shared stats-grid repair and did not require a separate owner patch
- fixes applied:
  - `risk-management-issue-13`
- deferred items: none

## Fix Summary
- Changed the shared risk-management metrics contract so unsupported summary-delta fields can remain unresolved instead of defaulting to faux numeric truth.
- Changed the shared stats-grid surface to degrade `总资产` and `今日收益` secondary delta rows to `待接入` when no dedicated live comparison-baseline field exists.
- Added node-level and owner-component regressions that pin the same mapper/grid truth.
- Added a Phase 4 routed assertion that guards the same stats-grid truth on `/risk/management`.
- Promoted `myweb-audit v1.49` so future holdings/exposure routes explicitly reject faux summary-delta semantics.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-13-repair-approval.yaml`
- Approved issue ids:
  - `risk-management-issue-13`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-13`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `node --test web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementData.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementHelpers.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementModulePresence.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/stopLossMonitorData.test.ts` -> passed `17/17`
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Alerts.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStockPanel.spec.ts` -> passed `35/35`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `27` structurally valid tests including the strengthened `/risk/management` stats-grid assertion
  - targeted system-Chrome browser verification confirmed:
    - natural PM2 `/risk/management` now renders `总资产 / ¥0 / 待接入` and `今日收益 / +¥0 / 待接入`
    - the same natural route no longer shows `+0%`
    - a controlled holdings payload with `total_profit_loss_percent: 1.84` now renders `总资产 / ¥372,664 / 待接入` and `今日收益 / +¥6,844 / 待接入`
    - the same controlled proof no longer shows `+1.84%`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-13-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-13-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-13-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-13-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-13-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementHelpers.ts web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStatsGrid.vue web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementData.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/CHANGELOG.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-13-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-13-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-13-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-13-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-management-summary-delta-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-13-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` returned `risk_level: low`, `changed_files: 126`, `changed_count: 317`, and `affected_count: 0`

## Next Batch Plan
- Continue applying `v1.49 + v1.48 + v1.43` to remaining holdings/exposure routes and freshness-bearing surfaces that still synthesize unsupported secondary semantics from aggregate payload fields.
