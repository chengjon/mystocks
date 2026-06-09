# Frontend View Governance 2b Read-Only Closeout

Date: 2026-05-11

Scope: `openspec/changes/update-frontend-view-governance` section `2b` read-only checklist evidence.

This closeout summarizes the current evidence state and defines the stop condition for further read-only expansion. It does not approve any archive move, deletion, route change, test retirement, or Vue refactor.

## Measured Coverage Snapshot

Commands:

```bash
find web/frontend/src/views -type f | wc -l
find web/frontend/src/views/artdeco-pages -type f | wc -l
find web/frontend/src/views -path '*/artdeco-pages/*' -prune -o -type f -print | wc -l
find docs/reports/quality/myweb-audit -maxdepth 1 -type f -name 'frontend-view-checklist-*.md' | sort | wc -l
```

Results:

| Scope | Count |
| --- | ---: |
| All current `views/**` files | 566 |
| `views/artdeco-pages/**` files | 186 |
| Non-ArtDeco `views/**` files | 380 |
| Current checklist evidence docs | 49 |

Interpretation:

- ArtDeco files are covered by the ArtDeco subtree rollup and supporting sub-batch checklists.
- Non-ArtDeco files are covered by domain checklists, root legacy checklists, blank/error checklists, demo/example checklists, support-layer checklists, root demo/sidecar checklist, and the exact-path delta.
- The previous 108-path exact-match gap was a documentation granularity gap, not a newly discovered runtime ownership gap.

## Evidence Families Covered

| Family | Evidence docs | Current result |
| --- | --- | --- |
| Canonical business domains | `market`, `data`, `watchlist`, `strategy`, `trade`, `risk`, `system`, plus `ai`, `announcement`, `advanced-analysis`, `technical`, `stocks`, `settings`, `monitoring` checklists | Active route owners excluded from archive flow; legacy shells remain candidate-review only |
| Blank/special routes | blank/errors checklist | `/login`, 404, and `/trade/terminal` are special route truth or separately covered active route truth |
| Root legacy pages | top-level legacy checklist, root demo/sidecar checklist | Compatibility wrappers/static shells remain retained or candidate-review, not archive-approved |
| Demo/example assets | demo-directory, demo-examples, root demo/sidecar checklist | Demo trees require parent-shell decisions and guard retirement before movement |
| Support assets | `views/components`, `views/composables`, `views/styles`, exact-path delta | Tests, styles, configs, helpers, and data assets inherit owner lifecycle; no bulk extraction/archive |
| ArtDeco subtree | ArtDeco sub-batches and rollup | 186 files covered; no ArtDeco file is archive-approved by read-only evidence |
| Guard and sidecar assets | local-test checklists, exact-path delta, root sidecar checklist | Tests and agent sidecars are not redundant pages; handle under owning lifecycle or tooling hygiene |

## Current Archive Decision

No file is `archive-approved` from section `2b`.

This is intentional. The approved governance rule requires both:

- Code-path proof: no route, menu, dynamic import, test, style, config, docs, guard, or runtime-string dependency remains.
- Function-tree proof: the asset is formally redundant or retired, with successor or `no-successor-needed` rationale.

The 2b evidence set is enough to support future decisions, but it deliberately stops short of performing those decisions.

## Stop Condition For Further Read-Only Expansion

Further checklist expansion should stop unless a new file appears or a specific mutation candidate is selected.

Reasons:

- Current checklist count is already 49 documents for 566 `views/**` files.
- Remaining “gaps” are mostly exact wording/path granularity, not unclassified runtime risk.
- More generic checklist documents would increase governance noise and make later mutation batches harder to review.
- The next useful work is to choose a narrow mutation batch, then validate only the affected owners, guards, and successors.

## Recommended Next Mutation Batch Choices

Choose one narrow batch before entering section `3`.

| Option | Scope | Why it is a good first mutation candidate | Required gates |
| --- | --- | --- | --- |
| A. Root demo/test sandbox triage | Root demo/test pages such as `MinimalTest.vue`, `Test.vue`, `ArtDecoTest.vue`, `KLineDemo.vue`, `PageTitleDemo.vue` | High likelihood of true demo/test redundancy, isolated from canonical business routes | Guard-map check, direct source search, successor/no-successor rationale, targeted Vitest/style guards |
| B. Error demo shell decision | `views/errors/*` | Small, bounded, no current route owner; clear choice between formal error routes or archive | Error route contract decision, style guard retirement/migration, blank-layout smoke |
| C. Monitoring legacy functional absorption | `views/monitoring/{AlertRulesManagement,RiskDashboard,WatchlistManagement}.vue` and local support | Potential reusable assets for risk/watchlist/system canonical pages | Asset absorption matrix, API/composable comparison, tests migrated before archive |
| D. Root style residual cleanup plan | `views/styles/*` residual/test-guarded styles | Many files likely lifecycle-tied to root legacy pages; cleanup can reduce style debt | Owner-by-owner import check, style-source spec updates, ArtDeco lint changed-scope gate |

Recommendation: start with Option A or B. They are smaller and less likely to affect canonical business flows. Option C has higher product value but needs more careful asset absorption. Option D is best after root page lifecycle decisions are fixed.

## Section 3 Entry Criteria

Before any mutation batch:

- Pick one option and list exact files.
- For each file, record lifecycle status, successor or `no-successor-needed`, and guard/test references.
- Run GitNexus impact analysis if runtime code symbols are edited.
- Update or retire tests in the same batch as any file move.
- Run the targeted validation suite and report actual results.
- Keep OpenSpec validation passing.

## Closeout Conclusion

Section `2b` has reached a practical read-only closeout point. The project now has enough evidence to avoid accidental deletion and enough classification to choose controlled cleanup batches. Continuing to expand broad checklist coverage would create diminishing returns; the next productive step is a user-approved, narrow section `3` mutation batch.
