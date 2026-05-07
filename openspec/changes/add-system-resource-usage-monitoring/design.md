# System Resource Usage Monitoring Design

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Context
The current repository already contains several monitoring-adjacent surfaces:
- health probes under `web/backend/app/api/system/` and `web/backend/app/api/health.py`
- monitoring-oriented contracts in `web/frontend/src/api/monitoring.ts`
- a system telemetry page at `web/frontend/src/views/system/API.vue`

However, the active UI does not yet expose `6.1 资源使用` as a first-class independent capability. The missing pieces are a dedicated system resource page, a unified backend contract for resource snapshots and trends, and a consistent threshold/state model that the frontend can render without stitching together multiple partial contracts.

## Goals / Non-Goals
- Goals:
  - Provide a dedicated `/system/resources` page for single-node resource observation.
  - Return one unified backend contract covering host, process, database, and Redis resource views.
  - Expose current snapshots and a recent `60` minute short trend window.
  - Support default `15s` polling with pause/resume controls.
  - Return threshold definitions from the backend and derive `normal / warning / critical` states from those thresholds.
- Non-Goals:
  - Multi-node switching or aggregation.
  - WebSocket or SSE streaming.
  - User-editable thresholds or alert-notification workflows.
  - Long-range historical views such as `24h` or `7d`.
  - Replacing the current health / telemetry role of `API.vue`.

## Decisions
### Decision: Create an independent resource usage capability
The resource usage workbench should be its own system page instead of another section inside `API.vue`.

Rationale:
- `API.vue` is already the health and middleware telemetry surface
- `6.1 资源使用` needs its own mental model, controls, and trend layout
- a separate route reduces page sprawl and keeps FUNCTION_TREE closure evidence clear

### Decision: Use one unified backend resource-metrics contract
The backend should expose a single read contract for the page instead of forcing the frontend to compose multiple partial APIs.

Rationale:
- current metrics, health, and dependency endpoints are fragmented
- the frontend should not own threshold semantics or data-source stitching
- a unified response keeps snapshot, trend, and threshold semantics aligned

### Decision: Scope the first batch to one node and proxy dependency metrics
The first batch should only observe the current runtime host and its local dependencies. Database and Redis entries may use proxy resource indicators such as health, connection counts, and memory summaries rather than full operating-system resource views.

Rationale:
- this preserves a realistic MVP boundary
- it avoids prematurely expanding into multi-node or infra-wide observability
- it keeps PostgreSQL, TDengine, and Redis visible without requiring a full Prometheus-style inventory layer

### Decision: Keep thresholds server-defined
The backend should return the warning and critical thresholds for each monitored resource, and the frontend should only render the resulting status.

Rationale:
- threshold semantics must remain consistent across route consumers
- frontend-local thresholds would create a second truth source
- the current batch does not include user-editable alert policy

### Decision: Poll every 15 seconds by default
The page should use polling rather than streaming, with a user control to pause or resume polling.

Rationale:
- polling is simpler to integrate into the current system domain
- it is sufficient for host/process/dependency resource visibility in this batch
- it avoids introducing a new runtime transport contract before the panel is stable

## Risks / Trade-offs
- Risk: single-node scope may later need expansion.
  - Mitigation: keep the node envelope explicit so future node selection can remain additive.
- Risk: dependency resource views may appear weaker than host metrics.
  - Mitigation: explicitly describe database and Redis metrics as first-batch proxy summaries.
- Risk: adding a new system route may drift from router/menu/page-config truth.
  - Mitigation: modify `frontend-routing` in the same change and require route-level verification.
