# ArtDeco Critique: `market/Realtime.vue`

Date: 2026-05-28

OpenSpec change: `add-artdeco-impeccable-design-gate`

Target: `web/frontend/src/views/market/Realtime.vue`

## 1. Scope

This is a documentation-phase critique. It audits the implemented source and design fit before any UI implementation change.

No browser overlay, live visual screenshot, PM2 verification, E2E run, or source implementation is claimed in this report. The page should be re-critiqued with a live browser overlay after an approved implementation pass.

## 2. Evidence Summary

Observed source facts:

- The route page exists and is 512 lines.
- It imports `ArtDecoButton`, `ArtDecoCard`, `ArtDecoHeader`, `ArtDecoIcon`, `ArtDecoSelect`, `ArtDecoStatCard`, and `ArtDecoTable`.
- It uses `useArtDecoApi`, `apiClient`, and `extractRealtimeMarketOverview`.
- It has preset selection, refresh, request id display, current cache source tracking, loading, error, empty, and cache banner states.
- It has no hard-coded hex colors in the inspected page.
- It uses scoped SCSS with ArtDeco variables such as `--artdeco-spacing-*`, `--artdeco-bg-*`, `--artdeco-rise`, `--artdeco-down`, and `--artdeco-gold-*`.
- The inspected source had `stale` keyword count of 0, while cache state is present.

## 3. Design Health Score

Overall static score: `27 / 40`

| # | Heuristic | Score | Key Issue |
|---:|---|---:|---|
| 1 | Visibility of system status | 3 | Loading, error, empty, and cache are visible, but data freshness and stale age are not explicit enough. |
| 2 | Match between system and real world | 3 | A-share rise/fall semantics are present, but English decorative labels weaken the Chinese trading-terminal register. |
| 3 | User control and freedom | 3 | Preset selection, refresh, and retry exist, but refresh appears in two places without clear hierarchy. |
| 4 | Consistency and standards | 2 | Page uses ArtDeco components, but nested shells and local state banners create page-specific grammar. |
| 5 | Error prevention | 2 | Cache state exists, but stale or degraded data risk is not separated from successful snapshots. |
| 6 | Recognition rather than recall | 3 | Table, stat strip, select, and banners are understandable. Request id and freshness metadata could be more human-readable. |
| 7 | Flexibility and efficiency | 2 | Useful for a sample quote view, but lacks density controls, quick filters, or richer table affordances for power users. |
| 8 | Aesthetic and minimalist design | 3 | Strong ArtDeco token usage and no raw hex values, but the hero shell and gold stat treatment compete with data work. |
| 9 | Help users recover from errors | 3 | Error banner and retry are present. Recovery copy can be more precise about source, cache, and retry expectation. |
| 10 | Help and documentation | 3 | Inline copy explains the sample route, but microcopy should be more operational and less decorative. |

## 4. What Is Working

- The page already composes canonical ArtDeco components instead of hand-rolling all controls.
- The page avoids hard-coded hex colors in the inspected target file.
- Runtime state coverage is better than many legacy pages: loading, error, empty, cache, retry, and placeholder logic are already present.
- Financial rise/fall semantics are represented through `rise`, `fall`, `flat`, `--artdeco-rise`, `--artdeco-down`, and distribution segments.

## 5. Priority Issues

### P1: Freshness and stale state are underspecified

What: The page tracks cache source and request id, but the inspected source does not expose a distinct stale state or age-based freshness model.

Why: A real-time market page must make freshness trustworthy under pressure. Cache, stale, degraded, and live states are not interchangeable.

Fix direction: Shape a status strip that separates `live`, `refreshing`, `cache`, `stale`, `degraded`, `empty`, and `error` states with short operational copy.

Suggested command: `$impeccable shape web/frontend/src/views/market/Realtime.vue`

### P1: Page hierarchy reads partly like a hero surface

What: The page starts with a `hero-shell`, English eyebrow text such as `live quote observatory`, and a large theatrical shell before the user reaches the quote work area.

Why: This is a task page for live market monitoring. ArtDeco should frame the instrument, not delay the user with brand-like hero composition.

Fix direction: Convert the top area into a compact route header band with status, freshness, and one primary refresh action.

Suggested command: `$impeccable shape web/frontend/src/views/market/Realtime.vue`

### P1: Control hierarchy is split

What: Refresh appears in the header action and again in the toolbar. Preset selection sits inside a nested content shell.

Why: Repeated controls increase cognitive load and make the page feel assembled rather than governed by a page grammar.

Fix direction: Put preset, refresh, and state metadata into one `ArtDecoControlBar` pattern for the pilot. Keep one primary refresh action.

Suggested command: `$impeccable shape web/frontend/src/views/market/Realtime.vue`

### P1: Nested surfaces reduce data density

What: The page stacks `hero-shell`, `stats-strip`, `content-shell`, `toolbar`, and nested `ArtDecoCard` panels.

Why: Nested cards are a known product-design risk in this project. They create visual cost without improving the user decision path.

Fix direction: Use full-width bands and unframed internal layouts. Reserve cards for repeated panels or genuinely framed tools.

Suggested command: `$impeccable shape web/frontend/src/views/market/Realtime.vue`

### P2: Reusable route patterns are visible but not yet extracted

What: Header band, control bar, state banner, data panel, and distribution panel are all reusable candidates.

Why: The project has many data-dense pages. A successful pilot can become a route-level pattern, but extraction from one page is premature.

Fix direction: Design the pilot with named candidate patterns, then extract only after a second page proves reuse.

Suggested command: `$impeccable extract web/frontend/src/views/market/Realtime.vue` after approval and second-consumer evidence

### P2: Token vocabulary needs a bridge decision

What: The page uses `--artdeco-*` variables heavily while current product/design governance emphasizes `--ad-*` token language.

Why: Broad token cleanup can become churn. But every touched implementation should know whether it uses canonical tokens, alias-backed tokens, or compatibility values.

Fix direction: Shape brief should classify token cleanup as touched-scope only and avoid broad SCSS migration.

Suggested command: `$impeccable shape web/frontend/src/views/market/Realtime.vue`

## 6. Minor Observations

- `sample quote route` and `live quote observatory` are decorative English labels on a Chinese quantitative trading product surface.
- `样本快照与分布面板` is accurate, but the page could be more direct: current sample, freshness, quote table, breadth distribution.
- The distribution bar is useful, but the text and color should remain legible if one segment is very small.
- Responsive media rules exist, but mobile is not a product target for this plan. Do not over-invest in mobile redesign.

## 7. Static Anti-Pattern Verdict

The page does not look like generic blue SaaS or obvious AI slop. It has real product structure and ArtDeco specificity.

The main risk is a subtler product issue: a trading route is borrowing too much overview-page theater. Gold surfaces, hero language, and nested shells should be quieter so market state and freshness become the visual priority.

## 8. Recommended Next Step

Create the shape brief for approval:

```text
$impeccable shape web/frontend/src/views/market/Realtime.vue
```

Do not run `craft` or edit source files until the shape brief is approved.
