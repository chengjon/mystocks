# MyStocks 组件库规范文档

> **版本**: 1.0.0
> **基于**: Element Plus 2.4+ / Vue 3.4+
> **最后更新**: 2025-11-09

---

## 目录

1. [概述](#1-概述)
2. [基础组件](#2-基础组件)
3. [业务组件](#3-业务组件)
4. [图表组件](#4-图表组件)
5. [复合组件](#5-复合组件)
6. [组件开发规范](#6-组件开发规范)
7. [组件测试规范](#7-组件测试规范)

---

## 1. 概述

### 1.1 组件库架构

```
src/components/
├── base/              # 基础组件 (Element Plus 封装)
│   ├── Button/
│   ├── Input/
│   ├── Table/
│   └── Card/
├── business/          # 业务组件
│   ├── /     # 数值单元格
│   ├── StockCard/     # 股票卡片
│   └── TrendIndicator/
├── charts/            # 图表组件
│   ├── KLineChart/    # K线图
│   ├── VolumeChart/   # 成交量图
│   └── IndicatorChart/
└── composite/         # 复合组件
    ├── StockSearchBar/
    ├── TechnicalAnalysis/
    └── IndicatorPanel/
```

### 1.2 组件命名规范

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| **基础组件** | `My[ElementName]` | `MyButton`, `MyTable` |
| **业务组件** | `[Domain][Function]` | `StockCard`, `TrendIndicator` |
| **图表组件** | `[ChartType]Chart` | `KLineChart`, `VolumeChart` |
| **复合组件** | `[Feature][Type]` | `StockSearchBar`, `IndicatorPanel` |

### 1.3 设计 Token 引用

所有组件应使用 `design-tokens.json` 中定义的设计变量:

```vue
<script setup>
import tokens from '@/assets/design-tokens.json'

const primaryColor = tokens.colors.primary.$value
const spacing = tokens.spacing.md.$value
</script>
```

---

## 2. 基础组件

### 2.1 MyButton 按钮组件

#### 2.1.1 组件定义

```vue
<!-- src/components/base/Button/MyButton.vue -->
<template>
  <el-button
    :type="type"
    :size="size"
    :icon="icon"
    :loading="loading"
    :disabled="disabled"
    :plain="plain"
    :round="round"
    :circle="circle"
    @click="handleClick"
  >
    <slot></slot>
  </el-button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['large', 'default', 'small'].includes(value)
  },
  icon: String,
  loading: Boolean,
  disabled: Boolean,
  plain: Boolean,
  round: Boolean,
  circle: Boolean
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  if (!props.loading && !props.disabled) {
    emit('click', event)
  }
}
</script>
```

#### 2.1.2 Props 规范

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | String | `'default'` | 按钮类型: `default` `primary` `success` `warning` `danger` `info` |
| `size` | String | `'default'` | 尺寸: `large` `default` `small` |
| `icon` | String | - | 图标类名 (Element Plus Icon) |
| `loading` | Boolean | `false` | 加载状态 |
| `disabled` | Boolean | `false` | 禁用状态 |
| `plain` | Boolean | `false` | 朴素按钮 |
| `round` | Boolean | `false` | 圆角按钮 |
| `circle` | Boolean | `false` | 圆形按钮 |

#### 2.1.3 Events 规范

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `click` | `(event: MouseEvent)` | 点击事件 (loading/disabled 时不触发) |

#### 2.1.4 使用示例

```vue
<template>
  <!-- 基本用法 -->
  <MyButton type="primary">主要按钮</MyButton>

  <!-- 加载状态 -->
  <MyButton type="primary" :loading="isLoading" @click="handleSubmit">
    提交
  </MyButton>

  <!-- 图标按钮 -->
  <MyButton type="success" icon="Check" round>确认</MyButton>
</template>

<script setup>
import { ref } from 'vue'
import MyButton from '@/components/base/Button/MyButton.vue'

const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true
  try {
    await submitData()
  } finally {
    isLoading.value = false
  }
}
</script>
```

---

### 2.2 MyTable 表格组件

#### 2.2.1 组件定义

```vue
<!-- src/components/base/Table/MyTable.vue -->
<template>
  <el-table
    :data="data"
    :height="height"
    :max-height="maxHeight"
    :stripe="stripe"
    :border="border"
    :size="size"
    :highlight-current-row="highlightCurrentRow"
    @selection-change="handleSelectionChange"
    @sort-change="handleSortChange"
    @row-click="handleRowClick"
  >
    <slot></slot>
  </el-table>
</template>

<script setup>
const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  height: [String, Number],
  maxHeight: [String, Number],
  stripe: {
    type: Boolean,
    default: true
  },
  border: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['large', 'default', 'small'].includes(value)
  },
  highlightCurrentRow: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['selection-change', 'sort-change', 'row-click'])

const handleSelectionChange = (selection) => {
  emit('selection-change', selection)
}

const handleSortChange = ({ column, prop, order }) => {
  emit('sort-change', { column, prop, order })
}

const handleRowClick = (row, column, event) => {
  emit('row-click', row, column, event)
}
</script>
```

#### 2.2.2 Props 规范

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | Array | **必填** | 表格数据 |
| `height` | String/Number | - | 固定高度 |
| `maxHeight` | String/Number | - | 最大高度 |
| `stripe` | Boolean | `true` | 斑马纹 |
| `border` | Boolean | `false` | 边框 |
| `size` | String | `'default'` | 尺寸: `large` `default` `small` |
| `highlightCurrentRow` | Boolean | `true` | 高亮当前行 |

#### 2.2.3 Events 规范

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `selection-change` | `(selection: Array)` | 选择项变化 |
| `sort-change` | `({ column, prop, order })` | 排序变化 |
| `row-click` | `(row, column, event)` | 行点击 |

#### 2.2.4 使用示例

```vue
<template>
  <MyTable
    :data="tableData"
    stripe
    @row-click="handleRowClick"
  >
    <el-table-column type="selection" width="55" />
    <el-table-column prop="code" label="股票代码" width="120" sortable />
    <el-table-column prop="name" label="股票名称" width="180" />
    <el-table-column prop="price" label="当前价" width="120">
      <template #default="{ row }">
        < :value="row.price" :change="row.change" />
      </template>
    </el-table-column>
    <el-table-column prop="volume" label="成交量" sortable />
  </MyTable>
</template>

<script setup>
import { ref } from 'vue'
import MyTable from '@/components/base/Table/MyTable.vue'
import  from '@/components/business//.vue'

const tableData = ref([
  { code: '000001', name: '平安银行', price: 12.34, change: 2.5, volume: 123456 },
  { code: '000002', name: '万科A', price: 8.90, change: -1.2, volume: 234567 }
])

const handleRowClick = (row) => {
  console.log('Clicked row:', row)
}
</script>
```

---

## 3. 业务组件

### 3.1  数值单元格组件

#### 3.1.1 组件定义

```vue
<!-- src/components/business//.vue -->
<template>
  <span
    :class="[
      'value-cell',
      trendClass,
      sizeClass
    ]"
    :style="cellStyle"
  >
    <template v-if="showIcon">
      <el-icon class="trend-icon">
        <CaretTop v-if="trend === 'up'" />
        <CaretBottom v-if="trend === 'down'" />
        <Minus v-if="trend === 'flat'" />
      </el-icon>
    </template>

    <span class="value-text">
      {{ formattedValue }}
    </span>

    <template v-if="showChange && change !== null">
      <span class="change-text">
        ({{ changeText }})
      </span>
    </template>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { CaretTop, CaretBottom, Minus } from '@element-plus/icons-vue'
import tokens from '@/assets/design-tokens.json'

const props = defineProps({
  value: {
    type: [Number, String],
    required: true
  },
  change: {
    type: Number,
    default: null
  },
  precision: {
    type: Number,
    default: 2
  },
  unit: {
    type: String,
    default: ''
  },
  showIcon: {
    type: Boolean,
    default: false
  },
  showChange: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['large', 'default', 'small'].includes(value)
  }
})

const trend = computed(() => {
  if (props.change === null || props.change === 0) return 'flat'
  return props.change > 0 ? 'up' : 'down'
})

const trendClass = computed(() => {
  return `trend-${trend.value}`
})

const sizeClass = computed(() => {
  return `size-${props.size}`
})

const cellStyle = computed(() => {
  const colors = tokens.colors.financial
  const colorMap = {
    up: colors.up.$value,
    down: colors.down.$value,
    flat: colors.flat.$value
  }

  return {
    color: colorMap[trend.value]
  }
})

const formattedValue = computed(() => {
  const num = Number(props.value)
  if (isNaN(num)) return props.value

  const formatted = num.toFixed(props.precision)
  return props.unit ? `${formatted}${props.unit}` : formatted
})

const changeText = computed(() => {
  if (props.change === null) return ''

  const sign = props.change > 0 ? '+' : ''
  return `${sign}${props.change.toFixed(props.precision)}%`
})
</script>

<style scoped>
.value-cell {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  font-family: var(--el-font-family-mono, monospace);
}

.trend-icon {
  font-size: 14px;
}

.value-text {
  font-size: 14px;
}

.change-text {
  font-size: 12px;
  opacity: 0.8;
}

/* Size variants */
.size-large .value-text {
  font-size: 20px;
}

.size-large .change-text {
  font-size: 14px;
}

.size-small .value-text {
  font-size: 12px;
}

.size-small .change-text {
  font-size: 11px;
}

/* Trend colors applied via style binding */
</style>
```

#### 3.1.2 Props 规范

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `value` | Number/String | **必填** | 显示的数值 |
| `change` | Number | `null` | 涨跌幅百分比 (用于确定颜色) |
| `precision` | Number | `2` | 小数精度 |
| `unit` | String | `''` | 单位 (如 '%', '元') |
| `showIcon` | Boolean | `false` | 显示涨跌图标 |
| `showChange` | Boolean | `false` | 显示涨跌幅文本 |
| `size` | String | `'default'` | 尺寸: `large` `default` `small` |

#### 3.1.3 使用示例

```vue
<template>
  <!-- 基本用法 -->
  < :value="12.34" :change="2.5" />

  <!-- 带图标和涨跌幅 -->
  <
    :value="stockPrice"
    :change="priceChange"
    show-icon
    show-change
    size="large"
  />

  <!-- 带单位 -->
  < :value="turnoverRate" :change="1.2" unit="%" />
</template>

<script setup>
import { ref } from 'vue'
import  from '@/components/business//.vue'

const stockPrice = ref(12.34)
const priceChange = ref(2.5)
const turnoverRate = ref(3.45)
</script>
```

---

### 3.2 StockCard 股票卡片组件

#### 3.2.1 组件定义

```vue
<!-- src/components/business/StockCard/StockCard.vue -->
<template>
  <el-card
    :class="['stock-card', { 'is-selected': selected }]"
    :body-style="{ padding: '16px' }"
    shadow="hover"
    @click="handleClick"
  >
    <div class="stock-header">
      <div class="stock-info">
        <span class="stock-code">{{ stock.code }}</span>
        <span class="stock-name">{{ stock.name }}</span>
      </div>
      <div class="stock-tags">
        <el-tag
          v-for="tag in stock.tags"
          :key="tag"
          size="small"
          type="info"
        >
          {{ tag }}
        </el-tag>
      </div>
    </div>

    <div class="stock-price">
      <
        :value="stock.price"
        :change="stock.changePercent"
        show-icon
        show-change
        size="large"
      />
    </div>

    <div class="stock-metrics">
      <div class="metric-item">
        <span class="metric-label">涨跌额</span>
        < :value="stock.changeAmount" :change="stock.changePercent" />
      </div>
      <div class="metric-item">
        <span class="metric-label">成交量</span>
        <span class="metric-value">{{ formatVolume(stock.volume) }}</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">换手率</span>
        <span class="metric-value">{{ stock.turnoverRate }}%</span>
      </div>
    </div>

    <div v-if="showActions" class="stock-actions">
      <el-button size="small" @click.stop="handleAddToWatchlist">
        <el-icon><Star /></el-icon>
        自选
      </el-button>
      <el-button size="small" type="primary" @click.stop="handleViewDetails">
        详情
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { Star } from '@element-plus/icons-vue'
import  from '@/components/business//.vue'

const props = defineProps({
  stock: {
    type: Object,
    required: true,
    validator: (value) => {
      return value.code && value.name && value.price !== undefined
    }
  },
  selected: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'add-to-watchlist', 'view-details'])

const formatVolume = (volume) => {
  if (volume >= 100000000) return `${(volume / 100000000).toFixed(2)}亿`
  if (volume >= 10000) return `${(volume / 10000).toFixed(2)}万`
  return volume.toString()
}

const handleClick = () => {
  emit('click', props.stock)
}

const handleAddToWatchlist = () => {
  emit('add-to-watchlist', props.stock)
}

const handleViewDetails = () => {
  emit('view-details', props.stock)
}
</script>

<style scoped>
.stock-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stock-card.is-selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-code {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stock-name {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.stock-tags {
  display: flex;
  gap: 4px;
}

.stock-price {
  margin-bottom: 12px;
}

.stock-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-light);
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.metric-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.stock-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-light);
}
</style>
```

#### 3.2.2 Props 规范

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `stock` | Object | **必填** | 股票数据对象 (必须包含 code, name, price) |
| `selected` | Boolean | `false` | 是否选中状态 |
| `showActions` | Boolean | `true` | 是否显示操作按钮 |

**stock 对象结构**:
```typescript
interface Stock {
  code: string           // 股票代码
  name: string           // 股票名称
  price: number          // 当前价格
  changeAmount: number   // 涨跌额
  changePercent: number  // 涨跌幅百分比
  volume: number         // 成交量
  turnoverRate: number   // 换手率
  tags?: string[]        // 标签数组
}
```

#### 3.2.3 Events 规范

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `click` | `(stock: Object)` | 卡片点击事件 |
| `add-to-watchlist` | `(stock: Object)` | 添加到自选 |
| `view-details` | `(stock: Object)` | 查看详情 |

#### 3.2.4 使用示例

```vue
<template>
  <div class="stock-list">
    <StockCard
      v-for="stock in stocks"
      :key="stock.code"
      :stock="stock"
      :selected="selectedCode === stock.code"
      @click="handleStockClick"
      @add-to-watchlist="handleAddToWatchlist"
      @view-details="handleViewDetails"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockCard from '@/components/business/StockCard/StockCard.vue'

const selectedCode = ref(null)

const stocks = ref([
  {
    code: '000001',
    name: '平安银行',
    price: 12.34,
    changeAmount: 0.28,
    changePercent: 2.32,
    volume: 123456789,
    turnoverRate: 1.23,
    tags: ['银行', '蓝筹']
  },
  {
    code: '000002',
    name: '万科A',
    price: 8.90,
    changeAmount: -0.15,
    changePercent: -1.66,
    volume: 234567890,
    turnoverRate: 2.45,
    tags: ['地产']
  }
])

const handleStockClick = (stock) => {
  selectedCode.value = stock.code
}

const handleAddToWatchlist = (stock) => {
  console.log('Add to watchlist:', stock.code)
}

const handleViewDetails = (stock) => {
  console.log('View details:', stock.code)
}
</script>

<style scoped>
.stock-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
</style>
```

---

## 4. 图表组件

### 4.1 KLineChart K线图组件

#### 4.1.1 组件定义

```vue
<!-- src/components/charts/KLineChart/KLineChart.vue -->
<template>
  <div ref="chartRef" :style="{ width, height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { init, dispose } from 'klinecharts'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '500px'
  },
  theme: {
    type: String,
    default: 'light',
    validator: (value) => ['light', 'dark'].includes(value)
  },
  mainIndicators: {
    type: Array,
    default: () => ['MA']
  },
  subIndicators: {
    type: Array,
    default: () => ['VOL']
  }
})

const emit = defineEmits(['cross-hair', 'zoom', 'scroll'])

const chartRef = ref(null)
let chartInstance = null

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chartInstance) {
    dispose(chartRef.value)
    chartInstance = null
  }
})

watch(() => props.data, (newData) => {
  if (chartInstance && newData) {
    chartInstance.applyNewData(newData)
  }
})

watch(() => props.theme, (newTheme) => {
  if (chartInstance) {
    chartInstance.setStyles(getThemeStyles(newTheme))
  }
})

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = init(chartRef.value)

  // 设置主题
  chartInstance.setStyles(getThemeStyles(props.theme))

  // 加载数据
  chartInstance.applyNewData(props.data)

  // 创建主指标
  props.mainIndicators.forEach(indicator => {
    chartInstance.createIndicator(indicator, false, { id: 'candle_pane' })
  })

  // 创建副指标
  props.subIndicators.forEach(indicator => {
    chartInstance.createIndicator(indicator, false)
  })

  // 订阅事件
  chartInstance.subscribeAction('onCrosshairChange', (data) => {
    emit('cross-hair', data)
  })

  chartInstance.subscribeAction('onZoomChange', (data) => {
    emit('zoom', data)
  })

  chartInstance.subscribeAction('onScroll', () => {
    emit('scroll')
  })
}

const getThemeStyles = (theme) => {
  if (theme === 'dark') {
    return {
      grid: {
        horizontal: { color: '#393939' },
        vertical: { color: '#393939' }
      },
      candle: {
        type: 'candle_solid',
        priceMark: {
          high: { color: '#D9D9D9' },
          low: { color: '#D9D9D9' }
        },
        tooltip: {
          text: { color: '#D9D9D9' }
        }
      },
      indicator: {
        tooltip: {
          text: { color: '#D9D9D9' }
        }
      },
      xAxis: {
        axisLine: { color: '#393939' },
        tickText: { color: '#D9D9D9' }
      },
      yAxis: {
        axisLine: { color: '#393939' },
        tickText: { color: '#D9D9D9' }
      },
      crosshair: {
        horizontal: {
          line: { color: '#888888' },
          text: { backgroundColor: '#505050', color: '#D9D9D9' }
        },
        vertical: {
          line: { color: '#888888' },
          text: { backgroundColor: '#505050', color: '#D9D9D9' }
        }
      }
    }
  }

  // Light theme (default)
  return {
    grid: {
      horizontal: { color: '#E4E7ED' },
      vertical: { color: '#E4E7ED' }
    },
    candle: {
      type: 'candle_solid',
      priceMark: {
        high: { color: '#606266' },
        low: { color: '#606266' }
      },
      tooltip: {
        text: { color: '#606266' }
      }
    },
    indicator: {
      tooltip: {
        text: { color: '#606266' }
      }
    },
    xAxis: {
      axisLine: { color: '#DCDFE6' },
      tickText: { color: '#606266' }
    },
    yAxis: {
      axisLine: { color: '#DCDFE6' },
      tickText: { color: '#606266' }
    },
    crosshair: {
      horizontal: {
        line: { color: '#909399' },
        text: { backgroundColor: '#606266', color: '#FFFFFF' }
      },
      vertical: {
        line: { color: '#909399' },
        text: { backgroundColor: '#606266', color: '#FFFFFF' }
      }
    }
  }
}

// 暴露方法供父组件调用
defineExpose({
  getChartInstance: () => chartInstance
})
</script>
```

#### 4.1.2 Props 规范

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | Array | **必填** | K线数据数组 |
| `width` | String | `'100%'` | 图表宽度 |
| `height` | String | `'500px'` | 图表高度 |
| `theme` | String | `'light'` | 主题: `light` `dark` |
| `mainIndicators` | Array | `['MA']` | 主图指标数组 |
| `subIndicators` | Array | `['VOL']` | 副图指标数组 |

**data 数组元素结构**:
```typescript
interface KLineData {
  timestamp: number  // 时间戳 (毫秒)
  open: number       // 开盘价
  high: number       // 最高价
  low: number        // 最低价
  close: number      // 收盘价
  volume: number     // 成交量
}
```

#### 4.1.3 Events 规范

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `cross-hair` | `(data: Object)` | 十字光标移动事件 |
| `zoom` | `(data: Object)` | 缩放事件 |
| `scroll` | `()` | 滚动事件 |

#### 4.1.4 使用示例

```vue
<template>
  <KLineChart
    :data="klineData"
    height="600px"
    theme="light"
    :main-indicators="['MA', 'BOLL']"
    :sub-indicators="['VOL', 'MACD']"
    @cross-hair="handleCrosshair"
  />
</template>

<script setup>
import { ref } from 'vue'
import KLineChart from '@/components/charts/KLineChart/KLineChart.vue'

const klineData = ref([
  {
    timestamp: 1609459200000,
    open: 12.00,
    high: 12.50,
    low: 11.80,
    close: 12.30,
    volume: 1234567
  },
  // ...more data
])

const handleCrosshair = (data) => {
  console.log('Crosshair data:', data)
}
</script>
```

---

## 5. 复合组件

### 5.1 StockSearchBar 股票搜索栏组件

#### 5.1.1 组件定义

```vue
<!-- src/components/composite/StockSearchBar/StockSearchBar.vue -->
<template>
  <div class="stock-search-bar">
    <el-autocomplete
      v-model="searchQuery"
      :fetch-suggestions="handleSearch"
      :trigger-on-focus="false"
      placeholder="输入股票代码或名称"
      clearable
      :prefix-icon="Search"
      @select="handleSelect"
    >
      <template #default="{ item }">
        <div class="search-item">
          <div class="search-item-header">
            <span class="stock-code">{{ item.code }}</span>
            <span class="stock-name">{{ item.name }}</span>
          </div>
          <div class="search-item-info">
            <
              :value="item.price"
              :change="item.changePercent"
              size="small"
            />
          </div>
        </div>
      </template>
    </el-autocomplete>

    <el-button
      type="primary"
      :icon="Search"
      @click="handleSearchClick"
    >
      搜索
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import  from '@/components/business//.vue'

const props = defineProps({
  searchFn: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['select', 'search'])

const searchQuery = ref('')

const handleSearch = async (queryString, callback) => {
  if (!queryString) {
    callback([])
    return
  }

  try {
    const results = await props.searchFn(queryString)
    callback(results)
  } catch (error) {
    console.error('Search error:', error)
    callback([])
  }
}

const handleSelect = (item) => {
  emit('select', item)
}

const handleSearchClick = () => {
  emit('search', searchQuery.value)
}
</script>

<style scoped>
.stock-search-bar {
  display: flex;
  gap: 8px;
  align-items: center;
}

.el-autocomplete {
  flex: 1;
}

.search-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.search-item-header {
  display: flex;
  gap: 8px;
  align-items: center;
}

.stock-code {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stock-name {
  color: var(--el-text-color-regular);
}

.search-item-info {
  margin-left: auto;
}
</style>
```

#### 5.1.2 Props 规范

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `searchFn` | Function | **必填** | 搜索函数,接收查询字符串,返回 Promise<Array> |

**searchFn 返回值结构**:
```typescript
interface SearchResult {
  code: string           // 股票代码
  name: string           // 股票名称
  price: number          // 当前价格
  changePercent: number  // 涨跌幅百分比
}
```

#### 5.1.3 Events 规范

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `select` | `(item: Object)` | 选择搜索结果 |
| `search` | `(query: String)` | 点击搜索按钮 |

#### 5.1.4 使用示例

```vue
<template>
  <StockSearchBar
    :search-fn="searchStocks"
    @select="handleStockSelect"
    @search="handleSearch"
  />
</template>

<script setup>
import { ElMessage } from 'element-plus'
import StockSearchBar from '@/components/composite/StockSearchBar/StockSearchBar.vue'
import { searchStocksAPI } from '@/api/stock'

const searchStocks = async (query) => {
  const response = await searchStocksAPI(query)
  return response.data
}

const handleStockSelect = (stock) => {
  console.log('Selected stock:', stock)
  // Navigate to stock detail page
}

const handleSearch = (query) => {
  if (!query) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  console.log('Search query:', query)
}
</script>
```

---

## 6. 组件开发规范

### 6.1 组件文件结构

```
ComponentName/
├── ComponentName.vue       # 组件主文件
├── index.ts                # 导出文件
├── types.ts                # TypeScript 类型定义
├── constants.ts            # 常量定义
├── hooks/                  # 组合式函数
│   └── useComponentName.ts
├── utils/                  # 工具函数
│   └── helpers.ts
└── __tests__/              # 测试文件
    └── ComponentName.spec.ts
```

### 6.2 Props 设计原则

1. **必填 vs 可选**: 使用 `required: true` 明确必填属性
2. **类型验证**: 使用 `type` 和 `validator` 确保类型正确
3. **默认值**: 可选属性提供合理默认值
4. **命名规范**: 使用 camelCase,避免缩写

```vue
<script setup>
const props = defineProps({
  // ✅ Good: 明确类型和默认值
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['large', 'default', 'small'].includes(value)
  },

  // ❌ Bad: 缺少类型和验证
  size: {
    default: 'default'
  }
})
</script>
```

### 6.3 Events 设计原则

1. **命名规范**: 使用 kebab-case
2. **参数明确**: 单个参数传递对象,多个参数分开传递
3. **阻止冒泡**: 内部事件使用 `.stop` 修饰符

```vue
<script setup>
const emit = defineEmits([
  'update:modelValue',  // v-model 更新
  'change',             // 值变化
  'selection-change'    // 选择变化
])

// ✅ Good: 明确的事件触发
const handleChange = (value) => {
  emit('change', value)
}

// ❌ Bad: 不清晰的参数
const handleChange = (...args) => {
  emit('change', ...args)
}
</script>
```

### 6.4 插槽设计原则

1. **默认插槽**: 用于主要内容
2. **具名插槽**: 用于特定位置内容
3. **作用域插槽**: 传递数据给父组件

```vue
<template>
  <div class="component">
    <!-- 默认插槽 -->
    <slot></slot>

    <!-- 具名插槽 -->
    <slot name="header"></slot>
    <slot name="footer"></slot>

    <!-- 作用域插槽 -->
    <slot name="item" :item="item" :index="index"></slot>
  </div>
</template>
```

### 6.5 样式规范

1. **使用 scoped**: 避免样式污染
2. **BEM 命名**: 使用 Block-Element-Modifier
3. **CSS 变量**: 引用设计 Token

```vue
<style scoped>
/* ✅ Good: BEM 命名 + CSS 变量 */
.stock-card {
  padding: var(--spacing-md);
  border-radius: var(--border-radius-default);
}

.stock-card__header {
  margin-bottom: var(--spacing-sm);
}

.stock-card--selected {
  border-color: var(--color-primary);
}

/* ❌ Bad: 嵌套过深 + 硬编码值 */
.stock-card {
  padding: 12px;
}

.stock-card .header .title {
  font-size: 16px;
}
</style>
```

---

## 7. 组件测试规范

### 7.1 单元测试

使用 Vitest + Vue Test Utils:

```typescript
// ComponentName.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import  from '../.vue'

describe('', () => {
  it('renders value correctly', () => {
    const wrapper = mount(, {
      props: {
        value: 12.34,
        change: 2.5
      }
    })

    expect(wrapper.text()).toContain('12.34')
  })

  it('applies correct color based on trend', () => {
    const wrapper = mount(, {
      props: {
        value: 12.34,
        change: 2.5  // Positive change
      }
    })

    expect(wrapper.find('.value-cell').classes()).toContain('trend-up')
  })

  it('emits click event', async () => {
    const wrapper = mount(, {
      props: {
        value: 12.34,
        change: 2.5
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })
})
```

### 7.2 组件快照测试

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StockCard from '../StockCard.vue'

describe('StockCard snapshot', () => {
  it('matches snapshot', () => {
    const wrapper = mount(StockCard, {
      props: {
        stock: {
          code: '000001',
          name: '平安银行',
          price: 12.34,
          changeAmount: 0.28,
          changePercent: 2.32,
          volume: 123456789,
          turnoverRate: 1.23
        }
      }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })
})
```

### 7.3 集成测试

测试组件在实际场景中的交互:

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StockSearchBar from '../StockSearchBar.vue'

describe('StockSearchBar integration', () => {
  it('performs search and selects result', async () => {
    const mockSearchFn = vi.fn().mockResolvedValue([
      {
        code: '000001',
        name: '平安银行',
        price: 12.34,
        changePercent: 2.5
      }
    ])

    const wrapper = mount(StockSearchBar, {
      props: {
        searchFn: mockSearchFn
      }
    })

    // Simulate search
    const input = wrapper.find('input')
    await input.setValue('平安')
    await input.trigger('input')

    // Wait for search results
    await wrapper.vm.$nextTick()

    // Verify search function was called
    expect(mockSearchFn).toHaveBeenCalledWith('平安')

    // Select first result
    const firstResult = wrapper.find('.search-item')
    await firstResult.trigger('click')

    // Verify select event
    expect(wrapper.emitted('select')).toBeTruthy()
  })
})
```

---

## 总结

本规范文档定义了 MyStocks 项目的组件库标准,包括:

1. **组件分类**: 基础、业务、图表、复合四大类
2. **组件实现**: 详细的 Props、Events、Slots 定义
3. **开发规范**: 文件结构、命名、样式、测试标准
4. **使用示例**: 每个组件的实际代码示例

**下一步行动**:
- 基于此规范在 Figma 中创建对应组件
- 应用 design-tokens.json 确保一致性
- 导出 .fig 文件并导入 Pixso

参见 `PIXSO_IMPORT_GUIDE.md` 了解详细导入流程。
