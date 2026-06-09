# Batch Audit Report: secondary-batch-35

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) AdvancedAnalysis.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the legacy advanced-analysis workbench to an honest static shell because no semantically matching canonical owner exists

## Agent Summary

### route-inventory
- `AdvancedAnalysis.vue` remained in the high-priority secondary backlog because it still matched the selector, fallback-literal, and shared-composable heuristics.
- There is no routed or otherwise active canonical advanced-analysis owner to delegate these combined analysis, prediction, and result semantics to.

### data-state-audit
- `AdvancedAnalysis.vue` still rendered local analysis configuration, batch-run controls, Kronos prediction, system health cards, and result panels as if they were verified advanced-analysis truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no pseudo advanced-analysis truth > no fake configuration/prediction/health/result semantics
- primary owners selected:
  - `web/frontend/src/views/AdvancedAnalysis.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-35`
- deferred items: none

## Fix Summary
- Replaced `AdvancedAnalysis.vue` with an honest static shell because no semantically matching canonical owner exists.
- Removed the local analysis form, batch-run controls, Kronos prediction area, system health cards, and result panels instead of force-mapping the page to `/data/indicator`, `/detail/graphics/:symbol`, or `/strategy/signals`.
- Retired the now-unused local page-only composable `views/composables/useAdvancedAnalysis.ts`.
- Recorded the reusable precedent that legacy advanced-analysis workbenches with only local configuration, prediction, health, and result semantics should degrade to static shells when no canonical truth contract exists.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/AdvancedAnalysis.spec.ts` -> passed (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `275` total view files, `40` routed, `235` unrouted, `H=27 / M=113 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-35` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-35-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/AdvancedAnalysis.vue web/frontend/src/views/__tests__/AdvancedAnalysis.spec.ts web/frontend/src/views/composables/useAdvancedAnalysis.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-35-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-35-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-35-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/advanced-analysis-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-35-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-35-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (shared dirty worktree; not an isolated verdict)
- No Playwright batch was added because the repair targets an unrouted secondary page with no independent routed proof surface.
