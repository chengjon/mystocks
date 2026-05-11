# Frontend OpenStock Root Duplicate Archive

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `OpenStockDemo.vue` | `web/frontend/src/views/OpenStockDemo.vue` | `archive-candidate/root-duplicate-shell` | `web/frontend/src/views/demo/OpenStockDemo.vue` as retained demo owner | No active router/menu/config/package owner found; root shell duplicated the demo-directory OpenStock shell while reusing the same `views/demo/openstock/**` child tree. |

## Retained Active Assets

The following files remain active demo assets and were not moved in this batch:

- `web/frontend/src/views/demo/OpenStockDemo.vue`
- `web/frontend/src/views/demo/openstock/config.ts`
- `web/frontend/src/views/demo/openstock/components/index.ts`
- `web/frontend/src/views/demo/openstock/components/*.vue`

## Restore Rule

If a future change restores root-level OpenStock demo routing, first define route ownership, menu placement, canonical data truth, request provenance, and active test coverage. Do not restore the root shell while `web/frontend/src/views/demo/OpenStockDemo.vue` remains the demo-directory owner.
