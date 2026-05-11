# Frontend View Governance A4 ArtDecoTest Target-File Archive Prep

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A4-artdeco-test-target-file-archive`.

This package does not move files, edit runtime code, or retire guards.

## Candidate

| File | Classification | Route/menu status | Guard status | Proposed lifecycle |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/ArtDecoTest.vue` | `candidate-review/demo-sandbox` | No active router/menu owner found | Direct `lint:artdeco:changed` package target-file guard | `archive-candidate/demo-sandbox` after direct guard retirement |

## Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `ArtDecoTest.vue` | LOW | 0 | 0 |

Static reference search:

- Current focused search found no router/menu import for `ArtDecoTest.vue`.
- Current focused search found no direct Vue unit test importing `ArtDecoTest.vue`.
- Current focused search found no package script reference except `lint:artdeco:changed`.
- Current focused search found historical governance references in root demo sidecar inventory and this OpenSpec work line.
- The file is a local ArtDeco component visual smoke shell and contains diagnostic `console.log` calls; it is not a canonical route page.

## Direct Guard To Retire If Executed

If approved, the mutation batch must remove only this direct package target from `web/frontend/package.json`:

```text
node scripts/check-artdeco-tokens.js --target-file src/views/ArtDecoTest.vue --changed-from-git
```

No other `lint:artdeco:changed` target-file or target-dir entry is in scope.

## Proposed Mutation Scope

If approved:

- Move `web/frontend/src/views/ArtDecoTest.vue` to `archive/web/frontend/src/views/root-sandbox/artdeco-test/ArtDecoTest.vue`.
- Add an archive README for the ArtDeco test sandbox shell.
- Retire only the direct `ArtDecoTest.vue` `lint:artdeco:changed` target-file entry.
- Do not touch `DataVisualizationShowcase.vue`, `KLineDemo.vue`, `MarketDataDemo.vue`, `SkeletonUsage.vue`, `SmartDataSourceTest.vue`, or `StockAnalysisDemo.vue`.

## Required Execution Gates

- GitNexus impact for `ArtDecoTest.vue` before moving the file.
- Exact active-reference search after the move.
- `npm run lint:artdeco:changed` or a targeted equivalent proving the package script remains syntactically valid after removing the target-file segment.
- `openspec validate update-frontend-view-governance --strict`.
- Markdown governance gate for the archive README, execution report, and `tasks.md`.
- `git diff --cached --name-status`.
- `git diff --cached --check`.
- `gitnexus_detect_changes(scope="staged")`.

## Decision

This candidate is ready for an explicit execution decision. It is smaller than the other remaining guarded root demo pages because it has a single direct package guard and no discovered active route, menu, package target beyond that guard, or direct Vue test owner.
