# MyStocks ArtDeco Available Components Summary

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文件保留为历史兼容摘要，不再维护为权威组件统计清单。

## 当前使用方式

如果你要查“现在仓库里到底有哪些 ArtDeco 组件 / 页面块”，请直接看：

- [ARTDECO_COMPONENTS_CATALOG](/opt/claude/mystocks_spec/web/frontend/ARTDECO_COMPONENTS_CATALOG.md)
- [ARTDECO_COMPONENT_GUIDE](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_COMPONENT_GUIDE.md)
- [ARTDECO_FINTECH_UNIFIED_SPEC](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md)

## 为什么本文件降级为兼容摘要

历史上它汇总过多个 ArtDeco 文档中的组件数量，但这些数字已经不再代表当前仓库现实。

当前主口径已经迁移到：

- `src/components/artdeco/**` 的 reusable assets
- `views/artdeco-pages/components/` 的 page-level shared fragments
- `views/artdeco-pages/*-tabs/` 的 domain tab blocks

因此，本文件不再尝试给出“总组件数”。

## 当前建议

- 需要**准确库存**：看 `ARTDECO_COMPONENTS_CATALOG.md`
- 需要**目录放置规则**：看 `ARTDECO_COMPONENT_GUIDE.md`
- 需要**整体架构边界**：看 `ARTDECO_FINTECH_UNIFIED_SPEC.md`
- 需要**运行时视角**：看 `ArtDeco_System_Architecture_Summary.md`

## 状态

- 2026-04-01 起，本文件仅作为历史兼容入口保留。
- 若未来仍需做组件统计，请直接从源码重新盘点，不要复用本文件中的旧数字。
