# B4.014-M1d Strategy Health SQLAlchemy Text Probe Repair Authorization

Date: 2026-06-25

## Runtime Defect

`GET /api/strategy-mgmt/health` now returns HTTP 200 after the B4.014-M1a/M1b/M1c runtime blocker chain, but the response body still reports a database probe code error:

```text
Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
```

Current runtime probe:

- Backend `/health`: HTTP 200
- Strategy health `/api/strategy-mgmt/health`: HTTP 200
- Strategy health body:
  - `status`: `unhealthy`
  - `database`: `error`
  - `error`: SQLAlchemy textual SQL expression error

## Root Cause

The strategy management health endpoint executes a bare SQL string:

```python
db.execute("SELECT 1")
```

In SQLAlchemy 2, textual SQL must be wrapped with `sqlalchemy.text()`.

Target code path:

- `web/backend/app/api/strategy_mgmt.py`
- `health_check()`
- line around the database probe before `data_source.health_check()`

## GitNexus Impact

`web/backend/app/api/strategy_mgmt.py:health_check`

- Risk: LOW
- Direct impact: 0
- Affected execution flows: 0
- Affected modules: 0

GitNexus route lookup did not map `/api/strategy-mgmt/health`, but runtime probes confirm the route is active.

## Authorized Scope

Allowed source/test files:

- `web/backend/app/api/strategy_mgmt.py`
- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

Allowed action:

- Add a focused regression test proving `health_check()` uses a SQLAlchemy executable text clause for the database probe.
- Replace the bare string SQL probe with `text("SELECT 1")`.

Non-goals:

- No data source factory changes.
- No database schema, connection, pool, or environment changes.
- No API route or response redesign.
- No frontend changes.
- No OpenStock provider/runtime work.
- No B4.012 governance repair or repository hygiene work.

## Required Verification

- TDD RED/GREEN for the strategy health SQLAlchemy text probe.
- `python -m py_compile` on changed source/test files.
- Focused strategy management regression test file.
- Runtime probe: `GET /api/strategy-mgmt/health` no longer reports the SQLAlchemy textual SQL expression error.
- GitNexus staged verification and change detection.
- OPENDOG fresh verification.
- Exact staging only.
