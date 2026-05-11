# Frontend View Root Sandbox Archive

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `PageTitleDemo.vue` | `web/frontend/src/views/PageTitleDemo.vue` | `archive-candidate/root-demo-sandbox` | `no-successor-needed` | No active router/menu/pageConfig/source/test/package owner found during A1-minimal preflight. |

## Validation

- Final pre-move active reference grep found only the source file itself.
- Post-move active reference grep must return no `PageTitleDemo` references under `web/frontend/src`, `web/frontend/tests`, or `web/frontend/package.json`.
- `openspec validate update-frontend-view-governance --strict` must pass.
