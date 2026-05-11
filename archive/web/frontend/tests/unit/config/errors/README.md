# Archived Error Demo Shell Guards

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

These Vitest specs formerly guarded `web/frontend/src/views/errors/*` demo shells. They were archived with A2 because the guarded views had no active route, menu, pageConfig, or runtime owner.

Archived specs:

- `errors-mainline-gate.spec.ts`
- `errors-forbidden-style-source.spec.ts`
- `errors-network-style-source.spec.ts`
- `errors-service-unavailable-style-source.spec.ts`

Do not restore these specs without restoring or replacing the corresponding active error-route contract.
