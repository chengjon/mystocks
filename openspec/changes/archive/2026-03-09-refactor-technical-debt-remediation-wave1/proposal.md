## Why

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


最新技术债检查显示，仓库已具备部分质量门能力，但存在显著不一致：
- 前端 build 对 type-check 存在放行路径（例如 `vue-tsc --noEmit || true`）
- Type suppression（`@ts-ignore`/`as any`）与占位实现（TODO/FIXME/pass/mock）在关键路径累积
- 测试存在有效性债务（`assert True` 占位、长期 skip/xfail）

现有技术债提案要么偏治理框架（`tech-debt-governance-2026q1`），要么范围过大（`consolidate-technical-debt-remediation`），缺少一个可在 1~2 个迭代内执行并验收的“波次治理”提案。

## What Changes

本变更在 `code-quality` 能力上新增/强化“可执行治理门禁”，并形成三阶段修复排期：

1. Stage A（止血）：质量信号对齐 + no-new-debt
   - 统一 build/type-check/test 的门禁语义
   - 冻结技术债基线，新增债务不允许上升

2. Stage B（降风险）：优先消化高风险存量
   - 关键路径 suppression、placeholder、无效测试先清理

3. Stage C（机制化）：长期治理自动化
   - 例外审批（TTL/owner/issue）与过期自动失效
   - 周报/KPI 常态化追踪

## Impact

- **受影响能力**：`code-quality`
- **受影响范围**：CI 质量门、前后端关键路径修复计划、测试有效性治理
- **运行时行为**：不直接引入业务功能变更，主要是工程治理与交付质量约束
- **协作影响**：需要 Tech Lead + 模块负责人参与例外审批与周度治理复盘

## Related Changes

- `tech-debt-governance-2026q1`（治理框架）
- `consolidate-technical-debt-remediation`（历史大盘治理）
