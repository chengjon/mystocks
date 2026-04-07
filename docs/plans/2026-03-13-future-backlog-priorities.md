# Future Backlog Priorities

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **日期**: 2026-03-13
> **状态**: 候选任务池
> **适用范围**: 当前文档治理基线、Web / Data-DB / API 三条 worker 线完成后的后续规划

---

## 背景

当前项目已经明确拆出了三条并行主线：

- Web / ArtDeco 页面优化与测试
- Data / DB 盘点、清理与优化
- API 可用性与映射核查

在这些任务之外，项目仍存在若干系统性短板。这些短板不是单一页面、单一接口或单一数据源问题，而是会反复影响未来每一轮开发、排障、验收和协作效率的底层问题。

本任务池用于沉淀后续中长期改进方向，并为后续 OpenSpec proposal 提供排序基线。

## 排序原则

优先级由以下维度综合决定：

1. **收益面**：是否能降低多个模块的长期维护成本
2. **复用性**：是否能成为后续所有任务的公共基础设施
3. **风险面**：是否在当前架构下容易反复引发误判或回归
4. **实施成本**：投入是否与收益成正比
5. **依赖顺序**：是否是其他任务的前置条件

---

## P0 候选任务

### 1. Unify Runtime Truth

- **建议 change-id**: `unify-runtime-truth`
- **优先级**: P0
- **预估工作量**: L（5-8 人日）
- **目标**:
  - 统一 PM2 / Docker / `.env` / 端口 / health check 的真值来源
  - 明确 dev / test / prod 的运行口径
  - 建立一键运行验证和依赖检查入口
- **主要产出**:
  - 运行时真值文档
  - 端口和服务依赖矩阵
  - 健康检查与启动验证脚本
- **依赖**:
  - Data / DB 盘点结果
  - 当前主线运行配置现状
- **为什么优先**:
  - 这是所有 worker 线的共同地基
  - 当前“能不能跑、到底怎么跑”的口径不够统一

### 2. Generate Contract-Driven API Clients

- **建议 change-id**: `generate-contract-driven-api-clients`
- **优先级**: P0
- **预估工作量**: L（5-8 人日）
- **目标**:
  - 将 OpenAPI / 路由真值和前端类型、客户端调用打通
  - 降低 `verified/pending` 依赖人工维护的比例
  - 建立契约变更后前端自动发现字段不一致的链路
- **主要产出**:
  - 前端类型生成方案
  - API client 生成或收敛方案
  - CI 契约校验链路
- **依赖**:
  - API 可用性矩阵输出
  - 路由和 OpenAPI 真值收敛
- **为什么优先**:
  - 如果这条线不做，API 真值盘点会变成一次性劳动

### 3. Govern Test Layer Boundaries

- **建议 change-id**: `govern-test-layer-boundaries`
- **优先级**: P0
- **预估工作量**: M（3-5 人日）
- **目标**:
  - 重整 unit / integration / contract / e2e 的职责边界
  - 降低重复覆盖和低信噪比测试
  - 建立最小充分测试集
- **主要产出**:
  - 测试分层规范
  - 测试入口与职责映射
  - 回归定位推荐链路
- **依赖**:
  - Web / API 当前测试现状
- **为什么优先**:
  - 测试数量已经不少，但判别力和层次边界还可以进一步收敛

---

## P1 候选任务

### 4. Refactor Large Files By Domain

- **建议 change-id**: `refactor-large-files-by-domain`
- **优先级**: P1
- **预估工作量**: XL（8-12 人日）
- **目标**:
  - 收敛超大文件和职责混杂模块
  - 按 `FUNCTION_TREE` 和领域边界拆分
  - 降低改动 blast radius
- **主要产出**:
  - 超大文件清单
  - 拆分计划
  - 重点文件拆分与验证
- **依赖**:
  - FUNCTION_TREE 领域边界
  - Data / DB 和 API 盘点结论
- **为什么重要**:
  - 当前历史积累明显，后续会持续推高维护成本

### 5. Baseline Technical Debt Metrics

- **建议 change-id**: `baseline-technical-debt-metrics`
- **优先级**: P1
- **预估工作量**: M（3-5 人日）
- **目标**:
  - 将 mock-debt、type-debt、api-debt、navigation-debt 统一基线化
  - 区分新增债务和历史债务
  - 为每周/每 PR 提供增量视图
- **主要产出**:
  - 技术债分类规范
  - 基线文件
  - 统计或对比脚本
- **依赖**:
  - Web / API / Data-DB 各线产出的现状数据
- **为什么重要**:
  - 目前技术债信息很多，但尚未完全形成稳定治理机制

### 6. Improve Observability Runbooks

- **建议 change-id**: `improve-observability-runbooks`
- **优先级**: P1
- **预估工作量**: M（3-5 人日）
- **目标**:
  - 完善 Request ID、前后端日志、接口调用和数据库问题的关联排障能力
  - 建立常见故障 runbook
  - 统一页面故障降级和健康提示
- **主要产出**:
  - 观测性改进清单
  - 运行与排障 runbook
  - 页面级降级策略说明
- **依赖**:
  - 运行时真值统一任务优先完成更好
- **为什么重要**:
  - 当前项目已有监控，但“怎么快速定位问题”仍然偏经验驱动

---

## P2 候选任务

### 7. Link Function Tree With Code Graph

- **建议 change-id**: `link-function-tree-with-code-graph`
- **优先级**: P2
- **预估工作量**: L（5-8 人日）
- **目标**:
  - 让 `FUNCTION_TREE` 与 GitNexus / 代码图谱形成双向校验
  - 自动发现过期入口、缺测试入口、错误归属
- **主要产出**:
  - 功能树校验规则
  - 代码图谱映射规范
  - 自动校验脚本或报告
- **依赖**:
  - 文档治理基线稳定
  - FUNCTION_TREE 已成为稳定真值源
- **为什么重要**:
  - 这会把功能树从文档提升为治理基础设施

### 8. Standardize Safe Cleanup Workflow

- **建议 change-id**: `standardize-safe-cleanup-workflow`
- **优先级**: P2
- **预估工作量**: M（3-5 人日）
- **目标**:
  - 将“未引用不等于可删除”的规则工具化
  - 删除前自动检查功能树归属、路由引用、动态导入和兼容职责
- **主要产出**:
  - 清理/删除流程模板
  - 风险分级规则
  - 删除前检查清单或脚本
- **依赖**:
  - FUNCTION_TREE 与功能状态维护稳定
- **为什么重要**:
  - 项目历史积累较重，未来清理动作的误伤风险很高

---

## 建议启动顺序

### 第一梯队

1. `unify-runtime-truth`
2. `generate-contract-driven-api-clients`
3. `govern-test-layer-boundaries`

### 第二梯队

4. `refactor-large-files-by-domain`
5. `baseline-technical-debt-metrics`
6. `improve-observability-runbooks`

### 第三梯队

7. `link-function-tree-with-code-graph`
8. `standardize-safe-cleanup-workflow`

---

## 并行建议

- P0 任务中一次最多并行 2 条
- 推荐并行组合：
  - `unify-runtime-truth`
  - `govern-test-layer-boundaries`
- `generate-contract-driven-api-clients` 更适合在 API 可用性核查线收口后启动
- P1 与 P2 任务不建议在当前三条 worker 线尚未完成时抢跑

---

## 使用建议

- 该文档不是审批文件，而是候选任务池与排序基线
- 任一任务启动前仍需走 OpenSpec proposal / design / tasks 流程
- 若现有三条 worker 线输出了新的事实依据，应回到本页调整优先级和工作量估算

---

## 相关文档

- [FUNCTION_TREE](../FUNCTION_TREE.md)
- [AI Quick Start](../guides/ai-tools/AI_QUICK_START.md)
- [Function Tree Doc Routing Design](./2026-03-12-function-tree-doc-routing-design.md)
- [Parallel Worktree Allocation Design](./2026-03-12-parallel-worktree-allocation-design.md)
