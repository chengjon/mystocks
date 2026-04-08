# Governance Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/governance/` 的第一轮 bounded 收敛执行，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前治理口径、审批门禁或文档系统 trunk，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

## Why

- `docs/guides/governance/INDEX.md` 仍是自动生成式 family index
- decision register 已明确该 subtree 应保留为 `keep-supporting`
- 但如果 family index 继续维持 catch-all 形态，读者容易把该目录误读成仓库级治理真相层

## Changes

- 将 `docs/guides/governance/INDEX.md` 改为 transition index
- 明确当前阅读顺序为：
  - `architecture/STANDARDS.md`
  - `docs/overview/documentation-system.md`
  - family 内的 supporting workflow guides
- 保留 `FEATURE_MANAGEMENT_WORKFLOW.md` 与 `TECHNICAL_DEBT_MANAGEMENT.md` 作为专题 supporting guides
- 更新 decision register，把 `docs/guides/governance/` 记录为 `governance wave 1` 已执行批次

## Why Keep The Family

当前两份专题文档仍有明确用途：

- `FEATURE_MANAGEMENT_WORKFLOW.md`
  - 覆盖功能树、task card / PR 镜像与功能状态同步流程
- `TECHNICAL_DEBT_MANAGEMENT.md`
  - 覆盖技术债识别、分级和治理的专题执行细则

因此本波次只收敛 family 入口，不删除专题文档本体。

## Outcome

- `docs/guides/governance/` 不再以并行 governance trunk 的姿态出现
- 读者与 AI 会先被路由到 `architecture/STANDARDS.md` 与 `documentation-system.md`
- family 内文档继续保留，但被限定为 `supporting` 角色

## Validation

```bash
python scripts/compliance/markdown_governance_gate.py --root-dir . \
  docs/guides/governance/INDEX.md \
  docs/reports/documentation-governance/2026-04-08-governance-family-wave1.md \
  docs/reports/documentation-governance/2026-04-08-decision-register.md

python scripts/governance/audit_documentation_system.py --root-dir . --format text

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_governance_guides_are_converged_under_guides_governance_family \
  -q -o addopts=''
```
