# 2026-03-27 Frontend Directory Batch D：共享资产盘点

> 基线来源：
> - [2026-03-27-frontend-directory-restructure-batch-plan.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-restructure-batch-plan.md)
> - [2026-03-27-frontend-directory-batch-c-pilot-design.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-c-pilot-design.md)
>
> 目标：建立 `src/views/*` 与 `src/components/*` 的共享资产依赖地图，不移动文件，不提前启动 `src/shared/` 抽取。

## 1. 当前试点进度

截至本批次，`market/data` 试点域已完成两轮“入口归属迁移”：

- C1：`market` 3 页主线路由改指向 `views/market/*`
- C2：`data` 4 页主线路由改指向 `views/data/*`

当前实现方式仍是薄包装入口页：

- [Realtime.vue](/opt/claude/mystocks_spec/web/frontend/src/views/market/Realtime.vue)
- [Technical.vue](/opt/claude/mystocks_spec/web/frontend/src/views/market/Technical.vue)
- [LHB.vue](/opt/claude/mystocks_spec/web/frontend/src/views/market/LHB.vue)
- [Industry.vue](/opt/claude/mystocks_spec/web/frontend/src/views/data/Industry.vue)
- [Concepts.vue](/opt/claude/mystocks_spec/web/frontend/src/views/data/Concepts.vue)
- [FundFlow.vue](/opt/claude/mystocks_spec/web/frontend/src/views/data/FundFlow.vue)
- [Advanced.vue](/opt/claude/mystocks_spec/web/frontend/src/views/data/Advanced.vue)

这意味着：

- 路由真值已开始进入目标域目录
- 但页面主体实现仍主要停留在 `artdeco-pages`
- 因此 Batch D 的重点不是新 wrapper，而是 wrapper 背后的旧页依赖

## 2. 盘点范围

本次只盘点四类目录：

1. `web/frontend/src/views/components`
2. `web/frontend/src/views/composables`
3. `web/frontend/src/views/styles`
4. `web/frontend/src/components/*`

## 3. `src/views/components` 盘点

当前文件：

- `RiskOverviewTab.vue`
- `StopLossMonitoringTab.vue`
- `composables/useStopLossMonitoringTab.ts`
- `styles/RiskOverviewTab.css`
- `styles/StopLossMonitoringTab.css`

### 判定

- 这组文件位于 `src/views/components`，但与当前 `market/data` 试点页没有直接依赖关系
- 按路径静态搜索，本批未发现其它页面以源文件路径直接导入它们
- 更像历史结构遗留或局部实验性组织，而不是当前目录治理的共享基座

### 当前分类

- `待判定，但偏向历史残留`

### 当前建议

- 保留
- 不纳入 `src/shared/` 抽取
- 不作为下一批迁页的前置阻塞项

## 4. `src/views/composables` 盘点

当前存在 15 个源文件，另含测试文件。

代表性映射如下：

| 文件 | 当前主要归属 |
|---|---|
| `useTradingDashboard.ts` | 根层 [TradingDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/TradingDashboard.vue) |
| `tradingDashboardActions.ts` | 根层交易大盘配套逻辑 |
| `useIndustryConceptAnalysis.ts` | 根层 [IndustryConceptAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/IndustryConceptAnalysis.vue) |
| `useAdvancedAnalysis.ts` | 根层 [AdvancedAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/AdvancedAnalysis.vue) |
| `useAnalysis.ts` | 根层 [Analysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/Analysis.vue) |
| `useTechnicalAnalysis.ts` / `.types.ts` / `.shortcuts.ts` | 根层 [TechnicalAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/TechnicalAnalysis.vue) |
| `usemonitor.ts` | 根层 [monitor.vue](/opt/claude/mystocks_spec/web/frontend/src/views/monitor.vue) |

### 判定

- `src/views/composables` 目前主要服务于根层 legacy/root 视图
- 它不是 C1/C2 这批 route-wrapper 迁移的直接共享阻塞点
- 其中真正被当前 `data` 试点页使用的组合逻辑，已经不在这里，而是在：
  - [useDataAnalysis.ts](/opt/claude/mystocks_spec/web/frontend/src/composables/market/useDataAnalysis.ts)
  - [useArtDecoApi.ts](/opt/claude/mystocks_spec/web/frontend/src/composables/artdeco/useArtDecoApi.ts)

### 当前分类

- `历史根层视图配套层`

### 当前建议

- 保留原位
- 不与本轮目录迁移捆绑清理
- 后续如要治理，应独立按“根层 legacy 视图收缩”另开批次

## 5. `src/views/styles` 盘点

当前存在 27 个样式文件，命名集中对应根层页面或 legacy 视图：

- `Analysis.scss`
- `Dashboard.scss`
- `IndustryConceptAnalysis.scss`
- `Market.scss`
- `TechnicalAnalysis.css`
- `TradingDashboard.css`
- `monitor.scss`
- 以及多组 demo / 历史样式文件

### 判定

- 这批样式主要是根层视图或历史页的伴生文件
- C1/C2 新增的 `views/market/*` 与 `views/data/*` wrapper 并不直接依赖它们
- 当前试点页主体实现内部也主要使用：
  - `@/styles/artdeco-tokens.scss`
  - 页面私有的同目录数据转换文件
  - `@/components/artdeco/*`

### 当前分类

- `根层/历史页伴生样式层`

### 当前建议

- 保留原位
- 不在 Batch D 内启动 `styles/` 统一迁移
- 等真正进入“主体实现内迁”时，再按页面域逐步重挂

## 6. 当前真正的共享资产

结合 C1/C2 的 7 个试点页，当前真正稳定复用的共享层是：

### 6.1 已验证的共享基座

- [components/artdeco/index.ts](/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/index.ts)
- [useArtDecoApi.ts](/opt/claude/mystocks_spec/web/frontend/src/composables/artdeco/useArtDecoApi.ts)
- [ArtDecoChart.vue](/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/charts/ArtDecoChart.vue)
- [useDataAnalysis.ts](/opt/claude/mystocks_spec/web/frontend/src/composables/market/useDataAnalysis.ts)

### 6.2 仍应视为页面私有的资产

- `marketRealtimeData.ts`
- `marketKlineData.ts`
- `dragonTigerData.ts`
- `industryAnalysisData.ts`
- `marketConceptData.ts`
- `fundFlowPageData.ts`
- `AnalysisIndicators.vue`
- `AnalysisScreener.vue`
- `AnalysisResults.vue`

这些文件虽然具备一定复用潜力，但当前仍直接耦合具体页面语义，不应仅因“看起来像共享”就提前抽到 `src/shared/`。

## 7. 对 C1/C2 的影响结论

### 已验证结论

- C1/C2 的 route-wrapper 迁移不依赖 `src/views/components`
- C1/C2 的 route-wrapper 迁移不依赖 `src/views/styles`
- C1/C2 的 route-wrapper 迁移也不依赖 `src/views/composables`
- 当前最稳定的共享基座已经在 `src/components/*` 与 `src/composables/*`

### 工程含义

- 现阶段继续推进目录治理，不应先做 `src/shared/` 抽取
- 下一步如果继续，不该把重点放在“统一清空 views/* 辅助目录”
- 更合理的方向是：
  - 先决定是否继续做 `market/data` 主体实现内迁
  - 或切换到下一个低风险试点域

## 8. Batch D 输出结论

### 本批次正式结论

- `src/views/components`：保留，待判定，当前不动
- `src/views/composables`：根层 legacy 配套层，当前不动
- `src/views/styles`：根层/历史页伴生样式层，当前不动
- `src/components/*` 与 `src/composables/*`：当前真实共享层
- `market/data` 试点暂不需要新的 shared 抽取动作

## 9. 建议下一步

不建议直接继续新一轮迁页。  
建议下一步审批口径调整为：

`同意执行 market/data 试点主体实现内迁评估`

评估内容应只回答两个问题：

1. 当前 7 个 wrapper 中，哪些值得继续把主体实现从 `artdeco-pages` 挪到目标域目录
2. 哪些页面应停在“路由入口已归位”这一层，不再继续深挖
