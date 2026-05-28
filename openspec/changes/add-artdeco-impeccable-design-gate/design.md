# Design: ArtDeco Impeccable Design Gate

## Context

The Web frontend has a refreshed ArtDeco direction in `PRODUCT.md` and `DESIGN.md`, plus an implementation alignment plan at `docs/reports/tasks/2026-05-28-artdeco-web-design-alignment-plan.md`.

The plan is intentionally document-first. It should audit the already implemented Web ArtDeco design and produce design artifacts before any page implementation. This protects the project from local visual polish that conflicts with route truth, token truth, runtime state requirements, or the current ArtDeco documentation chain.

## Goals

- Use `impeccable` as a Web design governance workflow, not as a one-shot full-site beautification pass.
- Audit implemented ArtDeco pages and style assets before code changes.
- Align `DESIGN.md`, ArtDeco guide documents, component catalog references, and compatibility documents.
- Produce page-level critique and shape artifacts before implementation.
- Preserve an approval boundary between design documentation and source edits.
- Keep the first implementation candidate narrow enough to validate a reusable page grammar.

## Non-Goals

- Do not change Vue, TypeScript, SCSS, tokens, routes, or components during the pre-approval design phase.
- Do not redefine `views/artdeco-pages/**` as the universal active route truth.
- Do not rewrite historical V3 documents as current implementation truth.
- Do not extract shared components from a single page.
- Do not bypass OpenSpec or `architecture/STANDARDS.md` approval gates for UI/UX changes.

## Design Workflow

### Phase 1: Design Documentation Gate

Run the documentation and audit sequence:

1. `$impeccable document`
2. Compare the extracted design facts against the current ArtDeco documentation chain.
3. `$impeccable critique web/frontend/src/views/market/Realtime.vue`
4. Save critique findings as a report under `docs/reports/tasks/`.
5. `$impeccable shape web/frontend/src/views/market/Realtime.vue`
6. Treat the shape brief as the design document for approval.

Allowed outputs before approval:

- refreshed design context notes
- ArtDeco documentation alignment findings
- page-level critique reports
- shape briefs
- page review checklists
- implementation task plans
- verification plans

Disallowed outputs before approval:

- Vue implementation edits
- TypeScript implementation edits
- SCSS or token rewrites
- route changes
- component extraction
- broad visual cleanup
- build, PM2, or E2E success claims for UI code that has not been implemented

### Phase 2: Approval Boundary

The user must explicitly approve the design documents and implementation scope before implementation begins. Acceptable approval wording should be explicit, such as `批准`, `同意实施`, or a milestone approval comment that names the approved page and scope.

### Phase 3: Post-Approval Implementation

After approval, run:

1. `$impeccable craft <approved target>`
2. `$impeccable audit <approved target>`
3. `$impeccable polish <approved target>`
4. `$impeccable extract <approved target>` only after the pattern has 2+ consumers or an approved extraction rationale

Implementation must stay inside the approved shape scope and report the frontend quality gates required by `architecture/STANDARDS.md`.

## Priority Model

Use this priority order when original design or documentation can be improved:

| Priority | Meaning | Examples |
|---|---|---|
| P0 | Contradicts route truth, token truth, runtime safety, or verification gates | docs implying `views/artdeco-pages/**` is universal route truth, new hard-coded visual values, missing stale/error state |
| P1 | Affects high-use pages or task-critical workflows | realtime market data, trading workflow, risk monitoring, system operational state |
| P2 | Can become a reusable page or component pattern after evidence | page header band, control row, status strip, data panel, route-level state pattern |
| P3 | Historical, cosmetic, or low-risk documentation cleanup | old screenshots, V3 summary wording, compatibility pointer polish |

## Source Document Alignment

The design gate must compare against these ArtDeco documents:

- `docs/guides/web/ARTDECO_MASTER_INDEX.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/api/ArtDeco_System_Architecture_Summary.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`
- `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md`

## Risks

- `impeccable document` may rewrite `DESIGN.md`. If that happens, review the diff as design documentation, not as implementation.
- Existing ArtDeco documents may contain historical claims that should stay historical. Do not convert them into current truth without verification.
- The first pilot page may reveal cross-route component needs. Do not extract shared components until a second consumer or approved extraction rationale exists.
- OpenSpec validation may pass while design artifacts remain incomplete. The task checklist must still enforce artifact completion before approval.
