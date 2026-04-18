# CoinPulse
Electric, dark-mode, real-time energy for the decentralized frontier.

## Overview

CoinPulse is a high-intensity design system built for cryptocurrency trading platforms and DeFi applications. It thrives in permanent dark mode, using electric blues, vivid limes, and warm ambers to convey real-time market energy. Every element is optimized for data density, scanning speed, and split-second decision-making. The system treats precision and legibility as non-negotiable in volatile environments.

## Colors

- **Primary** (#2563EB): Electric Blue -- CTAs, active states, links
- **Secondary** (#84CC16): Lime -- profit indicators, positive deltas
- **Tertiary** (#F59E0B): Amber -- warnings, pending states, alerts
- **Neutral** (#71717A): Zinc -- muted text, inactive elements
- **Background** (#09090B): App background, root canvas
- **Surface** (#18181B): Cards, panels, modals
- **Success** (#22C55E): Profit, gains, confirmations
- **Warning** (#F59E0B): Pending transactions, caution
- **Error** (#EF4444): Loss, failed tx, negative delta
- **Info** (#2563EB): Informational banners, links

## Typography

- **Headline Font**: Space Mono
- **Body Font**: DM Sans
- **Mono Font**: Space Mono

- **Display**: Space Mono 32px bold, 1.1 line height, 0.02em tracking
- **Headline**: Space Mono 24px bold, 1.2 line height, 0.01em tracking
- **Subhead**: DM Sans 18px semibold, 1.3 line height
- **Body Large**: DM Sans 16px regular, 1.5 line height
- **Body**: DM Sans 14px regular, 1.5 line height
- **Body Small**: DM Sans 13px regular, 1.4 line height, 0.01em tracking
- **Caption**: DM Sans 12px medium, 1.3 line height, 0.02em tracking
- **Overline**: Space Mono 11px bold, 1.2 line height, 0.08em tracking
- **Code**: Space Mono 13px regular, 1.5 line height

## Spacing

- **Base unit:** 4px
- **Scale:** 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64
- **Component padding:** 8px horizontal, 4px vertical (compact)
- **Section spacing:** 24px between sections, 12px between related groups

## Border Radius

- **None** (0px): Table cells, data rows
- **Small** (4px): Chips, tags, badges
- **Medium** (8px): Cards, inputs, buttons, modals
- **Large** (12px): Containers, panels
- **XL** (16px): Feature cards, hero sections
- **Full** (9999px): Avatars, status indicators, toggles

## Elevation

**Philosophy:** Dark-mode glow effects using colored shadows. Blue/green glow for positive states, red glow for negative/alert states. No traditional drop shadows.
- **Subtle**: 8px glow #2563EB at 15%
- **Medium**: 16px glow #2563EB at 25%
- **Large**: 24px glow #2563EB at 35%
- **Overlay**: 40px glow #000000 at 60%
- **Profit**: 12px glow #22C55E at 30%
- **Loss**: 12px glow #EF4444 at 30%

## Components

### Buttons
#### Variants
- **Primary**: #2563EB fill, #FAFAFA text, no border. Hover: #3B82F6, blue glow.
- **Secondary**: transparent fill, #2563EB text, 1px #2563EB border. Hover: bg #2563EB1A.
- **Ghost**: transparent fill, #A1A1AA text, no border. Hover: bg #27272A, text #FAFAFA.
- **Destructive**: #EF4444 fill, #FAFAFA text, no border. Hover: #DC2626, red glow.
#### Sizes
Sizes: Small (28px, 8px 12px, 12px, 8px), Medium (36px, 8px 16px, 14px, 8px), Large (44px, 12px 24px, 16px, 8px).
#### Disabled State
0.4 opacity.
- disabled cursor
- No glow effects

### Cards
- **Background**: #18181B default, #27272A elevated.
- **Border**: 1px #27272A default, 1px #3F3F46 elevated.
- **Radius**: 8px default, 8px elevated.
- **Padding**: 16px default, 20px elevated.
- **Shadow**: 16px glow #2563EB at 15% elevated.
- **Hover**: border #3F3F46 default, blue glow intensifies elevated.

### Inputs
#### Text Input
- **Default**: 1px #3F3F46 border, #18181B fill, #FAFAFA text, no shadow.
- **Hover**: 1px #52525B border, #18181B fill, #FAFAFA text, no shadow.
- **Focus**: 1px #2563EB border, #18181B fill, #FAFAFA text, 8px glow #2563EB at 25% shadow.
- **Error**: 1px #EF4444 border, #18181B fill, #FAFAFA text, 8px glow #EF4444 at 20% shadow.
- **Disabled**: 1px #27272A border, #09090B fill, #52525B text, no shadow.
** 36px **height, ** 8px 12px **padding, ** 8px **radius, ** 12px / 500 / #A1A1AA, 4px below **label, ** 12px / 400 / #71717A, 4px above **helper text.

### Chips
#### Filter Chip
** #27272A **background, ** #A1A1AA / 12px / 500 **text, ** 1px #3F3F46 **border, ** 4px **radius, ** 4px 8px **padding, ** bg #2563EB1A, border #2563EB, text #2563EB **active.
#### Status Chip
** bg #22C55E1A, text #22C55E, border #22C55E33 **profit, ** bg #EF44441A, text #EF4444, border #EF444433 **loss, ** bg #F59E0B1A, text #F59E0B, border #F59E0B33 **pending.

### Lists
#### Default Item
** 40px **height, ** 8px 12px **padding, ** 1px #27272A **divider, ** bg #27272A **hover, ** bg #2563EB1A, left 2px #2563EB **selected, ** 14px / 400 / #FAFAFA **font.

### Checkboxes
** 16px **size, ** 1.5px #3F3F46 **border, ** 4px **radius, ** bg #2563EB, border #2563EB, white checkmark **checked, ** bg #2563EB, white dash **indeterminate, ** 40% opacity, disabled cursor **disabled, ** 14px / 400 / #FAFAFA, 8px gap **label.

### Radio Buttons
** 16px **size, ** 1.5px #3F3F46 **border, ** border #2563EB, inner dot #2563EB (8px) **selected, ** 40% opacity, disabled cursor **disabled, ** 14px / 400 / #FAFAFA, 8px gap **label.

### Tooltips
** #27272A **background, ** #FAFAFA / 12px / 400 **text, ** 6px 10px **padding, ** 4px **radius, ** 240px **max width, ** 6px, same background **arrow, ** 300ms show, 0ms hide **delay.

## Do's and Don'ts

1. **Do** use tabular/monospaced numerals for all financial figures so columns align perfectly.
2. **Do** animate price changes with brief color flashes -- green pulse for gains, red pulse for losses.
3. **Do** maintain green-for-profit and red-for-loss consistency across every screen and chart.
4. **Don't** truncate or round prices without user consent; precision matters in crypto.
5. **Do** show timestamps with timezone-aware formatting and relative time labels.
6. **Don't** use light mode; the entire system is designed for dark backgrounds only.
7. **Do** use blue glow shadows on interactive elements to reinforce the electric aesthetic.
8. **Don't** place more than one primary action per trading panel to avoid costly misclicks.
9. **Do** provide real-time visual feedback (spinners, skeleton loaders) for every data fetch.
10. **Don't** use decorative animations that compete with live market data for user attention.