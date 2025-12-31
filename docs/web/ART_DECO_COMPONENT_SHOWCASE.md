# Art Deco Component Showcase
## MyStocks 装饰艺术组件展示

This document provides visual examples and code snippets for all Art Deco components and patterns.

---

## 1. Button Components

### Default Button

**Visual:**
```
┌─────────────────────┐
│    CLICK HERE       │  ← Transparent bg, gold border, gold text
└─────────────────────┘
```

**Hover:**
```
┌─────────────────────┐
│    CLICK HERE       │  ← Gold bg, black text, glow effect
╰─────────────────────╯  ← Gold glow shadow
```

**Code:**
```vue
<ArtDecoButton variant="default">
  Click Here
</ArtDecoButton>
```

### Solid Button

**Visual:**
```
┌─────────────────────┐
│  SUBMIT FORM        │  ← Gold bg, black text
└─────────────────────┘
```

**Hover:**
```
┌─────────────────────┐
│  SUBMIT FORM        │  ← Lighter gold bg
╰─────────────────────╯  ← Intensified glow
```

**Code:**
```vue
<ArtDecoButton variant="solid">
  Submit Form
</ArtDecoButton>
```

### Outline Button

**Visual:**
```
┌─────────────────────┐
│   LEARN MORE        │  ← Thin gold border (1px)
└─────────────────────┘
```

**Hover:**
```
┌─────────────────────┐
│   LEARN MORE        │  ← Midnight blue fill
└─────────────────────┘
```

**Code:**
```vue
<ArtDecoButton variant="outline">
  Learn More
</ArtDecoButton>
```

### Size Variants

```vue
<ArtDecoButton size="sm">Small</ArtDecoButton>
<ArtDecoButton size="md">Medium</ArtDecoButton>
<ArtDecoButton size="lg">Large</ArtDecoButton>
```

---

## 2. Card Components

### Basic Card

**Visual:**
```
┌╲──────────────────────╱┐  ← Top-right L-bracket
│ SECTION TITLE          │  ← Gold, uppercase, wide tracking
│ Description            │  ← Muted gray, normal case
├────────────────────────┤  ← Header separator (20% gold)
│                        │
│ Card content goes here │  ← Primary text color
│ with full styling      │
│                        │
┗╱──────────────────────╲┐  ← Bottom-left L-bracket
```

**Code:**
```vue
<ArtDecoCard
  title="SECTION TITLE"
  subtitle="Description"
>
  <p>Card content goes here</p>
  <p>with full styling</p>
</ArtDecoCard>
```

### Hoverable Card

**Hover Effect:**
- Border opacity: 30% → 100%
- Lift: translateY(-8px)
- Glow: Box shadow appears

**Code:**
```vue
<ArtDecoCard
  title="MARKET DATA"
  subtitle="Real-time updates"
  hoverable
>
  <p>Hover over this card to see the effect</p>
</ArtDecoCard>
```

### Clickable Card

**Code:**
```vue
<ArtDecoCard
  title="PORTFOLIO"
  subtitle="View your holdings"
  clickable
  @click="navigateToPortfolio"
>
  <p>Click to view details</p>
</ArtDecoCard>
```

### Card with Custom Footer

**Code:**
```vue
<ArtDecoCard title="ANALYSIS">
  <p>Main content here</p>

  <template #footer>
    <div class="card-footer">
      <span>Last updated: 2 minutes ago</span>
      <ArtDecoButton variant="outline" size="sm">Refresh</ArtDecoButton>
    </div>
  </template>
</ArtDecoCard>

<style scoped lang="scss">
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

---

## 3. Input Components

### Basic Input

**Visual:**
```
USERNAME                    ← Label: uppercase, small, gold
─────────────────────────    ← Border: 2px gold
Enter your username...       ← Placeholder: muted gray
```

**Focus State:**
```
USERNAME
══════════════════════════   ← Brighter gold + glow
Enter your username...
╰──────────────────────────╯  ← Glow shadow
```

**Code:**
```vue
<ArtDecoInput
  v-model="username"
  label="USERNAME"
  placeholder="Enter your username"
/>
```

### Input with Error

**Visual:**
```
USERNAME
─────────────────────────    ← Red border
Enter your username...
This field is required        ← Red error message
```

**Code:**
```vue
<ArtDecoInput
  v-model="username"
  label="USERNAME"
  placeholder="Enter your username"
  required
  errorMessage="This field is required"
/>
```

### Input with Helper Text

**Code:**
```vue
<ArtDecoInput
  v-model="email"
  label="EMAIL ADDRESS"
  type="email"
  placeholder="user@example.com"
  helperText="We'll never share your email with anyone else"
/>
```

### Input with Icon Prefix

**Code:**
```vue
<ArtDecoInput
  v-model="search"
  placeholder="Search stocks..."
>
  <template #prefix>
    <el-icon><Search /></el-icon>
  </template>
</ArtDecoInput>
```

---

## 4. Typography Examples

### Heading Hierarchy

```vue
<template>
  <div class="typography-showcase">
    <h1>LEVEL ONE HEADING</h1>      <!-- 60px, Marcellus, gold -->
    <h2>Level Two Heading</h2>      <!-- 36px -->
    <h3>Level Three Heading</h3>    <!-- 24px -->
    <h4>Level Four Heading</h4>     <!-- 20px -->
    <p>This is body text with normal spacing.</p>
    <p class="text-muted">This is muted text.</p>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

h1, h2, h3, h4, h5, h6 {
  font-family: var(--artdeco-font-display);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
  color: var(--artdeco-accent-gold);
}

p {
  font-family: var(--artdeco-font-body);
  color: var(--artdeco-fg-primary);
  line-height: var(--artdeco-leading-relaxed);
}

.text-muted {
  color: var(--artdeco-fg-muted);
}
</style>
```

### Section with Divider

**Visual:**
```
                ─────────────
                   TITLE
                ─────────────
```

**Code:**
```vue
<div class="section-header">
  <h2>MARKET OVERVIEW</h2>
</div>

<style scoped lang="scss">
@import '@/styles/artdeco-patterns.scss';

.section-header {
  @include artdeco-section-divider(120px, 1px);
  text-align: center;
  padding: var(--artdeco-spacing-6) 0;
}
</style>
```

---

## 5. Layout Patterns

### Stats Grid

**Code:**
```vue
<template>
  <el-row :gutter="24">
    <el-col :xs="24" :sm="12" :md="6">
      <ArtDecoCard :hoverable="false" class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-label">TOTAL STOCKS</div>
        <div class="stat-value">5,234</div>
        <div class="stat-trend up">+12.5%</div>
      </ArtDecoCard>
    </el-col>

    <el-col :xs="24" :sm="12" :md="6">
      <ArtDecoCard :hoverable="false" class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-label">MARKET CAP</div>
        <div class="stat-value">¥89.2B</div>
        <div class="stat-trend up">+8.3%</div>
      </ArtDecoCard>
    </el-col>

    <el-col :xs="24" :sm="12" :md="6">
      <ArtDecoCard :hoverable="false" class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-label">VOLUME</div>
        <div class="stat-value">¥12.5B</div>
        <div class="stat-trend down">-3.2%</div>
      </ArtDecoCard>
    </el-col>

    <el-col :xs="24" :sm="12" :md="6">
      <ArtDecoCard :hoverable="false" class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-label">ACTIVE</div>
        <div class="stat-value">3,891</div>
        <div class="stat-trend">0%</div>
      </ArtDecoCard>
    </el-col>
  </el-row>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.stat-card {
  text-align: center;

  :deep(.artdeco-card__content) {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--artdeco-spacing-3);
  }
}

.stat-icon {
  font-size: 32px;
  opacity: 0.8;
}

.stat-label {
  font-family: var(--artdeco-font-display);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}

.stat-value {
  font-family: var(--artdeco-font-display);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
  color: var(--artdeco-accent-gold);
  font-size: var(--artdeco-text-3xl);
}

.stat-trend {
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-weight-semibold);

  &.up {
    color: var(--artdeco-color-up); // Red for A-share up
  }

  &.down {
    color: var(--artdeco-color-down); // Green for A-share down
  }
}
</style>
```

### Two-Column Layout

```vue
<template>
  <el-row :gutter="24">
    <el-col :xs="24" :md="16">
      <ArtDecoCard title="MAIN CONTENT">
        <p>Primary content area</p>
      </ArtDecoCard>
    </el-col>

    <el-col :xs="24" :md="8">
      <ArtDecoCard title="SIDEBAR">
        <p>Secondary content</p>
      </ArtDecoCard>
    </el-col>
  </el-row>
</template>
```

---

## 6. Advanced Patterns

### Diamond Frame (Icon Container)

**Visual:**
```
    ▲
   ╱ ╲
  │   │  ← 45° rotated square
  │ ★ │  ← Icon (counter-rotated)
  │   │
   ╲ ╱
    ▼
```

**Code:**
```vue
<template>
  <div class="icon-diamond">
    <el-icon :size="24"><Star /></el-icon>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-patterns.scss';

.icon-diamond {
  @include artdeco-diamond-frame(48px);
}
</style>
```

### Double Frame (Image Container)

**Visual:**
```
┌───────────────────┐  ← Outer gold border
│ ╱───────────────╲ │
│ │               │ │
│ │   IMAGE       │ │  ← Inner dark border
│ │               │ │
│ ╲───────────────╱ │
└───────────────────┘
```

**Code:**
```vue
<template>
  <div class="image-frame">
    <img src="chart.png" alt="Market Chart" />
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-patterns.scss';

.image-frame {
  @include artdeco-double-frame(
    $outer-color: var(--artdeco-border-gold),
    $inner-color: var(--artdeco-bg-card),
    $gap: 8px
  );

  img {
    width: 100%;
    display: block;
    filter: grayscale(100%);
    transition: filter var(--artdeco-duration-base);

    &:hover {
      filter: grayscale(0%);
    }
  }
}
</style>
```

### Sunburst Effect

**Visual:**
```
    ◡◡◡◡◡
   ◡███◡███◡
  ◡██████████◡   ← Radial gold gradient
 ◡██████████████◡
```

**Code:**
```vue
<template>
  <div class="hero-section">
    <h1>MARKET ANALYSIS</h1>
    <p>Real-time insights</p>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-patterns.scss';

.hero-section {
  @include artdeco-sunburst-radial(
    $color: var(--artdeco-accent-gold),
    $opacity-start: 0.15,
    $opacity-end: 0
  );

  text-align: center;
  padding: var(--artdeco-spacing-16) 0;
}
</style>
```

### Roman Numeral Sections

**Code:**
```vue
<template>
  <div class="section" v-for="(section, index) in sections" :key="index">
    <div class="section-number">I</div>
    <h2>{{ section.title }}</h2>
    <p>{{ section.content }}</p>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.section {
  position: relative;
  padding-left: 60px;
}

.section-number {
  position: absolute;
  left: 0;
  top: 0;

  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-4xl);
  color: var(--artdeco-accent-gold);
  text-transform: uppercase;
  opacity: 0.3;
}

h2 {
  margin-left: -20px;
}
</style>
```

---

## 7. Interactive Elements

### Form Example

**Code:**
```vue
<template>
  <ArtDecoCard title="USER SETTINGS">
    <form @submit.prevent="handleSubmit">
      <ArtDecoInput
        v-model="form.username"
        label="USERNAME"
        placeholder="Enter username"
        required
      />

      <ArtDecoInput
        v-model="form.email"
        label="EMAIL"
        type="email"
        placeholder="user@example.com"
        required
        style="margin-top: 16px;"
      />

      <ArtDecoInput
        v-model="form.bio"
        label="BIOGRAPHY"
        type="textarea"
        placeholder="Tell us about yourself"
        style="margin-top: 16px;"
      />

      <div style="margin-top: 24px; display: flex; gap: 12px;">
        <ArtDecoButton variant="outline" type="button">Cancel</ArtDecoButton>
        <ArtDecoButton variant="solid" type="submit">Save Changes</ArtDecoButton>
      </div>
    </form>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  username: '',
  email: '',
  bio: ''
})

const handleSubmit = () => {
  console.log('Form submitted:', form)
}
</script>
```

### Action Bar

**Code:**
```vue
<template>
  <div class="action-bar">
    <div class="action-bar-left">
      <h2>DATA EXPORT</h2>
      <p>Select format and date range</p>
    </div>

    <div class="action-bar-right">
      <ArtDecoButton variant="outline" size="sm">Cancel</ArtDecoButton>
      <ArtDecoButton variant="solid" size="sm">Export</ArtDecoButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-5);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-gold-subtle);
  margin-bottom: var(--artdeco-spacing-6);

  h2 {
    margin: 0;
    font-size: var(--artdeco-text-xl);
  }

  p {
    margin: 0;
    color: var(--artdeco-fg-muted);
  }
}

.action-bar-right {
  display: flex;
  gap: var(--artdeco-spacing-3);
}
</style>
```

---

## 8. Data Display

### Table with Art Deco Styling

**Code:**
```vue
<template>
  <ArtDecoCard title="STOCK WATCHLIST">
    <table class="artdeco-table">
      <thead>
        <tr>
          <th>SYMBOL</th>
          <th>NAME</th>
          <TH>PRICE</TH>
          <th>CHANGE</th>
          <th>ACTION</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="stock in stocks" :key="stock.symbol">
          <td>{{ stock.symbol }}</td>
          <td>{{ stock.name }}</td>
          <td class="text-gold">{{ stock.price }}</td>
          <td :class="stock.change > 0 ? 'text-up' : 'text-down'">
            {{ stock.change > 0 ? '+' : '' }}{{ stock.change }}%
          </td>
          <td>
            <ArtDecoButton variant="outline" size="sm">Trade</ArtDecoButton>
          </td>
        </tr>
      </tbody>
    </table>
  </ArtDecoCard>
</template>

<script setup lang="ts">
const stocks = [
  { symbol: '600519', name: '贵州茅台', price: '¥1,856.00', change: 2.5 },
  { symbol: '000858', name: '五粮液', price: '¥168.50', change: -1.2 },
  { symbol: '600036', name: '招商银行', price: '¥42.30', change: 0.8 }
]
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-body);

  th {
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    color: var(--artdeco-accent-gold);
    border-bottom: 2px solid var(--artdeco-border-gold);
    padding: var(--artdeco-spacing-3);
    text-align: left;
    font-weight: var(--artdeco-weight-normal);
  }

  td {
    color: var(--artdeco-fg-primary);
    border-bottom: 1px solid var(--artdeco-border-gold-muted);
    padding: var(--artdeco-spacing-3);
  }

  tr:hover td {
    background: rgba(212, 175, 55, 0.05);
  }

  .text-gold {
    color: var(--artdeco-accent-gold);
  }

  .text-up {
    color: var(--artdeco-color-up); // Red for A-share up
  }

  .text-down {
    color: var(--artdeco-color-down); // Green for A-share down
  }
}
</style>
```

---

## 9. Full Page Example

### Dashboard Layout

```vue
<template>
  <div class="dashboard-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1>DASHBOARD</h1>
      <p>Real-time market overview</p>
    </div>

    <!-- Stats Grid -->
    <el-row :gutter="24" class="stats-grid">
      <el-col :xs="24" :sm="12" :md="6">
        <ArtDecoCard :hoverable="false">
          <div class="stat">5,234</div>
          <div class="stat-label">TOTAL STOCKS</div>
        </ArtDecoCard>
      </el-col>
      <!-- More stats... -->
    </el-row>

    <!-- Charts Section -->
    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :xs="24" :md="16">
        <ArtDecoCard title="MARKET HEAT" subtitle="Sector performance">
          <div class="chart-container" ref="chartRef"></div>
        </ArtDecoCard>
      </el-col>

      <el-col :xs="24" :md="8">
        <ArtDecoCard title="TOP MOVERS" subtitle="Gainers & losers">
          <table class="artdeco-table">
            <!-- Table content -->
          </table>
        </ArtDecoCard>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';

.dashboard-page {
  @include artdeco-crosshatch-bg();
  min-height: 100vh;
  padding: var(--artdeco-spacing-6);
}

.page-header {
  @include artdeco-section-divider(120px, 1px);
  text-align: center;
  margin-bottom: var(--artdeco-spacing-8);

  h1 {
    font-family: var(--artdeco-font-display);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    color: var(--artdeco-accent-gold);
    font-size: var(--artdeco-text-5xl);
    margin: 0 0 var(--artdeco-spacing-2) 0;
  }

  p {
    color: var(--artdeco-fg-muted);
    margin: 0;
    font-family: var(--artdeco-font-body);
  }
}

.stat {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-4xl);
  color: var(--artdeco-accent-gold);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
}

.stat-label {
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  font-size: var(--artdeco-text-xs);
  margin-top: var(--artdeco-spacing-2);
}

.chart-container {
  height: 350px;
  background: rgba(10, 10, 10, 0.3);
  border: 1px solid var(--artdeco-border-gold-muted);
}
</style>
```

---

## 10. Accessibility Examples

### Skip to Content Link

```vue
<template>
  <a href="#main-content" class="skip-to-content">
    Skip to main content
  </a>
  <main id="main-content">
    <!-- Page content -->
  </main>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.skip-to-content {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--artdeco-accent-gold);
  color: var(--artdeco-bg-primary);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  text-decoration: none;
  z-index: var(--artdeco-z-tooltip);
  font-weight: var(--artdeco-weight-medium);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);

  &:focus {
    top: 0;
  }
}
</style>
```

---

**End of Component Showcase**

For more information, see:
- [Art Deco Implementation Report](./ART_DECO_IMPLEMENTATION_REPORT.md)
- [Art Deco Quick Reference](./ART_DECO_QUICK_REFERENCE.md)
