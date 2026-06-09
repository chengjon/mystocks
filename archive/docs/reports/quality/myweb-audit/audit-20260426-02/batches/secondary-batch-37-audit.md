# Batch Audit Report: secondary-batch-37

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) market/CapitalFlow.vue`
  - `(unrouted) market/Concepts.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing two legacy market-domain pages into thin wrappers over the existing canonical `/data/*` owners instead of preserving duplicate pseudo-live market shells

## Agent Summary

### route-inventory
- `market/CapitalFlow.vue` and `market/Concepts.vue` remained in the high-priority secondary backlog because they still matched selector-driven pseudo-live shells and duplicated `/data/*` market-analysis semantics outside the current router graph.
- Both pages have semantically matching active canonical owners at `web/frontend/src/views/data/FundFlow.vue` and `web/frontend/src/views/data/Concepts.vue`.

### data-state-audit
- `market/CapitalFlow.vue` still rendered local overview cards, a refresh-all action, movers tables, and a wrapper-local `FundFlowPanel` shell as if they were independent market-domain truth.
- `market/Concepts.vue` still rendered local concept stats, refresh controls, hot rankings, and detail-table chrome as if they were independent market-domain truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: yes
- priority order applied: canonical delegation > no duplicate market-domain shell truth > no new wrapper-local snapshot/store
- primary owners selected:
  - `web/frontend/src/views/market/CapitalFlow.vue`
  - `web/frontend/src/views/market/Concepts.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-37`
- deferred items: none

## Fix Summary
- Replaced `market/CapitalFlow.vue` with a thin wrapper over the canonical `/data/fund-flow` owner.
- Replaced `market/Concepts.vue` with a thin wrapper over the canonical `/data/concept` owner.
- Recorded the reusable precedent that legacy market-domain pages should delegate to canonical data-domain owners when the verified truth already exists there, instead of preserving duplicate overview, refresh, ranking, or detail shells.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because both repaired owners are unrouted secondary pages with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/market/__tests__/CapitalFlow.spec.ts src/views/market/__tests__/Concepts.spec.ts src/views/data/__tests__/FundFlow.spec.ts src/views/data/__tests__/Concepts.spec.ts` -> passed (`10/10`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `275` total view files, `40` routed, `235` unrouted, `H=24 / M=116 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-37` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-37-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/market/CapitalFlow.vue web/frontend/src/views/market/Concepts.vue web/frontend/src/views/market/__tests__/CapitalFlow.spec.ts web/frontend/src/views/market/__tests__/Concepts.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-37-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-37-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-37-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/market-fund-flow-concepts-legacy-canonical-wrapper-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-37-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-37-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`; shared dirty worktree, not an isolated verdict)
- No Playwright batch was added because the repair targets unrouted secondary pages with no independent routed proof surface.
