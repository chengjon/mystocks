# Frontend View Checklist: `views/artdeco-pages/{market,ml-tabs,risk,trade}/`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/market/`, `web/frontend/src/views/artdeco-pages/ml-tabs/`, `web/frontend/src/views/artdeco-pages/risk/`, and `web/frontend/src/views/artdeco-pages/trade/`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `views/artdeco-pages/market/` | empty directory | none | no files found | directory exists only; no file-level guard evidence | `empty-placeholder-directory/artdeco-market` | `not-archive-approved` |
| `views/artdeco-pages/ml-tabs/` | empty directory | none | no files found | directory exists only; no file-level guard evidence | `empty-placeholder-directory/artdeco-ml-tabs` | `not-archive-approved` |
| `views/artdeco-pages/risk/` | empty directory | none | no files found | directory exists only; no file-level guard evidence | `empty-placeholder-directory/artdeco-risk` | `not-archive-approved` |
| `views/artdeco-pages/trade/` | empty directory | none | no files found | directory exists only; no file-level guard evidence | `empty-placeholder-directory/artdeco-trade` | `not-archive-approved` |

## Evidence

- `find web/frontend/src/views/artdeco-pages/market -maxdepth 2 -type f -print` returned no files.
- `find web/frontend/src/views/artdeco-pages/ml-tabs -maxdepth 2 -type f -print` returned no files.
- `find web/frontend/src/views/artdeco-pages/risk -maxdepth 2 -type f -print` returned no files.
- `find web/frontend/src/views/artdeco-pages/trade -maxdepth 2 -type f -print` returned no files.
- `ls -la` shows all four directories exist, but each contains only `.` and `..`.
- Current market route truth is under `web/frontend/src/views/market/*`, plus reviewed ArtDeco compatibility wrappers under `market-tabs/*` and `market-data-tabs/*`.
- Current AI/ML route truth is under `web/frontend/src/views/ai/MlWorkbench.vue` and its local AI composables/tests, not `artdeco-pages/ml-tabs/`.
- Current risk route truth is under `web/frontend/src/views/risk/*`, plus reviewed ArtDeco compatibility/support assets under `risk-tabs/*`.
- Current trade route truth is under `web/frontend/src/views/trade/*` and `TradingDashboard.vue`, plus reviewed ArtDeco compatibility/support assets under `trading-tabs/*` and the retained `ArtDecoTradingManagement.vue` shell.

## Functional Asset Assessment

- There are no Vue, TypeScript, SCSS, test, or helper files inside either directory, so there is no reusable page asset to absorb.
- These directories do not create active menu or route surfaces by themselves.
- Empty directory cleanup is still a structural mutation. It should not be inferred from redundant-page review because Git does not normally track empty directories, and local filesystem state may differ across worktrees.
- If a future mutation batch removes these directories from the working tree, it should be documented as directory hygiene, not page archive.

## Redundant Page Decision

No file in this batch is archive-approved because there are no files in scope.

- Do not count these directories as unresolved page assets.
- Do not treat this checklist as approval to remove parent ArtDeco directories or reviewed sibling directories.
- If directory removal is desired later, handle it as a separate approved housekeeping action after confirming no `.gitkeep`, build script, generator, or documentation contract expects the path.

## Follow-Up Notes

- Continue remaining ArtDeco review with test/support subdirectories if needed; the direct `risk/` and `trade/` placeholder directories have no file-level assets.
- Keep `market-tabs/*` and `market-data-tabs/*` conclusions separate from this empty-directory note; those sibling directories already have their own checklists and contain active compatibility/support assets.
- Keep `risk-tabs/*` and `trading-tabs/*` conclusions separate from this empty-directory note; those sibling directories already have their own checklists and contain active compatibility/support assets.
- Keep canonical ML governance tied to the AI-domain ML workbench unless a future approved proposal reintroduces ArtDeco ML tabs.
