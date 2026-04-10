# Legacy Router Archive Strategy

> **历史文档说明**:
> 本文档用于完成 `govern-phase3-phase4-frontend-closure` 的任务 `2.2`，
> 把 `router/index.js*` 与 `phase4.routes.js` 从“状态标签”进一步收束为“归档策略”。
> 本文档不批准任何删除或移动动作，仍需遵守 `architecture/STANDARDS.md`。

**Generated:** 2026-04-07  
**Change:** `govern-phase3-phase4-frontend-closure`  
**Task:** `2.2 Produce and approve the legacy router archive strategy for router/index.js* and phase4.routes.js`

## 1. Strategy Goal

本批次只回答三个问题：

1. 哪些文件当前必须原位保留，不能先动
2. 哪些文件具备优先归档条件
3. 哪些文件必须等页面资产和文档真相一起收口后再处理

当前默认前提不变：

```text
web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

因此，以下 4 个文件都不是当前 runtime truth，但它们的退场条件并不相同。

## 2. File Classification Recap

| File | Lifecycle Status | Core Evidence |
|---|---|---|
| `web/frontend/src/router/index.js` | historical legacy router asset | 仍保存旧版 technical / monitoring 路由形态，且被大量历史文档写成“路由配置” |
| `web/frontend/src/router/index.js.clean` | historical broken backup / stale working copy | 文件结构损坏，不能作为可靠历史模板 |
| `web/frontend/src/router/index.js.backup-phase2.3` | historical backup | 文件名与内容都明确指向 Phase 2.3 备份 |
| `web/frontend/src/router/phase4.routes.js` | stale route asset | 未接入现役主链，且仍引用缺失页面 `StrategyMgmtPhase4.vue` |

## 3. Archive Strategy Matrix

| File | Immediate Action | Why Not Delete Now | Eventual Disposition | Required Gate Before Mutation |
|---|---|---|---|---|
| `src/router/index.js` | 原位保留，先去真相化 | 仍承载历史 route sample，且 monitoring / technical 历史目标要靠它做证据归类 | 与 `index.js.backup-phase2.3` 成组归档 | 完成 E3/E4 页面资产判定 + 历史文档去真相化 |
| `src/router/index.js.clean` | 标记为优先归档候选 | 虽已损坏，但仍应先保留一份审计证据，避免无痕删除 | 移入历史归档目录，不再与 canonical router 并列 | 确认无脚本/人工流程把它当模板使用 |
| `src/router/index.js.backup-phase2.3` | 原位保留，等待成组处理 | 是命名明确的历史备份，不宜早于 `index.js` 单独退场 | 与 `index.js` 一起归档为成组历史路由样本 | `index.js` 相同门禁；并同步收口 Phase 2.3 备份叙述 |
| `src/router/phase4.routes.js` | 条件保留，待 duplicate-page 收口 | 仍绑定 root `Phase4Dashboard` 历史入口语义，且引用缺失页面 | 在 E4 后转入单文件历史归档或附说明退役 | 完成 `Phase4Dashboard` / `StrategyMgmtPhase4` 去向判定 |

## 4. Recommended Archive Order

推荐的后续归档顺序如下：

1. **第一优先级：`index.js.clean`**
   - 原因：它不是主链、不是可靠备份、结构又已损坏
   - 适合最早从 `src/router/` 主目录移出

2. **第二优先级：`phase4.routes.js`**
   - 前提：`E4 duplicate-page retirement alignment` 已完成
   - 原因：它与 root `Phase4Dashboard` 的历史入口语义绑定，不能早于页面判定动作

3. **最后成组处理：`index.js` + `index.js.backup-phase2.3`**
   - 原因：这两份文件目前共同承担“旧主路由形态证据”的职责
   - 若只移动其中一份，会让历史证据链失衡

## 5. Mutation Rules

### 5.1 `index.js`

当前策略：

- 不删除
- 不单独归档
- 先把它从“疑似现役路由”降级为“历史样本”

前置门禁：

- 完成 monitoring 页面退场条件清单
- 完成 duplicate page 退场条件清单
- 清理把它写成“当前路由配置”的历史文档表述

### 5.2 `index.js.clean`

当前策略：

- 可列为最早归档候选
- 但必须保留一次完整审计记录

前置门禁：

- 确认仓库内无测试、脚本、说明文档把它当“可继续编辑的模板”
- 在归档说明中明确写明其“损坏工作副本”性质

### 5.3 `index.js.backup-phase2.3`

当前策略：

- 不单独先删
- 优先与 `index.js` 统一编目

前置门禁：

- 与 `index.js` 相同
- 另需处理历史报告中对 Phase 2.3 备份的引用

### 5.4 `phase4.routes.js`

当前策略：

- 暂不移动
- 先保留为 duplicate-page 审计的历史路由证据

前置门禁：

- 明确 `src/views/Phase4Dashboard.vue` 的最终生命周期
- 明确缺失页 `StrategyMgmtPhase4.vue` 是否正式废弃
- 确认无任何路由聚合、测试或运行链仍把它当活跃入口

## 6. Proposed Archive Shape

若后续审批通过，建议把这些文件移入单独历史目录，而不是继续放在 canonical router 同层：

```text
web/frontend/src/router/_history/
  index.js
  index.js.clean
  index.js.backup-phase2.3
  phase4.routes.js
  README.md
```

`README.md` 至少需要记录：

- 每个文件的生命周期标签
- 原始来源阶段
- 为什么保留
- 何时不再作为当前实现真相源

## 7. Blockers To Resolve Before Archive

当前仍存在的阻塞项：

1. `web/frontend/DEMO-AUDIT.md`、`scripts/cli/web/REPORT.md`、`docs/standards/PROJECT_MODULES.md` 等历史文档仍把 `router/index.js` 写成“路由配置”
2. `docs/architecture/Phase4_Day3_Frontend_Integration完成报告.md` 仍把 `phase4.routes.js` 写成待接入对象
3. `views/monitoring/*` 与 `Phase4Dashboard` / `TechnicalAnalysis` 的页面资产退场条件还未闭环

这意味着当前阶段只能定策略，不能直接执行迁移。

## 8. Decision Output for Batch E2

本批次产出如下：

- `index.js` = 原位保留，等待 E3/E4 后与备份成组归档
- `index.js.clean` = 最早可归档候选，但需附损坏说明
- `index.js.backup-phase2.3` = 与 `index.js` 成组归档
- `phase4.routes.js` = 待 E4 后决定单文件归档或历史退役说明

换言之，`E2` 的目标不是“立刻归档”，而是把后续归档动作从“凭感觉删旧文件”变成“按门禁执行的历史资产迁移”。
