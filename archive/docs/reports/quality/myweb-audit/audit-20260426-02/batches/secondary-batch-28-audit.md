# Batch Audit Report: secondary-batch-28

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) system/Architecture.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the legacy architecture dashboard to an honest static shell because no verified canonical architecture owner exists

## Agent Summary

### route-inventory
- `Architecture.vue` remained in the high-priority secondary backlog because it still matched the stats-strip heuristic and preserved shell-level migration/topology cards.
- There is no routed or otherwise active canonical architecture owner to delegate these semantics to.

### data-state-audit
- `Architecture.vue` still rendered hardcoded migration progress, database counts, cache-retirement copy, routing strategy, and stack summaries as if they were live verified system truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no pseudo migration metrics > no fake topology truth
- primary owners selected:
  - `web/frontend/src/views/system/Architecture.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-28`
- deferred items: none

## Fix Summary
- Replaced `Architecture.vue` with an honest static shell because no verified canonical architecture owner exists.
- Removed the local migration progress cards, topology counts, database summaries, retirement percentages, and stack-summary chrome instead of force-mapping the page to unrelated `/system/*` owners.
- Recorded the reusable precedent that legacy architecture dashboards with only hardcoded migration and topology metrics should degrade to static shells when no canonical truth contract exists.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/system/__tests__/Architecture.spec.ts` -> passed (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory remains `275` total view files, `40` routed, `235` unrouted, `H=34 / M=106 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-28` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-28-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/system/Architecture.vue web/frontend/src/views/system/__tests__/Architecture.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-28-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-28-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-28-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/system-architecture-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-28-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-28-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because the repair targets an unrouted secondary page with no independent routed proof surface.
