# Batch Audit Report: secondary-batch-38

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) market/Auction.vue`
  - `(unrouted) market/Etf.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading two legacy market-domain pages to honest static shells because no semantically matching verified canonical auction or ETF owner exists

## Agent Summary

### route-inventory
- `market/Auction.vue` and `market/Etf.vue` remained in the high-priority secondary backlog because they still matched selector, stats, shared-composable, or pseudo-live market shell heuristics before repair.
- Neither page has a current router entry, and nearby sibling modules are embedded/legacy surfaces rather than one-to-one canonical route truth.

### data-state-audit
- `market/Auction.vue` still rendered local auction KPI cards, refresh simulation, status tags, and hardcoded sample rows as if they were verified auction truth.
- `market/Etf.vue` still rendered local ETF overview cards, auto-refresh controls, category selectors, table/ranking chrome, and hardcoded ETF rows as if they were verified ETF truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: yes
- priority order applied: honest static shell > no pseudo market truth > no fake metrics/selectors/rankings/sample rows
- primary owners selected:
  - `web/frontend/src/views/market/Auction.vue`
  - `web/frontend/src/views/market/Etf.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-38`
- deferred items: none

## Fix Summary
- Replaced `market/Auction.vue` with an honest static shell because no semantically matching verified auction owner exists.
- Replaced `market/Etf.vue` with an honest static shell because no semantically matching verified ETF owner exists.
- Recorded the reusable precedent that unresolved legacy market subpages should not be remapped to embedded siblings that still carry fallback or tab-local semantics.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because both repaired owners are unrouted secondary pages with no independent routed proof surface in the current router graph
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/market/__tests__/Auction.spec.ts src/views/market/__tests__/Etf.spec.ts` -> passed (`2/2`)
  - `cd web/frontend && npx vitest run src/views/market/__tests__/*.spec.ts` -> passed (`17/17`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `275` total view files, `40` routed, `235` unrouted, `H=22 / M=118 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-38` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-38-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/market/Auction.vue web/frontend/src/views/market/Etf.vue web/frontend/src/views/market/__tests__/Auction.spec.ts web/frontend/src/views/market/__tests__/Etf.spec.ts .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-38-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-38-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-38-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/market-auction-etf-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-38-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-38-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`; shared dirty worktree, not an isolated verdict)
- No Playwright batch was added because the repair targets unrouted secondary pages with no independent routed proof surface.
