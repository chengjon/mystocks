# Dashboard Critique & Audit Report

> Date: 2026-05-10
> Target: `/dashboard` route (`ArtDecoDashboard.vue` + `ArtDecoDashboard.scss`)
> Method: LLM Design Review (in-head) + manual anti-pattern scan
> Register: product
> Context: PRODUCT.md + DESIGN.md (ArtDeco v3.0)

---

## Anti-Patterns Verdict

### LLM Assessment: MIXED

The dashboard avoids the worst AI-generated tells but falls into several category-reflex traps:

**First-order check:** "Finance dashboard" immediately suggests dark background + gold accents. The actual implementation matches exactly that expectation. The ArtDeco motif is intentional and documented in DESIGN.md, so this is a deliberate brand choice, not an AI reflex. Verdict: **pass with caveat** (brand-consistent, but externally indistinguishable from "fintech that uses gold").

**Second-order check:** "Fintech dashboard that's not generic SaaS" suggests hero-metric template with big numbers and card grids. The dashboard has both. Verdict: **partial fail**.

**Specific AI slop tells detected:**

| Pattern | Found | Location |
|---------|-------|----------|
| Identical card grids | YES | `.content-grid { grid-template-columns: repeat(3, 1fr) }` with 9 uniform cards |
| Hero-metric template | YES | Large stat cards (上证指数/深证成指/创业板指) with big number + label + change% + glow |
| Emoji in professional UI | YES | Fast nav uses 📈📋🔍💼🎯⚠️ as nav icons |
| Display font in buttons | YES | `.stress-test-btn` uses `artdeco-font-display` (Cinzel) for button text |
| Display font in indicator names | YES | `.indicator-name` uses `artdeco-font-display` for technical labels |
| Display font in nav labels | YES | `.nav-label` uses `artdeco-font-display` (Cinzel) for navigation text |
| Gradient background on interactive elements | YES | `.stress-test-btn` has `linear-gradient(135deg, ...)` background |
| Decorative gradient overlay | YES | `.artdeco-dashboard::before` radial gradient background |
| Side-stripe borders | NO | Not detected |
| Glassmorphism | NO | Not detected |
| Gradient text (`background-clip: text`) | NO | Not in dashboard (exists in `artdeco-tokens.scss` mixin but unused here) |

**Deterministic scan:** CLI unavailable in the current sandbox. `npx impeccable` could not be used as stable evidence because npm cache/install access failed or stalled; manual source scan performed instead.

---

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 4 | Meta bar shows DATA/REQ/TIME/SYNC. Market status badge. Loading skeletons. Error states. Strong. |
| 2 | Match System / Real World | 3 | A-share red/green convention correct. Chinese labels appropriate. Sentiment indicator as percentage bar is abstract. |
| 3 | User Control and Freedom | 3 | Collapsible sections for indicators and monitoring. Tab switching for fund flow and stock pool. No undo for stress test but non-destructive. |
| 4 | Consistency and Standards | 2 | Mixed font usage: display font in buttons and labels where body font should be. Emoji vs icon inconsistency. Gradient used on some cards but not others. |
| 5 | Error Prevention | 3 | Stress test button disabled when data not ready. Skeleton states for loading. Error sections per card. |
| 6 | Recognition Rather Than Recall | 2 | 9 cards in content grid. No visual hierarchy differentiating them. Fast nav at bottom requires scrolling past all data. |
| 7 | Flexibility and Efficiency | 2 | No keyboard shortcuts visible. No way to customize panel layout. No quick-filter on fund flow. All panels always visible. |
| 8 | Aesthetic and Minimalist Design | 2 | Information overload: ~15 distinct data panels on one scrollable page. Decorative gradient overlay and gold line compete with data. |
| 9 | Error Recovery | 3 | Error messages inline per card. Retry not explicit but data refreshes. Global meta bar shows TIME/SYNC, but individual data cards lack per-source freshness timestamps. |
| 10 | Help and Documentation | 1 | No help text, tooltips, or onboarding. "Quick nav" is the only guidance but it's navigation, not help. |
| **Total** | | **26/40** | **Needs Improvement** |

---

## Cognitive Load Assessment

**Checklist (8 items):**

1. **>7 visible choices at first glance?** YES - meta bar (5 items) + 4 stat cards + 3 index cards = 12+ visible elements. FAIL
2. **No clear visual entry point?** PARTIAL - "QUANTIX" header is dominant but below it everything has equal weight. FAIL
3. **Information not progressively disclosed?** PARTIAL - collapsibles for indicators/monitoring help, but market panorama is fully expanded. FAIL
4. **Similar items not grouped visually?** YES - fund flow overview and fund flow ranking are separate cards with no visual link. FAIL
5. **User must scroll to find key info?** YES - stress test, stock pool, and quick nav are below the fold on 1920px. FAIL
6. **Labels use jargon without explanation?** NO - Chinese labels are standard market terms for the audience. PASS
7. **State changes lack feedback?** NO - loading skeletons, error messages, market status badge all present. PASS
8. **Dense numeric data without alignment?** NO - JetBrains Mono + tabular-nums used correctly. PASS

**Failure count: 5 (Critical).** Target: 0-1 for good UX.

**Visible options at main decision point:** ~12 interactive/scanable elements on initial viewport. Flagged (>4).

---

## What's Working

1. **System status transparency.** The meta bar (DATA/REQ/TIME/SYNC) is excellent for a quant terminal. Users can see data freshness, request health, and sync status at a glance. This directly serves the "split-second reads on price action" requirement from PRODUCT.md.

2. **Loading and error state coverage.** Every card has skeleton loading (`ArtDecoSkeleton`) and error states. No blank panels or mystery meat loading indicators. This respects the "expert confidence" design principle.

3. **A-share color convention correctness.** Red for rise/up/inflow, green for down/fall/outflow consistently applied across stat cards, flow items, and stock items. CSS class names (`.rise`, `.fall`, `.inflow`, `.outflow`) correctly map to `--artdeco-up` and `--artdeco-down`.

---

## Priority Issues

### [P1] Display font (Cinzel) used in UI labels and buttons

**What:** `.stress-test-btn`, `.indicator-name`, and `.nav-label` use `artdeco-font-display` (Cinzel serif).

**Why it matters:** PRODUCT.md says "Expert confidence: speak the language of the domain, not the language of generic software." The product register reference says: "Display fonts in UI labels, buttons, data" is a **ban**. Cinzel is a decorative serif designed for hero headlines, not for button labels or tab text. It reduces readability at small sizes and breaks the "tool disappears into the task" product ideal.

**Fix:** Switch buttons (`stress-test-btn`), indicator names, and nav labels to `artdeco-font-body` (Barlow). Reserve `artdeco-font-display` (Cinzel) exclusively for the page title "QUANTIX" and section-level headings (h3/h4 in card headers). Note: `.flow-tab` and `.pool-tab` already correctly use `artdeco-font-body`.

**Suggested command:** `/impeccable typeset dashboard`

### [P2] Identical card grid in content-grid (anti-pattern)

**What:** `.content-grid` uses `repeat(3, 1fr)` with 9 cards of similar visual weight. Each card has: title + content area. The market heatmap, capital flow heatmap, sector radar, stress test, longhu bang, block trading, capital ranking, stock pool, and quick nav all look structurally identical at the grid level.

**Why it matters:** The shared design laws explicitly ban "identical card grids: same-sized cards with icon + heading + text, repeated endlessly." This is the exact pattern. No visual hierarchy differentiates "market heatmap" (high value) from "quick nav" (low value, could be sidebar).

**Fix:** Introduce visual hierarchy: make chart cards (heatmap, radar) span 2 columns. Move "quick nav" to sidebar or header. Use size variation, not uniformity.

**Suggested command:** `/impeccable layout dashboard`

### [P3] Emoji as navigation icons

**What:** The fast nav section uses emoji (📈📋🔍💼🎯⚠️) as icons for navigation items.

**Why it matters:** Emoji rendering varies across platforms. They lack the precision and visual consistency expected in a professional quant terminal. PRODUCT.md's anti-references include "consumer finance apps" with "emoji-driven feedback." The ArtDeco system has `ArtDecoIcon` component used elsewhere on this page.

**Fix:** Replace all emoji with `ArtDecoIcon` using appropriate icon names (e.g., `trending-up`, `list`, `search`, `briefcase`, `target`, `alert-triangle`).

**Suggested command:** `/impeccable polish dashboard`

### [P3] Information density without hierarchy

**What:** The page presents ~15 data panels in a single scrollable view with no clear priority ordering. Fund flow overview, market indicators, fund flow ranking, and stock pool all compete for attention at equal visual weight.

**Why it matters:** PRODUCT.md says "Data speaks first" and "every pixel must justify itself." When everything is equally prominent, nothing is prominent. The user has to scan all panels to find what matters now.

**Fix:** Establish a clear information hierarchy:
- Tier 1 (always visible, top): Market indices + fund flow overview
- Tier 2 (visible, secondary): Charts (heatmap, trend)
- Tier 3 (on demand): Indicators, monitoring, stress test, rankings
- Tier 4 (navigation): Quick nav, stock pool

Collapse tiers 3-4 by default or move to tabs.

**Suggested command:** `/impeccable distill dashboard`

### [P2] Gradient overlay and decorative elements competing with data

**What:** `::before` applies a radial gradient overlay (gold + bronze). `::after` adds a gold decorative line at top. Cards use `gradient` variant. Chart sections have gradient backgrounds. Stress test button has gradient fill.

**Why it matters:** PRODUCT.md principle: "A gold glow that obscures a price tick is a bug, not a feature." The design principle "Theatrical restraint" says ArtDeco drama should be at "brand-forward moments" only. The dashboard is a data-critical surface. Multiple gradient layers on the primary data surface violates this principle.

**Fix:** Remove `::before` gradient overlay from the dashboard (save it for overview/landing pages). Remove `gradient` variant from fund-flow and market-indicator cards. Keep the decorative `::after` gold line as it's subtle and brand-consistent.

**Suggested command:** `/impeccable quieter dashboard`

---

## Technical Audit (a11y, Anti-patterns, Performance)

### Accessibility

| Check | Status | Detail |
|-------|--------|--------|
| `aria-live` on dynamic regions | PASS | `request-meta-bar` and `dashboard-alerts` both have `aria-live="polite"` |
| `focus-visible` on interactive elements | PASS | `.flow-tab`, `.pool-tab`, `.stress-test-btn`, `.nav-item` all have gold focus-visible styles |
| `font-variant-numeric: tabular-nums` | PASS | All monetary/numeric data uses `artdeco-font-mono` which enforces tabular-nums |
| Semantic HTML | PARTIAL | Uses `<section>`, `<nav>`, `<h3>`, `<h4>` but card content lacks `<article>` or `<dl>` for data pairs |
| Color-only meaning | PASS | Rise/fall uses both color classes AND text (+/-) |
| Keyboard navigation | PARTIAL | Tab navigation works for buttons and links, but no `tabindex` management for collapsible sections |
| `prefers-reduced-motion` | NOT DETECTED | No `@media (prefers-reduced-motion)` in dashboard SCSS. Hover transforms (`translateY`) persist |
| ARIA roles for tabs | FAIL | `.flow-tab` and `.pool-tab` use button elements without `role="tablist"/"tab"/"tabpanel"` |

### Anti-patterns (Code Level)

| Pattern | Found | Severity |
|---------|-------|----------|
| `style="..."` inline styles | YES (6+ instances) | Medium - `style="height: 300px;"` on heatmap sections, `style="margin-top: 10px;"` on skeleton, and others in template |
| `_idx` unused index in v-for | YES (3 instances) | Low - `v-for="(tab, _idx) in flowTabs"` |
| Hardcoded Chinese strings | YES (many) | Info - no i18n, but project scope is Chinese market only |
| `v-if` + `v-else` chain complexity | Moderate | Long conditional chains in template |
| No `key` duplication risk | PASS | All v-for keys are unique |

### Performance Indicators

| Check | Status |
|-------|--------|
| Scoped styles | PASS (`<style scoped>`) |
| Lazy component loading | PASS (via composable pattern) |
| Chart lazy loading | PASS (conditional render with v-if) |
| Skeleton loading | PASS (prevents layout shift) |
| CSS calc() complexity | FLAG - extensive `calc()` with var() arithmetic in media queries |

---

## Persona Red Flags

**Li Wei (Quant Trader, 10yr experience):**
- Scans dashboard at market open looking for sector rotation signals
- Has to scroll past fund flow overview + market indicators + flow section + collapsibles to reach the heatmap
- The 3-column grid at desktop resolution means heatmaps are squeezed to ~33% width
- Red flag: no way to expand a chart to full-width for detailed analysis
- Red flag: no keyboard shortcut to jump between sections

**Zhang Min (Systematic Strategy Developer):**
- Wants to see technical indicators alongside market data for correlation analysis
- Indicators section is collapsible (good) but detached from the charts it should contextualize
- Red flag: indicator items show only name/value/signal, no sparkline or mini-chart
- Red flag: stress test results are static numbers with no comparison to historical scenarios

---

## Questions to Consider

1. What if the 3-column grid were replaced with a 2-column layout where charts span full width? Would that improve scanability?

2. Does the dashboard need to show everything at once? What if "monitoring" and "indicators" were a separate tab or panel?

3. The "QUANTIX" brand name appears in both the header and the meta bar. Is the repetition intentional, or should one be removed?

4. Should the fast nav section exist at all? The sidebar already provides navigation. Is this redundancy helping or cluttering?

---

*Report generated 2026-05-10 | MyStocks Dashboard Critique & Audit | Total score: 26/40 (Needs Improvement)*
