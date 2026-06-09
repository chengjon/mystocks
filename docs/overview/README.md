# Overview Transition Index

> **导航说明**:
> 本文件是 `docs/overview/` 的 transition index，用于把读者导向当前有效的 trunk 与少量仍保留的 supporting overview 文档。
> 它不再承担整个 `docs/` 树的总入口角色；仓库文档主干入口已上移到 [`docs/README.md`](../README.md)。

## Start Here

- 仓库级共享规则与审批门禁：
  [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)
- 文档系统 trunk map：
  [`documentation-system.md`](documentation-system.md)
- 当前能力真相：
  [`openspec/specs/`](../../openspec/specs)
- 已批准但未完成的变更：
  [`openspec/changes/`](../../openspec/changes)

## Retained Overview Documents

- [`项目总览.md`](项目总览.md)
- [`开发与安全规范.md`](开发与安全规范.md)
- [`开发工具链指南.md`](开发工具链指南.md)
- [`CURRENT_STATUS.md`](CURRENT_STATUS.md)
- [`archived.md`](archived.md)

## Compatibility Notes

- [`INDEX.md`](INDEX.md) 仅作为旧链接兼容索引保留
- [`agents.md`](agents.md)、[`claude.md`](claude.md) 与 [`initialization-prompt.md`](initialization-prompt.md) 仍可作为 onboarding supporting docs 使用
- 若某个 overview 文档与 trunk 冲突，以 trunk 为准，而不是回头扩写 overview 根索引

## Governance Status

- `docs/overview/README.md` 不再模拟 `docs/` 根入口
- `docs/overview/` 现在只承担项目总览与 onboarding supporting surface
- 后续 cleanup 应继续收缩重复入口，而不是重新堆积全量索引
