# Change: Add System Resource Usage Monitoring

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
`FUNCTION_TREE` still marks `6.1 资源使用` as unfinished. The current repository truth already exposes health probes and monitoring-oriented API surfaces, but the active system UI still centers on backend health, middleware status, and telemetry notes. It does not yet provide a dedicated resource-usage workbench with a unified backend contract for host, process, database, and Redis metrics.

## What Changes
- Add a dedicated `system-resource-usage-monitoring` capability for single-node resource observation.
- Add a unified backend `resource-metrics` contract that returns current snapshots, short-window trends, dependency summaries, and server-defined threshold states.
- Add a dedicated `/system/resources` frontend route and a matching system navigation label.
- Keep the new resource usage page separate from `API.vue`, which remains the health and telemetry control surface.

## Impact
- Affected specs:
  - `system-resource-usage-monitoring`
  - `frontend-routing`
- Affected code:
  - `web/backend/app/api/system/*`
  - `web/backend/app/services/*` or a dedicated system-resource aggregation layer
  - `web/frontend/src/api/*`
  - `web/frontend/src/views/system/*`
  - `web/frontend/src/router/index.ts`
