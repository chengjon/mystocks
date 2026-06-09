# Reports Trunk Wave 2

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/reports/README.md` 的 canonical-retention 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前治理口径、审批门禁或文档系统 trunk，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

## Why

- `docs/reports/README.md` 实际已经是 canonical historical-evidence trunk
- decision register 里这条仍停留在 `open`
- `reports-root-refinement-wave1` 已经完成正文收敛，本波次只需要把 register 与自动化验证追平当前事实

## Changes

- 将 `docs/reports/README.md` 在 decision register 中收口为已执行
- 新增一条 hygiene 测试，固定：
  - `docs/README.md` 继续把读者路由到 `docs/reports/README.md`
  - `docs/reports/README.md` 继续保持 historical-evidence trunk 角色

## Validation Basis

- `docs/README.md` 当前仍把“历史证据”路由到 `docs/reports/README.md`
- `docs/reports/README.md` 当前明确：
  - 自身是 canonical historical-evidence entrypoint
  - 当前规则应回到 `architecture/STANDARDS.md`
  - 治理执行证据应回到 `docs/reports/documentation-governance/`

## Outcome

- `docs/reports/README.md` 的 register 状态与仓库当前事实对齐
- reports 根 trunk 的角色不再只停留在 wave1 报告里，而是有测试和台账共同兜底

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_reports_readme_remains_canonical_historical_evidence_trunk \
  -q -o addopts=''

python scripts/compliance/markdown_governance_gate.py --root-dir . \
  docs/reports/documentation-governance/2026-04-08-reports-trunk-wave2.md \
  docs/reports/documentation-governance/2026-04-08-decision-register.md

python scripts/governance/audit_documentation_system.py --root-dir . --format text
```
