# Phase 5: Composables Disposition - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 05-composables-disposition
**Areas discussed:** Extraction Criteria, tradingDashboardActions Fate, Convention Documentation

---

## Extraction Criteria

| Option | Description | Selected |
|--------|-------------|----------|
| Consumer count only | 2+ consumers → extract, 1 → keep view-local. No exceptions. | |
| Consumer count + role check | 2+ → extract. 1 consumer + domain utility → may extract to appropriate location. 1 + view-specific → keep view-local. | ✓ |
| Role check + growth potential | Same as role check but also consider pre-emptive extraction for files likely to grow consumers. | |

**User's choice:** Consumer count + role check
**Notes:** Default is "don't extract" for single-consumer files. Role check only activates when the file clearly serves a cross-cutting concern (CSRF, shared types, etc.) — and even then, it goes to the appropriate location (api/, utils/), NOT src/composables/.

---

## tradingDashboardActions.ts Fate

| Option | Description | Selected |
|--------|-------------|----------|
| Keep in views/composables/ | 1 consumer (useTradingDashboard.ts), pragmatic, no harm. | ✓ |
| Co-locate with TradingDashboard.vue | Move to views/trading-dashboard/ closer to consumer. | |
| Keep as-is (no move) | Stay where it is, extraction question only arises when second consumer appears. | |

**User's choice:** Keep in views/composables/
**Notes:** It's a transport helper (CSRF + HTTP), not a composable. If a second consumer ever appears, destination should be `src/api/` or feature-local service — NOT `src/composables/`.

---

## useTradingDashboard.ts Disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Keep view-local | 1 consumer (TradingDashboard.vue), view-specific state management. No extraction case. | ✓ |

**User's choice:** Keep view-local (confirmed)

---

## Convention Documentation

| Option | Description | Selected |
|--------|-------------|----------|
| New CONVENTIONS doc | New file in docs/guides/frontend/ with extraction rules and examples. | |
| Extend AUDIT doc | Add conventions section to existing COMPOSABLES-AUDIT.md. | |
| Add to STANDARDS.md | Add composable rules to architecture/STANDARDS.md frontend conventions section. | ✓ |

**User's choice:** Add to STANDARDS.md
**Notes:** STANDARDS.md is the canonical rules file — conventions belong there. COMPOSABLES-AUDIT.md remains as audit evidence (why), STANDARDS.md is the forward rule (how).

---

## Test Co-migration

**Status:** Not discussed — user explicitly deferred as a derived question. Only relevant if extraction is decided. No extraction → no migration needed.

---

## Claude's Discretion

- Exact wording of STANDARDS.md addition
- Whether to add examples in the STANDARDS.md entry
- Whether to update COMPOSABLES-AUDIT.md with a "Final Disposition" section

## Deferred Ideas

- Renaming tradingDashboardActions.ts to reflect its actual role (transport, not composable)
- Pre-emptive extraction of any view-local composable based on growth potential
