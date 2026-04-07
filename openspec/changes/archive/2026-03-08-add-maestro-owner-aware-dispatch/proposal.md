# Add Maestro Owner-Aware Dispatch

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


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
