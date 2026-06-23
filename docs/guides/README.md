# Guides Transition Index

> **导航说明**:
> 本文件是 `docs/guides/` 的 transition index，不是仓库共享规则、当前实现状态或单一 canonical trunk。
> Guides 目录按 concern 分流；当前主干入口仍是 [`docs/README.md`](../README.md)。

## How To Use Guides

按 concern 进入对应 guide family，而不是把 `docs/guides/` 当成统一真相层：

- AI / agent workflows:
  - [`ai-tools/`](ai-tools)
  - [`superpowers/`](superpowers)
- frontend / web:
  - [`frontend/`](frontend)
  - [`web/`](web)
  - [`typescript/`](typescript)
- operational workflows:
  - [`pm2/`](pm2)
  - [`openspec-cmd/`](openspec-cmd)
  - [`multi-cli-tasks/`](multi-cli-tasks)
  - [`onboarding/`](onboarding)
- governance helpers:
  - [`governance/`](governance)
  - [`documentation/`](documentation)

## Canonical Targets

这些绝对路径用于 repository-hygiene 断言和 AI 导航对账；读者仍应通过上方 family 链接进入具体文档。

- Repository docs trunk: `/opt/claude/mystocks_spec/docs/README.md`
- AI / agent workflows: `/opt/claude/mystocks_spec/docs/guides/ai-tools/`
- Frontend guides: `/opt/claude/mystocks_spec/docs/guides/frontend/`
- Web guides: `/opt/claude/mystocks_spec/docs/guides/web/`
- TypeScript guides: `/opt/claude/mystocks_spec/docs/guides/typescript/`
- PM2 guides: `/opt/claude/mystocks_spec/docs/guides/pm2/`
- OpenSpec command guides: `/opt/claude/mystocks_spec/docs/guides/openspec-cmd/`
- Multi CLI task guides: `/opt/claude/mystocks_spec/docs/guides/multi-cli-tasks/`
- Onboarding guides: `/opt/claude/mystocks_spec/docs/guides/onboarding/`
- Governance guides: `/opt/claude/mystocks_spec/docs/guides/governance/`
- Documentation guides: `/opt/claude/mystocks_spec/docs/guides/documentation/`

## Root-Level Compatibility Entries

以下 root-level guide files 仍保留为 compatibility/supporting entries，不构成并行 trunk：

- [`ARTDECO_MASTER_INDEX.md`](ARTDECO_MASTER_INDEX.md)
- [`ARTDECO_COMPONENT_GUIDE.md`](ARTDECO_COMPONENT_GUIDE.md)
- [`frontend-structure.md`](frontend-structure.md)
- [`web-redesign-requirements.md`](web-redesign-requirements.md)

## Governance Status

- `docs/guides/README.md` 和 `docs/guides/INDEX.md` 已从 broad catch-all index 收敛为 transition index
- `docs/guides/` 不再被视为单一 canonical docs trunk
- 后续 cleanup 应按 family 执行，而不是对整棵 guides 树一次性删除
