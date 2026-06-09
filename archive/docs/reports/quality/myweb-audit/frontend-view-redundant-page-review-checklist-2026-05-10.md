# Frontend View Redundant Page Review Checklist - 2026-05-10

## Purpose

This checklist is the per-page decision form for frontend view governance. It prevents useful Vue pages from being archived only because they are not visible in the current menu or not directly imported by the router.

Use this checklist for every non-canonical view before assigning `archive-candidate`.

## Page Metadata

| Field | Value |
|---|---|
| Page path |  |
| Current directory |  |
| Initial inventory class | `candidate-review` / `absorb-assets` / `compat-retained` / `experimental` / `archive-candidate` |
| Previous historical classification |  |
| Previous classification source |  |
| Previous classification upheld or changed? |  |
| Route status | `active` / `redirect` / `dead` |
| Guard status | `mainline-guarded` / `spec-guarded` / `unguarded` |
| Proposed lifecycle status |  |
| Reviewer |  |
| Review date |  |

## Truth-Source Checks

| Check | Yes/No | Evidence |
|---|---|---|
| Is this page dynamically imported by `router/index.ts`? |  |  |
| Is this page reachable through a compatibility route or alias? |  |  |
| Is this page represented by `MenuConfig.ts`? |  |  |
| Is this page an intentional hidden route, blank page, detail page, or special shell? |  |  |
| Is this page referenced by layout tabs, page registries, or generated page config? |  |  |
| Is this page referenced by docs, runtime string links, or examples that are still expected to work? |  |  |

If any answer above is `Yes`, the page is not automatically redundant. Continue classification, but do not archive until the reference has a successor or explicit retention decision.

## Functional Coverage Checks

| Check | Yes/No | Evidence |
|---|---|---|
| Does this page provide a workflow not covered by the canonical route page? |  |  |
| Does this page provide a visible business-domain capability for market/data/watchlist/strategy/trade/risk/system/ai? |  |  |
| Does this page contain selector behavior, tab orchestration, or cross-slice state that the canonical page still lacks? |  |  |
| Does this page contain domain calculation rules for market, strategy, trading, risk, or system state? |  |  |
| Does this page preserve compatibility behavior for existing tests, docs, or historical links? |  |  |

If any answer above is `Yes`, classify as `absorb-assets`, `compat-retained`, or `candidate-review`, not `archive-candidate`.

## Reusable Asset Checks

| Asset class | Present? | Absorption target / rationale |
|---|---|---|
| Reusable UI component |  |  |
| Shared composable or API normalization |  |  |
| Request provenance, freshness, or runtime-status logic |  |  |
| Metric cards, KPI grid, stats strip, or summary logic |  |  |
| Table columns, filters, selectors, or query schema |  |  |
| Domain calculation rule |  |  |

If any asset is present, it must be absorbed into a canonical page/shared layer or explicitly rejected with rationale before archive.

## Guard And Test Checks

Discovery commands:

```bash
rg -n "<page-path>|<page-basename>|<directory-name>" web/frontend/tests web/frontend/src --glob '!**/.claude/**'
find web/frontend -type f -name '*mainline-gate*.spec.ts' -print
```

Record every matching guard or spec file in the evidence column. Do not answer `No` unless the search command and search terms are recorded.

| Check | Yes/No | Evidence |
|---|---|---|
| Is the page or directory referenced by `*-mainline-gate.spec.ts`? |  |  |
| Is the page imported or read by any `*.spec.ts` file? |  |  |
| Does a test assert this page's style source, class cleanup, route path, or runtime behavior? |  |  |
| Has the relevant test guard been migrated to the canonical successor? |  |  |
| If the guard is retired, is the retirement rationale recorded? |  |  |

Guarded pages cannot become `archive-candidate` until the guard is migrated or explicitly retired.

## Successor Decision

| Field | Value |
|---|---|
| Canonical successor page |  |
| Successor covers all useful functionality? | `Yes` / `No` |
| Missing functionality to absorb |  |
| No-successor-needed rationale |  |

Every `archive-candidate` must have either a canonical successor or a `no-successor-needed` rationale.

## Redundant Eligibility Gate

A page is eligible for redundant cleanup only if all conditions are true:

| Required condition | Pass/Fail | Evidence |
|---|---|---|
| Not part of active routed-page baseline |  |  |
| Not represented by visible menu |  |  |
| Not an intentional hidden route or special shell |  |  |
| Provides no unique business-domain function coverage |  |  |
| All useful assets absorbed or explicitly rejected |  |  |
| No active static import reference |  |  |
| No active dynamic import reference |  |  |
| No layout tab or page registry reference |  |  |
| No page-config reference |  |  |
| No documentation or example link that is still expected to work |  |  |
| No runtime string-link or feature-flag reference |  |  |
| No test guard or spec reference, or guard migration/retirement is recorded |  |  |
| Successor or `no-successor-needed` rationale recorded |  |  |

If any condition fails, the page is not redundant and must not be archived as redundant.

## Final Decision

| Lifecycle decision | Select one |
|---|---|
| Keep as canonical or special page |  |
| Keep as `compat-retained` |  |
| Mark `absorb-assets` |  |
| Mark `experimental` |  |
| Mark `archive-candidate` |  |

| Execution action | Value |
|---|---|
| No action needed |  |
| Needs asset absorption batch |  |
| Needs guard/test migration batch |  |
| Scheduled for approved archive batch |  |
| Archive batch ID / approval reference |  |

## Archive Target

| Lifecycle / evidence | Target | When to use |
|---|---|---|
| `experimental` with lab/reference value | `views/archive/experimental/` | Lab or experimental pages preserved for reference |
| `archive-candidate` with canonical successor | `views/archive/replaced/` | Fully replaced business pages with documented successors |
| Demo/sample-only evidence and no production role | `views/archive/demo/` | Demo or sample-only views with no production role |
| Legacy migration remnant or old naming surface | `views/archive/legacy/` | Historical compatibility or migration remnants with no remaining hidden reference |

Archive is isolation, not physical deletion.

## Rollback Procedure

If a hidden reference is discovered after an archive move:

1. Restore the page to its original path.
2. Reclassify it as `compat-retained`.
3. Record the hidden reference source.
4. Re-run the guard/test discovery step.
5. Do not retry archive until the reference is migrated or explicitly retired.
