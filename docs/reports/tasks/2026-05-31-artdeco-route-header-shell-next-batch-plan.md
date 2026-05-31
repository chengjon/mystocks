# ArtDeco Route Header Shell Next Batch Plan

Date: 2026-05-31

Purpose: identify the next safe batch for ArtDeco route header shell migration after the completed trade execution and trade reconciliation closeouts.

This is a planning and coverage document only. It does not authorize code changes by itself.

## Governance Position

OpenSpec:

- No new OpenSpec proposal is required for this document because it is a docs-only candidate plan.
- Future page migrations remain implementation work under the existing route-header-shell governance pattern.
- If a future task changes router ownership, API contracts, frontend API clients, route aliases, redirects, or shared page architecture, it must stop and use an explicit OpenSpec/Function Tree scope before implementation.

Function Tree:

- Current gate status at planning time: `active gates: none`.
- Each future page migration should create its own Function Tree node.
- Each node should keep the same route-header-shell-only boundary unless explicitly approved otherwise.

GitNexus:

- Future index refreshes must use local `gitnexus analyze`.
- Do not use `npx gitnexus analyze`.

## Current Completed Ledger

Already migrated and closed:

| Route | Page file | Status |
|---|---|---|
| `/trade/positions` | `web/frontend/src/views/trade/Center.vue` | migrated |
| `/trade/portfolio` | `web/frontend/src/views/trade/Portfolio.vue` | migrated |
| `/risk/alerts` | `web/frontend/src/views/risk/Alerts.vue` | migrated |
| `/market/realtime` | `web/frontend/src/views/market/Realtime.vue` | migrated |
| `/trade/execution` | `web/frontend/src/views/trade/Execution.vue` | migrated |
| `/trade/reconciliation` | `web/frontend/src/views/trade/Reconciliation.vue` | migrated |

Canonical ledger source:

- `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`

Ledger hygiene note:

- `/trade/positions` is routed to `web/frontend/src/views/trade/Center.vue` in `web/frontend/src/router/index.ts`.
- The route header shell rules ledger should use that active router file path, not a stale `Positions.vue` path.

## Scan Method

The scan inspected:

- routed Vue pages under `web/frontend/src/views/`
- direct `ArtDecoHeader` usage
- existing `ArtDecoRouteHeader` usage
- route header test hooks such as `*-header`
- E2E references under `web/frontend/tests/e2e/`
- router truth from `web/frontend/src/router/index.ts`

This scan is a prioritization aid. Before each implementation, rerun the local preflight because the worktree is active and other agents may change route files or tests.

## Batch A: Ready Next

These pages match the proven pattern: routed page, local `ArtDecoHeader`, stable header test hook, and existing E2E coverage.

| Priority | Route | Page file | Header hook | E2E anchor | Recommendation |
|---|---|---|---|---|---|
| A1 | `/trade/signals` | `web/frontend/src/views/trade/Signals.vue` | `trade-signals-header` | `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts` | Migrate next |

Why `/trade/signals` should be next:

- It is in the same trade domain as the last four migrated trade pages.
- It has an existing route-level E2E test: `Trade-Signals renders mocked signal execution workspace`.
- It already exposes `trade-signals-header`, which can receive the same RED/GREEN `artdeco-route-header` assertion.
- The scope can stay narrow: header shell only, no signal semantics, no execution history semantics, no review lens or trust strip extraction.

Suggested next Function Tree node:

```text
route-header-shell-trade-signals
```

Suggested focused E2E gate:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals renders mocked signal execution workspace" --project=chromium
```

Non-goals for `/trade/signals`:

- do not modify router paths or route metadata
- do not modify backend API contracts or frontend API clients
- do not change signal confidence, review lens, trust strip, execution history, provenance, pending, failed-first-load, or mock-data semantics
- do not extract shared signal business components

## Batch B: Header Shell Candidate, Needs Shape Or Test Hardening

These pages have route-level header hooks and E2E coverage, but they do not currently follow the same local `ArtDecoHeader` pattern. Treat them as second-wave candidates because the migration may require a small shape review before code changes.

| Priority | Route | Page file | Header hook | Current shape | E2E anchor | Recommendation |
|---|---|---|---|---|---|---|
| B1 | `/ai/sentiment` | `web/frontend/src/views/ai/Sentiment.vue` | `ai-sentiment-header` | custom header, no direct `ArtDecoHeader` | `web/frontend/tests/e2e/ai-sentiment-workbench.spec.ts` | shape first |
| B2 | `/ai/batch` | `web/frontend/src/views/ai/BatchAnalysis.vue` | `ai-batch-header` | custom header, no direct `ArtDecoHeader` | `web/frontend/tests/e2e/ai-batch-analysis.spec.ts` | shape first |

Recommended handling:

- Run an impeccable critique or short shape brief before implementation.
- Confirm whether the existing custom header can be wrapped by `ArtDecoRouteHeader` without losing local runtime states.
- Add the same RED/GREEN `artdeco-route-header` assertion only after confirming the route header shell is the correct target.

## Batch C: Needs E2E Hook Or Coverage Before Migration

These routed pages still use local `ArtDecoHeader` or header-like shells, but they either lack a stable `*-header` test hook, lack focused E2E coverage, or have broader domain risk. Do not migrate them until the test anchor is created or confirmed.

| Domain | Routes | Notes |
|---|---|---|
| Market | `/market/technical`, `/market/lhb` | local ArtDeco/header-like pages; add or confirm focused E2E before shell migration |
| Data | `/data/industry`, `/data/concept`, `/data/fund-flow` | sector/fund-flow semantics; avoid changing financial color or data-empty semantics |
| Trade | `/trade/history` | trade ledger semantics; add a dedicated header hook before migration |
| Risk | `/risk/overview`, `/risk/stop-loss`, `/risk/news` | risk severity and alert/news semantics require strict non-goals |
| System | `/system/health`, `/system/api`, `/system/resources`, `/system/data` | operational surfaces; verify PM2/API health assumptions and avoid changing status semantics |

Recommended handling:

1. Add or confirm a stable route-level header test hook.
2. Add a focused E2E assertion for page visibility and existing core content.
3. Only then perform a route-header-shell migration node.

## Excluded Or Deferred Surfaces

Do not treat these as normal route-header-shell candidates without a separate route truth decision:

| Surface | Reason |
|---|---|
| `web/frontend/src/views/artdeco-pages/**` not mapped by router | embedded/legacy ArtDeco surface, not active route truth by default |
| `/dashboard` via `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` | current repo-truth exception; needs separate dashboard-specific shape and route ownership review |
| `web/frontend/src/views/stocks/Screener.vue` | not mapped by the active router scan |
| tab components under `artdeco-pages/*-tabs/` | tab content, not route-level page shell |

## Recommended Execution Order

1. `/trade/signals`
2. `/ai/sentiment` after shape review
3. `/ai/batch` after shape review
4. Market pages with existing or added E2E coverage
5. Data pages with sector/fund-flow semantic guardrails
6. Risk and system pages after focused test anchors are available

## Required Per-Page Gate

Each migration must include:

1. Function Tree node with allowed paths and explicit non-goals.
2. GitNexus impact before editing the page file.
3. RED E2E assertion proving the header lacks `artdeco-route-header`.
4. Minimal `ArtDecoRouteHeader` migration.
5. GREEN focused E2E.
6. Target ESLint.
7. ArtDeco token check.
8. Impeccable JSON check.
9. Type check.
10. Function Tree validate and gate.
11. GitNexus staged scope gate.
12. Implementation commit.
13. Function Tree closeout.
14. Ledger update after closeout.
15. Closeout commit.

## Hard Boundaries

Every future page in this line must preserve:

- same route path
- same router entry
- same page component ownership
- same backend API contract
- same frontend API client
- same runtime state owner
- same domain semantics

Every future page in this line must avoid:

- router path changes
- route aliases
- redirects
- menu rewiring
- parallel ArtDeco routes
- legacy/canonical dual entries
- backend API or OpenAPI changes
- frontend API client changes
- shared business component extraction
- opportunistic page redesign

## Immediate Recommendation

Proceed with `/trade/signals` next.

It is the only remaining scanned page that has all of the following:

- active routed page
- direct local `ArtDecoHeader`
- stable route header test hook
- existing focused E2E coverage
- same trade-domain route grammar as the pages already migrated

This makes it the lowest-risk continuation of the current route header shell line.
