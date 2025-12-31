# Bitcoin DeFi Web3 Design System Documentation

**MyStocks Quantitative Trading Platform - Web3 Design System**

**Version**: 1.0.0
**Last Updated**: 2025-12-30
**Status**: Production Ready

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing System](#spacing-system)
5. [Border Radius](#border-radius)
6. [Shadows & Glows](#shadows--glows)
7. [Component Styles](#component-styles)
8. [Patterns & Textures](#patterns--textures)
9. [Animation & Motion](#animation--motion)
10. [Accessibility](#accessibility)
11. [Implementation Examples](#implementation-examples)

---

## Design Philosophy

### Core Principles

**"Secure, Technical, and Valuable"**

The MyStocks Web3 design system embodies the essence of Bitcoin DeFi aesthetics:

1. **Digital Gold**: Orange (#F7931A) represents value, energy, and Bitcoin's fire
2. **True Void**: Deep black background (#030304) creates infinite depth
3. **Precision Engineering**: Grid patterns, aligned data, mathematical perfection
4. **Cryptographic Trust**: Luminescent glows, layered depth, living interface
5. **Technical Sophistication**: Glass morphism, radial blurs, neon effects

### Visual DNA

| Element | Description | Usage |
|---------|-------------|-------|
| **True Void** | #030304 | Main background |
| **Dark Matter** | #0F1115 | Cards/surfaces |
| **Bitcoin Orange** | #F7931A | Primary accent, CTAs |
| **Digital Gold** | #FFD600 | Gradients, highlights |
| **Grid Pattern** | 50px mesh | Blockchain network effect |

---

## Color System

### Background Colors

```scss
// SCSS Variables
$web3-bg-primary: #030304;      // True void (main background)
$web3-bg-surface: #0F1115;      // Dark matter (cards)
$web3-bg-overlay: rgba(3, 3, 4, 0.92);  // Modal overlays
$web3-bg-glass-light: rgba(255, 255, 255, 0.05);  // Glass morphism
$web3-bg-glass-dark: rgba(0, 0, 0, 0.40);  // Dark glass

// CSS Custom Properties
--web3-bg-primary: #030304;
--web3-bg-surface: #0F1115;
--web3-bg-glass-light: rgba(255, 255, 255, 0.05);
```

### Foreground Colors

```scss
$web3-fg-primary: #FFFFFF;      // Pure light (text)
$web3-fg-secondary: #94A3B8;    // Stardust (secondary text)
$web3-fg-muted: #64748B;        // Dim boundary (disabled)
```

### Accent Colors (Bitcoin DeFi)

```scss
$web3-accent-primary: #F7931A;  // Bitcoin orange
$web3-accent-secondary: #EA580C; // Burnt orange
$web3-accent-gold: #FFD600;     // Digital gold
```

### Gradients

```scss
// Orange fire gradient
$web3-gradient-orange: linear-gradient(to right, #EA580C, #F7931A);

// Gold gradient
$web3-gradient-gold: linear-gradient(to right, #F7931A, #FFD600);
```

### Market Colors (A-Share)

```scss
$web3-color-up: #FF5252;        // Red (上涨)
$web3-color-down: #00E676;      // Green (下跌)
$web3-color-flat: #B0B3B8;      // Gray (平盘)
```

---

## Typography

### Font Families

```scss
// Headings (Space Grotesk - technical, modern)
$web3-font-heading: 'Space Grotesk', sans-serif;

// Body text (Inter - clean, readable)
$web3-font-body: 'Inter', sans-serif;

// Monospace data (JetBrains Mono - code, financial data)
$web3-font-mono: 'JetBrains Mono', monospace;
```

**Google Fonts Import**:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Font Sizes

| Token | Size | Usage |
|-------|------|-------|
| `--web3-text-xs` | 12px | Small labels, captions |
| `--web3-text-sm` | 14px | Secondary text, menu items |
| `--web3-text-base` | 16px | Body text, input fields |
| `--web3-text-lg` | 18px | Emphasized body text |
| `--web3-text-xl` | 20px | Small headings |
| `--web3-text-2xl` | 24px | H4, card titles |
| `--web3-text-3xl` | 30px | H3 (mobile) |
| `--web3-text-4xl` | 36px | H2 (mobile), H3 (desktop) |
| `--web3-text-5xl` | 48px | H1 (mobile), H2 (desktop) |
| `--web3-text-6xl` | 60px | Large hero |
| `--web3-text-7xl` | 72px | Massive hero |

**Dramatic Contrast**: Heroes are massive (`text-4xl → md:text-7xl`), body is comfortable (`text-base` or `text-lg`).

### Font Weights

```scss
$web3-weight-normal: 400;       // Regular body text
$web3-weight-medium: 500;       // Emphasized text
$web3-weight-semibold: 600;     // Headings, buttons
$web3-weight-bold: 700;         // Logo, CTAs
```

### Letter Spacing

```scss
$web3-tracking-tight: -0.02em;  // Compact text
$web3-tracking-normal: 0em;     // Body text
$web3-tracking-wide: 0.025em;   // Slightly spaced
$web3-tracking-wider: 0.05em;   // Uppercase labels
$web3-tracking-widest: 0.1em;   // Logo, extreme emphasis
```

---

## Spacing System

**Base Unit**: 4px

| Token | Value | Usage |
|-------|-------|-------|
| `--web3-spacing-0` | 0 | None |
| `--web3-spacing-1` | 4px | Micro spacing |
| `--web3-spacing-2` | 8px | Tight spacing |
| `--web3-spacing-3` | 12px | Compact spacing |
| `--web3-spacing-4` | 16px | Default spacing |
| `--web3-spacing-5` | 20px | Comfortable spacing |
| `--web3-spacing-6` | 24px | Loose spacing |
| `--web3-spacing-8` | 32px | Section spacing |
| `--web3-spacing-10` | 40px | Large spacing |
| `--web3-spacing-12` | 48px | XL spacing |
| `--web3-spacing-16` | 64px | XXL spacing |
| `--web3-spacing-20` | 80px | Section separation |
| `--web3-spacing-24` | 96px | Hero separation |

---

## Border Radius

```scss
$web3-radius-none: 0;           // Sharp corners
$web3-radius-sm: 8px;           // Inputs, small elements
$web3-radius-md: 12px;          // Medium cards
$web3-radius-lg: 16px;          // Large cards (default)
$web3-radius-xl: 20px;          // Modals
$web3-radius-full: 9999px;      // Pill buttons
```

**Usage Rules**:
- **Cards**: `rounded-2xl` (16px) - elevated surfaces, "blocks in the chain"
- **Buttons**: `rounded-full` (pill) - emit colored light
- **Inputs**: `rounded-lg` (8px) or bottom-border only

---

## Shadows & Glows

### Orange Glow (Signature Effect)

```scss
// Subtle orange glow
$web3-glow-orange-sm: 0 0 20px -5px rgba(234, 88, 12, 0.3);

// Medium orange glow (default)
$web3-glow-orange-md: 0 0 20px -5px rgba(234, 88, 12, 0.5);

// Usage
box-shadow: var(--web3-glow-orange-md);
```

### Gold Glow

```scss
$web3-glow-gold: 0 0 20px rgba(255, 214, 0, 0.3);
```

### Card Elevation

```scss
$web3-glow-card: 0 0 50px -10px rgba(247, 147, 26, 0.1);
```

### Traditional Drop Shadows (Minimal Use)

```scss
$web3-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$web3-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
$web3-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

---

## Component Styles

### Buttons

#### Primary Button (Orange Fire Gradient)

```vue
<Web3Button variant="primary" size="md">
  Confirm Transaction
</Web3Button>
```

**Characteristics**:
- Pill-shaped (`rounded-full`)
- Orange fire gradient background
- White bold uppercase text
- Orange glow shadow
- Hover: Intensified glow

#### Outline Button

```vue
<Web3Button variant="outline" size="sm">
  Cancel
</Web3Button>
```

**Characteristics**:
- Transparent background
- Border: 2px solid white/20
- Hover: Border orange + glow

#### Ghost Button

```vue
<Web3Button variant="ghost" size="lg">
  Learn More
</Web3Button>
```

**Characteristics**:
- Transparent background
- No border
- Hover: Glass morphism background

### Cards

#### Default Card

```vue
<Web3Card title="MARKET OVERVIEW" hoverable>
  <p>Card content here...</p>
</Web3Card>
```

**Characteristics**:
- Dark matter background (#0F1115)
- Rounded corners (16px)
- Ultra-thin border (white/10)
- Corner border accents (Bitcoin orange)
- Hover: Lift + orange glow

#### Glass Card

```vue
<Web3Card variant="glass" hoverable>
  <p>Glass morphism content...</p>
</Web3Card>
```

**Characteristics**:
- Glass morphism (backdrop-blur: 16px)
- Background: white/5
- Stronger border

### Inputs

```vue
<Web3Input
  v-model="value"
  label="Wallet Address"
  placeholder="Enter address..."
  size="md"
/>
```

**Characteristics**:
- Glass morphism background
- Bottom border only (2px)
- Focus: Orange border + glow
- Monospace font for values

---

## Patterns & Textures

### Grid Pattern (Blockchain Network Effect)

**MANDATORY**: This is the signature Web3 pattern

```scss
@mixin web3-grid-bg {
  background-color: var(--web3-bg-primary);
  background-size: 50px 50px;
  background-image:
    linear-gradient(to right, rgba(30, 41, 59, 0.5) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(30, 41, 59, 0.5) 1px, transparent 1px);
  mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
  -webkit-mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
}
```

**Usage**: Apply to main background, sidebar, content areas

### Glass Morphism

```scss
@mixin web3-glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

**Usage**: Headers, floating panels, overlay cards

### Radial Blur Glow

```scss
@mixin web3-radial-glow {
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, #F7931A 0%, transparent 70%);
    opacity: 0.10;
    filter: blur(120px);
    pointer-events: none;
    z-index: 0;
  }
}
```

---

## Animation & Motion

### GPU-Accelerated Animations Only

```scss
// Float animation (hero elements)
@keyframes web3-float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

// Spin animation (orbital rings)
@keyframes web3-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// Bounce animation (stat cards)
@keyframes web3-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

// Pulse animation (live indicators)
@keyframes web3-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

// Ping animation (badges)
@keyframes web3-ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}
```

### Transition Timing

```scss
$web3-duration-fast: 150ms;     // Micro-interactions
$web3-duration-base: 200ms;     // Default transitions
$web3-duration-slow: 300ms;     // Complex animations

$web3-ease-out: cubic-bezier(0, 0, 0.2, 1);
$web3-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

---

## Accessibility

### WCAG AA Compliance

**Contrast Ratios**:
- Normal text: 7.1:1 (white on #030304) ✅
- Large text: 12.6:1 ✅
- Orange accent: 3.1:1 (use for large text only) ✅

### Focus States

```scss
*:focus-visible {
  outline: 2px solid var(--web3-accent-primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(247, 147, 26, 0.1);
}
```

### Screen Readers

```html
<!-- Skip to content link -->
<a href="#main-content" class="skip-to-content">
  Skip to main content
</a>

<!-- Screen reader only text -->
<span class="sr-only">Hidden text for screen readers</span>
```

---

## Implementation Examples

### Gradient Text on Headlines

**MANDATORY**: Apply to hero headlines

```vue
<h1 class="text-gradient">
  MARKET OVERVIEW
</h1>

<style scoped>
.text-gradient {
  background: var(--web3-gradient-gold);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
</style>
```

### Corner Border Accents

**Decorative corner borders in Bitcoin orange**

```vue
<div class="card-with-corners">
  <!-- Card content -->
</div>

<style scoped>
.card-with-corners {
  position: relative;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border-color: var(--web3-accent-primary);
    opacity: 0.6;
  }

  &::before {
    top: 12px;
    left: 12px;
    border-top: 2px solid;
    border-left: 2px solid;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-bottom: 2px solid;
    border-right: 2px solid;
  }
}
</style>
```

### Glowing Animated Badges

**Pulsing dot badges**

```vue
<div class="status-badge">
  <span class="status-dot animate-ping"></span>
  <span>Live</span>
</div>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--web3-accent-primary);
  border-radius: 50%;
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}
```

---

## File Structure

```
web/frontend/src/
├── styles/
│   ├── web3-tokens.scss       # Design tokens (colors, fonts, spacing)
│   ├── web3-global.scss       # Global styles, animations, utilities
│   └── web3-patterns.scss     # Reusable patterns (optional)
├── components/
│   └── web3/
│       ├── Web3Button.vue     # Pill button with gradient
│       ├── Web3Card.vue       # Elevated card with glow
│       ├── Web3Input.vue      # Bottom-border input
│       └── index.ts           # Component exports
└── layouts/
    └── MainLayout.vue         # Main layout (Web3 styled)
```

---

## Quick Reference

### Essential CSS Variables

```css
/* Colors */
--web3-bg-primary: #030304;
--web3-bg-surface: #0F1115;
--web3-accent-primary: #F7931A;
--web3-fg-primary: #FFFFFF;

/* Typography */
--web3-font-heading: 'Space Grotesk', sans-serif;
--web3-font-body: 'Inter', sans-serif;
--web3-font-mono: 'JetBrains Mono', monospace;

/* Radius */
--web3-radius-full: 9999px;  /* Buttons */
--web3-radius-lg: 16px;      /* Cards */

/* Effects */
--web3-glow-orange-md: 0 0 20px -5px rgba(234, 88, 12, 0.5);
--web3-glow-card: 0 0 50px -10px rgba(247, 147, 26, 0.1);
```

---

## Migration Notes

### From ArtDeco to Web3

| Aspect | ArtDeco | Web3 |
|--------|---------|------|
| Background | #0A0A0A | #030304 |
| Primary Accent | Gold #D4AF37 | Bitcoin Orange #F7931A |
| Heading Font | Marcellus | Space Grotesk |
| Body Font | Josefin Sans | Inter |
| Card Radius | 0px (sharp) | 16px (rounded) |
| Button Shape | Rectangular | Pill (rounded-full) |
| Border Width | 2px | 1px (ultra-thin) |
| Shadows | Black shadows | Orange/gold glows |
| Patterns | Diagonal crosshatch | Grid pattern |

---

## Best Practices

1. **Always use CSS variables** instead of hardcoded values
2. **Apply grid pattern** to main backgrounds
3. **Use gradient text** for hero headlines
4. **Add orange glow** to interactive elements
5. **Implement glass morphism** for floating panels
6. **Round buttons as pills** (rounded-full)
7. **Round cards as 16px** (rounded-2xl)
8. **Use monospace font** for financial data
9. **GPU-accelerate animations** (will-change, transform)
10. **Maintain WCAG AA** contrast ratios

---

**End of Documentation**

For questions or updates, contact the MyStocks Frontend Team.
