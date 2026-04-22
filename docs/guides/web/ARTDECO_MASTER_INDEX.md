# ArtDeco Master Index

> **导航说明**:
> 本文件是文档导航或索引，不是当前规则、当前基线或当前实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内目录、链接、数量和分类如未重新生成或复核，应视为导航快照，不得直接当作当前事实。


本文件是 MyStocks 项目 ArtDeco 文档体系的唯一总目录，负责回答三件事：

1. 当前哪些文档是活跃治理文档。
2. 每份文档的职责边界是什么。
3. 遇到具体任务时应该先读哪一份。

> 2026-04-19 文档治理刷新
>
> - 保留 2026-04-01 的治理重组成果。
> - 将 ArtDeco 文档链与当前仓库路由真相、目录真相、设计契约重新对齐。
> - 明确 `artdeco-pages/**` 不再默认等于“活跃业务路由真相源”。
> - 将根目录 `DESIGN.md` 纳入当前设计契约链路。
> - 将 2026-04-19 落地的 `header summary` 共享状态、品牌 chrome 收敛、组件状态机 token 纳入当前口径。
> - 为历史上缺少 `web/` 子目录或使用旧文档命名的路径补齐兼容入口。

## 1. 文档分层

### 1.1 活跃治理文档

| 标签 | 文档 | 职责 |
|------|------|------|
| `[必读]` | [ARTDECO_START_HERE](./ARTDECO_START_HERE.md) | 单页上手入口，给第一次接手的人最短阅读路径 |
| `[必读][架构]` | [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md) | 当前 ArtDeco Fintech 的统一规格：设计身份、目录边界、运行时承载模式 |
| `[必读][设计契约]` | [DESIGN.md](../../../DESIGN.md) | 当前项目级设计系统契约，承载 ArtDeco 优化版的动效、密度、金融反馈和交互层级规则 |
| `[必读][样式真值]` | [ARTDECO_SCSS_GOVERNANCE_BASELINE](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md) | 令牌、Grid、兼容层、样式导入规范的事实源 |
| `[必读][组件]` | [ARTDECO_COMPONENT_GUIDE](./ARTDECO_COMPONENT_GUIDE.md) | 组件目录治理、`*-tabs` 铁律、放置决策树 |
| `[组件][目录]` | [ARTDECO_COMPONENTS_CATALOG](../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md) | 当前组件全景目录，覆盖 reusable assets 与 page-level workbench blocks |
| `[组件][运行时状态]` | [useHeaderSummary](../../../web/frontend/src/composables/useHeaderSummary.ts) | 当前共享头部摘要状态容器；将 Dashboard 摘要上提到 Layout header 的运行时桥接层 |
| `[页面][模板]` | [ARTDECO_PAGE_TEMPLATE_GUIDE](./ARTDECO_PAGE_TEMPLATE_GUIDE.md) | 模板化工作台页面的承载方式 |
| `[页面][验证]` | [ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT](./ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md) | 页面骨架、一致性与工作台化收敛的审计记录 |
| `[验证]` | [ARTDECO_FINTECH_IMPLEMENTATION_AUDIT](./ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md) | 活跃实现与统一规格的对账文档 |

### 1.2 运行时与历史基准文档

| 标签 | 文档 | 职责 |
|------|------|------|
| `[架构][运行时摘要]` | [ArtDeco_System_Architecture_Summary](../../api/ArtDeco_System_Architecture_Summary.md) | 从 Vue 路由、容器模式、组件边界角度总结当前运行时 |
| `[历史基准]` | [ARTDECO_V3_COMPLETE_SUMMARY](../../reports/ARTDECO_V3_COMPLETE_SUMMARY.md) | V3 升级过程与后续治理刷新之间的历史基准 |
| `[目录真相参考]` | [frontend-structure](../frontend-structure.md) | 当前前端路由入口、域目录真相与兼容包装层边界 |
| `[运行时][兼容入口]` | `web/frontend/src/styles/artdeco-main.css` | 兼容性 ArtDeco 样式入口，仍被部分布局路径使用；通过 `artdeco-colors.css` / `artdeco-variables.css` 链接入兼容 token；不是当前 token 真值来源 |

### 1.3 兼容入口

以下兼容入口保留是为了兼容历史报告、审核记录和外部引用；真实内容仍在 `docs/guides/web/`：

| 兼容路径 | 指向 |
|----------|------|
| [docs/guides/ARTDECO_MASTER_INDEX.md](/opt/claude/mystocks_spec/docs/guides/ARTDECO_MASTER_INDEX.md) | `docs/guides/web/ARTDECO_MASTER_INDEX.md` |
| [docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md](/opt/claude/mystocks_spec/docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md) | `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md` |
| [docs/guides/ARTDECO_COMPONENT_GUIDE.md](/opt/claude/mystocks_spec/docs/guides/ARTDECO_COMPONENT_GUIDE.md) | `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` |
| [docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md](/opt/claude/mystocks_spec/docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md) | `docs/api/ArtDeco_System_Architecture_Summary.md` |

## 2. 推荐阅读顺序

如果你是第一次接手 ArtDeco：

1. [ARTDECO_START_HERE](./ARTDECO_START_HERE.md)
2. [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
3. [DESIGN.md](../../../DESIGN.md)
4. [ARTDECO_SCSS_GOVERNANCE_BASELINE](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md)
5. [ARTDECO_COMPONENT_GUIDE](./ARTDECO_COMPONENT_GUIDE.md)
6. [ArtDeco_System_Architecture_Summary](../../api/ArtDeco_System_Architecture_Summary.md)
7. [ARTDECO_COMPONENTS_CATALOG](../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md)

## 3. 按任务找文档

| 任务 | 优先文档 |
|------|----------|
| 判断当前 ArtDeco 到底是什么 | `ARTDECO_START_HERE.md` |
| 判断“现在该按什么规则实现” | `ARTDECO_FINTECH_UNIFIED_SPEC.md` |
| 判断动效、密度、金融反馈、主按钮层级 | `DESIGN.md` |
| 判断共享头部摘要、Dashboard 到 Layout 的摘要桥接 | `web/frontend/src/composables/useHeaderSummary.ts` + `ArtDecoLayoutEnhanced.vue` + `useArtDecoDashboard.ts` |
| 改 token / 字体 / 间距 / glow / Grid | `ARTDECO_SCSS_GOVERNANCE_BASELINE.md` |
| 判断组件放哪里 | `ARTDECO_COMPONENT_GUIDE.md` |
| 查现有组件与页面块存量 | `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` |
| 理解页面模板与工作台壳层 | `ARTDECO_PAGE_TEMPLATE_GUIDE.md` |
| 理解当前运行时架构 | `ArtDeco_System_Architecture_Summary.md` |
| 判断当前活跃路由入口是不是 `artdeco-pages/**` | `docs/guides/frontend-structure.md` + `web/frontend/src/router/index.ts` |
| 查历史基线与升级背景 | `ARTDECO_V3_COMPLETE_SUMMARY.md` |
| 查实现/页面是否已治理到位 | `ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md` / `ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md` |

## 4. 当前目录口径

当前 ArtDeco 文档体系按三层理解：

1. **治理层**
   `START_HERE`、`UNIFIED_SPEC`、`DESIGN.md`、`SCSS_GOVERNANCE_BASELINE`、`COMPONENT_GUIDE`
2. **运行时与目录层**
   `COMPONENTS_CATALOG`、`System_Architecture_Summary`、`PAGE_TEMPLATE_GUIDE`、`frontend-structure`
3. **验证与历史层**
   `FINTECH_IMPLEMENTATION_AUDIT`、`FINTECH_PAGE_COMPOSITION_AUDIT`、`V3_COMPLETE_SUMMARY`

## 4.1 当前入口口径补充

当前仓库必须同时区分两类“入口”：

1. **活跃业务路由入口**
   以 `web/frontend/src/router/index.ts` 和 `web/frontend/src/views/<domain>/*.vue` 为主真相源。
2. **ArtDeco 工作台与兼容入口**
   以 `web/frontend/src/views/artdeco-pages/**` 为主，承担模板页、工作台块、兼容包装层和少量例外路由。

当前已知例外：

- `/dashboard` 仍由 `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` 提供
- `/trade/terminal` 仍由 `web/frontend/src/views/TradingDashboard.vue` 提供
- `/strategy/signals` 仍由 `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` 提供
- `/strategy/pos` 仍由 `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` 提供
- `/risk/pnl` 仍由 `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` 提供

因此，不能再把 `artdeco-pages/**` 直接写成“前端当前所有主业务页面入口”。

## 4.2 2026-04-19 新增对齐点

本轮文档链需要额外吸收以下当前代码事实：

1. `DESIGN.md` 已从“设计参考”升级为当前设计契约主链文件，明确承载：
   - 数据优先动效
   - `200ms / 400ms` 混合过渡预算
   - `glow-profit / glow-loss`
   - `compact / micro-density`
   - 单交易面板单主按钮
2. `web/frontend/src/styles/artdeco-tokens.scss` 已落地：
   - `--artdeco-transition-quick`
   - `--artdeco-transition-base`
   - `--artdeco-glow-profit`
   - `--artdeco-glow-loss`
   - `--ad-*` 组件状态机 token
   - chip / tooltip / overlay 语义 token
3. `ArtDecoLayoutEnhanced.vue` 已承载共享头部摘要，`ArtDecoDashboard.vue` 不再独占顶部摘要区。
4. `useHeaderSummary.ts` 是当前共享摘要状态的真值桥接层；这类 2+ 消费者 composable 属于 `src/composables/`，符合 `STANDARDS.md` 的 View-Local / shared composable 分层规则。
5. 品牌 chrome 当前已做去装饰化收敛：
   - `ArtDecoHeader.vue` 的默认 logo 文本清空
   - `ArtDecoCollapsibleSidebar.vue` 的品牌框边线移除
   - 运行时更偏向“数据优先、装饰后退”

## 5. 不再作为当前唯一事实源的文档

以下文档仍可保留为历史参考，但不应作为新实现的直接规范：

- `ART_DECO_COMPONENT_SHOWCASE*.md`
- `mystocks-artdeco-available-components.md`
- 各类早期 ArtDeco 设计展示、阶段报告、迁移笔记

判断原则：

- 能决定“现在怎么写”的，只能是活跃治理文档和源码。
- 历史文档用来理解背景，不用来覆盖当前真值。

## 6. 维护规则

- 新增 ArtDeco 文档时，必须先判断它属于治理层、运行时层还是历史层，再回填到本索引。
- 如果文档职责变了，先改本索引，再改文档正文。
- 如果文档路径变了，必须保留兼容入口或同步修正所有上游引用。
- 当 `web/frontend/src/styles/artdeco-tokens.scss`、`DESIGN.md`、`web/frontend/src/views/artdeco-pages/**`、`web/frontend/src/components/artdeco/**`、`web/frontend/src/router/index.ts` 的结构发生变化时，至少同步更新：
  - 本索引
  - `ARTDECO_FINTECH_UNIFIED_SPEC.md`
  - `ARTDECO_COMPONENTS_CATALOG.md`
  - `ArtDeco_System_Architecture_Summary.md`
  - `ARTDECO_V3_COMPLETE_SUMMARY.md`
