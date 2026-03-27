# 2026-03-27 Market/Data 试点主体实现内迁评估

> 基线来源：
> - [2026-03-27-frontend-directory-batch-c-pilot-design.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-c-pilot-design.md)
> - [2026-03-27-frontend-directory-batch-d-shared-assets-inventory.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-d-shared-assets-inventory.md)
>
> 目标：对已完成 route-wrapper 归位的 7 个 `market/data` 页面，判断是否值得继续把主体实现从 `artdeco-pages` 内迁到目标域目录。

## 1. 评估标准

每个页面只按以下 5 项判断：

1. 页面体量是否仍可控
2. 页面私有依赖是否少且清晰
3. 是否已有足够测试保护
4. 内迁后是否能显著提升目录语义
5. 是否会引入额外 shared 抽取压力

结论只允许 3 类：

- `继续内迁`
- `延后内迁`
- `止步于入口归位`

## 2. 逐页真值表

| 路由 | 旧实现 | 行数 | 页面私有依赖 | 当前测试保护 | 结论 |
|---|---|---:|---|---|---|
| `market-realtime` | `MarketRealtimeTab.vue` | 319 | `marketRealtimeData.ts` | `market-data.spec.ts` + `marketRealtimeData.test.ts` | `继续内迁` |
| `market-technical` | `MarketKLineTab.vue` | 285 | `marketKlineData.ts` | `kline-chart.spec.ts` + `MarketKLineTab.spec.ts` + `marketKlineData.test.ts` | `继续内迁` |
| `market-lhb` | `DragonTigerAnalysis.vue` | 345 | `dragonTigerData.ts` | `market-data.spec.ts` + `dragonTigerData.test.ts` | `继续内迁` |
| `data-industry` | `ArtDecoIndustryAnalysis.vue` | 372 | `industryAnalysisData.ts` | `comprehensive-all-pages.spec.ts` + `industryAnalysisData.test.ts` + `industryAnalysisData.spec.ts` | `继续内迁` |
| `data-concept` | `MarketConceptTab.vue` | 271 | `marketConceptData.ts` | `comprehensive-all-pages.spec.ts` + `MarketConceptTab.spec.ts` + `marketConceptData.test.ts` | `继续内迁` |
| `data-fund-flow` | `FundFlowAnalysis.vue` | 454 | `fundFlowPageData.ts` + `ArtDecoChart.vue` | `comprehensive-all-pages.spec.ts` + `FundFlowAnalysis.spec.ts` + `fundFlowPageData.test.ts` | `延后内迁` |
| `data-indicator` | `ArtDecoDataAnalysis.vue` | 347 | `AnalysisIndicators.vue` + `AnalysisScreener.vue` + `AnalysisResults.vue` + `useDataAnalysis.ts` | `comprehensive-all-pages.spec.ts` | `止步于入口归位` |

## 3. 判断理由

### 3.1 建议继续内迁的 5 页

- `market-realtime`
- `market-technical`
- `market-lhb`
- `data-industry`
- `data-concept`

这些页面有共同特征：

- 主体文件体量仍在可控区间
- 页面私有依赖只有 1 个本地数据转换文件
- 已有 E2E 或单测保护，不是“裸迁移”
- 内迁后目录语义提升直接且明显
- 不会逼迫当前批次提前抽 `src/shared/`

### 3.2 建议延后的 1 页

- `data-fund-flow`

原因：

- 页面体量在本组中最大
- 已经直接依赖共享图表组件 [ArtDecoChart.vue](/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/charts/ArtDecoChart.vue)
- 页面同时承担趋势图和排行表两类展示职责

它不是不能迁，而是不适合与前 5 页放在同一微批次里。  
更合理的做法是把它单独作为一个后续批次。

### 3.3 建议止步于入口归位的 1 页

- `data-indicator`

原因：

- 它不是单文件页面，而是一个由 3 个本地子组件和 1 个业务 composable 共同构成的小型工作台
- 当前主体实现仍带有明显的 page-private 结构
- 继续内迁很容易从“目录治理”滑向“局部组件重构”
- 现阶段这样做，收益明显低于风险

当前更合理的策略是：

- 保留 [Advanced.vue](/opt/claude/mystocks_spec/web/frontend/src/views/data/Advanced.vue) 作为主线路由入口
- 不继续把 [ArtDecoDataAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue) 连同其 3 个子组件整体搬迁

## 4. 建议执行顺序

如果后续继续做“主体实现内迁”，建议只按下面顺序推进：

1. `market-realtime`
2. `market-technical`
3. `market-lhb`
4. `data-industry`
5. `data-concept`
6. `data-fund-flow`

`data-indicator` 不进入当前内迁序列。

## 5. 不建议做的事

- 不把 7 页一起整体内迁
- 不在当前阶段顺手抽 `src/shared/`
- 不把 `AnalysisIndicators.vue` / `AnalysisScreener.vue` / `AnalysisResults.vue` 当作目录治理顺手清理项
- 不把 `fundFlowPageData.ts` 与其它 market/data helper 机械合并

## 6. 本评估结论

### 正式结论

- `继续内迁`：5 页
- `延后内迁`：1 页
- `止步于入口归位`：1 页

### 工程结论

当前 `market/data` 试点已经证明：

- “主线路由入口归位”是可行的
- 但“主体实现内迁”必须继续拆小批次
- 并不是所有 wrapper 都值得继续深挖

## 7. 建议下一步审批口径

如果继续推进目录治理，建议下一步批准为：

`同意执行 market/data 主体实现内迁 M1：先迁 5 个单依赖页面`

M1 只应覆盖：

- `market-realtime`
- `market-technical`
- `market-lhb`
- `data-industry`
- `data-concept`
