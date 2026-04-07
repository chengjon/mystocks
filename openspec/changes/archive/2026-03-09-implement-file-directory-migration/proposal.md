# Implement File Directory Migration

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


## Why

MyStocks accumulated severe directory-structure drift during rapid growth. The repository root contains
far more files than the intended policy allows, related files are scattered across inconsistent folders,
and existing directory rules are documented but not enforced consistently. This reduces maintainability,
increases onboarding cost, and makes automation harder to trust.

## What Changes

- Migrate files from non-canonical locations into governed directories with a gradual, auditable process
- Add and enforce directory-structure checks through existing automation entrypoints
- Normalize documentation, scripts, and source-code layout around approved taxonomy and boundaries
- Document migration decisions, risks, rollback strategy, and validation expectations

## Impact

- Affected specs: `file-organization`
- Affected code: repository structure, directory governance scripts/hooks, and related documentation/indexes
