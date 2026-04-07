# 2026-03-27 本地脏工作区分批计划

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> 目标：把当前主工作树的本地未提交修改，从“混合脏工作区”拆成可理解、可提交、可验证的批次。
> 身份：历史分批计划快照；其中分支、文件数和批次状态均对应 `2026-03-27` 当时环境。

## 1. 当前状态

- 当前分支：`main`
- 当前本地/远端提交点：`00fff0cd6`
- 当前未提交修改总数：`72` 个文件

已先完成非破坏性备份快照：

- 备份分支：`backup/main-dirty-pre-triage-20260327`
- 备份提交：`38865cdea7de97cbba6d77e4c604399c932df0cf`

说明：

- 这个备份分支只是快照，不改变当前工作区
- 后续即使分批时误操作，也还能回到这个快照点

## 2. 总体分布

当前修改主要集中在：

- `web/frontend/src/views`：`69`
- `web/frontend/src/components`：`45`
- `.omc/state/sessions/...`：`3`
- 其余为 `web/frontend` 顶层文档/脚本/报告、少量 `docs/scripts/reports/src`

这说明当前工作区不是单一主题，而是至少混合了：

1. 前端组件/UI 批
2. 前端页面批
3. 前端文档/报告批
4. 脚本/说明批
5. 运行时状态文件批

已完成批次：

- `Batch 4`：导航与共享壳层组件
- `Batch 5`：市场共享组件层
- `Batch 6`：市场 / 技术 / 股票页面层

这些批次已在隔离 worktree 中验证通过，并已合入/推送到 `main`。

## 3. 分批原则

### 3.1 不把生成物和功能改动混在一起

以下内容必须单独处理：

- `.omc/state/sessions/...`
- 报告/总结类 Markdown
- 测试 HTML、说明页、theme quick reference

### 3.2 先收低耦合，再碰高耦合

优先处理：

- 文档
- 报告
- 运行时状态
- 独立脚本

后处理：

- `src/components/layout`
- `src/components/shared`
- `src/views/market`
- `src/views/monitoring`
- `src/views/strategy`

### 3.3 共享层和页面层不要混提

以下两类必须拆开：

- 共享组件/导航组件
- 使用这些组件的页面视图

否则一旦回归，很难定位问题来自“组件层”还是“页面层”。

## 4. 推荐批次

## Batch 0：运行时状态快照层

### 范围

- `.omc/state/sessions/5ae67728-2aaa-4150-a71f-2b770e97ae82/*`

### 风险

- `低`

### 说明

- 这类文件是会话/运行状态，不应和业务改动混提
- 如果要保留，只能作为“上下文快照”单独处理

### 建议

- 单独快照
- 不混入功能提交

## Batch 1：仓库根层必要性复核批

### 范围

- [ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md)
- [phase7_initialization_summary.md](/opt/claude/mystocks_spec/reports/phase7_initialization_summary.md)
- [ai-collaboration-setup.sh](/opt/claude/mystocks_spec/scripts/ai-collaboration-setup.sh)
- [001_create_strategy_tables.sql](/opt/claude/mystocks_spec/scripts/db/migrations/001_create_strategy_tables.sql)
- [monitor_phase7_progress.sh](/opt/claude/mystocks_spec/scripts/monitor_phase7_progress.sh)
- [README.md](/opt/claude/mystocks_spec/src/interfaces/README.md)

### 风险

- `低到中`

### 说明

- 这批不在主前端代码路径上
- 但经逐文件复核后，**不能整体视为“必要更新批”**

### 当前复核结论

- **真实内容更新候选**
  - [ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md)
    - 属于文档进展同步
    - 方向上是更新，不是回退
    - 但仍是“可选保留”，不是运行必需项

- **假脏 / 无正文变化**
  - [phase7_initialization_summary.md](/opt/claude/mystocks_spec/reports/phase7_initialization_summary.md)
  - [monitor_phase7_progress.sh](/opt/claude/mystocks_spec/scripts/monitor_phase7_progress.sh)

- **纯行尾变化，不构成有效更新**
  - [ai-collaboration-setup.sh](/opt/claude/mystocks_spec/scripts/ai-collaboration-setup.sh)
  - [001_create_strategy_tables.sql](/opt/claude/mystocks_spec/scripts/db/migrations/001_create_strategy_tables.sql)
  - [README.md](/opt/claude/mystocks_spec/src/interfaces/README.md)

### 建议

- 不要把 Batch 1 整体直接提交
- 只把 [ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md) 保留为候选项
- 其余 5 个先视为噪音或格式状态，不纳入提交批次

## Batch 2：前端顶层文档/报告/静态辅助资产

### 范围

- `web/frontend/ACCESSIBILITY_*`
- `web/frontend/PHASE*`
- `web/frontend/QUICK_THEME_VERIFICATION.md`
- `web/frontend/THEME_APPLICATION_REPORT.md`
- `web/frontend/TYPESCRIPT_ERROR_RESOLUTION_FINAL_REPORT.md`
- `web/frontend/reports/*`
- `web/frontend/public/accessibility-test.html`
- `web/frontend/src/theme-test.html`
- `web/frontend/src/styles/THEME_QUICK_REFERENCE.md`

### 风险

- `低`

### 说明

- 这批大多是说明文档、测试辅助页、报告产物
- 但经逐文件比对后，**当前这 23 个文件不构成真实更新批**

### 当前复核结论

- **真实内容更新**
  - `0` 个

- **假脏 / 字节完全一致**
  - `15` 个
  - 包含：
    - `ACCESSIBILITY_*`
    - `QUICK_THEME_VERIFICATION.md`
    - `THEME_APPLICATION_REPORT.md`
    - `TYPESCRIPT_ERROR_RESOLUTION_FINAL_REPORT.md`
    - `reports/*`
    - `public/accessibility-test.html`
    - `src/theme-test.html`
    - `src/styles/THEME_QUICK_REFERENCE.md`

- **纯行尾变化**
  - `8` 个
  - 包含：
    - `PHASE3_*`
    - `PHASE4_*`

### 工程判断

- 当前 `Batch 2` 不是“值得直接提交”的真实更新批
- 如果继续处理，这一批更像：
  - 假脏刷新
  - 行尾标准化
  - 或直接放弃

它们不是功能更新，也不是当前主线必须保留的内容

### 建议

- 不要把 Batch 2 作为下一批直接收口
- 先把它视为“工作区噪音批”，暂不提交

## Batch 3：前端工具与校验脚本层

### 范围

- `web/frontend/package.json`
- `web/frontend/scripts/run-lighthouse-audits.sh`
- `web/frontend/scripts/summarize-lighthouse-reports.js`
- `web/frontend/test-bb-api.js`
- `web/frontend/tests/unit/utils/atrading.test.ts`
- `web/frontend/validate-theme-import.sh`

### 风险

- `中`

### 说明

- 这批会影响本地验证方式、脚本入口和测试口径
- 不应与 UI 页面改动混提

### 当前复核结论

- **真实内容更新候选**
  - [package.json](/opt/claude/mystocks_spec/web/frontend/package.json)
    - 真实改动点只有一处：
      扩大 `lint:artdeco:changed` 的扫描范围，把大量 `views/components/market/system/monitoring/...` 文件重新纳入 changed-scope 门禁

- **假脏 / 字节完全一致**
  - [run-lighthouse-audits.sh](/opt/claude/mystocks_spec/web/frontend/scripts/run-lighthouse-audits.sh)
  - [summarize-lighthouse-reports.js](/opt/claude/mystocks_spec/web/frontend/scripts/summarize-lighthouse-reports.js)
  - [validate-theme-import.sh](/opt/claude/mystocks_spec/web/frontend/validate-theme-import.sh)

- **纯行尾变化**
  - [test-bb-api.js](/opt/claude/mystocks_spec/web/frontend/test-bb-api.js)
  - [atrading.test.ts](/opt/claude/mystocks_spec/web/frontend/tests/unit/utils/atrading.test.ts)

### 工程判断

- `Batch 3` 不再是一个完整的可提交批次
- 其中只有 `package.json` 值得继续判断是否保留
- 但这个改动本质上是**门禁范围升级**
- 它不适合脱离后面的 UI 清理批次单独提交

也就是说：

- 如果后续不保留当前大批前端 UI/样式治理工作，这个 `package.json` 变更就偏**提前**，不值得单独保留
- 如果后续要继续收口前端 UI/ArtDeco token 债，它就属于**配套更新**

### 建议

- 不直接执行 Batch 3 提交
- 把 [package.json](/opt/claude/mystocks_spec/web/frontend/package.json) 视为“依附于后续前端治理批次的配套改动”
- 其余 5 个视为噪音，不纳入提交

## Batch 4：导航与共享壳层组件

### 范围

- `web/frontend/src/components/layout/*`
- `web/frontend/src/components/menu/*`
- `web/frontend/src/components/menu_root/*`
- `web/frontend/src/components/common/*`
- `web/frontend/src/components/shared/*`
- `web/frontend/src/views/errors/ServiceUnavailable.vue`
- `web/frontend/src/views/components/*`

### 风险

- `高`

### 说明

- 这是共享 UI 壳层
- 影响面广，容易波及大量页面

### 当前复核结论

- 这批文件都是**真实内容变化**，不是假脏
- 抽查代表文件后，变化模式高度一致：
  - `@import` -> `@use`
  - 样式入口标准化
  - 共享 UI 样式 token 接入
  - 基本不涉及业务数据流和接口契约

代表样本：

- [ArtDecoHeader.vue](/opt/claude/mystocks_spec/web/frontend/src/components/layout/ArtDecoHeader.vue)
- [PageHeader.vue](/opt/claude/mystocks_spec/web/frontend/src/components/shared/ui/PageHeader.vue)
- [CommandPalette.vue](/opt/claude/mystocks_spec/web/frontend/src/components/menu/CommandPalette.vue)
- [KeyboardShortcuts.vue](/opt/claude/mystocks_spec/web/frontend/src/components/common/KeyboardShortcuts.vue)
- [RiskOverviewTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/components/RiskOverviewTab.vue)

### 工程判断

- `Batch 4` 整体方向是**更新，不是倒退**
- 它更像“共享壳层样式收口批”
- 风险主要来自“共享范围广”，而不是功能逻辑变化

### 建议

- `Batch 4` 值得保留
- 但必须单独提交，不能与页面层混提
- 提交前必须至少补跑共享壳层相关 smoke/页面验证

### 建议

- 不要和页面批混提
- 后于文档/脚本批处理

## Batch 5：市场共享组件层

### 范围

- `web/frontend/src/components/market/*`
- `web/frontend/src/components/Charts/*`
- `web/frontend/src/components/chart/*`
- `web/frontend/src/components/data/DataCard.vue`
- `web/frontend/src/components/realtime/*`
- `web/frontend/src/components/technical/IndicatorPanel.vue`
- `web/frontend/src/components/sse/DashboardMetrics.vue`
- `web/frontend/src/components/monitoring/*`

### 风险

- `中到高`

### 说明

- 这是页面下方的业务共享组件层
- 与 `market/views`、`stocks/views`、`monitoring/views` 强耦合

### 当前复核结论

- 这批文件也都是**真实内容变化**
- 但相较 `Batch 4`，它不只是样式入口语法收口，还包含：
  - 内联样式提取为 class
  - 硬编码颜色替换为 token
  - 图表配色和 grid 色值改走主题变量
  - 局部尺寸改为 token 计算

代表样本：

- [FundFlowPanel.vue](/opt/claude/mystocks_spec/web/frontend/src/components/market/FundFlowPanel.vue)
- [WencaiPanel.scss](/opt/claude/mystocks_spec/web/frontend/src/components/market/styles/WencaiPanel.scss)
- [AdvancedHeatmap.vue](/opt/claude/mystocks_spec/web/frontend/src/components/Charts/AdvancedHeatmap.vue)

### 工程判断

- `Batch 5` 整体方向仍然偏**更新**
- 但它已经触到组件呈现逻辑和主题表现层
- 比 `Batch 4` 更容易引入视觉回归或交互回归

### 建议

- `Batch 5` 可以保留，但不要先于 `Batch 4`
- 必须绑定更强验证：
  - `lint:artdeco:changed`
  - 相关页面 E2E / visual / smoke
- [package.json](/opt/claude/mystocks_spec/web/frontend/package.json) 的那处 `lint:artdeco:changed` 扩容改动，应视为 `Batch 5` 的配套变更，而不是独立批次

### 当前状态

- `已完成`

### 建议

- 先于对应页面批次单独整理

## Batch 6：市场 / 技术 / 股票页面层

### 范围

- `web/frontend/src/views/market/*`
- `web/frontend/src/views/technical/*`
- `web/frontend/src/views/stocks/*`
- `web/frontend/src/views/announcement/*`
- `web/frontend/src/views/monitor.vue`
- `web/frontend/src/views/Market.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`
- `web/frontend/src/views/TdxMarket.vue`
- `web/frontend/src/views/Wencai.vue`

### 风险

- `高`

### 说明

- 这批页面会直接受 Batch 5 影响
- 适合在共享组件层稳定后再处理

### 建议

- 不要先于 Batch 5

### 当前复核结论

- 这批 `29` 个页面/样式文件都是**真实内容变化**
- 抽查代表文件后，主变化模式仍然以：
  - 页面 `<style>` 从 `@import` 切到 `@use`
  - 页面样式文件中的 token / 尺寸表达式收口
  - 少量 SVG/icon/内联样式改为 class 为主

代表样本：

- [MarketDataView.vue](/opt/claude/mystocks_spec/web/frontend/src/views/market/MarketDataView.vue)
- [Concepts.scss](/opt/claude/mystocks_spec/web/frontend/src/views/market/styles/Concepts.scss)
- [Screener.vue](/opt/claude/mystocks_spec/web/frontend/src/views/stocks/Screener.vue)
- [Portfolio.scss](/opt/claude/mystocks_spec/web/frontend/src/views/stocks/styles/Portfolio.scss)
- [TechnicalAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/technical/TechnicalAnalysis.vue)

### 工程判断

- `Batch 6` 方向上是**更新，不是倒退**
- 风险高于 `Batch 4/5`，因为它已经深入到页面层
- 但经过隔离 worktree 验证，当前这批已经证明可收口

### 当前状态

- `已完成`

## Batch 7：分析 / 仪表板 / Demo / 根层工作台页面

### 范围

- `web/frontend/src/views/Analysis.vue`
- `web/frontend/src/views/BacktestAnalysis.vue`
- `web/frontend/src/views/BacktestWizard.vue`
- `web/frontend/src/views/Dashboard.vue`
- `web/frontend/src/views/DataVisualizationShowcase.vue`
- `web/frontend/src/views/EnhancedDashboard.vue`
- `web/frontend/src/views/IndicatorLibrary.vue`
- `web/frontend/src/views/IndustryConceptAnalysis.vue`
- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/PortfolioManagement.vue`
- `web/frontend/src/views/PyprofilingDemo.vue`
- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/Settings.vue`
- `web/frontend/src/views/SkeletonUsage.vue`
- `web/frontend/src/views/SmartDataSourceTest.vue`
- `web/frontend/src/views/StockAnalysisDemo.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/StrategyManagement.vue`
- `web/frontend/src/views/TaskManagement.vue`
- `web/frontend/src/views/TradeManagement.vue`
- `web/frontend/src/views/TradingDashboard.vue`
- `web/frontend/src/views/demo/*`
- `web/frontend/src/views/styles/Analysis.scss`
- `web/frontend/src/views/styles/BacktestWizard.scss`
- `web/frontend/src/views/styles/Dashboard.scss`
- `web/frontend/src/views/styles/IndustryConceptAnalysis.scss`
- `web/frontend/src/views/styles/Settings.scss`
- `web/frontend/src/views/styles/TradingDecisionCenter.scss`

### 风险

- `高`

### 当前复核结论

- 这批文件从抽样结果看，仍以页面 `<style>` 入口从 `@import` 到 `@use` 的收口为主
- 与 `Batch 6` 一致，整体方向偏**更新**
- 但它覆盖的是根层工作台 / demo / dashboard 类页面，视觉面更大

### 建议

- 值得继续，但不建议和 `Batch 8` 混提
- 应拆成 `Batch 7a`：根层真实业务页
- `Batch 7b`：demo / showcase / skeleton 辅助页

## Batch 8：监控 / 系统 / 策略 / 交易页面层

### 范围

- `web/frontend/src/views/monitoring/*`
- `web/frontend/src/views/system/*`
- `web/frontend/src/views/strategy/*`
- `web/frontend/src/views/trade-management/*`
- `web/frontend/src/views/technical/TechnicalAnalysis.vue`
- `web/frontend/src/views/technical/styles/TechnicalAnalysis.scss`
- `web/frontend/src/styles/web3-global.scss`
- `web/frontend/src/styles/web3-tokens.scss`

### 风险

- `高`

### 当前复核结论

- 这批文件也都属于**真实内容变化**
- 但比 `Batch 7` 多了一个特殊点：
  - `views/technical/TechnicalAnalysis.scss` 已开始依赖新的
    [web3-global.scss](/opt/claude/mystocks_spec/web/frontend/src/styles/web3-global.scss)
    和
    [web3-tokens.scss](/opt/claude/mystocks_spec/web/frontend/src/styles/web3-tokens.scss)
- 这意味着 `technical` 这一支不能被拆成“只改页面不带支撑文件”的批次

### 建议

- 不要直接整体执行 `Batch 8`
- 更合理的是先拆出一个最小前置批：
  - `Batch 8a`：`technical + web3 style support`
- 再决定是否继续推进 `monitoring / system / strategy / trade-management`

## Batch 7：分析 / 仪表板 / Demo / 根层工作台页面

### 范围

- `web/frontend/src/views/Analysis.vue`
- `web/frontend/src/views/BacktestAnalysis.vue`
- `web/frontend/src/views/BacktestWizard.vue`
- `web/frontend/src/views/Dashboard.vue`
- `web/frontend/src/views/DataVisualizationShowcase.vue`
- `web/frontend/src/views/EnhancedDashboard.vue`
- `web/frontend/src/views/IndicatorLibrary.vue`
- `web/frontend/src/views/IndustryConceptAnalysis.vue`
- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/PortfolioManagement.vue`
- `web/frontend/src/views/PyprofilingDemo.vue`
- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/Settings.vue`
- `web/frontend/src/views/SmartDataSourceTest.vue`
- `web/frontend/src/views/StockAnalysisDemo.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/TaskManagement.vue`
- `web/frontend/src/views/TradeManagement.vue`
- `web/frontend/src/views/TradingDashboard.vue`
- `web/frontend/src/views/demo/*`

### 风险

- `高`

### 说明

- 这批根层视图和演示页主题混杂
- 不适合与 domain 页或共享组件层混提

### 建议

- 再拆成“真实业务页 / demo 页 / 工具页”子批次

## Batch 8：监控 / 系统 / 策略 / 交易页面层

### 范围

- `web/frontend/src/views/monitoring/*`
- `web/frontend/src/views/system/*`
- `web/frontend/src/views/strategy/*`
- `web/frontend/src/views/trade-management/*`
- `web/frontend/src/views/StrategyManagement.vue`

### 风险

- `高`

### 说明

- 这批既有监控页，也有系统页，还有策略执行页
- 功能链复杂，不应该现在直接混着处理

### 建议

- 最后处理
- 最好再按 domain 二次拆分

## 5. 推荐执行顺序

### 推荐顺序

1. `Batch 0`：运行时状态快照层
2. `Batch 1`：仓库根层补充文档与辅助脚本
3. `Batch 2`：前端顶层文档/报告/静态辅助资产
4. `Batch 3`：前端工具与校验脚本层
5. `Batch 4`：导航与共享壳层组件
6. `Batch 5`：市场共享组件层
7. `Batch 6`：市场 / 技术 / 股票页面层
8. `Batch 7`：分析 / 仪表板 / Demo / 根层工作台页面
9. `Batch 8`：监控 / 系统 / 策略 / 交易页面层

### 最值得先收口的第一个真实批次

如果你要我直接开始处理，我建议从：

`Batch 8a：technical + web3 style support 收口`

开始。

原因：

- `Batch 7` 和 `Batch 8` 都已确认是有效更新方向
- 但 `Batch 8` 里有一个清晰的最小依赖簇：
  - `technical/TechnicalAnalysis.vue`
  - `technical/styles/TechnicalAnalysis.scss`
  - `src/styles/web3-global.scss`
  - `src/styles/web3-tokens.scss`
- 先收这个最小簇，可以把当前剩余风险再压低一层

## 6. 不建议的做法

- 不要直接从 `views` 或 `components` 最大目录开刀
- 不要把 `package.json` 和 UI 页面改动混提
- 不要把共享壳层组件和页面层一起收
- 不要在这一步继续新增功能开发

## 7. 下一步审批口径

如果继续，我建议下一步审批为：

`同意执行 Batch 1：仓库根层补充文档与辅助脚本收口`

如果按当前复核后的更准确口径，建议改为：

`同意执行 Batch 8a：technical + web3 style support 收口`
