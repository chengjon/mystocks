# Phase 3: Enhanced K-line Charts - Quick Reference

**Version**: 1.0
**Date**: 2025-12-27
**Status**: 95% Complete (14/15 tasks)

---

## 📦 Component Files

### Main Components

| File | Lines | Purpose |
|------|-------|---------|
| `src/components/Market/ProKLineChart.vue` | 753 | Professional K-line chart component |
| `src/components/Market/IndicatorSelector.vue` | 330 | Indicator selection UI component |

### Utility Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/utils/indicators.ts` | 249 | Basic technical indicators (10 indicators) |
| `src/utils/indicators-extended.ts` | 500+ | Extended indicators (20+ indicators) |
| `src/utils/atrading.ts` | 176 | A股 market features |
| `src/utils/data-sampling.ts` | 430 | Data downsampling utilities |
| `src/utils/lazy-loading.ts` | 530 | Lazy loading for historical data |

---

## 🚀 Quick Start

### 1. Basic Usage

```vue
<template>
  <ProKLineChart
    symbol="000001.SZ"
    :height="600"
    :show-price-limits="true"
    :forward-adjusted="false"
    board-type="main"
    @data-loaded="handleDataLoaded"
  />
</template>

<script setup lang="ts">
import ProKLineChart from '@/components/Market/ProKLineChart.vue'

const handleDataLoaded = (data: any[]) => {
  console.log(`Loaded ${data.length} candles`)
}
</script>
```

### 2. Custom Periods and Indicators

```vue
<template>
  <ProKLineChart
    symbol="000001.SZ"
    :periods="customPeriods"
    :indicators="customIndicators"
    :height="600"
  />
</template>

<script setup lang="ts">
import ProKLineChart from '@/components/Market/ProKLineChart.vue'

const customPeriods = [
  { label: '5分', value: '5m' },
  { label: '日K', value: '1d' },
  { label: '周K', value: '1w' }
]

const customIndicators = [
  { label: 'MA5', value: 'MA5' },
  { label: 'MA20', value: 'MA20' },
  { label: 'MACD', value: 'MACD' }
]
</script>
```

### 3. With Indicator Selector

```vue
<template>
  <div class="chart-container">
    <IndicatorSelector
      v-model="selectedIndicators"
      @change="handleIndicatorChange"
    />
    <ProKLineChart
      symbol="000001.SZ"
      :indicators="selectedIndicators"
      :height="600"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ProKLineChart from '@/components/Market/ProKLineChart.vue'
import IndicatorSelector from '@/components/Market/IndicatorSelector.vue'

const selectedIndicators = ref<string[]>(['MA5', 'MA20', 'VOL'])

const handleIndicatorChange = (indicators: string[]) => {
  console.log('Selected indicators:', indicators)
}
</script>
```

---

## 📊 Technical Indicators

### Basic Indicators (indicators.ts)

```typescript
import {
  calculateMA,
  calculateEMA,
  calculateMACD,
  calculateRSI,
  calculateKDJ,
  calculateBOLL,
  calculateATR
} from '@/utils/indicators'

// Moving Average
const ma5 = calculateMA(klineData, 5)
const ema12 = calculateEMA(klineData, 12)

// MACD
const macd = calculateMACD(klineData)
// Returns: { macd: number[], signal: number[], histogram: number[] }

// RSI
const rsi = calculateRSI(klineData, 14)

// KDJ
const kdj = calculateKDJ(klineData, 9, 3, 3)
// Returns: { k: number[], d: number[], j: number[] }
```

### Extended Indicators (indicators-extended.ts)

```typescript
import {
  calculateADX,
  calculateCCI,
  calculateMFI,
  calculateOBV,
  calculateWilliamsR,
  calculateStochRSI
} from '@/utils/indicators-extended'

// ADX (Average Directional Index)
const adx = calculateADX(klineData, 14)

// CCI (Commodity Channel Index)
const cci = calculateCCI(klineData, 20)

// MFI (Money Flow Index)
const mfi = calculateMFI(klineData, 14)

// OBV (On Balance Volume)
const obv = calculateOBV(klineData)

// Williams %R
const williamsR = calculateWilliamsR(klineData, 14)
```

---

## 🇨🇳 A股 Market Features

### Price Limit Detection

```typescript
import {
  detectPriceLimit,
  getPriceLimitColor,
  PriceLimitStatus
} from '@/utils/atrading'

// Detect price limit
const status = detectPriceLimit(
  currentPrice,    // Current close price
  prevClose,       // Previous close price
  'main'           // Board type: 'main' | 'chiNext' | 'star' | 'bje'
)

// Get color
const color = getPriceLimitColor(status)
// Returns: '#EF5350' (limit up) or '#26A69A' (limit down)

// Check status
if (status === PriceLimitStatus.LIMIT_UP) {
  console.log('涨停!')
} else if (status === PriceLimitStatus.LIMIT_DOWN) {
  console.log('跌停!')
}
```

### Board Types

| Board | Limit | Type |
|-------|-------|------|
| main | 10% | 主板 |
| chiNext | 20% | 创业板 |
| star | 20% | 科创板 |
| bje | 30% | 北交所 |

### Adjustment Factor

```typescript
import {
  needsAdjustment,
  calculateAdjustmentFactor
} from '@/utils/atrading'

// Check if adjustment is needed
const needsAdj = needsAdjustment('1d')  // true
const needsAdj = needsAdjustment('5m')  // false

// Calculate adjustment factor
const factor = calculateAdjustmentFactor(10.5, 10.0)
// Returns: 0.95238
```

### Lot Size and Settlement

```typescript
import {
  getLotShares,
  formatLotShares,
  calculateTPlus1SettlementDate,
  formatSettlementDate
} from '@/utils/atrading'

// Lot size (100 shares per lot)
const lots = getLotShares(500)  // 5 lots
const formatted = formatLotShares(500)  // "5手"

// T+1 settlement
const tradeDate = new Date('2025-12-27')
const settlementDate = calculateTPlus1SettlementDate(tradeDate)
const formatted = formatSettlementDate(tradeDate)  // "2025-12-28"
```

---

## ⚡ Performance Optimization

### Data Downsampling

```typescript
import {
  downsampleData,
  autoDownsample,
  getRecommendedMaxPoints,
  DownsamplingMethod
} from '@/utils/data-sampling'

// Manual downsampling
const downsampled = downsampleData(fullData, {
  maxPoints: 1000,
  method: DownsamplingMethod.LTTB,  // Best for visualization
  keepLast: true
})

// Auto downsampling (recommended)
const displayData = autoDownsample(fullData, true)

// Get recommended max points
const maxPoints = getRecommendedMaxPoints(800, 0.5)  // 400 points
```

### Downsampling Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| NONE | No downsampling | Small datasets |
| SIMPLE | Every Nth point | Fast preview |
| EXTREME | High/Low points | Preserving extremes |
| OHLC | Aggregated OHLC | Candlestick charts |
| LTTB | Largest triangles | Best visualization |

### Lazy Loading

```typescript
import {
  createLazyLoader,
  type LoadRequestConfig
} from '@/utils/lazy-loading'

// Create loader
const loader = createLazyLoader(
  // Data loader function
  async (config: LoadRequestConfig) => {
    const response = await marketApi.getKLineData({
      symbol: config.symbol,
      interval: config.period,
      limit: config.limit || 1000,
      adjust: config.adjust || 'none'
    })
    return response.data
  },
  // Config (optional)
  {
    initialLoadSize: 1000,
    chunkSize: 500,
    maxCacheSize: 10000,
    enableDownsampling: true,
    preloadChunks: 2
  }
)

// Initialize
const initialData = await loader.initialize('000001.SZ', '1d', 'none')

// Load more
const moreData = await loader.loadMore('none')

// Get display data (downsampled)
const displayData = loader.getDisplayData(1000)

// Get load progress
const progress = loader.getLoadProgress()
// Returns: { loaded: 1500, total: 2000, percentage: 75 }
```

---

## 🎨 Customization

### Chart Styles

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { init } from 'klinecharts'

const chartContainer = ref<HTMLElement>()

onMounted(() => {
  const chart = init(chartContainer.value!)

  // Custom A股 colors
  chart.setStyles({
    candle: {
      bar: {
        upColor: '#EF5350',    // Red (up)
        downColor: '#26A69A',  // Green (down)
        noChangeColor: '#888888'
      }
    }
  })
})
</script>
```

### Indicator Colors

```typescript
// Apply MA with custom color
const applyMAIndicator = (period: number, color: string) => {
  chartInstance.value?.createIndicator('MA', true, {
    id: `MA${period}`,
    calcParams: [period]
  })

  // Note: klinecharts 9.x may require additional API calls
  // to set custom colors. Check documentation for details.
}
```

---

## 📡 Events

### ProKLineChart Events

| Event | Payload | Description |
|-------|---------|-------------|
| @period-change | period: string | Period changed |
| @indicator-change | indicators: string[] | Indicators changed |
| @data-loaded | data: any[] | Data loaded successfully |
| @error | error: Error | Error occurred |

### Example

```vue
<template>
  <ProKLineChart
    symbol="000001.SZ"
    @period-change="handlePeriodChange"
    @indicator-change="handleIndicatorChange"
    @data-loaded="handleDataLoaded"
    @error="handleError"
  />
</template>

<script setup lang="ts">
const handlePeriodChange = (period: string) => {
  console.log('Period changed to:', period)
}

const handleIndicatorChange = (indicators: string[]) => {
  console.log('Indicators changed:', indicators)
}

const handleDataLoaded = (data: any[]) => {
  console.log('Loaded:', data.length, 'candles')
}

const handleError = (error: Error) => {
  console.error('Chart error:', error)
}
</script>
```

---

## 🔧 API Reference

### ProKLineChart Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| symbol | string | required | Stock code |
| periods | TimePeriod[] | 8 periods | Available periods |
| defaultPeriod | string | '1d' | Default period |
| indicators | Indicator[] | 8 indicators | Available indicators |
| height | string \| number | '600px' | Chart height |
| showPriceLimits | boolean | true | Show price limit markers |
| forwardAdjusted | boolean | false | Use forward adjustment |
| boardType | 'main' \| 'chiNext' \| 'star' \| 'bje' | 'main' | Board type for price limits |

### IndicatorSelector Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| modelValue | string[] | [] | Selected indicators |
| showSelectedTags | boolean | true | Show selected tags |

---

## 🐛 Troubleshooting

### Common Issues

1. **Chart not rendering**
   - Check if symbol prop is provided
   - Check if container has height
   - Check console for errors

2. **Indicators not showing**
   - Check if data is loaded first
   - Check indicator names match exactly
   - Check if indicators are supported

3. **Price limits not working**
   - Check if boardType is correct
   - Check if showPriceLimits is true
   - Check if data has previous close price

4. **Performance issues**
   - Enable downsampling for large datasets
   - Use lazy loading for historical data
   - Reduce maxPoints for display data

---

## 📚 Related Documentation

- [Complete Completion Report](./PHASE3_COMPLETION_REPORT.md)
- [Task List](../../openspec/changes/frontend-optimization-six-phase/tasks.md)
- [Project Guide](../../CLAUDE.md)

---

## 🎯 Next Steps

1. **Integrate into StockDetail page** (T3.14)
   - Replace existing chart component
   - Test with real stock data
   - Verify all features work

2. **Complete remaining indicators** (Phase 4)
   - Implement 70+ indicators total
   - Add indicator customization UI
   - Performance testing

3. **Create Git tag** (T3.15)
   ```bash
   git tag -a phase3-kline-charts -m "增强K线图表系统完成"
   git push origin phase3-kline-charts
   ```

---

**Last Updated**: 2025-12-27
**Author**: Claude Code (Frontend Specialist)
**Project**: MyStocks Frontend Optimization - Phase 3
