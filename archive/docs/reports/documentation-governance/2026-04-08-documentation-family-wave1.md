# Documentation Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/documentation/` 的第一轮 bounded 收敛执行，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档 trunk、治理口径或执行入口，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

## Why

- `docs/guides/documentation/INDEX.md` 仍是自动生成式 catch-all index
- 该 family 已被 decision register 标记为 `merge-into-trunk`
- canonical documentation governance trunk 已经明确为 `docs/overview/documentation-system.md`
- 但 `DOCUMENTATION_WORKFLOW_GUIDE.md`、目录治理方法论文档、拆分指南等仍被多处计划、评审和 AI guide 直接引用，暂不满足 delete gate

## Changes

- 将 `docs/guides/documentation/INDEX.md` 改为 transition index
- 明确当前阅读顺序为：
  - `docs/overview/documentation-system.md`
  - `CANONICAL_TRUNK_ADMISSION_GUIDE.md`
  - family 内的 supporting/reference guides
- 保留 `DOCUMENTATION_WORKFLOW_GUIDE.md` 作为 active supporting workflow guide
- 保留 `文件目录整理方法论指南.md`、`文件目录管理方案.md`、`文档管理指南.md`、`文档结构说明.md`、`超长文档拆分办法.md` 作为专题 supporting/reference guides
- 更新 decision register，把 `docs/guides/documentation/` 记录为 `documentation wave 1` 已执行批次

## Why Not Delete The Specialized Guides Yet

当前仍存在直接入链：

- `docs/guides/ai-tools/CLAUDE.md`
- `docs/plans/2026-03-09-repository-hygiene-governance-implementation-plan.md`
- `docs/plans/code_refactoring_plan.md`
- `docs/reports/reviews/PROJECT_STRUCTURE_PLAN_REVIEW.md`

因此本波次只收敛 family 入口，不对专题指南做逐份 archive/delete。

## Outcome

- `docs/guides/documentation/` 不再以并行 governance trunk 的姿态出现
- 读者与 AI 会先被路由到 `documentation-system.md`
- 旧的专题指南继续留在 family 内，但被限制为 `supporting/reference` 角色
- 该批次符合 trunk-first，而不是 file-by-file disclaimer remediation

## Validation

```bash
python scripts/compliance/markdown_governance_gate.py --root-dir . \
  docs/guides/documentation/INDEX.md \
  docs/reports/documentation-governance/2026-04-08-documentation-family-wave1.md \
  docs/reports/documentation-governance/2026-04-08-decision-register.md

python scripts/governance/audit_documentation_system.py --root-dir . --format text

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_documentation_process_guides_are_converged_under_guides_documentation_family \
  -q -o addopts=''
```
