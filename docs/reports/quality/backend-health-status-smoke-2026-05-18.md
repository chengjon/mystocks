# Backend Health/Status Smoke Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

日期：2026-05-18

关联 OpenSpec change：`consolidate-backend-health-endpoints`

## 结论

G 线首个 smoke 批次已验证 canonical / compatibility health endpoints 的当前运行形态。本批次没有修改后端运行代码，没有新增或删除任何 health/status path。

已验证：

- `GET /health`：存在，返回 JSON，HTTP 200，`data.status=healthy`。
- `GET /health/ready`：存在，返回 JSON，HTTP 200，`data.status=ready`。
- `GET /api/health/ready`：存在，返回 JSON，HTTP 200，`data.status=ready`。
- `GET /api/health/services`：存在，返回 JSON，HTTP 200，`data.status=degraded`。
- `GET /health/readiness`：不在 OpenAPI 中，保持 absent。
- OpenAPI baseline path count 与当前 path count 均为 501；health/status 相关路径无 added / removed diff。

`/api/health/services` 当前返回 degraded，说明依赖服务检查存在非 healthy 子项；这不影响本批次结论，因为该端点的定位是 system services health，不是 liveness 或 readiness。

## Smoke Evidence

执行方式：FastAPI `TestClient(app)` 直接请求当前应用。

| Path | HTTP | JSON | `data.status` | 结论 |
|------|------|------|---------------|------|
| `/health` | 200 | yes | `healthy` | liveness path 可访问 |
| `/health/ready` | 200 | yes | `ready` | canonical readiness path 可访问 |
| `/api/health/ready` | 200 | yes | `ready` | compatibility readiness path 可访问 |
| `/api/health/services` | 200 | yes | `degraded` | system services health path 可访问 |

所有返回均包含统一响应顶层字段：

```text
code, data, errors, message, request_id, success, timestamp
```

## OpenAPI Diff Evidence

对比文件：`docs/reports/quality/generated/openapi-before.json`

结果：

```text
baseline_path_count = 501
current_path_count = 501
added_paths = 0
removed_paths = 0
```

Health path 对比：

| Path | Baseline | Current |
|------|----------|---------|
| `/health` | present | present |
| `/health/ready` | present | present |
| `/api/health/ready` | present | present |
| `/api/health/services` | present | present |
| `/api/health/detailed` | present | present |
| `/health/readiness` | absent | absent |

## Regression Test Evidence

Targeted endpoint label test passed:

```text
pytest -o addopts= web/backend/tests/test_performance_middleware_endpoint_labels.py -q --no-cov
3 passed in 0.75s
```

Broader historical OpenAPI documentation suite was executed for visibility:

```text
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov
108 passed, 5 failed in 82.96s
```

The 5 failures are not introduced by this G-line smoke batch and are not health taxonomy implementation failures:

| Failing test | Observed issue |
|--------------|----------------|
| `test_health_routes_are_unique_and_domain_scoped` | Existing duplicate operationId warning from `strategy_mgmt` compatibility redirect. |
| `test_announcement_endpoints_have_examples_parameter_docs_and_error_responses` | Historical `/api/v1/announcement/announcement/*` expectations no longer match current OpenAPI paths. |
| `test_kline_data_endpoints_have_docs_examples_and_error_responses` | Example shape lacks expected `code` field. |
| `test_sentiment_endpoint_has_docs_examples_and_parameter_descriptions` | Example data lacks expected `sentiment` field. |
| `test_position_write_endpoints_have_request_and_response_examples` | Example data lacks expected `session_id` field. |

Therefore OpenSpec task `4.6` remains open. It should not be marked complete until either this broader suite is stabilized or the approved implementation issue names a narrower affected-test subset.

## Closure Boundary

Closed by this evidence:

- `4.1 Run /health/ready smoke`
- `4.2 Run /api/health/ready smoke`
- `4.3 Run /api/health/services smoke`
- `4.5 Run OpenAPI diff and classify changes`
- `5.1 Update health/status endpoint documentation with canonical and compatibility paths`

Still open:

- `4.4` canonical status endpoint smoke, because no non-health canonical status path has been approved yet.
- `4.6` affected backend/frontend smoke, because the broad historical OpenAPI suite has existing unrelated failures.
- `4.7` PM2 backend status and configured health checks.
- `5.2` retained domain smoke/status endpoint owner registry.
- `5.3` retired endpoint and rollback notes; no endpoint was retired in this batch.

