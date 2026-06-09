# HTML5 Migration Worker Lifecycle Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.4.5 Add error handling and worker lifecycle management`
Scope: Desktop-only, repo-local audit only

## Decision

`2.4.5` remains open.

This batch records the current worker lifecycle and error-handling surface. The repo has lifecycle concepts in comments, protocol types, and generic helper utilities, but the active worker manager still does not own a verified worker lifecycle.

## Evidence Checked

Commands:

```bash
rg -n "new Worker|Worker\\(|workersManager|calculateIndicator|indicatorDataWorker|protocol|terminate\\(|onerror|postMessage|message|KLine|kline|OHLC|lifecycle|retry" web/frontend/src/workers web/frontend/src/utils web/frontend/src/stores web/frontend/src/components/technical web/frontend/src/components/artdeco/charts web/frontend/src/views/market web/frontend/tests
sed -n '1,260p' web/frontend/src/utils/workersManager/workers-manager.ts
sed -n '1,260p' web/frontend/src/workers/protocol.ts
sed -n '360,430p' web/frontend/src/utils/chartPerformanceUtils.ts
```

Observed repo facts:

- `web/frontend/src/utils/workersManager/workers-manager.ts` has a `terminate()` method, but the worker field is never populated in the placeholder `calculateIndicator()` path inspected here.
- `getHealthStatus()` currently returns a static healthy response, not a measured worker heartbeat.
- `web/frontend/src/workers/protocol.ts` defines heartbeat, timeout, error-message, and priority queue concepts.
- `web/frontend/src/utils/chartPerformanceUtils.ts` has a generic `processInWorker(...)` helper that creates a worker, handles `onmessage` / `onerror`, and terminates it.

## Gap Summary

The repo has pieces that could support lifecycle management, but there is no verified canonical worker lifecycle for the active `workersManager` path.

Static health status and a generic helper do not prove worker creation, heartbeat, timeout handling, restart, error recovery, or cleanup for the current Web Worker feature.

## Task Disposition

Keep `2.4.5` unchecked until a later approved batch implements and verifies canonical worker lifecycle management.

Minimum future evidence should include:

- Active worker creation and termination in `workersManager`.
- Error-path and timeout tests.
- Health status derived from actual worker state or an approved alternative.
- Cleanup verification when components/stores no longer need worker work.
