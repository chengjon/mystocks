# Batch Audit Report: secondary-batch-34

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) Stocks.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the legacy stocks workbench to an honest static shell because no semantically matching canonical owner exists

## Agent Summary

### route-inventory
- `Stocks.vue` remained in the high-priority secondary backlog because it still matched the selector and fallback-literal heuristics.
- There is no routed or otherwise active canonical stocks owner to delegate these combined list, filter, and action semantics to.

### data-state-audit
- `Stocks.vue` still rendered local filters, stock rows, refresh chrome, and detail-analysis actions as if they were verified stock-list truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no pseudo stocks truth > no fake filter/list/refresh/action semantics
- primary owners selected:
  - `web/frontend/src/views/Stocks.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-34`
- deferred items: none

## Fix Summary
- Replaced `Stocks.vue` with an honest static shell because no semantically matching canonical owner exists.
- Removed the local filter bar, faux stock list, refresh chrome, and detail-analysis actions instead of force-mapping the page to `/watchlist/screener`, `/market/realtime`, or `/detail/graphics/:symbol`.
- Recorded the reusable precedent that legacy stocks workbenches with only local filter, list, refresh, and action semantics should degrade to static shells when no canonical truth contract exists.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/Stocks.spec.ts` -> passed (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `275` total view files, `40` routed, `235` unrouted, `H=28 / M=112 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-34` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-34-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/Stocks.vue web/frontend/src/views/__tests__/Stocks.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-34-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-34-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-34-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/stocks-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-34-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-34-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (shared dirty worktree; not an isolated verdict)
- No Playwright batch was added because the repair targets an unrouted secondary page with no independent routed proof surface.
