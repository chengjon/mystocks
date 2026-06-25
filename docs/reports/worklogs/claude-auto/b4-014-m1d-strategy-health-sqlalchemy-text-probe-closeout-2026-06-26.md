# B4.014-M1d Strategy Health SQLAlchemy Text Probe Closeout

Date: 2026-06-26

## Mainline Target

Restore the `/api/strategy-mgmt/health` runtime path past the SQLAlchemy 2 probe failure:

```text
Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
```

This package stays inside the B4.014 P0 runtime usability line. It does not resume B4.012 governance cleanup, frontend work, OpenSpec work, OpenStock provider/runtime work, or repository hygiene.

## Authorized Scope

- `web/backend/app/api/strategy_mgmt.py`
- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

## Implementation

- Wrapped the strategy health database probe with SQLAlchemy `text("SELECT 1")`.
- Added a regression test proving `health_check()` sends a `TextClause` to the database session.
- Restored unrelated response-example imports so the source diff remains limited to the runtime probe fix.

## Verification Evidence

Fresh checks executed during implementation:

- RED test before source change:
  - `pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_strategy_mgmt_backtest_regressions.py::test_strategy_health_database_probe_uses_sqlalchemy_text_clause`
  - Failed because the handler passed a raw string to `db.execute()`.
- GREEN focused test:
  - `pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_strategy_mgmt_backtest_regressions.py::test_strategy_health_database_probe_uses_sqlalchemy_text_clause`
  - Passed.
- Focused regression file:
  - `pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_strategy_mgmt_backtest_regressions.py`
  - Passed: 5 tests.
- Syntax gate:
  - `python -m py_compile web/backend/app/api/strategy_mgmt.py web/backend/tests/test_strategy_mgmt_backtest_regressions.py`
  - Passed.
- Runtime probe after PM2 backend restart:
  - `GET http://localhost:8020/health`: HTTP 200.
  - `GET http://localhost:8020/api/strategy-mgmt/health`: HTTP 200.
  - SQLAlchemy textual SQL error: not present.

## Remaining P0 Runtime Blocker

The strategy health endpoint still reports an unhealthy body because the next database check queries a missing runtime table:

```text
psycopg2.errors.UndefinedTable: relation "user_strategies" does not exist
```

This is not part of M1d. It should be handled as a follow-up B4.014-M1 P0 blocker package, with a separate decision on whether strategy health should:

- remain a lightweight readiness probe that validates DB connectivity and data-source availability, or
- explicitly require strategy/backtest schema initialization before reporting healthy.

## Boundary

No database schema creation, migration, connection pool, repository, frontend, OpenStock runtime, route redesign, B4.012 cleanup, or unrelated dirty-worktree file was modified in this package.
