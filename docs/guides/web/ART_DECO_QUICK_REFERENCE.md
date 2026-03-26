# Art Deco Quick Reference Guide
## MyStocks 装饰艺术快速参考手册

**Last Updated**: 2026-01-20
**Version**: 2.0 (Phase 2-4 Enhancements)

> Governance note
>
> - Active SCSS truth lives in [ARTDECO_SCSS_GOVERNANCE_BASELINE.md](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md).
> - This file is a quick reference and visual companion. When examples here conflict with the baseline or source files, the baseline wins.
> - New SCSS examples should prefer `@use` over legacy `@import`.

---

## 🆕 What's New in v2.0

- ✨ **3 New Component Categories**: business (10), charts (8), trading (13)
- ✨ **Double Border Button Variant**: Signature ArtDeco double-frame style
- ✨ **Roman Numeral Input Labels**: Automatic numeral conversion
- ✨ **60+ Financial Design Tokens**: Technical indicators, risk levels, GPU metrics
- ✨ **Sharper Card Corners**: Fixed to 0px radius (perfectly sharp)
- 📊 **66 Total Components**: Up from 64, better organized than ever

---

## TL;DR - Essential Commands

### Import Components

**From Main Index (Recommended)**:
```typescript
import { ArtDecoButton, ArtDecoCard, ArtDecoInput } from '@/components/artdeco'
```

**From Category Index (Tree-Shaking Friendly)**:
```typescript
// Business components
import { ArtDecoDateRange, ArtDecoFilterBar } from '@/components/artdeco/business'

// Chart components
import { TimeSeriesChart, DrawdownChart } from '@/components/artdeco/charts'

// Trading components
import { ArtDecoOrderBook, ArtDecoTradeForm } from '@/components/artdeco/trading'
```

### Import Styles

```scss
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-patterns.scss' as *;
```

### Quick Component Usage

```vue
<template>
  <!-- Button -->
  <ArtDecoButton variant="solid" @click="handleAction">
    Click Me
  </ArtDecoButton>

  <!-- Card -->
  <ArtDecoCard title="TITLE" subtitle="Description">
    <p>Content goes here</p>
  </ArtDecoCard>

  <!-- Input -->
  <ArtDecoInput v-model="text" label="LABEL" placeholder="Enter text" />
</template>
```

---

## Color Palette

### Primary Colors

```scss
var(--artdeco-bg-global)       // #0A0A0A - Obsidian Black
var(--artdeco-bg-card)         // #141414 - Rich Charcoal
var(--artdeco-gold-primary)    // #D4AF37 - Metallic Gold ⭐
var(--artdeco-fg-primary)      // #F2F0E4 - Champagne Cream
var(--artdeco-fg-muted)        // #A0A0A0 - Muted Foreground
```

### Market Colors (A-Share Convention)

```scss
var(--artdeco-rise)            // #FF5252 - Red (涨)
var(--artdeco-down)            // #00E676 - Green (跌)
var(--artdeco-flat)            // #B0B3B8 - Gray (平)
```

---

## Typography

### Font Families

```scss
font-family: var(--font-display);  // Cinzel (headings)
font-family: var(--font-body);     // Barlow (body)
font-family: var(--font-mono);     // JetBrains Mono (data)
```

### Heading Rules (MANDATORY)

```scss
// All headings MUST be:
text-transform: uppercase;                    // All caps
letter-spacing: var(--artdeco-tracking-widest); // 0.1em
color: var(--artdeco-gold-primary);            // Gold
```

### Font Sizes

```scss
--artdeco-text-6xl: 64px;   // H1
--artdeco-text-4xl: 44px;   // H2
--artdeco-text-2xl: 30px;   // H3
--artdeco-text-base: 16px;  // Body
```

---

## Common Patterns

### Background with Crosshatch

```scss
.hero-section {
  @include artdeco-crosshatch-bg;
}
```

### Card with Corner Brackets

```scss
.my-card {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  @include artdeco-corner-brackets;
}
```

### Gold Glow on Hover

```scss
.button {
  transition: all var(--artdeco-transition-base);

  &:hover {
    box-shadow: var(--artdeco-glow-intense);
  }
}
```

### Section Divider

```html
<div class="artdeco-section-divider">
  <span>SECTION TITLE</span>
</div>
```

---

## 🆕 Component API Reference (Phase 2 Enhancements)

### ArtDecoButton ⭐ Enhanced

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | `'default' \| 'solid' \| 'outline' \| 'secondary' \| 'rise' \| 'fall' \| **`'double-border'`** \| 'pulse'` | `'default'` | Button style |
| size | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| disabled | `boolean` | `false` | Disabled state |
| block | `boolean` | `false` | Full width |

**🆕 NEW: Double Border Variant** (Signature ArtDeco Style)
```vue
<ArtDecoButton variant="double-border">
  DOUBLE BORDER
</ArtDecoButton>
```

**All Variants**:
- `default` - Transparent bg, gold border
- `solid` - Gold bg, black text
- `outline` - Thin gold border
- `secondary` - Alias for outline
- `rise` - Red border (A股涨)
- `fall` - Green border (A股跌)
- **`double-border`** - ⭐ Double frame style (NEW)
- `pulse` - Pulsing animation

---

### ArtDecoInput ⭐ Enhanced

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| modelValue | `string \| number` | `''` | Input value (v-model) |
| label | `string` | `''` | Uppercase label |
| **labelType** | **`'default' \| 'roman'`** | **`'default'`** | **Label style (NEW)** |
| placeholder | `string` | `''` | Placeholder text |
| type | `string` | `'text'` | Input type |
| disabled | `boolean` | `false` | Disabled state |
| required | `boolean` | `false` | Show asterisk |
| errorMessage | `string` | `''` | Error message (red) |
| helperText | `string` | `''` | Helper text (gray) |
| variant | `'default' \| 'bordered'` | `'default'` | Input style |

**🆕 NEW: Roman Numeral Labels**
```vue
<ArtDecoInput
  v-model="username"
  label="USERNAME 1"
  label-type="roman"
/>
<!-- Displays: USERNAME Ⅰ -->

<ArtDecoInput
  label="EMAIL 2"
  label-type="roman"
/>
<!-- Displays: EMAIL Ⅱ -->
```

**Features**:
- Supports numbers 1-20 (Ⅰ, Ⅱ, Ⅲ, Ⅳ, Ⅴ, Ⅵ, Ⅶ, Ⅷ, Ⅸ, Ⅹ, Ⅺ, Ⅻ, Ⅼ, Ⅽ, Ⅾ, Ⅿ, ⅰ, ⅱ, ⅳ, Ⅹ)
- Auto-detects trailing numbers
- Falls back to appending "Ⅰ" if no number found

---

### ArtDecoCard ⭐ Enhanced

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| title | `string` | `''` | Card title (display font) |
| subtitle | `string` | `''` | Card subtitle (muted) |
| hoverable | `boolean` | `true` | Enable hover lift effect |
| clickable | `boolean` | `false` | Make card clickable |
| variant | `'default' \| 'stat' \| 'bordered' \| 'chart' \| 'form' \| 'elevated'` | `'default'` | Card style |

**🆕 ENHANCED: Sharp Corners**
```scss
// Now uses 0px radius (perfectly sharp)
border-radius: var(--artdeco-radius-none);
```

---

## 🆕 Financial Design Tokens (Phase 1)

### Technical Indicator Tokens

```scss
// MACD Indicator
var(--artdeco-indicator-macd-positive)      // #00E676 - Bullish signal
var(--artdeco-indicator-macd-negative)      // #FF5252 - Bearish signal
var(--artdeco-indicator-macd-neutral)       // #B0B3B8 - Neutral

// RSI Indicator
var(--artdeco-indicator-rsi-overbought)     // #FF5252 - >70 overbought
var(--artdeco-indicator-rsi-oversold)       // #00E676 - <30 oversold
var(--artdeco-indicator-rsi-neutral)        // #FFD700 - 30-70 normal

// Bollinger Bands
var(--artdeco-indicator-bb-upper)           // #FF5252 - Upper band
var(--artdeco-indicator-bb-lower)           // #00E676 - Lower band
var(--artdeco-indicator-bb-middle)          // #D4AF37 - Middle band

// Moving Averages
var(--artdeco-indicator-ma-fast)            // #00E676 - Fast MA (e.g., MA5)
var(--artdeco-indicator-ma-medium)          // #FFD700 - Medium MA (e.g., MA20)
var(--artdeco-indicator-ma-slow)            // #FF5252 - Slow MA (e.g., MA60)
```

### Risk Level Tokens

```scss
// Risk Assessment Colors
var(--artdeco-risk-low)                     // #00E676 - Low risk
var(--artdeco-risk-medium)                  // #FFD700 - Medium risk
var(--artdeco-risk-high)                    // #FF5252 - High risk
var(--artdeco-risk-extreme)                 // #FF1744 - Extreme risk

// Risk Score Indicators
var(--artdeco-risk-score-0)                 // #00E676 - Score 0-20
var(--artdeco-risk-score-1)                 // #76FF03 - Score 20-40
var(--artdeco-risk-score-2)                 // #FFD700 - Score 40-60
var(--artdeco-risk-score-3)                 // #FF5252 - Score 60-80
var(--artdeco-risk-score-4)                 // #FF1744 - Score 80-100
```

### GPU Performance Tokens

```scss
// GPU Status Colors
var(--artdeco-gpu-normal)                   // #00E676 - Normal load (<60%)
var(--artdeco-gpu-busy)                     // #FFD700 - High load (60-85%)
var(--artdeco-gpu-overload)                 // #FF5252 - Overload (>85%)
var(--artdeco-gpu-error)                    // #FF1744 - Error state

// GPU Metrics
var(--artdeco-gpu-usage-low)                // #00E676 - 0-30% usage
var(--artdeco-gpu-usage-medium)             // #FFD700 - 30-70% usage
var(--artdeco-gpu-usage-high)               // #FF5252 - 70-100% usage

// Memory Status
var(--artdeco-memory-healthy)               // #00E676 - <80% used
var(--artdeco-memory-warning)               // #FFD700 - 80-90% used
var(--artdeco-memory-critical)              // #FF5252 - >90% used
```

### Market Data Tokens

```scss
// Price Change Indicators
var(--artdeco-price-up-strong)              // #FF1744 - Strong gain (>5%)
var(--artdeco-price-up-moderate)            // #FF5252 - Moderate gain (2-5%)
var(--artdeco-price-down-strong)            // #00E676 - Strong drop (>5%)
var(--artdeco-price-down-moderate)          // #4CAF50 - Moderate drop (2-5%)

// Volume Indicators
var(--artdeco-volume-high)                  // #FF5252 - High volume
var(--artdeco-volume-normal)                // #FFD700 - Normal volume
var(--artdeco-volume-low)                   // #00E676 - Low volume

// Volatility Indicators
var(--artdeco-volatility-low)               // #00E676 - Low volatility
var(--artdeco-volatility-normal)            // #FFD700 - Normal volatility
var(--artdeco-volatility-high)              // #FF5252 - High volatility
```

### Strategy Performance Tokens

```sharp
// Return Categories
var(--artdeco-return-excellent)             // #00E676 - >20% return
var(--artdeco-return-good)                  // #76FF03 - 10-20% return
var(--artdeco-return-neutral)               // #FFD700 - 0-10% return
var(--artdeco-return-poor)                  // #FF5252 - Negative return

// Sharpe Ratio Indicators
var(--artdeco-sharpe-excellent)             // #00E676 - Sharpe >2
var(--artdeco-sharpe-good)                  // #FFD700 - Sharpe 1-2
var(--artdeco-sharpe-poor)                  // #FF5252 - Sharpe <1

// Maximum Drawdown Levels
var(--artdeco-drawdown-low)                 // #00E676 - DD <5%
var(--artdeco-drawdown-medium)              // #FFD700 - DD 5-15%
var(--artdeco-drawdown-high)                // #FF5252 - DD >15%
```

### Usage Example

```vue
<template>
  <div class="risk-indicator" :style="{ color: riskColor }">
    Risk Level: {{ riskLabel }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  riskScore: number // 0-100
}>()

const riskColor = computed(() => {
  if (props.riskScore < 30) return 'var(--artdeco-risk-low)'
  if (props.riskScore < 60) return 'var(--artdeco-risk-medium)'
  if (props.riskScore < 80) return 'var(--artdeco-risk-high)'
  return 'var(--artdeco-risk-extreme)'
})

const riskLabel = computed(() => {
  if (props.riskScore < 30) return 'LOW'
  if (props.riskScore < 60) return 'MEDIUM'
  if (props.riskScore < 80) return 'HIGH'
  return 'EXTREME'
})
</script>
```

**File Location**: `web/frontend/src/styles/artdeco-financial.scss`

**Import**:
```scss
@use '@/styles/artdeco-financial.scss' as *;
```

---

## Component API Reference

### ArtDecoButton

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | `'default' \| 'solid' \| 'outline'` | `'default'` | Button style |
| size | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| disabled | `boolean` | `false` | Disabled state |
| block | `boolean` | `false` | Full width |

```vue
<ArtDecoButton variant="solid" size="lg" block>
  Primary Action
</ArtDecoButton>
```

### ArtDecoCard

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| title | `string` | `''` | Card title (display font) |
| subtitle | `string` | `''` | Card subtitle (muted) |
| hoverable | `boolean` | `true` | Enable hover lift effect |
| clickable | `boolean` | `false` | Make card clickable |

```vue
<ArtDecoCard
  title="MARKET OVERVIEW"
  subtitle="Real-time data"
  hoverable
  @click="handleCardClick"
>
  <p>Card content here</p>
  <template #footer>
    <ArtDecoButton>View Details</ArtDecoButton>
  </template>
</ArtDecoCard>
```

### ArtDecoInput

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| modelValue | `string \| number` | `''` | Input value (v-model) |
| label | `string` | `''` | Uppercase label |
| placeholder | `string` | `''` | Placeholder text |
| type | `string` | `'text'` | Input type |
| disabled | `boolean` | `false` | Disabled state |
| required | `boolean` | `false` | Show asterisk |
| errorMessage | `string` | `''` | Error message (red) |
| helperText | `string` | `''` | Helper text (gray) |

```vue
<ArtDecoInput
  v-model="username"
  label="USERNAME"
  placeholder="Enter your username"
  required
  helperText="Must be at least 3 characters"
/>
```

---

## Utility Classes

### Text Colors

```html
<div class="text-artdeco-gold">Gold text</div>
<div class="text-artdeco-cream">Primary text</div>
<div class="text-artdeco-muted">Muted text</div>
```

### Background Colors

```html
<div class="bg-artdeco-primary">Black background</div>
<div class="bg-artdeco-card">Charcoal background</div>
```

### Typography

```html
<h1 class="font-artdeco-display">TITLE</h1>
<p class="font-artdeco-body">Body text</p>
```

### Borders & Glows

```html
<div class="artdeco-border-gold">Gold border</div>
<div class="artdeco-hover-glow">Gold glow on hover</div>
```

---

## Design Rules (MANDATORY)

### 1. Headings

✅ **CORRECT:**
```scss
h1 {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
  color: var(--artdeco-gold-primary);
}
```

❌ **WRONG:**
```scss
h1 {
  font-family: 'Arial', sans-serif;
  text-transform: capitalize;
  letter-spacing: normal;
  color: #FFF;
}
```

### 2. Borders

✅ **CORRECT:**
```scss
.card {
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none); // Sharp corners
}
```

❌ **WRONG:**
```scss
.card {
  border: 1px solid #333;
  border-radius: 8px; // No rounded corners!
}
```

### 3. Backgrounds

✅ **CORRECT:**
```scss
body {
  @include artdeco-crosshatch-bg();
  background-color: var(--artdeco-bg-primary);
}
```

❌ **WRONG:**
```scss
body {
  background-color: #000;
  // Missing diagonal crosshatch pattern!
}
```

### 4. Buttons

✅ **CORRECT:**
```vue
<ArtDecoButton variant="solid">
  SUBMIT
</ArtDecoButton>
```

❌ **WRONG:**
```vue
<button class="el-button">Submit</button>
// Use ArtDecoButton instead!
```

---

## Common Tasks

### Add a New Page with Art Deco Styling

```vue
<template>
  <div class="page-container">
    <!-- Page header with section divider -->
    <div class="page-header">
      <h1>PAGE TITLE</h1>
      <p class="subtitle">Page description here</p>
    </div>

    <!-- Content with Art Deco cards -->
    <ArtDecoCard title="SECTION I" subtitle="First section">
      <p>Content goes here</p>
    </ArtDecoCard>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-patterns.scss' as *;

.page-container {
  @include artdeco-crosshatch-bg;
  padding: var(--artdeco-spacing-6);
}

.page-header {
  @extend .artdeco-section-divider;
  text-align: center;
  margin-bottom: var(--artdeco-spacing-8);
}

h1 {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
  color: var(--artdeco-gold-primary);
}

.subtitle {
  color: var(--artdeco-fg-muted);
  font-family: var(--font-body);
}
</style>
```

### Create an Art Deco Table

```vue
<template>
  <ArtDecoCard title="DATA TABLE">
    <table class="artdeco-table">
      <thead>
        <tr>
          <th>Column I</th>
          <th>Column II</th>
          <th>Column III</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.col1 }}</td>
          <td>{{ item.col2 }}</td>
          <td>{{ item.col3 }}</td>
        </tr>
      </tbody>
    </table>
  </ArtDecoCard>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-body);

  th {
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    color: var(--artdeco-gold-primary);
    border-bottom: 2px solid var(--artdeco-border-gold);
    padding: var(--artdeco-spacing-3);
    text-align: left;
  }

  td {
    color: var(--artdeco-fg-primary);
    border-bottom: 1px solid var(--artdeco-border-default);
    padding: var(--artdeco-spacing-3);
  }

  tr:hover td {
    background: rgba(212, 175, 55, 0.05);
  }
}
</style>
```

### Add Glow Effect to Elements

```scss
@use '@/styles/artdeco-patterns.scss' as *;

// Method 1: Using utility class
.highlight-box {
  @extend .artdeco-hover-glow;
}

// Method 2: Direct box-shadow
.highlight-box {
  transition: box-shadow var(--artdeco-transition-base);

  &:hover {
    box-shadow: var(--artdeco-glow-intense);
  }
}

// Method 3: Custom glow
.custom-glow {
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}
```

---

## Troubleshooting

### Fonts Not Loading

**Problem**: Cinzel or Barlow not displaying

**Solution**:
1. Check browser console for network errors
2. Verify `artdeco-global.scss` is imported in `main.js`
3. Check internet connection (Google Fonts requires CDN)
4. Fallback to system fonts if blocked

### Colors Not Applied

**Problem**: Art Deco colors not showing

**Solution**:
1. Verify CSS custom properties are loaded: `getComputedStyle(document.documentElement).getPropertyValue('--artdeco-gold-primary')`
2. Check `artdeco-global.scss` import order (must be first)
3. Clear browser cache and rebuild: `npm run dev`

### Corner Brackets Not Visible

**Problem**: L-shaped corners not displaying

**Solution**:
1. Ensure parent has `position: relative`
2. Check `z-index` (brackets might be behind content)
3. Verify contrast against background
4. Increase border width if needed

---

## Best Practices

### DO's ✅

- Use ArtDecoButton, ArtDecoCard, ArtDecoInput components
- Apply `@include artdeco-crosshatch-bg;` or reuse the crosshatch utility/pattern layer
- Make headings uppercase with `var(--artdeco-tracking-widest)` (current baseline: `0.1em`)
- Use gold accent color sparingly but decisively
- Add corner brackets to cards and containers
- Include glow effects on interactive elements
- Maintain sharp corners (0px or 2px max radius)
- Test contrast ratios (minimum 7:1 for gold on black)

### DON'Ts ❌

- Don't use rounded corners (> 2px)
- Don't use drop shadows (use glow effects instead)
- Don't use lowercase for headings (must be uppercase)
- Don't use blue/purple/green for accents (gold only)
- Don't skip diagonal crosshatch background
- Don't use system fonts for headings (use the ArtDeco display font stack)
- Don't mix Art Deco with other design systems
- Don't override Art Deco tokens without good reason

---

## Resources

### Full Documentation
- [Art Deco Implementation Report](./ART_DECO_IMPLEMENTATION_REPORT.md)

### Design Specification
- `/opt/iflow/myhtml/prompts/ArtDeco.md`

### Component Files
- `/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/`

### Style Files
- `/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-*.scss`

---

## Quick Copy-Paste Snippets

### Button Group

```vue
<ArtDecoButton variant="outline">Cancel</ArtDecoButton>
<ArtDecoButton variant="solid">Confirm</ArtDecoButton>
```

### Form Input

```vue
<ArtDecoInput
  v-model="formData.email"
  label="EMAIL ADDRESS"
  type="email"
  placeholder="user@example.com"
  required
  :error-messages="errors.email"
/>
```

### Stats Card

```vue
<ArtDecoCard :hoverable="false">
  <div class="stat-value">1,234</div>
  <div class="stat-label">TOTAL STOCKS</div>
</ArtDecoCard>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.stat-value {
  font-family: var(--font-display);
  font-size: var(--artdeco-text-4xl);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
}

.stat-label {
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  font-size: var(--artdeco-text-sm);
}
</style>
```

---

**End of Quick Reference**

For detailed implementation guide, see [ART_DECO_IMPLEMENTATION_REPORT.md](./ART_DECO_IMPLEMENTATION_REPORT.md)
