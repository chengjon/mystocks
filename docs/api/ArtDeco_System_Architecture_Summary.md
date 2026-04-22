# ArtDeco System Architecture Summary

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


本文档从运行时角度总结当前 ArtDeco 前端体系，重点是“现在实际上怎么跑”，而不是历史理想模型。

> 2026-04-19 对齐补充
>
> - ArtDeco 仍然是前端主要视觉与工作台体系。
> - 但当前活跃业务路由已经大量收敛到 `views/<domain>/*.vue`。
> - `artdeco-pages/**` 现在同时承担模板页、工作台块、兼容包装层和少量路由例外入口。
> - Dashboard 摘要状态已上提到 Layout header，由共享 composable 驱动。
> - `artdeco-tokens.scss` 已吸收 `DESIGN.md` 的状态机 token、金融 glow、200/400ms 过渡预算。

## 1. 当前运行时全景

ArtDeco 运行时由六层组成：

1. **路由与布局壳层**
   `web/frontend/src/router/index.ts` + `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`
2. **活跃业务域页面层**
   `web/frontend/src/views/{market,data,watchlist,strategy,trade,risk,system}/**`
3. **可复用资产层**
   `web/frontend/src/components/artdeco/**`
4. **页面工作台层**
   `web/frontend/src/views/artdeco-pages/**`
5. **设计令牌层**
   `web/frontend/src/styles/artdeco-*.scss`
6. **共享运行时状态层**
   `web/frontend/src/composables/useHeaderSummary.ts`

## 2. 不是单一容器架构，而是三种模式并存

### 2.1 模板化工作台

代表文件：

- `web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`

特点：

- 统一提供 `header / stats / tabs / content` 承载面
- 通过 `pageConfig`、`tabs`、`defaultTab` 驱动工作台壳层
- 适合风险、系统、策略类的标准工作台

### 2.2 直接 Tab 容器

代表文件：

- `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue`

特点：

- 页面内直接定义 tab rail 与 content panel
- 容器自己维护 tab 元数据与局部数据流
- 适合历史积累较深、尚未完全模板化的页面

### 2.3 功能树驱动总控容器

代表文件：

- `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`

特点：

- 左侧功能树，右侧动态组件
- 适合总控台、总入口、跨域编排场景
- 页面自身承担更强的 orchestration 职责

### 2.4 Layout 级共享摘要模式

代表文件：

- `web/frontend/src/composables/useHeaderSummary.ts`
- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`

特点：

- 页面级摘要状态通过 composable 推送到 Layout
- Layout header 统一展示“策略运行中 / 今日盈亏 / 当前时间 / 刷新动作”
- 摘要承载与业务路由解耦，页面不再各自复制顶部 header actions

## 3. 路由与配置边界

### 3.1 Router 是主入口

`web/frontend/src/router/index.ts` 当前负责：

- 挂载 `ArtDecoLayoutEnhanced.vue`
- 定义主业务域路由：`market`、`data`、`watchlist`、`strategy`、`trade`、`risk`、`system`
- 将大量 ArtDeco page/workbench 直接作为独立路由挂入

更准确地说：

- 大多数主业务页面已经挂在 `views/<domain>/*.vue`
- ArtDeco 页面作为路由入口时属于“明确声明的例外”，不能再按目录推断

### 3.2 `pageConfig.ts` 不是唯一真值

`web/frontend/src/config/pageConfig.ts` 当前是自动生成的页面配置文件，提供：

- routePath
- title / description
- apiEndpoint
- wsChannel
- component

但当前现实是：

- 它对页面元信息有价值
- 它不是所有 ArtDeco tabs 的唯一事实源
- 很多页面的 tab 结构仍然由页面自身维护

因此，架构文档不能再把 `pageConfig.ts` 写成“所有页签块都由它动态驱动”。

### 3.3 当前路由例外清单

当前确认仍由 ArtDeco 目录直接承载的代表性路由包括：

- `/dashboard` -> `views/artdeco-pages/ArtDecoDashboard.vue`
- `/strategy/signals` -> `views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- `/strategy/pos` -> `views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- `/risk/pnl` -> `views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`

当前新增的一条运行时事实：

- `/dashboard` 的顶部摘要不再完全由 `ArtDecoDashboard.vue` 本页私有渲染，而是通过 `useHeaderSummary` 上提到 `ArtDecoLayoutEnhanced.vue`

此外，`/trade/terminal` 是当前保留的非域目录例外，由 `views/TradingDashboard.vue` 提供。

## 4. 组件边界

### 4.1 Reusable Assets

`web/frontend/src/components/artdeco/**`

当前共 7 层：

- `base`
- `core`
- `business`
- `charts`
- `trading`
- `advanced`
- `specialized`

### 4.2 Page-Level Shared Fragments

`web/frontend/src/views/artdeco-pages/components/`

这不是全局组件库，而是 ArtDeco 页面系统内部共享片段层。

### 4.3 Domain Tab Blocks

`web/frontend/src/views/artdeco-pages/*-tabs/`

这些文件是域内工作台块：

- 允许页面上下文绑定
- 允许独立路由态 / 内嵌态双承载
- 默认不应跨域复用

### 4.4 ArtDeco 页面目录的当前角色

`views/artdeco-pages/**` 当前主要承载四类对象：

1. 模板化工作台页
2. 域内工作台块
3. 页面系统内部共享片段
4. 兼容包装层与少量活跃路由例外

因此，目录存在本身不代表该文件就是当前 canonical routed page。

## 5. 设计令牌事实点

当前 `web/frontend/src/styles/artdeco-tokens.scss` 明确包含：

- 字体：`Cinzel` / `Barlow` / `JetBrains Mono`
- A 股颜色：`--artdeco-rise` = 红，`--artdeco-down` = 绿
- 间距：13 个编号级别
  - `1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32`
- 语义别名：`sm / md / lg / xl`
- 紧凑变量：`compact-*`
- 金融 glow：`--artdeco-glow-profit` / `--artdeco-glow-loss`
- 过渡预算：`--artdeco-transition-quick = 200ms`、`--artdeco-transition-base = 400ms`
- 组件状态机：`--ad-*`
- tooltip / overlay / chip token

同时，当前交互与视觉优化契约还要叠加读取根目录 `DESIGN.md`，尤其是：

- 数据优先动效
- 盈亏 glow 语义
- 紧凑 / 微密度模式
- 交易面板单主按钮规则
- 200ms / 400ms 混合过渡预算
- 组件状态机与 chip / tooltip / overlay token 约束

## 6. 当前代表性页面映射

| 页面 | 模式 | 说明 |
|------|------|------|
| `ArtDecoRiskManagement.vue` | 模板化工作台 | 标准 `pageConfig + slots` 承载 |
| `ArtDecoMarketData.vue` | 直接 Tab 容器 | 容器内直写 tabs 与数据流 |
| `ArtDecoTradingCenter.vue` | 功能树驱动总控台 | 左树右内容，动态组件切换 |
| `ArtDecoLayoutEnhanced.vue + useHeaderSummary.ts` | Layout 级共享摘要 | 将 dashboard 摘要上提到布局壳层 |
| `strategy-tabs/ArtDecoStrategyManagement.vue` | 独立工作台路由 | 既可作为独立路由，也可纳入域内编排 |
| `risk-tabs/RiskOverviewTab.vue` | 域内工作台块 | 域内风险工作台入口 |

## 7. 架构结论

当前 ArtDeco 前端的准确描述不是单一“容器 - 页签块”模型，而是：

- **布局壳层统一**
- **活跃业务域路由已部分域目录化**
- **组件层分层明确**
- **页面承载模式并存**
- **路由驱动与模板化工作台共存**

后续架构治理的重点不是再创造一个抽象名词，而是继续把页面收敛到更清晰的边界：

- 哪些是 reusable assets
- 哪些是 page-level shared fragments
- 哪些是 domain tab blocks
- 哪些应该继续模板化
- 哪些运行时状态应提升到 layout-level composable，而不是继续沉积在单页 header 中
