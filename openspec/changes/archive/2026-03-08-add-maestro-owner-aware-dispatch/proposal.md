# Add Maestro Owner-Aware Dispatch

## Why

The collaboration registry now persists assignment state, but the runtime does not yet use that
assignment information to decide which CLI should execute work. As a result, owner decisions are
recorded but not enforced by the runtime.

## What Changes

- Add runtime CLI identity and optional stale reclaim behavior
- Use collaboration assignment data during dispatch decisions
- Add a small collab management CLI for main CLI assignment operations
- Add collaboration status API endpoints for issue state, workspaces, and stale worker visibility

## Impact

- Affected specs: `symphony-service`
- Affected code: `src/services/symphony/config.py`, `src/services/symphony/orchestrator.py`, `src/services/symphony/status_api.py`, `src/services/maestro/collab/registry.py`, `scripts/runtime/maestro_collab.py`
