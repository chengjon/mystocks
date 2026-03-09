# Task Plan: 全仓代码精简（code-simplifier + planning-with-files）

## Goal
在不改变业务行为与对外契约的前提下，完成一次可落地、可回滚、可验证的全仓代码精简方案，优先收敛重复入口与历史兼容层。

## Phases
- [x] Phase 1: 规划与上下文建立
- [x] Phase 2: 只读分析（code-simplifier 全仓扫描）
- [x] Phase 3: 分阶段优化方案设计（含验收/回滚）
- [x] Phase 4: 交付执行清单

## Key Questions
1. 哪些精简项收益最高且行为风险最低？
2. 哪些删除动作必须先做“调用迁移”再执行？
3. 用什么客观门禁证明“精简后等价可用”？

## Decisions Made
- 先做只读分析，避免盲目改动。
- 采用“入口收敛 -> 调用迁移 -> 删除冗余”顺序。
- 把工作拆分为 P0/P1/P2，先 Quick Wins 再中期重构。
- 根据审查反馈补齐四项关键缺口：
  - Frontend canonical client 先决策（`src/api/apiClient` vs `src/services/api-client`）再迁移；
  - 验收门禁对齐 baseline + PM2 + E2E；
  - stylelint 改为条件性门禁（待脚本化后再升级硬门禁）；
  - Backend legacy 扫描范围扩展到 `.old/.new/.bak/.backup*`。

## Errors Encountered
- 无实质性执行错误（本轮仅产出规划文档，不做代码变更）。

## Status
**In Progress** - Phase B 执行清单与 PR 拆分矩阵已落盘（`phase-b-execution-checklist.md`、`phase-b-pr-slices-and-validation-matrix.md`）；下一步进入 Batch 1A（`httpClient.js`）最小迁移实现并跑门禁。
