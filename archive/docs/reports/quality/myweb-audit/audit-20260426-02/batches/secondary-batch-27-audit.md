# Batch Audit Report: secondary-batch-27

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) Wencai.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the legacy Wencai page into a thin wrapper over the already-live `WencaiPanel.vue` truth component instead of preserving a second pseudo overview and statistics shell

## Agent Summary

### route-inventory
- `Wencai.vue` remained in the high-priority secondary backlog because it still matched selector and fallback-literal heuristics even after the canonical route matrix was closed.
- The live feature contract is not a routed `/wencai` owner, but `WencaiPanel.vue` already owns the real Wencai API/query/result/history behavior.

### data-state-audit
- `Wencai.vue` still fronted `WencaiPanel.vue` with a wrapper-local overview card, fake API status, pseudo statistics tabs, and a local `loadStatistics()` fetch, duplicating truth in front of the real panel.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: thin wrapper over live truth component > no wrapper-local pseudo overview > no duplicate summary fetch
- primary owners selected:
  - `web/frontend/src/views/Wencai.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-27`
- deferred items: none

## Fix Summary
- Replaced `Wencai.vue` with a thin wrapper over `WencaiPanel.vue`.
- Removed the local pseudo overview, fake API status, statistics tabs, and wrapper-local summary fetch instead of preserving a second shell-level truth source.
- Recorded the reusable precedent that an unrouted legacy page may preserve an inner live truth component even when no routed canonical owner exists, as long as the outer wrapper deletes its fake shell semantics.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page and the live contract already sits inside the preserved `WencaiPanel.vue` component
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/Wencai.spec.ts` -> passed (`1/1`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory remains `275` total view files, `40` routed, `235` unrouted, `H=35 / M=105 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-27` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-27-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/Wencai.vue web/frontend/src/views/__tests__/Wencai.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/route-truth-operations.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-27-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-27-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-27-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/wencai-legacy-live-panel-wrapper-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-27-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-27-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because the repair targets an unrouted legacy owner and the preserved live contract already lives inside the reused `WencaiPanel.vue` component.
