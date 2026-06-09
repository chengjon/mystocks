# Operations Testing Trunks Wave 2

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/operations/README.md` 与 `docs/testing/README.md` 的 canonical-retention 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前治理口径、审批门禁或文档系统 trunk，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

## Why

- `docs/operations/README.md` 与 `docs/testing/README.md` 实际已经处于 canonical trunk 形态
- decision register 里这两条仍停留在 `open`
- hygiene tests 仍有一部分基于旧假设，继续要求 secondary index 平铺全部 leaf docs，或要求 README 保留旧式相对链接写法

## Changes

- 将 `docs/operations/README.md` 与 `docs/testing/README.md` 在 decision register 中收口为已执行
- 刷新 `tests/unit/scripts/test_repository_hygiene_paths.py` 中与 operations/testing trunk 对应的 3 个断言集合
- 新口径明确区分：
  - `README.md` 是 canonical trunk
  - `INDEX.md` 是 secondary index
  - supporting / compatibility leaves 可以保留，但不必全部暴露在 secondary index 中

## Validation Basis

- `docs/README.md` 仍把读者路由到：
  - `docs/operations/README.md`
  - `docs/testing/README.md`
- `docs/operations/INDEX.md` 当前只暴露 preferred runbook families 与 selected root runbooks
- `docs/testing/INDEX.md` 当前只暴露 preferred testing docs
- supporting / compatibility docs 继续保留在 README、supporting docs 或 cleanup index 中，而不是重新回到平铺索引

## Outcome

- operations/testing 两个 canonical trunks 的 register 状态与仓库当前事实对齐
- hygiene tests 不再要求文档回退到旧式“全量叶子平铺”结构
- 文档治理继续保持 trunk-first，而不是把 secondary index 重新膨胀成 broad catch-all surface

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_operational_guides_are_converged_under_docs_operations_families \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_quick_start_guide_is_converged_under_docs_operations_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_testing_specialized_guides_are_converged_under_docs_testing_family \
  -q -o addopts=''

python scripts/compliance/markdown_governance_gate.py --root-dir . \
  docs/reports/documentation-governance/2026-04-08-operations-testing-trunks-wave2.md \
  docs/reports/documentation-governance/2026-04-08-decision-register.md

python scripts/governance/audit_documentation_system.py --root-dir . --format text
```
