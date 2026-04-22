# ArtDeco Fintech Unified Spec

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文件是当前 MyStocks ArtDeco Fintech 体系的统一规格文档。

> 2026-04-19 规格对齐补充
>
> - 保留 2026-04-01 的目录与运行时分层结论。
> - 将根目录 `DESIGN.md` 中 CoinPulse 吸收项提升为统一规格的一部分。
> - 将 `useHeaderSummary -> ArtDecoLayoutEnhanced -> ArtDecoDashboard` 的共享头部摘要链纳入运行时规格。
> - 将 `artdeco-tokens.scss` 中的 `--ad-*` 状态机 token、金融 glow、200/400ms 过渡预算写入当前实施基线。
> - 补齐历史兼容入口：`docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md`。

它回答的不是“历史上怎么做过”，而是：

1. 当前活跃的 ArtDeco 设计身份是什么。
2. 组件、页面块、容器分别应该放在哪里。
3. 运行时实际上有哪些承载模式。
4. 新增页面或组件时必须遵守哪些工程边界。

## 1. 设计身份

当前项目的活跃风格应理解为：

`Original ArtDeco` + `A 股金融语义` + `高密度量化工作台` = `ArtDeco Fintech`

关键特征：

- 黑金高对比，不走普通后台灰蓝语法
- 标题使用 `Cinzel`
- 正文使用 `Barlow`
- 数值、代码、状态元信息优先使用 `JetBrains Mono`
- A 股语义强制执行“红涨绿跌”
- 页面必须有舞台层，而不只是把业务卡片堆在一起

## 2. 当前真值链

### 2.1 样式真值

新代码默认只认以下主链文件：

- `web/frontend/src/styles/artdeco-tokens.scss`
- `web/frontend/src/styles/artdeco-grid.scss`
- `web/frontend/src/styles/artdeco-global.scss`
- `web/frontend/src/styles/artdeco-financial.scss`
- `web/frontend/src/styles/artdeco-quant-extended.scss`

其中：

- `artdeco-tokens.scss` 当前明确包含 `Cinzel + Barlow + JetBrains Mono`
- 间距体系以源码为准，当前为 **13 个编号级别**
  - `1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32`
  - 另有 `sm/md/lg/xl` 语义别名
  - 另有 `compact-*` 紧凑间距变量
- 当前还明确包含以下设计契约实现点：
  - `--artdeco-transition-quick = 200ms`
  - `--artdeco-transition-base = 400ms`
  - `--artdeco-glow-profit`
  - `--artdeco-glow-loss`
  - `--ad-*` 组件状态机 token
  - chip / tooltip / overlay token

### 2.2 文档真值

活跃治理链路为：

1. `ARTDECO_START_HERE.md`
2. `ARTDECO_FINTECH_UNIFIED_SPEC.md`
3. `DESIGN.md`
4. `ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
5. `ARTDECO_COMPONENT_GUIDE.md`
6. `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
7. `docs/api/ArtDeco_System_Architecture_Summary.md`
8. `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`

其中职责边界为：

- `DESIGN.md`：设计契约层，定义动效预算、密度模式、金融反馈、交易面板交互层级
- `artdeco-tokens.scss` 等样式文件：样式令牌与实现真值层
- `router/index.ts` + `docs/guides/frontend-structure.md`：活跃业务路由与目录真值层
- `artdeco-pages/**`：工作台、模板、域块与兼容包装层真值
- `useHeaderSummary.ts`：跨 Layout / Dashboard 的共享头部摘要状态层，不是设计真值，但属于当前运行时桥接真值

### 2.3 路由真值与 ArtDeco 真值必须分开理解

当前仓库不是“ArtDeco 页面目录 = 活跃业务路由入口”的结构。

需要区分：

1. **活跃业务路由真值**
   - `web/frontend/src/router/index.ts`
   - `web/frontend/src/views/<domain>/*.vue`
2. **ArtDeco 工作台真值**
   - `web/frontend/src/components/artdeco/**`
   - `web/frontend/src/views/artdeco-pages/**`

当前业务域路由主线是：

- `market`
- `data`
- `watchlist`
- `strategy`
- `trade`
- `risk`
- `system`

当前已知 ArtDeco 例外入口：

- `/dashboard` -> `views/artdeco-pages/ArtDecoDashboard.vue`
- `/strategy/signals` -> `views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- `/strategy/pos` -> `views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- `/risk/pnl` -> `views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- `/dashboard` header summary metrics 由 `views/artdeco-pages/composables/useArtDecoDashboard.ts` 推送到 `src/composables/useHeaderSummary.ts`，再由 `layouts/ArtDecoLayoutEnhanced.vue` 统一渲染

这意味着：ArtDeco 体系仍是前端核心视觉与工作台承载体系，但它不等于“所有业务路由都继续直接落在 `artdeco-pages/**`”。

## 3. 组件与页面的目录边界

### 3.1 Reusable UI / Base 资产

目录：`web/frontend/src/components/artdeco/`

当前分成 7 层：

- `base/`：原子 UI
- `core/`：壳层、导航、状态、框架级能力
- `business/`：通用业务交互
- `charts/`：通用图表能力
- `trading/`：交易域可复用组件
- `advanced/`：高阶分析组件
- `specialized/`：强专题资产

### 3.2 Page-Level Shared Fragments

目录：`web/frontend/src/views/artdeco-pages/components/`

这是页面工作台内部的共享片段层，职责是：

- 在多个 ArtDeco 页面/页签块间复用
- 仍然带有页面工作台语境
- 不应伪装成全站原子 UI

它与 `src/components/artdeco/` 的区别是：

- `src/components/artdeco/` 面向稳定资产沉淀
- `views/artdeco-pages/components/` 面向 ArtDeco 页面系统内部复用

### 3.3 Domain Tab Blocks

目录：`web/frontend/src/views/artdeco-pages/*-tabs/`

这类文件是域内工作台块，不是全局组件库。规则：

- 允许绑定当前页面状态、路由和局部业务流
- 允许为独立路由态和内嵌态做壳层适配
- 默认不跨域 import
- 如果某个块开始被多个域长期复用，应提升到更高层级

## 4. 当前运行时承载模式

当前仓库不是单一容器模式，而是三种模式并存：

| 模式 | 代表文件 | 特征 |
|------|----------|------|
| 模板化工作台 | `views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`、`ArtDecoRiskManagement.vue` | 通过 `pageConfig + stats + tabs + content` 插槽统一承载 |
| 直接 Tab 容器 | `ArtDecoMarketData.vue` | 容器内直接声明 tab rail 和 tab content |
| 功能树驱动容器 | `ArtDecoTradingCenter.vue` | 左侧功能树 + 右侧动态组件，适合总控类页面 |

### 4.1 共享头部摘要模式

除上述三类容器外，当前还应补充一条运行时模式：

| 模式 | 代表文件 | 特征 |
|------|----------|------|
| Layout 级共享摘要 | `src/composables/useHeaderSummary.ts`、`layouts/ArtDecoLayoutEnhanced.vue`、`views/artdeco-pages/composables/useArtDecoDashboard.ts` | 页面摘要状态由页面 composable 推送到共享状态容器，再由 Layout header 统一承载 |

该模式用于：

- 将 Dashboard 顶部指标提升为 layout-level summary
- 减少页面内部重复 header actions
- 保持 `/dashboard` 仍为路由例外入口，但不再独占摘要壳层

补充说明：

- `router/index.ts` 以 `ArtDecoLayoutEnhanced.vue` 为主壳层。
- `pageConfig.ts` 是自动生成的路由元数据源，但它 **不是** 当前所有 ArtDeco tabs 的唯一事实源。
- `pageConfig.ts` 当前服务于页面元数据和部分模板化承载，不应被描述成“所有页面块统一由它生成”。
- `pageConfig.ts` 也不承载 `header summary` 这类共享运行时状态；这类状态当前由 composable 层完成桥接。
- 许多工作台页面已经可作为独立路由直接挂载，例如：
  - `strategy-tabs/ArtDecoStrategyManagement.vue`
  - `strategy-tabs/ArtDecoBacktestAnalysis.vue`
  - `trading-tabs/ArtDecoSignalsView.vue`
  - `risk-tabs/RiskOverviewTab.vue`
  - `system-tabs/ArtDecoMonitoringDashboard.vue`

### 4.1 兼容包装层规则

当活跃业务路由已经迁到 `views/<domain>/*.vue` 时：

- `artdeco-pages/**` 中的同类文件默认视为 **工作台块、模板页或兼容包装层**
- 兼容包装层必须保持薄封装，不能重新沉淀业务真值
- 新增页面时，优先判断应进入域目录还是 ArtDeco 工作台目录，而不是机械复制两份

## 5. 工程铁律

### 5.1 视觉实现

- 禁止新增硬编码颜色、间距、圆角、阴影、过渡
- 新代码优先使用 `@use`
- 禁止把兼容层重新当成真值层
- A 股涨跌语义只用 `--artdeco-rise` / `--artdeco-down` 或对应语义别名
- 数据优先反馈遵循 `DESIGN.md`：数据动作 `200ms`，装饰动作 `400ms`
- 金融状态 glow 优先使用 `--artdeco-glow-profit` / `--artdeco-glow-loss`
- 组件状态切换优先绑定 `--ad-*` 状态机 token，不再散落 ad-hoc hover/focus/error 样式
- overlay / backdrop 共享表面优先绑定 `--ad-overlay-*` token；当前已在 `ArtDecoLoadingOverlay.vue` 与 `ArtDecoTradeForm.vue` 落地
- tooltip token 当前保留为共享合同真值；若未来需要独立 tooltip primitive，应优先在共享组件层实现，而不是先在图表或页面局部样式中扩散

### 5.2 目录治理

- `src/components/artdeco/**` 只放可持续沉淀的可复用资产
- `views/artdeco-pages/components/` 只放页面系统内共享片段
- `*-tabs/` 只放域内工作台块
- 页面专属逻辑不要上提到 base/core

### 5.3 页面承载

- 新页面优先复用现有工作台壳层
- 页面至少要有明确的 header、meta、content 节奏
- 需要 tabs 时，优先延续当前 `tabs shell -> content shell` 结构
- 若该页面是活跃业务路由 canonical entry，优先落在 `views/<domain>/`
- 若该页面是 ArtDeco 工作台内部块、模板页、兼容壳或独立工作台页签，才落在 `views/artdeco-pages/**`
- 若页面需要把摘要状态提升到 Layout 统一头部，优先通过共享 composable 桥接，而不是在多个页面重复实现 header actions

### 5.4 桌面端约束

- 项目当前是桌面端工作台，不做移动端/平板适配
- 允许桌面端内部的 Grid 断点与列数折叠
- 不允许以“响应式治理”为名新增移动端语法分支
- E2E 中出现的 mobile/tablet viewport 仅作为布局稳定性验证，不构成移动端产品适配承诺

## 6. 验证基线

涉及 ArtDeco 代码改动时，至少确认：

- `npx vue-tsc --noEmit`
- ArtDeco token 合规检查
- 涉及 Layout / 路由 / 菜单时运行 `bash scripts/run_e2e_pm2.sh`
- 若使用 PM2 现有前端复用模式执行 Playwright，需显式说明 `PLAYWRIGHT_EXTERNAL_FRONTEND=1`

报告时必须写实际结果，不允许再写固定文案：

- 实际执行命令
- 浏览器项目
- 通过 / 失败 / 跳过数量
- PM2 服务地址与状态

### 6.1 当前实施基线快照（2026-04-19）

- `PM2`
  - `mystocks-backend` -> `http://localhost:8020`
  - `mystocks-frontend` -> `http://localhost:3020`
- 稳定 E2E 子集：
  - `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:stable`
  - `chromium`
  - `10 passed / 0 failed / 0 skipped`

## 7. 与其他文档的关系

- 入门看 `ARTDECO_START_HERE.md`
- 目录看 `ARTDECO_MASTER_INDEX.md`
- 设计契约看 `DESIGN.md`
- 组件清单看 `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- 运行时摘要看 `docs/api/ArtDeco_System_Architecture_Summary.md`
- 历史基准看 `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`
- 活跃前端路由目录真相看 `docs/guides/frontend-structure.md`
