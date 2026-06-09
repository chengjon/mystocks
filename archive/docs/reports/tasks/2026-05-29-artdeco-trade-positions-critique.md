# ArtDeco Critique: `trade/Center.vue`

> Scope: documentation-only critique for the routed trade positions page.
> Target route: `/trade/positions`
> Target component: `web/frontend/src/views/trade/Center.vue`
> Source state: current working tree on 2026-05-29. The target Vue file was already dirty before this critique; this task does not modify it.

## 1. Scope and Method

This critique applies the impeccable workflow to the already implemented Web ArtDeco page at `web/frontend/src/views/trade/Center.vue`.

The purpose is to decide whether the page is ready for an approved shape/craft pass, not to change code in this step. It reviews:

- page job clarity and information hierarchy
- ArtDeco fintech alignment
- runtime state visibility
- table and control ergonomics
- component reuse opportunities
- visual token and motion risk
- verification gate readiness

The page was assessed through:

- static component scan of the current Vue file
- router truth check against `web/frontend/src/router/index.ts`
- deterministic impeccable scan through `npx impeccable --json src/views/trade/Center.vue`
- alignment against current `PRODUCT.md`, `DESIGN.md`, ArtDeco documentation, and the Realtime/Risk pilot decisions

No screenshot, browser overlay, or Playwright run was executed for this critique because this is a design-planning step. Browser verification belongs in the approved craft phase.

## 2. Route and Ownership

The canonical route is confirmed in `web/frontend/src/router/index.ts`:

| Route | Route name | Component | Notes |
|---|---|---|---|
| `/trade/positions` | `trade-positions` | `@/views/trade/Center.vue` | Active trade positions surface |

Important route distinction:

- `/trade/positions` is the positions management route reviewed here.
- `/trade/terminal` is a separate terminal-style trading dashboard and is out of scope.

## 3. Current Implementation Signals

Current static scan:

| Metric | Value | Interpretation |
|---|---:|---|
| Lines | 596 | Medium-size page, large enough to hide repeated layout/state patterns |
| `ArtDeco` references | 22 | Uses the project ArtDeco component vocabulary |
| `data-test` references | 0 | Weak verification hook surface for a critical trade route |
| `aria-*` references | 3 | Some accessibility consideration exists, but not systematic |
| `title=` attributes | 2 | Native tooltips may need replacement if controls become more complex |
| Loading references | 8 | Runtime loading exists in code |
| Error references | 20 | Error handling exists and is visible in implementation |
| Empty references | 5 | Empty state exists |
| Raw hex colors | 0 | Good token discipline in this file |
| `rgb()` / `rgba()` | 0 | Good token discipline in this file |
| `@media` references | 2 | Needs review against the desktop-only product constraint |
| Element Plus table/button/card refs | 0 | Page relies on custom ArtDeco composition rather than stock Element Plus table/card grammar |

Notable visible copy:

- `position ledger desk`
- `position allocation route`
- `REQ_ID`, `TIME`, `ROWS`, `TOTAL_PNL`
- `移动端可横向滚动查看更多列。`

The page is already closer to ArtDeco than many legacy screens: it uses tokens, custom table layout, request/process metadata, and explicit data states. The main gap is not "make it more decorative"; the page needs stronger trade-workflow intent and a clearer operational structure.

## 4. Design Health Score

Overall score: **24 / 40**

| Area | Score | Notes |
|---|---:|---|
| Route truth and product fit | 3 / 4 | Canonical routed page; domain is relevant to trade review |
| Primary job clarity | 2 / 4 | It reads as holdings display, allocation panel, and ledger at once |
| Information hierarchy | 2 / 4 | Summary metrics, hero, and table compete for first attention |
| Runtime state design | 3 / 4 | Request/process/error/empty signals exist but are not yet a decisive status model |
| Table ergonomics | 3 / 4 | Columns are appropriate; scan affordances and controls are thin |
| ArtDeco visual alignment | 3 / 4 | Tokenized, restrained, and on-brand; some decorative density needs pruning |
| Token discipline | 4 / 4 | No raw colors detected in current scan |
| Motion/performance | 2 / 4 | Width transition warning on position fill should be corrected in craft |
| Verification readiness | 1 / 4 | No `data-test` hooks for route-level gates |
| Copy and localization | 1 / 4 | Internal English scaffolding and mobile copy conflict with product voice |

## 5. Anti-Patterns Verdict

### LLM Assessment

The page is structurally useful but still reads like an ArtDeco-styled report page, not yet like a mature positions review desk. A trade operator should immediately know:

- whether the snapshot is current
- what exposure or PnL needs attention
- which rows are exceptions
- what the next safe action is
- whether the visible data is live, stale, cached, partial, or failed

The current page exposes some of that information, but the design does not force it into the first scan path.

### Deterministic Scan

`npx impeccable --json src/views/trade/Center.vue` returned one finding:

| Severity | Anti-pattern | Location | Finding |
|---|---|---:|---|
| Warning | `layout-transition` | `web/frontend/src/views/trade/Center.vue:538` | `transition: width` on the position fill bar |

Craft implication: if the position bar remains animated, use `transform: scaleX(...)`, opacity, or another compositing-friendly method instead of animating width.

### Visual Overlays

Visual overlay inspection was not run in this documentation-only critique. It should be run during the approved craft phase, at minimum for a 1440px desktop viewport, and preferably with the current PM2 frontend if available.

## 6. What's Working

- The route is already canonical: `/trade/positions` maps to `web/frontend/src/views/trade/Center.vue`.
- The component uses project ArtDeco components rather than falling back to generic Element Plus cards.
- Color use appears tokenized; no raw hex or RGB values were detected.
- The table columns match the position-review domain: stock, shares, average cost, current price, market value, PnL, PnL percent, and weight.
- Request/process metadata exists, which supports the ArtDeco runtime-state standard.
- Loading, error, and empty paths are already present in implementation.
- The position bar provides a useful exposure cue if performance and visual priority are corrected.
- The page has enough local structure to become a reusable trade/risk table pattern after one more approved craft pass.

## 7. Priority Issues

### [P1] The page's primary job is still ambiguous

The route title says positions management, but the page copy and layout mix several jobs:

- `position ledger desk`
- `position allocation route`
- `持仓结构与仓位面板`
- summary metrics
- full positions table

For this product, `/trade/positions` should be framed as a **持仓审阅工作台**: review current holdings, identify exposure/PnL exceptions, and decide whether follow-up action is needed. It should not behave like a marketing hero, a generic report, or the trade terminal.

Craft direction: make the primary job "positions review and exposure triage" explicit in the header, control row, status strip, and table emphasis.

### [P1] Runtime metadata exists but is not yet operational

`REQ_ID`, `TIME`, `ROWS`, and total PnL appear in the UI, but they do not yet form a user-facing state model. Operators need a status band that answers:

- Is this snapshot verified?
- Is it currently refreshing?
- Is the page showing cached data?
- Did the last refresh fail?
- Is the result partial or degraded?
- How many rows are visible after filters?

Craft direction: turn metadata into a compact runtime status strip with stable labels and state-specific styling.

### [P1] The table lacks first-level triage controls

The positions table has the right columns, but the page currently under-serves high-speed review. A trade operator should be able to isolate:

- all positions
- profitable positions
- losing positions
- high-weight positions
- positions needing attention

Craft direction: add a compact control row or segmented filter model. This should be page-local at first, not extracted globally until Realtime, Risk Alerts, and Positions prove a common pattern.

### [P2] The header/stat treatment can push the primary table down

The current ArtDeco hero/stat composition risks repeating the pre-fix Risk Alerts problem: prominent decorative or summary areas can delay the user's arrival at the actual work surface.

Craft direction: keep the header and summary strip compact. The primary table should be visible early at 1280x720 and should not feel secondary to ornament or copy.

### [P2] English scaffolding weakens the product tone

Internal English labels are visible in a Chinese operational product:

- `position ledger desk`
- `position allocation route`
- `REQ_ID`
- `TIME`
- `ROWS`
- `TOTAL_PNL`

Some metadata abbreviations may be acceptable in terminal-style surfaces, but this page is not the execution terminal. The copy should use calm operational Chinese unless there is a specific reason to preserve terminal abbreviations.

Craft direction: prefer labels such as `持仓审阅`, `仓位快照`, `请求`, `耗时`, `行数`, `总盈亏`, `已验证`, `刷新中`, `显示缓存快照`.

### [P2] Desktop-only standard conflicts with mobile copy

The page includes `移动端可横向滚动查看更多列。` while the current product/design context is desktop-only with minimum 1280x720.

Craft direction: remove mobile-facing copy. If the table needs overflow behavior on constrained desktop widths, state it as a desktop table affordance or rely on visual affordance without instructional text.

### [P2] Verification hooks are absent

There are no `data-test` hooks in a critical trade route. This limits reliable Playwright and route-matrix validation after craft.

Craft direction: add stable hooks for page root, refresh action, runtime status, filter segments, table rows, error state, empty state, and retry action.

### [P2] Position bar animation can cause layout work

The deterministic scan found `transition: width`. Width animation is a known layout-transition anti-pattern.

Craft direction: use `transform: scaleX(...)` with fixed transform origin, or remove the animation if the value changes often during refresh.

### [P3] ArtDeco ornament should stay subordinate to risk and exposure

Corner markers, bars, dividers, and gold accents are acceptable in this system, but on a trade surface they must not compete with PnL color, exposure weight, stale state, or error state.

Craft direction: reserve gold geometry for structure and hierarchy. Let financial state colors and table contrast carry decisions.

## 8. Cognitive Load Assessment

The page has the right raw material, but it asks the user to assemble the workflow mentally:

- The user sees position metrics but must infer which metric controls the page's decision.
- The user sees runtime metadata but must infer whether the data can be trusted.
- The user sees a positions table but cannot quickly segment by operational concern.
- The user sees English scaffolding and mobile copy that interrupt the product voice.

The craft pass should reduce cognitive load by creating a single scan order:

1. Header tells the page job and data freshness.
2. Exposure strip shows the current portfolio condition.
3. Control row selects the review lens.
4. Status strip tells whether the result is live, stale, degraded, or failed.
5. Table presents the position rows with consistent numeric rhythm.

## 9. Persona Red Flags

### Alex, Power User

Alex needs speed and precision. The current page has the data but not enough control affordance. Lack of segment filters and stable keyboard/test hooks makes it feel more like a display page than an operator's workbench.

### Sam, Accessibility-Dependent User

Sam benefits from semantic status and stable labels. Current metadata abbreviations and sparse `aria-*` coverage make state interpretation harder than necessary.

### Project-Specific Persona: A-share Trade Operator

The trade operator needs to identify exposure concentration, large unrealized losses, stale data, and refresh failures before acting. The current page does not yet prioritize these questions strongly enough.

## 10. Minor Observations

- The page should avoid becoming a second trade terminal; `/trade/terminal` already owns that job.
- If position rows eventually support drilldown or handoff, that interaction should be explicit and testable.
- The custom table can remain if it preserves fixed row rhythm and tabular numerals.
- A future shared `ArtDecoDataPanel` or `ArtDecoStatusStrip` may be justified, but extraction should wait until at least this third route proves the repeated pattern.

## 11. Questions To Resolve Before Craft

1. Should the page title be `头寸管理工作台` or `持仓审阅工作台`?
2. Which threshold defines `高仓位` in the UI: fixed percentage, top-N weights, or API-provided flag?
3. Does `需关注` mean losing position, high weight, stale price, or a composite of several local signals?
4. Should the page keep terminal-style abbreviations for request metadata, or convert them fully to Chinese labels?
5. Is there an existing route for position drilldown or terminal handoff, or should this craft pass avoid adding that interaction?

## 12. Recommended Actions

Recommended next command:

```text
$impeccable shape trade positions ArtDeco positions review desk
```

Recommended approved craft scope after the shape brief:

- reframe the page as a positions review desk
- compact the header/status band
- add position triage segments
- strengthen runtime status states
- preserve the existing API contract
- preserve the existing route
- clean user-facing copy
- replace `transition: width`
- add route-level `data-test` hooks

Do not implement source changes until the shape brief is explicitly approved.
