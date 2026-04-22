# MyStocks Design System
Dark-mode, gold-accented quantitative trading terminal — ArtDeco luxury meets fintech precision.

## Overview

MyStocks is a dark-mode design system for personal quantitative trading and stock analysis. It fuses the theatrical elegance of Art Deco (gold accents, geometric patterns, serif headlines) with the data-density demands of a Bloomberg-style terminal. The system is optimized for **A-share markets** (Chinese stock convention: red = profit/up, green = loss/down), single-user desktop deployment, and split-second decision-making in volatile environments.

---

## ArtDeco Brand DNA

### Core Principles

- **Geometry as decoration**: use structured lines, measured frames, repeated motifs, and architectural rhythm rather than soft organic ornament.
- **Contrast as drama**: preserve the obsidian-black and metallic-gold contrast so hierarchy remains ceremonial and premium.
- **Verticality and symmetry**: prefer balanced compositions, column rhythm, and upward emphasis in dashboards, hero headers, and framed analysis panels.
- **Theatrical restraint**: interactive feedback should feel deliberate and engineered, not playful or bouncy.

### Visual Signatures

- **Diagonal crosshatch**: the background grid remains the primary ambient ArtDeco texture for the active runtime.
- **Gold glow over drop shadow**: emphasis should come from gold luminescence and controlled halo layers, not generic black shadow stacks.
- **Uppercase display typography**: display headings remain serif, uppercase, and widely tracked.
- **Double-frame and divider language**: framed panels, measured separators, and geometric section dividers are preferred over soft card-only grouping.
- **Roman numeral / rotated diamond motifs**: allowed as secondary brand accents in overview, onboarding, attribution, and storytelling surfaces.

### Usage Boundaries

- **Data-dense and execution-critical surfaces**: trading, risk, monitoring, order, and real-time watch panels default to restrained decoration and prioritize scanability.
- **Brand-forward surfaces**: overview dashboards, empty states, feature intros, strategy summaries, and explanatory analysis cards may use stronger ArtDeco motifs when they do not compete with core data.
- **Financial semantics override ornament**: profit/loss state, risk state, execution status, and stale-data feedback always take priority over decorative gold treatment.

### Runtime Exceptions

- **Decorative corner markers remain globally disabled in the current project runtime.** Historical stepped-corner and corner-bracket treatments caused overlap with existing UI elements and degraded visual clarity, so they are intentionally kept off even though they are part of the broader ArtDeco mother-style vocabulary.
- **Stepped-corner language may still be referenced conceptually** in layout framing, divider rhythm, and sharp geometry, but not through globally rendered corner marker elements unless a future implementation proves non-overlapping.

---

## Comparative Analysis: CoinPulse vs ArtDeco

| Dimension | CoinPulse (Reference) | ArtDeco (Current System) | MyStocks Decision |
|-----------|----------------------|--------------------------|-------------------|
| **Theme** | Permanent dark, no light mode | Permanent dark, forced `color-scheme: dark` | Keep permanent dark only |
| **Primary Accent** | Electric Blue `#2563EB` | Classical Gold `#D4AF37` | Gold (brand identity) |
| **Market Convention** | Western: green=profit, red=loss | A-Share: red=up/profit, green=down/loss | A-Share convention (no change) |
| **Headline Font** | Space Mono (monospace) | Cinzel / Marcellus (serif) | Keep Cinzel (ArtDeco identity) |
| **Body Font** | DM Sans | Barlow / Josefin Sans | Keep Barlow (cleaner for data) |
| **Data Font** | Space Mono | JetBrains Mono | Keep JetBrains Mono (tabular nums) |
| **Background** | Pure black `#09090B` | Obsidian `#0A0A0A` | Keep obsidian (nearly identical) |
| **Surface** | Dark zinc `#18181B` | Charcoal `#141414` | Keep charcoal (warmer tone) |
| **Elevation** | Blue/green/red glow shadows | Gold glow shadows | Keep gold glow (brand consistency) |
| **Spacing** | 4px base, compact | 4px base, 13-step scale | Keep 13-step scale (more flexible) |
| **Border Radius** | 4-16px range | 0-16px (ArtDeco sharp preferred) | Keep sharp-first (ArtDeco DNA) |
| **Transitions** | 150-300ms snappy | 200-800ms theatrical | Use hybrid: 200ms data, 400ms decorative |
| **Data Density** | High (crypto trading) | Medium-high | Adopt CoinPulse compact mode for tables |
| **Animation** | Minimal, data-focused | Theatrical (gold shimmer, crosshatch) | Reduce decorative animation in data views |

### Key Takeaways from CoinPulse

1. **Data-first animations**: CoinPulse uses brief color flashes for price changes — adopt this for real-time data
2. **Tabular numerics everywhere**: Mandatory `font-variant-numeric: tabular-nums` for all financial figures
3. **Single primary action per panel**: Prevent costly misclicks in trading interfaces
4. **Glow-based elevation**: Colored shadows instead of traditional drop shadows — ArtDeco already does this with gold
5. **Compact component padding**: CoinPulse uses 8px horizontal / 4px vertical — adopt for data-dense views

---

## Colors

### Brand Palette

- **Primary** (#D4AF37): Classical Gold — brand identity, CTAs, active states, headlines
- **Primary Light** (#F0E68C): Champagne — hover states, highlights, gradient endpoints
- **Primary Dark** (#8B7355): Dim Gold — shadows, subtle borders, inactive accents
- **Bronze** (#CD7F32): Bronze — secondary accent, badges, tertiary actions

### Backgrounds

- **Background** (#0A0A0A): Obsidian Black — root canvas, app background
- **Surface** (#141414): Rich Charcoal — cards, panels, modals
- **Elevated** (#1A1A1A): Warm Charcoal — dropdowns, tooltips, overlays
- **Header** (#111118): Deep Navy-Black — sidebar, top bar, navigation

### Foregrounds

- **Primary Text** (#F2F0E4): Champagne Cream — main body text, headings
- **Muted Text** (#A0A0A0): Anchor Gray — secondary text, timestamps (WCAG AA compliant)
- **Subtle Text** (rgba(255,255,255,60%)): Ghost White — placeholders, hints, disabled

### Financial Colors (A-Share Convention)

> **Critical**: This system follows the Chinese A-share market convention.
> Red = up/profit, Green = down/loss. This is the OPPOSITE of Western convention.

- **Up / Profit** (#FF5252): A-Share Red — rising prices, gains, positive deltas
- **Down / Loss** (#00E676): A-Share Green — falling prices, losses, negative deltas
- **Flat / Neutral** (#B0B3B8): Neutral Gray — unchanged, flat, baseline

### Semantic Colors

- **Success** (#FF5252): Maps to Up/Profit (A-Share convention)
- **Error** (#00E676): Maps to Down/Loss (A-Share convention)
- **Warning** (#D4AF37): Classical Gold — reuses brand color for warnings
- **Info** (#4FC3F7): Sky Blue — informational banners, links, tooltips

### Border System

- **Default** (rgba(212,175,55,30%)): Gold at 30% — standard borders
- **Hover** (rgba(212,175,55,100%)): Full Gold — interactive hover borders
- **Accent** (rgba(212,175,55,80%)): Gold at 80% — emphasis borders
- **Gold** (#D4AF37): Solid Gold — decorative elements, ArtDeco accents

---

## Typography

### Font Families

- **Display Font**: Cinzel (ArtDeco geometric serif) — headlines, logo, section titles
- **Body Font**: Barlow (modern sans-serif) — body text, labels, UI elements
- **Data Font**: JetBrains Mono (monospace) — prices, volumes, percentages, codes

### Type Scale

| Token | Size | Usage |
|-------|------|-------|
| `text-6xl` | 64px (4rem) | Hero / dramatic title |
| `text-5xl` | 48px (3rem) | Page title |
| `text-4xl` | 44px (2.75rem) | Section hero |
| `text-3xl` | 36px (2.25rem) | Large heading |
| `text-2xl` | 30px (1.875rem) | Section heading |
| `text-xl` | 24px (1.5rem) | Card heading |
| `text-lg` | 20px (1.25rem) | Sub-heading |
| `text-base` | 16px (1rem) | Body text |
| `text-sm` | 14px (0.875rem) | Helper text |
| `text-xs` | 12px (0.75rem) | Labels, captions |

### Compact Type Scale (Data-Dense Views)

| Token | Size | Usage |
|-------|------|-------|
| `text-compact-xs` | 11px | Micro labels |
| `text-compact-sm` | 12px | Table cells |
| `text-compact-base` | 14px | Compact body |
| `text-compact-md` | 16px | Compact heading |
| `text-compact-lg` | 18px | Compact title |

### Type Rules

- **Headings**: Cinzel, uppercase, `letter-spacing: 0.05em-0.1em`, gold color
- **Body**: Barlow, normal case, `letter-spacing: normal`, champagne cream
- **Financial Data**: JetBrains Mono, `font-variant-numeric: tabular-nums`, `letter-spacing: 0.02em`
- **Weights**: Light 400, Normal 400, Medium 500, Semibold 600, Bold 700

---

## Spacing

### Base Unit: 4px

### Standard Scale (13 steps)

| Token | Value | Usage |
|-------|-------|-------|
| `spacing-1` | 4px (0.25rem) | Inline gaps, icon margins |
| `spacing-2` | 8px (0.5rem) | Compact padding, list items |
| `spacing-3` | 12px (0.75rem) | Card inner padding |
| `spacing-4` | 16px (1rem) | Standard padding |
| `spacing-5` | 20px (1.25rem) | Section inner |
| `spacing-6` | 24px (1.5rem) | Section gaps |
| `spacing-8` | 32px (2rem) | Content spacing |
| `spacing-10` | 40px (2.5rem) | Large gaps |
| `spacing-12` | 48px (3rem) | Section dividers |
| `spacing-16` | 64px (4rem) | Page sections |
| `spacing-20` | 80px (5rem) | Major sections |
| `spacing-24` | 96px (6rem) | Hero spacing |
| `spacing-32` | 128px (8rem) | Full-page separators |

### Compact Spacing (Data-Dense Views)

| Token | Value | Usage |
|-------|-------|-------|
| `compact-xs` | 4px | Table cell padding |
| `compact-sm` | 8px | Compact card padding |
| `compact-md` | 12px | Compact section padding |
| `compact-lg` | 16px | Compact container padding |

---

## Border Radius

- **None** (0px): ArtDeco standard — data rows, table cells, most containers
- **Small** (2px): Minimal softening — tags, small badges
- **Medium** (8px): Cards, inputs, modals
- **Large** (12px): Special panels, feature cards
- **XL** (16px): Hero sections, prominent containers
- **Full** (9999px): Avatars, status indicators, pill buttons

> **Philosophy**: ArtDeco favors sharp, geometric lines. Default to `none` for data components. Use `medium` only for interactive elements (buttons, inputs).

---

## Elevation

### Philosophy: Gold luminescence, not black drop shadows.

| Level | Value | Usage |
|-------|-------|-------|
| **None** | `0 0 #0000` | Flat elements |
| **SM** | `0 1px 2px rgba(0,0,0,5%)` | Subtle lift |
| **MD** | `0 4px 6px -1px rgba(0,0,0,10%)` | Cards |
| **LG** | `0 10px 15px -3px rgba(0,0,0,10%)` | Elevated panels |
| **XL** | `0 20px 25px -5px rgba(0,0,0,10%)` | Modals, drawers |

### Gold Glow Effects (ArtDeco Signature)

| Level | Value | Usage |
|-------|-------|-------|
| **Subtle** | `0 0 15px rgba(212,175,55,20%)` | Hover states |
| **Intense** | `0 0 20px rgba(212,175,55,40%)` | Active focus |
| **Maximum** | `0 0 30px rgba(212,175,55,60%)` | Hero emphasis |

### Financial Glow Effects (from CoinPulse)

| Level | Value | Usage |
|-------|-------|-------|
| **Profit** | `0 0 12px rgba(255,82,82,30%)` | Profit indicators |
| **Loss** | `0 0 12px rgba(0,230,118,30%)` | Loss indicators |

---

## Components

### Buttons

#### Variants
- **Primary**: #D4AF37 fill, #0A0A0A text, no border. Hover: #F0E68C, gold glow.
- **Secondary**: transparent fill, #D4AF37 text, 1px rgba(212,175,55,30%) border. Hover: bg rgba(212,175,55,10%).
- **Ghost**: transparent fill, #A0A0A0 text, no border. Hover: bg #1A1A1A, text #F2F0E4.
- **Danger**: #00E676 fill (A-Share down=green), #0A0A0A text. Hover: brighter green + glow.

#### Sizes
| Size | Height | Padding | Font | Radius |
|------|--------|---------|------|--------|
| Small | 28px | 8px 12px | 12px | 2px |
| Medium | 36px | 8px 16px | 14px | 2px |
| Large | 44px | 12px 24px | 16px | 2px |

#### States
- **Disabled**: 0.4 opacity, disabled cursor, no glow effects
- **Loading**: Gold spinner replaces text content

### Cards

| State | Background | Border | Radius | Padding | Shadow |
|-------|-----------|--------|--------|---------|--------|
| Default | #141414 | 1px rgba(212,175,55,30%) | 8px | 16px | none |
| Elevated | #1A1A1A | 1px rgba(212,175,55,80%) | 8px | 20px | gold glow subtle |
| Hover | #141414 | 1px #D4AF37 | 8px | 16px | gold glow intense |
| Compact (data) | #141414 | 1px rgba(212,175,55,20%) | 0px | 12px | none |

### Inputs

| State | Border | Fill | Text | Shadow |
|-------|--------|------|------|--------|
| Default | 1px rgba(212,175,55,30%) | #141414 | #F2F0E4 | none |
| Hover | 1px rgba(212,175,55,80%) | #141414 | #F2F0E4 | none |
| Focus | 1px #D4AF37 | #141414 | #F2F0E4 | gold glow subtle |
| Error | 1px #00E676 | #141414 | #F2F0E4 | loss glow |
| Disabled | 1px rgba(212,175,55,10%) | #0A0A0A | #8B7355 | none |

- Height: 36px, Padding: 8px 12px, Radius: 2px
- Label: 12px / 500 / #A0A0A0, 4px below
- Helper text: 12px / 400 / #8B7355, 4px above

### Filter Chips

| State | Background | Text | Border |
|-------|-----------|------|--------|
| Default | rgba(212,175,55,8%) | #A0A0A0 | rgba(212,175,55,20%) |
| Active | rgba(212,175,55,20%) | #D4AF37 | #D4AF37 |

- Radius: 2px, Padding: 4px 8px
- Use for: market/sector/indicator filters

### Status Chips

| Type | Background | Text | Border |
|------|-----------|------|--------|
| Up/Profit | rgba(255,82,82,10%) | #FF5252 | rgba(255,82,82,20%) |
| Down/Loss | rgba(0,230,118,10%) | #00E676 | rgba(0,230,118,20%) |
| Warning | rgba(212,175,55,10%) | #D4AF37 | rgba(212,175,55,20%) |
| Neutral | rgba(255,255,255,5%) | #A0A0A0 | rgba(255,255,255,10%) |
| Holding | rgba(79,195,247,10%) | #4FC3F7 | rgba(79,195,247,20%) |
| Pending | rgba(255,167,38,10%) | #FFA726 | rgba(255,167,38,20%) |

### Data Tables

- Font: JetBrains Mono, 12-13px
- Header: 8px 12px padding, #A0A0A0 text, rgba(212,175,55,30%) bottom border
- Cell: 4px 12px padding (compact), rgba(212,175,55,10%) row dividers
- Hover: rgba(212,175,55,5%) background
- Selected: rgba(212,175,55,15%) background, left 2px #D4AF37 border

### Tooltips

- Background: #1A1A1A, Text: #F2F0E4 at 12px/400
- Padding: 6px 10px, Radius: 2px, Max-width: 240px
- Arrow: 6px, same background color
- Delay: show 300ms / hide 0ms (financial data demands speed)

### Overlay/Backdrop

- Background: rgba(0,0,0,60%), Blur: 2px
- Z-index: 40 (compatible with Element Plus Dialog/Drawer)

---

## Component State Machine

> Token pattern: `--ad-{component}-{property}-{state}`. Element Plus handles logic; these tokens override visuals only.

### Button State Table

| State | Border | Background | Text | Shadow |
|-------|--------|-----------|------|--------|
| Default | rgba(212,175,55,30%) | #D4AF37 | #0A0A0A | none |
| Hover | #D4AF37 | #F0E68C | #0A0A0A | gold glow subtle |
| Focus | #D4AF37 | #D4AF37 | #0A0A0A | gold glow medium |
| Error | #00E676 | #00E676 | #0A0A0A | loss glow |
| Disabled | rgba(212,175,55,10%) | #141414 | #8B7355 | none |

### Input State Table

| State | Border | Background | Text | Shadow |
|-------|--------|-----------|------|--------|
| Default | rgba(212,175,55,30%) | #141414 | #F2F0E4 | none |
| Hover | rgba(212,175,55,80%) | #141414 | #F2F0E4 | none |
| Focus | #D4AF37 | #141414 | #F2F0E4 | gold glow subtle |
| Error | #00E676 | #141414 | #F2F0E4 | loss glow |
| Disabled | rgba(212,175,55,10%) | #0A0A0A | #8B7355 | none |

### Card State Table

| State | Border | Background | Shadow |
|-------|--------|-----------|--------|
| Default | rgba(212,175,55,30%) | #141414 | none |
| Elevated | rgba(212,175,55,80%) | #1A1A1A | gold glow subtle |
| Hover | #D4AF37 | #141414 | gold glow intense |

### Table Row State Table

| State | Background | Border |
|-------|-----------|--------|
| Default | transparent | rgba(212,175,55,10%) divider |
| Hover | rgba(212,175,55,5%) | — |
| Selected | rgba(212,175,55,15%) | left 2px solid #D4AF37 |

---

## Financial Semantic Glow

> Extension of the gold glow system with market-state awareness. Retains gold brand identity while adding directional feedback.

| Token | Value | Usage |
|-------|-------|-------|
| `glow-subtle` | 0 0 15px rgba(212,175,55,20%) | Default hover |
| `glow-medium` | 0 0 18px rgba(212,175,55,30%) | Active focus |
| `glow-intense` | 0 0 20px rgba(212,175,55,40%) | Strong emphasis |
| `glow-max` | 0 0 30px rgba(212,175,55,60%) | Hero elements |
| **`glow-profit`** | 0 0 12px rgba(255,82,82,30%) | Profit/up indicators |
| **`glow-loss`** | 0 0 12px rgba(0,230,118,30%) | Loss/down indicators |

---

## Transitions

### Hybrid Approach (CoinPulse speed + ArtDeco drama)

| Token | Duration | Usage |
|-------|----------|-------|
| `transition-quick` | 200ms | Data updates, micro-interactions |
| `transition-base` | 300ms | Standard UI transitions |
| `transition-slow` | 400ms | Decorative effects, card hover |
| `transition-dramatic` | 600ms | Page transitions, hero elements |

### Easing

| Token | Value | Usage |
|-------|-------|-------|
| `ease-linear` | linear | Spinners, progress |
| `ease-in` | cubic-bezier(0.4, 0, 1, 1) | Elements leaving |
| `ease-out` | cubic-bezier(0, 0, 0.2, 1) | Elements entering |
| `ease-in-out` | cubic-bezier(0.4, 0, 0.2, 1) | State changes |

### Data Animations (from CoinPulse)

```css
/* Price flash — brief color burst on data change */
@keyframes price-flash-up {
  0%, 100% { background-color: transparent; }
  50% { background-color: rgba(255, 82, 82, 20%); }
}

@keyframes price-flash-down {
  0%, 100% { background-color: transparent; }
  50% { background-color: rgba(0, 230, 118, 20%); }
}

/* ArtDeco gold shimmer for page load */
@keyframes artdeco-shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
```

### Motion Governance

| Motion Class | Duration | Easing | Allowed Use | Forbidden Use |
|-------------|----------|--------|-------------|---------------|
| `data-critical` | 120-200ms | `ease-out` | Price ticks, row updates, order acknowledgements, hover on dense controls | Looping shimmer, bounce, parallax |
| `ui-standard` | 200-300ms | `ease-in-out` | Dropdowns, tabs, drawers, focus transitions | Live market cells |
| `decorative` | 320-400ms | `ease-out` | Page reveal, empty states, hero framing, section entrance | Trading rows, order book, risk alerts |
| `persistent` | 1000ms+ | linear only | Loaders, progress indicators | Decorative ambient motion |

- **Rule**: one data refresh should trigger at most one highlight effect per changed datum.
- **Rule**: flashing effects must fade back to resting state within `200ms`; no lingering glow on unchanged data.
- **Rule**: when more than 5 values update simultaneously, prefer row-level flash over per-cell flash to reduce noise.
- **Rule**: decorative motion must pause or disappear in compact/data-dense modes.
- **Rule**: all motion must degrade to opacity-only or no animation under `prefers-reduced-motion: reduce`.

### Financial Feedback

#### Price Change Response
- **Tick up / profit**: brief red flash (`rgba(255,82,82,20%)`) plus optional soft text glow for 120-160ms.
- **Tick down / loss**: brief green flash (`rgba(0,230,118,20%)`) plus optional soft text glow for 120-160ms.
- **Flat / unchanged**: no flash; preserve visual silence.
- **Large move threshold**: when move magnitude exceeds local alert threshold, add one extra border accent pulse, not a second background flash.

#### Profit / Loss Glow Semantics
- **Profit glow**: use around realized/unrealized PnL summaries, winning position cards, confirmed take-profit events.
- **Loss glow**: use around drawdown warnings, losing position cards, stop-loss triggers, breach banners.
- **Neutral rule**: never apply profit/loss glow to entire page backgrounds; the effect belongs to a card, metric, chip, or bounded chart region.
- **Priority rule**: financial glow overrides decorative gold glow when both compete on the same element.

### Density Modes

| Mode | Usage | Row Height | Cell Padding | Card Padding | Typography |
|------|-------|------------|--------------|--------------|------------|
| `comfortable` | Analysis pages, settings, forms, narrative dashboards | 40-44px | 8px 12px | 16-20px | `text-sm` to `text-base` |
| `compact` | Watchlists, rankings, monitor boards, order panels | 32-36px | 4px 8px or 4px 12px | 8-12px | `text-compact-sm` to `text-compact-base` |
| `micro-density` | Order book ladders, tick tape, heat tables | 24-28px | 4px 6px | 8px | `text-compact-xs` to `text-compact-sm` |

- **Default**: use `comfortable` outside trading and monitoring surfaces.
- **Trading rule**: any panel showing more than 12 concurrent numeric rows should default to `compact`.
- **Micro-density rule**: only for expert data widgets with proven scan value; never for forms or modal workflows.
- **Separation rule**: compact layouts rely on contrast, divider rhythm, and alignment rather than extra whitespace.

### Trading Panel Action Hierarchy

- **One primary action only** per trading panel, order ticket, or execution card.
- **Primary action candidates**: `买入`, `卖出`, `确认下单`, `应用风控`, `启动策略`.
- **All other actions** must be secondary, ghost, icon-only, or overflow actions.
- **Destructive actions** such as `清仓`, `删除规则`, `停止策略` cannot visually compete with the primary action; they require separation or confirmation.
- **Placement**: primary action anchors bottom-right of the panel on desktop unless the panel is a vertical command strip.
- **Size**: primary button should be the only filled CTA in its panel and must maintain 44px minimum height.
- **Disabled clarity**: when the primary action is disabled, show the blocking reason inline, not only in tooltip.

### Charts and Data Visualization

- **Line charts** are the default for trend-over-time price, NAV, and latency views.
- **Bars** are preferred for ranking,资金流对比, category comparison, and contribution breakdown.
- **Radar charts** are allowed only for 5-8 axes strategic comparison and must include a supporting data table.
- **Chart interaction**: hover + crosshair + zoom are allowed on analysis views; live trading views should avoid heavy hover choreography.
- **Color semantics**: chart rise/fall colors must remain aligned with A-share convention even if external libraries default to Western colors.
- **Pattern backup**: when multiple series use similar hues, add dash/pattern variation so charts remain readable under color vision deficiency.
- **Glow rule**: use restrained outer glow on active series only; do not blur every line.

### Loading, Empty, and Alert States

- **Loading**: use skeletons for panels larger than 300ms load time; spinner-only is reserved for tiny inline refreshes.
- **Streaming updates**: show last update timestamp and connection health near the widget title, not buried in footer.
- **Empty states**: keep them operational and concise; include a next action, filter hint, or onboarding hint instead of decorative illustration.
- **Alert banners**: risk and execution alerts must enter fast (`200ms`) and persist until acknowledged or resolved.
- **Toast rule**: success toasts auto-dismiss; loss/risk toasts require longer dwell or explicit dismissal based on severity.

---

## Layout

### Sidebar
- Width: 260px expanded, 68px collapsed
- Background: #111118
- Border: right 1px rgba(212,175,55,20%)

### Content Area
- Max width: 1400px
- Padding: 32px (standard), 16px (compact mode)
- Background: #0A0A0A with diagonal gold crosshatch at 6% opacity

### Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `z-auto` | auto | Normal flow |
| `z-0` | 0 | Base layer |
| `z-10` | 10 | Dropdowns |
| `z-20` | 20 | Sticky headers |
| `z-30` | 30 | Tooltips |
| `z-40` | 40 | Modals |
| `z-50` | 50 | Toasts, notifications |
| `z-fixed` | 100 | Fixed overlays |

---

## Accessibility

- **Focus**: 2px solid #D4AF37 outline, 2px offset (non-blurred, ArtDeco geometric)
- **Screen reader**: `.sr-only` utility class provided
- **Skip navigation**: Gold skip-to-content link at top
- **Reduced motion**: All animations disabled when `prefers-reduced-motion: reduce`
- **Contrast**: Muted text (#A0A0A0) on dark background meets WCAG AA (7.3:1 ratio)
- **Print**: Stripped to white background, black text, no decorative elements
- **Data flash accessibility**: price flash must never be the sole carrier of meaning; numeric delta, icon, or label must remain visible.
- **Dense table accessibility**: sticky headers and zebra/divider rhythm are required once row count exceeds one viewport.
- **Keyboard safety**: the primary action in a trading panel must have a visible focus ring and must not share ambiguous hotkeys with destructive actions.

---

## Do's and Don'ts

### Typography & Data

1. **Do** use `font-variant-numeric: tabular-nums` for ALL financial figures — columns must align.
2. **Do** use JetBrains Mono for prices, volumes, percentages, and codes — never Barlow or Cinzel for data.
3. **Don't** truncate or round stock prices without user consent — precision matters.
4. **Do** show timestamps with timezone-aware formatting and relative time labels.

### Color & Brand

5. **Do** maintain red=up/profit and green=down/loss consistency across EVERY screen and chart.
6. **Don't** mix market color conventions — always use A-Share (red=up, green=down), never Western.
7. **Don't** use light mode — the entire system is designed for dark backgrounds only.
8. **Do** use gold glow shadows on interactive elements to reinforce the ArtDeco aesthetic.

### Animation & Feedback

9. **Do** animate price changes with brief color flashes (red pulse for up, green pulse for down).
10. **Do** provide real-time visual feedback (spinners, skeleton loaders) for every data fetch.
11. **Don't** use decorative animations that compete with live market data for user attention.

### Interaction Safety (from CoinPulse)

12. **Don't** place more than one primary action per trading panel to avoid costly misclicks.
13. **Do** use secondary actions as text buttons, icon buttons, or overflow menus — never competing primary buttons.
14. **Do** disable (0.4 opacity, no glow) rather than hide unavailable actions.

### Layout & Responsiveness

15. **Do** default to sharp corners (0px radius) for data components; use rounded corners only for interactive controls.
16. **Don't** add responsive/mobile styles — this system is desktop-only (min 1280x720).
17. **Do** use the compact spacing scale for data-dense views (dashboards, watchlists, order books).
18. **Don't** let decorative patterns (crosshatch, sunburst) obscure or distract from core data.
19. **Don't** re-enable global decorative corner markers unless overlap and collision issues are explicitly solved in runtime.

### Component States

20. **Do** use the `--ad-{component}-{property}-{state}` token system for all component state transitions.
21. **Don't** create ad-hoc hover/focus styles outside the state machine — bind to `--ad-*` tokens.
22. **Do** use semantic glow variants (`glow-profit`, `glow-loss`) for financial status feedback.
23. **Do** downgrade decorative gold effects when profit/loss semantics need to be read first.
24. **Don't** let multiple flashing cells compete in the same panel; aggregate the signal when data bursts happen.
25. **Do** expose connection freshness, last-update time, and stale-data state in every real-time widget.
26. **Don't** use filled secondary CTAs inside a trading panel; preserve the single-primary-action rule.

---

## Implementation Files

| File | Purpose |
|------|---------|
| `web/frontend/src/styles/artdeco-tokens.scss` | Core design tokens (colors, typography, spacing, animation) |
| `web/frontend/src/styles/artdeco-global.scss` | Global resets, fonts, scrollbar, focus, animations |
| `web/frontend/src/styles/artdeco-colors.css` | Legacy CSS color variables |
| `web/frontend/src/styles/artdeco-typography.css` | Typography utility classes |
| `web/frontend/src/styles/design-tokens.scss` | Chart colors, component mixins |
| `web/frontend/src/styles/fintech-design-system.scss` | Bloomberg-style data terminal tokens |
| `web/frontend/src/styles/artdeco-quant-extended.scss` | Quantitative trading extensions |
| `web/frontend/src/styles/artdeco-patterns.scss` | ArtDeco decorative patterns |
| `web/frontend/src/styles/artdeco-financial.scss` | Financial-specific styles |
| `web/frontend/src/styles/chart-theme.ts` | ECharts theme configuration |
| `web/frontend/src/styles/echarts-theme.ts` | ECharts alternative theme |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | 2026-04-10 | Expert evaluation: bold gold usage, full typography system, compact spacing |
| 3.1 | 2026-04-18 | CoinPulse comparison: hybrid transitions, financial glow effects, data-first animation rules |
| 3.2 | 2026-04-18 | Added motion governance, density modes, trading panel action hierarchy, chart/alert state rules |
| 3.3 | 2026-04-19 | CoinPulse absorption: component state machine (`--ad-{component}-{property}-{state}`), filter/status chip specs including Holding/Pending tokens, tooltip/overlay tokens, financial semantic glow, single-action rule, consolidated Do's & Don'ts |
| 3.4 | 2026-04-19 | Added ArtDeco brand DNA and visual signatures from the mother-style guide; documented current runtime exception that decorative corner markers remain globally disabled due to overlap/collision issues |

---

*This design system is for MyStocks, a personal quantitative trading platform. Desktop-only, dark-mode, A-share convention.*
