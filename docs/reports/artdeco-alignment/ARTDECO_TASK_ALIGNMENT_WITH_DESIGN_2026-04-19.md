# ArtDeco Task Alignment With DESIGN

Date: 2026-04-19  
Status: Draft for review  
Purpose: Align the latest ArtDeco governance/runtime documents with concrete project tasks while keeping execution direction consistent with `DESIGN.md`

---

## 1. Alignment Verdict

The latest ArtDeco document chain is now broadly aligned around one strategic center:

- `DESIGN.md` is the design contract truth
- the `web/` guide documents define governance, runtime structure, and placement rules
- the uppercase compatibility paths under `docs/guides/` and `docs/api/` are redirect-only, not parallel truth

For project execution, the correct order of authority is now:

1. `architecture/STANDARDS.md`
2. `DESIGN.md`
3. `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
4. `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
5. `docs/api/ArtDeco_System_Architecture_Summary.md`
6. `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
7. `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`

This means future ArtDeco work should no longer start from historical V3 prose or directory habit. It should start from `DESIGN.md` strategy, then use the other docs to decide placement, runtime path, and implementation boundary.

---

## 2. Strategic Direction From DESIGN.md

The project task direction that must remain stable is:

- ArtDeco brand DNA stays intact: black/gold contrast, geometric framing, uppercase display typography
- trading and data-dense surfaces stay data-first rather than decoration-first
- A-share semantics remain mandatory: red = up/profit, green = down/loss
- desktop-only workbench remains the product target
- Element Plus remains the behavioral base; ArtDeco adds token/theme overrides instead of replacing component logic
- interaction safety remains explicit: one primary action per trading panel
- component state behavior should move toward the `--ad-*` token system
- decorative corner markers remain globally disabled until overlap issues are solved

Anything that violates these points is misaligned even if it looks “more decorative” or “more complete”.

---

## 3. What Each Document Should Contribute To Tasks

### 3.1 `docs/guides/web/ARTDECO_MASTER_INDEX.md`

Task meaning:

- use this as the routing table for documentation
- use it to determine whether a document is active governance, runtime reference, or historical baseline
- use it to prevent task execution from starting from deprecated or compatibility-only paths

Project task implication:

- every new ArtDeco task should cite the active `web/` path, not the uppercase compatibility path

### 3.2 `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`

Task meaning:

- this is the main implementation-boundary doc after `DESIGN.md`
- it defines active style truth, route truth separation, runtime modes, and engineering constraints

Project task implication:

- use this to decide whether a feature belongs in tokens, reusable components, page workbench blocks, or domain views
- use this to reject work that tries to treat `artdeco-pages/**` as the universal routed-page truth

### 3.3 `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`

Task meaning:

- this is the current inventory map
- it answers “what already exists” before building or moving anything

Project task implication:

- every new component task should first check whether an equivalent asset already exists
- every refactor task should classify its target as reusable asset, page fragment, domain block, or runtime state helper

### 3.4 `docs/api/ArtDeco_System_Architecture_Summary.md`

Task meaning:

- this is the runtime reality map
- it explains how the current frontend actually runs instead of how an idealized model should run

Project task implication:

- use this before any layout, routing, page-shell, or summary-state change
- use this to avoid false assumptions such as “everything is driven by `pageConfig.ts`”

### 3.5 `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`

Task meaning:

- this is the placement decision document
- it defines where reusable components, page fragments, domain blocks, and shared composables belong

Project task implication:

- every UI task should include a placement decision before implementation
- any task involving `src/components/artdeco/**`, `views/artdeco-pages/**`, or `src/composables/` should be checked against this guide first

### 3.6 `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`

Task meaning:

- historical baseline only
- useful for understanding what V3 contributed and what has changed since

Project task implication:

- use it for context, not for current implementation rules
- do not reopen old V3 behavior if it conflicts with the current `DESIGN.md` contract

### 3.7 `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md`

Task meaning:

- compatibility redirect only

Project task implication:

- do not update this file with independent content
- keep it as a thin redirect when path compatibility matters

### 3.8 `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md`

Task meaning:

- compatibility redirect only

Project task implication:

- do not treat it as a second architecture source

---

## 4. Concrete Task Alignment For The Current Project

The current project task set should be organized into the following workstreams.

### Workstream A: Runtime truth and compatibility closure

Direct source:

- `DESIGN.md`
- `ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `ArtDeco_System_Architecture_Summary.md`

Concrete tasks:

- keep `artdeco-tokens.scss` as canonical token truth
- keep `artdeco-main.css`, `artdeco-variables.css`, and `artdeco-colors.css` as compatibility bridges only
- continue eliminating conflicting compatibility values only when they affect active runtime paths
- do not create new truth in compatibility files

Success condition:

- active runtime paths resolve to the design contract without hidden legacy overrides

### Workstream B: Component state-machine adoption

Direct source:

- `DESIGN.md`
- `ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `ARTDECO_COMPONENT_GUIDE.md`

Concrete tasks:

- adopt `--ad-*` state tokens on a narrow shared surface first
- prioritize `ArtDecoButton`, `ArtDecoInput`, `ArtDecoCard`, shared table row states
- keep Element Plus logic intact and change only visual token wiring
- remove ad-hoc hover/focus/error patterns only when the tokenized state replaces them

Success condition:

- shared primitives express consistent state behavior without rewriting base UI logic

### Workstream C: Chip / badge / status semantics

Direct source:

- `DESIGN.md`
- `ARTDECO_COMPONENTS_CATALOG.md`

Concrete tasks:

- define one canonical implementation path for filter chips and status chips
- align badge-like components with holding / pending / warning / profit / loss semantics
- avoid business-inline chip styling in page-level blocks when a reusable primitive can carry it

Success condition:

- market filters and status indicators read consistently across pages

### Workstream D: Layout-level summary and shared runtime state

Direct source:

- `ARTDECO_MASTER_INDEX.md`
- `ArtDeco_System_Architecture_Summary.md`
- `ARTDECO_COMPONENT_GUIDE.md`

Concrete tasks:

- treat `useHeaderSummary.ts` as the current shared summary bridge
- move repeated header summary logic into shared composables only when there are 2+ real consumers
- do not push this logic into token files, page config, or base components

Success condition:

- cross-page summary behavior is shared through runtime state, not copied across pages

### Workstream E: Directory and placement governance

Direct source:

- `ARTDECO_COMPONENT_GUIDE.md`
- `ARTDECO_COMPONENTS_CATALOG.md`
- `ARTDECO_FINTECH_UNIFIED_SPEC.md`

Concrete tasks:

- new routed pages default to `views/<domain>/`
- new ArtDeco workbench blocks go to `views/artdeco-pages/*-tabs/`
- stable reusable assets go to `src/components/artdeco/**`
- layout/page shared state with 2+ consumers goes to `src/composables/`
- compatibility wrappers stay thin

Success condition:

- no new parallel structure is created during ArtDeco cleanup or feature work

---

## 5. Explicit Do / Do Not Task Rules

### Do

- start implementation tasks from `DESIGN.md` strategy, not historical V3 language
- use the `web/` guide files as active governance references
- treat runtime structure, placement, and design contract as separate but linked concerns
- keep desktop-first, data-first, A-share-first assumptions stable
- preserve the approved exception that decorative corner markers stay disabled

### Do Not

- do not use compatibility redirect files as editable truth sources
- do not treat `artdeco-pages/**` as the default home for every new page
- do not introduce a second component-state model outside `--ad-*`
- do not reintroduce Marcellus/Josefin-era behavior if it conflicts with the current contract
- do not convert historical V3 summary text into current execution truth without checking current code and `DESIGN.md`

---

## 6. Recommended Immediate Task Order

To stay aligned with the latest doc chain and `DESIGN.md`, the safest next execution order is:

1. finish Phase A+B sign-off as documentation/runtime truth closure
2. run a narrow state-machine adoption batch on shared primitives
3. align chip/badge/status semantics on reusable assets
4. align tooltip/overlay tokens on shared primitives
5. only then consider broader responsive residue or chart-theme cleanup

Reason:

- this sequence follows the design contract and avoids mixing governance cleanup with wide-scope visual refactors

---

## 7. Review Conclusion

The latest ArtDeco 8-document chain is directionally correct and now points to the same strategic center as `DESIGN.md`.

For this project, the correct execution interpretation is:

- `DESIGN.md` decides the experience strategy
- `ARTDECO_FINTECH_UNIFIED_SPEC.md` decides implementation boundary
- `ARTDECO_COMPONENT_GUIDE.md` decides placement
- `ArtDeco_System_Architecture_Summary.md` decides runtime understanding
- `ARTDECO_COMPONENTS_CATALOG.md` prevents duplicate construction
- `ARTDECO_V3_COMPLETE_SUMMARY.md` provides historical baseline only

If future tasks follow that order, ArtDeco work will stay consistent with the current project direction instead of drifting back into historical parallel truths.

