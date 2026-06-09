# B4.001 Frontend Route/UI Dirty Atlas

Date: 2026-06-06
Mode: `no-source`
Branch: `wip/root-dirty-20260403`
HEAD: `a9bcb8b50`

## Scope

This node starts B4 after the B3 OpenSpec governance bucket was closed.

Scope is read-only classification of dirty files under `web/frontend/**`, with emphasis on route/UI files, route contracts, route-header leftovers, tests, shared UI components, styles, state/API helpers, and frontend runtime/config files.

No frontend source, test, style, asset, or route file was edited. No file was staged.

## Governing Inputs

- `architecture/STANDARDS.md`
  - Same-domain `no-source` inventory may be batched.
  - `source-authorized` implementation must be split by risk.
  - Deletion/retirement must be separately authorized.
- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
  - B4 is `Frontend route/UI dirty`.
  - Frontend route/layout source work requires route/layout gates.
  - Route-header leftovers must not be mixed into unrelated cleanup commits.
  - OPENDOG is advisory and does not replace Git, tests, GitNexus, or user approval.
- `docs/reports/worklogs/claude-auto/route-header-migration-line-handoff-2026-06-05.md`
  - Preserve route-header handoff boundaries.
  - Do not revert existing dirty leftovers in `Concepts.vue`, `Industry.vue`, or related route files without explicit authorization.
  - If the route-header line resumes later, recommended next route is `/data/fund-flow` via `web/frontend/src/views/data/FundFlow.vue`.

## OPENDOG Preflight

OPENDOG was run before broad B4 exploration:

- `agent-guidance --project mystocks --top 5 --json`: returned guidance successfully.
- `verification --id mystocks --json`: verification evidence exists but is stale.
- `stats --id mystocks --path-classification source`: returned project stats.
- `unused --id mystocks --path-classification source`: returned unused-file candidates.

Disposition: stale OPENDOG verification does not block this no-source inventory, but it blocks risky cleanup/source work until fresh verification evidence is recorded or the stale-evidence caveat is explicitly accepted.

## Refreshed Dirty Count

The guide's B4 count was a 2026-06-05 snapshot. Current `git status --porcelain=v1 -z` shows:

| Scope | Count |
|---|---:|
| Total dirty entries in worktree | 1305 |
| Dirty entries under `web/frontend/**` | 340 |
| Non-deletion frontend entries | 312 |
| Frontend deletion entries | 28 |

This reconciles the operator-stated B4 `312` count as the current non-deletion frontend route/UI dirty set. The additional 28 entries are deletion-retirement candidates and must be handled under a separate deletion/retirement authority.

Frontend status breakdown:

| Status | Count |
|---|---:|
| Modified | 241 |
| Deleted | 28 |
| Untracked | 71 |

## Domain Breakdown

| Domain | Total | Modified | Deleted | Untracked | Initial disposition |
|---|---:|---:|---:|---:|---|
| `views/artdeco-pages` | 68 | 50 | 0 | 18 | Route/UI source-authorized slice |
| `tests/unit` | 36 | 19 | 4 | 13 | Deletion preflight first for deleted tests; remaining tests need test-authorized pairing |
| `views/root-legacy-vue` | 31 | 30 | 1 | Deletion preflight first for deleted page; remaining modified pages need route/UI slices |
| `views/strategy` | 22 | 10 | 4 | 8 | Deletion preflight first; then strategy route/UI slice |
| `views/system` | 19 | 12 | 0 | 7 | System route/UI slice |
| `other-frontend` | 17 | 17 | 0 | 0 | Classify separately before source work |
| `views/advanced-analysis` | 14 | 13 | 0 | 1 | Route/UI slice |
| `views/market` | 14 | 10 | 2 | 2 | Deletion preflight first; route-header handoff applies to selected market/data pages |
| `views/risk` | 9 | 7 | 0 | 2 | Risk route/UI slice |
| `components/artdeco` | 8 | 4 | 0 | 4 | Shared ArtDeco UI slice |
| `tests/component-or-node` | 8 | 5 | 0 | 3 | Test-authorized, pair with source behavior where possible |
| `views/stocks` | 8 | 8 | 0 | 0 | Route/UI slice |
| `views/composables` | 7 | 2 | 5 | 0 | Deletion preflight first |
| `tests/e2e` | 7 | 6 | 0 | 1 | E2E test-authorized slice |
| `views/stock-analysis` | 6 | 0 | 6 | 0 | Deletion-retirement preflight |
| `views/styles` | 6 | 0 | 6 | 0 | Deletion-retirement preflight |
| `components/market` | 5 | 5 | 0 | 0 | Shared market UI component slice |
| `utils-adapters` | 5 | 5 | 0 | 0 | Classify with state/API behavior before source work |
| `views/trade-management` | 5 | 5 | 0 | 0 | Trade route/UI slice |
| `views/trade` | 5 | 3 | 0 | 2 | Trade route/UI slice |
| `views/trading-decision` | 5 | 4 | 0 | 1 | Trading decision route/UI slice |
| `views/trading` | 5 | 4 | 0 | 1 | Trading route/UI slice |
| `views/data` | 4 | 3 | 0 | 1 | Data route/UI slice; route-header handoff applies |
| `views/settings` | 4 | 4 | 0 | 0 | Settings route/UI slice |
| `state/composables` | 3 | 3 | 0 | 0 | State/composable source slice |
| `layout` | 3 | 3 | 0 | 0 | Layout source slice; route/layout gates required |
| `views/announcement` | 3 | 2 | 0 | 1 | Announcement route/UI slice |
| `views/watchlist` | 3 | 1 | 0 | 2 | Watchlist route/UI slice |
| `public-assets` | 2 | 2 | 0 | 0 | Asset/runtime preflight before source work |
| `state/stores` | 2 | 2 | 0 | 0 | Store/source contract slice |
| `views/technical` | 2 | 1 | 0 | 1 | Technical route/UI slice |
| `frontend-docs` | 2 | 0 | 0 | 2 | Docs/no-source preserve or docs-authorized |
| `state/api` | 1 | 1 | 0 | 0 | API contract source slice |
| `views/__tests__` | 1 | 0 | 0 | 1 | Test-authorized or route-paired |

## Risk Buckets

### B4-D0 Deletion-Retirement Candidates

Count: 28 deleted frontend entries.

These must not be treated as normal frontend cleanup. Before deletion acceptance, each group needs:

- route/router/menu lookup
- import/reference scan
- test coverage or route smoke relevance check
- user approval for deletion-retirement authority
- separate staged allowlist and GitNexus detection

Initial domains requiring deletion preflight:

- `tests/unit`
- `views/root-legacy-vue`
- `views/strategy`
- `views/market`
- `views/composables`
- `views/stock-analysis`
- `views/styles`

### B4-RH Route-Header Handoff Preservation

Do not mix route-header migration continuation with general dirty cleanup.

Handoff-sensitive files/areas include:

- `web/frontend/src/views/data/Concepts.vue`
- `web/frontend/src/views/data/Industry.vue`
- `web/frontend/src/views/market/LHB.vue`
- potential next route-header slice: `web/frontend/src/views/data/FundFlow.vue`

Any route-header continuation needs its own source-authorized route-header package and route-specific verification.

### B4-R1 Active Route Pages

Candidate source-authorized route/UI slices after deletion candidates are isolated:

1. `views/data` and route-header-adjacent market/data pages.
2. `views/market`.
3. `views/system`.
4. `views/risk`.
5. `views/strategy`.
6. `views/trade`, `views/trading`, `views/trading-decision`, `views/trade-management`.
7. `views/watchlist`, `views/announcement`, `views/technical`.
8. `views/artdeco-pages` only after router truth is checked; do not assume `artdeco-pages/` is canonical unless `web/frontend/src/router/index.ts` points there.
9. `views/root-legacy-vue` only after active route truth is checked.

### B4-C Shared UI / Layout / Assets

Candidate source-authorized slices:

- `components/artdeco`
- `components/market`
- `layout`
- `public-assets`

These should not be mixed with route-page changes unless a route explicitly depends on the shared component behavior being repaired.

### B4-S State / API / Composable Support

Candidate source-authorized slices:

- `state/api`
- `state/stores`
- `state/composables`
- `utils-adapters`

These need API/render contract checks before route UI work consumes them.

### B4-T Frontend Tests

Candidate test-authorized slices:

- `tests/unit`
- `tests/e2e`
- `tests/component-or-node`
- `views/__tests__`

Pair tests with the source behavior they verify unless they are purely harness/config cleanup.

### B4-O Other Frontend Runtime/Config

`other-frontend` includes `.omc` state, frontend task files, package/config files, and runtime public files. These need a separate classification pass before any source or cleanup package.

### B4-DOC Frontend Docs

`web/frontend/docs/worklogs/**` entries are docs/no-source preserve candidates. They are not route/UI implementation work.

## Proposed Cleanup Queue

| Queue | Mode | Purpose | Gate before source work |
|---|---|---|---|
| B4.002 deletion candidate inventory | `no-source` | Expand the 28 deleted frontend entries into route/import/test evidence and deletion-retirement candidates | No source edits; no staging |
| B4.003 route-header residue preflight | `no-source` | Reconcile route-header handoff-sensitive dirty files and decide whether to resume route-header migration or preserve | Route/header handoff review |
| B4.004 data/market route package preflight | `no-source` | Split data/market dirty into route-header vs ordinary route/UI changes | Router truth and route-specific test list |
| B4.005 system/risk route package preflight | `no-source` | Group lower-deletion active route pages for first source-authorized route/UI package | route config/static tests |
| B4.006 strategy/trade route package preflight | `no-source` | Separate high-volume strategy/trade route changes from deleted candidates and tests | route/API contract and affected tests |
| B4.007 ArtDeco/root legacy route truth preflight | `no-source` | Check which `artdeco-pages/` and root legacy Vue files are actively routed | router truth before editing |
| B4.008 shared UI/component preflight | `no-source` | Group shared component/layout/style/assets and decide route coupling | component tests or route consumers |
| B4.009 frontend state/API support preflight | `no-source` | Classify state/composable/API/utils files before route pages consume them | API/render contract checks |
| B4.010 frontend tests preflight | `no-source` | Pair unit/e2e/node tests with source domains or mark test-only | affected test command list |
| B4.011 other frontend config/docs preflight | `no-source` | Classify `.omc`, task docs, package/config/public/docs files | docs/config/runtime authority decision |

## Required Gates For Later Source-Authorized Frontend Packages

For any future source-authorized route/UI package:

- stage explicit pathspecs only
- `git diff --cached --name-status`
- `git diff --cached --check`
- GitNexus staged detection with fresh index
- route/router truth check against `web/frontend/src/router/index.ts`
- route-specific static/config test where applicable
- frontend syntax/type gate against current baseline
- PM2 status if route is exercised
- actual E2E or smoke result with command, browser/project, and pass/fail/skip counts

## Current No-Source Closeout

- No frontend source/resource/test file was edited.
- No frontend file was staged.
- This report is a governance artifact for the B4 queue and should remain separate from source-authorized route/UI commits.
