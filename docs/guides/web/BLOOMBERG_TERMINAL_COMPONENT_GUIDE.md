# ArtDeco Terminal 组件使用指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 📋 目录

1. [概述](#概述)
2. [核心组件](#核心组件)
3. [设计系统](#设计系统)
4. [使用指南](#使用指南)
5. [样式规范](#样式规范)
6. [最佳实践](#最佳实践)
7. [性能优化](#性能优化)
8. [测试指南](#测试指南)

---

## 概述

ArtDeco Terminal 组件库为 MyStocks 项目提供专业金融终端风格的用户界面，采用深色主题、高对比度显示和实时数据展示。

### 设计理念

- **专业金融风格**: 遵循 ArtDeco Terminal 的专业数据展示方式
- **高对比度**: OLED 深色背景 (#000000) 与金融蓝 (#0080FF) 的强烈对比
- **信息密度**: 在有限空间内展示大量关键数据
- **实时更新**: 支持高频数据刷新而不影响视觉稳定性
- **多屏幕适配**: 针对 1920x1080 桌面显示优化

### 技术栈

- **框架**: Vue 3 Composition API + TypeScript
- **UI库**: Element Plus (自定义主题)
- **样式**: SCSS + CSS Variables
- **图表**: ECharts (金融配色)
- **字体**: IBM Plex Sans + Roboto Mono

---

## 核心组件

### 1. ArtDecoStatCard - 统计卡片组件

**文件位置**: `src/components/ArtDecoStatCard.vue`

#### 功能特性

- ✅ 支持5种数据格式（数字、货币、百分比、涨跌幅、自定义）
- ✅ 3种趋势指示（上涨、下跌、持平）
- ✅ 加载状态占位符
- ✅ 图标支持
- ✅ 响应式布局

#### API 参考

```typescript
interface Props {
  label: string           // 卡片标签（大写）
  value: number | string  // 显示值
  icon?: string           // 图标名称（Element Plus图标）
  format?: 'number' | 'currency' | 'percent' | 'change' | 'custom'
  trend?: 'up' | 'down' | 'neutral'  // 趋势方向
  loading?: boolean       // 加载状态
  customFormat?: (value: any) => string  // 自定义格式化函数
}
```

#### 使用示例

```vue
<template>
  <div class="stats-grid">
    <!-- 基础数字格式 -->
    <ArtDecoStatCard
      label="TOTAL STOCKS"
      :value="5216"
      icon="data"
      format="number"
    />

    <!-- 货币格式 + 上涨趋势 -->
    <ArtDecoStatCard
      label="TOTAL ASSETS"
      :value="portfolio.total_assets"
      icon="wallet"
      format="currency"
      trend="up"
    />

    <!-- 百分比格式 + 下跌趋势 -->
    <ArtDecoStatCard
      label="DAILY CHANGE"
      :value="+2.35"
      icon="trending-up"
      format="percent"
      trend="up"
    />

    <!-- 涨跌幅格式（自动颜色） -->
    <ArtDecoStatCard
      label="PROFIT RATE"
      :value="15.67"
      icon="chart"
      format="change"
      :trend="profitRate >= 0 ? 'up' : 'down'"
    />

    <!-- 自定义格式 -->
    <ArtDecoStatCard
      label="RATIO"
      :value="ratio"
      icon="pie-chart"
      format="custom"
      :custom-format="(v) => `${v.toFixed(2)}:1`"
    />

    <!-- 加载状态 -->
    <ArtDecoStatCard
      label="LOADING..."
      :value="0"
      format="number"
      :loading="isLoading"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ArtDecoStatCard from '@/components/ArtDecoStatCard.vue'

const portfolio = ref({
  total_assets: 1250000.50
})

const profitRate = ref(15.67)
const ratio = ref(1.618)
const isLoading = ref(false)
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
</style>
```

#### 数据格式说明

| 格式类型 | 说明 | 示例 |
|---------|------|------|
| `number` | 千分位数字 | 5,216 |
| `currency` | 货币格式（¥） | ¥1,250,000.50 |
| `percent` | 百分比 | +2.35% |
| `change` | 涨跌幅（自动颜色） | +15.67% 🔺 / -5.23% 🟢 |
| `custom` | 自定义格式 | 1.62:1 |

---

### 2. ArtDeco 页面布局

#### 标准页面结构

```vue
<template>
  <div class="page-container">
    <!-- ArtDeco 风格头部 -->
    <div class="artdeco-header">
      <div class="header-title-section">
        <h1 class="page-title">PAGE TITLE</h1>
        <p class="page-subtitle">DESCRIPTION | METADATA | STATUS</p>
      </div>
      <div class="header-actions">
        <el-button type="primary">ACTION</el-button>
      </div>
    </div>

    <!-- 统计卡片网格 -->
    <div class="stats-grid">
      <ArtDecoStatCard
        v-for="stat in statistics"
        :key="stat.label"
        v-bind="stat"
      />
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 页面特定内容 -->
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: #000000;
  min-height: 100vh;
}

.artdeco-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20px;
  border-bottom: 2px solid #1E293B;
}

.page-title {
  font-family: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
  font-size: 28px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #0080FF;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.page-subtitle {
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 11px;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin: 0;
  line-height: 1.4;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
</style>
```

---

## 设计系统

### 颜色规范

#### 主题色彩

```scss
// 核心背景色
$bg-oled: #000000;           // OLED纯黑背景
$bg-card: linear-gradient(135deg, #0F1115 0%, #141A24 100%);  // 卡片渐变
$bg-hover: rgba(0, 128, 255, 0.05);     // 悬停背景
$bg-active: rgba(0, 128, 255, 0.08);    // 激活背景

// 金融色彩
$financial-blue: #0080FF;   // ArtDeco蓝（主色）
$financial-blue-light: #3DA9FC;

// A股涨跌色
$market-up: #FF3B30;        // 上涨（红）
$market-down: #00E676;      // 下跌（绿）
$market-neutral: #94A3B8;   // 持平（灰）

// 文本色
$text-primary: #FFFFFF;
$text-secondary: #94A3B8;
$text-muted: #64748B;

// 边框色
$border-primary: #1E293B;
$border-hover: #334155;
```

#### 颜色使用规则

1. **背景**:
   - 页面背景: `#000000` (纯黑，OLED优化)
   - 卡片背景: 渐变 `#0F1115 → #141A24`
   - 输入框背景: `#0A0A0A`

2. **数据颜色**:
   - 上涨值: `#FF3B30` (A股红色)
   - 下跌值: `#00E676` (A股绿色)
   - 中性/无变化: `#94A3B8`
   - 主标题: `#0080FF` (金融蓝)

3. **文字颜色**:
   - 主要文字: `#FFFFFF` (纯白)
   - 次要文字: `#94A3B8` (蓝灰)
   - 占位符: `#64748B` (深灰)

### 字体规范

#### 字体家族

```scss
// 标题字体
$font-heading: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;

// 正文字体
$font-body: 'IBM Plex Sans', sans-serif;

// 数据字体（等宽）
$font-mono: 'Roboto Mono', 'Courier New', monospace;
```

#### 字体大小

```scss
$font-size-h1: 28px;        // 页面标题
$font-size-h2: 20px;        // 区块标题
$font-size-h3: 16px;        // 卡片标题
$font-size-body: 13px;      // 正文
$font-size-small: 11px;     // 副标题/说明
$font-size-mono: 12px;      // 数据显示
```

#### 字体使用

1. **标题**: 全大写，字间距 0.15em
   ```scss
   .page-title {
     text-transform: uppercase;
     letter-spacing: 0.15em;
   }
   ```

2. **数据**: 使用 Roboto Mono 等宽字体
   ```scss
   .data-value {
     font-family: 'Roboto Mono', monospace;
     font-feature-settings: "tnum";  // 等宽数字
   }
   ```

### 间距规范

```scss
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;
$spacing-xxl: 48px;

// 组件内间距
$card-padding: 20px;
$button-padding: 12px 24px;
$input-padding: 8px 12px;
```

---

## 使用指南

### 快速开始

#### 1. 安装依赖

```bash
npm install element-plus
npm install @element-plus/icons-vue
```

#### 2. 导入组件

```typescript
// 全局注册（main.ts）
import ArtDecoStatCard from '@/components/ArtDecoStatCard.vue'
app.component('ArtDecoStatCard', ArtDecoStatCard)

// 或局部导入
import ArtDecoStatCard from '@/components/ArtDecoStatCard.vue'
```

#### 3. 创建第一个ArtDeco页面

```vue
<!-- Dashboard.vue -->
<template>
  <div class="dashboard-container">
    <!-- 头部 -->
    <div class="dashboard-header">
      <div class="header-title-section">
        <h1 class="page-title">MARKET OVERVIEW</h1>
        <p class="page-subtitle">REAL-TIME MARKET INTELLIGENCE</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <ArtDecoStatCard
        label="TOTAL STOCKS"
        :value="totalStocks"
        icon="data"
        format="number"
      />
      <ArtDecoStatCard
        label="RISING"
        :value="risingStocks"
        icon="trending-up"
        trend="up"
        format="number"
      />
      <ArtDecoStatCard
        label="FALLING"
        :value="fallingStocks"
        icon="trending-down"
        trend="down"
        format="number"
      />
      <ArtDecoStatCard
        label="INDEX"
        :value="indexValue"
        icon="chart"
        format="currency"
      />
    </div>

    <!-- 图表区域 -->
    <div class="chart-section">
      <!-- ECharts 图表 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ArtDecoStatCard from '@/components/ArtDecoStatCard.vue'

const totalStocks = ref(5216)
const risingStocks = ref(2456)
const fallingStocks = ref(1892)
const indexValue = ref(3250.75)

onMounted(() => {
  // 加载数据
})
</script>

<style scoped lang="scss">
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: #000000;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20px;
  border-bottom: 2px solid #1E293B;
}

.header-title-section {
  flex: 1;
}

.page-title {
  font-family: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
  font-size: 28px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #0080FF;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 11px;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.chart-section {
  background: linear-gradient(135deg, #0F1115 0%, #141A24 100%);
  border: 1px solid #1E293B;
  border-radius: 8px;
  padding: 24px;
  min-height: 400px;
}
</style>
```

---

## 样式规范

### 卡片样式

#### ArtDecoStatCard 样式

```scss
.artdeco-stat-card {
  background: linear-gradient(135deg, #0F1115 0%, #141A24 100%);
  border: 1px solid #1E293B;
  border-radius: 8px;
  padding: 20px;
  position: relative;
  overflow: hidden;

  // 微妙的内阴影效果
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);

  // 悬停效果
  transition: all 0.2s ease;

  &:hover {
    border-color: #334155;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  // 卡片头部
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;

    .card-icon {
      color: #0080FF;
      font-size: 16px;
    }

    .card-label {
      font-family: 'IBM Plex Sans', sans-serif;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.15em;
      color: #94A3B8;
    }
  }

  // 卡片数值
  .card-value {
    font-family: 'Roboto Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
    font-feature-settings: "tnum";  // 等宽数字

    // 趋势颜色
    &.trend-up {
      color: #FF3B30;  // A股红色
    }

    &.trend-down {
      color: #00E676;  // A股绿色
    }

    &.trend-neutral {
      color: #94A3B8;
    }
  }

  // 趋势指示器
  .trend-indicator {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 12px;

    &.up {
      color: #FF3B30;
    }

    &.down {
      color: #00E676;
    }

    &.neutral {
      color: #94A3B8;
    }
  }
}
```

### 标签页样式

```scss
.artdeco-tabs-wrapper {
  display: flex;
  gap: 2px;
  border-bottom: 2px solid #1E293B;
  margin-bottom: 24px;
}

.artdeco-tab {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: #94A3B8;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    color: #0080FF;
    background: rgba(0, 128, 255, 0.05);
  }

  &.active {
    color: #0080FF;
    border-bottom-color: #0080FF;
    background: rgba(0, 128, 255, 0.08);
  }
}
```

---

## 最佳实践

### 1. 数据格式化

#### ✅ 推荐做法

```vue
<!-- 使用内置格式 -->
<ArtDecoStatCard
  label="ASSETS"
  :value="1250000.50"
  format="currency"
/>
<!-- 显示: ¥1,250,000.50 -->

<!-- 使用 trend 属性自动着色 -->
<ArtDecoStatCard
  label="CHANGE"
  :value="2.35"
  format="percent"
  trend="up"
/>
<!-- 显示: +2.35% 🔺 (红色) -->
```

#### ❌ 避免做法

```vue
<!-- 手动格式化（维护困难） -->
<ArtDecoStatCard
  label="ASSETS"
  value="¥1,250,000.50"
  format="custom"
/>

<!-- 不使用 trend 属性 -->
<ArtDecoStatCard
  label="CHANGE"
  value="+2.35%"
  :style="{ color: 'red' }"
/>
```

### 2. 加载状态

#### ✅ 推荐做法

```vue
<template>
  <ArtDecoStatCard
    label="TOTAL STOCKS"
    :value="totalStocks"
    :loading="isLoading"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const totalStocks = ref(0)
const isLoading = ref(true)

// 加载数据
fetchData().then(data => {
  totalStocks.value = data.total
  isLoading.value = false
})
</script>
```

### 3. 响应式布局

#### ✅ 推荐做法

```scss
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  // 4列布局
  gap: 16px;

  // 中等屏幕
  @media (max-width: 1440px) {
    grid-template-columns: repeat(3, 1fr);  // 3列
  }

  // 小屏幕
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);  // 2列
  }
}
```

### 4. 性能优化

#### 使用 `v-memo` 优化列表

```vue
<template>
  <div class="stats-grid">
    <ArtDecoStatCard
      v-for="stat in statistics"
      :key="stat.id"
      v-memo="[stat.value, stat.trend]"
      v-bind="stat"
    />
  </div>
</template>
```

#### 防抖高频更新

```typescript
import { ref, watch } from 'vue'
import { debounce } from 'lodash-es'

const realTimeData = ref(0)

// 防抖更新（每500ms最多更新一次）
const debouncedUpdate = debounce((newValue) => {
  realTimeData.value = newValue
}, 500)

// 监听高频数据源
watch(highFrequencyDataSource, (newValue) => {
  debouncedUpdate(newValue)
})
```

---

## 性能优化

### 加载性能

#### 页面加载时间目标

| 指标 | 目标 | 实际 |
|------|------|------|
| 首次内容绘制 (FCP) | < 1s | ~500ms ✅ |
| DOM 交互时间 (TTI) | < 3s | ~1s ✅ |
| 完全加载时间 | < 5s | ~1s ✅ |
| 平均页面加载 | < 4s | ~1s ✅ |

#### 优化策略

1. **组件懒加载**
   ```typescript
   // 按需加载图表组件
   const EChartsComponent = defineAsyncComponent(
     () => import('@/components/EChartsComponent.vue')
   )
   ```

2. **虚拟滚动**（大列表）
   ```vue
   <VirtualList
     :items="largeDataList"
     :item-size="50"
   />
   ```

3. **防抖/节流**（高频更新）
   ```typescript
   import { debounce } from 'lodash-es'

   const updateChartData = debounce(() => {
     // 更新图表逻辑
   }, 300)
   ```

### 渲染性能

#### 使用 `v-once` 静态内容

```vue
<template>
  <div class="card-header" v-once>
    <h1>{{ staticTitle }}</h1>
  </div>

  <div class="card-content">
    <p>{{ dynamicContent }}</p>
  </div>
</template>
```

#### 计算属性缓存

```typescript
import { computed } from 'vue'

// ✅ 使用计算属性（有缓存）
const formattedValue = computed(() => {
  return formatNumber(props.value)
})

// ❌ 避免在模板中直接调用方法
// <div>{{ formatNumber(value) }}</div>
```

---

## 测试指南

### Playwright 测试

项目包含完整的 ArtDeco 组件测试套件。

#### 运行测试

```bash
# 运行所有ArtDeco测试（推荐入口）
npm run test:e2e -- --grep "artdeco"

# 运行特定测试（补充场景：单文件测试）
npx playwright test tests/artdeco/test-artdeco-pages.spec.js

# 运行特定测试用例（补充场景：grep过滤）
npx playwright test tests/artdeco/ --grep "Performance"

# 运行特定浏览器（推荐入口）
npm run test:e2e:chromium -- --grep "artdeco"
```

#### 测试覆盖

**测试文件**: `tests/artdeco/test-artdeco-pages.spec.js`

| 测试类型 | 数量 | 描述 |
|---------|------|------|
| 页面渲染测试 | 3 | Dashboard, Market, Trade Management |
| 组件检查 | 3 | H1元素、统计卡片、标签页 |
| 控制台错误 | 1 | 检测JavaScript错误 |
| 性能监控 | 1 | 页面加载时间、FCP、TTI |
| 无限循环诊断 | 2 | 检测渲染异常 |

#### 测试断言

```javascript
// 页面渲染断言
expect(h1Elements.length).toBeGreaterThanOrEqual(1)
expect(statCards.length).toBe(4)

// 性能断言
expect(loadTime).toBeLessThan(5000)  // 5秒内加载
expect(domInteractive).toBeLessThan(3000)  // 3秒内可交互

// 控制台错误断言
expect(errors.length).toBe(0)  // 0个关键错误
```

### 手动测试清单

#### 功能测试

- [ ] 所有统计卡片正确显示数据
- [ ] 货币格式正确（¥符号、千分位）
- [ ] 百分比格式正确（%符号）
- [ ] 涨跌幅颜色正确（红涨绿跌）
- [ ] 趋势指示器正确显示
- [ ] 加载状态正确显示
- [ ] 图标正确显示

#### 样式测试

- [ ] 背景色为纯黑 (#000000)
- [ ] 卡片渐变背景正确
- [ ] 标题为金融蓝 (#0080FF)
- [ ] 字体使用正确（IBM Plex Sans + Roboto Mono）
- [ ] 间距符合规范
- [ ] 边框颜色正确
- [ ] 悬停效果工作正常

#### 响应式测试

- [ ] 1920x1080 显示正常
- [ ] 1440x900 显示正常
- [ ] 1280x720 显示正常
- [ ] 卡片网格正确响应

---

## 相关文档

### 组件相关

- **ArtDecoStatCard 源码**: `src/components/ArtDecoStatCard.vue`
- **Dashboard 页面**: `src/views/Dashboard.vue`
- **Market 页面**: `src/views/Market.vue`
- **Trade Management 页面**: `src/views/TradeManagement.vue`

### 设计规范

- **颜色规范**: 见上方 [颜色规范](#颜色规范)
- **字体规范**: 见上方 [字体规范](#字体规范)
- **间距规范**: 见上方 [间距规范](#间距规范)

### 测试相关

- **测试套件**: `tests/artdeco/test-artdeco-pages.spec.js`
- **Playwright 配置**: `playwright.config.js`

### 其他参考

- **Element Plus 文档**: https://element-plus.org/
- **ECharts 文档**: https://echarts.apache.org/
- **Vue 3 文档**: https://vuejs.org/

---

## 更新日志

### v1.0.0 (2026-01-09)

**新增**:
- ✅ ArtDecoStatCard 组件
- ✅ ArtDeco 页面布局模板
- ✅ 完整测试套件（21个测试）
- ✅ 性能监控集成
- ✅ 完整使用文档

**性能指标**:
- 平均页面加载时间: 993ms
- 首次内容绘制: ~500ms
- DOM 交互时间: ~1s

**测试覆盖**:
- 3个主要页面测试
- 3个浏览器支持（Chromium, Firefox, WebKit）
- 100% 测试通过率

---

## 贡献指南

### 组件开发

1. **遵循现有样式规范**
   - 使用 ArtDeco 颜色系统
   - 遵循字体和间距规范
   - 保持一致的视觉风格

2. **编写测试**
   - 为新组件添加 Playwright 测试
   - 确保性能指标达标
   - 测试多个浏览器

3. **更新文档**
   - 添加 API 参考
   - 提供使用示例
   - 更新最佳实践

### 代码风格

```typescript
// 组件命名: PascalCase + ArtDeco 前缀
ArtDecoStatCard.vue
ArtDecoChart.vue
ArtDecoTable.vue

// Props 命名: camelCase
interface Props {
  label: string
  value: number
  format?: string
}

// 事件命名: kebab-case
const emit = defineEmits<{
  'update:value': [value: number]
  'card-click': [event: MouseEvent]
}>()
```

---

## 联系方式

**问题反馈**: 请在项目 Issues 中提交
**文档维护**: 开发团队
**最后更新**: 2026-01-09

---

**文档版本**: v1.0.0
**项目**: MyStocks ArtDeco Terminal 组件库
**许可**: MIT License
