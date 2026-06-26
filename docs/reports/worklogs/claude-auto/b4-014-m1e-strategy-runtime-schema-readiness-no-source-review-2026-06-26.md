# B4.014-M1e Strategy Runtime Schema Readiness No-Source Review

Date: 2026-06-26

## Mainline Target

Restore the strategy management runtime path as part of `B4.014 mainline A-share quant runtime usability recovery`.

This review is `no-source`: no source, test, schema, OpenSpec, frontend, OpenStock runtime, or repository hygiene files were modified. The purpose is to decide the next P0 source package after M1d removed the SQLAlchemy textual SQL probe failure.

## Runtime Evidence

Runtime environment observed from PM2 backend:

- Backend: `http://localhost:8020`
- PostgreSQL target: `192.168.123.104:5438/mystocks`

Fresh endpoint probes:

- `GET /api/strategy-mgmt/health`
  - HTTP 200
  - Body status: `unhealthy`
  - Failure: `psycopg2.errors.UndefinedTable: relation "user_strategies" does not exist`
- `GET /api/strategy-mgmt/strategies?user_id=1001`
  - HTTP 500
  - Failure: `relation "user_strategies" does not exist`
- `GET /api/strategy-mgmt/backtest/results?user_id=1001`
  - HTTP 500
  - Failure: `column backtest_results.user_id does not exist`

M1d result remains valid: the previous SQLAlchemy textual SQL error is no longer present.

## Runtime Schema Truth

Observed runtime table state in PostgreSQL:

- `user_strategies`: missing
- `backtest_results`: present, but incompatible with current ORM expectations because `user_id` is missing
- `backtest_equity_curves`: missing
- `backtest_trades`: present
- `strategy_signals`: missing

Related runtime tables already present include:

- `backtest_results`
- `backtest_trades`
- `backtests`
- `ddd_strategies`
- `strategies`
- `strategy_backtest`
- `strategy_definition`
- `strategy_health`
- `strategy_parameters`
- `strategy_result`
- `trade_history`
- `trade_signals`

## ORM / Initialization Boundary

The strategy and backtest repositories currently define their own SQLAlchemy declarative bases:

- `app.repositories.strategy_repository.Base` contains `user_strategies`
- `app.repositories.backtest_repository.Base` contains `backtest_results`, `backtest_equity_curves`, `backtest_trades`
- Neither repository `Base` is the same object as `app.core.database.Base`
- `app.core.database.Base.metadata.tables` is empty in the runtime import path

This means the strategy/backtest ORM table definitions are not part of a unified backend metadata initialization path.

Existing SQL bootstrap files contain `backtest_results` and `backtest_trades`, but this review did not find a corresponding active `user_strategies` creation path. Existing runtime `backtest_results` also appears older than the current ORM model because the ORM queries `user_id`, while the live table lacks that column.

## Impact

This is a P0 mainline runtime blocker, not a cosmetic health-check issue:

- Strategy health remains `unhealthy`.
- Strategy list is HTTP 500.
- Backtest result list is HTTP 500.
- Strategy and backtest pages cannot be considered usable until the schema contract and runtime table state align.

## Risk Assessment

Risk level: high, because fixing this may touch persistent database schema behavior.

Recommended implementation must avoid broad migration rewrites. The next source package should be small and explicitly decide one of these approaches before editing:

1. Runtime schema readiness route:
   - Provide a minimal, idempotent strategy runtime schema initialization/repair path for `user_strategies` and the current backtest ORM-required columns/tables.
   - Verify strategy list and backtest result list no longer 500 for an empty runtime database state.
2. Health-check scope route:
   - Keep `/health` as a lightweight readiness probe, but this alone is insufficient because `/strategies` and `/backtest/results` still fail.

Because list endpoints are already failing, route 1 is the mainline-useful path.

## Recommended Next Package

`B4.014-M1e strategy runtime schema readiness repair`

Source authorization should be requested separately and should be limited to the smallest files required to:

- centralize or invoke current strategy/backtest ORM metadata creation safely, or
- add a minimal idempotent runtime schema readiness helper used by the strategy module startup/probe path, and
- add focused tests proving:
  - `user_strategies` schema readiness is checked/created idempotently,
  - backtest table schema drift is detected or repaired without destructive migration,
  - strategy list/backtest list runtime probes stop returning 500 for schema-readiness reasons.

Forbidden for the implementation package:

- No OpenStock provider/runtime development.
- No frontend changes.
- No B4.012 cleanup.
- No repository hygiene.
- No broad migration framework rewrite.
- No destructive database operations.
- No unrelated schema/table cleanup.
