# Add Maestro Collaboration Core

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


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
