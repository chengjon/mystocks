# Mock Data Guide Family

> **导航说明**:
> 本文件是 `docs/guides/mock-data/` 的 transition index，不是仓库共享规则、当前 trunk map 或当前实现状态的唯一事实来源。
> 若需确认文档系统主干与 reader routing，请优先阅读 [`docs/overview/documentation-system.md`](../../overview/documentation-system.md)；若涉及审批门禁、删除判定或共享治理规则，请回到 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md)。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于 Mock/Real 数据切换专题说明，不承担仓库级治理 trunk。推荐阅读顺序：

1. [`MOCK_DATA_USAGE_RULES.md`](./MOCK_DATA_USAGE_RULES.md)
2. [`MOCK_REAL_DATA_SWITCHING_GUIDE.md`](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
3. [`MOCK_REAL_DATA_INDEX.md`](./MOCK_REAL_DATA_INDEX.md)
4. 再按需进入历史路线图、历史计划和旧快照说明

## Active Supporting Guides

- [`MOCK_DATA_USAGE_RULES.md`](./MOCK_DATA_USAGE_RULES.md)
  - 当前 Mock 使用边界、允许/禁止场景与专题执行细则
- [`MOCK_REAL_DATA_SWITCHING_GUIDE.md`](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
  - 当前 Mock/Real 数据切换、readiness 与验证路径主指南
- [`MOCK_REAL_DATA_INDEX.md`](./MOCK_REAL_DATA_INDEX.md)
  - family 内的专题导航与按角色阅读入口

## Retained Historical References

以下文件继续保留在 `mock-data/` family 中，但作为历史参考或兼容快照使用，不应被误读为当前主入口：

- [`REAL_DATA_INTEGRATION_PRINCIPLES.md`](./REAL_DATA_INTEGRATION_PRINCIPLES.md)
  - 历史架构原则参考
- [`REAL_DATA_INTEGRATION_ROADMAP.md`](./REAL_DATA_INTEGRATION_ROADMAP.md)
  - 历史路线图
- [`PHASE_2_REAL_DATA_INTEGRATION_PLAN.md`](./PHASE_2_REAL_DATA_INTEGRATION_PLAN.md)
  - 历史实施计划
- [`README_MOCK_DATA.md`](./README_MOCK_DATA.md)
  - 旧版 Mock 系统说明快照，保留作历史背景参考，不再作为当前入口

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只应暴露当前核心入口，其余历史/计划/旧快照说明统一通过本 index 进入
- 若后续历史文档的 inbound links 继续下降，再按 bounded batch 单独评估 archive/delete
