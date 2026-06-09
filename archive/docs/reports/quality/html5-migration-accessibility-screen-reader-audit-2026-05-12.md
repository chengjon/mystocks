# HTML5 Migration Accessibility Screen Reader Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.8.4 Add screen reader optimizations`
Scope: Desktop-only, repo-local audit only

## Decision

`2.8.4` remains open.

This batch records current screen-reader related evidence for stock, market, trading, and risk data surfaces. The repo already contains live-region helpers and several local `role="status"`, `role="alert"`, `aria-live`, and descriptive label patterns. It does not yet define or verify a domain-specific screen-reader narration strategy for financial data.

## Evidence Checked

Commands:

```bash
rg -n "aria-live|role=\"status\"|role=\"alert\"|screen reader|screenreader|sr-only|visually-hidden|aria-label|announce|announcement|liveRegion|useAria|price|涨跌|涨幅|成交|风险|买入|卖出|signal|volume" web/frontend/src/views/{market,data,watchlist,strategy,trade,risk,system} web/frontend/src/components/artdeco web/frontend/src/components/market web/frontend/src/components/technical web/frontend/src/composables/useAria
find web/frontend/src/composables/useAria -maxdepth 2 -type f -print -exec sed -n '1,180p' {} \;
```

Observed repo facts:

- `web/frontend/src/composables/useAria/use-aria.ts` provides a `liveRegion(label, politeness)` helper and documents a real-time data card example for `上证指数`.
- `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` exposes statistic values as `role="status"` with `aria-live="polite"` and labels such as `${label}: ${displayValue}`.
- Several current views expose runtime or data-loading feedback through `role="status"`, `role="alert"`, or `aria-live="polite"`, including industry/data views, strategy GPU runtime banners, risk stop-loss messages, and trade execution runtime messages.
- Trading and market surfaces contain many financial concepts that would require narration rules, including price, change percentage, volume, turnover, risk level, buy/sell direction, signal confidence, and execution result.
- The ARIA helper type surface supports labels, described-by, live regions, invalid state, modal/dialog state, selected state, checked state, and value text, which can support a future screen-reader strategy.

## Gap Summary

The current repo has generic screen-reader primitives, but not a domain-specific screen-reader contract for financial data.

There is no verified narration standard for stock code/name, latest price,涨跌幅,涨跌额, volume, turnover, risk severity, buy/sell/hold signals, confidence values, order status, stop-loss thresholds, or chart/heatmap summaries. Without such a standard, local `aria-label` and `aria-live` usage cannot be treated as stock-data reading optimization.

There is no evidence of screen-reader acceptance using NVDA, VoiceOver, ChromeVox, or an equivalent manual verification record. Existing axe smoke coverage can detect selected accessibility violations, but it does not prove that dynamic stock and trading data is read in the intended order or with the intended business meaning.

Live regions exist, but this audit did not find a throttling or priority policy for rapidly changing market values. A future implementation needs to avoid noisy announcements for high-frequency data while still announcing meaningful state changes.

## Task Disposition

Keep `2.8.4` unchecked until a later approved batch defines and verifies screen-reader narration for representative stock, market, trade, and risk surfaces.

Minimum future evidence should include:

- A financial data screen-reader copy standard for prices,涨跌幅, volume, risk levels, trade directions, signals, and status changes.
- A policy for live-region priority and throttling on dynamic market data.
- Representative implementation or approved alternative patterns for stat cards, data tables, trading forms, alerts, and chart summaries.
- Manual or automated acceptance evidence with at least one screen-reader workflow.
