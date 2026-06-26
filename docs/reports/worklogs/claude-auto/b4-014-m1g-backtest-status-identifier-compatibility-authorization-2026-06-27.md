# B4.014-M1g Backtest Status Identifier Compatibility Authorization

Date: 2026-06-27

Status: authorization-prepared, no source edits in this package.

## Mainline Reason

B4.014-M1f proved that the next user-visible strategy runtime blocker is not the degraded timeseries data-source dependency. The concrete blocker is:

```text
GET /api/strategy-mgmt/backtest/status/1 -> HTTP 500
operator does not exist: character varying = integer
```

Runtime schema evidence shows:

- `backtest_results.backtest_id`: `character varying`
- `backtest_results.strategy_id`: `character varying`
- `backtest_results.user_id`: `integer`

The current API route and repository lookup compare an integer route parameter against a legacy string identifier column. This fails before the request reaches `BacktestEngine`, `strategy_service`, OpenStock, or any timeseries data path.

## GitNexus Impact

Pre-edit impact analysis was run before any source modification:

| Target | File | Risk | Notes |
| --- | --- | --- | --- |
| `get_backtest_status` | `web/backend/app/api/strategy_mgmt.py` | LOW | 0 direct indexed callers, 0 affected processes. |
| `BacktestRepository` | `web/backend/app/repositories/backtest_repository.py` | MEDIUM | 10 direct callers, 23 total impacted symbols, 0 affected processes. |
| `BacktestResultModel` | `web/backend/app/repositories/backtest_repository.py` | MEDIUM | 10 direct callers, 23 total impacted symbols, 0 affected processes. |

The repair is mainline-safe only if kept local to identifier normalization and direct regression coverage.

## Requested Source Authorization

Authorization name:

`B4.014-M1g backtest status identifier compatibility repair`

Allowed source files:

- `web/backend/app/api/strategy_mgmt.py`
- `web/backend/app/repositories/backtest_repository.py`

Allowed test files:

- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

Allowed actions:

- Normalize `backtest_id` handling for status/result repository lookups so legacy string identifiers do not trigger PostgreSQL varchar/int operator errors.
- Preserve existing runtime data; no destructive migration, no table rebuild, no data delete.
- Add or adjust focused regression tests for legacy string ID compatibility.
- Keep response contracts stable for existing strategy/backtest endpoints.

Non-goals:

- No OpenStock provider/runtime development.
- No data-source runtime repair.
- No strategy core or backtest engine rewrite.
- No frontend changes.
- No API path redesign.
- No broad schema migration framework work.
- No B4.012 governance cleanup.
- No unrelated dirty worktree files.

## Required Gates For Implementation Package

- GitNexus impact already captured before editing; rerun staged GitNexus checks before commit.
- `python -m py_compile` on modified backend source/test files.
- Focused regression test:
  - `pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_strategy_mgmt_backtest_regressions.py`
- Runtime smoke after backend reload:
  - `GET /health` remains HTTP 200.
  - `GET /api/strategy-mgmt/health` remains HTTP 200.
  - `GET /api/strategy-mgmt/strategies?user_id=1001` remains HTTP 200.
  - `GET /api/strategy-mgmt/backtest/results?user_id=1001` remains HTTP 200.
  - `GET /api/strategy-mgmt/backtest/status/1` must no longer fail with varchar/int comparison.
- OPENDOG fresh verification.
- Exact staging only for authorized files and generated FUNCTION_TREE/worklog files.

## Expected Outcome

The strategy/backtest read surface should stop producing the current `backtest_id` varchar/int 500. If the endpoint returns a domain-level "not found" for absent ID `1`, that is acceptable; the unacceptable condition is an unhandled SQL operator error.
