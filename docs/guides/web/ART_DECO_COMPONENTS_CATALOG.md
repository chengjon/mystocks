# ArtDeco Components Catalog
## ArtDeco 组件目录

**Last Updated**: 2026-01-20
**Version**: 2.0
**Total Components**: 66

---

## 📑 Catalog Navigation

- [Base Components](#base-components) (13)
- [Business Components](#business-components) (10)
- [Chart Components](#chart-components) (8)
- [Trading Components](#trading-components) (13)
- [Advanced Components](#advanced-components) (10)
- [Core Components](#core-components) (12)

---

## Base Components

### Atomic UI components providing fundamental interface elements.

| Component | Description | Props | Variants | Status |
|-----------|-------------|-------|---------|--------|
| **ArtDecoAlert** | Alert notification component | `message`, `type`, `dismissible` | `default`, `success`, `warning`, `error` | ✅ Stable |
| **ArtDecoBadge** | Small status badge | `text`, `variant` | `default`, `success`, `warning`, `error`, `info` | ✅ Stable |
| **ArtDecoButton** | Button with ArtDeco styling | `variant`, `size`, `disabled`, `block` | `default`, `solid`, `outline`, `secondary`, `rise`, `fall`, **`double-border`**, `pulse` | ✅ **Enhanced** |
| **ArtDecoCard** | Content card container | `title`, `subtitle`, `hoverable`, `clickable`, `variant` | `default`, `stat`, `bordered`, `chart`, `form`, `elevated` | ✅ **Enhanced** |
| **ArtDecoCollapsible** | Collapsible content section | `title`, `opened` | - | ✅ Stable |
| **ArtDecoDialog** | Modal dialog component | `title`, `size`, `persistent` | `default`, `small`, `medium`, `large` | ✅ Stable |
| **ArtDecoInput** ⭐ | Text input with ArtDeco styling | `modelValue`, `label`, **`labelType`**, `placeholder`, `disabled`, `variant` | `default`, `bordered` | ✅ **Enhanced** |
| **ArtDecoLanguageSwitcher** | Language selector | `languages`, `modelValue` | - | ✅ Stable |
| **ArtDecoProgress** | Progress indicator | `value`, `type`, `show-label` | `default`, `determinate`, `indeterminate` | ✅ Stable |
| **ArtDecoSelect** | Dropdown select component | `options`, `modelValue`, `placeholder` | - | ✅ Stable |
| **ArtDecoSkipLink** | Accessibility skip link | `label`, `href` | - | ✅ Stable |
| **ArtDecoStatCard** | Statistics display card | `title`, `value`, `trend`, `icon` | - | ✅ Stable |
| **ArtDecoSwitch** | Toggle switch component | `modelValue`, `disabled` | - | ✅ Stable |

**Phase 2 Updates**:
- ✨ **ArtDecoButton**: Added `double-border` variant (signature ArtDeco double-frame style)
- ✨ **ArtDecoCard**: Fixed corner radius to `0px` (perfectly sharp)
- ✨ **ArtDecoInput**: Added `labelType="roman"` prop for Roman numeral labels

---

## Business Components

### Business logic and UI components for forms, configuration, and general operations.

| Component | Description | Category | Status |
|-----------|-------------|----------|--------|
| **ArtDecoAlertRule** | Alert rule configuration | Configuration | ✅ Stable |
| **ArtDecoBacktestConfig** | Backtest strategy configuration | Configuration | ✅ Stable |
| **ArtDecoButtonGroup** | Grouped button controls | Control | ✅ Stable |
| **ArtDecoCodeEditor** | Code/editor display component | Display | ✅ Stable |
| **ArtDecoDateRange** | Date range picker | Form Input | ✅ Stable |
| **ArtDecoFilterBar** | Filter and search bar | Filter | ✅ Stable |
| **ArtDecoInfoCard** | Information display card | Display | ✅ Stable |
| **ArtDecoMechanicalSwitch** | Mechanical toggle switch | Control | ✅ Stable |
| **ArtDecoSlider** | Range slider control | Form Input | ✅ Stable |
| **ArtDecoStatus** | Status indicator | Display | ✅ Stable |

**Path**: `@/components/artdeco/business/`

**Import Example**:
```typescript
import { ArtDecoDateRange, ArtDecoFilterBar } from '@/components/artdeco/business'
// or
import { ArtDecoDateRange } from '@/components/artdeco'
```

---

## Chart Components

### Chart and visualization components for financial data and market analysis.

| Component | Description | Chart Type | Status |
|-----------|-------------|------------|--------|
| **CorrelationMatrix** | Correlation heatmap matrix | Heatmap | ✅ Stable |
| **DepthChart** | Market depth visualization | Depth Chart | ✅ Stable |
| **DrawdownChart** | Drawdown visualization | Line Chart | ✅ Stable |
| **HeatmapCard** | Heat map display card | Heatmap | ✅ Stable |
| **PerformanceTable** | Performance metrics table | Table | ✅ Stable |
| **TimeSeriesChart** | Time series line/area chart | Time Series | ✅ Stable |
| **ArtDecoKLineChartContainer** | K-line chart wrapper | Candlestick | ✅ Stable |
| **ArtDecoRomanNumeral** | Roman numeral display | Decorative | ✅ Stable |

**Path**: `@/components/artdeco/charts/`

**Import Example**:
```typescript
import { TimeSeriesChart, DrawdownChart } from '@/components/artdeco/charts'
// or
import { TimeSeriesChart } from '@/components/artdeco'
```

---

## Trading Components

### Trading-specific components for order management, position tracking, and trading UI.

| Component | Description | Trading Feature | Status |
|-----------|-------------|-----------------|--------|
| **ArtDecoCollapsibleSidebar** | Collapsible side panel | Navigation | ✅ Stable |
| **ArtDecoDynamicSidebar** | Dynamic/hideable sidebar | Navigation | ✅ Stable |
| **ArtDecoLoader** | Loading indicator | Feedback | ✅ Stable |
| **ArtDecoOrderBook** | Order book display | Market Data | ✅ Stable |
| **ArtDecoPositionCard** | Position information card | Portfolio | ✅ Stable |
| **ArtDecoRiskGauge** | Risk level gauge | Risk Management | ✅ Stable |
| **ArtDecoSidebar** | Fixed sidebar panel | Navigation | ✅ Stable |
| **ArtDecoStrategyCard** | Trading strategy card | Algorithm Trading | ✅ Stable |
| **ArtDecoTable** | Data table component | Display | ✅ Stable |
| **ArtDecoTicker** | Ticker display | Market Data | ✅ Stable |
| **ArtDecoTickerList** | Ticker list | Market Data | ✅ Stable |
| **ArtDecoTopBar** | Top navigation/action bar | Navigation | ✅ Stable |
| **ArtDecoTradeForm** | Trade execution form | Order Entry | ✅ Stable |

**Path**: `@/components/artdeco/trading/`

**Import Example**:
```typescript
import { ArtDecoOrderBook, ArtDecoTradeForm } from '@/components/artdeco/trading'
// or
import { ArtDecoOrderBook } from '@/components/artdeco'
```

---

## Advanced Components

### Advanced analysis components for complex data visualization and decision support.

| Component | Description | Analysis Type | Status |
|-----------|-------------|--------------|--------|
| **ArtDecoAnomalyTracking** | Anomaly detection display | Anomaly Detection | ✅ Stable |
| **ArtDecoBatchAnalysisView** | Batch analysis interface | Batch Processing | ✅ Stable |
| **ArtDecoCapitalFlow** | Capital flow visualization | Flow Analysis | ✅ Stable |
| **ArtDecoChipDistribution** | Chip distribution display | Distribution | ✅ Stable |
| **ArtDecoDecisionModels** | Decision model interface | Decision Support | ✅ Stable |
| **ArtDecoFinancialValuation** | Financial valuation display | Valuation | ✅ Stable |
| **ArtDecoMarketPanorama** | Market overview dashboard | Market Overview | ✅ Stable |
| **ArtDecoSentimentAnalysis** | Sentiment analysis display | Sentiment | ✅ Stable |
| **ArtDecoTimeSeriesAnalysis** | Time series analysis | Technical Analysis | ✅ Stable |
| **ArtDecoTradingSignals** | Trading signals display | Signals | ✅ Stable |

**Path**: `@/components/artdeco/advanced/`

**Import Example**:
```typescript
import { ArtDecoTradingSignals, ArtDecoSentimentAnalysis } from '@/components/artdeco/advanced'
```

---

## Core Components

### Core layout and structural components for application architecture.

| Component | Description | Type | Status |
|-----------|-------------|------|--------|
| **ArtDecoAnalysisDashboard** | Analysis dashboard layout | Layout | ✅ Stable |
| **ArtDecoBreadcrumb** | Breadcrumb navigation | Navigation | ✅ Stable |
| **ArtDecoFooter** | Page footer | Layout | ✅ Stable |
| **ArtDecoFunctionTree** | Function tree display | Navigation | ✅ Stable |
| **ArtDecoFundamentalAnalysis** | Fundamental analysis interface | Analysis | ✅ Stable |
| **ArtDecoHeader** | Page header | Layout | ✅ Stable |
| **ArtDecoIcon** | Icon component | Display | ✅ Stable |
| **ArtDecoLoadingOverlay** | Loading overlay | Feedback | ✅ Stable |
| **ArtDecoRadarAnalysis** | Radar chart analysis | Analysis | ✅ Stable |
| **ArtDecoStatusIndicator** | Status indicator | Display | ✅ Stable |
| **ArtDecoTechnicalAnalysis** | Technical analysis interface | Analysis | ✅ Stable |
| **ArtDecoToast** | Toast notification | Feedback | ✅ Stable |

**Path**: `@/components/artdeco/core/`

---

## 🆕 Phase 2 Enhancements (2026-01-20)

### New Features

#### 1. ArtDecoButton - Double Border Variant
**Signature ArtDeco visual element now implemented**

```vue
<ArtDecoButton variant="double-border">
  DOUBLE BORDER
</ArtDecoButton>
```

**Features**:
- Double-frame style (outer 2px + inner 1px)
- Smooth hover animation (borders contract from 4px to 2px offset)
- Gold glow effect on hover
- Perfectly sharp corners (0px radius)

#### 2. ArtDecoInput - Roman Numeral Labels
**Automatic Roman numeral conversion**

```vue
<ArtDecoInput
  v-model="username"
  label="USERNAME 1"
  label-type="roman"
/>
<!-- Displays: USERNAME Ⅰ -->
```

**Features**:
- Supports numbers 1-20
- Auto-detects trailing numbers in labels
- Falls back to appending "Ⅰ" if no number found
- Preserves original label casing

#### 3. ArtDecoCard - Sharp Corners
**Fixed corner radius to ArtDeco standard**

```scss
// Before: 8px stepped corners (too rounded)
// After: 0px radius (perfectly sharp)
border-radius: var(--artdeco-radius-none);
```

---

## 🎨 Design Token Updates

### New Financial Tokens (Phase 1)

```scss
// Technical Indicators
var(--artdeco-indicator-macd-positive)      // #00E676
var(--artdeco-indicator-macd-negative)      // #FF5252
var(--artdeco-indicator-rsi-overbought)    // #FF5252
var(--artdeco-indicator-rsi-oversold)      // #00E676

// Risk Levels
var(--artdeco-risk-low)                   // #00E676
var(--artdeco-risk-medium)                 // #FFD700
var(--artdeco-risk-high)                   // #FF5252

// GPU Performance
var(--artdeco-gpu-normal)                 // #00E676
var(--artdeco-gpu-busy)                   // #FFD700
var(--artdeco-gpu-overload)                // #FF5252

// And 40+ more financial tokens
```

**File**: `styles/artdeco-financial.scss`

---

## 📦 Component Usage Guidelines

### Import Patterns

#### Pattern 1: Import from Main Index (Recommended)
```typescript
import { ArtDecoButton, ArtDecoCard, ArtDecoInput } from '@/components/artdeco'
```

**Pros**:
- ✅ Backwards compatible
- ✅ IDE autocomplete support
- ✅ Single import statement

#### Pattern 2: Import from Category Index
```typescript
// Business components
import { ArtDecoDateRange, ArtDecoFilterBar } from '@/components/artdeco/business'

// Chart components
import { TimeSeriesChart, DrawdownChart } from '@/components/artdeco/charts'

// Trading components
import { ArtDecoOrderBook, ArtDecoTradeForm } from '@/components/artdeco/trading'
```

**Pros**:
- ✅ Clear category organization
- ✅ Smaller bundle size (tree-shaking friendly)
- ✅ Better code organization

#### Pattern 3: Direct File Import (Not Recommended)
```typescript
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
```

**Cons**:
- ❌ Brittle (breaks on file moves)
- ❌ Harder to maintain
- ❌ No IDE autocomplete

---

## 🔍 Component Search Guide

### Find Component by Use Case

**I need a...** | **Component** | **Category**
|---|---|---|
| Button | `ArtDecoButton` | base |
| Card container | `ArtDecoCard` | base |
| Text input | `ArtDecoInput` | base |
| Date picker | `ArtDecoDateRange` | business |
| Line chart | `TimeSeriesChart` | charts |
| Order entry | `ArtDecoTradeForm` | trading |
| Navigation sidebar | `ArtDecoSidebar` | trading |
| Loading spinner | `ArtDecoLoader` | trading |
| Dashboard layout | `ArtDecoAnalysisDashboard` | core |
| Modal dialog | `ArtDecoDialog` | base |

---

## 📊 Component Statistics

### By Category

| Category | Count | Percentage |
|----------|-------|------------|
| **base** | 13 | 19.7% |
| **business** | 10 | 15.2% |
| **charts** | 8 | 12.1% |
| **trading** | 13 | 19.7% |
| **advanced** | 10 | 15.2% |
| **core** | 12 | 18.2% |
| **TOTAL** | **66** | **100%** |

### By Function

| Function | Count |
|----------|-------|
| **Form Input** | 4 |
| **Display/Card** | 8 |
| **Navigation** | 5 |
| **Chart/Viz** | 8 |
| **Feedback** | 3 |
| **Control** | 5 |
| **Layout** | 8 |
| **Analysis** | 6 |
| **Trading** | 5 |
| **Decorative** | 2 |

---

## 🚀 Quick Start

### 1. Import Component

```typescript
import { ArtDecoButton, ArtDecoCard, ArtDecoInput } from '@/components/artdeco'
```

### 2. Use in Template

```vue
<template>
  <div class="my-component">
    <ArtDecoCard title="ANALYSIS">
      <ArtDecoInput v-model="symbol" label="SYMBOL" />
      <ArtDecoButton variant="solid" @click="analyze">
        ANALYZE
      </ArtDecoButton>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoInput } from '@/components/artdeco'

const symbol = ref('600519')
const analyze = () => {
  // Handle analysis
}
</script>
```

### 3. Import Styles

```scss
@import '@/styles/artdeco-global.scss';
```

---

## 📚 Related Documentation

- **[ART_DECO_QUICK_REFERENCE.md](./ART_DECO_QUICK_REFERENCE.md)** - Quick reference guide
- **[ART_DECO_COMPONENT_SHOWCASE_V2.md](./ART_DECO_COMPONENT_SHOWCASE_V2.md)** - Component examples
- **[ART_DECO_IMPLEMENTATION_REPORT.md](./ART_DECO_IMPLEMENTATION_REPORT.md)** - Implementation guide
- **[ArtDeco_System_Architecture_Summary.md](../api/ArtDeco_System_Architecture_Summary.md)** - Architecture overview
- **[ARTDECO_PHASE2_COMPLETION_REPORT.md](../reports/ARTDECO_PHASE2_COMPLETION_REPORT.md)** - Phase 2 enhancements
- **[ARTDECO_PHASE3-4_COMPLETION_REPORT.md](../reports/ARTDECO_PHASE3-4_COMPLETION_REPORT.md)** - Phase 3-4 reorganization

---

**Catalog Version**: 2.0
**Last Update**: 2026-01-20
**Maintainer**: Claude Code (Frontend Specialist)
