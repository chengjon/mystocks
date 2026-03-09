# Maestro Three-Layer Architecture Design

## Context

`Symphony` already acts as more than a tracker poller. In MyStocks it now represents:

- local-first orchestration
- multi-CLI automation after task activation
- workspace and runtime visibility

To extract this capability cleanly, the repo needs a stable family name and a layered boundary.

## Goals / Non-Goals

- Goals:
  - establish `Maestro` as the long-term runtime family name
  - create a three-layer extraction boundary
  - preserve current `symphony` imports during transition
- Non-Goals:
  - fully move implementation files out of `symphony` in this change
  - implement all future collaboration-core features now

## Decisions

1. Keep `symphony` as the current implementation package
2. Add `maestro` as a compatibility namespace immediately
3. Define the long-term layers as:
   - `maestro.kernel`
   - `maestro.collab`
   - `maestro.profiles`

## Risks / Trade-offs

- The first step is mostly namespace and architecture work, not a full refactor
- Some functionality still physically lives under `symphony`
- But this keeps churn low while making future extraction explicit

## Migration Plan

1. seed `maestro` namespace now
2. preserve old imports
3. migrate implementation files by layer in later changes
