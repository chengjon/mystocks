# Frontend View Governance 2.5 Business Domain Router/Menu Coverage Disposition

Date: 2026-05-12
Change: `update-frontend-view-governance`
Task: `2.5 Verify formal business-domain directory coverage against menu and router truth.`

## Decision

Close task 2.5 as a read-only router/menu coverage ledger. The formal routed business-domain baseline remains the seven current main business domains documented in `docs/guides/frontend-structure.md` and checked by the domain audit records:

- `market`
- `data`
- `watchlist`
- `strategy`
- `trade`
- `risk`
- `system`

The router truth source is `web/frontend/src/router/index.ts`; the main-menu truth source is `web/frontend/src/layouts/MenuConfig.ts`. This record does not modify either file.

## Coverage Ledger

| Domain / route group | Coverage result | Disposition |
| --- | --- | --- |
| `market` | Covered by market checklist. Active canonical pages, compatibility wrappers, local helpers, and legacy static shells are separated. | Active market route owners and support assets are excluded from archive flow. |
| `data` | Covered by data checklist. Active data route owners and helper modules are current canonical support. | Data directory is formal business-domain truth, not a historical ArtDeco residue. |
| `watchlist` | Covered by watchlist checklist. Current watchlist route surfaces are distinguished from stock-screening compatibility assets. | No watchlist directory page is archive-approved by menu/router absence. |
| `strategy` | Covered by strategy checklist. Current `/strategy/*` route wrappers and GPU page are separated from old workbench shells. | Route wrappers remain active entrypoints even when they delegate to ArtDeco or canonical bodies. |
| `trade` | Covered by trade checklist. `/trade/*` canonical pages and `/trade/terminal` special owner are separated from legacy trading shells. | `views/trade/*` is active route truth; `TradingDashboard.vue` remains the terminal exception. |
| `risk` | Covered by risk checklist. `/risk/*` routes, `/risk/pnl` ArtDeco wrapper, and orphan static shells are separated. | Active risk pages and route wrappers are excluded from archive flow. |
| `system` | Covered by system checklist. `/system/*` current route owners and legacy static shells are separated. | Active system pages and their support assets are excluded from archive flow. |
| Special active exceptions | Covered by frontend structure guide and focused checklists: `/dashboard`, `/trade/terminal`, `/login`, 404, `/detail/news/:symbol`, and `/risk/pnl`. | These exceptions are not drift; they are explicit repo-truth exceptions or special routes. |
| Menu-pending routed domains | AI checklist identifies `/ai/*` as router-active but not in the seven-domain sidebar menu. | Menu absence is not archive evidence; product/navigation decision is separate from archive governance. |

## Evidence Inputs

- `docs/guides/frontend-structure.md`
- `docs/reports/quality/myweb-audit/frontend-view-governance-2b-readonly-closeout-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-market-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-data-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-watchlist-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-strategy-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-trade-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-risk-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-system-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-ai-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-blank-errors-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-announcement-2026-05-10.md`

## Boundary

- This record verifies coverage against existing evidence only; it does not rewire menu, router, aliases, page config, or tests.
- A file missing from the seven-domain menu is not automatically dead if `router/index.ts`, a special route, compatibility wrapper, guard, or documented exception still owns it.
- A historical ArtDeco location is not automatically redundant if it is the current route owner or compatibility wrapper.
- Any future domain reshaping still requires a separate approved mutation batch.
