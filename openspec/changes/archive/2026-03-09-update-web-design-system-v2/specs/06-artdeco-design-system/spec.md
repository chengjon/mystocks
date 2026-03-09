# 06-artdeco-design-system Specification

## Purpose
Defines the ArtDeco design system V3.0 requirements for MyStocks quant trading platform, including color system, typography, animation, and visual decoration standards.

## Requirements

### Requirement: ArtDeco Color System V3.0

**Requirement**: The system SHALL implement ArtDeco Financial Color System V3.0 with bold gold accents for brand recognition.

#### Scenario: Core Brand Colors
**GIVEN** the design system needs primary colors
**WHEN** defining brand colors
**THEN** use:

```css
:root {
  /* ArtDeco core brand colors */
  --artdeco-gold: #D4AF37;
  --artdeco-gold-light: #F0E68C;
  --artdeco-bronze: #CD7F32;
  --artdeco-champagne: #F7E7CE;
}
```

#### Scenario: Background Colors
**GIVEN** the design system needs background colors
**WHEN** defining backgrounds
**THEN** use:

```css
:root {
  --color-bg-primary: #1A1A1D;
  --color-bg-card: #2A2A2E;
  --color-bg-elevated: #3A3A3E;
}
```

#### Scenario: Text Colors
**GIVEN** the design system needs text colors
**WHEN** defining text colors
**THEN** use:

```css
:root {
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #B8B8B8;
  --color-text-muted: #808080;
}
```

### Requirement: Financial Data Colors (A股 Convention)

**Requirement**: Financial data colors SHALL follow Chinese stock market convention (RED=上涨, GREEN=下跌).

#### Scenario: Price Movement Colors
**GIVEN** displaying stock price movements
**WHEN** showing price changes
**THEN** use:
- Green (#00C853) for price increase (上涨)
- Red (#FF1744) for price decrease (下跌)

```css
:root {
  --color-rise: #00C853;
  --color-fall: #FF1744;
  --color-warning: #D4AF37;
  --color-danger: #D32F2F;
  --color-info: #2196F3;
}
```

### Requirement: ArtDeco Typography System

**Requirement**: The system SHALL implement a three-tier typography system for professional financial application.

#### Scenario: Display Font (Headers)
**GIVEN** headings and display text
**WHEN** applying typography
**THEN** use Cinzel font with uppercase styling:

```css
@font-face {
  font-family: 'Cinzel';
  src: url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap');
}

:root {
  --font-display: 'Cinzel', 'Playfair Display', serif;
}

h1, h2, h3, .logo, .section-title {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
```

#### Scenario: Body Font (Content)
**GIVEN** body content and descriptions
**WHEN** applying typography
**THEN** use Barlow font:

```css
@font-face {
  font-family: 'Barlow';
  src: url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&display=swap');
}

:root {
  --font-body: 'Barlow', 'Inter', sans-serif;
}

body, p, span, .body-text {
  font-family: var(--font-body);
  font-weight: 400;
}
```

#### Scenario: Monospace Font (Numbers)
**GIVEN** financial numbers, codes, and tabular data
**WHEN** applying typography
**THEN** use JetBrains Mono with tabular nums:

```css
@font-face {
  font-family: 'JetBrains Mono';
  src: url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
}

:root {
  --font-mono: 'JetBrains Mono', 'Consolas', monospace;
}

.price, .percentage, .volume, .code {
  font-family: var(--font-mono);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
```

### Requirement: ArtDeco Animation System

**Requirement**: The system SHALL implement ArtDeco-themed animations for interactions and transitions.

#### Scenario: Page Load Animation
**GIVEN** a page entering the viewport
**WHEN** animating
**THEN** use golden glow sweep effect:

```css
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
```

#### Scenario: Button Hover Animation
**GIVEN** a button receiving hover state
**WHEN** animating
**THEN** use gold radial gradient expansion:

```css
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

#### Scenario: Data Update Flash
**GIVEN** real-time data updating
**WHEN** highlighting changes
**THEN** use gold background flash:

```css
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

#### Scenario: Tab Switch Animation
**GIVEN** tab navigation
**WHEN** switching tabs
**THEN** use gold slider transition:

```css
.tab-bar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--artdeco-gold);
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```

### Requirement: ECharts ArtDeco Theme

**Requirement**: Chart components SHALL use ArtDeco theme for visual consistency.

#### Scenario: Chart Color Palette
**GIVEN** an ECharts configuration
**WHEN** setting colors
**THEN** use ArtDeco palette:

```javascript
const artDecoTheme = {
  color: ['#D4AF37', '#4A90E2', '#00C853', '#FF1744'],
  backgroundColor: '#2A2A2E'
};
```

#### Scenario: Chart Typography
**GIVEN** chart axis labels
**WHEN** setting typography
**THEN** use JetBrains Mono for numbers:

```javascript
const artDecoTheme = {
  xAxis: {
    axisLabel: {
      fontFamily: 'JetBrains Mono, monospace'
    }
  },
  yAxis: {
    axisLabel: {
      fontFamily: 'JetBrains Mono, monospace'
    }
  }
};
```

### Requirement: Design Token Usage

**Requirement**: All visual styling SHALL use design tokens rather than hard-coded values.

#### Scenario: Token-Based Styling
**GIVEN** a component needs styling
**WHEN** applying styles
**THEN** use CSS custom properties:

```css
.component {
  color: var(--color-text-primary);
  background-color: var(--color-bg-card);
  border: 1px solid var(--artdeco-gold);
  font-family: var(--font-body);
}
```

#### Scenario: Token Composition
**GIVEN** needing complex styling
**WHEN** combining tokens
**THEN** compose with CSS custom properties:

```css
.card {
  background-color: var(--color-bg-card);
  border: 1px solid rgba(var(--artdeco-gold-rgb), 0.3);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1),
              0 0 20px rgba(var(--artdeco-gold-rgb), 0.1);
}
```

### Requirement: Visual Decoration Standards

**Requirement**: Components MAY use ArtDeco geometric decorations for brand identity.

#### Scenario: Corner Bracket Decoration
**GIVEN** a card or panel
**WHEN** applying ArtDeco decoration
**THEN** use corner bracket patterns:

```css
.artdeco-decorated::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 20px;
  height: 20px;
  border-top: 2px solid var(--artdeco-gold);
  border-left: 2px solid var(--artdeco-gold);
}

.artdeco-decorated::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  border-bottom: 2px solid var(--artdeco-gold);
  border-right: 2px solid var(--artdeco-gold);
}
```

### Requirement: Compact Table Mode

**Requirement**: Table components SHALL support compact mode for professional data density.

#### Scenario: Bloomberg-Standard Density
**GIVEN** a table in professional trading context
**WHEN** using compact mode
**THEN** use 32px row height:

```css
.table-compact {
  --row-height: 32px;
  --cell-padding: 4px 8px;
}

.table-compact .row {
  height: var(--row-height);
  padding: var(--cell-padding);
}
```

### Requirement: Performance Requirements

**Requirement**: Design system implementations SHALL meet performance criteria.

#### Scenario: Animation Performance
**GIVEN** CSS animations
**WHEN** measuring performance
**THEN** achieve 60fps frame rate with GPU-accelerated properties (transform, opacity).

#### Scenario: Page Load Performance
**GIVEN** full page with design system
**WHEN** measuring load time
**THEN** complete within 2 seconds.

#### Scenario: No Layout Shift
**GIVEN** design system applied
**WHEN** rendering
**THEN** have zero cumulative layout shift (CLS).

### Requirement: Compatibility Requirements

**Requirement**: Design system SHALL maintain backward compatibility.

#### Scenario: Existing Components
**GIVEN** existing components
**WHEN** applying design system
**THEN** all MUST remain functional with enhanced styling.

#### Scenario: Responsive Design
**GIVEN** design system
**WHEN** rendering at 1440px+
**THEN** maintain layout integrity.

#### Scenario: Browser Support
**GIVEN** modern browsers
**WHEN** using design system
**THEN** support Chrome, Firefox, Safari, Edge.
