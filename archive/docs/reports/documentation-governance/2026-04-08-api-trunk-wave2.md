# API Trunk Wave 2

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/api/README.md` 的 canonical-retention 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前治理口径、审批门禁或 API 真相源，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、FastAPI routes、Pydantic schema 与导出的 OpenAPI 为准。

## Why

- `docs/api/README.md` 实际已经是 canonical API navigation trunk
- decision register 里这条仍停留在 `open`
- hygiene tests 里仍有一部分基于旧假设，要求 `docs/api/INDEX.md` 暴露 supporting leaf docs，或要求 `docs/api/README.md` 继续平铺 integration leaf links

## Changes

- 将 `docs/api/README.md` 在 decision register 中收口为已执行
- 刷新 `tests/unit/scripts/test_repository_hygiene_paths.py` 中 2 个与 API trunk 对应的断言集合
- 新口径明确区分：
  - `docs/api/README.md` 是 canonical navigation trunk
  - 真实契约仍是 FastAPI routes + Pydantic schema + OpenAPI
  - `docs/api/INDEX.md` 是 secondary index，只暴露 preferred entrypoints
  - integration / support leaf docs 继续保留在 family index、supporting docs 与 cleanup index 中

## Validation Basis

- `docs/README.md` 继续把读者路由到 `docs/api/README.md`
- `docs/api/README.md` 继续保留：
  - contract-truth precedence
  - retained root reference docs
  - API development guidance routing
- `docs/api/INDEX.md` 当前只暴露 preferred entrypoints，而不再承担 broad flat index 职责

## Outcome

- API canonical trunk 的 register 状态与仓库当前事实对齐
- hygiene tests 不再要求 secondary index 回退为 supporting leaf 的平铺索引
- trunk-first 与 contract-first 的边界更加明确

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_api_endpoints_statistics_report_is_converged_under_docs_api_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_api_validation_and_error_guides_are_converged_under_docs_api_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_api_alignment_and_contract_plan_guides_are_converged_under_docs_api_guides_integration \
  -q -o addopts=''

python scripts/compliance/markdown_governance_gate.py --root-dir . \
  docs/reports/documentation-governance/2026-04-08-api-trunk-wave2.md \
  docs/reports/documentation-governance/2026-04-08-decision-register.md

python scripts/governance/audit_documentation_system.py --root-dir . --format text
```
