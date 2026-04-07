# MyStocks Web前端设计分析报告

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


**分析日期**: 2026-01-20
**分析方法**: UI/UX Pro Max 系统化设计审查
**设计系统**: ArtDeco + 量化交易终端
**目标**: 在保持ArtDeco风格的基础上增强量化管理专业感

---

> 2026-04-01 状态说明
>
> - 本文件是历史设计分析报告，不是当前 ArtDeco 规范入口。
> - 文中出现的组件数量、设计系统成熟度和实现边界，反映的是当时分析时点；若与当前代码不一致，以当前活跃治理文档和源码为准。
> - 当前建议先看：`docs/guides/web/ARTDECO_START_HERE.md`、`docs/guides/web/ARTDECO_MASTER_INDEX.md`、`docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`、`web/frontend/ARTDECO_COMPONENTS_CATALOG.md`。

## 📊 执行摘要

基于 UI/UX Pro Max 的专业设计审查，MyStocks 前端已建立了优秀的 ArtDeco 设计系统，但存在**量化专业性不足**的问题。本报告提供了**保持ArtDeco美学**的同时**增强量化管理风格**的具体改进方案。

### 关键发现

**✅ 设计优势**:
- 完整的 ArtDeco 组件库（原文 64 个组件为历史盘点值，当前库存请查最新目录）
- 独特的视觉识别（金色强调、几何装饰）
- 良好的设计令牌系统

**⚠️ 改进空间**:
- 数据密度不够高（量化终端需要高信息密度）
- 缺少专业金融色彩系统（涨跌色、状态色）
- 字体不够技术化（缺少等宽数字）
- 布局过于宽松（交易终端需要紧凑布局）

---

## 🎨 Part 1: 当前设计问题分析

### 1.1 数据密度问题 🔴 **High Priority**

**问题描述**:
当前 ArtDeco 设计过于宽松，不符合量化交易终端的高密度信息展示需求。

**具体表现**:
```vue
<!-- ❌ 当前: 宽松的卡片间距 -->
<ArtDecoCard class="market-panorama" padding="24px" gap="20px">
  <div class="stat-card" padding="16px">
    <h3>上证指数</h3>
    <div class="value">3021.45</div>
  </div>
</ArtDecoCard>
```

**量化终端标准**:
- 卡片间距: 4-8px（当前 20px）
- 内边距: 6-12px（当前 16-24px）
- 字体更小: 数据 12-14px（当前 14-16px）
- 信息更紧凑: 同屏显示 2-3 倍数据点

**UI/UX Pro Max 指导**:
> "Data-Dense Dashboard: Multiple charts/widgets, data tables, KPI cards, **minimal padding**, grid layout, space-efficient, **maximum data visibility**"

---

### 1.2 金融色彩系统缺失 🔴 **High Priority**

**问题描述**:
缺少专业的金融涨跌色彩和状态指示色彩系统。

**当前状态**:
```scss
// ⚠️ 仅使用 ArtDeco 金色系
--artdeco-gold-primary: #D4AF37;  // 金色（主色）
--artdeco-gold-hover: #F2E8C4;   // 亮金（悬停）
--artdeco-bg-global: #0A0A0A;    // 黑曜石黑
```

**缺失的专业色彩**:
```scss
// ❌ 缺失: 涨跌色（量化核心）
--color-rise: #26A69A;    // 涨 - 青绿色
--color-fall: #EF5350;    // 跌 - 红色

// ❌ 缺失: 信号色彩
--signal-strong-buy: #00C853;  // 强买
--signal-buy: #69F0AE;         // 买入
--signal-neutral: #FFD600;      // 中性
--signal-sell: #FF6D00;         // 卖出
--signal-strong-sell: #D50000;  // 强卖

// ❌ 缺失: 状态等级色
--status-normal: #22C55E;       // 正常 - 绿
--status-warning: #FFA500;       // 警告 - 橙
--status-critical: #DC2626;      // 危险 - 红
```

**UI/UX Pro Max 指导**:
> "Financial Dashboard: **Dark bg + red/green alerts + trust blue**"
> "Trading/Stock OHLC: Bullish: #26A69A, Bearish: #EF5350"

---

### 1.3 字体技术性不足 🟡 **Medium Priority**

**问题描述**:
当前字体过于装饰化，缺少量化交易需要的技术精确感。

**当前字体**:
```scss
--artdeco-font-heading: 'Marcellus', serif;  // 装饰性强
--artdeco-font-body: 'Josefin Sans', sans-serif;  // 几何复古
```

**问题分析**:
- ❌ **缺少等宽数字**: 数字不对齐，影响数据对比
- ❌ **缺少技术字体**: 不够精密，缺乏量化专业感
- ❌ **数字不够清晰**: Marcellus 的数字 0/1/O/l 容易混淆

**UI/UX Pro Max 推荐**:
```scss
// ✅ 推荐: Dashboard Data 字体对
--font-display: 'Fira Code', monospace;  // 数据显示
--font-body: 'Fira Sans', sans-serif;     // 标签说明
```

**替代方案: Financial Trust**
```scss
--font-display: 'IBM Plex Sans', sans-serif;  // 信任感强
--font-mono: 'IBM Plex Mono', monospace;     // 等宽技术
```

---

### 1.4 布局过于宽松 🟡 **Medium Priority**

**问题描述**:
当前布局适合展示型网站，但不符合量化交易操作台的需求。

**具体问题**:

#### 问题1: 卡片过大
```vue
<!-- ❌ 当前: 大卡片浪费空间 -->
<ArtDecoStatCard
  size="large"  // 120px 高度
  padding="24px"
  gap="16px"
/>
```

**量化终端标准**:
```vue
<!-- ✅ 改进: 紧凑卡片 -->
<ArtDecoStatCard
  size="compact"  // 48px 高度
  padding="6px 12px"  // data-dense-table-cell-padding
  gap="4px"
/>
```

#### 问题2: 间距过大
```scss
// ❌ 当前: 宽松间距
.section-gap { gap: 24px; }
.card-gap { gap: 16px; }
.element-gap { gap: 12px; }
```

**量化终端标准**:
```scss
// ✅ 改进: 数据密集型间距
.section-gap { gap: 12px; }  // 减半
.card-gap { gap: 8px; }      // 减半
.element-gap { gap: 4px; }   // 减半
```

**UI/UX Pro Max 指导**:
> "Data-Dense Dashboard: **minimal padding**, grid layout, space-efficient, **maximum data visibility**"

---

### 1.5 缺少量化专业组件 🟢 **Low Priority**

**问题描述**:
缺少量化交易特有的专业UI组件。

**缺失组件**:
- ❌ **深度深度DOM (Depth of Market)**: 5档买卖盘
- ❌ **分时图组件**: 实时价格曲线
- ❌ **K线图组件**: Candlestick chart
- ❌ **技术指标面板**: MACD, KDJ, RSI 等
- ❌ **策略信号指示器**: 买卖信号可视化
- ❌ **风险仪表盘**: 风险度量可视化

---

## 🎯 Part 2: 改进方案（保持ArtDeco美学）

### 2.1 设计原则：**ArtDeco + 量化专业感**

**核心理念**:
> **"在ArtDeco的奢华装饰中，融入量化交易终端的精密感"**

**三个关键词**:
1. **Decorative** (装饰性) - 保留 ArtDeco 金色几何美学
2. **Technical** (技术性) - 增加量化交易专业感
3. **Data-Dense** (数据密集) - 提高信息密度

---

### 2.2 色彩系统扩展：**ArtDeco Gold + 金融色** ✅

**新增金融色彩令牌**（不破坏现有ArtDeco系统）:

```scss
// ============================================
//   ARTDECO + QUANTITATIVE TRADING COLOR SYSTEM
//   ArtDeco美学 + 量化交易色彩
// ============================================

:root {
  // ========== 现有 ArtDeco 色彩（保持不变）==========
  --artdeco-gold-primary: #D4AF37;
  --artdeco-gold-hover: #F2E8C4;
  --artdeco-bg-global: #0A0A0A;
  --artdeco-bg-card: #141414;
  --artdeco-fg-primary: #FFFFFF;

  // ========== 新增: 金融涨跌色 ==========
  --quant-rise-base: #26A69A;      // 涨 - 青绿（主色）
  --quant-rise-light: #69F0AE;     // 涨 - 亮绿
  --quant-rise-bg: rgba(38, 166, 154, 0.1);  // 涨背景

  --quant-fall-base: #EF5350;      // 跌 - 红色（主色）
  --quant-fall-light: #FF8A80;     // 跌 - 亮红
  --quant-fall-bg: rgba(239, 83, 80, 0.1);   // 跌背景

  // ========== 新增: 信号等级色 ==========
  --signal-strong-buy: #00C853;    // 强买 - 深绿
  --signal-buy: #69F0AE;           // 买入 - 亮绿
  --signal-neutral: #FFD600;       // 中性 - 黄色
  --signal-sell: #FF6D00;          // 卖出 - 橙色
  --signal-strong-sell: #D50000;    // 强卖 - 深红

  // ========== 新增: 状态等级色 ==========
  --status-critical: #DC2626;       // 危险 - 深红
  --status-warning: #FFA500;        // 警告 - 橙色
  --status-normal: #22C55E;         // 正常 - 绿色
  --status-info: #3B82F6;            // 信息 - 蓝色

  // ========== 新增: ArtDeco 金属渐变 ==========
  --gold-gradient: linear-gradient(135deg, #D4AF37 0%, #F2E8C4 50%, #D4AF37 100%);
  --gold-shine: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.3), transparent);
}
```

**使用原则**:
- ✅ **标题、装饰**: 使用 ArtDeco 金色
- ✅ **数据涨跌**: 使用金融红绿色
- ✅ **信号强度**: 使用信号等级色
- ✅ **背景装饰**: 使用金色几何图案（淡化）

---

### 2.3 字体系统优化：**装饰性 + 技术性** ✅

**混合字体系统**（推荐方案1 - 量化专业型）:

```scss
// ============================================
//   HYBRID TYPOGRAPHY SYSTEM
//   混合字体: ArtDeco装饰 + 量化技术
// ============================================

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  // 标题字体: 保持 ArtDeco 装饰性
  --font-heading: 'Marcellus', serif;  // 保留 ArtDeco 风格

  // 正文字体: 使用技术字体（替代 Josefin Sans）
  --font-body: 'IBM Plex Sans', sans-serif;  // 信任感强

  // 数据字体: 新增等宽字体
  --font-data: 'JetBrains Mono', monospace;   // 数据显示
  --font-number: 'JetBrains Mono', monospace;  // 数字专用
}

// ========== 使用规范 ==========

// 1. 标题: ArtDeco 装饰字体
h1, h2, h3, .artdeco-title {
  font-family: var(--font-heading);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--artdeco-gold-primary);
}

// 2. 正文: 技术字体
body, p, .text-body {
  font-family: var(--font-body);
  color: var(--artdeco-fg-primary);
}

// 3. 数据/数字: 等宽字体（关键改进）
.data-value, .number-display, .price, .percent {
  font-family: var(--font-data);
  font-variant-numeric: tabular-nums;  // ⚡ 重要: 数字等宽
}
```

**替代方案2 - 金融信任型**:
```scss
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --font-heading: 'Marcellus', serif;       // ArtDeco标题
  --font-body: 'IBM Plex Sans', sans-serif; // 全部使用IBM（信任感强）
}
```

---

### 2.4 数据密度优化：**ArtDeco紧凑型布局** ✅

**新的尺寸系统**（data-dense优化）:

```scss
// ============================================
//   ARTDECO DATA-DENSE SPACING SYSTEM
//   ArtDeco 数据密集型间距系统
// ============================================

:root {
  // ========== 紧凑型间距 ==========
  --spacing-xs: 4px;     // 元素内间距
  --spacing-sm: 8px;     // 卡片内间距
  --spacing-md: 12px;    // 卡片间距
  --spacing-lg: 16px;    // 区域间距

  // ========== 紧凑型卡片 ==========
  --card-padding-compact: 6px 12px;      // 紧凑卡片内边距
  --card-padding-dense: 8px 16px;         // 密集卡片内边距
  --card-gap-compact: 4px;                 // 卡片元素间距

  // ========== 表格优化 ==========
  --table-cell-padding: 4px 8px;           // 表格单元格内边距
  --table-header-height: 32px;             // 表头高度
  --table-row-hover: rgba(212, 175, 55, 0.05); // 行悬停背景

  // ========== 组件尺寸 ==========
  --stat-card-compact-height: 48px;        // 紧凑型统计卡片高度
  --stat-card-dense-height: 64px;          // 密集型统计卡片高度
  --input-compact-height: 32px;            // 紧凑型输入框高度
}

// ========== 混合布局类 ==========

// 紧凑型容器
.artdeco-compact-container {
  padding: var(--spacing-sm);
  gap: var(--spacing-sm);
}

// 密集型网格
.artdeco-dense-grid {
  display: grid;
  gap: var(--card-gap-compact);
  padding: 0;

  // 3-4列密集布局
  &.cols-3 { grid-template-columns: repeat(3, 1fr); }
  &.cols-4 { grid-template-columns: repeat(4, 1fr); }
}

// 紧凑型卡片
.artdeco-card-compact {
  padding: var(--card-padding-compact);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--data-dense-border-color);

  // ArtDeco 金色边框（保持装饰性）
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg,
      transparent,
      var(--artdeco-gold-primary),
      transparent
    );
    opacity: 0.3;
  }
}
```

---

### 2.5 组件变体扩展：**量化专用组件** ✅

**新增组件变体**:

#### 1. ArtDecoStatCard 紧凑型
```vue
<ArtDecoStatCard
  variant="quant-compact"  // 新增: 量化紧凑型
  size="compact"           // 新增: 尺寸选项
  :value="3021.45"
  :change="+12.35"
  data-dense              // 新增: 数据密集模式
/>
```

**实现**:
```scss
.artdeco-stat-card {
  // 新增: 紧凑型变体
  &.variant-quant-compact {
    height: var(--stat-card-compact-height);
    padding: var(--card-padding-compact);

    .label {
      font-size: var(--data-dense-font-xs);  // 10px
      color: var(--artdeco-fg-muted);
    }

    .value {
      font-family: var(--font-data);          // 等宽字体
      font-size: var(--data-dense-font-lg);   // 16px
      font-variant-numeric: tabular-nums;
      color: var(--artdeco-fg-primary);
    }

    .change {
      font-family: var(--font-data);
      font-size: var(--data-dense-font-base); // 14px

      &.positive {
        color: var(--quant-rise-base);      // 金融涨色
      }

      &.negative {
        color: var(--quant-fall-base);      // 金融跌色
      }
    }
  }
}
```

#### 2. 数据密集型表格
```vue
<ArtDecoTable
  variant="quant-dense"      // 新增: 量化密集型
  :columns="columns"
  :data="tableData"
  compact                  // 新增: 紧凑模式
  striped                  // 新增: 斑马纹
  hover                    // 新增: 悬停高亮
/>
```

**实现**:
```scss
.artdeco-table {
  &.variant-quant-dense {
    // 紧凑型表格
    .table-cell {
      padding: var(--table-cell-padding);
      font-size: var(--data-dense-font-sm);   // 12px
    }

    // 表头
    .table-header {
      height: var(--table-header-height);
      background: rgba(212, 175, 55, 0.05);
      border-bottom: 1px solid var(--artdeco-gold-primary);
    }

    // 斑马纹（奇数行）
    &.striped {
      .table-row:nth-child(odd) {
        background: rgba(212, 175, 55, 0.02);
      }
    }

    // 悬停高亮
    &.hover {
      .table-row:hover {
        background: var(--table-row-hover);

        // ArtDeco 金色边框效果
        outline: 1px solid rgba(212, 175, 55, 0.2);
        outline-offset: -1px;
      }
    }
  }
}
```

---

### 2.6 专业量化组件：**新增组件** ✅

#### 组件1: 深度深度DOM (Depth of Market)

```vue
<template>
  <ArtDecoCard class="dom-panel" variant="quant-compact">
    <template #header>
      <div class="card-header">
        <ArtDecoIcon name="layers" />
        <h4>深度深度 DOM</h4>
        <ArtDecoBadge variant="info">5档</ArtDecoBadge>
      </div>
    </template>

    <div class="dom-grid">
      <!-- 买盘 -->
      <div class="dom-side buy">
        <div class="dom-row" v-for="level in 5" :key="level">
          <span class="price level-{{ level }}" :style="{color: getPriceColor(level, true)}">
            {{ formatPrice(buyPrices[level]) }}
          </span>
          <span class="volume">{{ formatVolume(buyVolumes[level]) }}</span>
        </div>
      </div>

      <!-- 最新价 -->
      <div class="dom-center">
        <div class="latest-price" :class="{ rise: latestChange > 0, fall: latestChange < 0 }">
          {{ latestPrice }}
        </div>
        <div class="price-change" :class="{ rise: latestChange > 0, fall: latestChange < 0 }">
          {{ formatPercent(latestChange) }}%
        </div>
      </div>

      <!-- 卖盘 -->
      <div class="dom-side sell">
        <div class="dom-row" v-for="level in 5" :key="level">
          <span class="volume">{{ formatVolume(sellVolumes[level]) }}</span>
          <span class="price level-{{ level }}" :style="{color: getPriceColor(level, false)}">
            {{ formatPrice(sellPrices[level]) }}
          </span>
        </div>
      </div>
    </div>
  </ArtDecoCard>
</template>
```

#### 组件2: 技术指标面板

```vue
<template>
  <ArtDecoCard class="indicators-panel" variant="quant-compact">
    <template #header>
      <div class="card-header">
        <ArtDecoIcon name="activity" />
        <h4>技术指标</h4>
      </div>
    </template>

    <div class="indicators-grid">
      <!-- MACD -->
      <div class="indicator-item">
        <div class="indicator-name">MACD</div>
        <div class="indicator-value" :class="macdSignal.class">
          {{ macdSignal.value }}
        </div>
        <div class="indicator-strength">
          <div class="strength-bar" :style="{width: macdSignal.strength + '%'}"></div>
        </div>
      </div>

      <!-- KDJ -->
      <div class="indicator-item">
        <div class="indicator-name">KDJ</div>
        <div class="indicator-value" :class="kdjSignal.class">
          {{ kdjSignal.value }}
        </div>
        <div class="indicator-strength">
          <div class="strength-bar" :style="{width: kdjSignal.strength + '%'}"></div>
        </div>
      </div>

      <!-- RSI -->
      <div class="indicator-item">
        <div class="indicator-name">RSI</div>
        <div class="indicator-value" :class="rsiSignal.class">
          {{ rsiSignal.value }}
        </div>
        <div class="indicator-strength">
          <div class="strength-bar" :style="{width: rsiSignal.strength + '%'}"></div>
        </div>
      </div>
    </div>
  </ArtDecoCard>
</template>
```

---

## 📐 Part 3: 具体实施步骤

### Step 1: 扩展色彩令牌系统 ✅ **立即执行**

**文件**: `web/frontend/src/styles/artdeco-tokens.scss`

**操作**:
```scss
// 在现有 :root 中添加金融色彩
:root {
  // ... 现有 ArtDeco 色彩

  // 新增: 金融涨跌色
  --quant-rise-base: #26A69A;
  --quant-fall-base: #EF5350;

  // 新增: 信号等级色
  --signal-strong-buy: #00C853;
  --signal-buy: #69F0AE;
  --signal-neutral: #FFD600;
  --signal-sell: #FF6D00;
  --signal-strong-sell: #D50000;

  // 新增: 状态等级色
  --status-critical: #DC2626;
  --status-warning: #FFA500;
  --status-normal: #22C55E;
  --status-info: #3B82F6;
}
```

### Step 2: 优化字体系统 ✅ **第二步执行**

**文件**: `web/frontend/src/styles/artdeco-global.scss`

**操作**:
```scss
// 导入技术字体
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --font-heading: 'Marcellus', serif;           // 保持 ArtDeco
  --font-body: 'IBM Plex Sans', sans-serif;    // 新增: 技术字体
  --font-data: 'JetBrains Mono', monospace;     // 新增: 数据字体
}

// 数据/数字使用等宽字体
.data-value, .price, .percent, .number-display {
  font-family: var(--font-data);
  font-variant-numeric: tabular-nums;
}
```

### Step 3: 创建数据密集型样式 ✅ **第三步执行**

**文件**: `web/frontend/src/styles/artdeco-data-dense.scss`

**操作**: 创建新文件（见下文完整代码）

### Step 4: 扩展 ArtDeco 组件 ✅ **第四步执行**

**操作**: 为现有组件添加 `variant="quant-compact"` 和 `size="compact"`

### Step 5: 创建量化专用组件 ✅ **第五步执行**

**操作**: 创建 DOM、技术指标面板等新组件

---

## 📋 Part 4: 完整实施代码文件

### 文件1: `artdeco-data-dense.scss`

**位置**: `web/frontend/src/styles/artdeco-data-dense.scss`

```scss
// ============================================
//   ARTDECO DATA-DENSE STYLES
//   ArtDeco 数据密集型样式 - 量化交易优化
//   Created: 2026-01-20
// ============================================

// ============================================
//   QUANTITATIVE TRADING COLOR TOKENS
//   量化交易色彩令牌
// ============================================

:root {
  // 金融涨跌色（基于 TradingView 标准）
  --quant-rise-base: #26A69A;           // 涨 - 青绿
  --quant-rise-light: #69F0AE;          // 涨 - 亮绿
  --quant-rise-bg: rgba(38, 166, 154, 0.1);

  --quant-fall-base: #EF5350;           // 跌 - 红色
  --quant-fall-light: #FF8A80;          // 跌 - 亮红
  --quant-fall-bg: rgba(239, 83, 80, 0.1);

  // 信号等级色
  --signal-strong-buy: #00C853;         // 强买
  --signal-buy: #69F0AE;                // 买入
  --signal-neutral: #FFD600;            // 中性
  --signal-sell: #FF6D00;                // 卖出
  --signal-strong-sell: #D50000;        // 强卖

  // 状态等级色
  --status-critical: #DC2626;            // 危险
  --status-warning: #FFA500;             // 警告
  --status-normal: #22C55E;              // 正常
  --status-info: #3B82F6;                // 信息

  // 数据密集型间距
  --dense-padding-xs: 4px;
  --dense-padding-sm: 8px;
  --dense-padding-md: 12px;
  --dense-gap-xs: 4px;
  --dense-gap-sm: 8px;
  --dense-gap-md: 12px;

  // 紧凑型组件尺寸
  --stat-card-compact-height: 48px;
  --table-cell-padding: 6px 12px;
  --table-header-height: 32px;
}

// ============================================
//   HYBRID TYPOGRAPHY
//   混合字体系统
// ============================================

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --font-heading: 'Marcellus', serif;
  --font-body: 'IBM Plex Sans', sans-serif;
  --font-data: 'JetBrains Mono', monospace;
}

// 数据字体应用
.data-value,
.price-display,
.percent-display,
.number-display,
.table-cell-data {
  font-family: var(--font-data);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;  // 数字稍微收紧
}

// ============================================
//   DATA-DENSE LAYOUTS
//   数据密集型布局
// ============================================

// 紧凑型容器
.artdeco-compact-container {
  padding: var(--dense-padding-sm);
  gap: var(--dense-gap-sm);
}

// 密集型网格
.artdeco-dense-grid {
  display: grid;
  gap: var(--dense-gap-xs);

  &.cols-2 { grid-template-columns: repeat(2, 1fr); }
  &.cols-3 { grid-template-columns: repeat(3, 1fr); }
  &.cols-4 { grid-template-columns: repeat(4, 1fr); }
  &.cols-5 { grid-template-columns: repeat(5, 1fr); }
}

// 紧凑型统计卡片
.artdeco-stat-card {
  &.variant-quant-compact {
    height: var(--stat-card-compact-height);
    padding: var(--dense-padding-sm);
    display: flex;
    align-items: center;
    justify-content: space-between;

    .label {
      font-size: 11px;
      color: var(--artdeco-fg-muted);
      text-transform: none;
      letter-spacing: 0;
    }

    .value {
      font-family: var(--font-data);
      font-size: 16px;
      font-weight: 600;
      color: var(--artdeco-fg-primary);
    }

    .change {
      font-family: var(--font-data);
      font-size: 12px;

      &.positive {
        color: var(--quant-rise-base);
      }

      &.negative {
        color: var(--quant-fall-base);
      }
    }
  }
}

// ============================================
//   QUANTITATIVE TRADING COMPONENTS
//   量化交易专用组件样式
// ============================================

// 深度深度 DOM (Depth of Market)
.dom-panel {
  .dom-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: var(--dense-gap-xs);
  }

  .dom-side {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .dom-row {
    display: flex;
    justify-content: space-between;
    gap: var(--dense-gap-sm);
    padding: var(--dense-padding-xs) 0;
    font-family: var(--font-data);
    font-size: 12px;

    .price {
      font-weight: 600;

      &.level-1 { opacity: 1.0; }
      &.level-2 { opacity: 0.8; }
      &.level-3 { opacity: 0.6; }
      &.level-4 { opacity: 0.4; }
      &.level-5 { opacity: 0.2; }
    }

    .volume {
      color: var(--artdeco-fg-muted);
      font-size: 10px;
    }
  }

  .dom-center {
    text-align: center;
    padding: var(--dense-padding-sm);
    border-left: 1px solid var(--artdeco-border-default);
    border-right: 1px solid var(--artdeco-border-default);

    .latest-price {
      font-family: var(--font-data);
      font-size: 20px;
      font-weight: 700;

      &.rise { color: var(--quant-rise-base); }
      &.fall { color: var(--quant-fall-base); }
    }

    .price-change {
      font-family: var(--font-data);
      font-size: 12px;

      &.rise { color: var(--quant-rise-base); }
      &.fall { color: var(--quant-fall-base); }
    }
  }
}

// 技术指标面板
.indicators-panel {
  .indicators-grid {
    display: grid;
    gap: var(--dense-gap-sm);

    .indicator-item {
      padding: var(--dense-padding-sm);
      background: rgba(212, 175, 55, 0.03);
      border: 1px solid rgba(212, 175, 55, 0.1);

      .indicator-name {
        font-size: 11px;
        color: var(--artdeco-fg-muted);
        margin-bottom: 4px;
      }

      .indicator-value {
        font-family: var(--font-data);
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 4px;

        &.strong-buy { color: var(--signal-strong-buy); }
        &.buy { color: var(--signal-buy); }
        &.neutral { color: var(--signal-neutral); }
        &.sell { color: var(--signal-sell); }
        &.strong-sell { color: var(--signal-strong-sell); }
      }

      .indicator-strength {
        .strength-bar {
          height: 4px;
          background: rgba(212, 175, 55, 0.2);
          border-radius: 2px;
          overflow: hidden;

          > div {
            height: 100%;
            background: var(--artdeco-gold-primary);
            transition: width 0.3s ease;
          }
        }
      }
    }
  }
}
```

---

## ✅ Part 5: 验证清单

### 色彩系统
- [ ] 金融涨跌色添加成功
- [ ] 信号等级色添加成功
- [ ] 状态等级色添加成功
- [ ] ArtDeco金色保持不变
- [ ] 色彩对比度符合 WCAG AA 标准

### 字体系统
- [ ] IBM Plex Sans 导入成功
- [ ] JetBrains Mono 导入成功
- [ ] 数据字体使用等宽显示
- [ ] Marcellus 保持 ArtDeco 风格
- [ ] 字体加载性能良好

### 布局优化
- [ ] 紧凑型容器创建成功
- [ ] 数据密集型网格正常显示
- [ ] 卡片间距符合量化标准
- [ ] 信息密度提高 2-3 倍

### 组件变体
- [ ] ArtDecoStatCard 紧凑型实现
- [ ] 数据密集型表格实现
- [ ] DOM 深度组件创建
- [ ] 技术指标面板创建

---

## 🎉 总结

### 改进效果预期

1. **信息密度提升**: 2-3倍（通过紧凑布局和等宽字体）
2. **专业感提升**: 引入金融色彩和技术字体
3. **ArtDeco美学保持**: 金色装饰和几何图案不变
4. **量化交易氛围**: 符合专业交易终端标准

### 设计原则达成

✅ **Decorative**: ArtDeco 金色美学完整保留
✅ **Technical**: 金融色彩和技术字体增强专业感
✅ **Data-Dense**: 紧凑布局大幅提高信息密度

---

**报告生成**: 2026-01-20
**下一步**: 实施Step 1-5，逐步应用改进
