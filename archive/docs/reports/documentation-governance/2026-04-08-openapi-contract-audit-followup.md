# OpenAPI Contract Audit Follow-up

> **历史/治理说明**:
> 本文件记录 `2026-04-08` 这轮 OpenAPI 文档债治理的实际审计口径与验证结果。
> 若需确认当前共享规则、当前执行流程或当前契约事实源，请优先回到 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、FastAPI routes、Pydantic schema 与实际导出的 `/openapi.json`。

## Purpose

本记录用于冻结以下结论：

- OpenAPI success example 审计必须区分 JSON 契约债与非 JSON 观察项
- Prometheus / OpenMetrics `text/plain` 端点不是 JSON 契约缺陷
- 后续不应再使用“只看成功响应里是否存在 `application/json` example，否则一律记缺口”的临时 one-liner 作为唯一口径

## Measured Result

实测日期：

- `2026-04-08`

实测命令：

```bash
python scripts/dev/openapi_success_example_audit.py --show-non-json
```

实测结果：

```text
JSON_SUCCESS_MISSING_EXAMPLES 0
NON_JSON_SUCCESS_RESPONSES 3
GET /api/metrics 200 [text/plain]
GET /api/gpu/metrics 200 [text/plain]
GET /metrics 200 [text/plain]
```

## Contract Interpretation

- `application/json` 成功响应必须带 `example` 或 `examples`
- `204` 成功响应不要求 example
- `text/plain` Prometheus/OpenMetrics 成功响应必须按真实媒体类型建模，不得为了“清零”伪造空的 JSON 成功响应
- 非 JSON 成功响应可以保留在审计输出中作为观察项，但不得和 JSON 契约债混算

## Code and CI Entry Points

- 审计脚本：
  [`scripts/dev/openapi_success_example_audit.py`](/opt/claude/mystocks_spec/scripts/dev/openapi_success_example_audit.py)
- 文档校验测试：
  [`web/backend/tests/test_api_documentation_validation.py`](/opt/claude/mystocks_spec/web/backend/tests/test_api_documentation_validation.py)
- `text/plain` 路由断言：
  [`web/backend/tests/test_health_route_conflicts.py`](/opt/claude/mystocks_spec/web/backend/tests/test_health_route_conflicts.py)
- CI 入口：
  [`api-contract-validation.yml`](/opt/claude/mystocks_spec/.github/workflows/api-contract-validation.yml)
- API 合规入口：
  [`api-compliance-testing.yml`](/opt/claude/mystocks_spec/.github/workflows/api-compliance-testing.yml)
- 本地合规入口：
  [`setup_compliance_testing.sh`](/opt/claude/mystocks_spec/scripts/setup_compliance_testing.sh)

## Closure Notes

- 本轮已把 3 个 Prometheus 文本端点的 OpenAPI 成功响应显式收敛为 `text/plain`
- 本轮已把 success example 审计脚本接入主 workflow、本地合规脚本与脚本说明
- 当前剩余 3 项不是 OpenAPI JSON 文档债，而是非 JSON 成功响应观察项
