# Frontend View Governance A4 OpenStock Root Duplicate Archive Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: execution record for `A4-openstock-demo-root-duplicate-archive-prep`.

## Approval And Scope

Approved action:

- Move only `web/frontend/src/views/OpenStockDemo.vue` into governed archive.
- Retain `web/frontend/src/views/demo/OpenStockDemo.vue`.
- Retain all `web/frontend/src/views/demo/openstock/**` child assets.
- Do not update router/menu/package/test entries because no active direct owner was found for the root duplicate shell.

## Impact And Reference Checks

GitNexus impact before move:

- Target: `OpenStockDemo.vue`
- Direction: upstream
- Risk: LOW
- Direct dependents: 0
- Affected processes: 0

Pre-move active reference checks:

```text
rg -n "OpenStockDemo|src/views/OpenStockDemo|@/views/OpenStockDemo|../OpenStockDemo\\.vue|./OpenStockDemo\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json openspec/changes/update-frontend-view-governance docs/reports/quality/myweb-audit --glob '!**/.claude/**'
rg -n "OpenStockDemo" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config web/frontend/package.json --glob '!**/.claude/**'
```

Result:

- No active router/menu/config/package reference to root `web/frontend/src/views/OpenStockDemo.vue`.
- Active OpenStock style-source guard reads `src/views/demo/OpenStockDemo.vue`, not the archived root shell.
- Remaining `OpenStockDemo` references are governance docs, historical inventory/guard-map records, `views/demo/OpenStockDemo.vue`, and `views/demo/openstock/**` child references.

## Files Moved

| Original path | Archive path |
| --- | --- |
| `web/frontend/src/views/OpenStockDemo.vue` | `archive/web/frontend/src/views/root-sandbox/openstock-demo/OpenStockDemo.vue` |

## Files Added

| File | Purpose |
| --- | --- |
| `archive/web/frontend/src/views/root-sandbox/openstock-demo/README.md` | Governed archive manifest and restore rule |

## Retained Files

| File group | Reason retained |
| --- | --- |
| `web/frontend/src/views/demo/OpenStockDemo.vue` | Temporary retained OpenStock demo owner and direct style-source guard target |
| `web/frontend/src/views/demo/openstock/**` | Child component tree still has direct style-source guards and possible absorption value |

## Cleanup Decision

This is an archive move, not deletion. The archived root shell is classified as `archive-candidate/root-duplicate-shell` with successor `web/frontend/src/views/demo/OpenStockDemo.vue`.

No child components were archived because they contain reusable feature ideas for market search, quotes, news, watchlist, K-line, and heatmap surfaces.

## Post-Move Checks

Executed checks:

| Check | Result |
| --- | --- |
| `rg -n "src/views/OpenStockDemo|@/views/OpenStockDemo|../OpenStockDemo\\.vue|./OpenStockDemo\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'` | Returned only `tests/unit/config/openstock-demo-style-source.spec.ts`, which targets retained `src/views/demo/OpenStockDemo.vue` |
| `rg -n "OpenStockDemo" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config web/frontend/package.json --glob '!**/.claude/**'` | No matches |
| `openspec validate update-frontend-view-governance --strict` | Passed |
| Markdown governance gate for this report, archive README, and `tasks.md` | Passed, 3 files, 0 errors |
| `npx vitest run tests/unit/config/openstock-demo-style-source.spec.ts tests/unit/config/openstock-components-mainline-gate.spec.ts tests/unit/config/demo-mainline-gate.spec.ts` | Passed, 3 files, 3 tests |
| `git diff --check` for changed paths | Passed |

Staged GitNexus detection remains required immediately before commit after the intended file set is staged.
