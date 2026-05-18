# Backend Health/Status Owner Registry

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

日期：2026-05-18

关联 OpenSpec change：`consolidate-backend-health-endpoints`

## 结论

本批次继续 G 线，但仍不改运行代码、不退役端点、不切换 PM2 / CI / frontend 探针。

本批次完成：

- 对当前 status-like endpoints 做 smoke 分类。
- 记录 retained domain smoke/status endpoints 与 owner。
- 记录本批无 retired endpoint，因此无路径级 rollback action。
- 记录 PM2 live probe 只读结果，但不运行会 `pm2 stop all` / `pm2 delete all` 的 stateful integration workflow。

## Status Smoke

执行方式：FastAPI `TestClient(app)`。

| Path | HTTP | 分类 | 结论 |
|------|------|------|------|
| `/api/status` | 200 | platform status | 当前可作为 platform status canonical smoke path。 |
| `/api/socketio-status` | 200 | service status | Socket.IO / realtime service status，保留在 system/service owner 下。 |
| `/api/trading/status` | 200 | domain status | Trading domain status，保留在 trading owner 下。 |
| `/api/notification/status` | 403 | protected domain status | 需认证，不能作为 public platform smoke。 |
| `/status` | 404 | absent root alias | 不新增 root `/status`。 |
| `/api/v1/system/status` | 404 | absent alias | 不新增该 alias，除非后续 consumer 证据要求。 |

当前 OpenAPI 中共有 22 个 status-like paths，包括 platform、cache、GPU、notification、trading、strategy、monitoring、optimization、risk、Kronos 等领域状态端点。G 线第一批只做分类和保留记录，不做 blanket deletion。

## PM2 Live Probe

`pm2 list` 显示：

| Service | Status | Uptime | Restart |
|---------|--------|--------|---------|
| `mystocks-backend` | online | 2D | 0 |
| `mystocks-frontend` | online | 2D | 0 |

Live HTTP probe：

| URL | HTTP | Content-Type | 结论 |
|-----|------|--------------|------|
| `http://localhost:8020/health` | 200 | `application/json` | backend liveness OK |
| `http://localhost:8020/api/health/ready` | 200 | `application/json` | backend readiness OK |
| `http://localhost:8020/api/health/services` | 200 | `application/json` | services endpoint reachable, data status degraded |
| `http://localhost:8020/api/status` | 200 | `application/json` | platform status OK |
| `http://localhost:3020/` | 200 | `text/html` | frontend root reachable |

`scripts/run_pm2_integration_workflow.sh gate` was intentionally not executed in this batch because the script begins with `clean_pm2`, which runs `pm2 stop all` and `pm2 delete all`. That is a stateful service orchestration action, not required for this documentation-only G-line owner registry batch.

## Retained Owner Registry

| Category | Retained path examples | Owner | Handling rule |
|----------|------------------------|-------|---------------|
| Platform liveness | `/health` | backend platform / app lifecycle | Public lightweight liveness; do not attach dependency checks. |
| Platform readiness | `/health/ready`, `/api/health/ready` | backend platform / app lifecycle | Preserve both until PM2, CI, frontend, scripts migrate. |
| Platform status | `/api/status` | metrics / platform status owner | Public basic status; no root `/status` alias unless approved. |
| System services health | `/api/health/services`, `/api/health/detailed` | system health / operations owner | Services health is diagnostic; not liveness. Detailed health may require auth/ops context. |
| Metrics / observability | `/metrics`, `/api/metrics`, `/api/gpu/metrics`, `/metrics/health` | observability / metrics owner | Keep separate from health consolidation; content-type and labels are monitoring contracts. |
| Announcement smoke/status | `/api/announcement/health`, `/api/announcement/status` | announcement domain owner | Retain because CI/scripts still use `/api/announcement/health` fallback. |
| Trading smoke/status | `/api/trading/status`, `/api/v1/trade/health` | trading domain owner | Retain as domain smoke/status; not platform readiness. |
| Risk domain status | `/api/v1/risk/health`, `/api/v1/risk/v31/stop-loss/status/{position_id}` | risk domain owner | Retain; status semantics are domain-specific. |
| Strategy domain status | `/api/v1/strategy/backtest/status/{backtest_id}`, `/api/v1/strategy/models/training/{task_id}/status`, `/api/v1/strategies/batch-analysis/runtime-status`, `/api/v1/strategies/ml/runtime-status` | strategy / ML runtime owner | Retain; these are job/runtime status endpoints. |
| Cache status | `/api/cache/status`, `/api/cache/prewarming/status` | cache domain owner | Retain; cache status is not platform readiness. |
| Data quality / source status | `/api/data-quality/status/overview`, `/api/multi-source/status`, data-source health-check paths | data governance owner | Retain; classify as adapter/data diagnostic. |
| Notification status | `/api/notification/status` | notification domain owner | Retain; protected by authentication. |
| Realtime / SSE status | `/api/socketio-status`, `/api/v1/sse/status` | realtime / websocket owner | Retain; service-specific status. |
| Kronos status | `/api/v1/kronos/status` | Kronos / AI analysis owner | Retain; model/service-specific status. |
| Optimization status | `/api/v1/optimization/status` | optimization owner | Retain; workload-specific status. |
| Backup health | `backup_recovery_secure/cleanup_old_backups.py` `/health` | backup domain owner | Deferred to backup route ownership, not G-line retirement. |
| Old monitoring health | `monitoring_old/routes.py` `/health` | old-module cleanup owner | Deferred to old-module archival/removal task. |

## Retired Endpoints

No endpoint was retired in this batch.

| Retired path | Reason | Rollback |
|--------------|--------|----------|
| None | No runtime path changed. | No rollback action required. |

## Remaining Boundaries

Open items:

- `4.6` remains open: broader affected backend/frontend smoke is not clean because `web/backend/tests/test_health_route_conflicts.py` currently has 5 unrelated OpenAPI documentation failures.
- `4.7` remains open: PM2 online state and live probes are recorded, but the stateful PM2 integration workflow was not executed in this batch.
- `3.x` implementation tasks remain open: no probe path, alias, or endpoint retirement was changed.

