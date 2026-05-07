# Frontend Entry Point Truth Source

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

**Created:** 2026-04-07
**Phase:** 03-structural-consolidation (Plan 03-01, Task 1)

## Canonical Entry

**`main-standard.ts`** — loaded by `index.html` line 67:
```html
<script type="module" src="/src/main-standard.ts"></script>
```

`main-standard.ts` is the current active browser runtime entry. It creates the Vue app with: createApp, createPinia, router, App.vue, core style imports, service worker registration, security init, version notification, and session restore.

## Historical Variants

- No active `web/frontend/verify-mount.js` consumer exists in the current tree.
- `src/main.js` is not present as a live source file in the current tree.
- Historical `main*.js/ts` variants are retained under `src/_entry-archive/` as archive assets, not current runtime entries.

## Entry Variant Inventory

| # | File | Consumers | Safe to Archive? |
|---|------|-----------|-----------------|
| 1 | `main-standard.ts` | index.html (canonical entry) | NO |
| 2 | `_entry-archive/main.js` | retained archive asset | ALREADY ARCHIVED |
| 3 | `_entry-archive/main-debug.js` | retained archive asset | ALREADY ARCHIVED |
| 4 | `_entry-archive/main-original.js` | retained archive asset | ALREADY ARCHIVED |
| 5 | `_entry-archive/main-simplified.js` | retained archive asset | ALREADY ARCHIVED |
| 6 | `_entry-archive/main-test.js` | retained archive asset | ALREADY ARCHIVED |
| 7 | `_entry-archive/main-enhanced.ts` | retained archive asset | ALREADY ARCHIVED |
| 8 | `_entry-archive/main-minimal.ts` | retained archive asset | ALREADY ARCHIVED |

## Current Boundary

- `main-standard.ts` is both the canonical entry and the active runtime entry.
- `_entry-archive/*` files are not evidence of active duplicate runtime paths.
- Historical docs that still mention `src/main.js` or `verify-mount.js` should be treated as archived context, not current repo-truth.

## Backup Files

- `App.vue.backup` — stale backup, audit consumers before deletion
- `_entry-archive/main.js.backup` — retained archive backup, audit consumers before deletion if future cleanup is approved

## Decision

- Keep `main-standard.ts` as the only current browser entry
- Treat `_entry-archive/` as historical retained assets, not active runtime duplicates
- Do not use old `main.js` / `verify-mount.js` claims as the basis for dead-code decisions
