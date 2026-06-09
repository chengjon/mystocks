# Shape Brief: `trade/Center.vue` ArtDeco Positions Review Desk

> Status: draft shape brief for approval.
> Target route: `/trade/positions`
> Target component: `web/frontend/src/views/trade/Center.vue`
> Implementation gate: no Vue, SCSS, router, API, or shared component changes until the user explicitly approves this brief.

## 1. Feature Summary

Reshape `/trade/positions` into a desktop-only ArtDeco positions review desk.

The page should help an A-share trade operator review the current holdings snapshot, identify exposure and unrealized PnL outliers, understand whether the data is trustworthy, and decide whether follow-up action is needed.

This is not a trade execution terminal and not a marketing-style portfolio page. It is a dense, operational review surface.

## 2. Confirmed Discovery Inputs

Confirmed route:

| Route | Route name | Component |
|---|---|---|
| `/trade/positions` | `trade-positions` | `web/frontend/src/views/trade/Center.vue` |

Current implementation signals:

- 596-line Vue page with local ArtDeco layout and custom positions table
- 22 `ArtDeco` references
- no raw hex or RGB values detected
- loading, empty, and error branches exist
- request/process/row metadata exists
- no `data-test` references detected
- one deterministic impeccable warning: `transition: width` at line 538
- user-facing copy includes internal English scaffolding and mobile-specific text

Related completed ArtDeco pilots:

- `market/Realtime.vue`: realtime market data desk
- `risk/Alerts.vue`: risk alert triage desk

This page should become the trade/positions counterpart to those pilots, while avoiding premature shared-component extraction.

## 3. Primary User Action

Primary action:

> Review current positions, isolate exposure/PnL exceptions, and refresh the snapshot when needed.

Secondary actions:

- switch between position review lenses
- retry after a failed load
- inspect whether data is live, stale, cached, partial, or degraded
- identify rows needing follow-up outside this page

Out of scope for this page:

- placing orders
- editing positions
- designing the trade terminal
- backend position model changes

## 4. Design Direction

Use the established ArtDeco fintech direction:

- obsidian surfaces
- measured gold structure
- tabular numeric rhythm
- restrained status color
- dense information without marketing composition
- Chinese operational product voice

Reference mental models:

- Bloomberg/terminal position monitor for density and status cadence
- IBKR-style portfolio positions for row-level financial scanning
- Linear-style triage controls for fast segmentation, not visual imitation

The design should feel like a mature internal financial workstation: calm, precise, and audit-friendly.

## 5. Scope

### In Scope After Approval

- Reframe header and page copy around positions review.
- Compress the hero/header so the table is visible early on desktop.
- Create a compact exposure summary strip.
- Add first-level review segments, such as `全部`, `盈利`, `亏损`, `高仓位`, and `需关注`.
- Convert request/process metadata into an operational runtime status strip.
- Improve the primary positions table scan path.
- Preserve loading, refreshing, empty, filtered-empty, error, stale, and degraded states.
- Replace width-based position bar animation with a compositing-friendly approach or remove the animation.
- Add stable `data-test` hooks for route-level gates.
- Keep style changes tokenized and local to touched selectors unless a proven shared abstraction is approved later.

### Out of Scope

- Backend API changes
- Router changes
- Global token migration
- Trade terminal redesign
- New order-entry interactions
- Shared component extraction
- Mobile or tablet redesign
- Broad redesign of all trade pages

## 6. Layout Strategy

### 6.1 Page Structure

Use a five-part desktop workbench:

1. Header/status band
2. Exposure summary strip
3. Review control row
4. Runtime status strip
5. Primary positions blotter

The table/blotter must remain the dominant work area.

### 6.2 Header/Status Band

Recommended title:

```text
持仓审阅工作台
```

Acceptable alternative:

```text
头寸管理工作台
```

Header content should answer:

- what this page is for
- whether the snapshot is current
- how many rows are visible
- whether the last refresh succeeded

Recommended metadata labels:

- `请求`
- `耗时`
- `行数`
- `已验证`
- `刷新中`
- `显示缓存快照`
- `同步异常`

Avoid:

- `position ledger desk`
- `position allocation route`
- decorative hero copy that delays the table
- mobile-specific instruction copy

### 6.3 Exposure Summary Strip

The summary strip should be compact and scannable.

Recommended fields:

| Field | Purpose |
|---|---|
| 总市值 | Scale of current exposure |
| 总盈亏 | Overall unrealized PnL condition |
| 盈利 / 亏损 | Quick distribution cue |
| 最高仓位 | Concentration warning |

The strip should not become four oversized cards. It should read as an instrument panel above the table.

### 6.4 Review Control Row

Recommended segments:

| Segment | Meaning |
|---|---|
| 全部 | Show all current positions |
| 盈利 | Positive PnL positions |
| 亏损 | Negative PnL positions |
| 高仓位 | Positions above the local concentration threshold |
| 需关注 | Composite attention bucket, initially derived from local row state |

The refresh action should live in the same operational zone, visually subordinate to the active review lens but easy to reach.

If `高仓位` and `需关注` thresholds are not API-provided, define local UI heuristics in code comments during craft and keep them conservative.

### 6.5 Runtime Status Strip

Runtime state must be a designed part of the page, not only metadata text.

Required states:

| State | UI meaning |
|---|---|
| Loading | No usable snapshot yet; show stable skeleton or loading state |
| Refreshing | Keep current snapshot visible and mark refresh in progress |
| Verified | Latest request succeeded and table reflects current response |
| Stale | Showing older snapshot because a refresh is overdue or failed |
| Degraded | Partial data or fallback path is visible |
| Empty | Request succeeded but there are no positions |
| Filtered empty | Positions exist, but current segment has no rows |
| Error | No trustworthy data available; retry action visible |

The status strip should use concise Chinese labels and clear severity contrast. It should not overuse gold for failure or warning states.

### 6.6 Primary Positions Blotter

Preserve the core columns:

- 股票
- 持股数
- 平均成本
- 当前价
- 市值
- 盈亏
- 盈亏%
- 仓位%

Craft expectations:

- tabular numerals
- fixed row rhythm
- clear positive/negative financial coloring
- exposure bar that does not animate layout properties
- high-weight rows easier to spot
- losing/high-attention rows visually legible without excessive decoration
- stable empty and error states inside the table area

The table should remain a review surface, not an order-entry grid.

## 7. Key States

### Default

The latest verified snapshot is visible. The `全部` segment is active. Summary strip and table agree on row counts and totals.

### Initial Loading

The page shows a stable layout with skeleton rows or a compact loading state. Avoid shifting the table area after data arrives.

### Refreshing With Existing Snapshot

Existing rows remain visible. The refresh control shows pending state, and the status strip communicates that a newer snapshot is being requested.

### Verified

A successful response sets the status to verified, updates request/process/row metadata, and refreshes summary metrics.

### Stale Snapshot

If the page is showing older data, the status strip must say so explicitly. Do not let stale data look identical to verified data.

### Degraded

Partial/fallback data should be visibly marked. The table may stay usable, but users must know confidence is reduced.

### Empty

If there are no positions, show an operational empty state with no marketing copy. The refresh action remains available.

### Filtered Empty

If a segment has no matching rows, keep the global summary visible and show a filtered-empty message in the table area.

### Error

If no trustworthy data can be displayed, show an error state with retry. If a previous snapshot is available, label it as cached/stale instead of replacing it with a blank page.

## 8. Interaction Model

Expected interactions after approval:

- Segment controls update the visible row set locally.
- Refresh triggers the existing fetch path.
- Retry reuses the refresh/fetch path.
- Runtime status updates from existing request state.
- Position rows remain non-editable unless existing behavior already supports drilldown.

Keyboard and accessibility expectations:

- segmented controls are keyboard reachable
- active segment is semantically exposed
- status changes are not communicated by color alone
- retry/refresh actions have clear labels

## 9. Content Requirements

Replace internal scaffolding with product copy:

| Current copy | Proposed direction |
|---|---|
| `position ledger desk` | `持仓审阅` |
| `position allocation route` | `仓位快照` or `仓位审阅` |
| `REQ_ID` | `请求` |
| `TIME` | `耗时` |
| `ROWS` | `行数` |
| `TOTAL_PNL` | `总盈亏` |
| `移动端可横向滚动查看更多列。` | remove, or replace with desktop table overflow language only if needed |

Preferred tone:

- concise
- operational
- Chinese-first
- no feature explanation prose inside the app
- no marketing claims

## 10. Implementation Guardrails

Implementation may start only after explicit approval with this wording or equivalent:

```text
批准实施 trade/Center.vue shape brief
```

When implementing:

- preserve route `/trade/positions`
- preserve the existing API contract unless separately approved
- do not modify `/trade/terminal`
- do not introduce a global shared component unless a clear local repetition is proven
- do not add mobile/tablet responsive work
- do not use hard-coded colors
- do not animate `width`, `height`, `margin`, or `padding`
- add `data-test` selectors for verification gates
- keep the table visible early at 1280x720
- report whether existing dirty changes were present before implementation

## 11. Verification Expectations After Approval

Expected minimum gates for the craft phase:

```text
git diff --check -- web/frontend/src/views/trade/Center.vue
npx eslint src/views/trade/Center.vue
node scripts/check-artdeco-tokens.js --target-file src/views/trade/Center.vue
npm run type-check -- --pretty false
```

Route/browser gate should include a focused Playwright check for `/trade/positions` or the existing phase matrix case that covers it. The report must name the actual browser project, pass/fail count, and any skipped cases.

If PM2 services are used for browser verification, final reporting must include:

- `mystocks-backend`: `http://localhost:8020`
- `mystocks-frontend`: `http://localhost:3020`

## 12. Proposed Craft Slice After Approval

Keep the first implementation slice intentionally narrow:

1. Header/status copy and layout compression
2. Exposure summary strip refinement
3. Segment controls and local row filtering
4. Runtime status strip
5. Table scan polish and position bar animation fix
6. Error/empty/filtered-empty copy cleanup
7. `data-test` hooks
8. Focused verification

Do not extract shared components in this slice. Re-evaluate extraction after comparing the implemented Realtime, Risk Alerts, and Positions patterns.

## 13. Open Questions

1. Which title should be canonical: `持仓审阅工作台` or `头寸管理工作台`?
2. Should `高仓位` use a fixed threshold, top-N ranking, or backend-provided metadata?
3. Should `需关注` be derived locally from PnL/exposure or wait for backend risk flags?
4. Should request metadata remain terminal-abbreviated or become fully Chinese?
5. Should row-level drilldown be introduced later, and if so, which route owns it?

## 14. Approval Boundary

This document is a design brief only. It does not approve implementation.

Implementation should begin only after the user approves this shape brief.
