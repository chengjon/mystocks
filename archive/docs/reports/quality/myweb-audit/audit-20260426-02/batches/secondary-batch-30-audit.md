# Batch Audit Report: secondary-batch-30

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) system/PerformanceMonitor.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the legacy performance-monitor dashboard to an honest static shell because no verified canonical performance-monitor owner exists

## Agent Summary

### route-inventory
- `PerformanceMonitor.vue` remained in the high-priority secondary backlog because it still matched the stats-strip heuristic and preserved shell-level performance cards, budget bars, and suggestion surfaces.
- There is no routed or otherwise active canonical performance-monitor owner to delegate these semantics to.

### data-state-audit
- `PerformanceMonitor.vue` still rendered hardcoded Core Web Vitals, budget bars, trend placeholders, and optimization suggestions as if they were live verified system truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no pseudo performance cards > no fake budget or suggestion truth
- primary owners selected:
  - `web/frontend/src/views/system/PerformanceMonitor.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-30`
- deferred items: none

## Fix Summary
- Replaced `PerformanceMonitor.vue` with an honest static shell because no verified canonical performance-monitor owner exists.
- Removed the local Core Web Vitals cards, budget bars, trend placeholders, and suggestion summaries instead of force-mapping the page to unrelated `/system/*` owners.
- Recorded the reusable precedent that legacy system performance-monitor dashboards with only hardcoded performance metrics and suggestion surfaces should degrade to static shells when no canonical truth contract exists.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/system/__tests__/PerformanceMonitor.spec.ts` -> passed (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory remains `275` total view files, `40` routed, `235` unrouted, `H=32 / M=108 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-30` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-30-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/system/PerformanceMonitor.vue web/frontend/src/views/system/__tests__/PerformanceMonitor.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-30-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-30-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-30-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/system-performance-monitor-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-30-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-30-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because the repair targets an unrouted secondary page with no independent routed proof surface.
