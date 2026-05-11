# Frontend Data Visualization Showcase Archive

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `DataVisualizationShowcase.vue` | `web/frontend/src/views/DataVisualizationShowcase.vue` | `archive-candidate/demo-sandbox` | Canonical chart, market, data, and ArtDeco visualization assets remain active | No active router/menu owner found; page was a standalone visualization showcase. |
| `DataVisualizationShowcase.scss` | `web/frontend/src/views/styles/DataVisualizationShowcase.scss` | `demo-local-style` | Archived with owning demo page | Imported only by `DataVisualizationShowcase.vue`; no separate active owner found. |

## Retired Direct Guards

The archive batch also retired only these direct guards:

- `node scripts/check-artdeco-tokens.js --target-file src/views/DataVisualizationShowcase.vue --changed-from-git`
- `'src/views/DataVisualizationShowcase.vue'` from `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-24.spec.ts`

## Restore Rule

If a future change needs this showcase, restore the page and local style together, then define a formal route or documented demo entry, owner, and active test coverage.
