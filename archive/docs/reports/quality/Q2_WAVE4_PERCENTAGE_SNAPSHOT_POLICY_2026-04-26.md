# Q2 Wave 4 Percentage Snapshot Policy

Date: 2026-04-26
Wave: `Wave 4 / Function Tree Evidence Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/FUNCTION_TREE.md`
- `docs/reports/quality/Q2_PHASE_E_FUNCTION_TREE_EVIDENCE_HARDENING_2026-04-25.md`

## Purpose

This note closes Wave 4 Batch 4 by making completion-percentage interpretation explicit.

## Policy

Function-tree completion percentages should be treated as one of two things:

- evidence-backed metrics
- informative managerial snapshots

If no declared calculation model exists, the percentage must be interpreted as a snapshot, not as audited readiness proof.

## Current Q2 Interpretation

Current domain percentages in `FUNCTION_TREE.md` should be interpreted conservatively as snapshots unless a future change defines:

- calculation source
- coverage scope
- validation method
- update cadence

## Hard Non-Claim

Percentages such as `95%`, `85%`, or `70%` must not be read as standalone proof of runtime readiness or production safety.
