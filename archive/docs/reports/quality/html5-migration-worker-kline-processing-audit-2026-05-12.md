# HTML5 Migration Worker K-Line Processing Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.4.2 Implement Web Worker for data processing tasks`
Scope: Desktop-only, repo-local audit only

## Decision

`2.4.2` remains open.

This batch records the current Web Worker surface for K-line and indicator data processing. The repo has an indicator worker and protocol definitions, but the active manager path still returns placeholder results and does not prove a canonical K-line data processing worker pipeline.

## Evidence Checked

Commands:

```bash
rg -n "new Worker|Worker\\(|workersManager|calculateIndicator|indicatorDataWorker|protocol|terminate\\(|onerror|postMessage|message|KLine|kline|OHLC|lifecycle|retry" web/frontend/src/workers web/frontend/src/utils web/frontend/src/stores web/frontend/src/components/technical web/frontend/src/components/artdeco/charts web/frontend/src/views/market web/frontend/tests
sed -n '1,260p' web/frontend/src/utils/workersManager/workers-manager.ts
sed -n '1,260p' web/frontend/src/workers/indicatorDataWorker.worker.ts
sed -n '230,380p' web/frontend/src/stores/marketData.ts
```

Observed repo facts:

- `web/frontend/src/workers/indicatorDataWorker.worker.ts` exists and calculates technical indicator outputs from `KLineData[]`.
- `web/frontend/src/workers/protocol.ts` defines worker protocol concepts, including a `PROCESS_KLINE_DATA` message type.
- `web/frontend/src/stores/marketData.ts` calls `workersManager.calculateIndicator(...)` when loading technical indicators.
- `web/frontend/src/utils/workersManager/workers-manager.ts` currently documents the implementation as a placeholder and returns generated random data instead of dispatching to a real Worker instance.

## Gap Summary

The indicator worker exists, but the active `workersManager` path does not currently create or use that worker for the store path inspected here.

`PROCESS_KLINE_DATA` exists in protocol definitions, but this audit did not find an active canonical K-line data processing worker path for K-line transformation, normalization, or heavy data processing tasks.

Generic chart helper code can create a worker with `new Worker(...)`, but that is not the canonical active K-line pipeline for this OpenSpec task.

## Task Disposition

Keep `2.4.2` unchecked until a later approved batch implements and verifies a real K-line data processing worker path.

Minimum future evidence should include:

- Active worker creation and message dispatch for K-line processing.
- Verified use by a canonical K-line or market-data route/component.
- A deterministic test proving processed K-line output comes from the worker path, not placeholder/random data.
