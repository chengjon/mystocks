# Batch Audit Report: secondary-batch-41

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) market/Tdx.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading the legacy market-domain TDX data-interface page to an honest static shell because no verified canonical TDX owner exists.

## Agent Summary

### route-inventory
- `market/Tdx.vue` remained in the high-priority secondary backlog because it matched selector, fallback-literal, and shared-composable heuristics before repair.
- The current router does not expose this page as an independent canonical route entry.
- The related top-level `TdxMarket.vue` was already an honest static shell, so it was not a live truth source to delegate to.

### data-state-audit
- `market/Tdx.vue` still rendered simulated connection and market-data state via `useTdx()`.
- `useTdx()` generated random response time, random active session counts, mock quotes, and simulated chart loading with TODO API comments.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: yes
- priority order applied: honest static shell > no simulated TDX connection/quote truth > delete page-local orphan pseudo-live files
- primary owner selected:
  - `web/frontend/src/views/market/Tdx.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-41`
- deferred items: none

## Fix Summary
- Replaced `market/Tdx.vue` with an honest static shell.
- Removed page-local pseudo-live `useTdx.ts` and its orphan page-only `Tdx.scss` after confirming no remaining references.
- Added owner regression coverage that fails if the page reintroduces connection status, refresh controls, response time/session metrics, quote UI, K-line controls, or hardcoded TDX server metadata.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph.
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/market/__tests__/Tdx.spec.ts` -> RED before repair, then passed after repair (`1/1`)
  - `cd web/frontend && npx vitest run src/views/market/__tests__/*.spec.ts` -> passed (`19/19`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `275` total view files, `40` routed, `235` unrouted, `H=13 / M=127 / L=95`
- Runtime and repo gates:
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-41` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-41-manifest.yaml` -> passed
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/market/Tdx.vue web/frontend/src/views/market/__tests__/Tdx.spec.ts web/frontend/src/views/market/composables/useTdx.ts web/frontend/src/views/market/styles/Tdx.scss .claude/skills/myweb-audit/references/route-truth-casebook.md .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-41-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-41-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-41-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/market-tdx-legacy-static-shell-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-41-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-41-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> `changed_count: 0`, `affected_count: 0`, `risk_level: low`; see manifest for the recorded staged-scope summary
