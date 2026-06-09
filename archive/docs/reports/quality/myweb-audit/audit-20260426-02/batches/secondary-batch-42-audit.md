# Batch Audit Report: secondary-batch-42

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) monitor.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the legacy system monitor page to an honest static shell because no verified one-to-one canonical monitoring owner exists.

## Agent Summary

### route-inventory
- `monitor.vue` remained in the high-priority secondary backlog because it matched shared-composable, fallback-literal, and pseudo-runtime heuristics before repair.
- The current router does not expose this page as an independent canonical route entry.
- Existing canonical `/system/*` routes provide verified system health/resource surfaces, but none is a one-to-one owner for this legacy monitor workbench.

### data-state-audit
- `monitor.vue` still rendered local pseudo-live monitoring state through `usemonitor()`.
- `usemonitor()` seeded service statuses, refresh timestamps, local history rows, and endpoint metadata without a verified monitoring contract.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: yes
- priority order applied: honest static shell > no local pseudo-live service checks > delete page-local orphan files
- primary owner selected:
  - `web/frontend/src/views/monitor.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-42`
- deferred items: none

## Fix Summary
- Replaced `monitor.vue` with an honest static shell.
- Removed page-local pseudo-live `usemonitor.ts` and its orphan page-only `monitor.scss`.
- Added owner regression coverage that fails if the page reintroduces old refresh controls, service details, history, local database labels, or hardcoded endpoint metadata.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph.
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/monitor.spec.ts` -> RED before repair, then passed after repair (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `276` total view files, `41` routed, `235` unrouted, `H=12 / M=128 / L=95`
- Runtime and repo gates:
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-42` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-42-manifest.yaml` -> passed
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/monitor.vue web/frontend/src/views/__tests__/monitor.spec.ts web/frontend/src/views/composables/usemonitor.ts web/frontend/src/views/styles/monitor.scss .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-42-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-42-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-42-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/monitor-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-42-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-42-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `rg "usemonitor|styles/monitor\\.scss|monitor\\.scss" web/frontend/src --glob '!**/.claude/**'` -> no matches
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed staged observation with `changed_count: 408`, `changed_files: 172`, `affected_count: 3`, `risk_level: medium`; unrelated pre-existing staged files dominate the result, so this is not an isolated batch-42 verdict
