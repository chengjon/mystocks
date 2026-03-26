# ArtDeco 组件展示
## ArtDeco Component Showcase

**版本**: v2.0 (Phase 2-4 Enhancements)
**更新日期**: 2026-01-20
**组件总数**: 66 (从 v1.1 的 64 个增加)
**适用范围**: MyStocks 量化交易平台前端

> 治理说明
>
> - 本文档是组件展示与视觉参考，不是当前 SCSS 真值。
> - 当前样式真值以 [ARTDECO_SCSS_GOVERNANCE_BASELINE.md](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md) 为准。
> - 若本文档中的 token 名、导入写法或视觉规则与基线冲突，以基线和源码为准。

---

## 🆕 What's New in v2.0

### Phase 2 Enhancements (2026-01-20)
- ✨ **ArtDecoButton**: 新增 `double-border` 变体 (装饰艺术双线框风格)
- ✨ **ArtDecoInput**: 新增 `labelType="roman"` 罗马数字标签
- ✨ **ArtDecoCard**: 修复为完美锐角 (0px 圆角)

### Phase 3 Reorganization (2026-01-20)
- 📂 **business/** (10组件) - 业务逻辑组件
- 📂 **charts/** (8组件) - 图表可视化组件
- 📂 **trading/** (13组件) - 交易UI组件

### Phase 4 Documentation Update (2026-01-20)
- 📚 更新所有文档以反映新结构
- 📚 添加金融设计令牌文档 (60+ tokens)

---

## 📋 目录

1. [基础组件展示](#基础组件展示) (13组件)
2. [业务组件展示](#业务组件展示) (10组件) ⭐ NEW
3. [图表组件展示](#图表组件展示) (8组件) ⭐ NEW
4. [交易组件展示](#交易组件展示) (13组件) ⭐ NEW
5. [高级组件展示](#高级组件展示) (10组件)
6. [核心组件展示](#核心组件展示) (12组件)
7. [页面级示例](#页面级示例)
8. [交互效果演示](#交互效果演示)

---

## 🎨 基础组件展示

### ArtDecoButton - 按钮组件

#### 变体展示

```vue
<template>
  <div class="button-showcase">
    <h3>Button Variants</h3>

    <!-- 默认按钮 -->
    <ArtDecoButton @click="handleDefault">
      DEFAULT BUTTON
    </ArtDecoButton>

    <!-- 实心按钮 -->
    <ArtDecoButton variant="solid" @click="handleSolid">
      SOLID BUTTON
    </ArtDecoButton>

    <!-- 轮廓按钮 -->
    <ArtDecoButton variant="outline" @click="handleOutline">
      OUTLINE BUTTON
    </ArtDecoButton>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoButton } from '@/components/artdeco'

const handleDefault = () => console.log('Default clicked')
const handleSolid = () => console.log('Solid clicked')
const handleOutline = () => console.log('Outline clicked')
</script>

<style scoped lang="scss">
.button-showcase {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    margin-bottom: 16px;
  }
}
</style>
```

#### 尺寸展示

```vue
<template>
  <div class="button-sizes">
    <h3>Button Sizes</h3>

    <ArtDecoButton size="small" variant="solid">
      SMALL
    </ArtDecoButton>

    <ArtDecoButton size="medium" variant="solid">
      MEDIUM
    </ArtDecoButton>

    <ArtDecoButton size="large" variant="solid">
      LARGE
    </ArtDecoButton>
  </div>
</template>
```

#### 状态展示

```vue
<template>
  <div class="button-states">
    <h3>Button States</h3>

    <ArtDecoButton variant="solid">
      NORMAL
    </ArtDecoButton>

    <ArtDecoButton variant="solid" disabled>
      DISABLED
    </ArtDecoButton>

    <!-- Hover状态需要用户交互展示 -->
    <ArtDecoButton variant="solid" class="hover-demo">
      HOVER ME
    </ArtDecoButton>
  </div>
</template>

<style scoped lang="scss">
.hover-demo:hover {
  box-shadow: var(--artdeco-glow-gold-medium);
}
</style>
```

#### 🆕 Phase 2: 双线框按钮 (Double Border Variant)

```vue
<template>
  <div class="double-border-demo">
    <h3>Double Border Button (Phase 2 Enhancement)</h3>

    <!-- ArtDeco signature style -->
    <ArtDecoButton variant="double-border" size="large">
      DOUBLE BORDER
    </ArtDecoButton>

    <!-- Different sizes -->
    <div class="size-examples">
      <ArtDecoButton variant="double-border" size="small">
        SMALL
      </ArtDecoButton>

      <ArtDecoButton variant="double-border" size="medium">
        MEDIUM
      </ArtDecoButton>

      <ArtDecoButton variant="double-border" size="large">
        LARGE
      </ArtDecoButton>
    </div>

    <!-- With hover effect demonstration -->
    <p class="note">
      <strong>Note:</strong> Hover over the buttons to see the animated border contraction effect (4px → 2px offset)
    </p>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoButton } from '@/components/artdeco'
</script>

<style scoped lang="scss">
.double-border-demo {
  padding: 24px;
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-gold-subtle);

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 24px;
  }

  .size-examples {
    display: flex;
    gap: 16px;
    margin: 16px 0;
    flex-wrap: wrap;
  }

  .note {
    margin-top: 24px;
    padding: 12px;
    background: rgba(212, 175, 55, 0.05);
    border-left: 2px solid var(--artdeco-accent-gold);
    color: var(--artdeco-fg-muted);
    font-size: 14px;
  }
}
</style>
```

**Features**:
- Double-frame style (outer 2px + inner 1px gold borders)
- Perfectly sharp corners (0px radius)
- Smooth hover animation (borders contract from 4px to 2px offset)
- Gold glow effect on hover
- ArtDeco signature visual element



### ArtDecoCard - 卡片组件

#### 基本卡片

```vue
<template>
  <div class="card-showcase">
    <h3>Basic Cards</h3>

    <!-- 简单卡片 -->
    <ArtDecoCard>
      <p>This is a basic Art Deco card with corner brackets and gold border.</p>
    </ArtDecoCard>

    <!-- 带标题的卡片 -->
    <ArtDecoCard>
      <template #header>
        <h4>CARD TITLE</h4>
      </template>
      <p>Card with header section and content area.</p>
    </ArtDecoCard>

    <!-- 带副标题的卡片 -->
    <ArtDecoCard>
      <template #header>
        <h4>SECTION TITLE</h4>
        <p class="subtitle">Card subtitle description</p>
      </template>
      <p>Full featured card with title and subtitle.</p>
    </ArtDecoCard>
  </div>
</template>

<style scoped lang="scss">
.card-showcase {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  padding: 24px;

  h3 {
    grid-column: 1 / -1;
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    margin-bottom: 16px;
  }

  h4 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-wider);
    margin: 0 0 8px 0;
  }

  .subtitle {
    color: var(--artdeco-text-secondary);
    font-size: var(--artdeco-font-size-sm);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-wide);
    margin: 0;
  }
}
</style>
```

#### 悬停效果卡片

```vue
<template>
  <div class="hover-cards">
    <h3>Hover Effects</h3>

    <ArtDecoCard hoverable>
      <template #header>
        <h4>HOVERABLE CARD</h4>
      </template>
      <p>This card lifts up and glows when you hover over it.</p>
      <p>Try hovering to see the theatrical effect!</p>
    </ArtDecoCard>

    <ArtDecoCard hoverable clickable @click="handleCardClick">
      <template #header>
        <h4>CLICKABLE CARD</h4>
      </template>
      <p>This card is both hoverable and clickable.</p>
      <p>Click me to trigger an action.</p>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoCard } from '@/components/artdeco'

const handleCardClick = () => {
  console.log('Card clicked!')
}
</script>
```

### ArtDecoInput - 输入组件

#### 输入类型展示

```vue
<template>
  <div class="input-showcase">
    <h3>Input Types</h3>

    <!-- 基础文本输入 -->
    <ArtDecoInput
      v-model="textValue"
      label="TEXT INPUT"
      placeholder="Enter text here..."
    />

    <!-- 数字输入 -->
    <ArtDecoInput
      v-model="numberValue"
      label="NUMBER INPUT"
      type="number"
      placeholder="Enter number..."
    />

    <!-- 密码输入 -->
    <ArtDecoInput
      v-model="passwordValue"
      label="PASSWORD"
      type="password"
      placeholder="Enter password..."
    />

    <!-- 邮箱输入 -->
    <ArtDecoInput
      v-model="emailValue"
      label="EMAIL ADDRESS"
      type="email"
      placeholder="user@example.com"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoInput } from '@/components/artdeco'

const textValue = ref('')
const numberValue = ref('')
const passwordValue = ref('')
const emailValue = ref('')
const emailValue = ref('')
</script>

<style scoped lang="scss">
.input-showcase {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  padding: 24px;

  h3 {
    grid-column: 1 / -1;
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    margin-bottom: 16px;
  }
}
</style>
```

#### 表单状态展示

```vue
<template>
  <div class="input-states">
    <h3>Input States</h3>

    <!-- 正常状态 -->
    <ArtDecoInput
      v-model="normalValue"
      label="NORMAL STATE"
      placeholder="Normal input"
    />

    <!-- 必填字段 -->
    <ArtDecoInput
      v-model="requiredValue"
      label="REQUIRED FIELD"
      placeholder="This field is required"
      required
    />

    <!-- 错误状态 -->
    <ArtDecoInput
      v-model="errorValue"
      label="ERROR STATE"
      placeholder="Invalid input"
      error-message="This field has an error"
    />

    <!-- 成功状态 -->
    <ArtDecoInput
      v-model="successValue"
      label="SUCCESS STATE"
      placeholder="Valid input"
      helper-text="This input is valid"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoInput } from '@/components/artdeco'

const normalValue = ref('')
const requiredValue = ref('')
const errorValue = ref('')
const successValue = ref('')
</script>
```

#### 🆕 Phase 2: 罗马数字标签 (Roman Numeral Labels)

```vue
<template>
  <div class="roman-numeral-demo">
    <h3>Roman Numeral Input Labels (Phase 2 Enhancement)</h3>

    <div class="form-grid">
      <!-- Auto-detects trailing numbers -->
      <ArtDecoInput
        v-model="username"
        label="USERNAME 1"
        label-type="roman"
        placeholder="Enter username..."
      />
      <!-- Displays: USERNAME Ⅰ -->

      <ArtDecoInput
        v-model="email"
        label="EMAIL 2"
        label-type="roman"
        type="email"
        placeholder="Enter email..."
      />
      <!-- Displays: EMAIL Ⅱ -->

      <ArtDecoInput
        v-model="password"
        label="PASSWORD 3"
        label-type="roman"
        type="password"
        placeholder="Enter password..."
      />
      <!-- Displays: PASSWORD Ⅲ -->

      <ArtDecoInput
        v-model="confirmPassword"
        label="CONFIRM PASSWORD 4"
        label-type="roman"
        type="password"
        placeholder="Confirm password..."
      />
      <!-- Displays: CONFIRM PASSWORD Ⅳ -->

      <!-- Higher numbers -->
      <ArtDecoInput
        v-model="phone"
        label="PHONE 5"
        label-type="roman"
        placeholder="Enter phone..."
      />
      <!-- Displays: PHONE Ⅴ -->

      <ArtDecoInput
        v-model="address"
        label="ADDRESS 10"
        label-type="roman"
        placeholder="Enter address..."
      />
      <!-- Displays: ADDRESS Ⅹ -->
    </div>

    <p class="note">
      <strong>Feature:</strong> Automatically converts trailing numbers to Roman numerals (Ⅰ-Ⅹ supported).
      Falls back to appending "Ⅰ" if no number is detected.
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoInput } from '@/components/artdeco'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const phone = ref('')
const address = ref('')
</script>

<style scoped lang="scss">
.roman-numeral-demo {
  padding: 24px;
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-gold-subtle);

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 24px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
  }

  .note {
    padding: 12px;
    background: rgba(212, 175, 55, 0.05);
    border-left: 2px solid var(--artdeco-accent-gold);
    color: var(--artdeco-fg-muted);
    font-size: 14px;
  }
}
</style>
```

**Supported Numbers**: 1-20 (Ⅰ, Ⅱ, Ⅲ, Ⅳ, Ⅴ, Ⅵ, Ⅶ, Ⅷ, Ⅸ, Ⅹ, Ⅺ, Ⅻ, Ⅼ, Ⅽ, Ⅾ, Ⅿ, ⅰ, ⅱ, ⅳ, Ⅹ)

**Features**:
- Auto-detects trailing numbers in labels
- Preserves original label casing
- Adds decorative ArtDeco flair to forms
- Perfect for multi-step forms or sequences



---

## 📊 业务组件展示 (Business Components)

### ArtDecoDateRange - 日期范围选择器

```vue
<template>
  <div class="date-range-demo">
    <h3>Backtest Date Range</h3>

    <ArtDecoDateRange
      v-model:start-date="startDate"
      v-model:end-date="endDate"
      label="DATE RANGE"
      :max-range="365"
      :min-date="minDate"
      :max-date="maxDate"
    />

    <div class="selected-info">
      <p>Start: {{ startDate }}</p>
      <p>End: {{ endDate }}</p>
      <p>Days: {{ dayCount }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArtDecoDateRange } from '@/components/artdeco/business'

const startDate = ref('2024-01-01')
const endDate = ref('2024-12-31')
const minDate = ref('2020-01-01')
const maxDate = ref(new Date().toISOString().split('T')[0])

const dayCount = computed(() => {
  const start = new Date(startDate.value)
  const end = new Date(endDate.value)
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
})
</script>

<style scoped lang="scss">
.date-range-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }

  .selected-info {
    margin-top: 16px;
    padding: 16px;
    background: rgba(212, 175, 55, 0.05);
    border: 1px solid var(--artdeco-border-gold-subtle);

    p {
      color: var(--artdeco-fg-primary);
      margin: 4px 0;
      font-family: var(--artdeco-font-body);
    }
  }
}
</style>
```

### ArtDecoFilterBar - 筛选栏

```vue
<template>
  <div class="filter-bar-demo">
    <h3>Market Data Filters</h3>

    <ArtDecoFilterBar
      :filters="[
        { key: 'symbol', label: 'SYMBOL', type: 'input', placeholder: 'Search symbol...' },
        { key: 'sector', label: 'SECTOR', type: 'select', options: ['All', 'Technology', 'Healthcare', 'Finance'] },
        { key: 'marketCap', label: 'MARKET CAP', type: 'select', options: ['All', 'Large', 'Medium', 'Small'] },
        { key: 'dateRange', label: 'DATE RANGE', type: 'daterange' }
      ]"
      @filter-change="handleFilterChange"
      @filter-reset="handleFilterReset"
    />
  </div>
</template>

<script setup lang="ts">
import { ArtDecoFilterBar } from '@/components/artdeco/business'

const handleFilterChange = (filters) => {
  console.log('Filters changed:', filters)
  // Apply filters to data
}

const handleFilterReset = () => {
  console.log('Filters reset')
  // Reset all filters
}
</script>

<style scoped lang="scss">
.filter-bar-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }
}
</style>
```

### ArtDecoSlider - 滑块控制

```vue
<template>
  <div class="slider-demo">
    <h3>Risk Tolerance</h3>

    <ArtDecoSlider
      v-model="riskLevel"
      :min="0"
      :max="100"
      :step="5"
      label="RISK LEVEL"
      :marks="{ 0: 'Conservative', 50: 'Moderate', 100: 'Aggressive' }"
      :show-value="true"
    />

    <div class="risk-info">
      <p :style="{ color: riskColor }">
        Risk Level: {{ riskLabel }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArtDecoSlider } from '@/components/artdeco/business'

const riskLevel = ref(50)

const riskLabel = computed(() => {
  if (riskLevel.value < 30) return 'Conservative'
  if (riskLevel.value < 70) return 'Moderate'
  return 'Aggressive'
})

const riskColor = computed(() => {
  if (riskLevel.value < 30) return 'var(--artdeco-risk-low)'
  if (riskLevel.value < 70) return 'var(--artdeco-risk-medium)'
  return 'var(--artdeco-risk-high)'
})
</script>

<style scoped lang="scss">
.slider-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }

  .risk-info {
    margin-top: 16px;

    p {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-text-lg);
      text-transform: uppercase;
    }
  }
}
</style>
```

---

## 📈 图表组件展示 (Chart Components)

### TimeSeriesChart - 时序图

```vue
<template>
  <div class="timeseries-demo">
    <h3>Price Chart</h3>

    <ArtDecoCard variant="chart">
      <template #header>
        <h4>600519 - 贵州茅台</h4>
      </template>

      <TimeSeriesChart
        :data="priceData"
        :indicators="['MA5', 'MA20', 'MA60']"
        :timeframe="timeframe"
        height="400px"
        @indicator-change="handleIndicatorChange"
        @timeframe-change="handleTimeframeChange"
      />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoCard } from '@/components/artdeco'
import { TimeSeriesChart } from '@/components/artdeco/charts'

const timeframe = ref('1D')

const priceData = ref([
  { timestamp: '2024-01-01', open: 1800, high: 1850, low: 1790, close: 1840, volume: 125000 },
  { timestamp: '2024-01-02', open: 1840, high: 1860, low: 1830, close: 1850, volume: 130000 },
  // ... more data
])

const handleIndicatorChange = (indicators) => {
  console.log('Indicators changed:', indicators)
}

const handleTimeframeChange = (newTimeframe) => {
  timeframe.value = newTimeframe
}
</script>

<style scoped lang="scss">
.timeseries-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }

  h4 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    margin: 0;
  }
}
</style>
```

### DrawdownChart - 回撤图

```vue
<template>
  <div class="drawdown-demo">
    <h3>Strategy Drawdown</h3>

    <ArtDecoCard variant="chart">
      <template #header>
        <h4>DRAWDOWN ANALYSIS</h4>
      </template>

      <DrawdownChart
        :data="drawdownData"
        :benchmark="benchmarkData"
        height="300px"
        :show-tooltip="true"
      />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoCard } from '@/components/artdeco'
import { DrawdownChart } from '@/components/artdeco/charts'

const drawdownData = ref([
  { date: '2024-01', value: -5.2 },
  { date: '2024-02', value: -8.5 },
  { date: '2024-03', value: -3.1 },
  // ... more data
])

const benchmarkData = ref([
  { date: '2024-01', value: -2.1 },
  { date: '2024-02', value: -4.5 },
  { date: '2024-03', value: -1.8 },
  // ... more data
])
</script>

<style scoped lang="scss">
.drawdown-demo {
  padding: 24px;

  h3, h4 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }

  h4 {
    font-size: var(--artdeco-text-xl);
  }
}
</style>
```

### HeatmapCard - 热力图

```vue
<template>
  <div class="heatmap-demo">
    <h3>Sector Performance</h3>

    <ArtDecoCard variant="chart">
      <template #header>
        <h4>MARKET HEATMAP</h4>
      </template>

      <HeatmapCard
        :data="heatmapData"
        :color-scale="['#00E676', '#FFD700', '#FF5252']"
        height="350px"
        @cell-click="handleCellClick"
      />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoCard } from '@/components/artdeco'
import { HeatmapCard } from '@/components/artdeco/charts'

const heatmapData = ref([
  { sector: 'Technology', change: 2.15, cap: 5000000000000 },
  { sector: 'Healthcare', change: -0.85, cap: 3500000000000 },
  { sector: 'Finance', change: 1.35, cap: 4200000000000 },
  { sector: 'Energy', change: 3.20, cap: 2800000000000 },
  // ... more sectors
])

const handleCellClick = (cell) => {
  console.log('Cell clicked:', cell)
  // Navigate to sector detail
}
</script>

<style scoped lang="scss">
.heatmap-demo {
  padding: 24px;

  h3, h4 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }
}
</style>
```

---

## 💹 交易组件展示 (Trading Components)

### ArtDecoOrderBook - 订单簿

```vue
<template>
  <div class="orderbook-demo">
    <h3>Order Book</h3>

    <ArtDecoOrderBook
      :bids="bidData"
      :asks="askData"
      :max-rows="10"
      :show-total="true"
      @price-click="handlePriceClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoOrderBook } from '@/components/artdeco/trading'

const bidData = ref([
  { price: 1850.50, quantity: 1200, total: 10 },
  { price: 1850.00, quantity: 2500, total: 25 },
  { price: 1849.50, quantity: 1800, total: 18 },
  // ... more bids
])

const askData = ref([
  { price: 1851.00, quantity: 900, total: 9 },
  { price: 1851.50, quantity: 2100, total: 21 },
  { price: 1852.00, quantity: 1600, total: 16 },
  // ... more asks
])

const handlePriceClick = (price) => {
  console.log('Price clicked:', price)
  // Set order price
}
</script>

<style scoped lang="scss">
.orderbook-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }
}
</style>
```

### ArtDecoTradeForm - 交易表单

```vue
<template>
  <div class="trade-form-demo">
    <h3>Place Order</h3>

    <ArtDecoCard>
      <ArtDecoTradeForm
        v-model:symbol="orderSymbol"
        v-model:side="orderSide"
        v-model:quantity="orderQuantity"
        v-model:price="orderPrice"
        v-model:order-type="orderType"
        :available-quantity="availableQuantity"
        :current-price="currentPrice"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoCard, ArtDecoTradeForm } from '@/components/artdeco'

const orderSymbol = ref('600519')
const orderSide = ref('buy')
const orderQuantity = ref(100)
const orderPrice = ref(1850.50)
const orderType = ref('limit')
const availableQuantity = ref(10000)
const currentPrice = ref(1850.50)

const handleSubmit = (order) => {
  console.log('Submit order:', order)
  // Submit order to backend
}

const handleCancel = () => {
  console.log('Order cancelled')
  // Reset form
}
</script>

<style scoped lang="scss">
.trade-form-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }
}
</style>
```

### ArtDecoTicker - 行情显示

```vue
<template>
  <div class="ticker-demo">
    <h3>Market Ticker</h3>

    <ArtDecoTicker
      :symbols="tickerData"
      :update-interval="3000"
      :flash-changes="true"
      @symbol-click="handleSymbolClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoTicker } from '@/components/artdeco/trading'

const tickerData = ref([
  { symbol: '600519', name: '贵州茅台', price: 1850.50, change: 12.50, changePercent: 0.68 },
  { symbol: '000001', name: '平安银行', price: 12.45, change: -0.15, changePercent: -1.19 },
  { symbol: '000002', name: '万科A', price: 8.90, change: 0.05, changePercent: 0.56 },
  // ... more symbols
])

const handleSymbolClick = (symbol) => {
  console.log('Symbol clicked:', symbol)
  // Navigate to symbol detail
}
</script>

<style scoped lang="scss">
.ticker-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    margin-bottom: 16px;
  }
}
</style>
```

---

## 🔧 专用组件展示 (Archived - Moved to New Categories)

### 金融专用组件

#### ArtDecoStatCard - 统计卡片

```vue
<template>
  <div class="stats-dashboard">
    <h3>Portfolio Statistics</h3>

    <div class="stats-grid">
      <ArtDecoStatCard
        title="TOTAL VALUE"
        :value="1256789.45"
        format="currency"
        trend="up"
        :change="12.5"
      />

      <ArtDecoStatCard
        title="TODAY'S GAIN"
        :value="2345.67"
        format="currency"
        trend="up"
        :change="2.3"
      />

      <ArtDecoStatCard
        title="TOTAL STOCKS"
        :value="45"
        format="number"
      />

      <ArtDecoStatCard
        title="WIN RATE"
        :value="68.5"
        format="percentage"
        trend="up"
        :change="0.5"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoStatCard } from '@/components/artdeco'
</script>

<style scoped lang="scss">
.stats-dashboard {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    text-align: center;
    margin-bottom: 32px;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
  }
}
</style>
```

#### ArtDecoTable - 数据表格

```vue
<template>
  <div class="table-showcase">
    <h3>Stock Holdings</h3>

    <ArtDecoCard>
      <ArtDecoTable
        :columns="columns"
        :data="tableData"
        :sortable="true"
        :striped="true"
      >
        <template #action="{ row }">
          <div class="action-buttons">
            <ArtDecoButton size="small" variant="outline" @click="viewPosition(row)">
              VIEW
            </ArtDecoButton>
            <ArtDecoButton size="small" variant="solid" @click="closePosition(row)">
              CLOSE
            </ArtDecoButton>
          </div>
        </template>
      </ArtDecoTable>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoTable, ArtDecoCard, ArtDecoButton } from '@/components/artdeco'

const columns = [
  { key: 'symbol', label: 'SYMBOL', sortable: true },
  { key: 'quantity', label: 'QUANTITY', sortable: true },
  { key: 'avgPrice', label: 'AVG PRICE', sortable: true, format: 'currency' },
  { key: 'currentPrice', label: 'CURRENT', sortable: true, format: 'currency' },
  { key: 'pnl', label: 'P&L', sortable: true, format: 'currency' },
  { key: 'pnlPercent', label: 'P&L %', sortable: true, format: 'percentage' },
  { key: 'action', label: 'ACTION', width: '160px' }
]

const tableData = ref([
  {
    symbol: '600519',
    quantity: 100,
    avgPrice: 1800.00,
    currentPrice: 1850.50,
    pnl: 5050.00,
    pnlPercent: 2.81
  },
  // ... more positions
])

const viewPosition = (position) => {
  console.log('View position:', position)
}

const closePosition = (position) => {
  console.log('Close position:', position)
}
</script>

<style scoped lang="scss">
.table-showcase {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    text-align: center;
    margin-bottom: 24px;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }
}
</style>
```

---

## 🚀 高级组件展示

### ArtDecoMarketPanorama - 市场全景

```vue
<template>
  <div class="market-panorama">
    <h3>MARKET PANORAMA</h3>

    <ArtDecoMarketPanorama
      :market-data="marketData"
      :time-range="selectedTimeRange"
      @sector-click="handleSectorClick"
      @index-click="handleIndexClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoMarketPanorama } from '@/components/artdeco'

const selectedTimeRange = ref('1D')

const marketData = {
  indices: [
    { name: '上证指数', value: 3128.45, change: 1.25, changePercent: 0.04 },
    { name: '深证成指', value: 10245.67, change: -45.23, changePercent: -0.44 },
    { name: '创业板指', value: 2156.89, change: 12.34, changePercent: 0.58 }
  ],
  sectors: [
    { name: '科技', changePercent: 2.15, volume: 1250000000 },
    { name: '医药', changePercent: -0.85, volume: 980000000 },
    { name: '新能源', changePercent: 1.95, volume: 1560000000 },
    // ... more sectors
  ]
}

const handleSectorClick = (sector) => {
  console.log('Sector clicked:', sector)
}

const handleIndexClick = (index) => {
  console.log('Index clicked:', index)
}
</script>

<style scoped lang="scss">
.market-panorama {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    text-align: center;
    margin-bottom: 32px;
  }
}
</style>
```

### ArtDecoTechnicalAnalysis - 技术分析

```vue
<template>
  <div class="technical-analysis">
    <h3>TECHNICAL ANALYSIS</h3>

    <ArtDecoTechnicalAnalysis
      :symbol="selectedSymbol"
      :indicators="selectedIndicators"
      :timeframe="selectedTimeframe"
      @indicator-toggle="handleIndicatorToggle"
      @timeframe-change="handleTimeframeChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoTechnicalAnalysis } from '@/components/artdeco'

const selectedSymbol = ref('600519')
const selectedTimeframe = ref('1D')
const selectedIndicators = ref(['MA', 'RSI', 'MACD'])

const handleIndicatorToggle = (indicator, enabled) => {
  console.log('Indicator toggled:', indicator, enabled)
}

const handleTimeframeChange = (timeframe) => {
  selectedTimeframe.value = timeframe
}
</script>

<style scoped lang="scss">
.technical-analysis {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    text-align: center;
    margin-bottom: 32px;
  }
}
</style>
```

---

## 🏗️ 核心组件展示

### ArtDecoAnalysisDashboard - 分析仪表盘

```vue
<template>
  <div class="analysis-dashboard">
    <ArtDecoAnalysisDashboard
      :user-id="currentUserId"
      :default-analysis-type="defaultAnalysisType"
      @analysis-start="handleAnalysisStart"
      @analysis-complete="handleAnalysisComplete"
      @dashboard-customize="handleDashboardCustomize"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoAnalysisDashboard } from '@/components/artdeco'

const currentUserId = ref('user123')
const defaultAnalysisType = ref('technical')

const handleAnalysisStart = (config) => {
  console.log('Analysis started:', config)
}

const handleAnalysisComplete = (results) => {
  console.log('Analysis completed:', results)
}

const handleDashboardCustomize = (customization) => {
  console.log('Dashboard customized:', customization)
}
</script>

<style scoped lang="scss">
.analysis-dashboard {
  min-height: 100vh;
  padding: 24px;

  @include artdeco-crosshatch-bg;
}
</style>
```

---

## 📄 页面级示例

### 完整仪表盘页面

```vue
<template>
  <div class="dashboard-page">
    <!-- 页面头部 -->
    <ArtDecoHeader
      title="TRADING DASHBOARD"
      subtitle="Real-time market analysis and portfolio management"
    />

    <!-- 面包屑导航 -->
    <ArtDecoBreadcrumb
      :items="[
        { label: 'HOME', path: '/' },
        { label: 'DASHBOARD', path: '/dashboard' }
      ]"
    />

    <!-- 工具栏 -->
    <div class="page-toolbar">
      <ArtDecoFilterBar
        :filters="[
          { key: 'timeRange', label: 'TIME RANGE', type: 'select', options: ['1D', '1W', '1M'] },
          { key: 'symbol', label: 'SYMBOL', type: 'input', placeholder: 'Enter symbol...' }
        ]"
        @filter-change="handleFilterChange"
      />
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <div class="stats-grid">
        <ArtDecoStatCard
          title="PORTFOLIO VALUE"
          :value="portfolioValue"
          format="currency"
          trend="up"
          :change="portfolioChange"
        />

        <ArtDecoStatCard
          title="TODAY'S P&L"
          :value="todaysPnL"
          format="currency"
          :trend="todaysPnL >= 0 ? 'up' : 'down'"
          :change="todaysPnLPercent"
        />

        <ArtDecoStatCard
          title="TOTAL POSITIONS"
          :value="totalPositions"
          format="number"
        />

        <ArtDecoStatCard
          title="WIN RATE"
          :value="winRate"
          format="percentage"
          trend="up"
          :change="0.5"
        />
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="charts-grid">
        <ArtDecoCard variant="chart">
          <template #header>
            <h4>MARKET OVERVIEW</h4>
          </template>
          <TimeSeriesChart
            :data="marketData"
            :indicators="['MA', 'RSI']"
            height="350px"
          />
        </ArtDecoCard>

        <ArtDecoCard variant="chart">
          <template #header>
            <h4>PORTFOLIO ALLOCATION</h4>
          </template>
          <HeatmapCard :data="portfolioData" height="350px" />
        </ArtDecoCard>
      </div>
    </div>

    <!-- 数据表格区域 -->
    <div class="table-section">
      <ArtDecoCard>
        <template #header>
          <h4>POSITIONS</h4>
        </template>
        <ArtDecoTable
          :columns="positionColumns"
          :data="positionData"
          :sortable="true"
          :striped="true"
        >
          <template #action="{ row }">
            <div class="action-buttons">
              <ArtDecoButton size="small" variant="outline" @click="viewPosition(row)">
                VIEW
              </ArtDecoButton>
              <ArtDecoButton size="small" variant="solid" @click="closePosition(row)">
                CLOSE
              </ArtDecoButton>
            </div>
          </template>
        </ArtDecoTable>
      </ArtDecoCard>
    </div>

    <!-- 页面底部 -->
    <ArtDecoFooter />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  ArtDecoHeader,
  ArtDecoBreadcrumb,
  ArtDecoFilterBar,
  ArtDecoStatCard,
  ArtDecoCard,
  ArtDecoTable,
  ArtDecoButton,
  ArtDecoFooter
} from '@/components/artdeco'
import { TimeSeriesChart, HeatmapCard } from '@/components/chart'

// 响应式数据
const portfolioValue = ref(1256789.45)
const todaysPnL = ref(3456.78)
const totalPositions = ref(12)
const winRate = ref(68.5)

const portfolioChange = computed(() => 12.5)
const todaysPnLPercent = computed(() => (todaysPnL.value / portfolioValue.value) * 100)

// 图表数据
const marketData = ref([])
const portfolioData = ref([])

// 表格配置
const positionColumns = [
  { key: 'symbol', label: 'SYMBOL', sortable: true },
  { key: 'quantity', label: 'QUANTITY', sortable: true },
  { key: 'avgPrice', label: 'AVG PRICE', sortable: true, format: 'currency' },
  { key: 'currentPrice', label: 'CURRENT', sortable: true, format: 'currency' },
  { key: 'pnl', label: 'P&L', sortable: true, format: 'currency' },
  { key: 'pnlPercent', label: 'P&L %', sortable: true, format: 'percentage' },
  { key: 'action', label: 'ACTION', width: '160px' }
]

const positionData = ref([
  {
    symbol: '600519',
    quantity: 100,
    avgPrice: 1800.00,
    currentPrice: 1850.50,
    pnl: 5050.00,
    pnlPercent: 2.81
  },
  // ... more positions
])

// 事件处理
const handleFilterChange = (filters) => {
  console.log('Filters changed:', filters)
  // 应用筛选逻辑
}

const viewPosition = (position) => {
  console.log('View position:', position)
  // 导航到持仓详情
}

const closePosition = (position) => {
  console.log('Close position:', position)
  // 关闭持仓逻辑
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';

.dashboard-page {
  min-height: 100vh;
  @include artdeco-crosshatch-bg;

  .page-toolbar {
    margin: 24px 0;
  }

  .stats-section {
    margin-bottom: 32px;

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 24px;
    }
  }

  .charts-section {
    margin-bottom: 32px;

    .charts-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;

      @media (max-width: 1024px) {
        grid-template-columns: 1fr;
      }
    }

    h4 {
      font-family: var(--artdeco-font-display);
      color: var(--artdeco-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-letter-spacing-wider);
      margin: 0 0 16px 0;
    }
  }

  .table-section {
    h4 {
      font-family: var(--artdeco-font-display);
      color: var(--artdeco-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-letter-spacing-wider);
      margin: 0 0 16px 0;
    }

    .action-buttons {
      display: flex;
      gap: 8px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dashboard-page {
    .stats-section .stats-grid {
      grid-template-columns: 1fr;
      gap: 16px;
    }

    .charts-section .charts-grid {
      grid-template-columns: 1fr;
      gap: 16px;
    }
  }
}
</style>
```

---

## ✨ 交互效果演示

### 悬停效果

```vue
<template>
  <div class="interaction-demo">
    <h3>Interaction Effects</h3>

    <div class="demo-grid">
      <!-- 按钮悬停 -->
      <ArtDecoCard>
        <template #header>
          <h4>BUTTON HOVER</h4>
        </template>
        <p>Hover over the button to see the gold glow effect</p>
        <ArtDecoButton variant="solid">
          HOVER ME
        </ArtDecoButton>
      </ArtDecoCard>

      <!-- 卡片悬停 -->
      <ArtDecoCard hoverable>
        <template #header>
          <h4>CARD HOVER</h4>
        </template>
        <p>This card lifts up and glows when hovered</p>
      </ArtDecoCard>

      <!-- 输入焦点 -->
      <ArtDecoCard>
        <template #header>
          <h4>INPUT FOCUS</h4>
        </template>
        <p>Click on the input to see the gold border animation</p>
        <ArtDecoInput
          v-model="demoInput"
          label="DEMO INPUT"
          placeholder="Focus me..."
        />
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoCard, ArtDecoButton, ArtDecoInput } from '@/components/artdeco'

const demoInput = ref('')
</script>

<style scoped lang="scss">
.interaction-demo {
  padding: 24px;

  h3 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-title);
    text-align: center;
    margin-bottom: 32px;
  }

  h4 {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-letter-spacing-wider);
    margin: 0 0 8px 0;
  }

  .demo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
  }

  p {
    color: var(--artdeco-text-secondary);
    margin-bottom: 16px;
  }
}
</style>
```

---

## 📚 相关资源

- **[实施指南](./ART_DECO_IMPLEMENTATION_REPORT.md)** - 详细的实施指南
- **[快速参考](./ART_DECO_QUICK_REFERENCE.md)** - 快速参考手册
- **[组件目录](./ARTDECO_COMPONENTS_CATALOG.md)** - 完整组件清单

---

**版本**: v1.1 | **更新**: 2026-01-18 | **维护**: Frontend Team</content>
<parameter name="filePath">/opt/claude/mystocks_spec/docs/guides/web/ART_DECO_COMPONENT_SHOWCASE_V2.md
