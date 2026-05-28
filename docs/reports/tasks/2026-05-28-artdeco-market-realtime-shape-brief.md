# Shape Brief: `market/Realtime.vue` ArtDeco Pilot

Date: 2026-05-28

OpenSpec change: `add-artdeco-impeccable-design-gate`

Target: `web/frontend/src/views/market/Realtime.vue`

Status: draft for approval. This brief does not authorize implementation until approved.

## 1. Purpose and Context

`market/Realtime.vue` should become the first ArtDeco Web route pilot because it tests the design system where it matters most: live market density, data freshness, user controls, A-share color semantics, and runtime state confidence.

The user is likely focused, time-sensitive, and comparing market state during live sessions or review windows. The page should feel like a reliable market instrument, not a branded showcase.

## 2. Design Direction

Direction: compact ArtDeco market workbench.

The page should keep the ArtDeco identity through frames, typography, dark surfaces, tabular rhythm, and restrained gold detail. It should reduce hero-like theater and give priority to freshness, filters, table data, and distribution state.

Image generation probe: skipped. This is not a net-new visual direction; the project already has ArtDeco product context, implemented tokens, and a concrete page target. Static source review is sufficient for this approval brief.

## 3. Scope

Approved implementation should be limited to:

- page header band
- control row
- primary quote table work area
- distribution or breadth panel
- stale, loading, error, cache, empty, and degraded state treatment
- touched-scope token cleanup

Out of scope:

- backend API contract changes
- route restructuring
- mobile redesign
- new charting library
- broad token migration
- global component extraction from this page alone
- rewriting historical ArtDeco documents

## 4. Layout Strategy

### Header Band

Replace the hero feel with a compact route header:

- title: `实时行情`
- subtitle: short operational line about current sample, market freshness, and quote coverage
- status chip: live, refreshing, cache, stale, degraded, error, or empty
- one primary refresh action
- optional request id as low-priority diagnostic text

Remove or demote decorative English labels such as `live quote observatory` and `sample quote route`.

### Control Row

Use one predictable control row:

- sample preset select
- refresh action
- freshness label
- sample count
- last verified snapshot indicator

Avoid duplicate refresh controls. If the header has refresh, the row should focus on filters and metadata.

### Primary Work Area

Use a data-first two-column work area at desktop width:

- left: quote table, largest surface
- right: breadth distribution, freshness and state context

Avoid placing a toolbar card inside a larger content card. Use bands or unframed containers with clear dividers.

### Secondary Context

Keep stats close to the data, but do not overuse gold stat cards. Gold should mark the ArtDeco frame or primary accent, not every metric.

Recommended stat grouping:

- total turnover
- market mood
- up/flat/down counts
- sample size

## 5. Key States

| State | User Need | Design Treatment |
|---|---|---|
| Default live | Trust the page is current and actionable | Status chip `实时`, freshness timestamp, table and distribution visible |
| Initial loading | Know the page is fetching first data | Skeleton or stable placeholders, not layout collapse |
| Refreshing | Keep reading current snapshot while update runs | Subtle refresh state in status strip and disabled refresh button |
| Cache | Understand data is usable but cached | Cache banner with source and last verified request id |
| Stale | Know data age is outside acceptable freshness | Stale banner or status strip with age and retry action |
| Degraded | Know partial data is present | Degraded status with what is missing and what remains reliable |
| Empty | Know no symbols are available for selected sample | Empty state with sample switch or retry direction |
| Error | Recover quickly | Error banner with concise cause and retry |

## 6. Interaction Model

- Preset selection triggers refresh for the selected sample.
- Refresh is the primary action and appears once.
- Retry uses the same fetch path as refresh but appears only in error state.
- Cache and stale states should not block table reading if a verified snapshot exists.
- Table remains read-first. Do not add row-level actions in the pilot unless approved separately.

## 7. Copy and Microcopy

Use Chinese operational copy. Avoid English decorative labels on task surfaces.

Candidate copy:

- Page title: `实时行情`
- Subtitle: `跟踪当前样本报价、成交额与涨跌分布。`
- Freshness label: `最新快照`
- Cache label: `缓存快照`
- Stale label: `快照可能已过期`
- Empty label: `当前样本暂无可展示行情`
- Error label: `行情同步失败`
- Retry action: `重试`

## 8. Token and Component Rules

- Prefer existing ArtDeco primitives before creating new components.
- Keep `ArtDecoHeader`, `ArtDecoButton`, `ArtDecoSelect`, `ArtDecoTable`, and `ArtDecoStatCard` if they remain fit for purpose.
- Use `artdeco-tokens.scss` as the token truth.
- Classify touched token usage as canonical, alias-backed, or compatibility bridge before cleanup.
- Do not broadly rewrite `--artdeco-*` to `--ad-*` in this pilot unless the token relationship is verified.
- Preserve A-share semantics: red/up/positive, green/down/negative.

## 9. Candidate Reusable Patterns

Do not extract these during the first page unless separately approved:

- `ArtDecoPageHeader`
- `ArtDecoControlBar`
- `ArtDecoStatusStrip`
- `ArtDecoDataPanel`
- route-level freshness state pattern

Treat this pilot as evidence gathering for extraction. Extraction should wait for `trade`, `risk`, or `system` routes to prove the same pattern.

## 10. Verification Plan After Approval

After implementation, report:

- changed files
- structural syntax error status
- ArtDeco lint or targeted token check
- type-check result with baseline comparison
- actual E2E or smoke command, browser project, pass/fail/skip counts
- PM2 service status if service startup, build, type check, or E2E is involved
- screenshot or visual inspection notes if a browser run is performed

## 11. Approval Question

Approve this shape brief for implementation only if the desired first slice is:

- compact header band
- single control row
- table-first primary work area
- explicit freshness/cache/stale/error states
- touched-scope token cleanup

Implementation must not begin until this brief and scope are explicitly approved.
