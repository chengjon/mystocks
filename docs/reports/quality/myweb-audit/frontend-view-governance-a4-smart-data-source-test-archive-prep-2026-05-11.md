# Frontend View Governance A4 SmartDataSourceTest Archive Prep

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A4-smart-data-source-test-archive`.

This package does not move files, edit runtime code, or retire guards.

## Candidates

| File | Classification | Route/menu status | Guard status | Proposed lifecycle |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/SmartDataSourceTest.vue` | `candidate-review/demo-sandbox` | No active router/menu owner found | Direct package target-file guard and root-demo style-entrypoint guard | `archive-candidate/demo-sandbox` after direct guard retirement |
| `web/frontend/src/views/styles/SmartDataSourceTest.css` | `demo-local-style` | Imported only by `SmartDataSourceTest.vue` | No separate active owner found | Archive together with owning demo page |

## Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `SmartDataSourceTest.vue` | LOW | 0 | 0 |
| `SmartDataSourceTest.css` | LOW | 0 | 0 |

Static reference search:

- Focused search found no active route/menu owner for `SmartDataSourceTest.vue`.
- `web/frontend/package.json` still contains a direct `lint:artdeco:changed` target-file guard for `src/views/SmartDataSourceTest.vue`.
- `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` still reads `src/views/SmartDataSourceTest.vue`.
- `SmartDataSourceTest.vue` imports `./styles/SmartDataSourceTest.css`; focused search found no other active owner for that style file.

Successor coverage:

- Current system/data-source health and data management truth should remain in canonical system/data routes and components, not in this root demo shell.
- The page is a manual diagnostic/demo shell around `SmartDataIndicator` and `smartDataService`, not a menu-visible business entry.
- No runtime capability should be absorbed in this batch; this is an archive-only decision for a guarded root demo shell and its local style asset.

## Direct Guards To Retire If Executed

If approved, the mutation batch must retire only:

- `node scripts/check-artdeco-tokens.js --target-file src/views/SmartDataSourceTest.vue --changed-from-git` from `web/frontend/package.json`.
- The single `'src/views/SmartDataSourceTest.vue'` entry from `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts`.

No other package guard, workflow guard, route, menu, or root-demo-style-entrypoints entry is in scope.

## Proposed Mutation Scope

If approved:

- Move `web/frontend/src/views/SmartDataSourceTest.vue` to `archive/web/frontend/src/views/root-sandbox/smart-data-source-test/SmartDataSourceTest.vue`.
- Move `web/frontend/src/views/styles/SmartDataSourceTest.css` to `archive/web/frontend/src/views/root-sandbox/smart-data-source-test/SmartDataSourceTest.css`.
- Add an archive README for the paired demo page and local style.
- Retire only the two direct guards listed above.
- Do not modify `SmartDataIndicator`, `smartDataService`, canonical system/data routes, or unrelated root demo pages.

## Required Execution Gates

- GitNexus impact for `SmartDataSourceTest.vue` and `SmartDataSourceTest.css` before moving files.
- Exact active-reference search after the move for both page and style path.
- Targeted config test for `root-demo-style-entrypoints.spec.ts` or an equivalent parse/read check proving the remaining file list is valid.
- OpenSpec strict validation.
- Markdown governance gate for archive README, execution report, and `tasks.md`.
- `git diff --cached --name-status`.
- `git diff --cached --check`.
- `gitnexus_detect_changes(scope="staged")`.

## Decision

This candidate is ready for an explicit execution decision. It is smaller than `DataVisualizationShowcase.vue`, `SkeletonUsage.vue`, and `StockAnalysisDemo.vue` because it has one direct package guard, one direct root-demo style-entrypoint guard, and one local style asset with no separate discovered owner.
