# Change: Canonicalize backend route UnifiedResponse contracts

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

`sequence-backend-architecture-unblocks` restored the backend runtime import
chain in an isolated worktree, but the source change cannot be committed because
`UnifiedResponse Contract Guard` rejects changed route files that still expose
plain or missing `response_model` declarations.

This is a separate API contract lane. It must not be hidden inside the runtime
unblock commit because it changes route OpenAPI response contracts across
multiple modules.

## What Changes

- Canonicalize the changed route files that currently block the runtime unblock
  commit:
  - `web/backend/app/api/data_quality.py`
  - `web/backend/app/api/indicators/indicator_cache.py`
  - `web/backend/app/api/signal_monitoring/signal_history_response.py`
  - `web/backend/app/api/technical_analysis.py`
- Replace missing or non-canonical route `response_model` declarations with
  `UnifiedResponse[...]` or `UnifiedPaginatedResponse[...]` declarations.
- Treat the target modules as different migration shapes rather than one
  uniform edit:
  - `data_quality.py` currently has route-contract errors with no route
    `response_model` declarations.
  - `indicator_cache.py` and `signal_history_response.py` already expose typed
    direct Pydantic response models and need canonical wrapper declarations.
  - `technical_analysis.py` is mixed: some routes already expose direct
    `response_model` declarations and the remaining route-contract errors still
    need explicit canonical declarations.
- Preserve runtime payload shape and caller contract parity unless an explicit
  endpoint-level test and OpenAPI diff records an intentional change.
- Re-run route/OpenAPI and health route evidence after the contract migration.

## Impact

- Affected specs:
  - `01-unified-response-format`
- Affected code:
  - four backend route modules listed above
  - route/OpenAPI evidence artifacts
  - quality reports and steward tree entries
- Affected gates:
  - `UnifiedResponse Contract Guard`
  - `test_health_route_conflicts.py`
  - targeted `app.openapi()` smoke

## Scope Boundaries

- This change does not migrate unrelated route modules.
- This change does not alter business behavior, service seams, singleton
  lifecycle, schema directory retirement, frontend behavior, or miniQMT evidence
  promotion.
- This change must not use `--no-verify`.
- This change must not archive `sequence-backend-architecture-unblocks`; it only
  unlocks a later source commit for that lane.
