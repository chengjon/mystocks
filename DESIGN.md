---
name: MyStocks ArtDeco Design System
description: Dark-mode, gold-accented quantitative trading terminal - ArtDeco luxury meets fintech precision
colors:
  classical-gold: "#D4AF37"
  champagne: "#F0E68C"
  dim-gold: "#8B7355"
  bronze: "#CD7F32"
  obsidian-black: "#0A0A0A"
  rich-charcoal: "#141414"
  warm-charcoal: "#1A1A1A"
  deep-navy-black: "#111118"
  champagne-cream: "#F2F0E4"
  anchor-gray: "#A0A0A0"
  ghost-white: "rgba(255,255,255,0.6)"
  a-share-red: "#FF5252"
  a-share-green: "#00E676"
  neutral-gray: "#B0B3B8"
  sky-blue: "#4FC3F7"
  deep-red: "#D50000"
  deep-green: "#00C853"
  signal-gray: "#888888"
typography:
  display:
    fontFamily: "Cinzel, Playfair Display, serif"
    fontWeight: 600
    letterSpacing: "0.05em"
  headline:
    fontFamily: "Cinzel, Playfair Display, serif"
    fontWeight: 600
    fontSize: "2.25rem"
    lineHeight: 1.25
    letterSpacing: "0.05em"
  body:
    fontFamily: "Barlow, Inter, sans-serif"
    fontWeight: 400
    fontSize: "1rem"
    lineHeight: 1.5
  label:
    fontFamily: "Barlow, Inter, sans-serif"
    fontWeight: 500
    fontSize: "0.75rem"
    letterSpacing: "0.025em"
  data:
    fontFamily: "JetBrains Mono, Consolas, monospace"
    fontWeight: 500
    letterSpacing: "0.02em"
  technical:
    fontFamily: "IBM Plex Sans, Helvetica Neue, sans-serif"
    fontWeight: 500
rounded:
  none: "0px"
  sm: "2px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  "1": "0.25rem"
  "2": "0.5rem"
  "3": "0.75rem"
  "4": "1rem"
  "5": "1.25rem"
  "6": "1.5rem"
  "8": "2rem"
  "10": "2.5rem"
  "12": "3rem"
  "16": "4rem"
  "20": "5rem"
  "24": "6rem"
  "32": "8rem"
  compact-xs: "0.25rem"
  compact-sm: "0.5rem"
  compact-md: "0.75rem"
  compact-lg: "1rem"
components:
  button-primary:
    backgroundColor: "{colors.classical-gold}"
    textColor: "{colors.obsidian-black}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.champagne}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.classical-gold}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.anchor-gray}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
  input-default:
    backgroundColor: "{colors.rich-charcoal}"
    textColor: "{colors.champagne-cream}"
    rounded: "{rounded.sm}"
    padding: "8px 12px"
  input-focus:
    backgroundColor: "{colors.rich-charcoal}"
    textColor: "{colors.champagne-cream}"
    rounded: "{rounded.sm}"
  card-default:
    backgroundColor: "{colors.rich-charcoal}"
    rounded: "{rounded.md}"
    padding: "16px"
  card-hover:
    backgroundColor: "{colors.rich-charcoal}"
    rounded: "{rounded.md}"
  chip-default:
    backgroundColor: "rgba(212,175,55,0.08)"
    textColor: "{colors.anchor-gray}"
    rounded: "{rounded.sm}"
    padding: "4px 8px"
  chip-active:
    backgroundColor: "rgba(212,175,55,0.2)"
    textColor: "{colors.classical-gold}"
    rounded: "{rounded.sm}"
---

# Design System: MyStocks ArtDeco

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Overview

MyStocks is a dark-mode design system for personal quantitative trading and stock analysis. It fuses the theatrical elegance of Art Deco (gold accents, geometric patterns, serif headlines) with the data-density demands of a Bloomberg-style terminal. The system is optimized for **A-share markets** (Chinese stock convention: red = profit/up, green = loss/down), single-user desktop deployment, and split-second decision-making in volatile environments.

Geometry as decoration, not ornament. Structured lines, measured frames, repeated motifs, and architectural rhythm replace soft organic decoration. Obsidian-black and metallic-gold contrast preserves a ceremonial, premium hierarchy. Verticality and symmetry dominate compositions: balanced column rhythm, upward emphasis in dashboards, framed analysis panels.

Interactive feedback is deliberate and engineered, never playful or bouncy. Gold luminescence and controlled halo layers provide emphasis instead of generic black shadow stacks. Uppercase display typography in Cinzel serif with wide tracking carries the ArtDeco identity. Framed panels, measured separators, and geometric section dividers group content; soft card-only grouping is avoided.

**ArtDeco Brand DNA:**

- **Diagonal crosshatch**: the primary ambient texture for the active runtime
- **Gold glow over drop shadow**: emphasis via gold luminescence and halo layers
- **Uppercase display typography**: Cinzel, serif, uppercase, widely tracked
- **Double-frame and divider language**: framed panels and geometric dividers over soft cards
- **Roman numeral / rotated diamond motifs**: secondary brand accents for overview, onboarding, attribution surfaces

**Usage Boundaries:**

- Data-dense and execution-critical surfaces (trading, risk, monitoring, order, watch panels) default to restrained decoration and prioritize scanability
- Brand-forward surfaces (overview dashboards, empty states, feature intros, strategy summaries) may use stronger ArtDeco motifs when they do not compete with core data
- Financial semantics override ornament: profit/loss state, risk state, execution status, and stale-data feedback always take priority over decorative gold treatment

**Runtime Exception:** Decorative corner markers remain globally disabled. Historical stepped-corner treatments caused overlap with existing UI elements and degraded visual clarity.

**Key Characteristics:**
- Permanent dark mode, no light mode, forced `color-scheme: dark`
- A-share convention: red = up/profit, green = down/loss
- ArtDeco sharp geometry: default to 0px radius for data, 8px for interactive elements
- Gold luminescence elevation system, not traditional drop shadows
- Hybrid transition timing: 200ms for data, 400ms for decorative
- Three density modes: comfortable, compact, micro-density
- Desktop-only, minimum 1280x720

## Colors

The palette is built around obsidian blacks and classical gold, with A-share financial semantics as the only saturated deviation. Gold is the brand identity, used structurally on borders, glows, and active states, not decoratively on every surface.

### Primary

- **Classical Gold** (#D4AF37): Brand identity. CTAs, active states, borders, headlines, section titles. The single voice of the system.
- **Champagne** (#F0E68C): Hover states, highlights, gradient endpoints. A lighter register of the same gold.
- **Dim Gold** (#8B7355): Shadows, subtle borders, inactive accents. Gold at rest.
- **Bronze** (#CD7F32): Secondary accent for badges, tertiary actions.

### Neutral

- **Obsidian Black** (#0A0A0A): Root canvas, app background. Nearly pure black with a warm cast.
- **Rich Charcoal** (#141414): Cards, panels, modals. The primary surface color.
- **Warm Charcoal** (#1A1A1A): Dropdowns, tooltips, overlays. Elevated surface.
- **Deep Navy-Black** (#111118): Sidebar, top bar, navigation. A cooler dark for structural chrome.
- **Champagne Cream** (#F2F0E4): Main body text, headings. Warm off-white, never pure white.
- **Anchor Gray** (#A0A0A0): Secondary text, timestamps. WCAG AA compliant (7.3:1 ratio on dark).
- **Ghost White** (rgba(255,255,255,60%)): Placeholders, hints, disabled text.

### Financial (A-Share Convention)

- **A-Share Red** (#FF5252): Rising prices, gains, positive deltas. Maps to success.
- **A-Share Green** (#00E676): Falling prices, losses, negative deltas. Maps to error.
- **Neutral Gray** (#B0B3B8): Unchanged, flat, baseline.
- **Sky Blue** (#4FC3F7): Informational banners, links, tooltips.

### Quantitative Trading Indicators

- **Deep Red** (#D50000): Strong buy signal. Deeper register of A-Share Red.
- **Deep Green** (#00C853): Strong sell signal. Deeper register of A-Share Green.
- **Signal Gray** (#888888): Neutral trading signal.
- **MACD Fast** (#2962FF): MACD fast line indicator.
- **MACD Slow** (#FF6D00): MACD slow line indicator.
- **KDJ-K** (#00BCD4): KDJ K-line indicator.
- **KDJ-D** (#7C4DFF): KDJ D-line indicator.
- **KDJ-J** (#FF4081): KDJ J-line indicator.
- **RSI** (#AA00FF): RSI indicator line.
- **BOLL Upper** (#FF5252): Bollinger Band upper rail.
- **BOLL Middle** (#D4AF37): Bollinger Band middle rail (gold).
- **BOLL Lower** (#00E676): Bollinger Band lower rail.
- **DOM Bid** (#00E676): Depth of market bid side.
- **DOM Ask** (#FF5252): Depth of market ask side.
- **DOM Spread** (#FFD700): Bid-ask spread indicator.
- **Risk Low** (#00E676): Low risk level.
- **Risk Medium** (#FFD700): Medium risk level.
- **Risk High** (#FF5252): High risk level.
- **Risk Extreme** (#D50000): Extreme risk level.

### Named Rules

**The One Voice Rule.** Classical Gold is the single accent. It carries borders, CTAs, active states, and section titles. Bronze is the only permitted secondary, and only for badges and tertiary actions. No other saturated colors appear outside financial data.

**The Financial Override Rule.** A-Share Red and Green override gold semantics wherever financial state (profit/loss, up/down) competes with decorative treatment. Financial glow always beats decorative gold glow on the same element.

## Typography

**Display Font:** Cinzel (ArtDeco geometric serif), with Playfair Display fallback.
**Body Font:** Barlow (modern sans-serif), with Inter fallback.
**Data Font:** JetBrains Mono (monospace), with Consolas fallback.
**Technical Font:** IBM Plex Sans (technical data), with Helvetica Neue fallback.

The pairing is authoritative and deliberate. Cinzel provides the ArtDeco identity through uppercase, widely tracked display type. Barlow handles body text with clean legibility at data-dense sizes. JetBrains Mono ensures tabular numeric alignment across all financial figures. IBM Plex Sans extends the system for technical indicator labels and strategy panels.

### Hierarchy

- **Display** (600 weight, clamp 2.5rem-4rem, line-height 1): Hero titles, dramatic page headers. Cinzel uppercase, letter-spacing 0.05-0.1em, gold color.
- **Headline** (600, 2.25rem, 1.25): Section titles. Cinzel uppercase, widely tracked.
- **Title** (600, 1.5rem, 1.25): Card headings, panel titles. Cinzel or Barlow.
- **Body** (400, 1rem, 1.5): Main text. Barlow normal case. Max line length 65-75ch.
- **Label** (500, 0.75rem, letter-spacing 0.025em): Tags, captions, small labels. Barlow.
- **Data** (500, 0.875rem base, letter-spacing 0.02em): Prices, volumes, percentages, codes. JetBrains Mono. `font-variant-numeric: tabular-nums` mandatory.

### Compact Type Scale (Data-Dense Views)

- **Compact XS** (0.6875rem / 11px): Micro labels, tick tape
- **Compact SM** (0.75rem / 12px): Table cells, compact data
- **Compact Base** (0.875rem / 14px): Compact body text
- **Compact MD** (1rem / 16px): Compact headings
- **Compact LG** (1.125rem / 18px): Compact titles

### Data Sizes (Quantitative Trading)

- **Data XS** (0.625rem / 10px): Extreme micro data
- **Data SM** (0.75rem / 12px): Standard data cells
- **Data Base** (0.875rem / 14px): Default data display
- **Data LG** (1rem / 16px): Emphasized data values

### Named Rules

**The Tabular Alignment Rule.** All financial figures use JetBrains Mono with `font-variant-numeric: tabular-nums`. Barlow and Cinzel are forbidden for numeric data. Column alignment is non-negotiable.

**The Data Font Override Rule.** In data-dense panels showing more than 12 concurrent numeric rows, compact type scale must be used. Standard scale is reserved for comfortable/analysis views.

## Elevation

MyStocks uses gold luminescence, not black drop shadows. Elevation comes from controlled gold halo layers at increasing intensity, not from traditional shadow stacking. For financial state feedback, colored glows (red for profit, green for loss) override gold when both compete.

### Shadow Vocabulary

- **None** (`0 0 #0000`): Flat elements at rest.
- **SM** (`0 1px 2px rgba(0,0,0,5%)`): Subtle lift.
- **MD** (`0 4px 6px -1px rgba(0,0,0,10%)`): Cards at rest.
- **LG** (`0 10px 15px -3px rgba(0,0,0,10%)`): Elevated panels.
- **XL** (`0 20px 25px -5px rgba(0,0,0,10%)`): Modals, drawers.

### Gold Glow Effects (ArtDeco Signature)

- **Subtle** (`0 0 15px rgba(212,175,55,20%)`): Default hover.
- **Medium** (`0 0 18px rgba(212,175,55,30%)`): Active focus.
- **Intense** (`0 0 20px rgba(212,175,55,40%)`): Card hover emphasis.
- **Maximum** (`0 0 30px rgba(212,175,55,60%)`): Hero elements.

### Financial Glow Effects

- **Profit** (`0 0 12px rgba(255,82,82,30%)`): Profit/up indicators.
- **Loss** (`0 0 12px rgba(0,230,118,30%)`): Loss/down indicators.

### Named Rules

**The Gold-Over-Black Rule.** Emphasis comes from gold luminescence and controlled halo layers, not generic black shadow stacks. When financial glow and decorative gold glow compete on the same element, financial glow wins.

**The Flat-By-Default Rule.** Surfaces are flat at rest. Shadows and glows appear only as a response to state (hover, elevation, focus).

## Components

### Buttons

- **Shape:** Sharp minimal (2px radius)
- **Primary:** Classical Gold fill (#D4AF37), obsidian-black text, no border. Hover: Champagne (#F0E68C) + gold glow subtle. Focus: gold glow medium.
- **Secondary:** Transparent fill, gold text, 1px gold border at 30%. Hover: gold bg at 10%.
- **Ghost:** Transparent fill, anchor-gray text, no border. Hover: warm-charcoal bg, champagne-cream text.
- **Danger:** A-Share Green fill (#00E676, A-Share down=green convention), obsidian-black text.
- **Sizes:** Small (28px height, 8px 12px padding, 12px font), Medium (36px, 8px 16px, 14px), Large (44px, 12px 24px, 16px).
- **Disabled:** 0.4 opacity, disabled cursor, no glow effects.
- **Loading:** Gold spinner replaces text content.
- **Trading Rule:** One primary action per trading panel. All other actions are secondary, ghost, or overflow.

### Cards

- **Shape:** Sharp-to-medium corners (0px for data, 8px for general)
- **Default:** Rich Charcoal bg, 1px gold border at 30%, no shadow, 16px padding.
- **Elevated:** Warm Charcoal bg, 1px gold border at 80%, gold glow subtle, 20px padding.
- **Hover:** Rich Charcoal bg, full gold border, gold glow intense.
- **Compact (data):** Rich Charcoal bg, 1px gold border at 20%, 0px radius, 12px padding.
- Nested cards are always wrong.

### Inputs

- **Shape:** Sharp minimal (2px radius), 36px height.
- **Default:** Rich Charcoal bg, 1px gold border at 30%, champagne-cream text.
- **Focus:** Full gold border, gold glow subtle.
- **Error:** A-Share Green border, loss glow. (Green = down/error in A-Share convention.)
- **Disabled:** Gold border at 10%, obsidian-black bg, dim-gold text.
- **Label:** 12px / 500 weight / anchor-gray, 4px below field.
- **Helper text:** 12px / 400 / dim-gold, 4px above field.

### Chips

- **Filter:** Default: gold bg 8%, anchor-gray text, gold border 20%. Active: gold bg 20%, gold text, solid gold border. 2px radius, 4px 8px padding.
- **Status (Up/Profit):** Red bg 10%, red text, red border 20%.
- **Status (Down/Loss):** Green bg 10%, green text, green border 20%.
- **Status (Warning):** Gold bg 10%, gold text, gold border 20%.
- **Status (Neutral):** White bg 5%, anchor-gray text, white border 10%.
- **Status (Holding):** Sky-blue bg 10%, sky-blue text, sky-blue border 20%.
- **Status (Pending):** Amber bg 10%, amber text (#FFA726), amber border 20%.

### Data Tables

- **Font:** JetBrains Mono, 12-13px.
- **Header:** 8px 12px padding, anchor-gray text, gold border at 30% bottom.
- **Cell:** 4px 12px padding (compact), gold border at 10% row dividers.
- **Hover:** Gold bg at 5%.
- **Selected:** Gold bg at 15%, left 2px solid gold border.

### Quantitative Trading Components

- **Compact Stat Card:** 48px height, 8px padding, data-sm labels in anchor-gray, data-lg values in JetBrains Mono semibold, data-sm changes with tabular-nums.
- **Indicator Panel:** Rich Charcoal bg, gold border at 30%, 0px radius, 12px padding. Header: technical font, semibold, gold, uppercase, wide tracking. Body: data font, tabular-nums, grid layout with label-value rows.
- **DOM Panel:** JetBrains Mono, data-sm, flex rows with 4px gap. Bid in green, ask in red, spread in gold semibold.
- **Signal Labels:** Strong buy (deep red, semibold), buy (A-Share red, medium), neutral (gray, medium), sell (A-Share green, medium), strong sell (deep green, semibold).

### Tooltips

- Warm Charcoal bg, champagne-cream text, 12px/400 weight. 6px 10px padding, 2px radius, 240px max-width. Show delay 300ms, hide 0ms.

### Navigation (Sidebar)

- 260px expanded, 68px collapsed. Deep Navy-Black bg. Right border gold at 20%.

## Do's and Don'ts

### Do:

- **Do** use `font-variant-numeric: tabular-nums` for ALL financial figures. Columns must align.
- **Do** use JetBrains Mono for prices, volumes, percentages, and codes. Never Barlow or Cinzel for data.
- **Do** maintain red=up/profit and green=down/loss consistency across every screen and chart.
- **Do** use gold glow shadows on interactive elements to reinforce the ArtDeco aesthetic.
- **Do** animate price changes with brief color flashes (red pulse for up, green pulse for down), 120-160ms duration.
- **Do** provide real-time visual feedback (spinners, skeleton loaders) for every data fetch.
- **Do** default to sharp corners (0px radius) for data components; use rounded corners only for interactive controls.
- **Do** use the compact spacing scale for data-dense views (dashboards, watchlists, order books).
- **Do** use semantic glow variants (glow-profit, glow-loss) for financial status feedback.
- **Do** expose connection freshness, last-update time, and stale-data state in every real-time widget.
- **Do** place only one primary action per trading panel. All other actions are secondary, ghost, or overflow.
- **Do** use IBM Plex Sans for technical indicator labels and strategy panel titles.

### Don't:

- **Don't** mix market color conventions. Always use A-Share (red=up, green=down), never Western.
- **Don't** use light mode. The entire system is designed for dark backgrounds only.
- **Don't** use decorative animations that compete with live market data for user attention.
- **Don't** place more than one primary action per trading panel to avoid costly misclicks.
- **Don't** add responsive/mobile styles. Desktop-only (min 1280x720).
- **Don't** let decorative patterns (crosshatch, sunburst) obscure or distract from core data.
- **Don't** re-enable global decorative corner markers unless overlap and collision issues are explicitly solved.
- **Don't** create ad-hoc hover/focus styles outside the state machine. Bind to `--ad-*` tokens.
- **Don't** use Tailwind-blue hero sections, identical card grids, or cookie-cutter metric layouts (generic SaaS dashboards).
- **Don't** use playful illustrations, rounded pastel UI, gamified onboarding, or emoji-driven feedback (consumer finance apps).
- **Don't** use gold indiscriminately across every surface or gratuitous animation loops (over-decorated fintech).
- **Don't** let multiple flashing cells compete in the same panel. Aggregate the signal when data bursts happen.
- **Don't** use filled secondary CTAs inside a trading panel. Preserve the single-primary-action rule.
- **Don't** truncate or round stock prices without user consent. Precision matters.

---

*Version 4.0 (Stitch format) | MyStocks ArtDeco Design System | Desktop-only, dark-mode, A-share convention*
