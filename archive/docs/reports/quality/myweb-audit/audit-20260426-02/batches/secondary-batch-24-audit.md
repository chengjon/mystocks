# Batch Audit Report: secondary-batch-24

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) EnhancedRiskMonitor.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the high-priority legacy `EnhancedRiskMonitor.vue` page into a thin wrapper over the canonical `/risk/management` owner instead of preserving a forked pseudo-live risk workbench shell

## Agent Summary

### route-inventory
- `EnhancedRiskMonitor.vue` remained in the high-priority secondary backlog because it still matched selector heuristics and still looked like a standalone live risk-management workbench.
- The page is not mounted by the current router graph, but it still presented itself as a full live risk-monitor surface even though a canonical `/risk/management` owner already exists.

### data-state-audit
- The legacy page still rendered local stop-loss, alert, websocket, GPU, and tabbed shell semantics with no independent verified contract.
- Because a semantically matching canonical risk-management owner already exists, the correct repair was a thin orchestration wrapper rather than a static shell or a new local snapshot/store.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: canonical-owner delegation > honest orchestration wrapper > static legacy shell > no fake live shell truth
- primary owners selected:
  - `web/frontend/src/views/EnhancedRiskMonitor.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-24`
- deferred items: none

## Fix Summary
- Replaced the legacy enhanced risk monitor page with a thin orchestration wrapper over the canonical `/risk/management` owner instead of a forked pseudo-live shell.
- Preserved the page only as a compatibility wrapper and delegated all real risk-management truth to the canonical owner.
- Reused the same precedent family as `RiskMonitor.vue`: if an unrouted legacy page already has a semantically matching canonical owner, keep it as a thin wrapper over that canonical truth instead of preserving local pseudo-live workbench surfaces.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/EnhancedRiskMonitor.spec.ts src/views/risk/__tests__/Center.spec.ts` -> passed (`4/4`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed (`275` view files, `40` routed, `235` unrouted, `H=39 / M=101 / L=95`)
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-24` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-24-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/EnhancedRiskMonitor.vue web/frontend/src/views/__tests__/EnhancedRiskMonitor.spec.ts .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json .claude/skills/myweb-audit/references/route-truth-casebook.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-24-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-24-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-24-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/enhanced-risk-monitor-legacy-canonical-wrapper-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-24-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-24-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
