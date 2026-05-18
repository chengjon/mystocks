# API Contract CI/CD Local Dry-Run Rerun

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

日期：2026-05-18

关联 OpenSpec change：`enhance-api-contract-management-integration`

## 结论

`.github/workflows/api-contract-validation.yml` 的 repository-local 等价验证已闭合。此前阻塞 8.2 的 OpenAPI 文档回归门、JSON success example audit、`backend_api_documentation` collector 均已通过。

本次不声明 GitHub Actions 云端实跑成功；结论限定为本地 workflow-equivalent dry-run 通过。

## 执行范围

本次按 workflow 关键步骤复测：

1. Contract models / schemas / services import。
2. `OpenAPIGenerator.scan_app(app)` + `generate_spec()`。
3. `web/backend/tests/test_api_documentation_validation.py` 文档回归门。
4. `scripts/dev/openapi_success_example_audit.py --show-non-json`。
5. `collect_backend_api_documentation()` collector。

## 通过证据

### Contract Import

命令等价于 workflow 的 `Validate contract models and services` 步骤。

结果：

```text
contract imports ok
```

### OpenAPI Generation

命令等价于 workflow 的 `Validate OpenAPI generation` 步骤，并显式调用 `generator.scan_app(app)`。

结果：

```text
openapi generation ok paths=504
```

### Documentation Regression Gate

命令：

```bash
pytest -o addopts= web/backend/tests/test_api_documentation_validation.py -q --no-cov
```

结果：

```text
16 passed in 15.46s
```

### Success Example Audit

命令：

```bash
python scripts/dev/openapi_success_example_audit.py --show-non-json
```

结果：

```text
JSON_SUCCESS_MISSING_EXAMPLES 0
NON_JSON_SUCCESS_RESPONSES 4
GET /api/v1/trade/reconciliation/export 200 [text/csv]
GET /api/metrics 200 [text/plain]
GET /api/gpu/metrics 200 [text/plain]
GET /metrics 200 [text/plain]
```

说明：4 个 non-JSON success response 是显式非 JSON 媒体类型，不计入 JSON success example 缺口。

### backend_api_documentation Collector

命令等价于 workflow 的 `Validate backend_api_documentation collector` 步骤。

结果：

```json
{
  "documented_endpoints": 538,
  "endpoints_with_errors": 538,
  "endpoints_with_examples": 537,
  "json_success_missing_examples": 0,
  "non_json_success_responses": 4,
  "total_endpoints": 538
}
```

## 支撑测试

本次额外执行了受影响路径的目标测试：

```text
web/backend/tests/test_api_documentation_validation.py
web/backend/tests/test_trade_execution_tracking_routes.py
web/backend/tests/test_trade_reconciliation_routes.py
```

结果：

```text
35 passed in 15.54s
```

Contract route / alert / impact / drift 相关测试：

```text
26 passed, 2 warnings in 3.00s
```

Backup recovery secure file tests：

```text
20 passed in 0.21s
```

Ruff targeted check：

```text
All checks passed!
```

## 本次修复口径

本次只修复契约生成、契约元数据和测试门禁问题，不改变业务执行逻辑：

- 为 execution tracking、trade reconciliation、batch analysis、ML workbench、advanced analysis、backup recovery、legacy strategy-mgmt 等路径补齐 OpenAPI success response examples、request examples、error responses、参数说明和 schema 字段说明。
- 在 `openapi_config.py` 既有 schema description patcher 中加入有限白名单，补齐 FastAPI 自动生成 request body schema 与 legacy schema 的描述。
- 修正文档门禁对 FastAPI catch-all route path 的匹配逻辑：`/{path:path}` 在 OpenAPI 中标准化为 `/{path}`，校验器应按 OpenAPI path-template 归一化后匹配。
- 修复 `backup_recovery_secure.log_security_event` 的 `verify_recovery_permission` re-export 导入缺口，避免 app import 被无关兼容导出阻断。

## 旁路风险

本次目标测试中额外探测到 `web/backend/tests/test_v1_batch_analysis_workbench_contract.py` 与 `web/backend/tests/test_v1_ml_workbench_contract.py` 失败，主要症状为 `app.api.v1.strategy.machine_learning` facade 未导出 batch / ML workbench 符号。

该失败不属于 `.github/workflows/api-contract-validation.yml` 的 contract validation 步骤，也不是本次 OpenAPI 元数据修复引入的断言失败。建议另立 7.x strategy ML facade 收口任务处理，不纳入 8.2 阻塞。

## 环境噪声

复测过程中仍可见本地 PostgreSQL `127.0.0.1:5438` 不可达、Mock backtest 数据源降级等日志。这些日志没有导致上述 contract workflow-equivalent 步骤失败。

## 8.2 判定

`8.2 Test CI/CD integration with contract validation` 可在 repository-local 范围内勾选完成。

尚未闭合项仍为 `7.5 Organize contract management training session`，该项属于外部培训/会议动作，不能通过仓库内代码或文档伪造完成态。
