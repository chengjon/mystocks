# Frontend Market Data Demo Archive

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `MarketDataDemo.vue` | `web/frontend/src/views/MarketDataDemo.vue` | `archive-candidate/demo-sandbox` | Canonical `/market/*` and `/data/*` routes remain active | No active router/menu/package/test owner found; page was a root-level demo for unified API client usage. |
| `useMarketData.js` | `web/frontend/src/composables/useMarketData.js` | `demo-local-composable` | Archived with owning demo page | Only imported by `MarketDataDemo.vue`; no independent active owner found. |

## Restore Rule

If a future change needs this demo, restore the page and its local composable together, then define a formal route or documented demo entry, owner, and active test coverage.
