# Maestro Collaboration Core Design

## Context

MyStocks now separates:

- human-authored task contracts
- runtime orchestration
- long-term extraction boundary (`kernel`, `collab`, `profiles`)

The next smallest useful step is to make `collab` real by adding a persistent local registry.

## Goals / Non-Goals

- Goals:
  - persist collaboration runtime facts locally
  - keep the solution SQLite-first
  - integrate with the current runtime without large churn
- Non-Goals:
  - full worker pool orchestration
  - automatic task decomposition
  - complete worktree fleet management

## Decisions

1. Use the existing local tracker SQLite path for the first collab registry
2. Add three persistence areas:
   - assignments
   - workspace registry
   - worker heartbeats
3. Keep assignment fields nullable where the main CLI has not filled in worker ownership yet

## Risks / Trade-offs

- The collab registry initially shares storage with the local tracker DB
- Some business coordination facts remain in `TASK.md` / `TASK-REPORT.md`
- This is acceptable because the registry is intentionally machine-state only

## Migration Plan

1. land the registry and tests
2. wire it to workspace creation and runtime events
3. later split storage if a standalone tool wants separate DB ownership
