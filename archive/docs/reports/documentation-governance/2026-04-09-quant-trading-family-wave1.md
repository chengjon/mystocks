# Quant Trading Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/quant-trading/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/quant-trading/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/quant-trading/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍将该 family 的阶段完成报告、历史实现计划和总览入口全部平铺暴露
- 这会让历史 phase 文档看起来与总览入口同优先级

## Changes

- 将 `docs/guides/quant-trading/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Quant Trading family 的根导航
- 根导航现在优先保留：
  - `guides/quant-trading/INDEX.md`
  - `guides/quant-trading/algorithm_system_usage_guide.md`
  - `guides/quant-trading/risk_management_system_plan.md`
  - `Supporting Guides` -> `guides/quant-trading/INDEX.md`
- 将 Phase 4、Phase 5 完成报告和历史实现计划收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/quant-trading/algorithm_system_usage_guide.md`
  - `docs/guides/quant-trading/risk_management_system_plan.md`
- family transition index:
  - `docs/guides/quant-trading/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 phase/historical quant-trading leaf docs 的直接暴露
- retention duty:
  - phase 完成报告与历史实现计划继续保留为 supporting/reference docs

## Expected Effect

- 根导航不再把量化交易 family 的历史 phase 文档误读为主入口
- 读者先进入系统总览与风险管理方案，再按需查看阶段完成报告和历史实现计划
- 后续若历史 phase 文档入链继续下降，可继续逐份评估 archive/delete
