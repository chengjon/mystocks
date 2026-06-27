# B4.014-M1i Controlled Minimal Backtest Execution Smoke

Date: 2026-06-28

Scope: runtime smoke evidence only. No source, test, runtime config, frontend, OpenSpec, OpenStock, or external dirty files were modified.

## Purpose

B4.014 is the active A-share quant runtime usability mainline. This package continues from M1h and validates whether the minimal strategy backtest execution chain can move beyond enqueue/status-readiness into actual `BacktestEngine` execution.

The smoke intentionally avoids `POST /api/strategy-mgmt/backtest/execute` because that route creates a database row and enqueues a Celery task. Instead, it invokes the Celery task synchronously with a fake `backtest_id` and verifies database row counts before and after execution.

## Runtime Context

| Runtime item | Evidence |
| --- | --- |
| Backend process | `mystocks-backend` found in PM2 |
| Backend port | `8020` |
| PostgreSQL host | `192.168.123.104` |
| PostgreSQL port | `5438` |
| PostgreSQL database | `mystocks` |
| Password handling | present in PM2 env, redacted in evidence |

Database safety snapshot with the PM2 backend environment:

| Check | Before | After |
| --- | ---: | ---: |
| `backtest_results` total rows | `0` | `0` |
| `backtest_id like 'm1i-smoke-%'` rows | `0` | `0` |

No smoke row was persisted.

## Smoke Method

The direct `.run(...)` call is not a valid Celery task harness for this code path because `self.update_state(...)` requires a task id. The controlled smoke therefore used:

```text
run_backtest_task.apply(args=[smoke_id, strategy_config, backtest_config], task_id=smoke_id, throw=False)
```

This gives Celery a concrete task id while keeping execution synchronous and observable.

## Result 1: API-Style Date Input

Input:

```text
symbol=000001
start_date=2024-01-02
end_date=2024-01-05
data_source_mode=strategy_service
```

Observed task result:

```text
state=FAILURE
result_type=ValueError
result=ValueError('没有加载到任何市场数据')
```

Signal from the execution path:

```text
StrategyService: 未获取到股票历史数据
BacktestEngine: 未找到 000001 的历史数据
BacktestEngine: ValueError("没有加载到任何市场数据")
```

Interpretation: the task now reaches `BacktestEngine` and `StrategyService.get_stock_history`, so the previous Celery task-id harness blocker is removed. The next blocker is market data loading.

## Result 2: Data Fetch Boundary Probe

The data-fetch boundary was tested with the same PM2 backend environment:

| Symbol | Start | End | Rows |
| --- | --- | --- | ---: |
| `000001` | `2024-01-02` | `2024-01-05` | `0` |
| `000001` | `20240102` | `20240105` | `4` |
| `000001` | `20240101` | `20240131` | `22` |
| `600519` | `20240102` | `20240105` | `4` |

Interpretation: `StrategyService.get_stock_history` can fetch A-share history through its current consumer path when dates are `YYYYMMDD`, but returns empty data when dates are API-style `YYYY-MM-DD`.

## Result 3: Canonical Data-Source Date Input

Input:

```text
symbol=000001
start_date=20240102
end_date=20240105
data_source_mode=strategy_service
```

Observed task result:

```text
state=FAILURE
result_type=ValueError
result=ValueError("time data '20240102' does not match format '%Y-%m-%d'")
```

Interpretation: the data-source consumer expects `YYYYMMDD`, but `BacktestEngine` date parsing expects `%Y-%m-%d`. The backtest execution chain has a runtime contract mismatch between engine date handling and strategy data-source consumption.

## Mainline Blocker

Minimal backtest execution is not currently usable:

1. API-style dates (`YYYY-MM-DD`) satisfy `BacktestEngine` parsing but fail `StrategyService` historical data loading.
2. Data-source-style dates (`YYYYMMDD`) satisfy `StrategyService` but fail `BacktestEngine` parsing.
3. The failure happens before useful strategy execution or result generation.
4. No OpenStock/provider runtime change is implicated by this evidence. This is a MyStocks consumer/adaptation boundary issue.

## Decision

Prepare a dedicated source-authorized repair package:

```text
B4.014-M1j backtest date contract normalization repair
```

Recommended scope:

- Normalize date inputs at the MyStocks backtest/data-source boundary.
- Preserve API-facing request compatibility with `YYYY-MM-DD`.
- Feed `StrategyService.get_stock_history` the format it currently consumes successfully.
- Keep OpenStock/provider runtime out of scope.
- Add focused regression coverage proving minimal backtest market data loading works for API-style dates.

No source repair was performed in M1i.
