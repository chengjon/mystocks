# 2026-03-27 Frontend Directory 现状盘点

> **设计方案说明**:
> 本文件是架构设计、系统模型、功能结构、映射关系或规格方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、功能清单和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> 用途：作为 `frontend directory restructure` 替代任务的第一阶段基线文档。
>
> 说明：本盘点只描述当前真实状态，不代表立即执行迁移。

## 1. 当前总体结构

### `web/frontend/src/views` 顶层目录

当前顶层目录共 25 个：

- `.claude`
- `advanced-analysis`
- `announcement`
- `artdeco-pages`
- `components`
- `composables`
- `converted.archive`
- `demo`
- `errors`
- `examples`
- `freqtrade-demo`
- `market`
- `monitoring`
- `risk`
- `settings`
- `stock-analysis`
- `stocks`
- `strategy`
- `styles`
- `system`
- `tdxpy-demo`
- `technical`
- `trade-management`
- `trading`
- `trading-decision`

### `web/frontend/src/views` 根目录 `.vue` 文件

当前根层仍有 44 个 `.vue` 文件，说明目录治理目标尚未实现。

典型文件包括：

- `Dashboard.vue`
- `Market.vue`
- `TradingDashboard.vue`
- `Login.vue`
- `NotFound.vue`
- `StrategyManagement.vue`
- `TechnicalAnalysis.vue`
- `OpenStockDemo.vue`
- `FreqtradeDemo.vue`
- `ArtDecoTest.vue`

## 2. 活跃路由落点

基于 [router/index.ts](/opt/claude/mystocks_spec/web/frontend/src/router/index.ts) 当前实际 import：

- 活跃视图组件唯一落点共 34 个
- 其中 28 个仍位于 `artdeco-pages`
- 仅 6 个位于 `artdeco-pages` 之外

### 活跃路由组件分布

| 顶层位置 | 数量 | 说明 |
|---|---:|---|
| `artdeco-pages` | 28 | 当前主线业务页绝大多数仍集中在此 |
| 根层 `Login.vue` | 1 | 认证入口 |
| 根层 `NotFound.vue` | 1 | 错误页 |
| 根层 `TradingDashboard.vue` | 1 | 交易终端仍未域内归位 |
| `announcement` | 1 | 公告监控 |
| `stocks` | 1 | `Screener.vue` 仍走旧目录 |
| `strategy` | 1 | `BacktestGPU.vue` 已在域目录 |

### 结论

当前项目并不是“已经完成域目录化，只差扫尾”，而是：

- 新旧结构并存
- 主线路由仍高度依赖 `artdeco-pages`
- 少量页面已分散到 `stocks/strategy/announcement/根层`

因此后续目录治理必须以“迁移中间态”思维推进，而不能假设已有目标结构稳定成型。

## 3. 目录类别初步分类

### A. 明显活跃主线目录

- `artdeco-pages`
- `market`
- `risk`
- `strategy`
- `stocks`
- `system`
- `announcement`

### B. 明显历史/示例/演示目录

- `converted.archive`
- `demo`
- `examples`
- `freqtrade-demo`
- `tdxpy-demo`

### C. 交叉层/边界不清目录

- `components`
- `composables`
- `styles`
- `technical`
- `trade-management`
- `trading`
- `trading-decision`
- `advanced-analysis`
- `monitoring`
- `settings`
- `stock-analysis`

这些目录说明当前前端边界并不统一，后续不能只做“文件移动”，还需要先确定：

- 它们是保留为业务域
- 并入现有主域
- 还是降级到历史区

## 4. `artdeco-pages` 现状

`artdeco-pages` 当前包含 89 个 `.vue` 文件，是整个视图层最重的集中区。

典型活跃页面：

- `ArtDecoDashboard.vue`
- `ArtDecoDataAnalysis.vue`
- `ArtDecoMarketData.vue`
- `ArtDecoMarketQuotes.vue`
- `ArtDecoRiskManagement.vue`
- `ArtDecoStockManagement.vue`
- `ArtDecoTechnicalAnalysis.vue`

同时还包含：

- `_templates`
- `market-tabs`
- `market-data-tabs`
- `strategy-tabs`
- `trading-tabs`
- `risk-tabs`
- `system-tabs`
- `portfolio-tabs`
- `analysis-tabs`

### 结论

`artdeco-pages` 不是一个简单目录，而是当前“活跃主线页面总容器”。  
后续若要推进目录治理，必须先决定：

1. 是否以 `artdeco-pages` 为当前真值源逐域拆出
2. 哪些 tab 子目录应直接演进成目标域目录
3. 哪些内容属于历史兼容壳，不应强行迁移

## 5. 共享资产提取现状

旧 change 目标是假设将共享资产统一提到 `src/shared/`，但当前从目录上看：

- `src/views/components`
- `src/views/composables`
- `src/views/styles`
- `src/components/...`

仍存在多层级并存。

### 结论

共享资产提取不能直接按旧清单执行，需要先做：

1. 当前共享组件清单
2. 当前共享 composables 清单
3. 当前共享 styles 清单
4. 哪些仍被活跃路由使用

## 6. 关键风险

### 风险 1：把活跃主线路由误判为可迁移历史页

当前 34 个活跃路由组件里，28 个仍在 `artdeco-pages`。  
如果简单把 `artdeco-pages` 当“待淘汰历史目录”，会直接造成主线功能回退。

### 风险 2：把旧清单中的目标目录当成现状

旧任务写的是目标结构，不是今天的真实结构。  
若直接按旧 checklist 执行，会在错误前提上大量 `git mv`。

### 风险 3：共享资产与页面边界不清

当前很多目录仍混有“页面逻辑 / 共享组件 / 样式 / composables”。  
若不先分类，迁移会把依赖链打断。

## 7. 盘点结论

当前最适合的下一步不是“继续旧 92 项任务”，而是先进入新的批次设计：

### 建议 Batch A

- 标记所有活跃路由组件真实位置
- 建立“活跃页 / 历史页 / demo 页 / 错位目录”分类表

### 建议 Batch B

- 仅针对一个域做迁移设计样板
- 推荐从 `market` 或 `strategy` 二选一

### 建议 Batch C

- 共享资产提取盘点
- 不立刻迁移，只先产出依赖地图

## 8. 建议审批口径

如果继续推进此替代任务，建议下一步审批为：

`同意基于本盘点文档，创建 frontend directory restructure 新批次计划`
