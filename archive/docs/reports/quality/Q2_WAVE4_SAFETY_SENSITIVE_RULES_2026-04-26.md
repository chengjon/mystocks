# Q2 Wave 4 Safety-Sensitive Rules

Date: 2026-04-26
Wave: `Wave 4 / Function Tree Evidence Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/FUNCTION_TREE.md`
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`

## Purpose

This note closes Wave 4 Batch 2 by making the stricter rule for safety-sensitive nodes explicit.

## Safety-Sensitive Nodes

For function-tree interpretation, a node should be treated as safety-sensitive when it involves:

- funds movement
- position change
- pre-execution risk decisions
- live trading execution claims
- production-grade realtime path claims that affect trading decisions

## Rule

For safety-sensitive nodes:

- implementation evidence alone is never enough for `✅`
- UI presence alone is never enough for `✅`
- modeled domain logic alone is never enough for `✅`
- production-usable wording must be blocked if the relevant safety contract remains unresolved

## Current Q2 Application

Domain 05 should remain conservatively interpreted.

Execution-capable trading paths may exist, but current Q2 closure evidence still requires them to be read as `experimental` or `in-progress`, not `production-eligible`.
