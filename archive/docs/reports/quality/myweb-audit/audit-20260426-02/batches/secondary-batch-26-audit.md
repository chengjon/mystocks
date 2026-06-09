# Batch Audit Report: secondary-batch-26

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) trading-decision/DecisionOrders.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the remaining active trading-decision orders panel to an honest static shell because no semantically matching canonical order owner exists

## Agent Summary

### route-inventory
- `DecisionOrders.vue` remained in the high-priority secondary backlog because it still matched selector/fallback heuristics and remained directly imported by the live `TradingDecisionCenter.vue` shell.
- Unlike `DecisionPortfolio.vue` and `DecisionPositions.vue`, this panel has no clean canonical `/trade/orders` or `/trade/execution` owner to delegate to.

### data-state-audit
- `DecisionOrders.vue` still rendered a local order-entry form, search flow, buy/sell actions, refresh button, and order-history table even though the current router graph has no semantically matching canonical owner for those semantics.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no fake live order-entry surface > no new secondary truth source
- primary owners selected:
  - `web/frontend/src/views/trading-decision/DecisionOrders.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-26`
- deferred items: none

## Fix Summary
- Replaced `DecisionOrders.vue` with an honest static shell because no semantically matching canonical order owner exists in the active router graph.
- Removed the local search form, submit actions, refresh button, and order-history table instead of force-mapping the panel to an unrelated `/trade/*` owner.
- Recorded the reusable precedent that a remaining unmatched sibling panel inside a live parent shell must degrade to a static shell after the owner-matched siblings are delegated away.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted embedded secondary panel inside a live parent shell
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/trading-decision/__tests__/DecisionOrders.spec.ts` -> passed (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory remains `275` total view files, `40` routed, `235` unrouted, `H=36 / M=104 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-26` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-26-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/trading-decision/DecisionOrders.vue web/frontend/src/views/trading-decision/__tests__/DecisionOrders.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-26-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-26-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-26-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-orders-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-26-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-26-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because the repair targets an unrouted secondary panel with no independent routed proof surface in the current router graph.
