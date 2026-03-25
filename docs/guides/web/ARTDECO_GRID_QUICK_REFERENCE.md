# ArtDeco Grid系统快速参考

**版本**: 1.0
**创建日期**: 2026-01-22
**用途**: 快速查找和使用ArtDeco Grid布局类

> 治理说明
>
> - 当前有效规范以 [ARTDECO_SCSS_GOVERNANCE_BASELINE.md](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md) 为准。
> - 本文档聚焦 `artdeco-grid.scss` 中已经实现的类与 mixin。
> - 新代码示例优先使用 `@use`，旧 `@import` 仅视为兼容写法。

---

## 🚀 快速开始

### 1. 工具类 (最简单)

```vue
<template>
  <!-- 3列Grid -->
  <div class="artdeco-grid-3">
    <ArtDecoCard>图表1</ArtDecoCard>
    <ArtDecoCard>图表2</ArtDecoCard>
    <ArtDecoCard>图表3</ArtDecoCard>
  </div>

  <!-- 4列Grid -->
  <div class="artdeco-grid-4">
    <StatCard />
    <StatCard />
    <StatCard />
    <StatCard />
  </div>

  <!-- 自适应Grid (热力图) -->
  <div class="artdeco-grid-auto">
    <HeatmapTile v-for="item in items" :key="item.id" />
  </div>
</template>
```

---

## 📦 可用的Grid类

### 基础Grid类

| 类名 | 用途 | 桌面端 | 平板端 | 移动端 |
|------|------|--------|--------|--------|
| `.artdeco-grid-3` | Dashboard图表 | 3列 | 2列 | 1列 |
| `.artdeco-grid-4` | 统计卡片 | 4列 | 3列 | 2列→1列 |
| `.artdeco-grid-2` | 左右对比 | 2列 | 1列 | 1列 |
| `.artdeco-grid-auto` | 热力图/板块 | 自适应 | 自适应 | 2列 |
| `.artdeco-grid-cards` | 股票池/列表 | 卡片Grid | 卡片Grid | 1列 |

### 语义化Grid类 (推荐)

| 类名 | 对应HTML区域 | 列数 | 间距 |
|------|-------------|------|------|
| `.charts-section` | 图表区域 | 3列 | 24px |
| `.summary-section` | 统计卡片 | 4列 | 24px |
| `.heatmap-section` | 板块热力图 | 自适应 | 8px |
| `.flow-section` | 资金流分析 | 2列 | 24px |
| `.pool-section` | 股票池/列表 | 卡片 | 24px |
| `.nav-section` | 导航/快捷方式 | 3列 | 32px |

---

## 🎯 使用场景示例

### 场景1: Dashboard主布局

```vue
<template>
  <section class="charts-section">
    <!-- 3列图表: 指数走势、成交额、换手率 -->
    <ArtDecoKLineChartContainer :symbol="'000001'" />
    <ArtDecoKLineChartContainer :symbol="'399001'" />
    <ArtDecoKLineChartContainer :symbol="'399006'" />
  </section>

  <section class="summary-section">
    <!-- 4列统计卡片 -->
    <ArtDecoStatCard label="总市值" :value="totalMarketCap" />
    <ArtDecoStatCard label="成交额" :value="totalVolume" />
    <ArtDecoStatCard label="上涨家数" :value="upCount" />
    <ArtDecoStatCard label="下跌家数" :value="downCount" />
  </section>

  <section class="heatmap-section">
    <!-- 自适应热力图 -->
    <HeatmapCard
      v-for="sector in sectors"
      :key="sector.code"
      :sector="sector"
    />
  </section>
</template>
```

---

### 场景2: 侧边栏布局

```vue
<template>
  <div class="sidebar-layout">
    <!-- 240px固定侧边栏 -->
    <aside class="sidebar">
      <ArtDecoMenu />
    </aside>

    <!-- 自适应主内容 -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-grid.scss' as *;

.sidebar-layout {
  @include artdeco-grid-container;
  grid-template-columns: 240px 1fr;
  gap: var(--artdeco-spacing-6);
}

@media (max-width: 1024px) {
  .sidebar-layout {
    grid-template-columns: 1fr;
  }
}
</style>
```

---

### 场景3: 自定义Grid

```vue
<template>
  <div class="my-custom-grid">
    <slot />
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-grid.scss' as *;

.my-custom-grid {
  @include artdeco-grid-container;
  grid-template-columns: repeat(3, 1fr) 200px;  // 3等宽 + 200px侧边栏
  gap: var(--artdeco-spacing-6);

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
}
</style>
```

---

## 🎨 间距工具类

### Gap间距

```html
<!-- 使用gap工具类 -->
<div class="artdeco-grid-3 gap-xs">8px间距</div>
<div class="artdeco-grid-3 gap-sm">12px间距</div>
<div class="artdeco-grid-3 gap-md">16px间距</div>
<div class="artdeco-grid-3 gap-lg">24px间距 (默认)</div>
<div class="artdeco-grid-3 gap-xl">32px间距</div>
<div class="artdeco-grid-3 gap-2xl">40px间距</div>
```

### 行/列间距分离

```html
<!-- 行间距16px,列间距24px -->
<div class="row-gap-md col-gap-lg">
  <!-- Grid items -->
</div>
```

---

## 📐 对齐工具类

### 水平对齐

```html
<div class="artdeco-grid-3 justify-start">左对齐</div>
<div class="artdeco-grid-3 justify-center">居中对齐</div>
<div class="artdeco-grid-3 justify-end">右对齐</div>
<div class="artdeco-grid-3 justify-between">两端对齐</div>
<div class="artdeco-grid-3 justify-around">均匀分布</div>
```

### 垂直对齐

```html
<div class="artdeco-grid-3 items-start">顶部对齐</div>
<div class="artdeco-grid-3 items-center">垂直居中</div>
<div class="artdeco-grid-3 items-end">底部对齐</div>
<div class="artdeco-grid-3 items-stretch">拉伸填充 (默认)</div>
```

---

## 📱 响应式断点

### 断点定义

| 断点名 | 宽度 | 设备 |
|--------|------|------|
| `--artdeco-breakpoint-xs` | 480px | 超小屏 |
| `--artdeco-breakpoint-sm` | 640px | 小屏手机 |
| `--artdeco-breakpoint-md` | 1024px | 平板 |
| `--artdeco-breakpoint-lg` | 1280px | 笔记本 |
| `--artdeco-breakpoint-xl` | 1536px | 桌面显示器 |

### 响应式辅助类

```html
<!-- 移动端隐藏 -->
<div class="artdeco-hide-mobile">仅在桌面端显示</div>

<!-- 桌面端隐藏 -->
<div class="artdeco-hide-desktop">仅在移动端显示</div>

<!-- 平板及以上显示 -->
<div class="artdeco-show-tablet">平板和桌面显示</div>

<!-- 桌面及以上显示 -->
<div class="artdeco-show-desktop">仅桌面显示</div>
```

---

## 🔧 Mixin参考 (高级用法)

### 基础Grid容器Mixin

```scss
@use '@/styles/artdeco-grid.scss' as *;

.my-grid {
  @include artdeco-grid-container;
  // 生成为: display: grid; width: 100%; max-width: 1800px; margin: 0 auto;
}
```

### 列数Mixin

```scss
// 3列Grid
@include artdeco-grid-3-cols;
// 响应式: 3列 → 2列 → 1列

// 4列Grid
@include artdeco-grid-4-cols;
// 响应式: 4列 → 3列 → 2列 → 1列

// 2列Grid
@include artdeco-grid-2-cols;
// 响应式: 2列 → 1列

// 自适应Grid
@include artdeco-grid-auto;
// 自适应填充,最小120px

// 卡片Grid
@include artdeco-grid-cards;
// 自适应填充,最小300px
```

---

## 🎭 完整示例: Dashboard布局

```vue
<template>
  <div class="dashboard-container">
    <!-- 顶部标题 -->
    <h1 class="artdeco-text-display">量化交易中心</h1>

    <!-- 3列图表区域 -->
    <section class="charts-section">
      <ArtDecoKLineChartContainer :symbol="'000001'" />
      <ArtDecoKLineChartContainer :symbol="'399001'" />
      <ArtDecoKLineChartContainer :symbol="'399006'" />
    </section>

    <!-- 4列统计卡片 -->
    <section class="summary-section">
      <ArtDecoStatCard
        v-for="stat in statistics"
        :key="stat.id"
        :label="stat.label"
        :value="stat.value"
        :variant="stat.variant"
      />
    </section>

    <!-- 数据源状态表格 -->
    <section class="status-section">
      <ArtDecoDataSourceTable :data-sources="dataSources" />
    </section>

    <!-- 板块热力图 -->
    <section class="heatmap-section">
      <HeatmapCard
        v-for="sector in sectors"
        :key="sector.code"
        :sector="sector"
      />
    </section>

    <!-- 2列资金流分析 -->
    <section class="flow-section">
      <CapitalFlowChart />
      <CapitalFlowTable />
    </section>
  </div>
</template>

<style scoped>
.dashboard-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: var(--artdeco-spacing-8);  // 32px
}

section {
  margin-bottom: var(--artdeco-spacing-8);  // 32px
}
</style>
```

---

## 💡 最佳实践

### ✅ 推荐做法

1. **使用语义化类** (如 `.charts-section`) 而非工具类 (如 `.artdeco-grid-3`)
2. **复用ArtDeco间距令牌** (`var(--artdeco-spacing-6)`) 而非硬编码值
3. **优先使用响应式Grid类** (内置响应式断点)
4. **保持Grid层级简单**,避免嵌套过深

### ❌ 避免做法

1. ❌ 硬编码间距值 (`gap: 24px` → `gap: var(--artdeco-spacing-6)`)
2. ❌ 内联Grid样式 (`style="display: grid"`)
3. ❌ 过度自定义Grid破坏响应式
4. ❌ 混用多套Grid系统

---

## 📚 相关文档

- **V3.1设计文档**: `docs/api/ARTDECO_TRADING_CENTER_OPTIMIZED_V3.1.md`
- **SCSS架构分析**: `docs/reports/ARTDECO_SCSS_ARCHITECTURE_ANALYSIS.md`
- **ArtDeco令牌**: `web/frontend/src/styles/artdeco-tokens.scss`
- **Grid系统源码**: `web/frontend/src/styles/artdeco-grid.scss`

---

**文档版本**: 1.0
**最后更新**: 2026-01-22
**维护者**: Claude Code
**状态**: ✅ 已完成
