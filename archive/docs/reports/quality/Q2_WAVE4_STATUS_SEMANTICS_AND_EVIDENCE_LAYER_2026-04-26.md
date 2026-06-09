# Q2 Wave 4 Status Semantics And Evidence Layer

Date: 2026-04-26
Wave: `Wave 4 / Function Tree Evidence Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/FUNCTION_TREE.md`
- `docs/reports/quality/Q2_PHASE_E_FUNCTION_TREE_EVIDENCE_HARDENING_2026-04-25.md`

## Purpose

This note closes Wave 4 Batch 1 by locking function-tree status semantics to one evidence model.

## Canonical Evidence Layers

Function-tree interpretation should distinguish:

- implementation evidence
- verification evidence
- runtime evidence
- safety/governance evidence

These layers are cumulative for strong claims and especially important for safety-sensitive capabilities.

## Status Semantics

- `📝`
  - intent exists, implementation evidence missing
- `🚧`
  - some implementation evidence exists, but verification, runtime, or governance evidence is incomplete
- `🧪`
  - implementation exists but evidence incompleteness is intentional or still too material for stable claims
- `✅`
  - implementation exists and the required additional evidence layers are satisfied for the node's sensitivity class
- `⚠️`
  - evidence exists but is contradicted by defects, regressions, or broken truth sources
- `🔒`
  - no longer canonical and explicitly retired

## Hard Interpretation Rule

`✅` must not be used as a narrative shortcut for “already production-ready” unless the required evidence layers for that node are actually present.
