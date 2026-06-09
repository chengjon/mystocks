# Batch Audit Report: secondary-batch-22

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) TdxMarket.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the top-level legacy TDX market workbench into an honest static shell because no verified canonical owner exists and the only same-domain sibling still depends on simulated transport and TODO APIs

## Agent Summary

### route-inventory
- `TdxMarket.vue` remained in the high-priority shortlist because it still combined selector-driven quote lookup with local fallback literals and a large pseudo-live shell.
- The current router graph exposes nearby verified `/market/*` and `/system/*` routes, but no verified one-to-one canonical TDX owner for direct delegation.

### data-state-audit
- `TdxMarket.vue` still rendered local index-monitoring, real-time quote, K-line, and auto-refresh surfaces as if they were live route truth.
- `market/Tdx.vue` was not an acceptable canonical owner because its `useTdx()` composable still simulates connection checks, quote data, and chart loading behind explicit TODO placeholders.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no legacy-to-legacy delegation > no fake local market truth
- primary owners selected:
  - `web/frontend/src/views/TdxMarket.vue`
- shared-impact review items:
  - `web/frontend/src/views/market/Tdx.vue` reviewed and explicitly left unresolved in the backlog; no delegation allowed
- fixes applied:
  - `secondary-shell-issue-22`
- deferred items:
  - `web/frontend/src/views/market/Tdx.vue` remains an unresolved secondary candidate because it still uses simulated transport via `useTdx()`

## Fix Summary
- Replaced `TdxMarket.vue` with an honest static shell instead of a local pseudo-live TDX market workbench.
- Preserved the page only as a legacy location that hands users off to verified `/market/realtime`, `/market/technical`, and `/system/data`.
- Recorded the precedent that unresolved same-domain legacy siblings cannot be promoted to canonical truth sources.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/TdxMarket.spec.ts` -> passed `1/1`
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory now reports `275` total view files, `40` routed, `235` unrouted, `H=41 / M=99 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
- Artifact validation:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-22` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-22-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remain online
  - `git diff --check -- ...secondary-batch-22 scope...` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
