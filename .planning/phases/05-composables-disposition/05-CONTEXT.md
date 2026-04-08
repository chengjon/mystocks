# Phase 5: Composables Disposition - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Resolve STRU-04 by making evidence-based decisions on the 2 extraction candidates from COMPOSABLES-AUDIT.md, accept view-local as the canonical pattern for 15/17 composables, and document the convention as a lasting project rule. No new capabilities — only classification decisions, potential file moves, and convention documentation.

</domain>

<decisions>
## Implementation Decisions

### Extraction Criteria
- **D-01:** Extraction rule is **role-first, then consumer count** (role check takes priority over consumer count):
  1. **Role gate (first):** Is the file actually a composable (reactive state + Vue lifecycle)? If NO, it does NOT belong in `src/composables/` regardless of consumer count. Route by role: transport helpers → `src/api/` or feature-local `helpers/`; shared types → `types/`; utilities → `utils/`.
  2. **Consumer count (second, for true composables only):** 2+ consumers → extract to `src/composables/`. 1 consumer + view-specific logic → keep view-local.
  3. **Single-consumer domain utility:** A file with 1 consumer that clearly serves a cross-cutting domain role (CSRF, auth, shared types) may be pre-emptively extracted to its role-appropriate location — but NOT to `src/composables/`.
- **D-02:** No pre-emptive extraction based on "growth potential" or "might be reused later" — extract only when a second consumer actually exists or the file provably serves a cross-cutting domain role

### Individual Composable Dispositions
- **D-03:** `useTradingDashboard.ts` → **keep view-local**. Single consumer (TradingDashboard.vue), view-specific state management, no shared-domain role. No extraction case.
- **D-04:** `tradingDashboardActions.ts` → **keep in `views/composables/` as an audited exception with documented naming debt**. Per D-01 role gate, this file is NOT a composable — it is a transport/helper layer (CSRF token resolution, HTTP post/delete wrappers). It stays in `views/composables/` solely because: (a) it has exactly 1 consumer, (b) moving it provides no functional benefit, (c) the move cost exceeds the semantic purity gain. **Naming debt:** This file should be flagged as "misnamed — not a composable" in COMPOSABLES-AUDIT.md so future contributors do not infer that transport helpers in composables/ directories is an accepted pattern. If a second consumer ever appears, relocate to `src/api/` or a feature-local `helpers/` — per D-01 role gate, NOT `src/composables/`.

### View-Local Pattern Documentation
- **D-05:** Document the view-local convention in `architecture/STANDARDS.md` (frontend conventions section) as the canonical project rule. This is the project's authoritative rules file and the right place for lasting conventions.
- **D-06:** The convention rule: "Role-first, then consumer count. (1) Files that are not composables (no reactive state / Vue lifecycle) do NOT go in `src/composables/` — route by role. (2) True composables with a single consumer are co-located with their view via `./composables/` relative imports — this is idiomatic Vue and the canonical pattern. (3) Extraction to `src/composables/` requires 2+ consumers."
- **D-07:** COMPOSABLES-AUDIT.md remains as the audit evidence document (why these decisions were made). STANDARDS.md is the forward-looking rule (how to decide in the future).

### Claude's Discretion
- Exact wording of the STANDARDS.md addition
- Whether to add examples in the STANDARDS.md entry (e.g., "useTradingDashboard.ts → 1 consumer → keep view-local")
- Whether to update COMPOSABLES-AUDIT.md with a "Final Disposition" section or leave it as-is

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Composables audit
- `web/frontend/COMPOSABLES-AUDIT.md` — Full inventory of 17 composables, consumer analysis, extraction candidates
- `web/frontend/MIGRATION_PROGRESS.md` — Original classification (15/17 view-local, 2 extraction candidates)

### Project governance
- `architecture/STANDARDS.md` — Canonical rules file; target location for view-local convention documentation
- `.planning/phases/03-structural-consolidation/03-CONTEXT.md` — D-11 through D-14 (original composable audit decisions from Phase 3)

### Extraction candidates (the 2 files under decision)
- `web/frontend/src/views/composables/useTradingDashboard.ts` — 14KB, view-specific composable with state/actions
- `web/frontend/src/views/composables/tradingDashboardActions.ts` — 1.8KB, HTTP transport layer (CSRF + API calls)

### Existing shared composables (for reference)
- `web/frontend/src/composables/` — ~35 shared composables (useMarket, useWebSocket, useTrading, etc.)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/composables/` already exists with ~35 shared composables — the shared location is established
- `COMPOSABLES-AUDIT.md` provides complete consumer inventory — no need to re-grep

### Established Patterns
- Views use relative imports: `import { useXxx } from './composables/useXxx'` — idiomatic Vue co-location
- `src/composables/` contains composables consumed by 2+ views via `@/composables/xxx` alias imports
- Phase 3 already decided: bulk move breaks 15+ imports, per-file migration only

### Integration Points
- `architecture/STANDARDS.md` — frontend conventions section is where the rule gets added
- No import changes needed in this phase (both candidates stay in place)

</code_context>

<specifics>
## Specific Ideas

- Audit documents explain "why these decisions"; STANDARDS.md defines "the rule going forward" — both are needed but serve different purposes
- tradingDashboardActions.ts is an audited exception: not a composable, but kept in views/composables/ for pragmatic reasons (1 consumer, no functional gain from moving). It MUST be flagged as naming debt so the convention rule is not undermined by its presence. If a second consumer appears, relocate to `src/api/` per D-01 role gate — never `src/composables/`

</specifics>

<deferred>
## Deferred Ideas

- Test co-migration (only relevant if extraction happens — no extraction decided, so no action needed)
- Renaming tradingDashboardActions.ts to reflect its actual role (transport, not composable) — cosmetic, not blocking
- Pre-emptive extraction of any view-local composable based on growth potential — out of scope per D-02

</deferred>

---

*Phase: 05-composables-disposition*
*Context gathered: 2026-04-08*
