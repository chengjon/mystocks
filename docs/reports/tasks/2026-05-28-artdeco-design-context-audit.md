# ArtDeco Web Design Context Audit

Date: 2026-05-28

OpenSpec change: `add-artdeco-impeccable-design-gate`

Primary plan: `docs/reports/tasks/2026-05-28-artdeco-web-design-alignment-plan.md`

## 1. Purpose

This report is the documentation-phase equivalent of `$impeccable document`.

It audits the currently implemented Web ArtDeco design system, source document chain, route truth, style layers, and first pilot target before any frontend implementation work begins. It does not modify Vue, TypeScript, SCSS, route, token, component, or composable files.

## 2. Evidence Mode

Evidence was gathered from local source files and ArtDeco documents by static inspection.

No live browser overlay was run in this phase. No PM2, E2E, build, or frontend quality-gate success is claimed here because no UI implementation has been performed.

Existing `DESIGN.md` was not overwritten. Because `DESIGN.md` already exists, this phase records design-context findings as an approval artifact instead of silently regenerating the root design file.

## 3. Implemented Style Layer Findings

| File | Observed Role | Current Signal | Design-Gate Finding |
|---|---|---:|---|
| `web/frontend/src/styles/artdeco-tokens.scss` | Primary ArtDeco token source | 692 lines, 233 custom properties, 85 `--ad-*` variables | Treat as canonical token source for new work. It already carries button and input state-machine tokens and imports the ArtDeco font stack. |
| `web/frontend/src/styles/element-plus-artdeco.scss` | Element Plus bridge | 543 lines, 79 custom properties, 36 unique hex colors | Bridge layer still contains local literal color values. Do not rewrite wholesale during documentation phase; normalize only touched implementation scope after approval. |
| `web/frontend/src/styles/artdeco-global.scss` | Global ArtDeco composition | 532 lines, imports tokens, extended quant, patterns, financial, grid | Acts as the runtime composition layer. It should not become the token truth source. |
| `web/frontend/src/styles/artdeco-financial.scss` | Financial semantic layer | 435 lines, 108 custom properties, 13 unique hex colors | Encodes finance-specific palette and semantics. It is useful for A-share states, but should be reconciled with `--ad-*` token language when touched. |
| `web/frontend/src/styles/bloomberg-terminal-override.scss` | Terminal-style compatibility override | 551 lines, 46 custom properties, 45 unique hex colors | High-risk legacy override surface. Keep it scoped to terminal surfaces; do not use it as general ArtDeco route truth. |

## 4. Source Document Alignment

| Document | Current Role | Finding |
|---|---|---|
| `PRODUCT.md` | Product and Web design context | Defines Web as a desktop product surface, not a marketing site. Confirms route truth, data-before-ornament, `artdeco-tokens.scss`, A-share red-up and green-down semantics, and known `/dashboard` exception. |
| `DESIGN.md` | Experience-strategy truth for active ArtDeco frontend work | Already includes Web implementation truth, page design standards, surface patterns, token governance, and state standards. It should be refined from evidence, not treated as a one-time ideal document. |
| `docs/guides/web/ARTDECO_MASTER_INDEX.md` | Current ArtDeco reading path | Already distinguishes reusable assets, page-level assets, and route truth. It says route truth is `router/index.ts` plus `views/<domain>/*.vue` with limited ArtDeco exceptions. |
| `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md` | Current unified ArtDeco spec | Remains a main guide for runtime, density, financial feedback, and component semantics. It should be cross-checked with `DESIGN.md` for page grammar and state language. |
| `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` | Component catalog | Useful for candidate reuse, but it should not decide route ownership. Use it to avoid duplicate component extraction. |
| `docs/api/ArtDeco_System_Architecture_Summary.md` | Architecture summary reference | Needs to remain a reference document, not the runtime or API truth source. |
| `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` | Placement and reuse guide | Explicitly states active business route pages prefer `views/<domain>/*.vue`, not default `artdeco-pages/**`. Use it before extracting components. |
| `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md` | Historical baseline | Explicitly historical. Do not rewrite it as current implementation truth without re-verification. |
| `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md` | Compatibility entry | Short historical compatibility pointer. Keep it as pointer unless a documentation cleanup task is approved. |
| `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md` | Compatibility entry | Short historical compatibility pointer. Keep it as pointer unless a documentation cleanup task is approved. |

## 5. Route Truth Findings

Confirmed route signals:

- `/dashboard` is backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The market realtime route imports `web/frontend/src/views/market/Realtime.vue`.
- `/trade/terminal` redirects to or uses `web/frontend/src/views/TradingDashboard.vue`.
- Active route truth is not equal to all files under `views/artdeco-pages/**`.

Design consequence:

- Page audits should target active routed pages first.
- `views/artdeco-pages/**` should be treated as a mix of dashboard exception, workbench pages, embedded blocks, wrappers, and compatibility assets.

## 6. Optimization Findings

| Priority | Finding | Why It Matters | Recommended Handling |
|---|---|---|---|
| P0 | Preserve approval boundary between design docs and implementation | `architecture/STANDARDS.md` requires UI/UX changes to go through design/proposal approval before code changes | Keep current phase documentation-only. Do not run `craft` or source edits before approval. |
| P0 | Route truth must stay anchored to router and `views/<domain>` | Misreading `views/artdeco-pages/**` as route truth would send implementation to the wrong ownership boundary | Keep this as a checklist item for every page critique. |
| P1 | `market/Realtime.vue` is the right first pilot | It is a high-value, data-dense, state-rich route that tests freshness, filters, table structure, and A-share semantics | Run critique and shape before implementation. |
| P1 | Stale/freshness state deserves explicit design treatment | Current route has loading, error, empty, and cache states, but no explicit stale state signal in the inspected source | Shape brief should define freshness strip, cache/stale/degraded labels, and retry behavior. |
| P1 | Token language is split between `--ad-*` and `--artdeco-*` families | The product/design docs prefer the `--ad-*` governance vocabulary, while existing pages still use `--artdeco-*` runtime variables | Do not rewrite broadly. In approved implementation scope, document whether values are canonical, alias-backed, or legacy bridge values. |
| P2 | Header band, control bar, status strip, and data panel are reusable candidates | These patterns are likely to recur across market, trade, risk, and system routes | Extract only after a second consumer or approved extraction rationale exists. |
| P2 | Component catalog should be used before new component creation | Existing ArtDeco components already include header, button, select, stat card, table, and card primitives | Prefer composition of existing components in first pilot. |
| P3 | Compatibility pointer docs are already short and correctly demoted | Lowercase/uppercase compatibility entries mostly point to current docs or mark historical status | Defer cleanup unless a doc pass explicitly approves pointer polish. |

## 7. Recommendation

Proceed to the first static page critique:

```text
$impeccable critique web/frontend/src/views/market/Realtime.vue
```

Then produce a shape brief for approval. Do not edit frontend implementation files until the critique and shape brief are reviewed and explicitly approved.
