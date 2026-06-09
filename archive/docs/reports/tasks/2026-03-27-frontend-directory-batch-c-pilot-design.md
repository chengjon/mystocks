# 2026-03-27 Frontend Directory Batch C：白名单试点迁移方案设计

> **设计方案说明**:
> 本文件是架构设计、系统模型、功能结构、映射关系或规格方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、功能清单和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> 基线来源：
> - [2026-03-27-frontend-directory-current-inventory.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-current-inventory.md)
> - [2026-03-27-frontend-directory-batch-a-active-route-truth-table.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-a-active-route-truth-table.md)
> - [2026-03-27-frontend-directory-batch-b-risk-classification.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-b-risk-classification.md)
> - [2026-03-27-frontend-directory-batch-b-freeze-list.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-b-freeze-list.md)
> - [2026-03-27-frontend-directory-batch-b-migration-white-list.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-b-migration-white-list.md)

## 1. 目标

Batch C 不直接迁移，而是完成“试点迁移方案设计”。

本阶段要回答的问题只有三个：

1. 第一个试点域选哪一组页面最安全
2. 这组页面迁移时需要保护哪些依赖和验证门禁
3. 迁移步骤如何设计成可回滚、可验证的小批次

## 2. 试点域选择

### 最终选择

选择 `market/data` 作为第一试点域。

### 选择理由

相对 `strategy / trade / risk / system`，`market/data` 更适合做首轮试点：

- 白名单页面数量充足，可逐步拆批
- 多数页面是单路由、单组件，不存在多路由复用问题
- 相比策略/交易链路，业务耦合度更低
- 相比系统/监控页，关键性略低，回退成本更可控

### 暂不选择的域

- `strategy`
  - 仍有大量 L3 复杂页，且与跨 Tab 上下文强耦合
- `trade`
  - 含 `TradingDashboard.vue` 等冻结页，交易链路风险高
- `risk`
  - 虽有白名单，但与 `PortfolioOverviewTab` 等共享组件关系更复杂
- `system`
  - 监控页被冻结，系统页整体更适合等方法成熟后再处理

## 3. 试点范围设计

## C1：首批试点页

### 当前状态

`已完成`

### 建议纳入

1. [MarketRealtimeTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue)
2. [MarketKLineTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue)
3. [DragonTigerAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue)

### 选择原因

- 都是单路由页面
- 相对 import 依赖浅：
  - `MarketRealtimeTab.vue`：1 个相对依赖
  - `MarketKLineTab.vue`：1 个相对依赖
  - `DragonTigerAnalysis.vue`：1 个相对依赖
- 不属于冻结页
- 不被多路由复用

### 当前真实依赖特征

| 页面 | 行数 | 相对依赖数 | 主要相对依赖 |
|---|---:|---:|---|
| `MarketRealtimeTab.vue` | 319 | 1 | `./marketRealtimeData` |
| `MarketKLineTab.vue` | 285 | 1 | `./marketKlineData` |
| `DragonTigerAnalysis.vue` | 345 | 1 | `./dragonTigerData` |

### 迁移目标路径（设计态，不立即执行）

| 当前文件 | 目标路径 |
|---|---|
| `artdeco-pages/market-tabs/MarketRealtimeTab.vue` | `views/market/Realtime.vue` |
| `artdeco-pages/market-tabs/MarketKLineTab.vue` | `views/market/Technical.vue` |
| `artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | `views/market/LHB.vue` |

### 已落地结果

已按薄包装入口方案完成主线路由切换，对应提交：

- `5137ab0e1` `refactor(frontend): remap market pilot routes to domain views`

## C2：第二批试点候选

### 当前状态

`已完成`

在 C1 通过后，才考虑进入：

1. [ArtDecoIndustryAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue)
2. [MarketConceptTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue)
3. [FundFlowAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue)
4. [ArtDecoDataAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue)

### 为什么不放进首批

- `ArtDecoDataAnalysis.vue` 有多个相对依赖组件
- `FundFlowAnalysis.vue` 体量更大
- 这几页更适合作为“方法验证后”的第二波，而不是试点起步页

### 已落地结果

已按与 C1 相同的薄包装入口方案完成主线路由切换，对应提交：

- `b4053a357` `refactor(frontend): remap data routes to domain views`

## 4. 本批次明确不碰的页面

### 冻结页

- `Login.vue`
- `NotFound.vue`
- `TradingDashboard.vue`
- `Screener.vue`
- `AnnouncementMonitor.vue`
- `BacktestGPU.vue`
- `ArtDecoDashboard.vue`
- `ArtDecoMonitoringDashboard.vue`

### 复用页 / 高复杂页

- `StrategySignalsTab.vue`
- `ArtDecoTradingPositions.vue`
- `PortfolioOverviewTab.vue`
- `ArtDecoStrategyManagement.vue`
- `StrategyParametersTab.vue`
- `ArtDecoBacktestAnalysis.vue`
- `ArtDecoStrategyOptimization.vue`
- `ArtDecoSignalsView.vue`
- `ArtDecoTradingHistory.vue`
- `ArtDecoRiskManagement.vue`

## 5. 试点执行策略（设计态）

### Phase C1-Prep：迁移前核对

1. 核对 3 个试点页当前路由入口
2. 核对其相对依赖文件是否应同批搬迁
3. 核对是否有字符串/文档/测试硬编码旧路径

### Phase C1-Move：页面与最小依赖迁移

1. 仅迁移 3 个页面
2. 仅迁移它们直接依赖的本地数据转换文件：
   - `marketRealtimeData`
   - `marketKlineData`
   - `dragonTigerData`
3. 不在本批次抽象到 `src/shared`

### Phase C1-Compat：路由兼容

1. 更新 `router/index.ts` 指向新路径
2. 保持路由 URL 不变
3. 页面行为必须完全等价

### Phase C1-Verify：验证门禁

至少执行：

1. `git diff --check`
2. `npm run lint`
3. `npm run type-check` 或当前团队等效门禁
4. 目标页相关 E2E / smoke
5. 若涉及视觉稳定区，补跑相关 visual

### Phase C1-Commit：单独提交

试点页迁移必须独立提交，不与其它域合并。

## 6. 回滚策略

### 回滚触发条件

满足任一条件即回滚：

- 路由无法解析
- 页面加载白屏
- 相关 E2E 失败
- import 路径错误引起构建失败

### 回滚范围

- 只回滚 C1 的 3 个页面与对应最小依赖
- 不影响其它域

## 7. 建议后续批次衔接

若 C1 成功，再进入：

- Batch D：共享资产盘点
- 然后才决定是否把 `market/data` 第二批推进，或切换到其它域

当前状态：

- Batch D 已完成
- `market/data` 试点的路由入口归属已经覆盖 C1 + C2 共 7 页
- 下一步不建议直接继续迁页，应先评估是否值得做主体实现内迁

## 8. 本批次输出结论

### 已形成的设计结论

- 第一试点域：`market/data`
- 第一试点页：3 个
- 当前策略：页面迁移优先，shared 抽取延后
- 当前门禁：必须以“可回滚、小提交、路由不变”为原则

## 9. 建议审批口径

如果继续推进目录治理，建议下一步审批为：

`同意执行 market/data 主体实现内迁 M1：先迁 5 个单依赖页面`

当前已完成的输出物：

- [2026-03-27-frontend-directory-batch-c1-preparation-checklist.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-c1-preparation-checklist.md)
- [2026-03-27-frontend-directory-batch-d-shared-assets-inventory.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-d-shared-assets-inventory.md)
- [2026-03-27-frontend-directory-market-data-body-migration-assessment.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-market-data-body-migration-assessment.md)
