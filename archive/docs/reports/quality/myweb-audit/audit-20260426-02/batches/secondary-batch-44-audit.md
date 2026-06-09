# Batch Audit Report: secondary-batch-44

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) StockAnalysisDemo.vue`
  - `(unrouted children) stock-analysis/*Tab.vue`
- Batch rationale: close the six high-priority stock-analysis child tabs by retiring the legacy aggregate demo parent that was their only consumer.

## Agent Summary

### route-inventory
- The six `stock-analysis/*Tab.vue` files remained in the high-priority secondary backlog because they matched selector and stats-strip heuristics.
- `StockAnalysisDemo.vue` is not a current router entry and was the only source import for all six tab files.
- Existing canonical market and strategy pages can own their specific slices, but no one-to-one owner exists for the aggregate stock-analysis demo.

### data-state-audit
- The child tabs preserved local TDX parsing examples, strategy snippets, RQAlpha backtest metrics, realtime ticker cards, monitoring logs, local paths, and integration-status claims.
- The repair avoids creating any new stock-analysis snapshot or store; it degrades the parent to a static handoff shell and removes the orphan children.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: yes
- priority order applied: honest static shell > remove selector-driven demo truth > delete page-local orphan children/style
- primary owner selected:
  - `web/frontend/src/views/StockAnalysisDemo.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-44`
- deferred items: none

## Fix Summary
- Replaced `StockAnalysisDemo.vue` with an honest static shell.
- Removed six page-local stock-analysis tab components and the page-only SCSS.
- Converted the prior style-normalization config test into a decommission guard for the retired tab files.
- Added owner regression coverage that fails if the page reintroduces the tab labels or dynamic selector workbench.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary page with no independent routed proof surface in the current router graph.
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/StockAnalysisDemo.spec.ts` -> RED before repair, then passed after repair (`1/1`)
  - `cd web/frontend && npx vitest run src/views/__tests__/StockAnalysisDemo.spec.ts tests/unit/config/stock-analysis-style-normalization.spec.ts tests/unit/config/root-demo-style-entrypoints.spec.ts` -> passed (`5/5`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `270` total view files, `41` routed, `229` unrouted, `H=5 / M=129 / L=95`
- Runtime and repo gates:
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-44` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-44-manifest.yaml` -> passed
  - `git diff --check -- <secondary-batch-44 files>` -> passed
  - `timeout 180s npm run type-check` -> failed only on existing frontend type debt in `dashboardService.ts` and `useKLinePatternOverlays.ts`; no new structural syntax error was introduced by this batch
  - `pm2 list` -> `mystocks-backend` and `mystocks-frontend` online at `http://localhost:8020` and `http://localhost:3020`
  - `gitnexus_detect_changes({scope: "staged"})` -> mixed-staged observation only: `changed_count=436`, `changed_files=199`, `affected_count=3`, `risk_level=medium`; the staged index already contained many unrelated files, so this is not an isolated batch-44 risk verdict
