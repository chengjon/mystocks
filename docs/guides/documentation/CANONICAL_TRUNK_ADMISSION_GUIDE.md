# Canonical Trunk Admission Guide

> **参考指南说明**:
> 本文件是文档准入与治理执行的 lightweight operating guide，不是仓库共享规则或当前 trunk map 的唯一事实来源。
> 若涉及审批门禁、删除判定或共享规则，请优先遵循 `architecture/STANDARDS.md` 与 [`docs/overview/documentation-system.md`](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)。

## Purpose

这份指南只回答两个问题：

1. 新文档应该如何进入当前文档系统
2. 遇到 stale 文档时默认应该怎么治理

## Admission Workflow

新增或重写文档时，按以下顺序执行：

1. 先识别 concern
   - 共享规则：`architecture/STANDARDS.md`
   - 当前 capability truth：`openspec/specs/`
   - 已批准变更：`openspec/changes/`
   - 运行/runbooks：`docs/operations/README.md`
   - 测试 guidance：`docs/testing/README.md`
   - API 导航：`docs/api/README.md`
   - 历史证据：`docs/reports/README.md`
2. 判断是否已有 canonical trunk
   - 若已有：优先更新 trunk 或在 trunk 下新增 supporting doc
   - 若没有，且属于能力/架构/治理变化：先走 OpenSpec proposal
3. 选择 lifecycle
   - `canonical`
   - `supporting`
   - `report`
   - `plan`
   - `generated_reference`
   - `archive_candidate`
   - `delete_candidate`
4. 再决定目录与文件名
   - 不允许先随手落盘，再事后解释“它属于哪里”

## Default Remediation Order

发现 stale 文档时，默认 remediation 顺序是：

1. 确认 canonical trunk
2. 更新根入口、README、INDEX 与 active links
3. 执行 bounded `archive` 或 `delete`
4. 仅在确有短期过渡需要时，保留一次性 rewrite

默认策略不是逐份补免责声明。

也就是说，若 replacement 已存在且 retention / compatibility gate 已满足，优先执行：

```text
delete/archive > rewrite
```

## When Rewrite Is Allowed

只有在以下场景才应把 rewrite 作为主要动作：

- 需要短期 transition index
- 需要兼容旧链接
- 需要保留极少量 reader routing 提示
- archive/delete 条件尚未满足，但 trunk 已明确

## Minimum Checks Before Merging

```bash
python scripts/compliance/markdown_governance_gate.py --root-dir . --format text
python scripts/governance/audit_documentation_system.py --format text
```

若本次改动涉及 OpenSpec：

```bash
openspec validate <change-id> --strict
```

## Anti-Patterns

- 先新增并行 README/INDEX，再事后宣称它只是“辅助文档”
- 对一批 stale 文档逐份补说明，但不先定义 trunk
- 让历史报告、计划稿、compatibility leaf 与 canonical trunk 并列表达“当前真相”
- 仅凭“暂时方便导航”长期保留 broad catch-all index

## Related Files

- [`docs/README.md`](/opt/claude/mystocks_spec/docs/README.md)
- [`docs/overview/documentation-system.md`](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)
- [`config/governance/documentation-taxonomy.yaml`](/opt/claude/mystocks_spec/config/governance/documentation-taxonomy.yaml)
- [`scripts/governance/audit_documentation_system.py`](/opt/claude/mystocks_spec/scripts/governance/audit_documentation_system.py)
