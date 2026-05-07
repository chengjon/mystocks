# API Contract Testing Best Practices

> **使用说明**:
> 本文件说明当前仓库里 API contract testing 的推荐执行方式与目录口径，不替代 OpenAPI 真相源、仓库共享规则或 CI 历史报告。
> 共享规则仍以 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md) 为准；接口事实仍以 FastAPI 路由、Pydantic Schema 与 `/openapi.json` 为准。

## Current Test Layout

当前仓库是“三层并存”状态：

- current backend integration entry
  - [`tests/integration/contract/`](/opt/claude/mystocks_spec/tests/integration/contract)
- current unit / repo-truth checks
  - [`tests/unit/contract/`](/opt/claude/mystocks_spec/tests/unit/contract)
- current canonical support implementation package
  - [`tests/contract_support/`](/opt/claude/mystocks_spec/tests/contract_support)
- retained legacy contract tree
  - [`tests/contract/`](/opt/claude/mystocks_spec/tests/contract)

这意味着：
- 新增 contract tests 优先落在 `tests/integration/contract/` 或 `tests/unit/contract/`
- contract framework/support code 的 canonical 主实现应优先落在 `tests/contract_support/`
- `tests/contract/` 仍保留为 legacy tree，不能再把它当唯一 canonical 目录
- `tests/contract/` 当前更接近 support / compatibility tree；真实 pytest case 已优先迁入主测试结构

## Canonical Helpers

优先复用这些 helper，而不是自行拼一套 schema loader：

- runtime OpenAPI loader and fixtures:
  [`contract_testing.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/contract_testing.py)
- validator core:
  [`contract_validator.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/contract_validator.py)

关键 repo-truth：
- 默认契约来源是运行时生成的 OpenAPI
- 显式 `spec_path` / `openapi_spec_path` 只作为 compatibility override

## Preferred Test Types

### 1. Integration contract tests

适用场景：
- 验证真实 FastAPI 路由响应是否匹配当前 OpenAPI
- 验证 generator / validator / executor 的集成行为

现有入口：
- [`test_contract_executor.py`](/opt/claude/mystocks_spec/tests/integration/contract/test_contract_executor.py)
- [`test_contract_generator.py`](/opt/claude/mystocks_spec/tests/integration/contract/test_contract_generator.py)
- [`test_contract_validator.py`](/opt/claude/mystocks_spec/tests/integration/contract/test_contract_validator.py)
- [`test_api_contract_schemathesis.py`](/opt/claude/mystocks_spec/tests/integration/contract/test_api_contract_schemathesis.py)

### 2. Unit repo-truth tests

适用场景：
- 校验 helper、runtime source、workflow wiring
- 避免 regression 把 runtime-generated OpenAPI 又退回静态 spec truth

现有入口：
- [`test_contract_support_aliases.py`](/opt/claude/mystocks_spec/tests/unit/contract/test_contract_support_aliases.py)
- [`test_contract_engine_runtime_source.py`](/opt/claude/mystocks_spec/tests/unit/contract/test_contract_engine_runtime_source.py)
- [`test_risk_router_runtime_import.py`](/opt/claude/mystocks_spec/tests/unit/contract/test_risk_router_runtime_import.py)
- [`test_ci_workflow_runtime_setup.py`](/opt/claude/mystocks_spec/tests/unit/scripts/test_ci_workflow_runtime_setup.py)

### 3. Frontend seam tests

适用场景：
- 验证前端 contract-related compatibility seam
- 验证 version negotiation 的 fallback truth

现有入口：
- [`unifiedApiClient.contract.test.ts`](/opt/claude/mystocks_spec/web/frontend/src/api/__tests__/unifiedApiClient.contract.test.ts)
- [`versionNegotiator.spec.ts`](/opt/claude/mystocks_spec/web/frontend/src/services/__tests__/versionNegotiator.spec.ts)

## Recommended Commands

Backend contract suite:

```bash
python -m pytest -q \
  tests/integration/contract/test_contract_executor.py \
  tests/integration/contract/test_contract_generator.py \
  tests/integration/contract/test_contract_validator.py
```

Unit repo-truth contract checks:

```bash
python -m pytest -q \
  tests/unit/contract/test_contract_support_aliases.py \
  tests/unit/contract/test_contract_engine_runtime_source.py \
  tests/unit/contract/test_risk_router_runtime_import.py \
  tests/unit/scripts/test_ci_workflow_runtime_setup.py
```

Frontend seam checks:

```bash
cd web/frontend
npm run test -- src/api/__tests__/unifiedApiClient.contract.test.ts
npm run test -- src/services/__tests__/versionNegotiator.spec.ts
```

## Writing New Contract Tests

推荐流程：

1. 明确要测哪一层
   - backend route / validator / generator
   - workflow wiring
   - frontend compatibility seam
2. 优先复用 `contract_testing.py` 的 fixtures 与 helper
3. 默认基于 runtime-generated OpenAPI 断言
4. 只有在历史快照回放或隔离场景下，才使用显式 `spec_path`
5. 对 breaking change 检查，优先联动 `/api/contracts/validate` 或 `/api/contracts/diff`

## Marker Guidance

当前 helper 会注册：
- `contract`
- `contract_validation`

如果是新增 pytest case，优先沿用这些现有 marker，不要再造平行 marker 名称。

## Anti-Patterns

- 不要只在 `tests/contract/` 增加新案例，然后宣称已完成主测试结构迁移
- 不要把静态 spec 文件当默认事实源，绕过运行时 OpenAPI
- 不要把 frontend wrapper compatibility test 误写成 full runtime schema validation test
- 不要把 workflow 定义存在，误写成 CI 实跑闭环已经得到最新证据
