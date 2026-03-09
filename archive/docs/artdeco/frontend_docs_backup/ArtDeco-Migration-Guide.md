# ArtDeco 风格迁移指南

## 概述

本指南帮助将非 ArtDeco 风格的 Vue 组件改造为符合 ArtDeco 设计系统的风格。

## ArtDeco 设计原则

### 核心理念
- **极简主义中的极致主义**：每个元素都是经过精心设计的，既丰富又克制
- **几何装饰**：使用三角形、人字形、辐射状、锯齿形图案
- **极端对比度**：黑曜石黑背景 vs 金属金色强调色
- **对称与平衡**：基于中心轴线的对称布局
- **垂直感**：受摩天大楼启发的向上动势
- **材料奢华感**：模拟黄铜、蚀刻玻璃、漆木等材质

### 配色方案

```css
/* 背景色 */
--artdeco-bg-primary: #0A0A0A;  /* 黑曜石黑 */
--artdeco-bg-card: #141414;     /* 深炭色 */
--artdeco-bg-secondary: #1E3D59; /* 午夜蓝 */

/* 文字色 */
--artdeco-fg-primary: #F2F0E4;  /* 香槟奶油色 */
--artdeco-fg-muted: #888888;    /* 锡灰色 */

/* 强调色 */
--artdeco-accent-gold: #D4AF37;     /* 金属金色 */
--artdeco-accent-gold-light: #F2E8C4; /* 浅金色 */

/* A股市场色 */
--artdeco-color-up: #FF5252;     /* 红色（上涨） */
--artdeco-color-down: #00E676;   /* 绿色（下跌） */
--artdeco-color-flat: #B0B3B8;   /* 灰色（平盘） */
```

### 字体系统

```css
--artdeco-font-display: 'Marcellus', 'Italiana', serif; /* 标题字体 */
--artdeco-font-body: 'Josefin Sans', sans-serif;        /* 正文字体 */
--artdeco-font-mono: 'JetBrains Mono', monospace;       /* 等宽字体 */
```

### 关键样式规则

1. **圆角**：严格为 0px 或最多 2px（极少使用）
2. **边框**：1px 细线或 2px 双线
3. **间距**：使用 8px 基础单位的倍数
4. **字母间距**：标题使用 `0.2em`，正文使用 `0.05em`
5. **大写**：所有标题必须大写
6. **发光效果**：使用 `box-shadow` 模拟霓虹灯效果

## 组件改造检查清单

### 1. 根容器
- [ ] 使用 `--artdeco-bg-primary` 作为背景色
- [ ] 添加 ArtDeco 对角线背景图案
- [ ] 设置最小高度 `min-height: 100vh`
- [ ] 添加适当的内边距 `padding: var(--artdeco-spacing-6)`

### 2. 卡片组件
- [ ] 使用 `--artdeco-bg-card` 作为背景色
- [ ] 添加金色边框 `border: 1px solid rgba(212, 175, 55, 0.3)`
- [ ] 添加角落装饰（L 形边框）
- [ ] 添加双框效果（伪元素）
- [ ] 添加悬停效果（金色发光 + 向上位移）

### 3. 标题文字
- [ ] 使用 `--artdeco-font-display` 字体
- [ ] 大写转换 `text-transform: uppercase`
- [ ] 宽字母间距 `letter-spacing: var(--artdeco-tracking-widest)` (0.2em)
- [ ] 使用金色 `--artdeco-accent-gold`
- [ ] 适当的大字号

### 4. 按钮
- [ ] 使用 `--artdeco-font-display` 字体
- [ ] 大写转换 `text-transform: uppercase`
- [ ] 宽字母间距 `letter-spacing: 0.2em`
- [ ] 锐利边角 `border-radius: var(--artdeco-radius-none)`
- [ ] 2px 金色边框
- [ ] 悬停时金色发光效果

### 5. 输入框
- [ ] 透明背景 `background: transparent`
- [ ] 仅底部边框（2px 金色）
- [ ] 聚焦时金色发光
- [ ] 使用 `--artdeco-font-body` 字体

### 6. 表格
- [ ] 透明背景
- [ ] 表头使用金色文字和边框
- [ ] 悬停行使用金色微弱背景
- [ ] 使用等宽字体显示数据

### 7. 徽章/标签
- [ ] 大写文字
- [ ] 使用 A股市场色（红涨绿跌）
- [ ] 锐利边角
- [ ] 半透明背景

## 改造模板

### 基础页面模板

```vue
<template>
  <div class="artdeco-page-container">
    <div class="artdeco-bg-pattern"></div>

    <!-- 页面标题 -->
    <div class="artdeco-page-header">
      <h1 class="artdeco-page-title">PAGE TITLE</h1>
      <p class="artdeco-page-subtitle">PAGE SUBTITLE</p>
    </div>

    <!-- 主要内容 -->
    <div class="artdeco-main-content">
      <!-- 你的内容 -->
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-page-container {
  min-height: 100vh;
  padding: var(--artdeco-spacing-6);
  position: relative;
  background: var(--artdeco-bg-primary);

  .artdeco-bg-pattern {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.04;
    background-image:
      repeating-linear-gradient(
        45deg,
        var(--artdeco-accent-gold) 0px,
        var(--artdeco-accent-gold) 1px,
        transparent 1px,
        transparent 10px
      ),
      repeating-linear-gradient(
        -45deg,
        var(--artdeco-accent-gold) 0px,
        var(--artdeco-accent-gold) 1px,
        transparent 1px,
        transparent 10px
      );
  }

  .artdeco-page-header {
    text-align: center;
    margin-bottom: var(--artdeco-spacing-8);
    position: relative;
    z-index: 1;

    .artdeco-page-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-h2);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-widest);
      color: var(--artdeco-accent-gold);
      margin: 0 0 var(--artdeco-spacing-2) 0;
    }

    .artdeco-page-subtitle {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-small);
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wider);
      margin: 0;
    }
  }

  .artdeco-main-content {
    position: relative;
    z-index: 1;
  }
}
</style>
```

### 卡片组件模板

```vue
<template>
  <div class="artdeco-card">
    <div class="artdeco-corner-tl"></div>
    <div class="artdeco-corner-br"></div>

    <div class="artdeco-card-header">
      <h3 class="artdeco-card-title">CARD TITLE</h3>
      <p class="artdeco-card-subtitle">Card subtitle</p>
    </div>

    <div class="artdeco-card-body">
      <!-- 卡片内容 -->
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-card {
  position: relative;
  background: var(--artdeco-bg-card);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: var(--artdeco-radius-none);
  padding: var(--artdeco-spacing-6);
  transition: all var(--artdeco-transition-slow);

  .artdeco-corner-tl,
  .artdeco-corner-br {
    position: absolute;
    width: 20px;
    height: 20px;
    pointer-events: none;
    opacity: 0.6;
  }

  .artdeco-corner-tl {
    top: 12px;
    left: 12px;
    border-top: 2px solid var(--artdeco-accent-gold);
    border-left: 2px solid var(--artdeco-accent-gold);
  }

  .artdeco-corner-br {
    bottom: 12px;
    right: 12px;
    border-bottom: 2px solid var(--artdeco-accent-gold);
    border-right: 2px solid var(--artdeco-accent-gold);
  }

  &:hover {
    border-color: var(--artdeco-accent-gold);
    box-shadow: var(--artdeco-glow-medium);
    transform: translateY(-2px);
  }

  .artdeco-card-header {
    margin-bottom: var(--artdeco-spacing-5);
    padding-bottom: var(--artdeco-spacing-4);
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);

    .artdeco-card-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-h4);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-widest);
      color: var(--artdeco-accent-gold);
      margin: 0 0 var(--artdeco-spacing-2) 0;
    }

    .artdeco-card-subtitle {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-small);
      color: var(--artdeco-fg-muted);
      margin: 0;
    }
  }

  .artdeco-card-body {
    font-family: var(--artdeco-font-body);
    color: var(--artdeco-fg-primary);
    line-height: 1.6;
  }
}
</style>
```

### 按钮组件模板

```vue
<template>
  <button class="artdeco-btn artdeco-btn-primary">
    BUTTON TEXT
  </button>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-font-size-body);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
  border: 2px solid var(--artdeco-accent-gold);
  border-radius: var(--artdeco-radius-none);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.artdeco-btn-primary {
  background: var(--artdeco-accent-gold);
  color: var(--artdeco-bg-primary);

  &:hover:not(:disabled) {
    background: var(--artdeco-accent-gold-light);
    box-shadow: var(--artdeco-glow-medium);
  }
}

.artdeco-btn-secondary {
  background: transparent;
  color: var(--artdeco-accent-gold);

  &:hover:not(:disabled) {
    background: var(--artdeco-bg-secondary);
    box-shadow: var(--artdeco-glow-subtle);
  }
}
</style>
```

## Element Plus 组件适配

### el-card 适配

```scss
.artdeco-el-card {
  background: var(--artdeco-bg-card) !important;
  border: 1px solid rgba(212, 175, 55, 0.3) !important;
  border-radius: var(--artdeco-radius-none) !important;

  :deep(.el-card__header) {
    background: transparent !important;
    border-bottom: 1px solid rgba(212, 175, 55, 0.2) !important;
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-font-size-h4);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    color: var(--artdeco-accent-gold);
  }

  :deep(.el-card__body) {
    background: transparent !important;
    color: var(--artdeco-fg-primary);
  }
}
```

### el-button 适配

```scss
.artdeco-el-button {
  font-family: var(--artdeco-font-display) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.2em !important;
  border-radius: 0 !important;
  border-width: 2px !important;

  &.el-button--primary {
    background: var(--artdeco-accent-gold) !important;
    border-color: var(--artdeco-accent-gold) !important;
    color: var(--artdeco-bg-primary) !important;

    &:hover {
      background: var(--artdeco-accent-gold-light) !important;
      box-shadow: var(--artdeco-glow-medium) !important;
    }
  }
}
```

### el-table 适配

```scss
.artdeco-el-table {
  background: transparent !important;

  :deep(.el-table__header) {
    th {
      background: rgba(212, 175, 55, 0.1) !important;
      color: var(--artdeco-accent-gold) !important;
      font-family: var(--artdeco-font-display) !important;
      font-weight: 600 !important;
      text-transform: uppercase !important;
      letter-spacing: var(--artdeco-tracking-wider) !important;
      border-bottom: 2px solid var(--artdeco-accent-gold) !important;
    }
  }

  :deep(.el-table__body) {
    tr {
      background: transparent !important;
      transition: background var(--artdeco-transition-base) !important;

      &:hover {
        background: rgba(212, 175, 55, 0.05) !important;
      }

      td {
        border-bottom: 1px solid rgba(212, 175, 55, 0.2) !important;
        color: var(--artdeco-fg-primary) !important;
      }
    }
  }
}
```

## 快速改造步骤

1. **导入 ArtDeco tokens**
   ```scss
   @import '@/styles/artdeco-tokens.scss';
   ```

2. **替换背景色**
   - `background: #fff` → `background: var(--artdeco-bg-primary)`
   - `background: #f5f5f5` → `background: var(--artdeco-bg-card)`

3. **替换文字颜色**
   - `color: #333` → `color: var(--artdeco-fg-primary)`
   - `color: #999` → `color: var(--artdeco-fg-muted)`

4. **替换强调色**
   - `color: #409eff` → `color: var(--artdeco-accent-gold)`
   - `border-color: #409eff` → `border-color: var(--artdeco-accent-gold)`

5. **添加字体**
   - 标题：`font-family: var(--artdeco-font-display)`
   - 正文：`font-family: var(--artdeco-font-body)`
   - 数字：`font-family: var(--artdeco-font-mono)`

6. **添加大写和字间距**
   - 标题：`text-transform: uppercase; letter-spacing: var(--artdeco-tracking-widest);`

7. **移除圆角**
   - `border-radius: 4px` → `border-radius: var(--artdeco-radius-none)`

8. **添加发光效果**
   - `box-shadow: 0 2px 4px rgba(0,0,0,0.1)` → `box-shadow: var(--artdeco-glow-subtle)`

## 已改造的组件

以下组件已完成 ArtDeco 风格改造：

1. ✅ Login.vue
2. ✅ Market.vue
3. ✅ StockDetail.vue（部分改造）
4. ✅ TradeManagement.vue（部分改造）

## 待改造的组件列表

### 主要页面视图 (剩余 10 个)
- [ ] RiskMonitor.vue
- [ ] Settings.vue
- [ ] TechnicalAnalysis.vue
- [ ] BacktestAnalysis.vue
- [ ] IndicatorLibrary.vue
- [ ] StrategyManagement.vue
- [ ] KLineDemo.vue
- [ ] RealTimeMonitor.vue
- [ ] Analysis.vue

### 业务组件 (4 个)
- [ ] StrategyCard.vue
- [ ] LinearCard.vue
- [ ] StrategyDialog.vue
- [ ] BacktestPanel.vue

### 市场数据组件 (9 个)
- [ ] FundFlowPanel.vue
- [ ] LongHuBangPanel.vue
- [ ] ChipRacePanel.vue
- [ ] ETFDataPanel.vue
- [ ] WencaiPanel.vue
- [ ] WencaiPanelV2.vue
- [ ] WencaiPanelSimple.vue
- [ ] IndicatorSelector.vue
- [ ] ProKLineChart.vue

### 其他组件 (64 个)

## 注意事项

1. **性能考虑**：大量使用发光效果可能会影响性能，建议适度使用
2. **响应式设计**：确保在移动设备上也能正常显示
3. **可访问性**：保持足够的颜色对比度（金色文字在黑色背景上约 7:1 对比度）
4. **Element Plus 兼容**：使用 `:deep()` 选择器覆盖 Element Plus 样式
5. **字体加载**：确保 Google Fonts 已正确加载

## 参考资料

- ArtDeco 设计文档：`/opt/claude/mystocks_spec/docs/design/html_sample/ArtDeco.md`
- ArtDeco tokens：`/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-tokens.scss`
- ArtDeco 主题：`/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco/artdeco-theme.css`
- 已改造的组件示例：Login.vue, Market.vue
