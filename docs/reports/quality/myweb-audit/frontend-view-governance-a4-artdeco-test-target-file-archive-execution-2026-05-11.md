# Frontend View Governance A4 ArtDecoTest Target-File Archive Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: execution record for `A4-artdeco-test-target-file-archive`.

## Approved Scope

Moved file:

- `web/frontend/src/views/ArtDecoTest.vue`

Retired direct package guard:

- `node scripts/check-artdeco-tokens.js --target-file src/views/ArtDecoTest.vue --changed-from-git`

Retained out of scope:

- `web/frontend/src/views/DataVisualizationShowcase.vue`
- `web/frontend/src/views/KLineDemo.vue`
- `web/frontend/src/views/MarketDataDemo.vue`
- `web/frontend/src/views/SkeletonUsage.vue`
- `web/frontend/src/views/SmartDataSourceTest.vue`
- `web/frontend/src/views/StockAnalysisDemo.vue`

## Pre-Move Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `ArtDecoTest.vue` | LOW | 0 | 0 |

Static reference checks:

- No active router/menu owner was found for `ArtDecoTest.vue`.
- No direct Vue unit test import was found for `ArtDecoTest.vue`.
- The only direct runtime/tooling owner found was the `lint:artdeco:changed` target-file entry retired in this batch.
- Historical governance references remain intentionally as audit evidence.

## Files Moved

| Original path | Archive path |
| --- | --- |
| `web/frontend/src/views/ArtDecoTest.vue` | `archive/web/frontend/src/views/root-sandbox/artdeco-test/ArtDecoTest.vue` |

## Files Added

| File | Purpose |
| --- | --- |
| `archive/web/frontend/src/views/root-sandbox/artdeco-test/README.md` | Governed archive manifest and restore rule |

## Cleanup Decision

This is an archive move, not deletion. The page is classified as `archive-candidate/demo-sandbox` with `no-successor-needed` because it was a local ArtDeco component visual smoke shell without active route, menu, or direct Vue test ownership.

## Post-Move Checks

| Check | Command / Scope | Result |
| --- | --- | --- |
| Exact active-reference search | `rg -n "src/views/ArtDecoTest\|@/views/ArtDecoTest\|../ArtDecoTest\\.vue\|./ArtDecoTest\\.vue\|ArtDecoTest\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| Package script parse/guard check | Parse `web/frontend/package.json` and inspect `scripts.lint:artdeco:changed` | Passed; JSON parses, `src/views/ArtDecoTest.vue` is absent, adjacent guards such as `SkeletonUsage.vue` and `Stocks.vue` remain present. |
| OpenSpec strict validation | `openspec validate update-frontend-view-governance --strict` | Passed. |
| Markdown governance gate | Archive README, this execution report, and `tasks.md` | Passed; `3` files, `0` errors. |
| Diff whitespace check | `git diff --check -- <changed paths>` | Passed. |

## Staged Commit Gate

Final staged scope:

| Check | Result |
| --- | --- |
| `git diff --cached --name-status` | Passed; staged scope contains only `ArtDecoTest.vue` rename, archive README, this execution record, `tasks.md`, and `package.json`. |
| `git diff --cached --check` | Passed. |
| `gitnexus_detect_changes(scope="staged")` | Passed; risk `low`, changed symbols `1` (`web/frontend/package.json`), affected processes `0`. |
