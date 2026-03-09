# Frontend Common Types Splitting Design

**Date:** 2026-03-07
**Scope:** `web/frontend/src/api/types/common/all.ts` structural refactor

## Context

`web/frontend/src/api/types/common/all.ts` 当前超过 2200 行，内含 271 个 `export interface/type`，已经成为前端类型入口的单点聚合文件。虽然 `web/frontend/src/api/types/common.ts` 已开始转向分域导出，但 `all.ts` 仍保留大量内联定义，导致审查报告继续将其判定为超大文件与类型职责过度集中。

现有分域文件已经存在：
- `web/frontend/src/api/types/domains/system-base.ts`
- `web/frontend/src/api/types/domains/market-data.ts`
- `web/frontend/src/api/types/domains/trading-ops.ts`
- `web/frontend/src/api/types/domains/strategy-types.ts`

其中只覆盖了 133 个类型，仍有约 140 个类型停留在 `all.ts` 中。

## Decision

采用“分域下沉 + 兼容层保留”的方案：
1. 将 `all.ts` 中剩余内联类型全部迁移到分域文件；
2. 复用既有 4 个分域文件，必要时新增少量分域文件承接剩余类型；
3. 将 `all.ts` 改造成纯兼容层，仅保留类型重导出，不再定义任何内联类型；
4. `common.ts` 作为主入口，继续按分域重导出，避免新代码直接依赖 `all.ts`；
5. 保持现有导入兼容，避免本轮触发大规模调用方改造。

## Domain Mapping

- **system-base**：统一响应、错误、分页、消息、订阅、用户资料、调度/任务状态等系统级契约
- **market-data**：行情、K线、公告、指标、资金流、龙虎榜、筹码、评分、监控摘要等市场与分析读模型
- **trading-ops**：账户、持仓、订单、成交、风险告警、组合、看板等交易与运营模型
- **strategy-types**：策略、回测、算法训练/预测、模型管理、特征生成、任务配置等策略与算法模型
- **monitoring-alerts**（新增）：备份/恢复、通知测试、监控汇总、调度控制等运维与告警模型

## Non-Goals

- 本轮不修复 `generated-types` 缺失导出导致的既有类型错误；
- 本轮不处理归档页面生命周期治理；
- 本轮不调整业务 API 调用层，只做类型结构重组与兼容层收敛。

## Safety Strategy

- 先写结构性测试，要求 `all.ts` 不再包含内联 `export interface/type`；
- 保留兼容层重导出，避免现有 `import type { X } from '@/api/types/common/all'` 失效；
- 使用 `vue-tsc --noEmit` 验证没有新增类型回归；
- 若出现问题，优先通过补充重导出或跨域类型引用修复，而不是回退到大文件。

## Validation

- `vitest`/结构测试：验证 `all.ts` 仅为兼容重导出层；
- `npm --prefix web/frontend run type-check`：验证结构性语法错误为 0，类型错误数不高于基线；
- 必要时补充消费侧单测，确认常用入口类型仍可导入。
