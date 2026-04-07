# Define Maestro Three-Layer Architecture

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


## Why

The MyStocks runtime currently uses `Symphony` as the implementation name, but the runtime has now
grown into a broader local-first orchestration and multi-CLI automation system. A more durable
family name and extraction boundary are needed so the generic runtime and collaboration core can be
moved into a standalone tool later.

## What Changes

- Introduce `Maestro` as the recommended long-term runtime family name
- Seed a `src/services/maestro` compatibility namespace in the repository
- Define a three-layer architecture: `kernel`, `collab`, and `profiles`
- Keep `symphony` as the compatibility implementation path for now

## Impact

- Affected specs: `symphony-service`
- Affected code: `src/services/maestro/**`, `src/services/symphony/__init__.py`, `WORKFLOW.md`
- Affected docs: local workflow guide and Maestro architecture plans
