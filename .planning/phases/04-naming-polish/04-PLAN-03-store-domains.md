---
wave: 3
depends_on: []
files_modified:
  - web/frontend/src/stores/market.ts
  - web/frontend/src/stores/marketData.ts
  - web/frontend/src/stores/trading.ts
  - web/frontend/src/stores/tradingData.ts
requirements_addressed: [NAME-05]
autonomous: true
must_haves:
  - Each overlapping store pair has domain boundary comment at top of file
  - Frontend build succeeds after changes
  - No store code logic modified
---

# Plan 03: Store Domain Clarification (NAME-05)

**Objective:** Document domain boundaries for overlapping Pinia store pairs. Documentation-only — no code logic changes, no merging.

## Task 1: Add domain boundary comments to market stores

<read_first>
- `web/frontend/src/stores/market.ts` — simple API wrapper store
- `web/frontend/src/stores/marketData.ts` — enhanced store with IndexedDB
</read_first>

<action>
1. At the top of `web/frontend/src/stores/market.ts` (before existing imports), add:
```typescript
/**
 * Domain: Market Overview & Analysis (Simple API Wrapper)
 *
 * Provides lightweight market data access via the baseStore template pattern.
 * Responsible for: market overview, market analysis (technical/capital_flow/longhu_bang).
 * Consumers: overview widgets, simple dashboard cards.
 *
 * For enhanced market data with IndexedDB caching, offline support,
 * and web worker integration, see marketData.ts.
 */
```

2. At the top of `web/frontend/src/stores/marketData.ts` (before existing imports), add:
```typescript
/**
 * Domain: Market Data with IndexedDB Caching (Enhanced)
 *
 * Provides rich market data management with intelligent caching (IndexedDB → Network → Fallback),
 * offline support, sync status tracking, and web worker integration for technical indicators.
 * Responsible for: cached market data, technical indicator computation, offline-first access.
 * Consumers: chart views, analysis pages, data-intensive components.
 *
 * For simple real-time market overview without caching, see market.ts.
 */
```
</action>

<acceptance_criteria>
- `web/frontend/src/stores/market.ts` line 1 contains `Domain: Market Overview`
- `web/frontend/src/stores/marketData.ts` line 1 contains `Domain: Market Data with IndexedDB`
- Both files contain `see market` referencing the other store
- Neither file's export signatures or logic changed
</acceptance_criteria>

## Task 2: Add domain boundary comments to trading stores

<read_first>
- `web/frontend/src/stores/trading.ts` — trade orders & system status
- `web/frontend/src/stores/tradingData.ts` — trading signals, history, analytics
</read_first>

<action>
1. At the top of `web/frontend/src/stores/trading.ts` (before existing imports), add:
```typescript
/**
 * Domain: Trading Operations (Orders & System Status)
 *
 * Manages trade order execution, system health monitoring, and basic trading state.
 * Responsible for: trade order CRUD, system health data, system info.
 * Consumers: order placement UI, system status dashboard.
 *
 * For trading analytics (signals, history, positions, performance),
 * see tradingData.ts.
 */
```

2. At the top of `web/frontend/src/stores/tradingData.ts` (before existing imports), add:
```typescript
/**
 * Domain: Trading Analytics (Signals, History, Performance)
 *
 * Manages analytical trading data: signals, trade history, position monitoring, performance analysis.
 * Responsible for: trading signals, trading history, position monitoring, performance metrics.
 * Consumers: analytics views, strategy performance dashboards, trading signals display.
 *
 * For trade order operations and system health, see trading.ts.
 */
```
</action>

<acceptance_criteria>
- `web/frontend/src/stores/trading.ts` line 1 contains `Domain: Trading Operations`
- `web/frontend/src/stores/tradingData.ts` line 1 contains `Domain: Trading Analytics`
- Both files contain `see trading` referencing the other store
- Neither file's export signatures or logic changed
</acceptance_criteria>

## Verification

```bash
# Domain comments present
head -5 web/frontend/src/stores/market.ts | grep -q "Domain:"
head -5 web/frontend/src/stores/marketData.ts | grep -q "Domain:"
head -5 web/frontend/src/stores/trading.ts | grep -q "Domain:"
head -5 web/frontend/src/stores/tradingData.ts | grep -q "Domain:"

# Frontend still builds
cd web/frontend && npm run build

# Stylelint passes
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"
```
