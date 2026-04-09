# TypeScript Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/typescript/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/typescript/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/typescript/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把 quickstart、用户手册、培训材料、排障指南、修复方案和历史实施计划全部平铺暴露
- 这会让专项修复材料和历史方案看起来与核心上手文档同优先级

## Changes

- 将 `docs/guides/typescript/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 TypeScript family 的根导航
- 根导航现在优先保留：
  - `guides/typescript/INDEX.md`
  - `guides/typescript/Typescript_QUICKSTART.md`
  - `guides/typescript/Typescript_USER_GUIDE.md`
  - `guides/typescript/Typescript_BEST_PRACTICES.md`
  - `guides/typescript/Typescript_CONFIG_REFERENCE.md`
  - `Supporting Guides` -> `guides/typescript/INDEX.md`
- 将培训、排障、修复和历史扩展系统方案收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/typescript/Typescript_QUICKSTART.md`
  - `docs/guides/typescript/Typescript_USER_GUIDE.md`
  - `docs/guides/typescript/Typescript_BEST_PRACTICES.md`
  - `docs/guides/typescript/Typescript_CONFIG_REFERENCE.md`
- family transition index:
  - `docs/guides/typescript/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 TypeScript family 训练/方案类 leaf docs 的直接暴露
- retention duty:
  - 培训、排障、修复和扩展系统方案继续保留为 supporting/reference docs

## Expected Effect

- 根导航不再把 TypeScript family 的专项修复或历史方案误读为主入口
- 读者先进入上手、用户手册、最佳实践和配置参考，再按需查看 API、培训、排障与历史方案
- 后续若历史方案和专项修复材料入链继续下降，可继续逐份评估 archive/delete
