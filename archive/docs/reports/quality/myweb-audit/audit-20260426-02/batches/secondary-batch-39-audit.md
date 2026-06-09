# Batch Audit Report: secondary-batch-39

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) MarketData.vue`
  - `(unrouted) market/MarketDataView.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading two legacy market-data aggregate pages to honest static shells because no one-to-one verified aggregate market-data owner exists

## Agent Summary

### route-inventory
- `MarketData.vue` and `market/MarketDataView.vue` remained in the high-priority secondary backlog because they still matched selector-driven multi-tab aggregate shell heuristics before repair.
- Neither page has a current router entry, and their semantics span multiple canonical route families rather than one verified owner.

### data-state-audit
- `MarketData.vue` still mounted legacy fund-flow, ETF, chip-race, and LHB components from a local tab shell.
- `market/MarketDataView.vue` still mounted legacy market table components and added shell-local realtime badge, clock, and back action semantics.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: yes
- priority order applied: honest static shell > no aggregate market-data duplicate truth > no fake tabs/runtime chrome/component-local direct requests
- primary owners selected:
  - `web/frontend/src/views/MarketData.vue`
  - `web/frontend/src/views/market/MarketDataView.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-39`
- deferred items: none

## Fix Summary
- Replaced `MarketData.vue` with an honest static shell because no one-to-one verified aggregate market-data owner exists.
- Replaced `market/MarketDataView.vue` with an honest static shell because its nested aggregate semantics also lack a verified owner.
- Recorded the reusable precedent that legacy market-data aggregate pages should not keep multi-route tabs or component-local request surfaces when the canonical truth already lives in split `/market/*` and `/data/*` routes.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because both repaired owners are unrouted secondary pages with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/MarketData.spec.ts src/views/market/__tests__/MarketDataView.spec.ts` -> passed (`2/2`)
  - `cd web/frontend && npx vitest run src/views/__tests__/MarketData.spec.ts src/views/market/__tests__/*.spec.ts` -> passed (`19/19`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `275` total view files, `40` routed, `235` unrouted, `H=20 / M=120 / L=95`
- Runtime and repo gates:
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-39` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-39-manifest.yaml` -> passed
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/MarketData.vue web/frontend/src/views/market/MarketDataView.vue web/frontend/src/views/__tests__/MarketData.spec.ts web/frontend/src/views/market/__tests__/MarketDataView.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-39-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-39-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-39-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/market-data-legacy-aggregate-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-39-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-39-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`; shared dirty worktree, not an isolated verdict)
- No Playwright batch was added because the repair targets unrouted secondary pages with no independent routed proof surface.
