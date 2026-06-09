# HTML5 Migration Worker Performance Readiness Rerun

Date: 2026-05-13

Change: `implement-html5-migration-experience-optimization`

Scope: Current repo-local readiness check for task `3.2.4`; this is not a worker performance benchmark.

## Check

The rerun inspected the current worker orchestration and static worker assets needed before a fair same-dataset performance benchmark can be executed.

Checked files:

- `web/frontend/src/utils/workersManager/workers-manager.ts`
- `web/frontend/src/stores/marketData.ts`
- `web/frontend/src/workers/indicatorDataWorker.worker.ts`
- `web/frontend/src/workers/protocol.ts`
- `web/frontend/public/workers/indicator-calculator.js`
- `web/frontend/public/workers/protocol.js`
- `web/frontend/dist/workers/indicator-calculator.js`
- `web/frontend/dist/workers/protocol.js`

## Result

Current benchmark readiness: `false`.

Observed facts:

- Source worker file exists.
- Source protocol file exists.
- `marketData.ts` still calls `workersManager.calculateIndicator(...)`.
- `workers-manager.ts` still contains placeholder implementation text.
- `workers-manager.ts` does not create a real `Worker`.
- `workers-manager.ts` calculation path still uses `Math.random()`.
- `public/workers/indicator-calculator.js` exists and imports `./protocol.js`.
- `public/workers/protocol.js` is missing.
- `dist/workers/indicator-calculator.js` exists and imports `./protocol.js`.
- `dist/workers/protocol.js` is missing.

## Disposition

`3.2.4` remains open.

There is no valid same-dataset worker performance comparison path while the active manager path is placeholder-based and the static worker protocol asset is missing. Recording a speedup under this state would incorrectly turn a placeholder or broken worker asset path into performance evidence.

Future closure requires:

- real `WorkersManager` orchestration using an actual worker;
- complete worker protocol assets in the served build path;
- a same-dataset benchmark comparing main-thread baseline, worker path, UI responsiveness, and fallback behavior.

