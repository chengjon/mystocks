# Add Maestro Collaboration Core

## Why

The repository now has a stable long-term runtime family name (`Maestro`) and a defined three-layer
architecture, but the second layer `maestro.collab` still lacks a persistent collaboration core.
Without it, assignment, workspace/worktree mapping, and heartbeat/stale runtime signals only exist
partially in memory or are spread across ad-hoc runtime structures.

## What Changes

- Add a SQLite-backed collaboration registry under `maestro.collab`
- Persist issue assignment status, workspace/worktree registry, and worker heartbeat metadata
- Wire the collaboration registry into the existing local-first runtime

## Impact

- Affected specs: `symphony-service`
- Affected code: `src/services/maestro/collab/**`, `src/services/symphony/service.py`, `src/services/symphony/orchestrator.py`, `src/services/symphony/workspace_manager.py`
