# Guides Transition Index

> **导航说明**:
> 本文件是 `docs/guides/` 的 transition index，不是仓库共享规则、当前实现状态或单一 canonical trunk。
> Guides 目录按 concern 分流；当前主干入口仍是 [`docs/README.md`](/opt/claude/mystocks_spec/docs/README.md)。

## How To Use Guides

按 concern 进入对应 guide family，而不是把 `docs/guides/` 当成统一真相层：

- AI / agent workflows:
  - [`ai-tools/`](/opt/claude/mystocks_spec/docs/guides/ai-tools/)
  - [`superpowers/`](/opt/claude/mystocks_spec/docs/guides/superpowers/)
- frontend / web:
  - [`frontend/`](/opt/claude/mystocks_spec/docs/guides/frontend/)
  - [`web/`](/opt/claude/mystocks_spec/docs/guides/web/)
  - [`typescript/`](/opt/claude/mystocks_spec/docs/guides/typescript/)
- operational workflows:
  - [`pm2/`](/opt/claude/mystocks_spec/docs/guides/pm2/)
  - [`openspec-cmd/`](/opt/claude/mystocks_spec/docs/guides/openspec-cmd/)
  - [`multi-cli-tasks/`](/opt/claude/mystocks_spec/docs/guides/multi-cli-tasks/)
  - [`onboarding/`](/opt/claude/mystocks_spec/docs/guides/onboarding/)
- governance helpers:
  - [`governance/`](/opt/claude/mystocks_spec/docs/guides/governance/)
  - [`documentation/`](/opt/claude/mystocks_spec/docs/guides/documentation/)

## Root-Level Compatibility Entries

以下 root-level guide files 仍保留为 compatibility/supporting entries，不构成并行 trunk：

- [`ARTDECO_MASTER_INDEX.md`](/opt/claude/mystocks_spec/docs/guides/ARTDECO_MASTER_INDEX.md)
- [`ARTDECO_COMPONENT_GUIDE.md`](/opt/claude/mystocks_spec/docs/guides/ARTDECO_COMPONENT_GUIDE.md)
- [`frontend-structure.md`](/opt/claude/mystocks_spec/docs/guides/frontend-structure.md)
- [`web-redesign-requirements.md`](/opt/claude/mystocks_spec/docs/guides/web-redesign-requirements.md)

## Governance Status

- `docs/guides/README.md` 和 `docs/guides/INDEX.md` 已从 broad catch-all index 收敛为 transition index
- `docs/guides/` 不再被视为单一 canonical docs trunk
- 后续 cleanup 应按 family 执行，而不是对整棵 guides 树一次性删除
