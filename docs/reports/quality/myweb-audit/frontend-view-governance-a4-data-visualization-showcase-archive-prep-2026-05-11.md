# Frontend View Governance A4 DataVisualizationShowcase Archive Prep

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A4-data-visualization-showcase-archive`.

This package does not move files, edit runtime code, or retire guards.

## Candidates

| File | Classification | Route/menu status | Guard status | Proposed lifecycle |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/DataVisualizationShowcase.vue` | `candidate-review/demo-sandbox` | No active router/menu owner found | Direct package target-file guard, root-demo style-entrypoint guard, and console-log cleanup guard | `archive-candidate/demo-sandbox` after direct guard retirement |
| `web/frontend/src/views/styles/DataVisualizationShowcase.scss` | `demo-local-style` | Imported only by `DataVisualizationShowcase.vue` | No separate active owner found | Archive together with owning demo page |

## Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `DataVisualizationShowcase.vue` | LOW | 0 | 0 |
| `DataVisualizationShowcase.scss` | LOW | 0 | 0 |

Static reference search:

- Focused search found no active route/menu owner for `DataVisualizationShowcase.vue`.
- `web/frontend/package.json` still contains a direct `lint:artdeco:changed` target-file guard for `src/views/DataVisualizationShowcase.vue`.
- `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` still reads `src/views/DataVisualizationShowcase.vue`.
- `web/frontend/tests/unit/config/console-log-cleanup-batch-24.spec.ts` reads only `src/views/DataVisualizationShowcase.vue` to guard one historical console-log cleanup.
- `DataVisualizationShowcase.vue` imports `./styles/DataVisualizationShowcase.scss`; focused search found no other active owner for that style file.

Successor coverage:

- Canonical chart and visualization capabilities remain in shared chart components, market K-line pages, data-domain pages, and ArtDeco chart tabs.
- The page is a standalone visual showcase, not a menu-visible business entry or active route truth.
- No runtime visualization capability should be absorbed in this batch; this is an archive-only decision for a guarded root demo shell and its local style asset.

## Direct Guards To Retire If Executed

If approved, the mutation batch must retire only:

- `node scripts/check-artdeco-tokens.js --target-file src/views/DataVisualizationShowcase.vue --changed-from-git` from `web/frontend/package.json`.
- The single `'src/views/DataVisualizationShowcase.vue'` entry from `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts`.
- `web/frontend/tests/unit/config/console-log-cleanup-batch-24.spec.ts` if it has no remaining assertion target after this page is archived.

No other package guard, workflow guard, route, menu, or root-demo-style-entrypoints entry is in scope.

## Proposed Mutation Scope

If approved:

- Move `web/frontend/src/views/DataVisualizationShowcase.vue` to `archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/DataVisualizationShowcase.vue`.
- Move `web/frontend/src/views/styles/DataVisualizationShowcase.scss` to `archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/DataVisualizationShowcase.scss`.
- Add an archive README for the paired demo page and local style.
- Retire only the direct guards listed above.
- Do not modify canonical chart components, market/data routes, ArtDeco chart tabs, `SkeletonUsage.vue`, or `StockAnalysisDemo.vue`.

## Required Execution Gates

- GitNexus impact for `DataVisualizationShowcase.vue` and `DataVisualizationShowcase.scss` before moving files.
- Exact active-reference search after the move for both page and style path.
- Staged package/spec guard checks proving only direct DataVisualizationShowcase guards were retired.
- OpenSpec strict validation.
- Markdown governance gate for archive README, execution report, and `tasks.md`.
- `git diff --cached --name-status`.
- `git diff --cached --check`.
- `gitnexus_detect_changes(scope="staged")`.

## Decision

This candidate is ready for an explicit execution decision. It is smaller than `SkeletonUsage.vue` because it has no workflow guard, and safer than `StockAnalysisDemo.vue` because `StockAnalysisDemo.vue` currently has unrelated dirty worktree edits.
