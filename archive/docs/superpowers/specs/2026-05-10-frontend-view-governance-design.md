# Frontend View Governance Design

Date: 2026-05-10

## Context

The frontend currently contains many Vue view files under `web/frontend/src/views/`. The active runtime surface is much smaller than the file inventory because the repository retains canonical routed pages, ArtDeco compatibility wrappers, embedded tabs, demos, examples, and historical migration assets.

The intended cleanup must not treat "not in the sidebar" or "not directly routed" as deletion evidence. View cleanup is a migration-closure problem: first define truth sources, then classify functional assets, then absorb valuable capabilities, and only then isolate redundant pages in archive.

## Goals

- Maintain and optimize the current frontend view directory structure instead of replacing it wholesale.
- Ensure every formal business-domain directory has functional coverage aligned with current menu and route truth.
- Avoid rebuilding or discarding existing useful assets by reviewing legacy/non-canonical pages for reusable business capability before cleanup.
- Treat `web/frontend/src/layouts/MenuConfig.ts` as the single source of truth for the visible main menu.
- Treat `web/frontend/index.html -> /src/main-standard.ts -> router/index.ts` as the frontend runtime entry truth chain.
- Treat `web/frontend/src/router/index.ts` dynamic imports as the single source of truth for active routed pages.
- Keep the current router dynamic-import set as the canonical business-view baseline. The current measured value is 42 view-specific dynamic imports, but the rule follows the route import set rather than a hardcoded count.
- Preserve a shallow structure: formal business domains, special detail/blank pages, and governed archive.
- Classify every non-canonical view before mutation.
- Absorb reusable business assets into canonical pages or shared layers before archiving old pages.
- Archive only pages that are fully replaced, obsolete, and have no remaining reusable assets or hidden references.

## Non-Goals

- Do not delete view files as part of the first governance pass.
- Do not move files before the inventory and classification are approved.
- Do not introduce a second menu configuration source.
- Do not expand the main menu beyond two levels.
- Do not perform broad visual polish while doing structural closure.
- Do not classify a page as redundant while it still provides unique business function coverage, reusable implementation assets, compatibility behavior, or guard/test value.

## Truth Sources

| Surface | Role |
|---|---|
| `index.html -> /src/main-standard.ts -> router/index.ts` | Runtime entry truth chain |
| `MenuConfig.ts` | Visible main-menu truth |
| `router/index.ts` dynamic imports | Active routed page truth |
| `views/<domain>/<Page>.vue` | Canonical business page shape |
| `/dashboard`, `/login`, `404`, `/detail/*` | Special pages outside the main menu hierarchy |
| Archive directory | Isolation target for formally retired pages, not a deletion target |

The menu and router must stay aligned. A menu item cannot point to a missing route. A routed page that is intentionally hidden from the menu must carry an explicit role such as detail page, blank-layout page, compatibility route, or experimental route.

`/detail/*` is an existing special route group in `router/index.ts`; it currently includes `/detail/graphics/:symbol` and `/detail/news/:symbol`. It is not a business-domain menu root and should stay outside the main menu hierarchy.

## Directory Structure Target

The governance target is to preserve a stable three-zone structure:

| Zone | Directory shape | Rule |
|---|---|---|
| Formal business domains | `views/market`, `views/data`, `views/watchlist`, `views/strategy`, `views/trade`, `views/risk`, `views/system`, plus approved `views/ai` if retained as a formal domain | Must have menu/route-aligned functional coverage |
| Special pages | Root-level shell/detail pages and currently routed ArtDeco exceptions such as `/dashboard`, `/login`, `404`, `/detail/*`, `/trade/terminal` | Must be explicitly listed as special, not mistaken for directory drift |
| Governed archive | `views/archive/**` | Stores reviewed retired pages only; no runtime/menu references allowed |

No new parallel business-domain directory should be introduced unless an approved routing/menu change declares it as formal. Existing non-formal directories are reviewed for assets and then classified, not mechanically deleted.

## Functional Coverage Rules

Each formal business-domain directory must retain page coverage for its current menu and route entries. A directory is considered covered when every visible menu leaf for that domain resolves to a router dynamic import and the imported page provides the expected functional surface or delegates to a documented canonical successor.

Before any non-canonical page is archived, the batch must answer whether it contains unique coverage for:

- A visible menu leaf.
- A hidden but intentional route such as detail, blank layout, compatibility, or experimental route.
- A domain workflow that is not yet represented in the current canonical page.
- A reusable asset that should be absorbed into a canonical page or shared layer.

If any answer is yes, the page is not redundant.

## Classification Model

Every non-canonical view receives one lifecycle status before mutation:

| Status | Meaning | Allowed action |
|---|---|---|
| `candidate-review` | Not canonical, but not yet analyzed | Read-only inventory only |
| `absorb-assets` | Contains reusable business assets | Extract or merge assets into canonical pages/shared layers |
| `compat-retained` | Still needed by wrapper, tab, test, or historical integration | Keep and document successor conditions |
| `experimental` | Demo, lab, or grey capability | Keep outside the main menu and mark as non-production |
| `archive-candidate` | Replaced, obsolete, no useful assets found | Eligible for approved archive move |
| `archived` | Isolated in archive after approval | No runtime/menu references allowed |

A compatibility wrapper is any view that forwards to, wraps, or composes a canonical page or tab without becoming an independent business truth source. Wrappers can stay `compat-retained` while callers still depend on their historical import paths, but they must not accumulate new standalone business logic.

Lifecycle status is not enough by itself. Each non-canonical view also receives two auxiliary labels:

| Dimension | Values | Purpose |
|---|---|---|
| Route status | `active`, `redirect`, `dead` | Records whether the page is directly routed, indirectly reachable through compatibility, or not reachable from the router |
| Guard status | `mainline-guarded`, `spec-guarded`, `unguarded` | Records whether tests or mainline-gate specs still protect the file or its directory |

An `archive-candidate` must include a successor page or an explicit `no-successor-needed` rationale. A page cannot become archive-eligible only because its route was moved.

## Redundant Page Definition

A page can be classified as redundant only when all of the following are true:

- It is not part of the active routed-page baseline.
- It is not a visible menu entry and is not an intentional hidden route.
- It does not provide unique business-domain function coverage.
- Its useful assets have either been absorbed into canonical pages/shared layers or explicitly rejected with rationale.
- It has no active static import, dynamic import, layout-tab, page-config, docs, string-link, or test guard reference.
- It has a documented canonical successor or `no-successor-needed` rationale.

Pages that fail any condition remain `candidate-review`, `absorb-assets`, `compat-retained`, or `experimental`.

Per-page decisions must use the review checklist at `docs/reports/quality/myweb-audit/frontend-view-redundant-page-review-checklist-2026-05-10.md`. A page cannot be marked `archive-candidate` unless the checklist records evidence for truth-source checks, functional coverage checks, reusable asset checks, guard/test checks, successor decision, and redundant eligibility.

The checklist must also record previous historical classification when available, the guard/spec discovery commands or guard-map artifact used, the lifecycle decision, and the separate execution action.

## Asset Extraction Scope

Each non-canonical page is reviewed for only five asset classes to avoid endless refactoring:

- Reusable UI components.
- Shared composables, API normalization, request provenance, or freshness handling.
- Metric cards, KPI grids, stats strips, and summary logic.
- Table columns, filters, selectors, and query schemas.
- Market, strategy, risk, trading, or system calculation rules.

If none of these asset classes are present, the page can move directly to archive-candidate after hidden-reference checks.

## Hidden Reference Checks

Before a page can be archived, the batch must check more than route/menu references:

- Static imports and dynamic imports.
- `import.meta.glob` patterns. No current matches were found during the review sweep, but this remains a defensive check for future additions.
- Layout tab registration and page registries.
- Tests and snapshots.
- `*-mainline-gate.spec.ts` and other guard specs, with migration status recorded before archive.
- Documentation links and generated page config.
- Feature flags and string-based runtime mappings.
- Legacy aliases and compatibility routes.

## Archive Rules

Archive is isolation, not deletion. Archived views must not be imported by router, menu, layout tabs, tests, or generated runtime config. Physical deletion requires a later explicit approval and a separate cleanup batch.

In this spec, "cleanup" means approved isolation, rerouting, or archive movement after review. It does not mean direct physical deletion.

The archive structure should remain shallow and searchable. Recommended shape:

```text
web/frontend/src/views/archive/
├── README.md
├── demo/
├── legacy/
├── replaced/
└── experimental/
```

Archive target mapping:

| Source classification | Archive target | Rule |
|---|---|---|
| Demo or sample-only view | `archive/demo/` | No production route/menu role and no reusable business asset remains |
| Legacy migration remnant or old naming surface | `archive/legacy/` | Superseded by canonical route or wrapper and no hidden reference remains |
| Fully replaced business page | `archive/replaced/` | Has a documented canonical successor |
| Experimental/lab page | `archive/experimental/` | Not part of production menu and intentionally preserved for reference |

`absorb-assets`, `compat-retained`, and unresolved `candidate-review` files have no archive destination until their lifecycle status changes.

Archive exit checklist:

- Route has no active or compatibility reference.
- Menu has no reference.
- Layout tabs and page registries have no reference.
- `import.meta.glob` has no match. Current codebase has no matches, so this is a defensive check.
- `*-mainline-gate.spec.ts` has no reference, or the guard has been migrated to the canonical successor.
- Other `*.spec.ts` files have no reference, or the tests have been migrated.
- Composable consumers are either migrated, explicitly retained, or archived in the same approved batch.
- A successor page or `no-successor-needed` rationale is recorded.

## Execution Plan

0. Build a guard map before lifecycle classification: `page -> mainline-gate specs -> other specs -> page-config/docs/runtime string references`.
1. Create a read-only inventory of all view files and classify each file against the current menu and route truth sources.
2. Run a pre-classification sweep for zero-router-reference legacy directories, including `stocks/`, `trading/`, `trading-decision/`, `trade-management/`, `technical/`, and `settings/`.
3. Review non-canonical views by business domain and assign lifecycle status plus route status and guard status.
4. For duplicate or forked pages, use a standard fork-resolution template: list versions, consumers, wrapper/fork/parallel-evolution status, canonical truth, and retirement condition.
5. Complete the redundant-page review checklist for every page proposed as `archive-candidate`.
6. Extract or merge reusable assets into canonical pages or approved shared layers.
7. Move only approved archive candidates into the archive directory.
8. If a hidden reference to an archived view is discovered after a move, restore the view to its original path and reclassify it as `compat-retained` until the reference is resolved.
9. Add guards that prevent archived views from re-entering runtime routes or menus.

## Verification

Every mutation batch that changes router, layout, menu, or file location must report:

- Structural syntax errors: 0 blocking errors.
- Type status compared with the current frontend type baseline.
- PM2 backend and frontend service status.
- Actual E2E or smoke command, browser project, executed suite, and pass/fail counts.

Read-only inventory batches only need command evidence and generated artifact paths.

Completion states:

- Governance complete: inventory, guard map, classification, approved asset absorption, and approved archive isolation are finished for the batch scope.
- Merge ready: governance complete, no unresolved archive guard references, type status does not regress from baseline, required tests/smokes pass, and the branch can merge to `main` without unresolved conflicts.
