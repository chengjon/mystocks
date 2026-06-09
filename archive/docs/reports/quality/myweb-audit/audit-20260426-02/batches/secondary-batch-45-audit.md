# Batch Audit Report: secondary-batch-45

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) strategy/BatchScan.vue`
  - `(unrouted) strategy/ResultsQuery.vue`
  - `(unrouted) strategy/SingleRun.vue`
  - `(unrouted) strategy/StatsAnalysis.vue`
- Batch rationale: close the four high-priority legacy strategy workbench pages by removing retired selector-owned execution/query state.

## Agent Summary

### route-inventory
- None of the four pages are registered in the current router graph.
- They are not imported by canonical `/strategy/*` routes.
- Current canonical strategy ownership remains `/strategy/repo`, `/strategy/backtest`, and `/strategy/opt`.

### data-state-audit
- The pages preserved old strategy selectors, execution buttons, result/export actions, auto-refresh state, and stats cards.
- The API facade they referenced is only present in deprecated frontend API code, so the pages could not provide verified current execution truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: yes
- priority order applied: honest static shell > remove selector-owned execution state > delete page-local orphan styles
- primary owner selected:
  - `web/frontend/src/views/strategy/BatchScan.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-45`
- deferred items: none

## Fix Summary
- Replaced four legacy strategy execution/query pages with honest static shells.
- Removed four page-local SCSS files tied only to the retired workbench UI.
- Added owner regression coverage and a decommission guard for retired style/API execution state.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable because these owners are unrouted secondary pages with no independent routed proof surface in the current router graph.
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/strategy/__tests__/LegacyStrategyWorkbench.spec.ts` -> RED before repair; failed while importing old pages and exposed a `BatchScan.vue` structural template error
  - `cd web/frontend && npx vitest run src/views/strategy/__tests__/LegacyStrategyWorkbench.spec.ts tests/unit/config/legacy-strategy-workbench-decommission.spec.ts tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts` -> passed (`7/7`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory is now `270` total view files, `41` routed, `229` unrouted, `H=1 / M=133 / L=95`
- Runtime and repo gates:
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-45` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-45-manifest.yaml` -> passed
  - `git diff --check -- <secondary-batch-45 files>` -> passed
  - `timeout 180s npm run type-check` -> failed only on existing frontend type debt in `dashboardService.ts` and `useKLinePatternOverlays.ts`; no new structural syntax error was introduced by this batch
  - `pm2 list` -> `mystocks-backend` and `mystocks-frontend` online at `http://localhost:8020` and `http://localhost:3020`
  - `gitnexus_detect_changes({scope: "staged"})` -> mixed-staged observation only: `changed_count=480`, `changed_files=220`, `affected_count=3`, `risk_level=medium`; the staged index already contained many unrelated files, so this is not an isolated batch-45 risk verdict
