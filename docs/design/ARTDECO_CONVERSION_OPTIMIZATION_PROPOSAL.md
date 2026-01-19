# ArtDeco Conversion Optimization Proposal

**Document ID**: DESIGN-2026-001
**Date**: 2026-01-16
**Author**: Business Design Master
**Status**: Proposal for Approval
**Reference**: `docs/guides/MYSTOCKS_HTML_TO_VUE_CONVERSION_STRATEGY.md`

---

## 1. Executive Summary

This proposal optimizes the "HTML to Vue Conversion Strategy" by enforcing strict adherence to the **ArtDeco Design System** and injecting **Quantitative Trading Workflow** enhancements. While the original strategy outlines the *technical* migration path, this document defines the *qualitative* standard to ensure the final product meets the "Business Design Master" criteria: **Luxurious Minimalism**, **High-Density Information Architecture**, and **Professional Financial Utility**.

The core directive is: **"No visual compromise. No functionality loss. Maximum trading efficiency."**

---

## 2. Visual & Stylistic Fidelity

To achieve a seamless integration with the existing ArtDeco ecosystem, the following rules must be strictly enforced during the conversion of all 9 source files.

### 2.1 The "Web3 to ArtDeco" Unification Rule

Four of the source files (`dashboard.html`, `backtest-management.html`, `data-analysis.html`, `stock-management.html`) utilize a "Web3 DeFi" aesthetic (Orange/Dark Grey). These **MUST** be completely re-skinned to match the ArtDeco system.

| Web3 Element (Legacy) | ArtDeco Standard (Target) | Token |
|-----------------------|---------------------------|-------|
| Primary Color `#F7931A` (Bitcoin Orange) | **Metallic Gold `#D4AF37`** | `$artdeco-gold-primary` |
| Font `Space Grotesk` | **`Marcellus`** (Headings) | `$artdeco-font-heading` |
| Font `Inter` | **`Josefin Sans`** (Body) | `$artdeco-font-body` |
| Card Style "Glassmorphism" | **Geometric Borders & L-Corners** | `@include artdeco-card-decorations` |
| Rounded Buttons | **Sharp Rectangular Buttons** | `ArtDecoButton` |

### 2.2 Component Mapping Strategy

We strictly prohibit the creation of custom "one-off" components unless absolutely necessary. All source HTML elements must map to the existing 52-component library.

#### Core Functional Modules Mapping

| Source HTML Structure | Target ArtDeco Component | Design Note |
|-----------------------|--------------------------|-------------|
| **Data Tables** (`<table>`, `.data-grid`) | **`ArtDecoTable`** | Enable `sortable`, `stripe`, and usage of A-share colors (Red/Green) for numeric changes. |
| **KPI/Metric Cards** (`.stat-box`, `.metric`) | **`ArtDecoStatCard`** | Use `trend` prop for up/down arrows. Ensure "Gold Glow" on hover. |
| **Navigation Tabs** (`.nav-tabs`, `.pills`) | **`ArtDecoFilterBar`** | Configure as a segmented control or tab group within the filter bar. |
| **Form Inputs** (`<input>`, `<select>`) | **`ArtDecoInput`, `ArtDecoSelect`** | **Strict Rule**: No default browser inputs. All inputs must have the signature bottom gold border. |
| **Charts** (D3/Canvas containers) | **`ArtDecoKLineChartContainer`** or **`TimeSeriesChart`** | Wrap any custom charts in `ArtDecoCard` to maintain visual consistency. |
| **Modals/Popups** | **`ArtDecoDialog`** | Ensure the "Diamond" header style is used. |
| **Loading States** (`.spinner`) | **`ArtDecoLoader`** | Replace generic spinners with the ArtDeco geometric rotation. |

---

## 3. UX/Workflow Enhancement (Quantitative Trading Focus)

As a "Business Design Master," I have identified three critical areas where the conversion must go beyond simple "porting" to deliver a superior trading experience.

### 3.1 Optimization 1: "Trader Density" over "Marketing Spacing"

**Problem**: The source HTML files (especially the Web3 ones) use generous "Marketing" whitespace (`padding: 32px`, large margins). This is inefficient for professional traders who need to scan market data rapidly.

**Optimization Directive**:
- **Compact Layouts**: Enforce a stricter grid system. Use `ArtDecoCard` with `size="compact"` (if available) or override padding to standard `16px` (`$spacing-md`) instead of `32px`.
- **Information Density**: In `ArtDecoTable`, reduce row height to maximize visible data rows per viewport.
- **Visual Hierarchy**: Use **Font Weight** and **Color** (Gold/White/Grey) rather than **Size** to distinguish hierarchy, allowing more content to fit on a single screen (e.g., 4k multi-monitor setups).

### 3.2 Optimization 2: Action-in-Context (The "One-Click" Rule)

**Problem**: Traditional designs often separate "View" (Market Data) from "Action" (Trading).
**Optimization Directive**:
- Embed **`ArtDecoTradeForm`** (miniature version) or "Quick Trade" buttons directly within **`ArtDecoMarketData.vue`** and **`ArtDecoMarketQuotes.vue`**.
- In **`ArtDecoTable`** rows, include a "Trade" action column that opens a pre-filled `ArtDecoDialog` for immediate order execution.
- **Why**: Quantitative traders spot an opportunity and execute in seconds. Context switching costs money.

### 3.3 Optimization 3: Global Market Awareness

**Problem**: Inner pages (like "Settings" or "Backtest") often lose context of the live market.
**Optimization Directive**:
- **Universal Ticker Tape**: Integrate **`ArtDecoTickerList`** into the top layout of **ALL** converted pages, not just the Dashboard.
- **Status Visibility**: Ensure **`ArtDecoStatus`** (System/Connection Health) is visible on every page.
- **Why**: A backtest might be running, but if a market crash happens, the trader needs to know immediately via the ticker tape, regardless of what page they are on.

---

## 4. Implementation Guidelines for Developers

1.  **Reference the Catalog**: Before writing a single line of CSS, search `ARTDECO_COMPONENTS_CATALOG.md`. If a component exists, **USE IT**.
2.  **Scss Variables Only**: Do not hardcode hex colors (e.g., `#D4AF37`). Always use `$artdeco-gold-primary`.
3.  **Strict Type Safety**: All new Vue pages must use `<script setup lang="ts">` and fully typed props/interfaces.
4.  **Acceptance Check**: A page is not "converted" until it looks like it belongs in the Great Gatsby's private trading terminal.

---

**Approval**: 
_Awaiting Sign-off from Project Lead_
