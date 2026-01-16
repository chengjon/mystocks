# Design: Frontend Framework Six-Phase Optimization

**Change ID**: `frontend-optimization-six-phase`
**Status**: Draft
**Last Updated**: 2025-12-26

---

## Architecture Overview

This document describes the architectural design for integrating two complementary frontend approaches into a unified, incrementally-implementable optimization plan.

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Framework A (Current)                   │
├─────────────────────────────────────────────────────────────┤
│  Vue 3.4 + JavaScript + Element Plus 2.8                   │
│  - 81 Vue components (mixed JS/TS)                         │
│  - 30+ pages with basic theming                            │
│  - ECharts 5.5 for visualization                          │
│  - klinecharts 9.6.0 (basic usage)                        │
│  - FastAPI backend integration                            │
└─────────────────────────────────────────────────────────────┘
```

### Target Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Optimized Framework A                        │
├──────────────────────────────────────────────────────────────────┤
│  Vue 3.4 + TypeScript (gradual) + Element Plus 2.8 (enhanced)    │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  UI/UX Layer     │  │  Chart Layer    │  │  AI Layer       │  │
│  │  (Phase 1)      │  │  (Phase 3-4)    │  │  (Phase 5)      │  │
│  │  - Dark Theme   │  │  - ProKLineChart│  │  - Query Engine │  │
│  │  - 5 Layouts    │  │  - 161 Indicators│ │  - Smart Recs   │  │
│  │  - Responsive  │  │  - A股 Rules    │  │  - NL Parsing   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Type Safety Layer (Phase 2)                   │  │
│  │  - Shared type definitions                               │  │
│  │  - Mixed JS/TS environment                               │  │
│  │  - Gradual component migration                           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │         Performance Monitoring (Phase 6)                   │  │
│  │  - GPU status dashboard                                   │  │
│  │  - Core Web Vitals tracking                               │  │
│  │  - Optimization suggestions                               │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Backend Integration: FastAPI (unchanged) + GPU Backend          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Design Decisions

### 1. Incremental TypeScript Migration

**Decision**: Allow JavaScript and TypeScript to coexist during migration period.

**Rationale**:
- Avoids big-bang rewrite risk
- Enables gradual learning curve for team
- Allows continuous delivery during migration
- Component-by-component migration reduces complexity

**Initial Configuration** (Week 1-2):

```json
// tsconfig.json (Phase 1: Loose configuration)
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
    "strict": false,              // ❌ Start loose
    "noUnusedLocals": false,      // ❌ Enable later
    "noUnusedParameters": false,  // ❌ Enable later
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

```json
// tsconfig.node.json (for Vite config)
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

**Strict Mode Rollout Timeline**:

```markdown
## Phase 1 (Week 1-2): Foundation
- ✅ strict: false
- ✅ noUnusedLocals: false
- ✅ noUnusedParameters: false
- **Goal**: Get TypeScript compiling without blocking migration

## Phase 2 (Week 3-4): Basic Type Safety
- ✅ strict: true
  - strictNullChecks: true
  - noImplicitAny: true
- ❌ noUnusedLocals: false (still off)
- ❌ noUnusedParameters: false (still off)
- **Goal**: Catch common type errors while staying flexible

## Phase 3 (Week 5-6): Enhanced Checks
- ✅ strict: true (all options)
- ✅ noUnusedLocals: true
- ❌ noUnusedParameters: false (enable in Phase 4)
- **Goal**: Enforce cleaner code, remove unused variables

## Phase 4 (Week 7-8): Full Strict Mode
- ✅ strict: true (all options)
- ✅ noUnusedLocals: true
- ✅ noUnusedParameters: true
- ✅ noImplicitReturns: true
- ✅ noUncheckedIndexedAccess: true
- **Goal**: Maximum type safety and code quality

## Phase 5 (Week 9+): Advanced Options (Optional)
- ✅ noPropertyAccessFromIndexSignature: true
- ✅ exactOptionalPropertyTypes: true
- **Goal**: Enforce stricter property access patterns
```

**Migration Strategy**:
1. **Start with new components written in TypeScript** (Week 1-2)
   - Create `ProKLineChart.vue` as first TypeScript component
   - Define types in `src/types/` directory
   - Use composition API with `<script setup lang="ts">`

2. **Migrate high-value components first** (Week 3-6)
   - Priority order:
     - `Dashboard.vue` → TypeScript
     - `Market.vue` → TypeScript
     - `StockDetail.vue` → TypeScript
     - `StrategyManagement.vue` → TypeScript
     - `BacktestAnalysis.vue` → TypeScript
     - `TechnicalAnalysis.vue` → TypeScript
     - `IndicatorLibrary.vue` → TypeScript

3. **Create shared type library** (Week 1-4)
   - `src/types/stock.ts` - Stock data types
   - `src/types/market.ts` - Market data types
   - `src/types/strategy.ts` - Strategy types
   - `src/types/backtest.ts` - Backtest types
   - `src/types/api.ts` - API request/response types

4. **Gradually increase strictness** (Follow Phase 1-5 timeline above)
   - Start with `strict: false`
   - Enable checks incrementally
   - Fix type errors phase by phase
   - Document migration progress

**Type Definition Library** (create in Week 1-2):

```typescript
// src/types/stock.ts
export interface Stock {
  code: string           // 股票代码 (e.g., "600519.SH")
  name: string           // 股票名称 (e.g., "贵州茅台")
  market: MarketType     // 市场类型
  sector?: string        // 行业
  listDate?: Date        // 上市日期
}

export type MarketType = 'SH' | 'SZ' | 'BJ'

export interface StockPrice {
  code: string
  name: string
  price: number          // 当前价
  prevClose: number      // 昨收价
  open: number           // 今开价
  high: number           // 最高价
  low: number            // 最低价
  volume: number         // 成交量
  amount: number         // 成交额
  change: number         // 涨跌额
  changePercent: number  // 涨跌幅
  timestamp: Date
}

export interface OHLCV {
  timestamp: Date
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount?: number
}

export interface StockRealtime extends StockPrice {
  bidPrice?: number[]      // 买盘价 [买一, 买二, ...]
  bidVolume?: number[]     // 买盘量
  askPrice?: number[]      // 卖盘价
  askVolume?: number[]     // 卖盘量
}

export type PriceLimitType = 'regular' | 'st' | 'chinext' | 'star' | 'ipo'

export interface PriceLimitConfig {
  limitUp: number          // 涨停价
  limitDown: number        // 跌停价
  currentPrice: number
  limitType: PriceLimitType
}
```

**Trade-offs**:
- ✅ Pros: Lower risk, continuous delivery, flexible timeline
- ❌ Cons: Longer migration period (9-12 weeks), potential type inconsistencies during transition

**Success Criteria**:
- All new components written in TypeScript from Week 2 onwards
- 80% of existing components migrated by Week 8
- Full strict mode enabled by Week 8
- Zero runtime type errors in production

### 2. Dark Theme Color System

**Decision**: Adopt Framework B's Bloomberg/Wind-style professional color palette.

**Rationale**:
- Financial trading terminals use dark themes for reduced eye strain
- Professional aesthetics improve user trust
- High contrast colors (亮绿/亮红) align with A股 conventions
- Industry-standard design patterns

**Color Palette**:

```scss
:root {
  // Backgrounds - Deep Blue-Black System
  --bg-primary: #0B0F19;        // Main background - extremely deep
  --bg-secondary: #1A1F2E;      // Secondary - deep blue-gray
  --bg-card: #232936;           // Card background - medium
  --bg-hover: #2D3446;          // Hover state

  // A股 Market Colors (RED=UP, GREEN=DOWN)
  --color-up: #FF5252;          // Up - bright RED (上涨) 涨
  --color-down: #00E676;        // Down - bright GREEN (下跌) 跌
  --color-flat: #B0B3B8;        // Flat - gray (平盘) 平

  // Accent Colors
  --color-primary: #2979FF;     // Primary - professional blue
  --color-success: #00C853;     // Success
  --color-warning: #FFAB00;     // Warning
  --color-danger: #FF1744;      // Danger

  // Text Colors
  --text-primary: #FFFFFF;      // Primary text - pure white
  --text-secondary: #B0B3B8;    // Secondary - light gray
  --text-tertiary: #7A7E85;     // Tertiary - dark gray
  --text-disabled: #4A4E55;     // Disabled - darker gray
}
```

**Accessibility Considerations**:
- WCAG 2.1 AA compliance: 4.5:1 contrast ratio for text
- Test with screen readers
- Support high-contrast mode preference
- Avoid color-only information conveyance

### 3. Professional K-line Chart Architecture

**Decision**: Enhance existing klinecharts 9.6.0 with lightweight-charts features and A股-specific functionality.

**Rationale**:
- klinecharts already installed and working
- Lightweight Charts provides advanced rendering performance
- A股 has unique requirements (涨跌停, T+1, lot sizes)
- Custom components allow full control over features

**Component Architecture**:

```typescript
// ProKLineChart.vue
<template>
  <div class="pro-kline-chart" ref="chartContainer">
    <!-- Main chart area -->
    <!-- Volume indicators -->
    <!-- Technical indicator overlays -->
    <!-- Toolbar for period/indicator selection -->
  </div>
</template>

<script lang="ts">
import { init, dispose } from 'klinecharts'
import { TechnicalIndicators } from '@/utils/indicators'
import type { KLineData, IndicatorConfig } from '@/types/market'

export default defineComponent({
  name: 'ProKLineChart',
  props: {
    symbol: String,
    periods: Array<string>,
    indicators: Array<string>
  },
  setup(props) {
    // Chart initialization
    // Data loading from API
    // A股-specific features (涨跌停 marks, 前复权)
    // Technical indicator rendering
  }
})
</script>
```

**A股-Specific Features**:
1. **涨跌停 Markers**: Visual indicators when price hits +/-10% or +/-20% limits
2. **前复权/后复权**: Adjust historical prices for splits/dividends
3. **T+1 Indicator**: Show settlement date markers
4. **100股 Lot Sizes**: Display quantities in standard lots
5. **Trading Hours**: Highlight pre-market (9:15-9:25) and auction periods

**Performance Optimizations**:
- Canvas-based rendering (60fps)
- Data downsampling for large datasets
- Lazy loading for historical data
- Web Workers for indicator calculations

### 4. Technical Indicator Library

**Decision**: Combine npm `technicalindicators` package with custom implementations for 161 total indicators.

**Rationale**:
- `technicalindicators` provides 70+ battle-tested indicators
- Custom implementations needed for A股-specific patterns
- Unified interface via abstraction layer
- Performance-critical code requires optimization

**Architecture**:

```typescript
// src/utils/indicator-library.ts
export class IndicatorLibrary {
  private indicators: Map<string, Indicator> = new Map()

  constructor() {
    // Register npm package indicators (70+)
    this.registerNpmIndicators()

    // Register custom indicators (91)
    this.registerCustomIndicators()
  }

  calculate(name: string, data: number[], params?: any): number[] {
    const indicator = this.indicators.get(name.toUpperCase())
    if (!indicator) {
      throw new Error(`Indicator ${name} not found`)
    }
    return indicator.calculate(data, params)
  }
}

// Category breakdown:
export const INDICATOR_CATEGORIES = {
  TREND: 45,      // SMA, EMA, MACD, etc.
  MOMENTUM: 38,   // RSI, STOCH, CCI, etc.
  VOLATILITY: 26, // BB, ATR, KELTNER, etc.
  VOLUME: 22,     // OBV, AD, CMF, etc.
  PATTERN: 30     // DOJI, HAMMER, ENGULFING, etc.
}
```

**Performance Considerations**:
- Cache indicator calculations for repeated calls
- Use Web Workers for heavy computations
- Batch calculate multiple indicators in single pass
- GPU acceleration for large datasets (via cuDF backend)

### 5. Natural Language Query Engine

**Decision**: Pattern-matching based parser with AI fallback for complex queries.

**Rationale**:
- Pattern matching covers 80%+ common queries
- Deterministic and fast (< 500ms)
- AI fallback handles edge cases
- Cost-effective (reduced API calls)

**Architecture**:

```typescript
// src/services/WencaiQueryEngine.ts
export class WencaiQueryEngine {
  // Predefined patterns (90%+ coverage)
  private patterns: QueryPattern[] = [
    {
      pattern: /连续(\d+)天上涨/,
      sqlTemplate: 'SELECT * FROM stocks WHERE change_pct > 0 GROUP BY symbol HAVING COUNT(*) >= {days}'
    },
    {
      pattern: /今日强势股|今日涨停/,
      sqlTemplate: 'SELECT * FROM stocks WHERE change_pct >= 9.8 AND date = today'
    },
    {
      pattern: /MACD金叉/,
      sqlTemplate: 'SELECT * FROM indicators WHERE macd_diff > 0 AND macd_diff_prev <= 0'
    }
    // ... 9 predefined templates
  ]

  async parseQuery(query: string): Promise<QueryResult> {
    // 1. Try pattern matching first
    for (const { pattern, sqlTemplate } of this.patterns) {
      const match = query.match(pattern)
      if (match) {
        return {
          sql: this.buildSQL(sqlTemplate, match),
          confidence: 0.9,
          method: 'pattern'
        }
      }
    }

    // 2. Fallback to AI semantic understanding
    return await this.fallbackToAI(query)
  }
}
```

**9 Predefined Templates**:
1. "连续N天上涨/下跌"
2. "今日强势股/涨停"
3. "低估值高成长"
4. "高成交量突破"
5. "技术指标金叉/死叉"
6. "主力资金流入"
7. "热点板块龙头"
8. "突破新高"
9. "回调企稳"

**AI Fallback Integration**:
- OpenAI GPT-4 API for semantic parsing
- Cache results for repeated queries
- Rate limiting and cost monitoring
- Confidence scoring below 0.7 triggers manual review

### 6. GPU Acceleration Monitoring

**Decision**: Frontend dashboard components for existing GPU backend (no backend changes).

**Rationale**:
- GPU backend already implemented (Phase 6.4 completed)
- Frontend needs real-time visibility into GPU operations
- Performance optimization requires monitoring
- Debugging GPU issues benefits from visual feedback

**Dashboard Architecture**:

```vue
<!-- BacktestGPU.vue -->
<template>
  <div class="backtest-gpu">
    <!-- GPU Status Card -->
    <el-card class="gpu-monitor">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="metric">
            <span class="label">GPU利用率</span>
            <el-progress :percentage="gpuUtilization" />
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric">
            <span class="label">显存使用</span>
            <el-progress :percentage="memoryUsage" />
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric">
            <span class="label">温度</span>
            <span class="value">{{ gpuTemp }}°C</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric">
            <span class="label">加速比</span>
            <span class="value">{{ accelerationRatio }}x</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Backtest Configuration & Results -->
    <!-- Preserved from existing framework A -->
  </div>
</template>

<script lang="ts">
export default defineComponent({
  name: 'BacktestGPU',
  setup() {
    // Poll GPU status every 1 second
    const gpuUtilization = ref(0)
    const memoryUsage = ref(0)
    const gpuTemp = ref(0)
    const accelerationRatio = ref(0)

    setInterval(async () => {
      const response = await fetch('/api/backtest/gpu-status')
      const status = await response.json()

      gpuUtilization.value = status.utilization
      memoryUsage.value = status.memoryUsage
      gpuTemp.value = status.temperature
      accelerationRatio.value = status.accelerationRatio
    }, 1000)

    return { gpuUtilization, memoryUsage, gpuTemp, accelerationRatio }
  }
})
</script>
```

**Performance Metrics Tracked**:
- GPU utilization percentage
- Memory usage (VRAM)
- Temperature (°C)
- Acceleration ratio (vs CPU)
- Task queue depth
- Error rates and fallbacks

**Intelligent Suggestions**:
- "GPU available for this task" → Enable GPU button
- "Memory usage high, consider clearing cache"
- "Temperature critical (85°C+), throttling imminent"
- "CPU fallback recommended for small datasets (< 1000 rows)"

### 7. Mobile Responsive Design Patterns

**Decision**: Implement mobile-first responsive design with touch-optimized interactions.

**Key Requirements**:

1. **Breakpoint System**
```scss
// styles/breakpoints.scss
$breakpoint-xs: 0px;       // Extra small phones (< 576px)
$breakpoint-sm: 576px;     // Small phones (≥ 576px)
$breakpoint-md: 768px;     // Tablets (≥ 768px)
$breakpoint-lg: 992px;     // Small laptops (≥ 992px)
$breakpoint-xl: 1200px;    // Desktops (≥ 1200px)
$breakpoint-xxl: 1400px;   // Large desktops (≥ 1400px)

// Mobile-first mixins
@mixin mobile-up {
  @media (min-width: $breakpoint-sm) { @content; }
}

@mixin tablet-up {
  @media (min-width: $breakpoint-md) { @content; }
}

@mixin desktop-up {
  @media (min-width: $breakpoint-lg) { @content; }
}
```

2. **Card-Based Tables for Small Screens**
```vue
<!-- MobileStockTable.vue -->
<template>
  <!-- Desktop view: Standard table -->
  <el-table
    v-if="!isMobile"
    :data="stocks"
    class="stock-table-desktop"
  >
    <el-table-column prop="code" label="代码" width="100" />
    <el-table-column prop="name" label="名称" width="150" />
    <el-table-column prop="price" label="价格" width="100">
      <template #default="{ row }">
        <span :class="getPriceClass(row)">
          {{ row.price }}
        </span>
      </template>
    </el-table-column>
    <el-table-column prop="changePercent" label="涨跌幅" width="100">
      <template #default="{ row }">
        <span :class="getChangeClass(row)">
          {{ row.changePercent }}%
        </span>
      </template>
    </el-table-column>
    <el-table-column prop="volume" label="成交量" />
  </el-table>

  <!-- Mobile view: Card-based layout -->
  <div v-else class="stock-cards-mobile">
    <el-card
      v-for="stock in stocks"
      :key="stock.code"
      class="stock-card"
      shadow="hover"
      @click="viewStockDetail(stock)"
    >
      <div class="stock-header">
        <span class="stock-code">{{ stock.code }}</span>
        <span class="stock-name">{{ stock.name }}</span>
      </div>

      <div class="stock-metrics">
        <div class="metric">
          <span class="label">现价</span>
          <span :class="['value', getPriceClass(stock)]">
            {{ stock.price }}
          </span>
        </div>

        <div class="metric">
          <span class="label">涨跌幅</span>
          <span :class="['value', getChangeClass(stock)]">
            {{ stock.changePercent }}%
          </span>
        </div>

        <div class="metric">
          <span class="label">成交量</span>
          <span class="value">{{ stock.volume }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useBreakpoints } from '@vueuse/core'

const breakpoints = useBreakpoints({
  mobile: 768,
  tablet: 992,
  desktop: 1200
})

const isMobile = breakpoints.smaller('mobile')

function getPriceClass(stock: Stock): string {
  if (stock.changePercent > 0) return 'market-up'
  if (stock.changePercent < 0) return 'market-down'
  return 'market-flat'
}

function getChangeClass(stock: Stock): string {
  return getPriceClass(stock)
}
</script>

<style scoped lang="scss">
.stock-table-desktop {
  // Desktop table styles
  width: 100%;

  @include mobile-down {
    display: none;
  }
}

.stock-cards-mobile {
  // Mobile card layout
  display: grid;
  gap: 12px;

  @include tablet-up {
    display: none;
  }
}

.stock-card {
  cursor: pointer;
  transition: transform 0.2s;

  &:active {
    transform: scale(0.98);
  }
}

.stock-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-base);
}

.stock-code {
  font-weight: 600;
  font-size: 16px;
}

.stock-name {
  color: var(--text-secondary);
}

.stock-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;

  .label {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-bottom: 4px;
  }

  .value {
    font-size: 14px;
    font-weight: 600;
  }
}

.market-up { color: var(--color-market-up); }    /* RED for 涨 */
.market-down { color: var(--color-market-down); }  /* GREEN for 跌 */
.market-flat { color: var(--color-market-flat); }  /* GRAY for 平 */
</style>
```

3. **Bottom Navigation for Phones**
```vue
<!-- MobileBottomNav.vue -->
<template>
  <el-tab-bar
    v-if="isMobile"
    v-model="activeTab"
    class="mobile-bottom-nav"
    @tab-change="handleTabChange"
  >
    <el-tab-item name="market">
      <template #icon>
        <el-icon><TrendCharts /></el-icon>
      </template>
      行情
    </el-tab-item>

    <el-tab-item name="portfolio">
      <template #icon>
        <el-icon><Wallet /></el-icon>
      </template>
      持仓
    </el-tab-item>

    <el-tab-item name="strategy">
      <template #icon>
        <el-icon><DataAnalysis /></el-icon>
      </template>
      策略
    </el-tab-item>

    <el-tab-item name="profile">
      <template #icon>
        <el-icon><User /></el-icon>
      </template>
      我的
    </el-tab-item>
  </el-tab-bar>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBreakpoints } from '@vueuse/core'

const breakpoints = useBreakpoints({
  mobile: 768
})

const isMobile = breakpoints.smaller('mobile')
const router = useRouter()
const activeTab = ref('market')

function handleTabChange(tabName: string) {
  router.push({ name: tabName })
}
</script>

<style scoped lang="scss">
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom); // iOS safe area

  @include tablet-up {
    display: none;
  }
}
</style>
```

4. **Touch-Optimized Interactions**
```scss
// styles/touch-optimizations.scss
// Increase tap target size for touch devices
@media (hover: none) and (pointer: coarse) {
  // Buttons
  .el-button {
    min-height: 44px;  // iOS recommended minimum
    min-width: 44px;
    padding: 12px 20px;
  }

  // Form inputs
  .el-input__inner {
    min-height: 44px;
    font-size: 16px;  // Prevent iOS auto-zoom
  }

  // Table rows
  .el-table__row {
    min-height: 48px;
  }

  // Card click targets
  .el-card {
    cursor: pointer;

    &:active {
      opacity: 0.8;
      transform: scale(0.98);
    }
  }

  // Remove hover effects on touch devices
  .el-button:hover,
  .el-card:hover {
    background-color: initial;  // Use active state instead
  }
}
```

### 8. Error State and Loading Designs

**Decision**: Implement comprehensive loading, error, and empty states for better UX.

**1. Loading States with Skeleton Screens**
```vue
<!-- StockTableSkeleton.vue -->
<template>
  <div class="stock-table-skeleton">
    <!-- Header skeleton -->
    <el-skeleton
      :rows="1"
      animated
      class="skeleton-header"
    />

    <!-- Body skeleton -->
    <el-skeleton
      :rows="10"
      animated
      :loading="true"
    >
      <template #template>
        <div
          v-for="i in 10"
          :key="i"
          class="skeleton-row"
        >
          <el-skeleton-item variant="text" style="width: 100px" />
          <el-skeleton-item variant="text" style="width: 150px" />
          <el-skeleton-item variant="text" style="width: 100px" />
          <el-skeleton-item variant="text" style="width: 100px" />
          <el-skeleton-item variant="text" style="width: 120px" />
        </div>
      </template>
    </el-skeleton>
  </div>
</template>

<style scoped lang="scss">
.stock-table-skeleton {
  padding: 20px;
}

.skeleton-header {
  margin-bottom: 20px;
}

.skeleton-row {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
}
</style>
```

**2. Error States with Retry Actions**
```vue
<!-- ErrorState.vue -->
<template>
  <el-result
    :icon="errorType"
    :title="errorTitle"
    :sub-title="errorMessage"
  >
    <template #extra>
      <el-button type="primary" @click="handleRetry">
        <el-icon><Refresh /></el-icon>
        重试
      </el-button>

      <el-button @click="handleGoHome">
        <el-icon><HomeFilled /></el-icon>
        返回首页
      </el-button>
    </template>

    <template #sub-title v-if="showDetails">
      <el-collapse class="error-details">
        <el-collapse-item title="错误详情" name="details">
          <pre class="error-stack">{{ errorStack }}</pre>
        </el-collapse-item>
      </el-collapse>
    </template>
  </el-result>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  errorType?: 'error' | 'warning' | 'info'
  errorTitle?: string
  errorMessage?: string
  errorStack?: string
  showDetails?: boolean
  retryAction?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  errorType: 'error',
  errorTitle: '加载失败',
  errorMessage: '请检查网络连接后重试',
  showDetails: false
})

const emit = defineEmits<{
  retry: []
  goHome: []
}>()

const router = useRouter()

function handleRetry() {
  if (props.retryAction) {
    props.retryAction()
  } else {
    emit('retry')
  }
}

function handleGoHome() {
  router.push({ name: 'home' })
  emit('goHome')
}
</script>

<style scoped lang="scss">
.error-details {
  margin-top: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.error-stack {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}
</style>
```

**3. Empty States with Guidance**
```vue
<!-- EmptyState.vue -->
<template>
  <el-empty
    :image="emptyImage"
    :image-size="200"
    :description="emptyDescription"
  >
    <template #description>
      <p class="empty-title">{{ emptyTitle }}</p>
      <p class="empty-description">{{ emptyDescription }}</p>
    </template>

    <template #default>
      <el-button
        v-if="actionButton"
        type="primary"
        @click="handleAction"
      >
        <el-icon>
          <component :is="actionIcon" />
        </el-icon>
        {{ actionButton }}
      </el-button>
    </template>
  </el-empty>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  DocumentAdd,
  Search,
  ShoppingCart,
  DataLine
} from '@element-plus/icons-vue'

interface Props {
  type?: 'no-data' | 'no-search-results' | 'no-position' | 'no-strategy'
  title?: string
  description?: string
  actionButton?: string
  actionIcon?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'no-data'
})

const emit = defineEmits<{
  action: []
}>()

const emptyConfigs = {
  'no-data': {
    title: '暂无数据',
    description: '请先添加数据或刷新页面',
    actionButton: '添加数据',
    actionIcon: DocumentAdd
  },
  'no-search-results': {
    title: '未找到相关结果',
    description: '请尝试使用其他关键词搜索',
    actionButton: '清除筛选',
    actionIcon: Search
  },
  'no-position': {
    title: '暂无持仓',
    description: '您还没有持有任何股票',
    actionButton: '去交易',
    actionIcon: ShoppingCart
  },
  'no-strategy': {
    title: '暂无策略',
    description: '创建您的第一个量化交易策略',
    actionButton: '创建策略',
    actionIcon: DataLine
  }
}

const config = computed(() => emptyConfigs[props.type])
const emptyTitle = computed(() => props.title || config.value.title)
const emptyDescription = computed(() => props.description || config.value.description)
const actionButton = computed(() => props.actionButton || config.value.actionButton)
const actionIcon = computed(() => props.actionIcon || config.value.actionIcon)

function handleAction() {
  emit('action')
}
</script>

<style scoped lang="scss">
.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
```

---

## A股 Market-Specific Requirements

### Critical A股 Trading Rules

**Decision**: Implement A股-specific trading logic to ensure compliance with Chinese market regulations.

**Key Requirements**:

1. **涨跌停 (Price Limits) Detection and Display**
   - 主板 (Main Board): ±10% daily limit
   - 创业板/科创板 (ChiNext/STAR): ±20% daily limit
   - ST股票 (Special Treatment): ±5% daily limit
   - 新股 (IPO): First 5 days no limit (44% for regular stocks)

```typescript
// utils/aStockLimits.ts
export interface PriceLimitConfig {
  limitUp: number;      // 涨停价
  limitDown: number;    // 跌停价
  currentPrice: number;
  limitType: 'regular' | 'st' | 'chinext' | 'star' | 'ipo';
}

export function calculatePriceLimits(
  prevClose: number,
  limitType: 'regular' | 'st' | 'chinext' | 'star' | 'ipo' = 'regular'
): PriceLimitConfig {
  const limitPercent = {
    regular: 0.10,
    st: 0.05,
    chnext: 0.20,
    star: 0.20,
    ipo: 0.44
  }[limitType];

  return {
    limitUp: parseFloat((prevClose * (1 + limitPercent)).toFixed(2)),
    limitDown: parseFloat((prevClose * (1 - limitPercent)).toFixed(2)),
    currentPrice: prevClose,
    limitType
  };
}

export function isLimitUp(price: number, limitConfig: PriceLimitConfig): boolean {
  return Math.abs(price - limitConfig.limitUp) < 0.01;
}

export function isLimitDown(price: number, limitConfig: PriceLimitConfig): boolean {
  return Math.abs(price - limitConfig.limitDown) < 0.01;
}
```

2. **T+1 Settlement Date Calculation**

```typescript
// utils/t1Settlement.ts
export function calculateSettlementDate(tradeDate: Date): Date {
  // T+1: Settlement on the next trading day
  const settlementDate = new Date(tradeDate);
  settlementDate.setDate(settlementDate.getDate() + 1);

  // Skip weekends (Saturday = 6, Sunday = 0)
  while (settlementDate.getDay() === 0 || settlementDate.getDay() === 6) {
    settlementDate.setDate(settlementDate.getDate() + 1);
  }

  // TODO: Add holiday calendar lookup for Chinese holidays
  // This requires a holiday API or local database

  return settlementDate;
}

export function canSellToday(tradeDate: Date, positionDate: Date): boolean {
  // T+1 rule: Can only sell stocks bought yesterday or earlier
  const today = new Date();
  const settlementDate = calculateSettlementDate(positionDate);

  return today >= settlementDate;
}
```

3. **100股 Lot Size Validation**

```typescript
// utils/lotSizeValidation.ts
export const MIN_LOT_SIZE = 100; // 1手 = 100股

export function validateLotSize(quantity: number): {
  isValid: boolean;
  message?: string;
  suggestedQuantity?: number;
} {
  if (quantity % MIN_LOT_SIZE !== 0) {
    const suggestedQuantity = Math.ceil(quantity / MIN_LOT_SIZE) * MIN_LOT_SIZE;
    return {
      isValid: false,
      message: `A股交易必须是100股的整数倍。建议买入: ${suggestedQuantity}股`,
      suggestedQuantity
    };
  }

  return { isValid: true };
}

export function calculateMaxBuyableLots(
  availableCapital: number,
  price: number
): number {
  const maxShares = Math.floor(availableCapital / price);
  const maxLots = Math.floor(maxShares / MIN_LOT_SIZE);

  return maxLots * MIN_LOT_SIZE;
}
```

4. **Trading Hours Display**

```typescript
// utils/tradingHours.ts
export interface TradingSession {
  name: string;
  startTime: string; // HH:mm format
  endTime: string;
  isOpen: boolean;
}

export function getCurrentTradingSession(): TradingSession | null {
  const now = new Date();
  const currentTime = now.getHours() * 60 + now.getMinutes();
  const dayOfWeek = now.getDay();

  // Weekend check
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    return null;
  }

  // Morning session: 9:30-11:30
  const morningStart = 9 * 60 + 30; // 9:30
  const morningEnd = 11 * 60 + 30;   // 11:30

  // Afternoon session: 13:00-15:00
  const afternoonStart = 13 * 60;    // 13:00
  const afternoonEnd = 15 * 60;      // 15:00

  if (currentTime >= morningStart && currentTime <= morningEnd) {
    return {
      name: '早盘',
      startTime: '09:30',
      endTime: '11:30',
      isOpen: true
    };
  } else if (currentTime >= afternoonStart && currentTime <= afternoonEnd) {
    return {
      name: '午盘',
      startTime: '13:00',
      endTime: '15:00',
      isOpen: true
    };
  }

  return null;
}

export function getNextTradingSession(): TradingSession {
  const now = new Date();
  const currentTime = now.getHours() * 60 + now.getMinutes();
  const morningStart = 9 * 60 + 30;

  if (currentTime < morningStart) {
    return {
      name: '早盘',
      startTime: '09:30',
      endTime: '11:30',
      isOpen: false
    };
  }

  return {
    name: '午盘',
    startTime: '13:00',
    endTime: '15:00',
    isOpen: false
  };
}
```

### A股 Color Convention (CRITICAL)

**IMPORTANT**: 中国A股市场使用 **红涨绿跌** 颜色约定,与国际市场相反。

```scss
// ✅ CORRECT: A股 Market Colors (RED=UP, GREEN=DOWN)
:root {
  // Market colors (A股专用)
  --color-market-up: #FF5252;      // 涨 (RED)
  --color-market-down: #00E676;    // 跌 (GREEN)
  --color-market-flat: #B0B3B8;    // 平 (GRAY)

  // Semantic UI colors (国际标准 - 与市场颜色分离)
  --color-success: #00C853;        // 操作成功 (green)
  --color-danger: #FF1744;         // 危险/错误 (red)
  --color-warning: #FFAB00;        // 警告 (amber)
  --color-info: #00B0FF;           // 信息 (blue)
}
```

**Usage Example**:
```vue
<template>
  <!-- ✅ Use market colors for price changes -->
  <span :class="priceClass" class="price-display">
    {{ price }}
    <span class="change-percent">{{ changePercent }}%</span>
  </span>

  <!-- ✅ Use semantic colors for UI states -->
  <el-alert type="success" v-if="orderSuccessful">
    订单提交成功
  </el-alert>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const priceClass = computed(() => {
  if (changePercent.value > 0) return 'market-up'    // RED for 涨
  if (changePercent.value < 0) return 'market-down'  // GREEN for 跌
  return 'market-flat'  // GRAY for 平
})
</script>

<style scoped>
.price-display.market-up { color: var(--color-market-up); }    /* RED */
.price-display.market-down { color: var(--color-market-down); }  /* GREEN */
.price-display.market-flat { color: var(--color-market-flat); }  /* GRAY */
</style>
```

### Port Configuration

**Decision**: Use designated port ranges to avoid conflicts with existing services.

**Port Allocation**:
- **Frontend Dev Server**: 3020-3029 (default: 3020)
- **Backend API Server**: 8020-8029 (default: 8020)

**Vite Configuration**:
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3020,  // Frontend server
    strictPort: false,  // Try next available port if 3020 is occupied
    proxy: {
      '/api': {
        target: 'http://localhost:8020',  // Backend server
        changeOrigin: true
      }
    }
  }
})
```

---

## Component Migration Strategy

### Phase-by-Phase Migration Order

**Phase 1: UI Components** (Week 1-2)
1. Layout components (5 total)
   - `MainLayout.vue`
   - `MarketLayout.vue`
   - `DataLayout.vue`
   - `RiskLayout.vue`
   - `StrategyLayout.vue`
2. Navigation components
   - `ResponsiveSidebar.vue`
   - `TopNavigationBar.vue`

**Phase 2: Core Business Components** (Week 3-5)
1. Dashboard pages
   - `Dashboard.vue` → TypeScript
   - `Market.vue` → TypeScript
   - `StockDetail.vue` → TypeScript
2. Strategy components
   - `StrategyManagement.vue` → TypeScript
   - `BacktestAnalysis.vue` → TypeScript
3. Technical analysis
   - `TechnicalAnalysis.vue` → TypeScript
   - `IndicatorLibrary.vue` → TypeScript

**Phase 3: Chart Components** (Week 6)
1. `ProKLineChart.vue` (new TypeScript component)
2. `TechnicalIndicatorOverlay.vue` (new)
3. `PeriodSelector.vue` (enhanced)

**Phase 4-6: Supporting Components** (Week 7-12)
1. Remaining page components (gradual)
2. Utility components
3. Service layers

### Type Definition Library

**Shared Types** (`src/types/`):

```typescript
// market.ts - Market data types
export interface StockData {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: string
}

export interface KLineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

// indicators.ts - Technical indicator types
export interface Indicator {
  name: string
  category: 'TREND' | 'MOMENTUM' | 'VOLATILITY' | 'VOLUME' | 'PATTERN'
  calculate: (data: number[], params?: any) => number[]
  validate?: (params: any) => boolean
}

export interface IndicatorConfig {
  name: string
  parameters: Record<string, number>
  display: {
    color: string
    lineWidth: number
    visible: boolean
  }
}

// trading.ts - A股 trading rules
export interface ATradingRule {
  name: string
  description: string
  validate: (data: TradeData) => boolean
}

export interface TradeData {
  symbol: string
  price: number
  quantity: number
  tradeDate: Date
  settlementDate: Date
  boardType: 'MAIN' | 'CHI NEXT' | 'STAR'
}

// strategy.ts - Strategy backtesting
export interface StrategyConfig {
  id: string
  name: string
  type: 'moving_average' | 'rsi' | 'macd' | 'momentum' | 'custom'
  parameters: Record<string, any>
  status: 'active' | 'inactive' | 'testing'
}

export interface BacktestResult {
  strategyId: string
  totalReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  trades: Trade[]
}

// ai.ts - AI query types
export interface QueryPattern {
  pattern: RegExp
  sqlTemplate: string
  parameters?: string[]
}

export interface QueryResult {
  sql: string
  confidence: number
  method: 'pattern' | 'ai'
  matchedPattern?: RegExp
}

export interface StockRecommendation {
  symbol: string
  name: string
  reason: string
  confidence: number
  category: 'hot' | 'alert' | 'strategy-match'
}
```

---

## Testing Strategy

### Unit Testing

```typescript
// Example: A股 trading rules test
describe('ATradingRules', () => {
  test('should validate T+1 settlement rule', () => {
    const tradeDate = new Date('2025-01-01')
    const settlementDate = new Date('2025-01-02')

    expect(ATradingRules.validateTPlus1(tradeDate, settlementDate)).toBe(true)

    const invalidSettlement = new Date('2025-01-01') // Same day
    expect(ATradingRules.validateTPlus1(tradeDate, invalidSettlement)).toBe(false)
  })

  test('should detect 涨停 for main board stocks', () => {
    const prevClose = 10.0
    const current = 11.0 // +10%

    const result = ATradingRules.checkPriceLimit(prevClose, current, 'stock')
    expect(result).toBe('limit_up')
  })

  test('should validate 100股 lot sizes', () => {
    expect(ATradingRules.validateLotSize(100)).toBe(true)
    expect(ATradingRules.validateLotSize(200)).toBe(true)
    expect(ATradingRules.validateLotSize(150)).toBe(false) // Not multiple of 100
    expect(ATradingRules.validateLotSize(0)).toBe(false)
  })
})
```

### Integration Testing

```typescript
// Example: Natural language query integration
describe('WencaiQueryEngine Integration', () => {
  test('should parse "连续3天上涨" query', async () => {
    const engine = new WencaiQueryEngine()
    const result = await engine.parseQuery('连续3天上涨')

    expect(result.sql).toContain('COUNT(*) >= 3')
    expect(result.confidence).toBeGreaterThan(0.8)
    expect(result.method).toBe('pattern')
  })

  test('should execute query and return stocks', async () => {
    const engine = new WencaiQueryEngine()
    const parseResult = await engine.parseQuery('今日涨停')
    const stocks = await engine.executeQuery(parseResult)

    expect(stocks.length).toBeGreaterThan(0)
    expect(stocks[0].changePercent).toBeGreaterThanOrEqual(9.8)
  })
})
```

### E2E Testing

```typescript
// Example: K-line chart E2E with Playwright
test('ProKLineChart displays A股 data correctly', async ({ page }) => {
  await page.goto('/stock-detail/000001')

  // Wait for chart to render
  await page.waitForSelector('.pro-kline-chart canvas')

  // Verify chart elements
  const chart = page.locator('.pro-kline-chart')
  await expect(chart).toBeVisible()

  // Test period switching
  await page.click('button:has-text("1周")')
  await page.waitForTimeout(500) // Wait for data reload

  // Verify 涨跌停 markers
  const limitUpMarkers = await page.locator('.limit-up-marker').count()
  expect(limitUpMarkers).toBeGreaterThan(0)
})
```

### Performance Testing

```typescript
// Example: Indicator calculation performance
test('should calculate 1000 RSI values in < 100ms', () => {
  const data = Array.from({ length: 1000 }, () => Math.random() * 100)
  const start = performance.now()

  const result = TechnicalIndicators.calculateRSI(data, 14)

  const duration = performance.now() - start
  expect(duration).toBeLessThan(100)
  expect(result).toHaveLength(1000 - 14) // RSI has warmup period
})
```

---

## Deployment Strategy

### Continuous Deployment

Each phase creates a Git tag for rollback safety:

```bash
# Phase 1 complete
git tag -a phase1-dark-theme -m "深色主题系统完成"
git push origin phase1-dark-theme

# Deploy to staging
npm run build
npm run test:e2e
# Manual QA approval
# Deploy to production
```

### Feature Flags

Progressive rollout using environment variables:

```javascript
// config.js
export const FEATURES = {
  darkTheme: process.env.VUE_APP_FEATURE_DARK_THEME === 'true',
  typeScript: process.env.VUE_APP_FEATURE_TYPESCRIPT === 'true',
  proCharts: process.env.VUE_APP_FEATURE_PRO_CHARTS === 'true',
  aiScreening: process.env.VUE_APP_FEATURE_AI_SCREENING === 'true',
  gpuMonitor: process.env.VUE_APP_FEATURE_GPU_MONITOR === 'true'
}
```

### Monitoring & Observability

1. **Frontend Error Tracking**: Sentry integration
2. **Performance Monitoring**: Core Web Vitals (FCP, LCP, CLS, FID)
3. **User Analytics**: Feature usage tracking
4. **A/B Testing**: Gradual rollout for critical features

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|-----------|
| TypeScript compilation breaks build | Allow JS/TS coexistence; incremental migration; strict peer review |
| Dark theme contrast issues | WCAG compliance testing; user feedback; accessibility audit |
| K-line chart performance degradation | Canvas rendering; data downsampling; Web Workers |
| GPU backend incompatibility | Graceful degradation to CPU; extensive testing; feature detection |
| AI query cost overruns | Rate limiting; caching; pattern-matching priority; cost monitoring |

### Operational Risks

| Risk | Mitigation |
|------|-----------|
| Extended timeline (12-16 weeks) | Phased delivery; early value realization; parallel work streams |
| Team learning curve for TypeScript | Training sessions; pair programming; documentation; gradual adoption |
| Feature creep | Strict scope control; change request process; stakeholder alignment |
| Resource constraints | Prioritize high-value components; extend timeline if needed; external support |

---

## Success Criteria

### Phase Completion Criteria

Each phase must meet:

1. **Functional Requirements**: All deliverables working as specified
2. **Quality Standards**: Unit test coverage > 80%, E2E tests passing
3. **Performance Benchmarks**: Page load < 2s, 60fps animations
4. **Accessibility**: WCAG 2.1 AA compliance
5. **Documentation**: User guides updated, API docs current

### Overall Success Metrics

1. **User Satisfaction**: Post-launch survey score > 4.0/5
2. **Adoption Rate**: 70%+ users actively using new features within 30 days
3. **Performance Improvement**: 40%+ reduction in page load times
4. **Developer Productivity**: 30%+ reduction in bug reports
5. **Business Impact**: 15%+ increase in user engagement (session duration)

---

## Appendix

### A. Framework A Component Inventory

**Current Components** (81 Vue files):
- 30+ page components (`src/views/`)
- 23 business components (`src/components/`)
- 15 general UI components (`src/components/common/`)
- 13 utility components (`src/utils/`)

### B. Framework B Reusable Assets

**Layout Components** (5 total):
- `MainLayout.vue` - Dashboard/main pages
- `MarketLayout.vue` - Market data pages
- `DataLayout.vue` - Analysis pages
- `RiskLayout.vue` - Risk monitoring pages
- `StrategyLayout.vue` - Strategy/backtesting pages

**Theme System**:
- Color variables (SCSS)
- Typography definitions
- Spacing and layout tokens
- Responsive breakpoints

### C. Technical Dependencies

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "element-plus": "^2.8.0",
    "klinecharts": "^9.6.0",
    "echarts": "^5.5.0",
    "technicalindicators": "^3.0.0",
    "lightweight-charts": "^4.0.0"
  },
  "devDependencies": {
    "typescript": "~5.3.0",
    "vue-tsc": "^1.8.0",
    "vite": "^5.4.0",
    "@types/lightweight-charts": "^4.0.0"
  }
}
```

### D. Reference Documentation

1. **Comprehensive Integration Plan**: `docs/guides/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md`
2. **Framework B Developer Guide**: `/opt/iflow/myhtml/DEVELOPER_GUIDE.md`
3. **Phase 1-4 Technical Guides**: `docs/design/update/技术实施指南_第*.md`
4. **Current Pages Documentation**: `docs/WEB_PAGES_DOCUMENTATION.md`
5. **A股 Trading Rules**: Trading rules for Chinese A-share market
6. **Technical Indicators Reference**: 161 indicators documentation

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-12-26
**Version**: 1.0
