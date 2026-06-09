# MyWeb Audit Report: /dashboard

> Date: 2026-05-10
> Route: `/dashboard`
> Mode: Quick Mode (single page)
> Verification Surface: `code-review-only` (frontend reachable but browser automation not available for this run)
> Files Audited:
>   - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` (542 lines)
>   - `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss` (837 lines)
>   - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts` (828 lines)
>   - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.chart-options.ts` (224 lines)
>   - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.types.ts` (55 lines)

---

## Route Inventory

| Field | Value |
|-------|-------|
| Route | `/dashboard` |
| Router Entry | `web/frontend/src/router/index.ts` |
| Canonical View | `ArtDecoDashboard.vue` |
| Composable | `useArtDecoDashboard.ts` |
| Route Class | `canonical-page` |
| Purpose | Market overview dashboard with fund flow, indices, heatmaps, stress test, and navigation |

---

## Audit Summary

| Role | Findings | Blocking | High | Medium | Low |
|------|----------|----------|------|--------|-----|
| Functional | 7 | 0 | 2 | 4 | 1 |
| Data-State | 9 | 0 | 3 | 5 | 1 |
| Visual-ArtDeco | 7 | 0 | 2 | 4 | 1 |
| Responsive-A11y | 6 | 0 | 1 | 4 | 1 |
| **Total** | **29** | **0** | **8** | **17** | **4** |

After merge and deduplication: **18 unique issues**.

---

## Merged Findings (Sorted by Severity)

### [F-01] High: Tab buttons lack ARIA tab semantics

| Field | Value |
|-------|-------|
| Source Roles | functional-audit, responsive-a11y-audit |
| Dedupe Key | `dashboard-tabs-no-aria-roles` |
| Severity | High |
| Trigger | User interacts with flow-tabs (1日/3日/5日) or pool-tabs (自选/持仓/重点) |
| Expected | Tab buttons use `role="tablist"/"tab"/"tabpanel"` with proper ARIA attributes for screen reader accessibility |
| Actual | Tab buttons are plain `<button type="button">` elements without any tab ARIA roles (`ArtDecoDashboard.vue:348-355`, `384-391`) |
| Evidence | Template lines 348-355 (flow-tabs), 384-391 (pool-tabs): `<button v-for="(tab, _idx) in flowTabs" :key="tab.key" type="button" class="flow-tab">` |
| Repair Target | `ArtDecoDashboard.vue` |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-02] High: Emoji used as navigation icons instead of ArtDecoIcon

| Field | Value |
|-------|-------|
| Source Roles | functional-audit, visual-artdeco-audit |
| Dedupe Key | `dashboard-emoji-nav-icons` |
| Severity | High |
| Trigger | User scrolls to quick-nav section |
| Expected | Navigation icons use `ArtDecoIcon` component for consistency and cross-platform rendering |
| Actual | Quick nav uses emoji characters (📈📋🔍💼🎯⚠️) as icon elements (`ArtDecoDashboard.vue:417-445`) |
| Evidence | Template lines 417, 421, 425, 429, 433, 437: `<div class="nav-icon">📈</div>` etc. |
| Repair Target | `ArtDecoDashboard.vue` |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-03] High: Stock pool tabs are decorative only, no data backing

| Field | Value |
|-------|-------|
| Source Roles | functional-audit, data-state-audit |
| Dedupe Key | `dashboard-stock-pool-no-data` |
| Severity | High |
| Trigger | User clicks stock pool tabs (自选/持仓/重点) |
| Expected | Tab switching triggers data fetch for the selected pool, or tabs are hidden/disabled if backend not connected |
| Actual | `activePoolTab` changes on click but `stockPoolGroups` is never populated from any API call. All tabs always show the same empty state notice: "真实接口尚未接入" (`useArtDecoDashboard.ts:126-130, 136-144`) |
| Evidence | Composable lines 126-130: `stockPoolGroups` init as empty; line 143: `stockPoolNotice` always returns "尚未接入" message |
| Repair Target | `ArtDecoDashboard.vue` (hide or disable tabs), `useArtDecoDashboard.ts` (wire to API or remove) |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-04] High: Zero-initialized market data rendered before first load

| Field | Value |
|-------|-------|
| Source Roles | data-state-audit |
| Dedupe Key | `dashboard-zero-init-before-load` |
| Severity | High |
| Trigger | Page load, before first API response completes |
| Expected | Loading skeleton covers ALL data surfaces until first verified snapshot |
| Actual | `marketData` initializes with `'0.00'` string values and `0` numbers (`useArtDecoDashboard.ts:87-100`). Before the first API response, ArtDecoStatCards render these zeros as if they were real data. `showFundFlowSkeleton` only covers the fund flow section, not the market indicators section. |
| Evidence | Composable lines 87-100: `shanghai: { index: '0.00', change: '0.00' }`, etc. Template line 119: market indicators section uses `v-else` after loading check, but the initial state has `loading.market = true` which shows skeleton correctly; however the stat cards at lines 120-146 will flash zeros on mount before loading flag takes effect in the reactive cycle. |
| Repair Target | `useArtDecoDashboard.ts` (use null/undefined initial state), `ArtDecoDashboard.vue` (add loading guard) |
| Primary Owner | `useArtDecoDashboard.ts` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-05] High: Sentiment indicator derived from industry counts, not stock counts

| Field | Value |
|-------|-------|
| Source Roles | data-state-audit |
| Dedupe Key | `dashboard-sentiment-from-industry` |
| Severity | High |
| Trigger | Page loads industry flow data |
| Expected | Market sentiment percentage reflects the ratio of rising to falling individual stocks |
| Actual | `marketSentiment` (line 276-284) is derived from `marketData.stocks.up/down` which are populated in `fetchIndustryFlow` (line 424-426) by counting rising/falling industries from the top-12 industry flow response, NOT from actual stock counts. With 12 industries where 8 are rising, sentiment shows 67%, which is misleading as "market sentiment". |
| Evidence | Composable lines 424-426: `const rising = marketHeat.value.filter(item => item.change > 0).length` — these are industry items, not stocks |
| Repair Target | `useArtDecoDashboard.ts` |
| Primary Owner | `useArtDecoDashboard.ts` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-06] High: Display font (Cinzel) used for UI labels, buttons, and navigation

| Field | Value |
|-------|-------|
| Source Roles | visual-artdeco-audit |
| Dedupe Key | `dashboard-display-font-in-ui` |
| Severity | High |
| Trigger | Visual inspection of stress test button, indicator names, and navigation labels |
| Expected | Cinzel reserved exclusively for page title and section-level headings. Buttons, indicator names, and nav labels use Barlow (body font) |
| Actual | `.stress-test-btn` uses `artdeco-font-display` (SCSS line 738), `.indicator-name` uses `artdeco-font-display` (SCSS line 524), `.nav-label` uses `artdeco-font-display` (SCSS line 471). Cinzel is a decorative serif designed for hero headlines, reducing readability at small sizes for UI labels. |
| Evidence | SCSS line 738: `font-family: var(--artdeco-font-display)` in `.stress-test-btn`; line 524: same in `.indicator-name`; line 471: same in `.nav-label` |
| Repair Target | `ArtDecoDashboard.scss` |
| Primary Owner | `ArtDecoDashboard.scss` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-07] High: Identical 3-column card grid without visual hierarchy

| Field | Value |
|-------|-------|
| Source Roles | visual-artdeco-audit |
| Dedupe Key | `dashboard-identical-card-grid` |
| Severity | High |
| Trigger | Visual inspection of content-grid section |
| Expected | Visual hierarchy differentiates high-value charts from low-value navigation and status cards |
| Actual | `.content-grid` uses `repeat(3, 1fr)` (SCSS line 127) with 9 cards of similar visual weight. Market heatmap (high value) and quick nav (low value) occupy the same grid cell size. PRODUCT.md anti-references ban "identical card grids: same-sized cards with icon + heading + text, repeated endlessly." |
| Evidence | SCSS line 127: `grid-template-columns: repeat(3, 1fr)` — 9 cards: heatmap, capital-flow-heatmap, sector-radar, stress-test, longhu-bang, block-trading, capital-ranking, stock-pool, quick-nav |
| Repair Target | `ArtDecoDashboard.scss`, `ArtDecoDashboard.vue` |
| Primary Owner | `ArtDecoDashboard.scss` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-08] Medium: `captureCoreTrace` only records last request from parallel batch

| Field | Value |
|-------|-------|
| Source Roles | data-state-audit |
| Dedupe Key | `dashboard-core-trace-overwrite` |
| Severity | Medium |
| Trigger | Page load triggers 6+ parallel API requests |
| Expected | Meta bar shows request ID and process time for the primary data surface |
| Actual | `captureCoreTrace` (line 178-185) overwrites `lastVerifiedCoreRequestId` with each response. In `refreshData` (line 647-662), 6 parallel requests all call `captureCoreTrace`. The meta bar displays whichever response arrives last, not necessarily the most relevant one. |
| Evidence | Composable line 178-185: `captureCoreTrace` unconditionally overwrites; line 651: `Promise.all` races all fetches |
| Repair Target | `useArtDecoDashboard.ts` |
| Primary Owner | `useArtDecoDashboard.ts` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-09] Medium: No `prefers-reduced-motion` media query

| Field | Value |
|-------|-------|
| Source Roles | responsive-a11y-audit, visual-artdeco-audit |
| Dedupe Key | `dashboard-no-reduced-motion` |
| Severity | Medium |
| Trigger | User has `prefers-reduced-motion: reduce` enabled in OS settings |
| Expected | Hover transforms (translateY) and transitions degrade to opacity-only or no animation |
| Actual | No `@media (prefers-reduced-motion)` exists in `ArtDecoDashboard.scss`. All hover transforms (`translateY` on flow-item, stock-item, nav-item, heat-item) persist regardless of motion preference. |
| Evidence | SCSS lines 163, 698, 707, 715: hover `transform: translateY(...)` without reduced-motion guard |
| Repair Target | `ArtDecoDashboard.scss` |
| Primary Owner | `ArtDecoDashboard.scss` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | Pattern-level: other ArtDeco pages may have the same gap |
| Verification Surface | code-review-only |

### [F-10] Medium: 6+ inline styles in template

| Field | Value |
|-------|-------|
| Source Roles | visual-artdeco-audit, responsive-a11y-audit |
| Dedupe Key | `dashboard-inline-styles` |
| Severity | Medium |
| Trigger | Code review |
| Expected | All styles in SCSS files per project CSS development guide |
| Actual | Template contains 6+ inline style attributes: `style="height: 300px;"` on 3 heatmap sections (lines 267, 285, 296), `style="margin-top: 10px;"` on skeleton (line 213), `style="height: 100%; display: flex; align-items: center; justify-content: center;"` on skeleton wrapper (line 269), `:style="{ width: marketSentiment + '%' }"` on sentiment fill (line 193) |
| Evidence | Template lines 213, 267, 269, 285, 296, 193 |
| Repair Target | `ArtDecoDashboard.vue`, `ArtDecoDashboard.scss` |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-11] Medium: Decorative gradient overlay on primary data surface

| Field | Value |
|-------|-------|
| Source Roles | visual-artdeco-audit |
| Dedupe Key | `dashboard-gradient-overlay-competing` |
| Severity | Medium |
| Trigger | Visual inspection of dashboard background |
| Expected | PRODUCT.md: "A gold glow that obscures a price tick is a bug, not a feature." ArtDeco drama reserved for brand-forward moments |
| Actual | `::before` applies radial gradient overlay (gold 4% + bronze 3%) on the entire dashboard (SCSS lines 35-45). `.chart-section` adds gradient background (SCSS lines 668-673). `.stress-test-btn` uses gradient fill (SCSS line 736). Multiple gradient layers on the primary data surface. |
| Evidence | SCSS lines 35-45: `::before` with `radial-gradient(...)`; lines 668-673: `.chart-section` gradient |
| Repair Target | `ArtDecoDashboard.scss` |
| Primary Owner | `ArtDecoDashboard.scss` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-12] Medium: Stress test is purely local formula presented as authoritative result

| Field | Value |
|-------|-------|
| Source Roles | functional-audit, data-state-audit |
| Dedupe Key | `dashboard-stress-test-local-only` |
| Severity | Medium |
| Trigger | User clicks "立即执行压力测试" button |
| Expected | Either a real backend stress test with clear "本地估算" labeling, or the button label makes clear this is a local estimate |
| Actual | `runOneClickStressTest()` (line 692-711) computes drawdown/VaR/concentration from current data with hardcoded coefficients. Results are displayed with the same visual weight as real API data. No "本地估算" disclaimer visible in the result area. The note text (line 319-320) says "基于当前页面已加载的真实行情数据做本地估算" but this disappears once results are shown. |
| Evidence | Composable lines 692-711: local formula with `Math.min(25, ...)` etc.; Template line 319-320: note text only visible when no result exists |
| Repair Target | `ArtDecoDashboard.vue` (add persistent disclaimer), `useArtDecoDashboard.ts` (optional: label as estimate) |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-13] Medium: Collapsible sections default expanded, contributing to information overload

| Field | Value |
|-------|-------|
| Source Roles | functional-audit |
| Dedupe Key | `dashboard-collapsibles-default-expanded` |
| Severity | Medium |
| Trigger | Page load |
| Expected | Secondary data (indicators, monitoring) default collapsed to reduce initial cognitive load |
| Actual | `indicatorsExpanded` and `monitoringExpanded` both initialize as `true` (composable lines 148-149). All sections are fully expanded on page load, presenting ~15 data panels simultaneously. |
| Evidence | Composable lines 148-149: `const indicatorsExpanded: Ref<boolean> = ref(true)` and `const monitoringExpanded: Ref<boolean> = ref(true)` |
| Repair Target | `useArtDecoDashboard.ts` |
| Primary Owner | `useArtDecoDashboard.ts` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-14] Medium: Non-token opacity and spacing values

| Field | Value |
|-------|-------|
| Source Roles | visual-artdeco-audit |
| Dedupe Key | `dashboard-non-token-values` |
| Severity | Medium |
| Trigger | Code review |
| Expected | All opacity and spacing values use design system tokens |
| Actual | `.card-header .artdeco-icon` has `opacity: 86%` (SCSS line 648, not a token), `.stress-test-btn:disabled` has `opacity: 80%` (SCSS line 758, not a token), `.artdeco-dashboard` has `padding: 2rem` (SCSS line 17, not a token), inline `style="margin-top: 10px;"` (template line 213) |
| Evidence | SCSS line 648: `opacity: 86%`, line 758: `opacity: 80%`, line 17: `padding: 2rem` |
| Repair Target | `ArtDecoDashboard.scss`, `ArtDecoDashboard.vue` |
| Primary Owner | `ArtDecoDashboard.scss` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-15] Medium: Responsive breakpoints below desktop minimum

| Field | Value |
|-------|-------|
| Source Roles | responsive-a11y-audit |
| Dedupe Key | `dashboard-below-minimum-breakpoints` |
| Severity | Medium |
| Trigger | Viewport width at 1200px, 1024px, 768px, or 394px |
| Expected | PRODUCT.md states desktop-only (minimum 1280x720). CLAUDE.md prohibits `@media (max-width)` responsive rules |
| Actual | Four breakpoints exist below 1280px: 1200px (SCSS line 489), 1024px (SCSS line 796), 768px (SCSS line 803), 394px (SCSS line 818). These are legacy but still active. PRODUCT.md now acknowledges "Some 768px breakpoint rules exist in legacy code but are not a supported target." |
| Evidence | SCSS lines 489, 796, 803, 818: all `@media (width <= ...)` with values below 1280px |
| Repair Target | `ArtDecoDashboard.scss` (evaluate which to keep as graceful degradation, which to remove) |
| Primary Owner | `ArtDecoDashboard.scss` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | Pattern-level: other pages may have similar legacy breakpoints |
| Verification Surface | code-review-only |

### [F-16] Medium: Semantic HTML incomplete for data pairs

| Field | Value |
|-------|-------|
| Source Roles | responsive-a11y-audit |
| Dedupe Key | `dashboard-semantic-html-incomplete` |
| Severity | Medium |
| Trigger | Screen reader navigation of data cards |
| Expected | Data pairs (label + value) use `<dl>`/`<dt>`/`<dd>` or `<article>` with appropriate ARIA |
| Actual | Card content uses generic `<div>` elements for all data pairs. Stat cards, indicator items, monitor items, flow items all use `<div class="metric-label">` / `<div class="metric-value">` without semantic markup. |
| Evidence | Template lines 240-244 (indicator-item), 256-259 (monitor-item), 323-335 (stress-metric-item) |
| Repair Target | `ArtDecoDashboard.vue` |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-17] Low: Brand name "QUANTIX" appears twice in visible header area

| Field | Value |
|-------|-------|
| Source Roles | functional-audit, visual-artdeco-audit |
| Dedupe Key | `dashboard-brand-duplicate` |
| Severity | Low |
| Trigger | Visual inspection of page header |
| Expected | Brand name appears once in the header area |
| Actual | "QUANTIX" appears in both `ArtDecoHeader` component (template line 5) and `.request-meta-bar` (template line 13: `<span class="brand-text dashboard-brand">QUANTIX</span>`) |
| Evidence | Template line 5: `<ArtDecoHeader title="QUANTIX" .../>`, line 13: `<span class="brand-text dashboard-brand">QUANTIX</span>` |
| Repair Target | `ArtDecoDashboard.vue` |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

### [F-18] Low: `_idx` unused index variable in v-for loops

| Field | Value |
|-------|-------|
| Source Roles | functional-audit |
| Dedupe Key | `dashboard-unused-vfor-index` |
| Severity | Low |
| Trigger | Code review |
| Expected | Unused loop variables are omitted or prefixed with `_` |
| Actual | Three v-for loops declare `_idx` but never use it: flow-tabs (line 349), pool-tabs (line 385), and potentially in skeleton loops. The `_` prefix convention is correct for unused variables but linters may still flag these. |
| Evidence | Template line 349: `v-for="(tab, _idx) in flowTabs"`, line 385: `v-for="(tab, _idx) in poolTabs"` |
| Repair Target | `ArtDecoDashboard.vue` |
| Primary Owner | `ArtDecoDashboard.vue` |
| Can Fix Frontend | Yes |
| Cross-Page Impact | None |
| Verification Surface | code-review-only |

---

## State Coverage Assessment

| State | Covered | Notes |
|-------|---------|-------|
| Default (success) | Yes | All sections render with live API data |
| Loading | Partial | Skeleton loading exists for fund flow, market indicators, capital flow. Missing: no skeleton for stock pool, longhu-bang, block-trading |
| Empty | Partial | Stock pool shows "尚未接入" notice. Capital flow shows degraded message. Missing: explicit empty state for indicators and monitoring when API returns empty array |
| Error | Yes | Per-section error messages, global dashboard-alerts bar, aggregate DATA/SYNC status |
| Disabled | Yes | Stress test button disabled when market/fundFlow loading or errored |
| Extreme Data | Not verified | code-review-only mode; no live test with extreme values |

---

## Positive Findings

1. **Stale data preservation is well-implemented.** The composable correctly preserves last verified snapshots on refresh failure with degraded messaging (e.g., "当前仍显示上次成功同步的排名快照"). Each data slice has its own `hasVerified*Snapshot` flag.

2. **Aggregate provenance is honest.** `aggregateDataStatus` and `aggregateSyncStatus` accurately track PENDING/REAL/MIXED/DEGRADED/UNAVAILABLE based on primary slice states. They do not claim success when slices are partial.

3. **A-share color convention is correct.** Rise/up/inflow uses `--artdeco-up` (#FF5252, red) and fall/down/outflow uses `--artdeco-down` (#00E676, green) consistently across all rendered surfaces.

4. **ARIA live regions are in place.** Both `request-meta-bar` and `dashboard-alerts` have `aria-live="polite"`, ensuring screen readers announce status changes.

5. **Focus-visible styles are present.** Interactive elements (flow-tab, pool-tab, stress-test-btn, nav-item) all have gold focus-visible styles for keyboard users.

6. **Tabular numeric alignment.** All numeric data uses `artdeco-font-mono` (JetBrains Mono) which enforces `font-variant-numeric: tabular-nums`.

7. **Success: false envelope handling.** `assertDashboardResponseSucceeded` correctly checks for resolved `success: false` envelopes and throws, preventing silent failures.

---

## Shared-Impact Candidates

| Issue | Shared Impact? | Reason |
|-------|---------------|--------|
| F-06 (display font in UI) | No | Dashboard-local SCSS |
| F-07 (identical card grid) | No | Dashboard-local layout |
| F-09 (prefers-reduced-motion) | Yes | Pattern-level gap likely exists in other ArtDeco pages |
| F-15 (below-minimum breakpoints) | Yes | Pattern-level legacy issue across codebase |

---

## Deferred Items

| Issue | Reason |
|-------|--------|
| Live-audit verification | Browser automation not available for this run; all findings are code-review-only |
| ArtDecoLongHuBang audit | Separate component; should be audited independently |
| ArtDecoBlockTrading audit | Separate component; should be audited independently |
| Extreme data state testing | Requires live API manipulation |

---

## Triage Summary

| Bucket | Count | Issues |
|--------|-------|--------|
| Fix-now (frontend-fixable, page-local) | 14 | F-01, F-02, F-03, F-04, F-06, F-07, F-09, F-10, F-11, F-12, F-13, F-14, F-16, F-17, F-18 |
| Fix-with-shared-impact-review | 2 | F-09, F-15 (pattern-level, may need cross-page coordination) |
| Defer (backend/API dependency) | 2 | F-05 (needs stock count API), F-08 (needs trace redesign) |

---

*Report generated 2026-05-10 | MyWeb Audit: /dashboard | Mode: Quick | Surface: code-review-only | 18 findings (8 High, 8 Medium, 2 Low)*
