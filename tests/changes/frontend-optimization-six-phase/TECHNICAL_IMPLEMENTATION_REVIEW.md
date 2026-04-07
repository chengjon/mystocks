# Technical Implementation Review: Frontend Optimization Six-Phase Proposal

> **历史分析说明**:
> 本文件是某次针对测试覆盖、缺陷、基线、诊断结果或方案可行性形成的历史分析记录，用于保留当时的判断依据与观察结果。
> 文中的结论、统计和问题判断均受生成时间、样本范围与当时仓库状态影响；如需判断当前状态，必须重新核对现行测试实现与最新验证结果。


**Reviewer**: Claude Code (Frontend Development Specialist)
**Date**: 2025-12-26
**Project**: MyStocks A股 Trading Platform (Chinese A-Share Market)
**Status**: ✅ CRITICAL BUGS IDENTIFIED - MUST FIX BEFORE APPROVAL

---

## Executive Summary

**CRITICAL BUG FOUND**: The proposal contains **INCORRECT A股 COLOR CONVENTIONS** that would confuse all Chinese users.

**Overall Technical Quality**: ⚠️ **GOOD WITH CRITICAL BUGS** (7/10)

**Approval Status**: ❌ **REQUIRES CRITICAL BUG FIXES BEFORE APPROVAL**

### Critical Issues Found

1. ❌ **CRITICAL**: Color system has A股 colors BACKWARDS (proposal says green=up, but A股 uses RED=UP)
2. ⚠️ **HIGH**: Missing TypeScript strict mode configuration details
3. ⚠️ **HIGH**: Insufficient mobile responsive design patterns
4. ⚠️ **MEDIUM**: No error state designs for complex components
5. ⚠️ **MEDIUM**: Missing klinecharts performance optimization details

---

## 1. CRITICAL BUG: A股 Color Convention Error

### The Bug

**Current proposal** (design.md lines 120-122):
```scss
// A股 Market Colors (Green=Up, Red=Down)
--color-up: #00E676;          // Up - bright green
--color-down: #FF5252;        // Down - bright red
```

**THIS IS WRONG FOR A股 (Chinese A-Share Market)** ❌

### Correct A股 Color Convention

**Chinese A-Share Market Convention**:
- 🔴 **RED = UP (涨)** - Price increase, gain, profit
- 🟢 **GREEN = DOWN (跌)** - Price decrease, loss, decline

**This is the OPPOSITE of international markets!**

### Why This Matters

In China:
- "大红大紫" (big red big purple) means "very prosperous"
- Red symbolizes good fortune, celebration, success
- Green can symbolize infidelity, negative meanings
- Every Chinese trader expects: **RED = 涨, GREEN = 跌**

### Corrected Color System

```scss
// ✅ CORRECT: A股 Market Colors (RED=UP, GREEN=DOWN)
:root {
  // A股 conventions
  --color-up: #FF5252;          // Up - bright RED (上涨) 涨
  --color-down: #00E676;        // Down - bright GREEN (下跌) 跌
  --color-flat: #B0B3B8;        // Flat - gray (平盘) 平

  // Note: Use different red/green shades from semantic colors
  // to avoid confusion between market trends and UI states
}
```

### Semantic Color Separation

```scss
// ✅ GOOD: Separate market colors from UI state colors
:root {
  // Market colors (A股: RED=UP, GREEN=DOWN)
  --color-market-up: #FF5252;      // 涨 (RED)
  --color-market-down: #00E676;    // 跌 (GREEN)
  --color-market-flat: #B0B3B8;    // 平 (GRAY)

  // Semantic UI colors (international standard)
  --color-success: #00C853;        // Success state (green)
  --color-danger: #FF1744;         // Danger state (red)
  --color-warning: #FFAB00;        // Warning state (amber)
  --color-info: #00B0FF;           // Info state (blue)
}
```

### Implementation Example

```vue
<template>
  <!-- ✅ CORRECT: Use market colors for price changes -->
  <div class="price-display">
    <span class="price" :class="priceClass">
      {{ currentPrice }}
    </span>
    <span class="change" :class="changeClass">
      {{ changePercent }}
    </span>
  </div>

  <!-- ✅ CORRECT: Use semantic colors for UI states -->
  <el-alert type="success">操作成功</el-alert>
  <el-alert type="danger">删除失败</el-alert>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps<{
  currentPrice: number
  previousPrice: number
}>()

// ✅ CORRECT: A股 color logic (RED=UP, GREEN=DOWN)
const priceClass = computed(() => {
  if (props.currentPrice > props.previousPrice) return 'text-market-up'    // RED
  if (props.currentPrice < props.previousPrice) return 'text-market-down'  // GREEN
  return 'text-market-flat'  // GRAY
})
</script>

<style scoped>
.text-market-up {
  color: var(--color-market-up);    /* RED for 涨 */
}

.text-market-down {
  color: var(--color-market-down);  /* GREEN for 跌 */
}

.text-market-flat {
  color: var(--color-market-flat);  /* GRAY for 平 */
}
</style>
```

### Must-Fix Locations

Update all these files with correct A股 colors:

1. **design.md** (line 120-122) - Color palette section
2. **proposal.md** - Any color references
3. **tasks.md** (Task T1.1) - Theme system setup
4. **All future CSS/SCSS files** - Use correct conventions
5. **All chart components** - K-line colors
6. **All data display components** - Price, change percent

### A股-Specific Color Guidelines

| Context | Color | Meaning |
|---------|-------|---------|
| **Price Increase** | 🔴 RED (#FF5252) | 涨 (UP) |
| **Price Decrease** | 🟢 GREEN (#00E676) | 跌 (DOWN) |
| **Unchanged** | ⚪ GRAY (#B0B3B8) | 平 (FLAT) |
| **Limit Up (涨停)** | 🔴🔴 RED + "涨停" label | +10% or +20% |
| **Limit Down (跌停)** | 🟢🟢 GREEN + "跌停" label | -10% or -20% |
| **Success Message** | ✅ GREEN (#00C853) | Operation successful |
| **Error Message** | ❌ RED (#FF1744) | Operation failed |

---

## 2. A股-Specific Technical Requirements

### 2.1 涨跌停 (Price Limits) Display

**A股 Trading Rules**:
- Main board (主板): ±10% daily limit
- ChiNext (创业板): ±20% daily limit
- STAR Market (科创板): ±20% daily limit
- ST stocks: ±5% daily limit

**Implementation**:

```typescript
// src/utils/atrading-rules.ts
export enum BoardType {
  MAIN = 'MAIN',           // 主板: ±10%
  CHI_NEXT = 'CHI_NEXT',   // 创业板: ±20%
  STAR = 'STAR',           // 科创板: ±20%
  ST = 'ST'                // ST股: ±5%
}

export interface PriceLimitResult {
  isLimitUp: boolean
  isLimitDown: boolean
  limitPrice: number
  limitPercent: number
}

export function checkPriceLimit(
  currentPrice: number,
  prevClose: number,
  boardType: BoardType
): PriceLimitResult {
  const limits = {
    [BoardType.MAIN]: 0.10,
    [BoardType.CHI_NEXT]: 0.20,
    [BoardType.STAR]: 0.20,
    [BoardType.ST]: 0.05
  }

  const limitPercent = limits[boardType]
  const limitUpPrice = prevClose * (1 + limitPercent)
  const limitDownPrice = prevClose * (1 - limitPercent)
  const changePercent = (currentPrice - prevClose) / prevClose

  return {
    isLimitUp: currentPrice >= limitUpPrice * 0.995, // Allow rounding
    isLimitDown: currentPrice <= limitDownPrice * 1.005,
    limitPrice: currentPrice >= limitUpPrice ? limitUpPrice : limitDownPrice,
    limitPercent: limitPercent
  }
}
```

```vue
<!-- PriceDisplay.vue -->
<template>
  <div class="price-display">
    <!-- Limit up badge -->
    <el-tag
      v-if="priceLimit.isLimitUp"
      type="danger"
      effect="dark"
      class="limit-badge"
    >
      涨停
    </el-tag>

    <!-- Limit down badge -->
    <el-tag
      v-if="priceLimit.isLimitDown"
      type="success"
      effect="dark"
      class="limit-badge"
    >
      跌停
    </el-tag>

    <span class="price" :class="priceClass">
      {{ formatPrice(currentPrice) }}
    </span>

    <span class="change" :class="changeClass">
      {{ formatChange(change, changePercent) }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { checkPriceLimit, BoardType } from '@/utils/atrading-rules'

const props = defineProps<{
  currentPrice: number
  prevClose: number
  boardType: BoardType
}>()

// ✅ RED=UP, GREEN=DOWN for A股
const priceClass = computed(() => {
  if (props.currentPrice > props.prevClose) return 'market-up'    // RED
  if (props.currentPrice < props.prevClose) return 'market-down'  // GREEN
  return 'market-flat'
})

const priceLimit = computed(() =>
  checkPriceLimit(props.currentPrice, props.prevClose, props.boardType)
)
</script>

<style scoped>
.market-up {
  color: var(--color-market-up);    /* RED for 涨 */
}

.market-down {
  color: var(--color-market-down);  /* GREEN for 跌 */
}

.market-flat {
  color: var(--color-market-flat);
}

.limit-badge {
  margin-right: 8px;
  font-weight: bold;
}
</style>
```

### 2.2 T+1 Settlement Date Display

**A股 Rule**: Trade date (T) + 1 business day = settlement date (T+1)

```typescript
// src/utils/atrading-rules.ts
export function getSettlementDate(tradeDate: Date): Date {
  const settlementDate = new Date(tradeDate)

  // Add 1 day
  settlementDate.setDate(settlementDate.getDate() + 1)

  // Skip weekends (Saturday=6, Sunday=0)
  while (settlementDate.getDay() === 0 || settlementDate.getDay() === 6) {
    settlementDate.setDate(settlementDate.getDate() + 1)
  }

  // Skip holidays (需要维护节假日列表)
  // const holidays = getHolidays(settlementDate.getFullYear())
  // while (holidays.includes(formatDate(settlementDate))) {
  //   settlementDate.setDate(settlementDate.getDate() + 1)
  // }

  return settlementDate
}

export function validateTPlus1(tradeDate: Date, settlementDate: Date): boolean {
  const expectedSettlement = getSettlementDate(tradeDate)
  return formatDate(settlementDate) === formatDate(expectedSettlement)
}
```

```vue
<!-- TradeInfo.vue -->
<template>
  <div class="trade-info">
    <div class="info-row">
      <span class="label">交易日期:</span>
      <span class="value">{{ formatDate(tradeDate) }}</span>
    </div>

    <div class="info-row">
      <span class="label">交收日期 (T+1):</span>
      <span class="value">{{ formatDate(settlementDate) }}</span>
      <el-tag size="small" type="info" style="margin-left: 8px">
        T+1
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getSettlementDate } from '@/utils/atrading-rules'

const props = defineProps<{
  tradeDate: Date
}>()

const settlementDate = computed(() => getSettlementDate(props.tradeDate))
</script>
```

### 2.3 Lot Size (100股) Formatting

**A股 Rule**: Minimum 100股 per trade (1手 = 100 shares)

```typescript
// src/utils/atrading-rules.ts
export function validateLotSize(quantity: number): boolean {
  return quantity > 0 && quantity % 100 === 0
}

export function formatLots(quantity: number): string {
  const lots = quantity / 100
  return `${lots}手 (${quantity}股)`
}

export function formatPriceWithLot(
  price: number,
  quantity: number
): { total: number; formatted: string } {
  const total = price * quantity
  const lots = quantity / 100

  return {
    total,
    formatted: `¥${total.toFixed(2)} (${lots}手)`
  }
}
```

```vue
<!-- OrderSummary.vue -->
<template>
  <div class="order-summary">
    <div class="row">
      <span>数量:</span>
      <span>{{ formatLots(quantity) }}</span>
    </div>

    <div class="row">
      <span>价格:</span>
      <span>¥{{ price.toFixed(2) }}</span>
    </div>

    <div class="row total">
      <span>金额:</span>
      <span class="value">¥{{ totalAmount.toFixed(2) }}</span>
    </div>

    <el-alert
      v-if="!isLotSizeValid"
      type="error"
      :closable="false"
      show-icon
    >
      A股交易必须为100股的整数倍
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { validateLotSize, formatLots } from '@/utils/atrading-rules'

const props = defineProps<{
  price: number
  quantity: number
}>()

const totalAmount = computed(() => props.price * props.quantity)
const isLotSizeValid = computed(() => validateLotSize(props.quantity))
</script>
```

### 2.4 Trading Hours Display

**A股 Trading Hours**:
- Morning: 9:30-11:30
- Afternoon: 13:00-15:00
- Pre-market call auction: 9:15-9:25
- Post-market call auction: 15:00-15:03 (used to be 15:00-15:30)

```typescript
// src/utils/market-hours.ts
export enum MarketPhase {
  PRE_MARKET = 'PRE_MARKET',           // 9:15-9:25
  MORNING_AUCTION = 'MORNING_AUCTION', // 9:25
  MORNING_TRADING = 'MORNING_TRADING', // 9:30-11:30
  LUNCH_BREAK = 'LUNCH_BREAK',         // 11:30-13:00
  AFTERNOON_TRADING = 'AFTERNOON_TRADING', // 13:00-15:00
  CLOSED = 'CLOSED'                    // 15:00+
}

export function getMarketPhase(date: Date): MarketPhase {
  const hours = date.getHours()
  const minutes = date.getMinutes()
  const time = hours * 60 + minutes

  // Pre-market: 9:15-9:25 (555-565 minutes)
  if (time >= 555 && time < 565) return MarketPhase.PRE_MARKET

  // Morning auction: 9:25 (565 minutes)
  if (time >= 565 && time < 570) return MarketPhase.MORNING_AUCTION

  // Morning trading: 9:30-11:30 (570-690 minutes)
  if (time >= 570 && time < 690) return MarketPhase.MORNING_TRADING

  // Lunch break: 11:30-13:00 (690-780 minutes)
  if (time >= 690 && time < 780) return MarketPhase.LUNCH_BREAK

  // Afternoon trading: 13:00-15:00 (780-900 minutes)
  if (time >= 780 && time < 900) return MarketPhase.AFTERNOON_TRADING

  return MarketPhase.CLOSED
}

export function formatMarketPhase(phase: MarketPhase): string {
  const labels = {
    [MarketPhase.PRE_MARKET]: '集合竞价',
    [MarketPhase.MORNING_AUCTION]: '开盘竞价',
    [MarketPhase.MORNING_TRADING]: '早盘交易中',
    [MarketPhase.LUNCH_BREAK]: '午间休市',
    [MarketPhase.AFTERNOON_TRADING]: '午盘交易中',
    [MarketPhase.CLOSED]: '休市'
  }
  return labels[phase]
}
```

```vue
<!-- MarketStatus.vue -->
<template>
  <div class="market-status">
    <el-tag :type="statusTagType" effect="dark">
      {{ marketPhaseLabel }}
    </el-tag>

    <span class="time" v-if="isTradingTime">
      {{ currentTime }}
    </span>

    <el-progress
      v-if="isTradingTime"
      :percentage="sessionProgress"
      :show-text="false"
      :stroke-width="4"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { getMarketPhase, formatMarketPhase, MarketPhase } from '@/utils/market-hours'

const currentTime = ref(new Date())

const marketPhase = computed(() => getMarketPhase(currentTime.value))
const marketPhaseLabel = computed(() => formatMarketPhase(marketPhase.value))

const statusTagType = computed(() => {
  if (marketPhase.value === MarketPhase.CLOSED) return 'info'
  if (marketPhase.value === MarketPhase.LUNCH_BREAK) return 'warning'
  return 'success' // Trading in progress
})

const isTradingTime = computed(() =>
  [
    MarketPhase.MORNING_TRADING,
    MarketPhase.AFTERNOON_TRADING
  ].includes(marketPhase.value)
)

const sessionProgress = computed(() => {
  // Calculate trading session progress percentage
  const hours = currentTime.value.getHours()
  const minutes = currentTime.value.getMinutes()
  const time = hours * 60 + minutes

  // Morning session: 9:30-11:30 (120 minutes)
  if (marketPhase.value === MarketPhase.MORNING_TRADING) {
    return ((time - 570) / 120) * 100
  }

  // Afternoon session: 13:00-15:00 (120 minutes)
  if (marketPhase.value === MarketPhase.AFTERNOON_TRADING) {
    return ((time - 780) / 120) * 100
  }

  return 0
})

let timer: number
onMounted(() => {
  timer = window.setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>
```

---

## 3. Vue 3 + TypeScript Implementation Strategy

### 3.1 TypeScript Configuration

**Create** `web/frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    // Language and Environment
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],

    // Modules
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowImportingTsExtensions": true,

    // Type Checking (Gradual Migration)
    "strict": false,              // Start loose
    "noUnusedLocals": false,      // Enable later
    "noUnusedParameters": false,  // Enable later
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,

    // Interop Constraints
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,

    // JS/TS Coexistence
    "allowJs": true,
    "checkJs": false,
    "jsx": "preserve",

    // Path Mapping
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.d.ts",
    "src/**/*.tsx",
    "src/**/*.vue"
  ],
  "exclude": [
    "dist",
    "node_modules"
  ],
  "references": [
    { "path": "./tsconfig.node.json" }
  ]
}
```

**Create** `web/frontend/tsconfig.node.json` (for Vite config):

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": [
    "vite.config.ts"
  ]
}
```

**Update** `web/frontend/vite.config.js` → `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3020,  // Use allowed port range (3020-3029 for frontend)
    proxy: {
      '/api': {
        target: 'http://localhost:8020',  // Use allowed port range (8020-8029 for backend)
        changeOrigin: true
      }
    }
  },
  build: {
    target: 'es2020',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts'],
          'klinecharts': ['klinecharts'],
          'vue-vendor': ['vue', 'vue-router', 'pinia']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

### 3.2 Type Definitions Structure

**Directory Structure**:
```
src/types/
├── index.ts              # Central export point
├── market.ts             # Market data types
├── indicators.ts         # Technical indicator types
├── trading.ts            # A股 trading rules types
├── strategy.ts           # Strategy & backtest types
├── ai.ts                 # AI query types
└── api.ts                # API response types
```

**src/types/market.ts**:

```typescript
/**
 * Stock basic information
 */
export interface StockInfo {
  /** Stock symbol (e.g., "000001", "600000") */
  symbol: string
  /** Stock name (e.g., "平安银行", "浦发银行") */
  name: string
  /** Board type */
  boardType: BoardType
  /** Industry classification */
  industry?: string
  /** Market cap (万元) */
  marketCap?: number
}

/**
 * A股 board types
 */
export enum BoardType {
  /** 主板 */
  MAIN = 'MAIN',
  /** 创业板 */
  CHI_NEXT = 'CHI_NEXT',
  /** 科创板 */
  STAR = 'STAR',
  /** ST股 */
  ST = 'ST'
}

/**
 * Real-time stock price data
 */
export interface StockPrice {
  symbol: string
  name: string
  /** Current price (元) */
  price: number
  /** Previous close price (元) */
  prevClose: number
  /** Price change (元) */
  change: number
  /** Price change percent (%) */
  changePercent: number
  /** Opening price (元) */
  open: number
  /** Highest price (元) */
  high: number
  /** Lowest price (元) */
  low: number
  /** Volume (股) */
  volume: number
  /** Amount (元) */
  amount: number
  /** Timestamp (ISO 8601) */
  timestamp: string
  /** Limit up/down status */
  limitStatus?: LimitStatus
}

/**
 * Price limit status
 */
export interface LimitStatus {
  /** Is at limit up (涨停) */
  isLimitUp: boolean
  /** Is at limit down (跌停) */
  isLimitDown: boolean
  /** Limit price */
  limitPrice: number
  /** Limit percentage (0.10 for 10%) */
  limitPercent: number
}

/**
 * K-line (candlestick) data point
 */
export interface KLineData {
  /** Unix timestamp (seconds) or ISO 8601 string */
  timestamp: number | string
  /** Opening price (元) */
  open: number
  /** Highest price (元) */
  high: number
  /** Lowest price (元) */
  low: number
  /** Closing price (元) */
  close: number
  /** Volume (股) */
  volume: number
  /** Turnover amount (元) */
  amount?: number
  /** Change percent (%) */
  changePercent?: number
}

/**
 * K-line period type
 */
export type KLinePeriod =
  | '1m'   // 1 minute
  | '5m'   // 5 minutes
  | '15m'  // 15 minutes
  | '30m'  // 30 minutes
  | '1h'   // 1 hour
  | '1d'   // 1 day
  | '1w'   // 1 week
  | '1M'   // 1 month

/**
 * OHLCV data (Open, High, Low, Close, Volume)
 */
export interface OHLCV extends KLineData {
  timestamp: number
}

/**
 *复权类型 (Adjustment type)
 */
export enum AdjustmentType {
  /** 不复权 (No adjustment) */
  NONE = 'none',
  /** 前复权 (Forward adjustment) */
  FRONT = 'front',
  /** 后复权 (Backward adjustment) */
  BACK = 'back'
}
```

**src/types/indicators.ts**:

```typescript
/**
 * Technical indicator interface
 */
export interface Indicator {
  /** Indicator name (unique identifier) */
  name: string
  /** Display name (Chinese) */
  displayName: string
  /** Category */
  category: IndicatorCategory
  /** Calculate method */
  calculate: (data: number[], params?: Record<string, number>) => number[]
  /** Validate parameters */
  validate?: (params: Record<string, number>) => boolean
  /** Default parameters */
  defaultParams?: Record<string, number>
  /** Description */
  description?: string
}

/**
 * Indicator categories
 */
export enum IndicatorCategory {
  /** 趋势指标 (Trend) */
  TREND = 'TREND',
  /** 动量指标 (Momentum) */
  MOMENTUM = 'MOMENTUM',
  /** 波动率指标 (Volatility) */
  VOLATILITY = 'VOLATILITY',
  /** 成交量指标 (Volume) */
  VOLUME = 'VOLUME',
  /** K线形态 (Pattern) */
  PATTERN = 'PATTERN'
}

/**
 * Indicator configuration for display
 */
export interface IndicatorConfig {
  /** Indicator name */
  name: string
  /** Parameters */
  parameters: Record<string, number>
  /** Display settings */
  display: {
    /** Color (CSS color) */
    color: string
    /** Line width */
    lineWidth: number
    /** Line style (solid, dashed, dotted) */
    lineStyle?: 'solid' | 'dashed' | 'dotted'
    /** Visibility */
    visible: boolean
  }
}

/**
 * Indicator calculation result
 */
export interface IndicatorResult {
  /** Indicator name */
  name: string
  /** Calculated values */
  values: number[]
  /** Valid from index (warmup period) */
  validFrom: number
}
```

**src/types/trading.ts**:

```typescript
import type { BoardType } from './market'

/**
 * A股 T+1 trading rule
 */
export interface ATradingRule {
  name: string
  description: string
  validate: (data: TradeData) => ValidationResult
}

/**
 * Trade data
 */
export interface TradeData {
  symbol: string
  price: number
  quantity: number
  tradeDate: Date
  settlementDate: Date
  boardType: BoardType
}

/**
 * Validation result
 */
export interface ValidationResult {
  isValid: boolean
  errors?: string[]
  warnings?: string[]
}

/**
 * Order type
 */
export enum OrderType {
  /** 限价单 (Limit order) */
  LIMIT = 'LIMIT',
  /** 市价单 (Market order) */
  MARKET = 'MARKET'
}

/**
 * Order side (buy/sell)
 */
export enum OrderSide {
  /** 买入 (Buy) */
  BUY = 'BUY',
  /** 卖出 (Sell) */
  SELL = 'SELL'
}

/**
 * Commission calculation result
 */
export interface CommissionResult {
  /** Commission fee (佣金) */
  commission: number
  /** Stamp tax (印花税, only for sell) */
  stampTax: number
  /** Transfer fee (过户费) */
  transferFee: number
  /** Total fees */
  total: number
}
```

**src/types/ai.ts**:

```typescript
/**
 * Query pattern for natural language parsing
 */
export interface QueryPattern {
  /** Regular expression */
  pattern: RegExp
  /** SQL template with placeholders */
  sqlTemplate: string
  /** Parameter names */
  parameters?: string[]
  /** Expected parameter types */
  parameterTypes?: Record<string, 'number' | 'string' | 'date'>
}

/**
 * Query result
 */
export interface QueryResult {
  /** Generated SQL */
  sql: string
  /** Confidence score (0-1) */
  confidence: number
  /** Matching method */
  method: 'pattern' | 'ai'
  /** Matched pattern (if pattern matching) */
  matchedPattern?: RegExp
  /** Extracted parameters */
  parameters?: Record<string, any>
}

/**
 * Stock recommendation
 */
export interface StockRecommendation {
  symbol: string
  name: string
  reason: string
  confidence: number
  category: RecommendationCategory
  timestamp: string
}

/**
 * Recommendation category
 */
export enum RecommendationCategory {
  /** 热门推荐 (Hot stocks) */
  HOT = 'hot',
  /** 异动提醒 (Price alerts) */
  ALERT = 'alert',
  /** 策略匹配 (Strategy match) */
  STRATEGY_MATCH = 'strategy-match'
}
```

### 3.3 Component Migration Pattern

**Before** (JavaScript):

```vue
<!-- Dashboard.vue -->
<template>
  <div class="dashboard">
    <h1>仪表盘</h1>
    <StockList :stocks="stocks" />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import StockList from '@/components/StockList.vue'
import { getStocks } from '@/api/market'

export default {
  name: 'Dashboard',
  components: { StockList },
  setup() {
    const stocks = ref([])

    onMounted(async () => {
      const data = await getStocks()
      stocks.value = data
    })

    return {
      stocks
    }
  }
}
</script>
```

**After** (TypeScript):

```vue
<!-- Dashboard.vue -->
<template>
  <div class="dashboard">
    <h1>仪表盘</h1>
    <StockList :stocks="stocks" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import StockList from '@/components/StockList.vue'
import { getStocks } from '@/api/market'
import type { StockPrice } from '@/types/market'

// ✅ Typed ref
const stocks = ref<StockPrice[]>([])

onMounted(async () => {
  const data = await getStocks()
  stocks.value = data
})
</script>

<!-- OR Options API style -->
<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import StockList from '@/components/StockList.vue'
import { getStocks } from '@/api/market'
import type { StockPrice } from '@/types/market'

export default defineComponent({
  name: 'Dashboard',
  components: { StockList },
  setup() {
    const stocks = ref<StockPrice[]>([])

    onMounted(async () => {
      const data = await getStocks()
      stocks.value = data
    })

    return {
      stocks
    }
  }
})
</script>
```

**Props with TypeScript**:

```vue
<script setup lang="ts">
import type { StockPrice, BoardType } from '@/types/market'

// ✅ Define props with types
interface Props {
  stocks: StockPrice[]
  loading?: boolean
  boardType?: BoardType
}

// ✅ withDefaults for default values
const props = withDefaults(defineProps<Props>(), {
  loading: false,
  boardType: BoardType.MAIN
})

// ✅ Define emits with types
interface Emits {
  (e: 'select-stock', symbol: string): void
  (e: 'refresh'): void
}

const emit = defineEmits<Emits>()

// ✅ Use props with type safety
const handleStockClick = (symbol: string) => {
  emit('select-stock', symbol) // ✅ Type-checked
}

// ✅ Computed with inferred types
const stockCount = computed(() => props.stocks.length)
const isMarketOpen = computed((): boolean => {
  // Market logic here
  return true
})
</script>
```

---

## 4. K-line Chart (klinecharts 9.6.0) Implementation

### 4.1 ProKLineChart Component

**Create** `src/components/Market/ProKLineChart.vue`:

```vue
<template>
  <div class="pro-kline-chart" ref="chartContainer">
    <!-- Chart toolbar -->
    <div class="chart-toolbar">
      <!-- Period selector -->
      <el-radio-group v-model="currentPeriod" size="small" @change="onPeriodChange">
        <el-radio-button label="1m">分时</el-radio-button>
        <el-radio-button label="5m">5分</el-radio-button>
        <el-radio-button label="15m">15分</el-radio-button>
        <el-radio-button label="1h">60分</el-radio-button>
        <el-radio-button label="1d">日线</el-radio-button>
        <el-radio-button label="1w">周线</el-radio-button>
      </el-radio-group>

      <!-- Adjustment type -->
      <el-dropdown trigger="click" @command="onAdjustmentChange">
        <el-button size="small">
          {{ adjustmentTypeLabel }}
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="none">不复权</el-dropdown-item>
            <el-dropdown-item command="front">前复权</el-dropdown-item>
            <el-dropdown-item command="back">后复权</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- Indicator selector -->
      <el-dropdown trigger="click">
        <el-button size="small">
          指标
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="toggleIndicator('MA')">MA</el-dropdown-item>
            <el-dropdown-item @click="toggleIndicator('VOL')">VOL</el-dropdown-item>
            <el-dropdown-item @click="toggleIndicator('MACD')">MACD</el-dropdown-item>
            <el-dropdown-item @click="toggleIndicator('RSI')">RSI</el-dropdown-item>
            <el-dropdown-item @click="toggleIndicator('KDJ')">KDJ</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- Chart container -->
    <div class="chart-container" ref="chartRef"></div>

    <!-- Loading state -->
    <div v-if="loading" class="chart-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="chart-error">
      <el-empty description="加载失败">
        <el-button type="primary" @click="loadData">重试</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { init, dispose, Chart, Styles } from 'klinecharts'
import type { KLineData, KLinePeriod, AdjustmentType } from '@/types/market'
import { getKLineData } from '@/api/market'
import { checkPriceLimit } from '@/utils/atrading-rules'

// Props
interface Props {
  symbol: string
  name?: string
  defaultPeriod?: KLinePeriod
  defaultAdjustment?: AdjustmentType
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  defaultPeriod: '1d',
  defaultAdjustment: 'none',
  height: 500
})

// Refs
const chartContainer = ref<HTMLDivElement>()
const chartRef = ref<HTMLDivElement>()
const chart = ref<Chart>()

// State
const currentPeriod = ref<KLinePeriod>(props.defaultPeriod)
const adjustmentType = ref<AdjustmentType>(props.defaultAdjustment)
const loading = ref(false)
const error = ref<Error | null>(null)
const activeIndicators = ref<Set<string>>(new Set(['MA', 'VOL']))

// Computed
const adjustmentTypeLabel = computed(() => {
  const labels = {
    none: '不复权',
    front: '前复权',
    back: '后复权'
  }
  return labels[adjustmentType.value]
})

// Methods
const initChart = () => {
  if (!chartRef.value) return

  // Dispose existing chart
  if (chart.value) {
    dispose(chartRef.value)
  }

  // ✅ A股 color scheme: RED=UP, GREEN=DOWN
  const styles: Styles = {
    grid: {
      show: true,
      size: 1,
      color: '#2D3446'
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#FF5252',      // ✅ RED for UP (涨)
        downColor: '#00E676',    // ✅ GREEN for DOWN (跌)
        noChangeColor: '#B0B3B8' // GRAY for FLAT (平)
      },
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        labels: ['时间: ', '开: ', '收: ', '高: ', '低: ', '成交量: '],
        text: {
          size: 12,
          color: '#D9D9D9'
        }
      },
      priceMark: {
        show: true,
        high: {
          show: true,
          color: '#FF5252',
          textSize: 10
        },
        low: {
          show: true,
          color: '#00E676',
          textSize: 10
        },
        last: {
          show: true,
          upColor: '#FF5252',
          downColor: '#00E676',
          noChangeColor: '#B0B3B8',
          text: {
            show: true,
            size: 12
          }
        }
      }
    },
    indicator: {
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        text: {
          size: 12,
          color: '#D9D9D9'
        }
      }
    },
    xAxis: {
      show: true,
      size: 'auto',
      axisLine: {
        show: true,
        color: '#2D3446'
      },
      tickLine: {
        show: true,
        size: 1,
        length: 5,
        color: '#2D3446'
      },
      tickText: {
        show: true,
        size: 12,
        color: '#B0B3B8',
        fontFamily: 'Roboto Mono, monospace'
      }
    },
    yAxis: {
      show: true,
      size: 'auto',
      position: 'right',
      axisLine: {
        show: true,
        color: '#2D3446'
      },
      tickLine: {
        show: true,
        size: 1,
        length: 5,
        color: '#2D3446'
      },
      tickText: {
        show: true,
        size: 12,
        color: '#B0B3B8',
        fontFamily: 'Roboto Mono, monospace'
      }
    },
    crosshair: {
      show: true,
      horizontal: {
        show: true,
        line: {
          show: true,
          style: 'dashed',
          dashValue: [4, 2],
          size: 1,
          color: '#FFFFFF'
        },
        text: {
          show: true,
          color: '#FFFFFF',
          size: 12,
          backgroundColor: '#2979FF'
        }
      },
      vertical: {
        show: true,
        line: {
          show: true,
          style: 'dashed',
          dashValue: [4, 2],
          size: 1,
          color: '#FFFFFF'
        },
        text: {
          show: true,
          color: '#FFFFFF',
          size: 12,
          backgroundColor: '#2979FF'
        }
      }
    }
  }

  chart.value = init(chartRef.value, styles)

  // Set default indicators
  if (activeIndicators.value.has('MA')) {
    chart.value?.createIndicator('MA', false, { period: [5, 10, 20, 60] })
  }

  if (activeIndicators.value.has('VOL')) {
    chart.value?.createIndicator('VOL', true, { height: 80 })
  }
}

const loadData = async () => {
  if (!chart.value) return

  loading.value = true
  error.value = null

  try {
    const data = await getKLineData({
      symbol: props.symbol,
      period: currentPeriod.value,
      adjustment: adjustmentType.value
    })

    // ✅ Add 涨跌停 markers
    const dataWithMarkers = data.map(item => {
      const limitStatus = checkPriceLimit(
        item.close,
        item.close, // Note: needs prevClose from API
        'MAIN' // TODO: get from stock info
      )

      return {
        ...item,
        timestamp: new Date(item.timestamp).getTime(),
        // Markers for limit up/down
        mark: limitStatus.isLimitUp ? 'limit-up' :
               limitStatus.isLimitDown ? 'limit-down' : undefined
      }
    })

    chart.value?.applyNewData(dataWithMarkers)

  } catch (err) {
    error.value = err as Error
    console.error('Failed to load K-line data:', err)
  } finally {
    loading.value = false
  }
}

const onPeriodChange = () => {
  loadData()
}

const onAdjustmentChange = (command: AdjustmentType) => {
  adjustmentType.value = command
  loadData()
}

const toggleIndicator = (indicator: string) => {
  if (!chart.value) return

  if (activeIndicators.value.has(indicator)) {
    activeIndicators.value.delete(indicator)
    chart.value?.removeIndicator(indicator)
  } else {
    activeIndicators.value.add(indicator)

    // Add indicator with default parameters
    switch (indicator) {
      case 'MA':
        chart.value?.createIndicator('MA', false, { period: [5, 10, 20, 60] })
        break
      case 'VOL':
        chart.value?.createIndicator('VOL', true, { height: 80 })
        break
      case 'MACD':
        chart.value?.createIndicator('MACD', true, { height: 100 })
        break
      case 'RSI':
        chart.value?.createIndicator('RSI', true, { height: 60 })
        break
      case 'KDJ':
        chart.value?.createIndicator('KDJ', true, { height: 80 })
        break
    }
  }
}

// Lifecycle
onMounted(() => {
  initChart()
  loadData()
})

onUnmounted(() => {
  if (chart.value && chartRef.value) {
    dispose(chartRef.value)
  }
})

// Watch for symbol changes
watch(() => props.symbol, () => {
  loadData()
})
</script>

<style scoped>
.pro-kline-chart {
  width: 100%;
  height: 100%;
  position: relative;
}

.chart-toolbar {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--color-border-base);
  align-items: center;
}

.chart-container {
  width: 100%;
  height: calc(100% - 60px); /* Subtract toolbar height */
}

.chart-loading,
.chart-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  z-index: 10;
}
</style>
```

### 4.2 Data Downsampling for Performance

**Create** `src/utils/chart-utils.ts`:

```typescript
/**
 * Downsample K-line data for performance
 * Largest-Triangle-Three-Buckets algorithm
 */
export function downsampleKLineData(
  data: KLineData[],
  threshold: number = 1000
): KLineData[] {
  if (data.length <= threshold) return data

  const bucketSize = data.length / threshold
  const sampled: KLineData[] = []
  let a = 0 // Start of current bucket

  sampled.push(data[0]) // Always include first point

  for (let i = 0; i < threshold - 1; i++) {
    // Calculate bucket range
    const avgRangeStart = Math.floor((i + 1) * bucketSize)
    const avgRangeEnd = Math.floor((i + 2) * bucketSize) + 1
    const avgRangeLength = avgRangeEnd - avgRangeStart

    // Get next bucket point
    const avgRangeStartNext = Math.floor((i + 2) * bucketSize) + 1
    const avgRangeEndNext = Math.min(Math.floor((i + 3) * bucketSize) + 1, data.length)
    const avgRangeLengthNext = avgRangeEndNext - avgRangeStartNext

    // Find max area triangle
    let maxArea = -1
    let maxAreaPoint: KLineData | null = null

    const avgX = (avgRangeStartNext + avgRangeEndNext) / 2
    const avgY = computeAverageY(data, avgRangeStartNext, avgRangeEndNext)

    for (let j = avgRangeStart; j < avgRangeEnd; j++) {
      const area = Math.abs(
        (avgX - (a + j)) * (data[j].close - avgY) / 2
      )

      if (area > maxArea) {
        maxArea = area
        maxAreaPoint = data[j]
        a = j
      }
    }

    sampled.push(maxAreaPoint!)
  }

  sampled.push(data[data.length - 1]) // Always include last point

  return sampled
}

function computeAverageY(data: KLineData[], start: number, end: number): number {
  let sum = 0
  for (let i = start; i < end; i++) {
    sum += data[i].close
  }
  return sum / (end - start)
}

/**
 * Load K-line data with lazy loading
 */
export async function loadKLineDataLazy(
  symbol: string,
  period: KLinePeriod,
  adjustment: AdjustmentType,
  onProgress: (data: KLineData[]) => void,
  chunkSize: number = 1000
): Promise<void> {
  let offset = 0
  let hasMore = true

  while (hasMore) {
    const chunk = await getKLineData({
      symbol,
      period,
      adjustment,
      limit: chunkSize,
      offset
    })

    onProgress(chunk)

    hasMore = chunk.length === chunkSize
    offset += chunkSize
  }
}
```

### 4.3 Web Worker for Indicator Calculations

**Create** `src/workers/indicator.worker.ts`:

```typescript
/// <reference lib="webworker" />

import { calculateSMA, calculateEMA, calculateRSI, calculateMACD } from '@/utils/indicators'

self.onmessage = (event: MessageEvent) => {
  const { type, data, params } = event.data

  try {
    switch (type) {
      case 'SMA':
        postMessage({ result: calculateSMA(data, params.period) })
        break

      case 'EMA':
        postMessage({ result: calculateEMA(data, params.period) })
        break

      case 'RSI':
        postMessage({ result: calculateRSI(data, params.period) })
        break

      case 'MACD':
        postMessage({
          result: calculateMACD(data, {
            fastPeriod: params.fastPeriod || 12,
            slowPeriod: params.slowPeriod || 26,
            signalPeriod: params.signalPeriod || 9
          })
        })
        break

      default:
        postMessage({ error: `Unknown indicator type: ${type}` })
    }
  } catch (error) {
    postMessage({ error: (error as Error).message })
  }
}

export {}
```

**Use in component**:

```typescript
import IndicatorWorker from '@/workers/indicator.worker.ts?worker'

const worker = new IndicatorWorker()

worker.onmessage = (event) => {
  if (event.data.error) {
    console.error('Indicator calculation error:', event.data.error)
  } else {
    indicatorValues.value = event.data.result
  }
}

// Trigger calculation
worker.postMessage({
  type: 'RSI',
  data: priceData.value,
  params: { period: 14 }
})
```

---

## 5. Performance Optimization

### 5.1 Bundle Size Optimization

**Update** `vite.config.ts`:

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-library': ['element-plus', '@element-plus/icons-vue'],
          'charts': ['echarts', 'klinecharts'],
          'utils': ['dayjs', 'lodash-es', 'axios']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  // Enable CSS code splitting
  css: {
    devSourcemap: true
  }
})
```

**Lazy load routes**:

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/views/Market.vue')
  },
  {
    path: '/strategy',
    name: 'StrategyManagement',
    component: () => import('@/views/StrategyManagement.vue')
  },
  {
    path: '/backtest',
    name: 'BacktestAnalysis',
    component: () => import('@/views/BacktestAnalysis.vue')
  }
  // ... other routes
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

### 5.2 Virtual Scrolling for Large Lists

**Install** `vue-virtual-scroller`:

```bash
npm install vue-virtual-scroller
```

**Use in table component**:

```vue
<template>
  <RecycleScroller
    class="stock-list"
    :items="stocks"
    :item-size="50"
    key-field="symbol"
    v-slot="{ item }"
  >
    <div class="stock-row">
      <span>{{ item.symbol }}</span>
      <span>{{ item.name }}</span>
      <span :class="getChangeClass(item)">{{ item.price }}</span>
      <span :class="getChangeClass(item)">{{ item.changePercent }}%</span>
    </div>
  </RecycleScroller>
</template>

<script setup lang="ts">
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import type { StockPrice } from '@/types/market'

const props = defineProps<{
  stocks: StockPrice[]
}>()

const getChangeClass = (stock: StockPrice) => {
  return stock.changePercent >= 0 ? 'market-up' : 'market-down'
}
</script>
```

---

## 6. Real-time Data: SSE vs WebSocket

### 6.1 Server-Sent Events (SSE) Implementation

**Backend (FastAPI)**:

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()

@router.get("/api/market/realtime")
async def market_realtime():
    async def event_generator():
        while True:
            # Get real-time data
            data = await get_realtime_stocks()

            # Send SSE event
            yield f"data: {json.dumps(data)}\n\n"

            # Wait 1 second
            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

**Frontend**:

```typescript
// src/composables/useRealtimeMarketData.ts
import { ref, onUnmounted } from 'vue'
import type { StockPrice } from '@/types/market'

export function useRealtimeMarketData() {
  const stocks = ref<StockPrice[]>([])
  const connected = ref(false)
  const error = ref<Error | null>(null)

  let eventSource: EventSource | null = null

  const connect = () => {
    eventSource = new EventSource('/api/market/realtime')

    eventSource.onopen = () => {
      connected.value = true
      error.value = null
    }

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      stocks.value = data
    }

    eventSource.onerror = (err) => {
      error.value = new Error('SSE connection error')
      connected.value = false

      // Auto-reconnect after 5 seconds
      setTimeout(() => {
        connect()
      }, 5000)
    }
  }

  const disconnect = () => {
    eventSource?.close()
    connected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    stocks,
    connected,
    error,
    connect,
    disconnect
  }
}
```

### 6.2 WebSocket Implementation

**Backend (FastAPI)**:

```python
from fastapi import WebSocket
from fastapi import APIRouter

router = APIRouter()

@router.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Get real-time data
            data = await get_realtime_stocks()

            # Send WebSocket message
            await websocket.send_json(data)

            # Wait 1 second
            await asyncio.sleep(1)

    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        await websocket.close()
```

**Frontend**:

```typescript
// src/composables/useWebSocketMarket.ts
import { ref, onUnmounted } from 'vue'
import type { StockPrice } from '@/types/market'

export function useWebSocketMarket() {
  const stocks = ref<StockPrice[]>([])
  const connected = ref(false)
  const error = ref<Error | null>(null)

  let ws: WebSocket | null = null
  let reconnectTimer: number | null = null

  const connect = () => {
    ws = new WebSocket('ws://localhost:8020/ws/market')

    ws.onopen = () => {
      connected.value = true
      error.value = null
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      stocks.value = data
    }

    ws.onerror = (err) => {
      error.value = new Error('WebSocket error')
    }

    ws.onclose = () => {
      connected.value = false

      // Auto-reconnect after 5 seconds
      reconnectTimer = window.setTimeout(() => {
        connect()
      }, 5000)
    }
  }

  const disconnect = () => {
    ws?.close()
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }
    connected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    stocks,
    connected,
    error,
    connect,
    disconnect
  }
}
```

---

## 7. Mobile Responsive Design

### 7.1 Breakpoint Strategy

**Create** `src/styles/breakpoints.scss`:

```scss
// Breakpoints
$breakpoint-xs: 320px;   // Extra small phones
$breakpoint-sm: 480px;   // Small phones
$breakpoint-md: 768px;   // Tablets
$breakpoint-lg: 1024px;  // Desktops
$breakpoint-xl: 1280px;  // Large desktops
$breakpoint-xxl: 1536px; // Extra large desktops

// Mixins
@mixin respond-to($breakpoint) {
  @if $breakpoint == xs {
    @media (min-width: $breakpoint-xs) { @content; }
  }
  @else if $breakpoint == sm {
    @media (min-width: $breakpoint-sm) { @content; }
  }
  @else if $breakpoint == md {
    @media (min-width: $breakpoint-md) { @content; }
  }
  @else if $breakpoint == lg {
    @media (min-width: $breakpoint-lg) { @content; }
  }
  @else if $breakpoint == xl {
    @media (min-width: $breakpoint-xl) { @content; }
  }
  @else if $breakpoint == xxl {
    @media (min-width: $breakpoint-xxl) { @content; }
  }
}

@mixin mobile-only {
  @media (max-width: $breakpoint-md - 1) { @content; }
}

@mixin tablet-only {
  @media (min-width: $breakpoint-md) and (max-width: $breakpoint-lg - 1) { @content; }
}

@mixin desktop-only {
  @media (min-width: $breakpoint-lg) { @content; }
}
```

### 7.2 Mobile-Specific Components

**Card-based table for mobile**:

```vue
<template>
  <!-- Desktop: Table view -->
  <el-table
    v-if="!isMobile"
    :data="stocks"
    class="stock-table"
  >
    <el-table-column prop="symbol" label="代码" width="100" />
    <el-table-column prop="name" label="名称" width="120" />
    <el-table-column prop="price" label="价格" width="100">
      <template #default="{ row }">
        <span :class="getChangeClass(row)">{{ row.price }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="changePercent" label="涨跌幅" width="100">
      <template #default="{ row }">
        <span :class="getChangeClass(row)">{{ row.changePercent }}%</span>
      </template>
    </el-table-column>
    <el-table-column prop="volume" label="成交量" />
  </el-table>

  <!-- Mobile: Card view -->
  <div v-else class="stock-cards">
    <div
      v-for="stock in stocks"
      :key="stock.symbol"
      class="stock-card"
      @click="handleStockClick(stock)"
    >
      <div class="card-header">
        <span class="symbol">{{ stock.symbol }}</span>
        <span class="price" :class="getChangeClass(stock)">
          {{ stock.price }}
        </span>
      </div>

      <div class="card-body">
        <div class="name">{{ stock.name }}</div>
        <div class="change" :class="getChangeClass(stock)">
          {{ stock.changePercent >= 0 ? '+' : '' }}{{ stock.changePercent }}%
        </div>
      </div>

      <div class="card-footer">
        <span class="volume">成交量: {{ formatVolume(stock.volume) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWindowSize } from '@vueuse/core'
import type { StockPrice } from '@/types/market'

const props = defineProps<{
  stocks: StockPrice[]
}>()

// Mobile breakpoint: < 768px
const isMobile = computed(() => {
  const { width } = useWindowSize()
  return width.value < 768
})

const getChangeClass = (stock: StockPrice) => {
  return stock.changePercent >= 0 ? 'market-up' : 'market-down'
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(2)}亿`
  }
  if (volume >= 10000) {
    return `${(volume / 10000).toFixed(2)}万`
  }
  return volume.toString()
}

const emit = defineEmits<{
  (e: 'select-stock', stock: StockPrice): void
}>()

const handleStockClick = (stock: StockPrice) => {
  emit('select-stock', stock)
}
</script>

<style scoped>
.stock-cards {
  padding: 12px;
}

.stock-card {
  background: var(--bg-card);
  border-radius: var(--border-radius-base);
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid var(--color-border-base);
  cursor: pointer;
  transition: all 0.2s;
}

.stock-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.symbol {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.price {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  font-family: 'Roboto Mono', monospace;
}

.name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.change {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  font-family: 'Roboto Mono', monospace;
}

.card-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
}

.volume {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.market-up {
  color: var(--color-market-up);    /* RED for 涨 */
}

.market-down {
  color: var(--color-market-down);  /* GREEN for 跌 */
}
</style>
```

---

## 8. Testing Strategy

### 8.1 Vitest Unit Testing

**Install** `@vitest/ui` and coverage tools:

```bash
npm install -D @vitest/ui @vitest/coverage-v8 @vue/test-utils
```

**vitest.config.ts**:

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'src/main.ts'
      ]
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

**Example test** - `atrading-rules.test.ts`:

```typescript
import { describe, it, expect } from 'vitest'
import { checkPriceLimit, validateLotSize, getSettlementDate } from '@/utils/atrading-rules'
import { BoardType } from '@/types/market'

describe('ATradingRules', () => {
  describe('checkPriceLimit', () => {
    it('should detect limit up for main board stock (+10%)', () => {
      const prevClose = 10.0
      const current = 11.0 // +10%

      const result = checkPriceLimit(current, prevClose, BoardType.MAIN)

      expect(result.isLimitUp).toBe(true)
      expect(result.isLimitDown).toBe(false)
      expect(result.limitPercent).toBe(0.10)
    })

    it('should detect limit down for main board stock (-10%)', () => {
      const prevClose = 10.0
      const current = 9.0 // -10%

      const result = checkPriceLimit(current, prevClose, BoardType.MAIN)

      expect(result.isLimitUp).toBe(false)
      expect(result.isLimitDown).toBe(true)
      expect(result.limitPercent).toBe(0.10)
    })

    it('should detect limit up for ChiNext stock (+20%)', () => {
      const prevClose = 10.0
      const current = 12.0 // +20%

      const result = checkPriceLimit(current, prevClose, BoardType.CHI_NEXT)

      expect(result.isLimitUp).toBe(true)
      expect(result.limitPercent).toBe(0.20)
    })
  })

  describe('validateLotSize', () => {
    it('should accept valid lot sizes', () => {
      expect(validateLotSize(100)).toBe(true)
      expect(validateLotSize(200)).toBe(true)
      expect(validateLotSize(1000)).toBe(true)
    })

    it('should reject invalid lot sizes', () => {
      expect(validateLotSize(150)).toBe(false)  // Not multiple of 100
      expect(validateLotSize(0)).toBe(false)    // Zero
      expect(validateLotSize(-100)).toBe(false) // Negative
    })
  })

  describe('getSettlementDate', () => {
    it('should return T+1 for weekday trade', () => {
      const tradeDate = new Date('2025-01-01') // Wednesday
      const settlementDate = getSettlementDate(tradeDate)

      expect(settlementDate.getDate()).toBe(2) // Thursday
    })

    it('should skip weekend for Friday trade', () => {
      const tradeDate = new Date('2025-01-03') // Friday
      const settlementDate = getSettlementDate(tradeDate)

      expect(settlementDate.getDate()).toBe(6) // Monday (skip Sat/Sun)
    })
  })
})
```

### 8.2 Vue Test Utils Component Testing

```typescript
// StockList.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StockList from '@/components/StockList.vue'
import type { StockPrice } from '@/types/market'

describe('StockList', () => {
  const mockStocks: StockPrice[] = [
    {
      symbol: '000001',
      name: '平安银行',
      price: 10.50,
      prevClose: 10.00,
      change: 0.50,
      changePercent: 5.0,
      open: 10.10,
      high: 10.60,
      low: 10.00,
      volume: 1000000,
      amount: 10500000,
      timestamp: '2025-01-01T15:00:00Z'
    }
  ]

  it('renders stock list correctly', () => {
    const wrapper = mount(StockList, {
      props: { stocks: mockStocks }
    })

    expect(wrapper.find('.stock-symbol').text()).toBe('000001')
    expect(wrapper.find('.stock-name').text()).toBe('平安银行')
  })

  it('applies correct color classes for A股 (RED=UP, GREEN=DOWN)', () => {
    const wrapper = mount(StockList, {
      props: { stocks: mockStocks }
    })

    const priceElement = wrapper.find('.stock-price')
    expect(priceElement.classes()).toContain('market-up') // RED for +5%
  })

  it('emits select-stock event when clicked', async () => {
    const wrapper = mount(StockList, {
      props: { stocks: mockStocks }
    })

    await wrapper.find('.stock-row').trigger('click')

    expect(wrapper.emitted('select-stock')).toBeTruthy()
    expect(wrapper.emitted('select-stock')![0]).toEqual(['000001'])
  })
})
```

### 8.3 Playwright E2E Testing

**playwright.config.ts**:

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './test/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3020',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3020',
    reuseExistingServer: !process.env.CI,
  },
})
```

**Example E2E test** - `kline-chart.spec.ts`:

```typescript
import { test, expect } from '@playwright/test'

test.describe('ProKLineChart', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/stock-detail/000001')
  })

  test('should render K-line chart with A股 colors', async ({ page }) => {
    // Wait for chart to load
    await page.waitForSelector('.pro-kline-chart canvas')

    // Verify chart exists
    const chart = page.locator('.pro-kline-chart')
    await expect(chart).toBeVisible()
  })

  test('should switch period and reload data', async ({ page }) => {
    // Click on 1周 period button
    await page.click('button:has-text("1周")')

    // Wait for data reload
    await page.waitForTimeout(500)

    // Verify chart updated
    const chart = page.locator('.pro-kline-chart')
    await expect(chart).toBeVisible()
  })

  test('should toggle indicators', async ({ page }) => {
    // Click indicator dropdown
    await page.click('button:has-text("指标")')

    // Select MACD
    await page.click('text=MACD')

    // Verify MACD indicator is displayed
    await expect(page.locator('.indicator-macd')).toBeVisible()
  })

  test('should display A股 color scheme correctly', async ({ page }) => {
    // Check chart styles
    const chartStyles = await page.locator('.pro-kline-chart canvas')
      .evaluate(el => {
        const styles = window.getComputedStyle(el)
        return {
          upColor: styles.getPropertyValue('--color-market-up'),
          downColor: styles.getPropertyValue('--color-market-down')
        }
      })

    // Verify RED=UP, GREEN=DOWN for A股
    expect(chartStyles.upColor).toContain('255, 82, 82') // RED
    expect(chartStyles.downColor).toContain('0, 230, 118') // GREEN
  })
})
```

---

## 9. Build & Deployment

### 9.1 Production Build Optimization

**Update** `package.json` scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "build:analyze": "vite build --mode analyze",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "lint": "eslint . --ext .vue,.js,.ts,.jsx,.tsx --fix"
  }
}
```

**Bundle analysis**:

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
})
```

### 9.2 Docker Deployment

**Dockerfile**:

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf**:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://backend:8020;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

---

## 10. Summary and Recommendations

### Critical Must-Fix Before Approval

1. ✅ **Fix A股 color convention** (RED=UP, GREEN=DOWN)
   - Update all color definitions in proposal
   - Update all component examples
   - Add color convention documentation

2. ✅ **Add comprehensive A股 trading rules**
   - 涨跌停 detection and display
   - T+1 settlement date calculation
   - 100股 lot size validation
   - Trading hours display

3. ✅ **Port configuration**
   - Frontend: 3020-3029 (update vite.config.ts)
   - Backend: 8020-8029 (update proxy target)

### High Priority Recommendations

4. ✅ **TypeScript strict mode migration plan**
   - Start with `strict: false`, gradually enable checks
   - Document strict mode rollout timeline

5. ✅ **Mobile responsive patterns**
   - Card-based tables for small screens
   - Bottom navigation for phones
   - Touch-optimized interactions

6. ✅ **Error state designs**
   - Loading states with skeleton screens
   - Error states with retry actions
   - Empty states with guidance

7. ✅ **Performance budget enforcement**
   - Bundle size limits
   - Lighthouse CI integration
   - Core Web Vitals monitoring

### Code Quality Recommendations

8. ✅ **Add comprehensive testing**
   - Unit tests for utilities (80%+ coverage)
   - Component tests for UI
   - E2E tests for critical user flows

9. ✅ **Implement error boundaries**
   - Vue error handling components
   - Sentry integration for error tracking
   - User-friendly error messages

10. ✅ **Accessibility enhancements**
    - High contrast mode support
    - Screen reader testing
    - Keyboard navigation audit

---

## Approval Status

**Current Status**: ❌ **REQUIRES CRITICAL BUG FIXES**

**Must Fix**:
1. A股 color convention error (RED=UP, GREEN=DOWN)

**After Fix**: ✅ **APPROVE WITH HIGH PRIORITY RECOMMENDATIONS**

The proposal demonstrates solid technical planning and comprehensive scope. The A股 color bug is critical but easily fixed. All other issues are enhancements that can be addressed during implementation.

---

**Review Completed**: 2025-12-26
**Reviewer**: Claude Code (Frontend Development Specialist)
**Next Steps**: Fix A股 color conventions, update proposal documents, begin implementation
