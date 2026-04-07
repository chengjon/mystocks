# Add Maestro Owner Suggestion

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


## Why

The main CLI is still responsible for deciding task ownership, but that decision currently depends on
manual reading of `.FILE_OWNERSHIP`, `TASK.md`, and path/module context. A conservative suggestion
layer can reduce repetitive work without removing the main CLI's final authority.

## What Changes

- Add a rule-based owner suggestion engine
- Use `.FILE_OWNERSHIP` and task path hints to rank likely owners
- Expose the suggestion engine through the Maestro collab CLI
- Keep assignment as an explicit operator action

## Impact

- Affected specs: `symphony-service`
- Affected code: `src/services/maestro/collab/**`, `scripts/runtime/maestro_collab.py`
