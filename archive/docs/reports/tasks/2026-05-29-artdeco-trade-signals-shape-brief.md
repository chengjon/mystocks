# Shape Brief: `trade/Signals.vue` ArtDeco Signal Trust Desk

> Date: 2026-05-29
> Command intent: `$impeccable shape trade signals ArtDeco signal trust desk`
> Target route: `/trade/signals`
> Target component: `web/frontend/src/views/trade/Signals.vue`
> Implementation gate: this brief is awaiting explicit user approval. No Vue, SCSS, router, API, test, or shared component changes are allowed until approval.

## 1. Feature Summary

`trade/Signals.vue` should become a signal trust desk: a dense operational route for reviewing live trading signals, understanding data freshness, and deciding whether a signal is actionable.

The page should not become a general strategy dashboard, marketing hero, or component-extraction exercise. It should keep the live signal list as the primary surface and make trust state visible before the user acts.

## 2. Confirmed Discovery Inputs

This brief is based on already available discovery inputs, so no additional interview round is needed before drafting:

- critique report: `docs/reports/tasks/2026-05-29-artdeco-trade-signals-critique.md`
- extraction analysis: `docs/reports/tasks/2026-05-29-artdeco-page-pilot-extraction-analysis.md`
- prior page pilots: Realtime, Risk Alerts, and Trade Positions
- current user boundary: no route changes, no API contract changes, no shared component extraction
- current project boundary: desktop Web only, minimum 1280x720, no mobile/tablet adaptation rules

Current implementation facts:

| Item | Value |
|---|---|
| Route | `/trade/signals` |
| Route name | `trade-signals` |
| Source file | `web/frontend/src/views/trade/Signals.vue` |
| Current file state | already dirty before critique / shape; do not revert unrelated changes |
| Lines | 711 |
| `data-test` hooks | 0 |
| `@media` rules | 2 |
| Deterministic impeccable scan | `[]` |
| ArtDeco token check | passed |

Visual direction probe skipped: this is not a net-new visual system or ambiguous brand direction. The route should reuse the proven ArtDeco operational-page grammar from the Realtime, Risk Alerts, and Trade Positions pilots.

## 3. Primary User Action

The target user should be able to answer, in order:

1. Is the signal data live, pending, stale, degraded, empty, or unavailable?
2. Which signals require review now?
3. Which signals are actionable versus observational?
4. Which rows have verified confidence and strategy provenance?
5. Can I safely refresh without losing the last verified snapshot?

Primary action: review the live signal list and decide whether a buy/sell/hold signal deserves execution attention.

Secondary actions:

- filter signals by review lens
- refresh data
- inspect signal quality caveats
- confirm strategy source and request provenance
- export or execute only when the row is ready

## 4. Design Direction

The page should follow the operational route grammar now proven across the ArtDeco pilots:

```text
compact route header -> signal review lens -> signal trust strip -> primary signal list -> secondary evidence panels
```

Design posture:

- dense, workbench-like, and financial
- restrained ArtDeco chrome
- clear trust semantics over decorative status
- Chinese operational copy for user-facing labels
- technical metadata only where useful for operators
- no mobile-first or marketing-like layout

The page should feel closer to a trading desk signal blotter than a generic dashboard.

## 5. Scope

### In Scope After Approval

If this brief is approved, the smallest useful craft slice should stay local to `trade/Signals.vue` and its route tests:

- reshape the route header/status band so the primary signal list appears earlier
- add a signal trust strip for verified, syncing, stale, degraded, empty, and unavailable states
- introduce a first-level review lens: `全部`, `买入`, `卖出`, `观望`, `高置信度`
- keep the current `/api/v1/trade/signals` data contract unchanged
- keep `ArtDecoTradingSignals` rendering intact unless explicitly approved otherwise
- demote placeholder quality/history panels beneath the live signal list
- add route-local `data-test` hooks for stable E2E verification
- remove or neutralize desktop-incompatible `@media` rules only inside the approved local page layout scope

### Out Of Scope

- router changes
- API contract changes
- backend changes
- new shared ArtDeco components
- extracting `ArtDecoTradingSignals`
- extracting `ArtDecoTradingSignalsControls`
- changing `views/artdeco-pages/**` ownership
- broad token migration
- mobile/tablet responsive behavior
- visual redesign of unrelated trade routes

## 6. Layout Strategy

### 6.1 Route Header

The current hero/status shell should be compressed into a route header band.

The header should contain:

- page title: `交易信号工作台`
- concise subtitle focused on live signal review and execution readiness
- data status summary
- last verified request ID
- last verified process time
- refresh action

Avoid making the header compete with the signal list. The first viewport should reveal the start of the primary data surface on desktop.

### 6.2 Signal Review Lens

The first-level control row should be immediately scannable:

| Lens | Purpose |
|---|---|
| `全部` | show all verified rows |
| `买入` | isolate buy candidates |
| `卖出` | isolate sell candidates |
| `观望` | show hold / watch rows |
| `高置信度` | show rows with verified confidence above the approved threshold |

The lens should not invent new API semantics. It should filter already available rows only.

### 6.3 Signal Trust Strip

The trust strip is the most important new page grammar.

It should state:

- data source state: pending, verified, empty, unavailable
- refresh state: idle, syncing, stale snapshot, degraded refresh
- visible count
- current lens
- request ID / process time when verified
- recovery action when first-load fails

The strip should be visually separate from warnings. A stale-but-usable snapshot is not the same as first-load unavailable data.

### 6.4 Primary Signal List

The signal list should remain dominant.

Keep:

- current ArtDeco signal row visual language
- buy / sell / hold semantics
- strategy source copy
- confidence labels
- execution readiness behavior

Improve later only if approved:

- row-level readiness indicators
- row-level stale snapshot marker
- route-local `data-test` hooks
- filtered-empty state for lens results

### 6.5 Secondary Evidence Panels

Quality analysis, type distribution, and history tracking should not compete with the live list.

Rules:

- verified execution history can stay visible when real data exists
- placeholder quality rows should be visibly secondary
- unverified quality / win-rate statistics must not look equivalent to real signal data
- if evidence is unavailable, state that explicitly and keep the panel compact

## 7. Key States

| State | User Experience |
|---|---|
| First load pending | Header and trust strip show syncing; summary numbers remain placeholders; signal list shows honest loading state |
| Verified data | Trust strip shows verified state, request ID, process time, visible count, and current lens |
| Empty verified payload | Trust strip shows empty state; primary list shows no signals without treating it as failure |
| First-load failure | Trust strip shows unavailable state with retry; no fake rows or fake metrics appear |
| Refreshing with prior data | Existing rows remain visible; trust strip says syncing |
| Refresh failure after prior data | Prior verified rows stay visible; trust strip shows stale/degraded state and the failed refresh reason |
| High-confidence lens without verified confidence | Lens should explain that confidence is unverified instead of showing misleading zeroes |
| Filtered empty | Show a compact route-local empty state for the selected lens |

## 8. Copy And Microcopy

Move user-facing route labels toward Chinese operational copy:

| Current Direction | Shape Direction |
|---|---|
| `signal execution desk` | `信号执行台` or remove if redundant |
| `signal review route` | `信号复核` |
| `DATA` | `数据状态` |
| `REQ_ID` | `请求编号` |
| `FILTER` | `筛选` |
| `交易信号同步中...` | keep, or align with trust strip copy |
| stale refresh text | keep explicit: `当前仍显示上次成功同步的交易信号快照` |

Microcopy should separate:

- unavailable first load
- stale but usable snapshot
- unverified confidence
- unavailable execution history
- filtered-empty results

## 9. Component And Ownership Boundary

The current route depends on ArtDeco workbench internals:

```text
@/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue
@/views/artdeco-pages/components/ArtDecoTradingSignalsControls.vue
```

For the approved craft slice, keep these dependencies as existing implementation reality.

Do not extract or move them in this page pass.

If a later extraction proposal is desired, it must be a separate task that proves:

- at least four routed pages share the same pattern
- the candidate component does not own API orchestration
- the candidate component does not change route metadata
- the candidate component does not alter API contracts
- the candidate has route-level E2E coverage

## 10. Verification Expectations For Future Craft

If implementation is later approved, minimum verification should include:

- `npx eslint src/views/trade/Signals.vue`
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Signals.vue`
- `npm run type-check -- --pretty false`
- targeted Chromium E2E for existing `Trade-Signals` cases in `phase3-mainline-matrix.spec.ts`
- `npx impeccable --json src/views/trade/Signals.vue`
- PM2 status if frontend services are started or affected

Route-local E2E hooks should cover:

- page root
- route header
- review lens
- signal trust strip
- primary signal list
- signal rows
- filtered-empty state
- first-load error state
- stale refresh state
- refresh action

## 11. Approval Checklist

Before craft, the user should explicitly approve:

- the signal trust desk direction
- local-only implementation scope
- no router changes
- no API contract changes
- no shared component extraction
- whether desktop-incompatible `@media` rules are in scope for cleanup
- whether `ArtDecoTradingSignals` and `ArtDecoTradingSignalsControls` must remain untouched

## 12. Brief Status

Status: awaiting approval.

This brief is complete as a design document, but implementation must not begin until the user explicitly approves it.
