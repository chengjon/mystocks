# Buger Guide Family

> **导航说明**:
> 本文件是 `docs/guides/buger/` 的 transition index，不是仓库共享规则、当前 BUGer 接入边界或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及当前接入实现状态，再结合根目录 `AGENTS.md` 与实际代码核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留 BUGer 服务接入、连接排障与客户端集成说明，不承担仓库级 trunk。推荐阅读顺序：

1. [`B项目接入指南.md`](./B项目接入指南.md)
2. [`客户端连接指南.md`](./客户端连接指南.md)
3. 再按需进入客户端集成说明

## Active Supporting Guides

- [`B项目接入指南.md`](./B项目接入指南.md)
  - BUGer 服务接入总览
- [`客户端连接指南.md`](./客户端连接指南.md)
  - 客户端连接配置与验证指南

## Retained Specialized References

- [`客户端集成指南.md`](./客户端集成指南.md)
  - BUGer 客户端集成细节说明

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只暴露接入总览和连接指南，客户端集成细节统一通过本 index 进入
- 若后续客户端集成细节文档入链继续下降，再按 bounded batch 单独评估 archive/delete
