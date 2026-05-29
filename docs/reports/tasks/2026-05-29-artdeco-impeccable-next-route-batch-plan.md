# ArtDeco Impeccable Next Route Batch Plan

Date: 2026-05-29

Status: draft for approval

Scope: design governance and page-selection planning only. This document does not approve frontend implementation.

## 1. Goal

Use `impeccable` as a Web design governance workflow for the next ArtDeco page batch after the `market/Realtime.vue` pilot.

The next batch should improve page design, component reuse, visual tokens, runtime states, and verification gates while staying aligned with the current ArtDeco document system. The batch must not become a broad "beautify the whole app" effort. It should select one high-value routed page, run critique and shape first, then wait for explicit approval before code changes.

## 2. Current OpenSpec Status

The OpenSpec change `add-artdeco-impeccable-design-gate` is functionally complete:

- Main implementation commit: `de0c5b8c9 feat(web): add ArtDeco realtime design gate pilot`.
- Active change tasks are checked in `openspec/changes/add-artdeco-impeccable-design-gate/tasks.md`.
- The archive branch `archive/artdeco-impeccable-design-gate` contains `efa776cf0 chore(openspec): archive ArtDeco design gate change`.
- The archive branch passed `openspec validate --all --strict` with `62 passed, 0 failed`.

The change is not merged back into the main worktree archive state yet. The main worktree still has an unrelated untracked `openspec/specs/artdeco-design-governance/` path, so archive integration should remain separate from the next design batch.

## 3. Governance Rules

This batch must follow the project approval gate:

- Produce design evidence first.
- Do not modify Vue, SCSS, route, API, or shared component files before explicit approval.
- Treat `web/frontend/src/router/index.ts` as route truth.
- Treat `web/frontend/src/views/<domain>/*.vue` as canonical business route entries unless a documented route exception applies.
- Treat `web/frontend/src/views/artdeco-pages/**` as wrappers, embedded pages, or compatibility surfaces unless route truth proves otherwise.
- Use ArtDeco tokens from the `--ad-*` family for approved future implementation.
- Keep desktop Web as the target surface. Minimum target viewport remains 1280x720.

For `impeccable` specifically:

- Register: `product`.
- Product scene: expert users operating a local A-share quantitative analysis terminal on desktop screens during market monitoring, trade review, risk review, and system operation.
- Design posture: restrained, authoritative, data-first ArtDeco fintech.
- Avoid marketing hero composition, decorative card grids, side-stripe borders, gradient text, and ornamental motion.

## 4. ArtDeco Alignment Sources

The next batch should continue aligning against these documents:

- `docs/guides/web/ARTDECO_MASTER_INDEX.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/api/ArtDeco_System_Architecture_Summary.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`
- `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md`

The most important live truths for this batch are:

- Route truth and ArtDeco truth are separate.
- Canonical routed pages should be reviewed before legacy ArtDeco wrappers.
- Reusable extraction must follow the component guide, not local convenience.
- Runtime state visibility is part of the design contract, not a later error-handling detail.

## 5. Pilot Baseline From `market/Realtime.vue`

The completed pilot established the page grammar for future ArtDeco route work:

- Compact route header band.
- Single predictable control row.
- Primary work area gives data the largest surface.
- Secondary panel supports interpretation without competing with primary data.
- Explicit loading, refreshing, live, cache, stale, degraded, empty, and error states.
- Existing E2E selectors and visible contracts are preserved where possible.
- Extraction is deferred until a second consumer proves reuse.

The next page should reuse this grammar as a review lens, not as a literal visual template.

## 6. Candidate Route Scan

The candidate scan focused on active routed pages under `web/frontend/src/views/trade`, `web/frontend/src/views/risk`, and `web/frontend/src/views/system`.

| Candidate | Route Status | Observed Signals | Design Relevance | Initial Priority |
|---|---:|---|---|---:|
| `web/frontend/src/views/risk/Alerts.vue` | Routed | 496 lines, high runtime-state density, 10 table references, 6 `title` attributes | Best next page for risk severity, alerts, table density, runtime state, and tooltip cleanup | P1 |
| `web/frontend/src/views/risk/Overview.vue` | Routed | 590 lines, high state density, tabbed structure, dynamic heading | Best page for risk cockpit hierarchy and tab grammar | P1 |
| `web/frontend/src/views/trade/Center.vue` | Routed | 596 lines, high ArtDeco usage, position structure, numeric columns | Best trade workflow candidate, but lower runtime-state evidence than risk pages | P1 |
| `web/frontend/src/views/trade/Signals.vue` | Routed | 711 lines, signal/execution panel, high state density | Strong workflow candidate after risk/trade structure is clarified | P2 |
| `web/frontend/src/views/trade/History.vue` | Routed | 558 lines, dense transaction columns, high ArtDeco usage | Good table-pattern candidate, less strategic than live trade/risk surfaces | P2 |
| `web/frontend/src/views/system/API.vue` | Routed | 398 lines, high state density, system health panel | Strong system-state candidate after trade/risk batch | P2 |
| `web/frontend/src/views/system/DataSource.vue` | Routed | 416 lines, data source status/configuration | Useful for runtime readiness and source-state patterns | P2 |
| `web/frontend/src/views/system/Settings.vue` | Routed | 716 lines, form-heavy settings surface | Good form/governance candidate, but lower ArtDeco page payoff | P3 |

## 7. Recommended Next Page

Recommended next `impeccable` target:

`web/frontend/src/views/risk/Alerts.vue`

Rationale:

- It is an active routed page.
- It has the strongest combination of runtime state density, table density, and risk semantics.
- Alert severity is a better stress test for ArtDeco product design than another market page.
- It can validate whether the Realtime pilot grammar works for risk-oriented workflows.
- The presence of `title` attributes suggests tooltip/accessibility debt can be reviewed without immediately changing code.
- Improvements here can later inform `risk/Overview.vue`, `system/API.vue`, and shared status surfaces.

Secondary candidate:

`web/frontend/src/views/trade/Center.vue`

Use this if the next priority is trade workflow consistency rather than risk-state grammar.

## 8. Proposed Impeccable Sequence

### Phase 1: Critique

Command intent:

`$impeccable critique web/frontend/src/views/risk/Alerts.vue`

Expected output document:

`docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md`

The critique should cover:

- Route ownership and wrapper boundaries.
- Page grammar: header, control row, primary table, supporting context, runtime status.
- Risk severity visual hierarchy.
- Alert table density and scan behavior.
- Tooltip and title-attribute debt.
- Loading, refreshing, empty, error, stale, degraded, and cache states.
- Token compliance and local visual-value debt.
- Whether any issue is P0, P1, P2, or P3.

### Phase 2: Shape

Command intent:

`$impeccable shape risk alerts ArtDeco redesign`

Expected output document:

`docs/reports/tasks/2026-05-29-artdeco-risk-alerts-shape-brief.md`

The shape brief should define:

- The page's physical scene and operating mode.
- Primary user tasks.
- Information priority order.
- Which visual structures remain from the current page.
- Which visual structures should be changed.
- State model and recovery paths.
- Verification gates.
- Explicit non-goals.

### Phase 3: Approval

No source implementation may begin until the user explicitly approves the shape brief.

Expected approval packet:

`docs/reports/tasks/2026-05-29-artdeco-risk-alerts-approval-packet.md`

The packet should include:

- Critique summary.
- Shape brief summary.
- File scope.
- Risks and compatibility contracts.
- Proposed verification commands.

### Phase 4: Craft

Only after approval:

`$impeccable craft risk alerts page`

Recommended implementation scope should be intentionally narrow:

- Header/status band.
- Filter/control row.
- Primary alert table layout.
- Severity/state strip.
- Loading, empty, error, stale, degraded, and cache presentation.
- Tokenized touched styles only.

Do not extract shared primitives during this phase unless a second consumer or approved extraction rationale exists.

### Phase 5: Audit, Polish, Extract Decision

After craft:

- Run technical verification.
- Run `$impeccable audit` for accessibility, states, and responsive desktop constraints.
- Run `$impeccable polish` only for scoped finishing issues.
- Decide whether extraction is justified by comparing `risk/Alerts.vue` and `market/Realtime.vue`.

Potential extraction candidates after two pages:

- `ArtDecoPageHeader`
- `ArtDecoControlBar`
- `ArtDecoStatusStrip`
- `ArtDecoDataPanel`
- route-level runtime state naming pattern

Extraction should remain a separate approved task.

## 9. Scoring Model

Use this scoring model for next-page selection and critique:

| Area | Weight | What Good Looks Like |
|---|---:|---|
| Route truth and ownership | 20 | Active route verified, no wrapper confusion |
| Task criticality | 20 | Page supports market, trade, risk, or system decisions |
| Runtime state clarity | 20 | Loading, refresh, stale, degraded, empty, error, and recovery are visible |
| Data density and hierarchy | 15 | Tables/charts are scannable and primary data wins |
| ArtDeco token alignment | 10 | Touched visual values use tokens or documented exceptions |
| Reuse potential | 10 | Candidate patterns can repeat across at least two pages |
| Verification feasibility | 5 | Existing smoke/E2E or focused checks can protect changes |

Recommended cutoff:

- 85 to 100: immediate pilot candidate.
- 70 to 84: candidate after critique.
- 50 to 69: document debt first.
- Below 50: defer unless the page is user-critical.

## 10. Verification Gates For Future Implementation

Future implementation must report:

- Structural syntax errors: expected `0`.
- Type-check result and whether any errors are pre-existing.
- ArtDeco token/lint result for touched files.
- PM2 service status if the page requires runtime verification.
- Actual E2E or smoke command, browser project, pass/fail/skip counts.
- Whether GitNexus impact/detect_changes was available, or why it was blocked.

For documentation-only critique and shape phases:

- Verify no Vue, TS, SCSS, route, API, or shared component files changed.
- Validate any related OpenSpec change if one is created.

## 11. Open Decisions

1. Should the next target be risk-first (`risk/Alerts.vue`) or trade-first (`trade/Center.vue`)?
2. Should the OpenSpec archive branch `archive/artdeco-impeccable-design-gate` be merged before the next batch starts?
3. Should the existing untracked `openspec/specs/artdeco-design-governance/` in the main worktree be treated as separate prior work or reconciled with the archive branch?
4. Should the next critique produce only a Markdown report, or also create a new OpenSpec change for the risk/trade batch?

## 12. Recommended Next Action

Proceed with documentation only:

`$impeccable critique web/frontend/src/views/risk/Alerts.vue`

Create:

`docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md`

Do not modify frontend source code until the critique is reviewed, a shape brief is produced, and the user explicitly approves implementation.
