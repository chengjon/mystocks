# API Contract Runtime Validation Developer Guide

> **使用说明**:
> 本文件是 API 契约 runtime validation 的 current-state developer guide，不是仓库共享规则、OpenAPI 唯一真相源或未来 roadmap 的替代品。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及 API 契约事实源，再以 FastAPI 路由、Pydantic Schema 与运行时导出的 `/openapi.json` 为准。

## Purpose

这份 guide 只说明当前仓库里已经存在的 runtime contract validation 链路、验证入口和边界，不把 OpenSpec 目标态自动等同于现状。

## Current Runtime Truth

当前可确认的 runtime validation 事实分成三层：

1. backend response validation
   - 入口：[`contract_validator.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/contract_validator.py)
   - 能力：按路径、方法、状态码对响应体做 schema 校验，并输出 `ValidationResult`
2. pytest contract fixtures / helpers
   - 入口：[`contract_testing.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/contract_testing.py)
   - 能力：默认加载 runtime-generated OpenAPI，给测试提供 `contract_validator`、`api_client`、`ContractTestMixin`
3. CI workflow gate
   - 入口：[`.github/workflows/api-contract-validation.yml`](/opt/claude/mystocks_spec/.github/workflows/api-contract-validation.yml)
   - 能力：按 contract scope 触发后端 import 校验、OpenAPI generation、documentation regression、frontend type generation 等步骤

## Frontend Boundary

前端当前并没有独立的 schema-enforcing runtime validator class。

当前 repo-truth 是：

- [`unifiedApiClient.ts`](/opt/claude/mystocks_spec/web/frontend/src/api/unifiedApiClient.ts) 只是 `apiClient` 的 legacy wrapper
- 它保留了 `ContractValidationError`、`createLoadingConfig`、`createCacheConfig` 等兼容导出
- [`versionNegotiator.ts`](/opt/claude/mystocks_spec/web/frontend/src/services/versionNegotiator.ts) 负责版本探测、兼容性检查与 fallback，不负责响应 schema 校验

因此“前端 runtime contract validation”在当前仓库里应理解为：
- 前端保留 contract-related error surface 和 version negotiation seam
- 真正的 schema validation 仍主要落在 backend validator 与 CI gate

不要把历史实现报告里提到的 `RuntimeContractValidator` 方案，误读成当前已在 `unifiedApiClient.ts` 落地。

## Canonical Files

- backend validator: [`contract_validator.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/contract_validator.py)
- pytest fixtures: [`contract_testing.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/contract_testing.py)
- contract routes: [`routes.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/routes.py)
- frontend wrapper boundary: [`unifiedApiClient.ts`](/opt/claude/mystocks_spec/web/frontend/src/api/unifiedApiClient.ts)
- frontend version negotiation: [`versionNegotiator.ts`](/opt/claude/mystocks_spec/web/frontend/src/services/versionNegotiator.ts)
- frontend wrapper contract tests: [`unifiedApiClient.contract.test.ts`](/opt/claude/mystocks_spec/web/frontend/src/api/__tests__/unifiedApiClient.contract.test.ts)
- version negotiation unit tests: [`versionNegotiator.spec.ts`](/opt/claude/mystocks_spec/web/frontend/src/services/__tests__/versionNegotiator.spec.ts)
- workflow runtime checks: [`test_ci_workflow_runtime_setup.py`](/opt/claude/mystocks_spec/tests/unit/scripts/test_ci_workflow_runtime_setup.py)

## Local Validation Commands

推荐的 repo-local 验证顺序：

```bash
python -m pytest -q \
  tests/integration/contract/test_contract_executor.py \
  tests/integration/contract/test_contract_generator.py \
  tests/integration/contract/test_contract_validator.py
```

前端单测实际应通过 Vitest 执行：

```bash
cd web/frontend
npm run test -- src/api/__tests__/unifiedApiClient.contract.test.ts
npm run test -- src/services/__tests__/versionNegotiator.spec.ts
```

工作流/文档 gate：

```bash
python -m pytest -q tests/unit/scripts/test_ci_workflow_runtime_setup.py
python scripts/dev/openapi_success_example_audit.py --show-non-json
python -m pytest -q \
  web/backend/tests/test_health_route_conflicts.py \
  web/backend/tests/test_api_documentation_validation.py
```

## Developer Workflow

当你修改 contract-related backend 或 frontend seam 时，按这个顺序做：

1. 先确认契约事实源
   - 看 FastAPI 路由、Pydantic schema、`/openapi.json`
2. 再确认 consumer seam
   - 前端如果涉及版本协商，看 `versionNegotiator.ts`
   - 前端如果涉及兼容错误表面，看 `unifiedApiClient.ts`
3. 跑 backend contract 验证
   - `tests/integration/contract/*`
4. 跑 frontend seam 单测
   - `unifiedApiClient.contract.test.ts`
   - `versionNegotiator.spec.ts`
5. 跑 workflow runtime assertions
   - `tests/unit/scripts/test_ci_workflow_runtime_setup.py`

## Common Misreads To Avoid

- 不要把 `unifiedApiClient.ts` 当成已经具备 full runtime schema validation 的 client
- 不要把历史实施报告中的伪代码当成当前实现
- 不要把 `docs/api/CONTRACT_MANAGEMENT_API.md` 这种 API reference 文档当成 current-state developer guide
- 不要把单次 CI workflow 定义存在，误写成端到端 runtime validation 已闭环

## Out Of Scope

以下内容不属于当前 guide 所覆盖的已落地能力：

- frontend automatic request/response adaptation for version differences
- dedicated `ContractImpactAnalyzer` backend service / UI
- contract-specific Prometheus / Grafana metrics closeout
- external training session closeout
