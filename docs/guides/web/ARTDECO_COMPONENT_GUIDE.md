# ArtDeco Component Development Guide (V3.1 Governance Baseline)

本文档定义了 MyStocks 项目中 ArtDeco 风格组件的工程标准与交付规范，并作为 V3.1 Governance Baseline 的开发准入文档。

> 2026-03-25 状态说明
>
> - 本文档仍然有效，但它只回答“组件怎么组织、怎么开发”。
> - 如果你是第一次接手，请先读：
>   - `docs/guides/web/ARTDECO_START_HERE.md`
>   - `docs/guides/web/ARTDECO_MASTER_INDEX.md`
> - 如果你要判断样式真值、兼容层边界、页面骨架，请结合：
>   - `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
>   - `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
>   - `docs/guides/web/ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`

## 1. 组件组织铁律 (Architectural Iron Law)

为防止分拆过程中的目录膨胀与逻辑耦合，必须严格遵守以下确权定义：

### 1.1 `components/[Domain]/` —— 稳定、可复用、跨页面
*   **存放内容**: 领域内通用业务组件；可被多个页面、多个 Tabs 复用；纯展示或纯逻辑封装，不绑定特定页面。
*   **核心规则**:
    *   **必须可复用**: 严禁存放仅某个特定 Tab 专属的代码。
    *   **无页面逻辑**: 禁止写页面级初始化或复杂的全局状态修改逻辑。
    *   **稳定可测试**: 必须具备良好的单元测试基础。

### 1.2 `[Domain]-tabs/` —— 页面级、页签块、不可复用
*   **存放内容**: 属于某个业务页面的子面板/子路由；业务逻辑重、一次性、页面专属。
*   **核心规则**:
    *   **专属分拆**: 仅用于拆分超大 Vue 文件，不做通用组件。
    *   **禁止外导**: 严禁被该页面以外的任何页面 `import`。
    *   **逻辑闭环**: 允许包含该 Tab 专属的复杂业务逻辑。

> **⚠️ 铁律**: `tabs/` 目录只放 “页面块”，`components/` 只放 “可复用组件”。

## 2. 物理目录映射 (Physical Mapping)

| 目录路径 | 属性 | 适用场景示例 |
|:---|:---|:---|
| `src/components/artdeco/base/` | 原子 UI | Button, Card, Input |
| `src/components/artdeco/core/` | 框架级能力 | Header, Breadcrumb, Icon, FunctionTree |
| `src/components/artdeco/business/` | 通用业务交互 | FilterBar, DateRange, AlertRule, DataSourceTable |
| `src/components/artdeco/charts/` | 通用图表 | ArtDecoChart, KLineChartContainer, PerformanceTable |
| `src/components/artdeco/trading/` | 交易领域组件 | Ticker, OrderBook, PositionCard, TradeForm |
| `src/components/artdeco/advanced/` | 高阶分析组件 | CapitalFlow, MarketPanorama, SentimentAnalysis |
| `src/components/artdeco/specialized/` | 高定制专题组件 | BlockTrading, LongHuBang |
| `src/views/artdeco-pages/components/[domain]/` | 通用业务 | `ArtDecoRealtimeMonitor`, `ArtDecoRiskGauge` |
| `src/views/artdeco-pages/[domain]-tabs/` | 页面块 | `MarketFundFlowTab`, `StrategyConfigTab` |

## 3. 组件选型决策树 (Decision Tree)

这部分回答一个高频问题：

> “我要做一个新能力，到底是新建基础组件、领域组件，还是直接写在页面里？”

### 3.1 第一步：先判断是不是页面块

如果同时满足以下条件，优先放到 `views/artdeco-pages/[domain]-tabs/` 或当前页面域：

- 只服务于一个页面或一个 Tab
- 强绑定当前页面状态、路由或局部业务流程
- 其他页面几乎不会复用

不要急着抽成全局组件。

### 3.2 第二步：如果要复用，再判断复用层级

按这个顺序选：

1. **`base/`**
   适合原子 UI。
   例：按钮、卡片、输入框、折叠面板、对话框。
2. **`core/`**
   适合页面骨架、导航、反馈、框架级能力。
   例：Header、Breadcrumb、Icon、Skeleton、LoadingOverlay。
3. **`business/`**
   适合通用业务交互。
   例：筛选条、告警规则、日期范围、数据源表格。
4. **`charts/`**
   适合跨页面通用图表。
   例：ArtDecoChart、K 线容器、PerformanceTable。
5. **`trading/`**
   适合交易领域专用组件。
   例：OrderBook、TradeForm、PositionCard。
6. **`advanced/`**
   适合复杂分析结果展示。
   例：CapitalFlow、ChipDistribution、SentimentAnalysis。
7. **`specialized/`**
   适合高定制专题资产。
   例：LongHuBang、BlockTrading。

### 3.3 快速判断口诀

- **跨页面 + 原子交互** -> `base`
- **跨页面 + 页面骨架/导航/反馈** -> `core`
- **跨页面 + 通用业务面板** -> `business`
- **跨页面 + 图表能力** -> `charts`
- **只在交易域稳定复用** -> `trading`
- **只在复杂分析域稳定复用** -> `advanced`
- **强专题、高定制、不宜泛化** -> `specialized`
- **只给某个页面/Tab 用** -> 页面域，不要提升

## 4. 组件开发前检查

新建组件前，先完成这 4 个判断：

1. 当前仓库里是不是已经有现成组件可复用。
2. 这个能力是不是只属于当前页面。
3. 如果未来复用，复用边界是原子 UI、框架能力、业务交互，还是领域组件。
4. 它是否会把页面级逻辑错误地提升到全局组件层。

建议同时对照：

- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/guides/web/ARTDECO_START_HERE.md`
- `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`

## 5. 工程编码标准 (Engineering Standards)

### 2.1 样式导入规范 (强制)
必须使用 SCSS 且必须通过令牌系统定义样式。禁止使用内联样式或硬编码颜色。
详细规则以 [ARTDECO_SCSS_GOVERNANCE_BASELINE.md](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md) 为准。

```vue
<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.your-component {
  background: var(--artdeco-bg-card);
  padding: var(--artdeco-spacing-4);
  color: var(--artdeco-gold-primary);
}
</style>
```

说明：

*   新代码优先使用 `@use`。
*   兼容别名如 `--artdeco-accent-gold` 可以继续读取，但不应在新代码中继续扩散。

### 2.2 金融语义颜色
在显示盈亏数据时，必须调用语义别名：
*   **盈利/上涨**: 使用 `var(--artdeco-profit)` 或 `var(--artdeco-rise)`
*   **亏损/下跌**: 使用 `var(--artdeco-loss)` 或 `var(--artdeco-down)`

### 2.3 响应式网格
优先复用语义化 Grid 类或现有 Grid mixin，确保在各断点下的一致性：

```scss
@use '@/styles/artdeco-grid.scss' as *;

.stats-grid {
  display: grid;
  @include artdeco-grid-4-cols;
  gap: var(--artdeco-spacing-4);
}
```

优先级：

*   先复用 `.summary-section`、`.charts-section` 等语义化 Grid 类
*   再使用 `artdeco-grid-2-cols`、`artdeco-grid-3-cols`、`artdeco-grid-4-cols` 等 mixin
*   禁止使用不存在的伪接口，例如 `@include artdeco-grid(4)`

## 6. 页面骨架组件优先级

如果你在做新页面，默认优先从这组组件开始组合，而不是从零拼：

### P0 首选

- `ArtDecoHeader`
- `ArtDecoBreadcrumb`
- `ArtDecoIcon`
- `ArtDecoCard`
- `ArtDecoButton`
- `ArtDecoStatCard`

### P1 常用

- `ArtDecoSkeleton`
- `ArtDecoLoadingOverlay`
- `ArtDecoStatusIndicator`
- `ArtDecoToast`
- `ArtDecoCollapsible`

### P2 视场景接入

- `business/*`
- `charts/*`
- `trading/*`
- `advanced/*`
- `specialized/*`

原则：

- 先搭舞台层，再挂领域组件。
- 先复用已有骨架能力，再决定是否扩展。

## 7. 可验证性核对表 (Definition of Done)

在提交任何 ArtDeco 相关变更前，必须自测以下项目：
- [ ] **物理一致性**: 新组件是否放在了正确的分类目录下？
- [ ] **令牌完整性**: 是否所有颜色和间距都使用了 `--artdeco-*` 变量？
- [ ] **A 股符合度**: 涨跌幅颜色是否符合“红涨绿跌”规范？
- [ ] **分拆有效性**: 大型 Vue 文件是否已按 Tab 有效分拆，且父组件正确下发配置？
- [ ] **编译验证**: `npx vue-tsc --noEmit` 是否零错误？

涉及 Layout、路由或菜单结构时，还必须补：

- [ ] **PM2 冒烟**: `bash scripts/run_e2e_pm2.sh`

当前已验证通过的 E2E 口径：

- 浏览器项目：`chromium`
- 套件：`tests/navigation-consistency.spec.ts`
- 结果：`14 passed`

---
**维护者**: Frontend Architecture Team
**治理口径**: V3.1 Governance Baseline
**最后审核**: 2026-03-25 (补充组件选型决策树与页面骨架优先级)
