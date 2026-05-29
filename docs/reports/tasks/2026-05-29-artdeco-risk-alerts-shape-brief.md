# Shape Brief: `risk/Alerts.vue` ArtDeco Triage Desk

Date: 2026-05-29

Status: awaiting explicit implementation approval

Target route: `/risk/alerts`

Target file for future implementation: `web/frontend/src/views/risk/Alerts.vue`

Supporting file likely affected after approval: `web/frontend/src/views/risk/AlertRuleManagementPanel.vue`

Related critique: `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md`

## 1. Feature Summary

`risk/Alerts.vue` should become an ArtDeco risk-alert triage desk for desktop Web users monitoring A-share risk signals. The page must help an operator quickly answer what needs attention now, whether the alert data is live or degraded, and how rules relate to the current alert stream.

The redesign direction is not a broad restyle. It is a focused page grammar improvement based on the completed `market/Realtime.vue` pilot: compact operational header, explicit runtime state, primary data area, secondary context, and tokenized touched styles.

## 2. Confirmed Discovery Inputs

The following direction is treated as confirmed for this shape brief:

- Primary priority: alert triage first.
- First-level controls: unread and high-priority alerts.
- Rule management: secondary configuration area, not the primary page job.
- Implementation gate: no Vue, SCSS, route, API, or shared component changes until the user explicitly approves this shape brief.

Visual direction probes were skipped because this is not a net-new surface or ambiguous visual identity problem. The ArtDeco product direction, route grammar, and Realtime pilot already constrain the design lane.

## 3. Primary User Action

The user should be able to identify and act on the most urgent risk alerts within one scan:

1. Confirm data freshness and route health.
2. Filter to unread or high-priority alerts.
3. Inspect the alert table in severity-first order.
4. Move to rule configuration only when they intentionally switch from review to setup.

Everything else on the page should support that sequence.

## 4. Design Direction

Color strategy: Restrained.

The page should use tinted dark ArtDeco surfaces, muted gold for structure, and semantic risk color only where it communicates severity, freshness, or action priority. Decorative gold should not compete with warning, error, stale, or high-priority alert states.

Theme scene sentence:

An experienced risk operator reviews A-share alert activity on a 27-inch desktop monitor during live market hours, with a dim trading-room environment, focused attention, and low tolerance for ambiguity.

Anchor references:

- Bloomberg Terminal for dense operational seriousness and tabular confidence.
- Linear issue triage for clear state filtering and fast queue review.
- Grafana alerting for explicit health, severity, and stale/degraded-state language.

Per-surface overrides:

- Keep the existing ArtDeco fintech identity.
- Do not introduce a new palette.
- Do not introduce campaign-like hero treatment.
- Do not use gradient text, glassmorphism, side-stripe accents, decorative animation, or identical card-grid expansion.

## 5. Scope

Fidelity: production-ready brief for a future code implementation.

Breadth: one routed page plus its embedded rule-management panel boundary.

Interactivity: shipped-quality route behavior after approval, not a throwaway prototype.

Time intent: create a second high-quality pilot after `market/Realtime.vue`, then decide whether shared extraction is justified.

In scope for future implementation after approval:

- Route-level header/status band.
- Alert triage control row.
- Primary alert table hierarchy.
- Runtime state strip.
- Rule-management secondary placement.
- Tokenized touched visual styles.
- Existing API and route contract preservation.

Out of scope:

- Backend API changes.
- Router changes.
- Global ArtDeco token migration.
- Full risk-domain redesign.
- Shared primitive extraction without a second-consumer decision.
- Mobile-first redesign.

## 6. Layout Strategy

### 6.1 Page Structure

The page should use a five-part workbench structure:

1. Header/status band.
2. Triage control row.
3. Runtime status strip.
4. Primary alert table.
5. Secondary rule-management area.

### 6.2 Header/Status Band

The header should be compact and operational:

- Title: `风险告警工作台` or an equivalent concise route title.
- Subtitle: one sentence explaining alert triage, not rule configuration.
- Metadata: request ID, last verified time or snapshot state, visible unread/high-priority counts.
- Primary action: refresh.

Avoid the current double-shell feeling where `hero-shell`, stat strip, and content shell all compete for first attention.

### 6.3 Triage Control Row

The control row should be the primary interaction surface:

- Severity segment: all, high-priority, warning, normal.
- Unread toggle: all vs unread.
- Optional quick filter: symbol/type search if already supported by existing data without API change.
- Refresh action.
- Secondary entry: rule management.

The row should be visually compact and familiar. Use segmented controls, toggles, and standard button affordances rather than invented controls.

### 6.4 Runtime Status Strip

Introduce a route-level state strip below controls or between header and controls:

- Live/verified state.
- Refreshing state.
- Partial sync state.
- Stale snapshot state.
- Degraded state.
- Empty state.
- Error state with retry path.

The strip should make data trust visible before the user reads the table.

### 6.5 Primary Alert Table

The alert table should own the largest surface:

- Sort or group high-priority and unread alerts first.
- Keep fixed-width columns for code, name, type, severity, and time.
- Let alert content use the most flexible width.
- Preserve `show-overflow-tooltip` if no better detail pattern is implemented, but prefer an approved inline detail row or expanded text pattern if shape later permits.
- Keep severity labels as text plus color, not color alone.

### 6.6 Secondary Rule Management

Rule management should remain available but visually secondary:

- Default: collapsed section, secondary panel, or configuration mode below the alert table.
- The user should not confuse creating/editing rules with reviewing live alerts.
- Mutation feedback should remain visible when rules are edited.
- Destructive rule actions should use a consistent ArtDeco action vocabulary after approval.

## 7. Key States

### Default

The user sees a compact header, triage controls, verified state, and the alert table sorted toward urgent items.

User feeling: oriented, in control, and able to act.

### Initial Loading

The structure remains stable. Header and controls stay visible. Table content shows a loading treatment or skeleton; counts show placeholder values only if no verified snapshot exists.

User feeling: the desk is preparing data, not broken.

### Refreshing With Existing Snapshot

The table remains visible. Status strip says refreshing and references last verified data.

User feeling: current screen remains usable while data updates.

### Live/Verified

The status strip confirms the alert and rule snapshots are verified. Counts, table, and rule summary agree.

User feeling: data can be trusted.

### Partial Sync

If rules or alerts fail independently, the status strip names the failed slice. The usable slice remains visible.

User feeling: knows exactly what is stale and what is still trustworthy.

### Stale Snapshot

The page should say it is showing the last successful snapshot, not imply live data. Retry remains visible.

User feeling: cautious but not blocked.

### Degraded

Use when data is available but incomplete, delayed, or only partially refreshed. Degraded should be semantically distinct from empty.

User feeling: operationally warned.

### Empty

If no alerts exist after a verified snapshot, the empty state should say the alert queue is clear and direct the user to rule status if needed.

User feeling: no action required, not uncertain.

### Error

If there is no verified data, the error state should clearly say what failed and provide retry.

User feeling: knows the recovery path.

### Rule Mutation Success/Error

Rule create, update, and delete feedback should stay near the rule-management area while not interrupting alert triage.

User feeling: setup action completed or needs correction.

## 8. Interaction Model

Entry flow:

1. Page opens on the alert review mode.
2. Header and status strip establish data trust.
3. User toggles unread/high-priority or severity segment.
4. Table updates without shifting the page frame.
5. User inspects alert details.
6. User enters rule management only when needed.

Control behavior:

- Refresh gives loading feedback but does not hide existing alert data.
- Severity filter changes the table and count context.
- Unread toggle narrows the table and should preserve the current severity selection.
- Rule-management entry reveals or focuses the secondary configuration area.
- Rule modal/drawer/section must have cancel and close paths.

Keyboard/accessibility expectations:

- Refresh and filters are reachable by keyboard.
- Current filter state is announced visually and programmatically.
- Runtime status changes keep `aria-live` behavior.
- Severity is expressed through text labels in addition to color.
- Destructive rule action labels must be explicit.

## 9. Content Requirements

Recommended user-facing vocabulary:

- Use Chinese operational labels for primary UI.
- Keep request IDs and technical metadata only where useful.
- Replace internal scaffolding such as `alert governance desk`, `FOCUS: alert center`, and `alert review route`.

Suggested labels:

- Header: `风险告警工作台`
- Primary mode: `告警审阅`
- Secondary mode: `规则配置`
- Severity filter: `全部`, `高优先级`, `预警`, `普通`
- Unread toggle: `仅未读`
- Runtime states: `已验证`, `刷新中`, `部分同步`, `显示缓存快照`, `数据降级`, `同步异常`
- Empty state: `当前无告警记录，风险告警队列为空。`
- Stale state: `当前显示上次成功同步的告警快照。`
- Error state: `告警记录暂不可用，请重试同步。`

Dynamic ranges:

- Alert count: 0 to at least 50 currently fetched rows.
- Rule count: 0 to many rules.
- Alert message: potentially long text, must not break table layout.
- Symbols and stock names: short but should remain aligned.

## 10. Implementation Guardrails

Future implementation should preserve:

- `/risk/alerts` route.
- Existing monitoring API calls unless a separate API proposal is approved.
- Existing `AlertRecordResponse` and `AlertRuleResponse` data contracts.
- Existing rule mutation behavior.
- Existing E2E-compatible data-test attributes in `AlertRuleManagementPanel.vue`.

Future implementation should avoid:

- New global tokens.
- New shared components before extraction is approved.
- Rewriting the full risk domain.
- Removing rule management entirely.
- Treating mobile breakpoints as the target design constraint.
- Making color the only severity signal.

## 11. Recommended References For Craft

When implementation is approved, load:

- `impeccable/reference/craft.md`
- `impeccable/reference/audit.md`
- `impeccable/reference/polish.md`
- `impeccable/reference/layout.md`
- `impeccable/reference/harden.md`
- `impeccable/reference/clarify.md`

Project references:

- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/reports/tasks/2026-05-28-artdeco-market-realtime-shape-brief.md`
- `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md`

## 12. Proposed Craft Slice After Approval

Recommended first implementation slice:

1. Compact the header/status band.
2. Replace duplicated stat surfaces with one triage/status band.
3. Add unread/high-priority/severity controls using existing local state only.
4. Make the alert table the primary surface.
5. Move rule management into a secondary configuration section.
6. Preserve API calls, rule mutations, and data-test selectors.
7. Report token lint, ESLint, type-check, PM2 status, and targeted E2E/smoke results.

Do not extract shared primitives in this slice.

## 13. Open Questions

These should be resolved before or during craft:

1. Should alert filtering be purely client-side for the first slice, using the fetched 50 rows, or should server-side query parameters be proposed later?
2. Should rule management become a collapsible section, tab, or drawer? The default recommendation is a collapsible secondary section to avoid route or modal complexity.
3. Should alert details expand inline, or should long messages stay tooltip-only for the first slice? The default recommendation is to preserve tooltip behavior in the first slice and defer row expansion.
4. Should unread state become actionable beyond filtering? The default recommendation is to defer mutation unless an existing API already supports marking read.

## 14. Approval Boundary

This brief is ready for review.

Implementation may begin only after explicit approval wording such as:

`批准实施 risk/Alerts.vue shape brief`

Without that approval, the next allowed action is documentation refinement only.
