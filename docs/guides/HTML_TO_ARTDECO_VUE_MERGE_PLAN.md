# 将转换后的Vue页面合并到ArtDeco前缀页面方案

根据您的澄清，目标是将 `Dashboard.vue`、`Market.vue` 等已转换页面中的布局和功能安排，吸收合并到现有的、已具备ArtDeco风格的 `ArtDecoDashboard.vue`、`ArtDecoMarketData.vue` 等页面中。

这需要对每个页面进行细致的代码合并，确保 ArtDeco 风格的设计得以保留和增强，同时整合新页面的功能和布局优势。

## 🎯 核心合并策略

1.  **ArtDeco风格优先**：始终以 `ArtDeco*` 文件的视觉风格和组件为基础。
2.  **功能与布局吸收**：将已转换页面 (`*.vue`) 的独特布局结构、Element Plus 组件（或其他通用组件）的功能逻辑，迁移到 `ArtDeco*` 页面中。
3.  **组件化替换**：迁移过程中，将已转换页面中使用的通用组件（如 Element Plus 组件）替换为项目已有的 ArtDeco 专用组件。如果ArtDeco组件库中没有直接对应的，则进行样式适配或创建新的ArtDeco组件。
4.  **数据与逻辑整合**：合并生命周期钩子、响应式数据、计算属性和方法，解决命名冲突。
5.  **样式适配**：将已转换页面中的 `<style>` 块内容适配为使用 ArtDeco 设计令牌 (`artdeco-tokens.scss`)，并整合到 `ArtDeco*` 文件的样式中。

## 🚀 合并实施步骤 (针对每个页面对)

**以下将以 `Dashboard.vue` 合并到 `ArtDecoDashboard.vue` 为例，详细说明操作流程。** 其他页面的合并将遵循类似原则。

### 示例合并：`Dashboard.vue` (源) INTO `ArtDecoDashboard.vue` (目标)

**文件路径**：
*   **源文件**：`web/frontend/src/views/Dashboard.vue`
*   **目标文件**：`web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`

#### **步骤 1: 备份文件** (重要)

在开始任何合并操作之前，请务必备份目标文件和源文件：
```bash
cp web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue.bak
cp web/frontend/src/views/Dashboard.vue web/frontend/src/views/Dashboard.vue.bak
```

#### **步骤 2: 分析和准备**

1.  **理解 `ArtDecoDashboard.vue` 的结构和风格**：
    *   **ArtDeco特性**：已有的戏剧性页面头部 (`ArtDecoHeader`)，市场全景仪表盘 (`market-panorama`)，可折叠面板 (`ArtDecoCollapsible`)，大量使用的 `ArtDecoCard`, `ArtDecoStatCard`, `ArtDecoIcon`, `ArtDecoBadge`, `ArtDecoButton`。
    *   **布局**：`artdeco-dashboard` 作为根容器，其内包含了多列网格布局（`content-grid`）、增强型资金流向、市场指标等。
    *   **样式**：使用纯ArtDeco风格的SCSS，大量引用 `artdeco-tokens.scss` 变量。
2.  **理解 `Dashboard.vue` 的核心内容和布局**：
    *   **布局**：`dashboard-container`，包含 `dashboard-header`、`stats-grid`（4列统计卡片）、`main-grid`（2/1列图表和表格）。
    *   **功能**：ECharts 图表（市场热度、行业资金流向）、Element Plus 表格（板块表现）、`BloombergStatCard`。
    *   **逻辑**：`echarts` 初始化逻辑、`loadData`、`handleRetry`、`handleRefresh`、以及 Element Plus 表格的数据和方法。
3.  **识别冲突点和集成点**：
    *   **头部**：`ArtDecoDashboard.vue` 有 `ArtDecoHeader`，`Dashboard.vue` 有 `dashboard-header`。应保留 `ArtDecoHeader`，并将其内容（如 title/subtitle/actions）从 `Dashboard.vue` 的 `dashboard-header` 中吸收过来。
    *   **统计卡片**：`Dashboard.vue` 有 `stats-grid` + `BloombergStatCard`。`ArtDecoDashboard.vue` 也有 `ArtDecoStatCard` 和类似的网格布局（如 `fund-flow-grid`, `indicators-grid`）。应将 `Dashboard.vue` 的统计卡片数据和布局集成到 `ArtDecoDashboard.vue` 现有的 `ArtDecoStatCard` 网格布局中。
    *   **图表**：`Dashboard.vue` 有两个ECharts图表。`ArtDecoDashboard.vue` 目前没有直接的ECharts图表区域，需要新增或整合到现有卡片中。
    *   **表格**：`Dashboard.vue` 有 Element Plus 表格。需要将表格数据和功能集成，并使用ArtDeco风格的表格组件（如果存在）或对原生HTML `<table>` 进行样式化。
    *   **逻辑**：两个文件都有数据 (`ref`)、计算属性 (`computed`)、生命周期钩子 (`onMounted`, `onUnmounted`) 和方法。需要仔细合并这些。

#### **步骤 3: 合并 `<script setup>` 逻辑**

将 `Dashboard.vue` 中的所有 `<script setup>` 逻辑迁移到 `ArtDecoDashboard.vue` 的 `<script setup>` 块中。

1.  **导入**：将 `Dashboard.vue` 中所有必要的导入（`ref`, `onMounted`, `nextTick`, `echarts`, `ECharts`, `EChartsOption`, `ElCard`, `ElButton`, `ElTable`, `ElTableColumn`, `ElTag`, `BloombergStatCard` 等）合并到 `ArtDecoDashboard.vue` 的 `<script setup>` 中。
    *   **注意**：`El*` 和 `BloombergStatCard` 需替换为 `ArtDeco*` 组件。ECharts可以保留。
2.  **数据声明**：将 `Dashboard.vue` 中的所有 `ref` (如 `loading`, `activeMarketTab`, `activeSectorTab`, `industryStandard`, `favoriteStocks`, `marketTabs`, `sectorTabs` 等) 合并到 `ArtDecoDashboard.vue` 中。解决命名冲突（例如，如果两者都有 `loading`，则将其合并为一个 `loading` 状态）。
3.  **方法和计算属性**：将 `Dashboard.vue` 中的所有方法 (`getSectorData`, `getChangeClass`, `getSignalVariant`, `updateIndustryChart`, `updateMarketHeatChart`, `initCharts`, `loadData`, `handleRetry`, `handleRefresh`) 合并到 `ArtDecoDashboard.vue`。
    *   **注意**：ECharts相关的 `marketHeatChartRef`, `industryChartRef` 也需一同迁移。
    *   **生命周期钩子**：合并 `onMounted` 和 `onUnmounted` 中的逻辑。确保 `initCharts()` 和 `loadData()` 在 `onMounted` 中被调用，并且 `timeInterval` 在 `onUnmounted` 中被清除。

#### **步骤 4: 合并 `<template>` 结构**

仔细地将 `Dashboard.vue` 的布局结构和功能区块融入 `ArtDecoDashboard.vue` 的 `<template>` 中。

1.  **头部**：`ArtDecoDashboard.vue` 已经有 `ArtDecoHeader`。将 `Dashboard.vue` `dashboard-header` 中的标题 (`MARKET OVERVIEW`, `REAL-TIME MARKET INTELLIGENCE & PORTFOLIO MONITORING`) 合并到 `ArtDecoHeader` 的 `title` 和 `subtitle` prop 中。
2.  **统计卡片**：将 `Dashboard.vue` 的 `stats-grid` 部分，替换 `BloombergStatCard` 为 `ArtDecoStatCard`，并整合到 `ArtDecoDashboard.vue` 的 `market-panorama` 区域，或者创建一个新的区域来放置这些通用统计。
    *   **Element Plus组件替换**：将 `el-card` 替换为 `ArtDecoCard`。
    *   **图表集成**：在 `ArtDecoDashboard.vue` 的合适位置（例如 `market-panorama` 的某个 `ArtDecoCard` 内部）添加 `marketHeatChartRef` 和 `industryChartRef` 对应的 `<div>` 元素。
    *   **表格集成**：将 `Dashboard.vue` 的 Element Plus 表格部分 (`el-table`) 迁移过来。由于没有现成的 `ArtDecoTable` 组件，需要：
        *   **方案A (推荐)**：将 `el-table` 的核心功能（数据绑定、列定义）迁移到 `ArtDecoDashboard.vue`，并对其进行样式定制，使其符合ArtDeco风格。可以创建一个私有的 `ArtDecoDashboardTable.vue` 组件封装。
        *   **方案B**：如果 `el-table` 的样式通过 `element-plus-override.scss` 已经足够 ArtDeco 化，则可以继续使用，但要明确记录其依赖。

#### **步骤 5: 合并 `<style scoped lang="scss">`**

将 `Dashboard.vue` 中的 `<style>` 块内容迁移到 `ArtDecoDashboard.vue` 的 `<style>` 块中。

1.  **令牌化**：将 `Dashboard.vue` 中使用的通用CSS变量（如 `var(--color-bg-primary)`）替换为 ArtDeco 设计令牌（`var(--artdeco-bg-global)`）。
2.  **选择器适配**：调整 `Dashboard.vue` 的CSS选择器，使其与合并后的 `ArtDecoDashboard.vue` 的DOM结构匹配。
3.  **组件样式覆盖**：如果 `Dashboard.vue` 有针对 Element Plus 组件的样式，考虑如何将其适配到 ArtDeco 组件上。
4.  **去重**：删除重复的样式定义。

#### **步骤 6: 路由和引用清理**

1.  **删除 `web/frontend/src/views/Dashboard.vue`**：一旦所有内容和功能都已成功合并到 `ArtDecoDashboard.vue` 中，就可以删除 `Dashboard.vue`。
2.  **更新导入**：检查 `web/frontend/src/main.js` 或其他文件中是否仍有对 `Dashboard.vue` 的直接导入，并将其删除或更新。

## 🗺️ 后续页面合并清单

完成 `Dashboard.vue` 到 `ArtDecoDashboard.vue` 的合并后，请按照以下列表依此进行其他页面的合并：

1.  **`Market.vue`** (源) **INTO** **`ArtDecoMarketData.vue`** (目标)
    *   **注意**：`Market.vue` 整合了 `market-data.html` 和 `market-quotes.html` 的功能。需要确保 `ArtDecoMarketData.vue` 能够处理这两种模式，可能需要引入选项卡或不同的视图状态。
2.  **`Stocks.vue`** (源) **INTO** **`ArtDecoStockManagement.vue`** (目标)
3.  **`Analysis.vue`** (源) **INTO** **`ArtDecoDataAnalysis.vue`** (目标)
4.  **`RiskMonitor.vue`** (源) **INTO** **`ArtDecoRiskManagement.vue`** (目标)
5.  **`TradingManagement.vue`** (源) **INTO** **`ArtDecoTradingManagement.vue`** (目标)
6.  **`BacktestAnalysis.vue`** (源) **INTO** **`ArtDecoTradingCenter.vue`** (目标)
7.  **`Settings.vue`** (源) **INTO** **`ArtDecoSettings.vue`** (目标)

## ✅ 验证和测试

每次合并完成后：

1.  **本地运行**：通过 `npm run dev` 或 PM2 启动项目，手动检查合并后的页面是否按预期显示和工作。
2.  **E2E测试**：重新运行 Playwright E2E 测试，特别是针对该页面的测试，确保没有引入回归。
3.  **视觉回归测试**：运行视觉回归测试，确保 ArtDeco 风格没有被破坏。

这个过程将是迭代和细致的。在您完成 `Dashboard.vue` 和 `ArtDecoDashboard.vue` 的合并后，请告知我结果，我们将继续其他页面的合并。