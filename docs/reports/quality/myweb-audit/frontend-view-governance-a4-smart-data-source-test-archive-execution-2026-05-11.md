# Frontend View Governance A4 SmartDataSourceTest Archive Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: execution record for `A4-smart-data-source-test-archive`.

## Approved Scope

Moved files:

- `web/frontend/src/views/SmartDataSourceTest.vue`
- `web/frontend/src/views/styles/SmartDataSourceTest.css`

Retired direct guards:

- `node scripts/check-artdeco-tokens.js --target-file src/views/SmartDataSourceTest.vue --changed-from-git`
- `'src/views/SmartDataSourceTest.vue'` from `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts`

Retained out of scope:

- `SmartDataIndicator`
- `smartDataService`
- Canonical system/data routes
- `DataVisualizationShowcase.vue`
- `SkeletonUsage.vue`
- `StockAnalysisDemo.vue`

## Pre-Move Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `SmartDataSourceTest.vue` | LOW | 0 | 0 |
| `SmartDataSourceTest.css` | LOW | 0 | 0 |

Static reference checks:

- No active router/menu owner was found for `SmartDataSourceTest.vue`.
- The page had one direct package target-file guard and one root-demo style-entrypoint guard.
- `SmartDataSourceTest.css` was imported only by `SmartDataSourceTest.vue`.

## Files Moved

| Original path | Archive path |
| --- | --- |
| `web/frontend/src/views/SmartDataSourceTest.vue` | `archive/web/frontend/src/views/root-sandbox/smart-data-source-test/SmartDataSourceTest.vue` |
| `web/frontend/src/views/styles/SmartDataSourceTest.css` | `archive/web/frontend/src/views/root-sandbox/smart-data-source-test/SmartDataSourceTest.css` |

## Files Added

| File | Purpose |
| --- | --- |
| `archive/web/frontend/src/views/root-sandbox/smart-data-source-test/README.md` | Governed archive manifest and restore rule |

## Cleanup Decision

This is an archive move, not deletion. The page is classified as `archive-candidate/demo-sandbox`, and its style is classified as `demo-local-style` because its only active owner was the archived page.

## Post-Move Checks

| Check | Command / Scope | Result |
| --- | --- | --- |
| Exact active-reference search for page | `rg -n "src/views/SmartDataSourceTest\|@/views/SmartDataSourceTest\|../SmartDataSourceTest\\.vue\|./SmartDataSourceTest\\.vue\|SmartDataSourceTest\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| Exact active-reference search for style | `rg -n "src/views/styles/SmartDataSourceTest\|styles/SmartDataSourceTest\|SmartDataSourceTest\\.css" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| Package guard check | Parse `web/frontend/package.json` and inspect `scripts.lint:artdeco:changed` | Passed; `src/views/SmartDataSourceTest.vue` is absent while adjacent guards for `DataVisualizationShowcase.vue`, `SkeletonUsage.vue`, and `StockAnalysisDemo.vue` remain present. |
| Style-entrypoint guard check | Inspect `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` | Passed; `src/views/SmartDataSourceTest.vue` is absent while adjacent entries for `DataVisualizationShowcase.vue` and `StockAnalysisDemo.vue` remain present. |
| Targeted Vitest | `npm run test -- --run tests/unit/config/root-demo-style-entrypoints.spec.ts` from `web/frontend` | Passed in the current worktree; `1` file, `2` tests. |
| Staged guard content check | Parse staged `package.json` and staged `root-demo-style-entrypoints.spec.ts` with `git show :<path>` | Passed; only the direct `SmartDataSourceTest.vue` guards are absent, while adjacent `DataVisualizationShowcase.vue`, `SkeletonUsage.vue`, and `StockAnalysisDemo.vue` guards remain present as applicable. |
| OpenSpec strict validation | `openspec validate update-frontend-view-governance --strict` | Passed. |
| Markdown governance gate | Archive README, this execution report, and `tasks.md` | Passed; `3` files, `0` errors. |
| Diff whitespace check | `git diff --check -- <changed paths>` | Passed. |

Note: an initial targeted Vitest attempt used the repository-relative path `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` from the `web/frontend` working directory and matched no files. It was rerun with the correct frontend-relative path above. `root-demo-style-entrypoints.spec.ts` already had unrelated unstaged worktree edits before this batch, so the staged commit scope was split to include only the `SmartDataSourceTest.vue` guard removal from that file.

## Staged Commit Gate

Final staged scope:

| Check | Result |
| --- | --- |
| `git diff --cached --name-status` | Passed; staged scope contains only the two source renames, archive README, direct package/spec guard removals, this execution record, and `tasks.md`. |
| `git diff --cached --check` | Passed. |
| `gitnexus_detect_changes(scope="staged")` | Passed; risk `low`, changed files `7`, affected processes `0`. |
