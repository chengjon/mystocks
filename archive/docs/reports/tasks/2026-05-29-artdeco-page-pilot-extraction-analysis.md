# ArtDeco Page Pilot Extraction Analysis

> Date: 2026-05-29
> Method: `$impeccable extract` decision analysis, documentation only.
> Scope: completed Web ArtDeco pilots for Realtime, Risk Alerts, and Trade Positions.
> Boundary: no route changes, no API contract changes, no shared component extraction, and no Vue source edits in this batch.

## 1. Purpose

This report compares the three completed ArtDeco page pilots before any shared design-system extraction work begins.

The goal is to separate:

- patterns that are stable enough to document now
- patterns that need one more route before extraction
- patterns that should stay page-local because their domain behavior differs

This is intentionally not a component implementation plan. It is the approval boundary before a future extraction proposal.

## 2. Inputs Reviewed

ArtDeco governance and architecture references:

- `docs/guides/web/ARTDECO_MASTER_INDEX.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/api/ArtDeco_System_Architecture_Summary.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`
- `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md`

Pilot artifacts:

- `docs/reports/tasks/2026-05-28-artdeco-market-realtime-critique.md`
- `docs/reports/tasks/2026-05-28-artdeco-market-realtime-shape-brief.md`
- `docs/reports/tasks/2026-05-28-artdeco-market-realtime-implementation-report.md`
- `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md`
- `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-shape-brief.md`
- `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-implementation-report.md`
- `docs/reports/tasks/2026-05-29-artdeco-trade-positions-critique.md`
- `docs/reports/tasks/2026-05-29-artdeco-trade-positions-shape-brief.md`
- `docs/reports/tasks/2026-05-29-artdeco-trade-positions-implementation-report.md`

Implementation surfaces compared without editing:

- `web/frontend/src/views/market/Realtime.vue`
- `web/frontend/src/views/risk/Alerts.vue`
- `web/frontend/src/views/trade/Center.vue`

## 3. OpenSpec Status

`openspec validate add-artdeco-impeccable-design-gate --strict` passed with:

```text
Change 'add-artdeco-impeccable-design-gate' is valid
```

`openspec list` reports:

```text
add-artdeco-impeccable-design-gate    Complete
```

Archive was not executed in this batch because the worktree already contains an untracked `openspec/specs/artdeco-design-governance/` canonical spec directory. Archiving now could mix this line with pre-existing OpenSpec spec work. The safe closeout is:

1. keep this analysis documentation-only
2. stage and commit only this report plus any explicit task-plan pointer updates
3. archive `add-artdeco-impeccable-design-gate` only after ownership of the existing `openspec/specs/artdeco-design-governance/` path is confirmed

## 4. Cross-Page Pattern Matrix

| Pattern | Realtime | Risk Alerts | Trade Positions | Extraction Readiness |
|---|---|---|---|---|
| Canonical route ownership | Active `views/market/Realtime.vue` route | Active `views/risk/Alerts.vue` route | Active `views/trade/Center.vue` route | Document now; no routing extraction |
| Operational header/status band | Market freshness and request context | Alert queue health and stale snapshot context | Positions review context and verified count | Document now as a route grammar |
| First-level control lens | Market filter / segment lens | Severity and triage lens | Review segment lens | Pattern candidate; component extraction deferred |
| Runtime status strip | loading, stale, error, refresh, verified states | verified, refreshing, stale, degraded, empty, error states | loading, verified, refreshing, stale, degraded, empty, error states | Strong candidate after one more route confirms state vocabulary |
| Primary data surface | market data surface, data-density first | alert table first, rule management secondary | positions table first, summary strip secondary | Do not extract; table semantics differ by domain |
| Empty/error/retry states | present, mixed with data freshness | present, needs triage-specific recovery language | route-local hooks and filtered-empty state added | Document checklist now; helper extraction later only if state API stabilizes |
| ArtDeco token discipline | tokenized touched styles | tokenized ArtDeco surfaces and severity semantics | tokenized financial row decorations | Keep as lint/audit gate, not component extraction |
| E2E verification surface | route compatibility preserved | route-level tests added in prior slice | route-local `data-test` hooks added | Document now as verification convention |

## 5. Quantitative Signals

The three pages show repeated vocabulary but not identical implementation contracts.

| File | `runtime` refs | `loading` refs | `error` refs | `stale` refs | `segment` refs | `data-test` hooks | `@media` refs |
|---|---:|---:|---:|---:|---:|---:|---:|
| `market/Realtime.vue` | 19 | 18 | 20 | 8 | 10 | 0 | 1 |
| `risk/Alerts.vue` | 12 | 11 | 8 | 18 | 0 | 6 | 2 |
| `trade/Center.vue` | 13 | 10 | 7 | 7 | 16 | 11 | 0 |

Interpretation:

- Runtime-state language repeats across all three pilots.
- Segment/control vocabulary repeats, but each page uses different domain labels and action semantics.
- `data-test` coverage improved in the later pilots, especially Trade Positions.
- Remaining `@media` references in Realtime and Risk Alerts should be reviewed against the desktop-only ArtDeco constraint before future extraction work.

## 6. Extraction Readiness Verdict

### Ready To Document Now

These patterns are mature enough for documentation and future audit checklists:

- route-level ArtDeco page grammar: header -> control lens -> runtime status -> primary data surface
- runtime trust language: verified, refreshing, stale, degraded, empty, and error states
- dense financial table priority over decorative metrics
- route-local E2E hooks for page, controls, status, data surface, empty, error, and retry states
- ArtDeco token gate for touched styles

### Candidate For Later Extraction

These may become reusable assets after one more routed page proves the same contract:

- `ArtDecoRuntimeStatusStrip`
- `ArtDecoReviewLens` / `ArtDecoTriageLens`
- `ArtDecoRouteDataPanel`
- route-level state-verification helper for E2E tests

The next page should prove whether the same runtime state contract holds outside market / risk / positions contexts.

### Not Ready For Extraction

These should remain page-local:

- API request orchestration
- table column definitions
- market / alert / position row semantics
- domain-specific segment labels
- rule-management or secondary configuration panels
- router metadata
- shared component placement under `src/components/artdeco/**`

## 7. ArtDeco Alignment

The current docs support this conservative route:

- `ARTDECO_MASTER_INDEX.md` treats `web/frontend/src/views/<domain>/*.vue` plus `router/index.ts` as the current active route truth.
- `ARTDECO_COMPONENT_GUIDE.md` says `src/components/artdeco/**` should hold sustainable reusable assets, not page-local orchestration.
- `ARTDECO_FINTECH_UNIFIED_SPEC.md` and `ARTDECO_V3_COMPLETE_SUMMARY.md` emphasize data-first financial density, compact / micro-density, semantic financial color, and component state-machine tokens.
- `ArtDeco_System_Architecture_Summary.md` keeps runtime architecture and component boundaries separate from historical ArtDeco compatibility layers.

That means the next responsible step is a design-pattern document or OpenSpec follow-up, not immediate shared component code.

## 8. Recommended Next Work

1. Do not extract shared components yet.
2. Treat `trade/Signals.vue` as the fourth completed pilot and use it to refresh the route-grammar evidence set.
3. Open a small OpenSpec follow-up only for the route-level ArtDeco page grammar and verification-hook standard.
4. Before any future `$impeccable craft`, require a shape brief and explicit user approval.
5. Before any future `$impeccable extract`, require an extraction proposal that proves:
   - at least four routed pages share the same pattern
   - the candidate component does not own API orchestration
   - the candidate component does not change route metadata
   - the candidate component does not alter API contracts
   - the candidate component has route-level E2E coverage

## 9. Verification

Completed for this documentation batch:

- `openspec validate add-artdeco-impeccable-design-gate --strict`: pass
- `openspec list`: `add-artdeco-impeccable-design-gate` is `Complete`
- No Vue source edits were made by this extraction-analysis batch
- No route files were edited
- No API contract files were edited
- No shared component files were edited

Known blocker carried forward:

- GitNexus staged detect remained a tooling-performance blocker in the previous commit and should be tracked separately from ArtDeco page design work.

## 10. Post-Signals Four-Pilot Refresh

This section supersedes the earlier three-pilot extraction notes now that `trade/Signals.vue` has been implemented and committed as `88ec01fd3 feat(web): craft ArtDeco trade signals trust desk`.

### 10.1 Current Evidence Set

| Route | Source lines | Local `@media` count | `data-testid` attrs | Primary runtime marker | Latest targeted E2E |
|---|---:|---:|---:|---|---|
| `market/Realtime.vue` | 621 | 1 | 0 | `status-strip` | market external PM2 smoke: 18 passed |
| `risk/Alerts.vue` | 753 | 2 | 0 | `runtime-status-strip` | Risk-Alerts Chromium: 4 passed |
| `trade/Center.vue` | 835 | 0 | 0 | `artdeco-trading-positions__runtime` | Trade-Positions Chromium: 4 passed |
| `trade/Signals.vue` | 821 | 0 | 7 | `signal-trust-strip` | Trade-Signals Chromium: 4 passed |

### 10.2 Four-Route Grammar

The four completed pilots now prove this Web ArtDeco route grammar:

```text
compact operational header
-> first-level review/control lens
-> runtime trust/status strip
-> primary data surface
-> secondary evidence panels
```

This grammar is strong enough to document and govern. It is still not a direct approval to extract shared Vue components, because each route still owns different data semantics, API orchestration, fallback copy, and table/list behavior.

### 10.3 Extraction Readiness Update

Ready to document now:

- route-level page grammar
- runtime state vocabulary
- first-level review/control lens placement
- primary data surface placement
- secondary panel placement
- route-level E2E hook expectations
- no-route/no-API/no-shared-component boundary for page craft slices

Candidate for a future OpenSpec proposal, not immediate code:

- `ArtDecoRouteHeaderBand`
- `ArtDecoReviewLens`
- `ArtDecoRuntimeTrustStrip`
- `ArtDecoPrimaryDataSurfaceShell`
- `ArtDecoRouteVerificationHooks`

Still not ready for direct extraction:

- API loading, normalization, stale snapshot, or retry orchestration
- route metadata, breadcrumbs, menu state, or router definitions
- table/list row semantics
- financial domain labels
- page-specific fallback copy
- compatibility imports from `web/frontend/src/views/artdeco-pages/**`

### 10.4 Updated Next Step

The next implementation should be documentation/specification work:

1. Draft an OpenSpec proposal such as `standardize-artdeco-route-grammar`.
2. Define route-level E2E hook naming before touching earlier pilots.
3. Define shared-component contracts before creating any files under `src/components/artdeco/**`.
4. Choose one low-risk follow-up route only after the proposal is approved.

This keeps the line aligned with the user boundary: no route changes, no API contract changes, and no shared component extraction without a separate approval gate.
