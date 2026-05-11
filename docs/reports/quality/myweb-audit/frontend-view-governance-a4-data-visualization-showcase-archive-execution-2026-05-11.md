# Frontend View Governance A4 DataVisualizationShowcase Archive Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: execution record for `A4-data-visualization-showcase-archive`.

## Approved Scope

Moved files:

- `web/frontend/src/views/DataVisualizationShowcase.vue`
- `web/frontend/src/views/styles/DataVisualizationShowcase.scss`

Retired direct guards:

- `node scripts/check-artdeco-tokens.js --target-file src/views/DataVisualizationShowcase.vue --changed-from-git`
- `'src/views/DataVisualizationShowcase.vue'` from `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-24.spec.ts`

Retained out of scope:

- Canonical chart components
- Market/data routes and tests
- ArtDeco chart tabs
- `SkeletonUsage.vue`
- `StockAnalysisDemo.vue`

## Pre-Move Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `DataVisualizationShowcase.vue` | LOW | 0 | 0 |
| `DataVisualizationShowcase.scss` | LOW | 0 | 0 |
| `console-log-cleanup-batch-24.spec.ts` | LOW | 0 | 0 |

Static reference checks:

- No active route/menu owner was found for `DataVisualizationShowcase.vue`.
- The page had one direct package target-file guard, one root-demo style-entrypoint guard, and one dedicated console-log cleanup guard.
- `DataVisualizationShowcase.scss` was imported only by `DataVisualizationShowcase.vue`.

## Files Moved

| Original path | Archive path |
| --- | --- |
| `web/frontend/src/views/DataVisualizationShowcase.vue` | `archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/DataVisualizationShowcase.vue` |
| `web/frontend/src/views/styles/DataVisualizationShowcase.scss` | `archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/DataVisualizationShowcase.scss` |

## Files Added

| File | Purpose |
| --- | --- |
| `archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/README.md` | Governed archive manifest and restore rule |

## Cleanup Decision

This is an archive move, not deletion. The page is classified as `archive-candidate/demo-sandbox`, and its style is classified as `demo-local-style` because its only active owner was the archived page. The dedicated console-log cleanup spec was retired because its only assertion target was the archived page.

## Post-Move Checks

| Check | Command / Scope | Result |
| --- | --- | --- |
| Exact active-reference search for page | `rg -n "src/views/DataVisualizationShowcase\|@/views/DataVisualizationShowcase\|../DataVisualizationShowcase\\.vue\|./DataVisualizationShowcase\\.vue\|DataVisualizationShowcase\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| Exact active-reference search for style | `rg -n "src/views/styles/DataVisualizationShowcase\|styles/DataVisualizationShowcase\|DataVisualizationShowcase\\.scss" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| Console cleanup guard search | `rg -n "console-log-cleanup-batch-24\|chart ready" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| Package guard check | Parse `web/frontend/package.json` and inspect `scripts.lint:artdeco:changed` | Passed; `src/views/DataVisualizationShowcase.vue` is absent while adjacent guards for `SkeletonUsage.vue` and `StockAnalysisDemo.vue` remain present. |
| Style-entrypoint guard check | Inspect `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` | Passed; `src/views/DataVisualizationShowcase.vue` is absent while `StockAnalysisDemo.vue` remains present. |
| OpenSpec strict validation | `openspec validate update-frontend-view-governance --strict` | Passed. |
| Markdown governance gate | Archive README, this execution report, and `tasks.md` | Passed; `3` files, `0` errors. |
| Diff whitespace check | `git diff --check -- <changed paths>` | Passed. |

Note: `root-demo-style-entrypoints.spec.ts` already had unrelated unstaged worktree edits before this batch, so the staged commit scope must be split to include only the `DataVisualizationShowcase.vue` guard removal from that file.

## Staged Commit Gate

Final staged scope:

- `R100 web/frontend/src/views/DataVisualizationShowcase.vue` to `archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/DataVisualizationShowcase.vue`
- `R100 web/frontend/src/views/styles/DataVisualizationShowcase.scss` to `archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/DataVisualizationShowcase.scss`
- `A archive/web/frontend/src/views/root-sandbox/data-visualization-showcase/README.md`
- `A docs/reports/quality/myweb-audit/frontend-view-governance-a4-data-visualization-showcase-archive-execution-2026-05-11.md`
- `M openspec/changes/update-frontend-view-governance/tasks.md`
- `M web/frontend/package.json`
- `D web/frontend/tests/unit/config/console-log-cleanup-batch-24.spec.ts`
- `M web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts`

Final gate results:

- `git diff --cached --name-status`: passed; staged scope matches the approved archive batch.
- `git diff --cached --check`: passed.
- `gitnexus_detect_changes(scope="staged")`: passed; risk `low`, affected processes `0`.
- `root-demo-style-entrypoints.spec.ts`: staged diff includes only the single `DataVisualizationShowcase.vue` guard removal; unrelated worktree edits remain unstaged.
