# ArtDeco Components Catalog
## 历史兼容组件目录入口

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文件保留为历史兼容入口，不再维护为当前权威组件目录。

## 当前应查看的文档

- [当前组件全景目录](/opt/claude/mystocks_spec/web/frontend/ARTDECO_COMPONENTS_CATALOG.md)
- [组件开发指南](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_COMPONENT_GUIDE.md)
- [统一规格](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md)

## 为什么降级

历史上 `docs/guides/web/ART_DECO_COMPONENTS_CATALOG.md` 记录过一版组件统计与分类，但它已经和当前仓库结构不一致。

当前组件体系必须区分：

- `src/components/artdeco/**` 的 reusable assets
- `views/artdeco-pages/components/` 的 page-level shared fragments
- `views/artdeco-pages/*-tabs/` 的 domain tab blocks

因此，当前准确库存与分类只认 `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`。

## 状态

- 2026-04-01 起，本文件仅作为历史兼容入口保留。
- 若外部文档仍引用本文件，请逐步迁移到当前组件全景目录。
