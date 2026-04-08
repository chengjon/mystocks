# Documentation Family Wave 2

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/documentation/` 导航暴露面的第二轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/documentation/` 导航暴露面的第二轮 bounded 收口。

## Why

- `docs/guides/documentation/` 在 wave 1 后已不再承担 governance trunk
- 但 `docs/INDEX.md` 仍把整组 specialized methodology guides 平铺为根导航叶子
- 这会让 supporting/reference guides 看起来像主入口，而不是 family 内部二级资料

## Changes

- 收薄 `docs/INDEX.md` 中 Documentation family 的根导航
- 保留以下优先入口：
  - `guides/documentation/INDEX.md`
  - `guides/documentation/CANONICAL_TRUNK_ADMISSION_GUIDE.md`
  - `guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md`
- 其余专题指南统一回收到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/overview/documentation-system.md`
- family transition index:
  - `docs/guides/documentation/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已清理过度暴露
- retention duty:
  - specialized methodology guides 仍保留为 supporting/reference docs

## Expected Effect

- 根导航不再把 documentation family 的 supporting leaf docs 错看成主入口
- reader routing 更符合 trunk-first
- 后续若这些 methodology guides 的 inbound links 继续下降，可再逐份评估 archive/delete
