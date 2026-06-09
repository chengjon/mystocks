# Batch Audit Report: secondary-batch-32

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) BacktestWizard.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the legacy backtest wizard to an honest static shell because no semantically matching canonical owner exists

## Agent Summary

### route-inventory
- `BacktestWizard.vue` remained in the high-priority secondary backlog because it still matched the stats-strip, selector, fallback-literal, and shared-composable heuristics.
- There is no routed or otherwise active canonical backtest-wizard owner to delegate these semantics to.

### data-state-audit
- `BacktestWizard.vue` still rendered local strategy templates, wizard steps, parameter comparison, faux KPI cards, and a wrapper-local chart as if they were verified backtest truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no pseudo backtest wizard truth > no fake stepper/comparison/KPI/chart semantics
- primary owners selected:
  - `web/frontend/src/views/BacktestWizard.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-32`
- deferred items: none

## Fix Summary
- Replaced `BacktestWizard.vue` with an honest static shell because no semantically matching canonical owner exists.
- Removed the local wizard steps, template cards, comparison table, faux KPI cards, and wrapper-local chart instead of force-mapping the page to `/strategy/backtest`.
- Retired the now-unused local pseudo-live support files `views/composables/useBacktestWizard.ts` and `views/styles/BacktestWizard.scss`.
- Recorded the reusable precedent that legacy backtest wizards with only local stepper, comparison, KPI, and chart semantics should degrade to static shells when no canonical truth contract exists.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/BacktestWizard.spec.ts` -> passed (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `275` total view files, `40` routed, `235` unrouted, `H=30 / M=110 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-32` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-32-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/BacktestWizard.vue web/frontend/src/views/__tests__/BacktestWizard.spec.ts web/frontend/src/views/composables/useBacktestWizard.ts web/frontend/src/views/styles/BacktestWizard.scss .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-32-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-32-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-32-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/backtest-wizard-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-32-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-32-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (shared dirty worktree; not an isolated verdict)
- No Playwright batch was added because the repair targets an unrouted secondary page with no independent routed proof surface.
