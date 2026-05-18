# Backend Health/Status Taxonomy Start

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

日期：2026-05-18

关联 OpenSpec change：`consolidate-backend-health-endpoints`

## 结论

G 线正式切入，但首批只做证据对齐和 health/status taxonomy 决策，不改后端运行代码、不退役端点、不切换 PM2 / CI / frontend 探针。

本批次确认：

- 编排文档存在，并要求 G 线优先决定 health/status taxonomy。
- route/OpenAPI baseline 存在，并已把健康端点分为 canonical、active fragmented、excluded 三类。
- `/health/readiness` 在代码根中无命中，不应作为兼容路径新增，除非后续显式批准。
- 当前 canonical 探针应保持为 `/health`、`/health/ready`、`/api/health/ready`、`/api/health/services`。
- `/api/announcement/health` 仍被多个 CI / smoke 脚本当作 fallback，不能在第一批退役。
- `backup_recovery_secure/cleanup_old_backups.py` 的 `/health` 属于 backup 域所有权问题，不纳入 G 线第一批 health/status consolidation。

## 证据来源

| 证据 | 结论 |
|------|------|
| `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` | G 线顺序在 C 线实现前，必须先确定 health/status taxonomy；C/G 共享 route exposure、OpenAPI diff 和 consumer matrix。 |
| `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md` | 已记录 5 个 canonical health endpoints、37 个 active fragmented health endpoints、2 个 excluded health-like routes。 |
| `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md` | 确认阻塞点不是 `/health/ready` 缺失，而是健康候选端点过多、prefix 复杂、领域 smoke 与系统探针混杂。 |
| 当前代码字符串扫描 | `/health/readiness` 在 `web/backend`、`web/frontend`、`src`、`scripts`、`tests`、`.github`、`config` 中无代码命中。 |
| 当前代码字符串扫描 | `/api/announcement/health` 仍被 CI / tests / scripts 引用，不能作为无消费者端点处理。 |

## Consumer Matrix

| 消费者类别 | 当前引用 | 处理口径 |
|------------|----------|----------|
| PM2 / ops | `config/pm2.config.js`、`config/pm2/pm2.config.js`、`scripts/run_pm2_integration_workflow.sh` 使用 `/health`，部分脚本同时等待 `/api/health/ready`。 | 保留 `/health` 和 `/api/health/ready`；任何切换必须先改配置并跑 PM2 workflow。 |
| CI workflows | 多个 workflow 使用 `/api/announcement/health || /health/ready` fallback。 | 第一批不得退役 `/api/announcement/health`；先迁移 CI，再评估退役。 |
| Frontend / E2E | `useBackendReadiness` 和多套 E2E 依赖 `/health/ready` / `/api/health/ready` 探针。 | 保留 readiness 双路径；前端只允许后续集中切换到 canonical API client。 |
| Performance / smoke tests | `tests/performance/api_smoke_endpoints.json` 和 performance drift 测试覆盖 `/health`、`/api/health/ready`。 | 将两者作为 G 线最小 smoke 固定点。 |
| Monitoring / Prometheus | 现有测试和监控文档引用 `/health` 的 `http_requests_total` 标签。 | 不改变 `/health` label 语义；若改标签必须同步监控验证。 |
| Scripts | `scripts/run-api-tests.sh`、`scripts/tests/run-api-tests.sh` 等仍使用 `/api/announcement/health`。 | 先迁移脚本消费者，再考虑 domain smoke 退役。 |
| Docs / generated artifacts | 大量历史文档和 generated output 引用 health/status。 | 只作为参考，不作为当前运行事实；当前事实以代码和最近验证为准。 |

## Taxonomy 决策

### 1. Platform Liveness

Canonical endpoint：`GET /health`

语义：进程存活，适合负载均衡、容器、PM2 基础探针使用。该端点不得承担数据库、外部服务或领域模块健康汇总职责。

### 2. Platform Readiness

Canonical endpoint：`GET /health/ready`

Compatibility endpoint：`GET /api/health/ready`

语义：后端应用是否达到可接收 API 流量的就绪状态。两条路径必须保留到 PM2、CI、frontend、E2E、scripts 的消费者迁移完成并有 OpenAPI diff 证据后，才可讨论退役兼容路径。

明确不新增：`GET /health/readiness`

原因：当前代码根无 `/health/readiness` 命中，历史审阅意见中的路径不代表当前实现事实。新增该路径会扩大兼容面，除非后续有明确外部消费者证据。

### 3. System Services Health

Canonical endpoint：`GET /api/health/services`

语义：系统依赖服务检查，包括数据库、磁盘、系统资源或其他基础依赖。该端点不是 liveness，不应被负载均衡器用作轻量存活探针。

Related diagnostic endpoint：`GET /api/health/detailed`

口径：保留为详细诊断或受控运维入口，不作为 readiness canonical endpoint。

### 4. Domain Smoke / Domain Status

代表路径包括但不限于：

- `/api/announcement/health`
- `/api/v1/risk/health`
- `/api/v1/trade/health`
- `/api/v1/strategy/*/status`
- `/api/v1/system/*`

口径：这些端点是领域 smoke/status，不等同平台 liveness/readiness。第一批只记录 owner 和消费者，不退役。

### 5. Metrics / Observability

代表路径：

- `/metrics`
- `/api/metrics`
- `/api/gpu/metrics`
- `/metrics/health`

口径：指标端点归 observability，不纳入平台 health endpoint 退役批次。若路径、标签或 content-type 改变，必须走 OpenAPI/metrics consumer 变更证据。

### 6. Compatibility / Alias

代表路径：

- `/api/health/ready`
- `/api/announcement/health` as CI fallback

口径：兼容路径不是技术债删除对象，必须先完成消费者迁移、OpenAPI diff、smoke 验证和 rollback 说明。

### 7. Excluded / Deferred

`backup_recovery_secure/cleanup_old_backups.py` 的 `/health` 属于 backup 域 route ownership，不归 G 线第一批处理。该路径应由 backup 域后续所有权任务决定是否保留、迁移或退役。

`monitoring_old/routes.py` 的 `/health` 是旧模块残留，应等待对应 old module 删除/归档任务处理，不在 G 线里单独退役。

## Rollback Triggers

以下任一情况发生，必须回滚对应 health/status 变更或恢复兼容路径：

- `/health`、`/health/ready`、`/api/health/ready` 任一路径 smoke 失败。
- PM2 backend health check 失败或服务重启循环。
- CI readiness fallback 失败。
- Frontend readiness composable 或 E2E smoke 失败。
- OpenAPI diff 出现未批准的 health/status path removal、operationId drift、response contract drift。
- Prometheus / monitoring label 从 `/health` 漂移且无同步验证。

## First Implementation Boundary

G 线下一批若进入实现，只允许选择一种最小动作：

1. 文档化 canonical / compatibility path，不改代码。
2. 增加 smoke 测试覆盖 `/health`、`/health/ready`、`/api/health/ready`、`/api/health/services`。
3. 迁移单一 consumer 到 canonical readiness，但保留旧 fallback。

第一批禁止：

- 删除 domain smoke endpoint。
- 删除 `/api/health/ready`。
- 新增 `/health/readiness`。
- 将 `/api/health/services` 当作 liveness 使用。
- 把 backup 域 `/health` 混入 G 线退役范围。

