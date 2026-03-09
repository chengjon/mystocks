## ADDED Requirements

### Requirement: ArtDeco Design Token Usage

**Requirement**: Smart and dumb components MUST use ArtDeco design tokens for consistent visual identity.

#### Scenario: Applying Design Token Colors
**GIVEN** a component that needs visual styling
**WHEN** applying colors
**THEN** it MUST use the ArtDeco design tokens:

```scss
// Color tokens
--artdeco-gold: #D4AF37;
--artdeco-gold-light: #F0E68C;
--artdeco-bronze: #CD7F32;
--artdeco-champagne: #F7E7CE;
--color-bg-primary: #1A1A1D;
--color-bg-card: #2A2A2E;
--color-text-primary: #FFFFFF;

// Financial data colors (A股 convention)
--color-rise: #00C853;
--color-fall: #FF1744;
--color-warning: #D4AF37;

// Usage example
.component {
  color: var(--color-text-primary);
  background-color: var(--color-bg-card);
  border: 1px solid var(--artdeco-gold);
}
```

#### Scenario: Applying Typography Tokens
**GIVEN** a component that needs text styling
**WHEN** applying typography
**THEN** it MUST use the typography tokens:

```scss
// Typography tokens
--font-display: 'Cinzel', serif;
--font-body: 'Barlow', sans-serif;
--font-mono: 'JetBrains Mono', monospace;

// Header typography
h1, h2, h3, .logo, .section-title {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

// Body typography
body, p, span, .body-text {
  font-family: var(--font-body);
  font-weight: 400;
}

// Number typography (tabular alignment)
.price, .percentage, .volume, .code {
  font-family: var(--font-mono);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
```

### Requirement: ArtDeco Animation System

**Requirement**: Components MUST implement ArtDeco animation effects for interactions and transitions.

#### Scenario: Page Load Animation
**GIVEN** a page or view component
**WHEN** mounting
**THEN** it SHOULD apply staggered page load animation:

```vue
<template>
  <div class="page-container page-enter">
    <div class="card" v-for="(item, index) in items" :key="item.id"
         :style="{ animationDelay: `${index * 0.1}s` }">
      {{ item.title }}
    </div>
  </div>
</template>

<style scoped>
@keyframes artdeco-page-load {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-enter {
  animation: artdeco-page-load 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
</style>
```

#### Scenario: Button Hover Animation
**GIVEN** a button component
**WHEN** user hovers
**THEN** it MUST apply gold radial gradient effect:

```scss
.artdeco-button {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.artdeco-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(212, 175, 55, 0.3) 0%,
    transparent 70%
  );
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.artdeco-button:hover::before {
  width: 300px;
  height: 300px;
}
```

#### Scenario: Card Hover Animation
**GIVEN** a card component
**WHEN** user hovers
**THEN** it MUST apply lift and gold glow effect:

```scss
.artdeco-card {
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.artdeco-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 8px 16px rgba(0, 0, 0, 0.2),
    0 0 20px rgba(212, 175, 55, 0.3);
  border-color: var(--artdeco-gold-light);
}
```

#### Scenario: Data Update Animation
**GIVEN** a component displaying real-time data
**WHEN** data updates
**THEN** it SHOULD apply gold flash animation:

```scss
@keyframes data-update-flash {
  0%, 100% {
    background-color: transparent;
  }
  50% {
    background-color: rgba(212, 175, 55, 0.2);
  }
}

.data-updated {
  animation: data-update-flash 0.8s ease;
}
```

#### Scenario: Tab Switching Animation
**GIVEN** a tab navigation component
**WHEN** active tab changes
**THEN** it MUST apply gold slider transition:

```scss
.tab-bar {
  position: relative;
}

.tab-bar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--artdeco-gold);
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.tab-bar.active-left::after {
  left: 0;
  width: 100px;
}

.tab-bar.active-right::after {
  left: 200px;
  width: 100px;
}
```

### Requirement: Financial Data Color Convention

**Requirement**: Components displaying financial data MUST follow A股 color convention (RED=上涨, GREEN=下跌).

#### Scenario: Price Change Coloring
**GIVEN** a component displaying price changes
**WHEN** rendering price data
**THEN** it MUST use:
- `--color-rise` (#00C853, green) for price increase
- `--color-fall` (#FF1744, red) for price decrease

```vue
<template>
  <div :class="['price-change', change > 0 ? 'up' : 'down']">
    {{ formatChange(change) }}
  </div>
</template>

<style scoped>
.price-change.up {
  color: var(--color-rise);
}

.price-change.down {
  color: var(--color-fall);
}
</style>
```

#### Scenario: Chart Data Coloring
**GIVEN** a chart component displaying financial data
**WHEN** configuring colors
**THEN** it MUST use consistent financial data colors:

```typescript
const chartColors = {
  up: '#00C853',
  down: '#FF1744',
  warning: '#D4AF37',
  primary: '#D4AF37',  // ArtDeco gold
  secondary: '#4A90E2'
};
```

### Requirement: ECharts ArtDeco Theme Integration

**Requirement**: Chart components MUST use the ArtDeco ECharts theme for visual consistency.

#### Scenario: K-Line Chart Theme
**GIVEN** a K-line chart component
**WHEN** configuring ECharts
**THEN** it MUST apply ArtDeco theme settings:

```typescript
const artDecoTheme = {
  color: ['#D4AF37', '#4A90E2', '#00C853', '#FF1744'],
  backgroundColor: '#2A2A2E',
  textStyle: {
    fontFamily: 'Barlow, sans-serif'
  },
  title: {
    textStyle: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 600,
      color: '#FFFFFF'
    }
  },
  legend: {
    textStyle: {
      fontFamily: 'Barlow, sans-serif',
      color: '#B8B8B8'
    }
  },
  xAxis: {
    axisLine: {
      lineStyle: {
        color: '#D4AF37'
      }
    },
    axisLabel: {
      fontFamily: 'JetBrains Mono, monospace',
      color: '#B8B8B8'
    }
  },
  yAxis: {
    axisLine: {
      lineStyle: {
        color: '#D4AF37'
      }
    },
    axisLabel: {
      fontFamily: 'JetBrains Mono, monospace',
      color: '#B8B8B8'
    }
  }
};
```

### Requirement: Compact Table Mode

**Requirement**: Table components SHOULD support compact mode with 32px row height for Bloomberg Terminal-standard data density.

#### Scenario: Compact Table Rendering
**GIVEN** a table component
**WHEN** compact mode is enabled
**THEN** it MUST use 32px row height and optimized spacing:

```scss
.table-compact {
  --row-height: 32px;
  --cell-padding: 4px 8px;
}

.table-compact .row {
  height: var(--row-height);
  padding: var(--cell-padding);
}

.table-compact .cell {
  font-size: 12px;
  font-family: var(--font-mono);
}
```

### Requirement: Component Visual Decoration

**Requirement**: Smart components MAY use ArtDeco geometric decorations for brand identity.

#### Scenario: Card Border Decoration
**GIVEN** a card component
**WHEN** applying ArtDeco decoration
**THEN** it MAY use gold corner brackets and border accents:

```scss
.artdeco-card-decorated {
  position: relative;
  border: 1px solid rgba(212, 175, 55, 0.3);
}

.artdeco-card-decorated::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  width: 20px;
  height: 20px;
  border-top: 2px solid var(--artdeco-gold);
  border-left: 2px solid var(--artdeco-gold);
}

.artdeco-card-decorated::after {
  content: '';
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 20px;
  height: 20px;
  border-bottom: 2px solid var(--artdeco-gold);
  border-right: 2px solid var(--artdeco-gold);
}
```
