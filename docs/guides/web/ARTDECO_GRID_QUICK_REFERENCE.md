# ArtDeco Grid 系统快速参考

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**状态**: 2026-04-01 已按当前规范复核
**用途**: 快速查找和使用 `artdeco-grid.scss` 中已经实现的 Grid 类与 mixin

> 治理说明
>
> - 当前有效规范以 [ARTDECO_SCSS_GOVERNANCE_BASELINE.md](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md) 为准。
> - 本文档聚焦 `artdeco-grid.scss` 中已经实现的类与 mixin。
> - 当前项目是桌面端工作台，不做移动端 / 平板适配。
> - 新代码示例优先使用 `@use`。

---

## 1. 快速开始

### 1.1 工具类

```vue
<template>
  <div class="artdeco-grid-3">
    <ArtDecoCard>图表1</ArtDecoCard>
    <ArtDecoCard>图表2</ArtDecoCard>
    <ArtDecoCard>图表3</ArtDecoCard>
  </div>

  <div class="artdeco-grid-4">
    <ArtDecoStatCard />
    <ArtDecoStatCard />
    <ArtDecoStatCard />
    <ArtDecoStatCard />
  </div>

  <div class="artdeco-grid-auto">
    <HeatmapTile v-for="item in items" :key="item.id" />
  </div>
</template>
```

---

## 2. 可用 Grid 类

### 2.1 基础 Grid 类

| 类名 | 用途 | 宽屏桌面 | 紧凑桌面 | 窄桌面 |
|------|------|----------|----------|--------|
| `.artdeco-grid-3` | Dashboard 图表 | 3列 | 2列 | 1列 |
| `.artdeco-grid-4` | 统计卡片 | 4列 | 3列 | 2列或1列 |
| `.artdeco-grid-2` | 左右对比 | 2列 | 1列 | 1列 |
| `.artdeco-grid-auto` | 热力图 / 板块 | 自适应 | 自适应 | 自适应 |
| `.artdeco-grid-cards` | 股票池 / 卡片列表 | 卡片 Grid | 卡片 Grid | 单列或稀疏多列 |

### 2.2 语义化 Grid 类（推荐）

| 类名 | 典型场景 | 列数 | 间距 |
|------|----------|------|------|
| `.charts-section` | 图表区域 | 3列 | 24px |
| `.summary-section` | 统计卡片 | 4列 | 24px |
| `.heatmap-section` | 板块热力图 | 自适应 | 8px |
| `.flow-section` | 资金流分析 | 2列 | 24px |
| `.pool-section` | 股票池 / 卡片列表 | 卡片 | 24px |
| `.nav-section` | 导航 / 快捷入口 | 3列 | 32px |

---

## 3. 使用场景示例

### 3.1 Dashboard 主布局

```vue
<template>
  <section class="charts-section">
    <ArtDecoKLineChartContainer :symbol="'000001'" />
    <ArtDecoKLineChartContainer :symbol="'399001'" />
    <ArtDecoKLineChartContainer :symbol="'399006'" />
  </section>

  <section class="summary-section">
    <ArtDecoStatCard label="总市值" :value="totalMarketCap" />
    <ArtDecoStatCard label="成交额" :value="totalVolume" />
    <ArtDecoStatCard label="上涨家数" :value="upCount" />
    <ArtDecoStatCard label="下跌家数" :value="downCount" />
  </section>

  <section class="heatmap-section">
    <HeatmapCard v-for="sector in sectors" :key="sector.code" :sector="sector" />
  </section>
</template>
```

### 3.2 自定义 Grid

```scss
@use '@/styles/artdeco-grid.scss' as *;
@use '@/styles/artdeco-tokens.scss' as *;

.my-custom-grid {
  @include artdeco-grid-container;
  grid-template-columns: repeat(3, 1fr) 200px;
  gap: var(--artdeco-spacing-6);

  @media (max-width: 1280px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}
```

说明：这里的断点是 **桌面端窗口尺寸分段**，不是移动端适配目标。

---

## 4. Gap 与对齐

### 4.1 Gap 工具类

```html
<div class="artdeco-grid-3 gap-xs">8px间距</div>
<div class="artdeco-grid-3 gap-sm">12px间距</div>
<div class="artdeco-grid-3 gap-md">16px间距</div>
<div class="artdeco-grid-3 gap-lg">24px间距</div>
<div class="artdeco-grid-3 gap-xl">32px间距</div>
<div class="artdeco-grid-3 gap-2xl">40px间距</div>
```

### 4.2 对齐工具类

```html
<div class="artdeco-grid-3 justify-start">左对齐</div>
<div class="artdeco-grid-3 justify-center">居中对齐</div>
<div class="artdeco-grid-3 justify-between">两端对齐</div>

<div class="artdeco-grid-3 items-start">顶部对齐</div>
<div class="artdeco-grid-3 items-center">垂直居中</div>
<div class="artdeco-grid-3 items-stretch">拉伸填充</div>
```

---

## 5. 断点说明

| 断点名 | 宽度 | 当前解读 |
|--------|------|----------|
| `--artdeco-breakpoint-xs` | 480px | 极窄窗口 |
| `--artdeco-breakpoint-sm` | 640px | 窄窗口 |
| `--artdeco-breakpoint-md` | 1024px | 紧凑桌面 |
| `--artdeco-breakpoint-lg` | 1280px | 标准桌面 |
| `--artdeco-breakpoint-xl` | 1536px | 宽屏桌面 |

> 注意
>
> 文档和源码里仍能看到 `mobile / tablet` 一类旧命名，但当前项目治理口径是桌面端工作台。新代码不要以这些命名为移动端适配理由。

---

## 6. Mixin 参考

```scss
@use '@/styles/artdeco-grid.scss' as *;

.my-grid {
  @include artdeco-grid-container;
}

.three-cols {
  @include artdeco-grid-3-cols;
}

.four-cols {
  @include artdeco-grid-4-cols;
}

.two-cols {
  @include artdeco-grid-2-cols;
}
```

解释：

- `artdeco-grid-3-cols`：宽屏 3 列，窗口变窄时收敛
- `artdeco-grid-4-cols`：宽屏 4 列，窗口变窄时逐步收敛
- `artdeco-grid-2-cols`：双列对比布局
- `artdeco-grid-auto` / `artdeco-grid-cards`：更适合热力图和卡片池

---

## 7. 最佳实践

### 推荐

1. 优先使用语义化类，例如 `.charts-section`、`.summary-section`
2. 间距优先使用 `var(--artdeco-spacing-*)`
3. 在桌面端窗口尺寸变化下保持信息密度稳定
4. 保持 Grid 层级简单，避免嵌套过深

### 避免

1. 硬编码 `gap: 24px`
2. 内联 `style="display: grid"`
3. 把 Grid 断点写成移动端适配体系
4. 混用多套 Grid 系统

---

## 8. 相关文档

- [ARTDECO_SCSS_GOVERNANCE_BASELINE](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md)
- [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
- [ARTDECO_PAGE_TEMPLATE_GUIDE](./ARTDECO_PAGE_TEMPLATE_GUIDE.md)
- `web/frontend/src/styles/artdeco-grid.scss`
- `web/frontend/src/styles/artdeco-tokens.scss`

---

**最后更新**: 2026-04-01
**维护者**: Claude Code
**状态**: ✅ 当前有效
