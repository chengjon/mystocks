# Batch Audit Report: secondary-batch-25

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) trading-decision/DecisionPortfolio.vue`
  - `(unrouted) trading-decision/DecisionPositions.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing two active trading-decision panels into thin wrappers over the existing canonical `/trade/*` owners instead of preserving local pseudo-live portfolio and positions shells

## Agent Summary

### route-inventory
- Both trading-decision panels stayed in the high-priority secondary backlog because they still matched selector/fallback heuristics and remained directly imported by the live `TradingDecisionCenter.vue` shell.
- Unlike orphan legacy pages, these panels sit on an active import chain, so they needed immediate repair instead of defer-to-retire triage.

### data-state-audit
- `DecisionPortfolio.vue` still rendered local total-assets, available-cash, position-value, total-profit, and profit-rate cards plus local quick actions instead of delegating to the canonical `/trade/portfolio` owner.
- `DecisionPositions.vue` still rendered a local refresh button, position-card grid wiring, and empty-state shell instead of delegating to the canonical `/trade/positions` owner.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: canonical-owner delegation > live-parent import-chain repair > no new secondary truth source
- primary owners selected:
  - `web/frontend/src/views/trading-decision/DecisionPortfolio.vue`
  - `web/frontend/src/views/trading-decision/DecisionPositions.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-25`
- deferred items:
  - `DecisionOrders.vue` stays out of scope because no semantically matching canonical `/trade/orders` owner currently exists

## Fix Summary
- Replaced `DecisionPortfolio.vue` with a thin wrapper over the canonical `/trade/portfolio` owner.
- Replaced `DecisionPositions.vue` with a thin wrapper over the canonical `/trade/positions` owner via the current route entrypoint.
- Recorded the reusable precedent that active sibling panels inside a live parent shell should be split by owner match: delegate the panels with clean canonical owners now, and leave unmatched siblings for later static-shell or owner-mapping decisions.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because both repaired owners are unrouted embedded secondary panels inside a live parent shell
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/trading-decision/__tests__/DecisionPortfolio.spec.ts src/views/trading-decision/__tests__/DecisionPositions.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Center.spec.ts` -> passed (`12/12`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory remains `275` total view files, `40` routed, `235` unrouted, `H=37 / M=103 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-25` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-25-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/trading-decision/DecisionPortfolio.vue web/frontend/src/views/trading-decision/DecisionPositions.vue web/frontend/src/views/trading-decision/__tests__/DecisionPortfolio.spec.ts web/frontend/src/views/trading-decision/__tests__/DecisionPositions.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/route-truth-operations.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-25-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-25-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-25-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-active-panel-canonical-wrapper-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-25-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-25-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because the repair targets unrouted secondary panels with no independent routed proof surface in the current router graph.
