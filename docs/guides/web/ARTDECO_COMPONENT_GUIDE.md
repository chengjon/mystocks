# ArtDeco Component Development Guide

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文档定义 ArtDeco 组件与页面块的放置规则、命名边界和开发准入标准。

> 2026-04-18 补充
>
> 当前前端已存在 `views/<domain>/*.vue` 的 canonical routed page 主线。
> 因此本指南除了回答“组件放哪”，还必须回答“这是 reusable asset、ArtDeco 工作台块，还是业务路由入口”。
>
> 2026-04-19 再补充：
>
> 共享布局级状态桥接（如 `useHeaderSummary.ts`）也需要纳入放置规则；它既不是 Vue 组件，也不是页面私有 composable。

## 1. 先记住 6 条铁律

1. `src/components/artdeco/**` 只放可持续沉淀的可复用资产。
2. `views/artdeco-pages/components/` 只放 ArtDeco 页面系统内部共享片段。
3. `views/artdeco-pages/*-tabs/` 只放域内工作台块，不默认跨域复用。
4. 页面专属逻辑不要上提到 `base / core`，临时页面块不要伪装成全局组件。
5. 活跃业务路由页优先放 `views/<domain>/*.vue`，不是默认放进 `artdeco-pages/**`。
6. 跨 Layout / Page 的共享运行时状态，若已有 2+ 消费者，放 `src/composables/`，不要伪装成组件，也不要继续塞在页面私有 `composables/`。

## 2. 目录治理矩阵

| 目录 | 定位 | 可以做什么 | 不该做什么 |
|------|------|------------|------------|
| `src/components/artdeco/base/` | 原子 UI | Button、Card、Input、Alert | 承载页面编排逻辑 |
| `src/components/artdeco/core/` | 壳层与框架能力 | Header、Breadcrumb、Skeleton、Icon、Toast | 承载某个业务域的专属流程 |
| `src/components/artdeco/business/` | 通用业务交互 | FilterBar、DateRange、Rule、Status | 绑定单一页面状态树 |
| `src/components/artdeco/charts/` | 通用图表 | Chart、KLine、Matrix、Depth | 写死单域业务语义 |
| `src/components/artdeco/trading/` | 交易域可复用组件 | OrderBook、Ticker、TradeForm | 绑定某一页的局部容器状态 |
| `src/components/artdeco/advanced/` | 高阶分析组件 | CapitalFlow、ChipDistribution、Sentiment | 变成临时页面拼装代码 |
| `src/components/artdeco/specialized/` | 强专题组件 | LongHuBang、BlockTrading | 冒充全局通用组件 |
| `views/artdeco-pages/components/` | 页面系统内部共享片段 | 在多个 ArtDeco 页面工作台之间复用 | 当作通用 UI 组件库 |
| `views/artdeco-pages/*-tabs/` | 域内工作台块 | 独立路由块、Tab block、内嵌块 | 随意跨域 import |
| `views/<domain>/` | 活跃业务路由页面 | 作为 router canonical entry，承载域页面组合 | 伪装成通用组件目录 |
| `src/composables/` | 跨 Layout / Page 的共享状态桥接 | 摘要状态、统一刷新动作、布局级运行时共享 | 当作页面私有 composable 堆放点 |

## 3. `*-tabs` 与 `components/` 的铁律

### 3.1 `*-tabs/`

适用条件：

- 属于某个业务域或某个页面工作流
- 绑定当前页面的 tabs、筛选、路由或局部状态
- 更像工作台块，而不是组件库资产

规则：

- 默认不跨域 import
- 可以保留页面级上下文
- 如果未来要跨域长期复用，应提升到更高层

### 3.2 `views/artdeco-pages/components/`

适用条件：

- 在多个 ArtDeco 页面/工作台之间复用
- 仍然带页面系统语境，但不是全站原子 UI
- 适合沉淀页面内部共享片段

规则：

- 允许被多个 ArtDeco 页面复用
- 不要承载顶层路由/页面初始化逻辑
- 不要与 `src/components/artdeco/` 重复建设

> 兼容说明
>
> 历史审核材料常写成 `components/[Domain]`。当前仓库现实更接近“平铺的 `views/artdeco-pages/components/` 共享层 + `*-tabs/` 域块层”。如果未来重新切分成 `components/[domain]/`，仍应沿用同一铁律：只放可复用的页面共享片段，不放页面专属逻辑。

## 4. 决策树

### 4.1 新能力先问 4 个问题

1. 它是不是纯视觉 / 通用交互？
2. 它是不是会在多个页面或多个域中稳定复用？
3. 它是不是强依赖当前页面的 tab、路由、筛选或局部状态？
4. 它是不是当前业务路由的 canonical 页面入口？
5. 它是不是跨 Layout / Page 的共享运行时状态？

### 4.2 放置建议

| 情况 | 应放目录 |
|------|----------|
| 原子 UI | `base/` |
| 壳层、导航、状态、框架能力 | `core/` |
| 通用业务交互 | `business/` |
| 通用图表能力 | `charts/` |
| 交易域稳定复用 | `trading/` |
| 高阶分析稳定复用 | `advanced/` |
| 强专题、难泛化 | `specialized/` |
| 多个 ArtDeco 页面内部共享 | `views/artdeco-pages/components/` |
| 单域工作台块 / 单页 tabs 块 | `views/artdeco-pages/*-tabs/` |
| 当前业务路由的主页面 | `views/<domain>/` |
| 跨 Layout / Page 的共享状态桥接 | `src/composables/` |

### 4.3 关于兼容包装层

如果某个旧 ArtDeco 页面仍然存在，是因为：

- 需要兼容旧 import
- 需要兼容嵌入式工作台用法
- 需要作为过渡壳层包装新域目录页面

此时规则是：

- 保持薄封装
- 不再把它扩写成新的业务真值
- 文档中明确标成 wrapper / compatibility / embedded shell

### 4.4 关于共享摘要状态

`useHeaderSummary.ts` 是当前明确的正例：

- 生产者：`views/artdeco-pages/composables/useArtDecoDashboard.ts`
- 消费者：`layouts/ArtDecoLayoutEnhanced.vue`
- 角色：共享运行时状态桥接

因此它应放在 `src/composables/`，而不是：

- 继续留在某个单页 `composables/` 私有目录
- 伪装成 `components/artdeco/core/` 组件
- 被误写成 token 或 pageConfig 真值

## 5. 样式与实现规则

### 5.1 样式导入

新代码优先：

```scss
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-grid.scss' as *;
```

规则：

- 禁止新增硬编码颜色、间距、圆角、阴影、过渡
- 新代码优先 `@use`，不要继续扩散 `@import`
- 涉及金融语义时，用 `artdeco-financial.scss` 提供的语义
- 交互节奏、密度模式、主按钮层级按根目录 `DESIGN.md` 执行
- 组件状态切换优先绑定 `artdeco-tokens.scss` 中的 `--ad-*` 状态机 token
- 金融 glow 反馈优先使用 `--artdeco-glow-profit` / `--artdeco-glow-loss`
- filter chip / status chip / compact badge 语义优先落在 `base/ArtDecoBadge.vue`，不要在 `artdeco-pages/**` 或域块样式里继续定义局部 `.status-chip` / `.status-badge`
- `business/ArtDecoStatus.vue` 只负责 dot-status 呈现；若需要胶囊态状态标签，应回到 `ArtDecoBadge.vue`

### 5.2 字体与间距

当前真值：

- 标题：`Cinzel`
- 正文：`Barlow`
- 数值与元信息：`JetBrains Mono`
- 间距：13 个编号级别 + 语义别名 + 紧凑变量

### 5.3 A 股颜色

- 上涨 / 盈利：红
- 下跌 / 亏损：绿

不要自行发明第二套市场语义。

## 6. 桌面端约束

- 当前项目是桌面端工作台
- 可以做桌面端 Grid 列数折叠
- 不做移动端 / 平板适配
- 不要把“响应式治理”写成移动端适配任务

## 7. 业务路由入口与 ArtDeco 工作台的分工

当前推荐分工是：

- `views/<domain>/*.vue`：面向导航、菜单、路由的 canonical entry
- `components/artdeco/**`：长期复用资产
- `views/artdeco-pages/components/`：工作台内部共享片段
- `views/artdeco-pages/*-tabs/`：工作台域块、独立 tab block、兼容工作台入口

例外允许存在，但必须在 router 中明确声明，而不是靠目录习惯默认成立。

## 8. 业务路由页面 Grammar 与验证 Hook

当 ArtDeco 工作从单个页面 craft 进入多页面治理时，先标准化 route grammar，再考虑共享组件。

### 8.1 标准 Route Grammar

数据密集型业务路由默认按这个顺序评审和实施：

```text
compact operational header
-> first-level review/control lens
-> runtime trust/status strip
-> primary data surface
-> secondary evidence panels
```

已验证试点包括：

- `web/frontend/src/views/market/Realtime.vue`
- `web/frontend/src/views/risk/Alerts.vue`
- `web/frontend/src/views/trade/Center.vue`
- `web/frontend/src/views/trade/Signals.vue`

偏离该顺序时，必须在 critique、shape brief、implementation report 或路由设计文档中说明原因。这个 grammar 只定义页面结构和验证义务，不自动授权 router、API contract、frontend API client 或 shared component 改动。

### 8.2 Runtime Trust / Status 词汇

route-level trust/status strip 必须诚实暴露数据状态。可用词汇包括：

- `loading` / `pending` / syncing
- `verified`
- `refreshing`
- `stale`
- `degraded`
- `empty`
- `unavailable`
- `refresh-failed`

如果刷新失败但页面仍有上次 verified snapshot，默认保留可见数据，并在 trust/status strip 中标明 stale 或 degraded。不要把 stale data 伪装成 live data，也不要把可用快照替换成无关 empty state。

### 8.3 Route-Level E2E Hook 标准

页面 craft slice 新增或调整以下可见面时，应优先提供 route-level hook，避免 E2E 依赖 nested shared component internals：

| Surface | 建议后缀 |
|---|---|
| page root | `*-page` |
| operational header | `*-header` |
| primary refresh/action | `*-refresh` / `*-primary-action` |
| review/control lens | `*-review-lens` / `*-control-lens` |
| runtime trust/status strip | `*-trust-strip` / `*-status-strip` |
| primary data surface | `*-table` / `*-list` / `*-primary-surface` |
| runtime message | `*-runtime-message` |
| empty state | `*-empty-state` |
| unavailable/error state | `*-error-state` / `*-unavailable-state` |
| retry action | `*-retry` |

命名应以 route 语义为前缀，例如 `trade-signals-trust-strip`。旧试点如果还没有 hook，后续触达时应在批准范围内补齐，或在报告中记录 defer 理由。

### 8.4 Shared Component Extraction Gate

不要因为四页长得像就直接创建 `ArtDecoRouteHeaderBand`、`ArtDecoReviewLens` 或 `ArtDecoRuntimeTrustStrip`。

抽共享组件前必须另起审批，并明确：

- props / slots / events
- 支持的 runtime state vocabulary
- 哪些语义仍留在 route-local
- token 使用规则
- E2E hook 命名
- migration order
- rollback plan

共享组件不得拥有 API orchestration、route metadata、router config、backend contract、frontend API client、金融行语义或页面专属 fallback copy。

## 9. 命名建议

当前仓库命名并不完全统一，因此本指南不强推机械改名；但新文件建议满足以下原则：

- 能看出业务域或职责
- 与所在目录语义一致
- 避免同层出现两个职责接近但命名风格完全不同的文件

比“统一成单一公式”更重要的是：目录边界正确、职责边界正确。

## 10. 提交前检查

至少确认：

- 新文件放在了正确目录
- 没有把页面专属逻辑提到 `base/core`
- 没有把域内工作台块错误抽成全局组件
- 没有把 canonical routed page 错放到 `artdeco-pages/**`
- 数据密集型 route craft 已评估 route grammar 和 runtime trust/status strip
- 新增页面可见面时，已优先提供 route-level E2E hook 或记录 defer 理由
- 没有把 route-local stale snapshot / fallback copy / API orchestration 抽成共享组件
- 没有新增硬编码视觉值
- 新样式优先使用 `@use`
- A 股语义没有写反

若改动涉及前端构建 / 类型检查 / E2E / 服务启动，还应按项目统一门禁报告：

- 结构性语法错误
- 类型错误是否高于基线
- PM2 服务状态
- 实际 E2E 执行结果

## 11. 与其他文档的关系

- 先上手：`ARTDECO_START_HERE.md`
- 看总目录：`ARTDECO_MASTER_INDEX.md`
- 看运行时架构：`docs/api/ArtDeco_System_Architecture_Summary.md`
- 看组件清单：`web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- 看样式真值：`docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
- 看设计契约：`DESIGN.md`
- 看当前前端路由目录真相：`docs/guides/frontend-structure.md`
