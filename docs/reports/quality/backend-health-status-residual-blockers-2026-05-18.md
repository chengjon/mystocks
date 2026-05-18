# Backend Health/Status Consolidation Residual Blockers

日期: 2026-05-18  
OpenSpec change: `consolidate-backend-health-endpoints`  
范围: G 线健康 / 状态端点整合剩余门禁判定

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 结论

当前 G 线已完成健康 / 状态端点的 taxonomy、canonical smoke、OpenAPI diff、status owner registry 和 PM2 只读状态确认。

2026-05-18 update:

- `4.6` 已由 `docs/reports/quality/backend-health-status-openapi-stabilization-2026-05-18.md` 覆盖并关闭。
- `4.7` 已由 `docs/reports/quality/backend-health-status-pm2-gate-2026-05-18.md` 覆盖并关闭。
- 本报告保留为执行完整 PM2 gate 前的残留风险快照，不再代表当前最终任务状态。

执行本报告时仍不关闭以下任务:

- `4.6 Run affected backend tests and frontend/API smoke.`
- `4.7 Confirm PM2 backend status and configured health checks with pm2 list and ./scripts/run_pm2_integration_workflow.sh or a named equivalent approved by the implementation issue.`

当时不关闭原因不是健康端点 smoke 失败，而是剩余门禁已经跨出本线可安全自主完成边界。

## 4.6 残留项

已执行:

- `pytest -o addopts= web/backend/tests/test_performance_middleware_endpoint_labels.py -q --no-cov`
- 结果: `3 passed`

已执行:

- `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov`
- 结果: `108 passed, 5 failed`

失败项归因:

- `_strategy_mgmt_compat.py` 兼容重定向路由仍产生 duplicate operationId warning。
- announcement OpenAPI 文档测试仍引用已不存在的 `/api/v1/announcement/announcement/health` 与 `/api/v1/announcement/announcement/status` 路径。
- data/kline success example 缺少测试期望字段 `code`。
- sentiment success example 缺少测试期望字段 `sentiment`。
- position write success example 缺少测试期望字段 `session_id`。

判定:

- 上述 5 项均不是 `consolidate-backend-health-endpoints` 本批次引入的健康端点行为回归。
- 修复范围会进入 strategy compatibility、announcement、data/kline、sentiment、trade position 等多个业务域的 OpenAPI 文档 / schema 治理。
- 在 G 线中直接修复会扩大变更边界，且可能与并行合同治理线重叠。

建议后续处理:

- 作为独立 OpenAPI documentation stabilization 批次处理。
- 不用健康端点整合线强行承接跨域 schema/example 债务。
- 若必须关闭 `4.6`，应先批准跨域 OpenAPI 文档修复范围，再按路径级提交执行。

## 4.7 残留项

已执行只读确认:

- `pm2 list`
- live probe:
  - `http://localhost:8020/health`
  - `http://localhost:8020/api/health/ready`
  - `http://localhost:8020/api/health/services`
  - `http://localhost:8020/api/status`
  - `http://localhost:3020/`

只读结果:

- `mystocks-backend`: online
- `mystocks-frontend`: online
- backend health/readiness/status probes: HTTP 200
- frontend root probe: HTTP 200

当前补充快照:

- `pm2 list` 采样结果显示 `mystocks-backend` 与 `mystocks-frontend` 均为 `online`，且未出现重启抖动。
- `http://localhost:8020/health` 返回 HTTP 200，`success=true`，`status=healthy`。
- `http://localhost:8020/health/ready` 返回 HTTP 200，`success=true`，`status=ready`。
- `http://localhost:8020/api/health/ready` 返回 HTTP 200，`success=true`，`status=ready`。
- `http://localhost:8020/api/health/services` 返回 HTTP 200，`success=true`，`status=degraded`。
- `http://localhost:3020/` 返回 HTTP 200，前端壳可访问。

未执行:

- `./scripts/run_pm2_integration_workflow.sh gate`

未执行原因:

- 该脚本的 gate 流程包含 `pm2 stop all` 与 `pm2 delete all`。
- 这不是只读验证，会重启 / 重建本地 PM2 进程状态。
- 执行本报告时，用户尚未批准执行会变更服务运行态的完整 PM2 gate。

后续状态:

- 用户已批准 stateful PM2 gate。
- `./scripts/run_pm2_integration_workflow.sh gate` 已通过。
- 关闭证据见 `docs/reports/quality/backend-health-status-pm2-gate-2026-05-18.md`。

建议后续处理:

- `4.7` 已关闭；无需再批准 named equivalent。

## 当前可关闭与不可关闭边界

可认为已闭合:

- canonical liveness: `GET /health`
- canonical readiness: `GET /health/ready`
- compatibility readiness: `GET /api/health/ready`
- canonical services health: `GET /api/health/services`
- status owner registry:
  - `/api/status`
  - `/api/socketio-status`
  - `/api/trading/status`
  - `/api/notification/status`
- OpenAPI path diff: no added or removed paths in this batch

执行完整 gate 前不可伪造完成:

- 跨域 OpenAPI 文档测试全绿
- 会重启 PM2 的完整 integration workflow
- 未经批准的 endpoint retirement

## 下一步建议

1. 保持 `consolidate-backend-health-endpoints` 当前实现边界不扩张。
2. 提交 / 归档前引用 `4.6` 与 `4.7` 的新关闭证据。
3. 后续 endpoint retirement 仍需独立审批，不能借本报告扩大删除范围。
4. 在上述两项完成前，不 archive 该 OpenSpec change。
