# Taxonomy Refinement Wave 2

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 在第二轮 taxonomy refinement 中，对剩余未分类文档桶的机器可读收口结果。

## Why

- 第一轮清理后，全局仍有 `270` 个 `unclassified`
- 剩余问题主要集中在历史目录和补充目录，而不是 canonical trunk 本身
- 这些路径更适合通过 taxonomy 明确生命周期，而不是逐篇重写正文

## Scope

本轮新增分类规则覆盖以下剩余桶：

- `docs/architecture/`
- `docs/plans/`
- `docs/standards/`
- `docs/design/`
- `docs/references/`
- `docs/worklogs/`
- `docs/web-dev/`
- `architecture/INDEX.md`
- `architecture/DOMAIN_BOUNDARIES.md`
- `docs/FUNCTION_TREE.md`
- `openspec/OPENSPEC_CONVENTIONS.md`
- `openspec/changes/check-report.md`
- `openspec/changes-*/**/*.md`

## Classification Decisions

- `docs/plans/` 明确为 `plan`，`docs/plans/INDEX.md` 作为 `generated_reference`
- `docs/worklogs/claude-auto/*.md` 明确为 `report`，`docs/worklogs/INDEX.md` 作为 `generated_reference`
- `docs/web-dev/*.md` 归入 `supporting`
- `docs/references/` 归入参考/ supporting 家族，索引文件单列为 `generated_reference`
- `docs/design/update/` 归入 `plan`，其余设计资料归入 `supporting`
- `docs/architecture/legacy-cn/` 明确为 `archive_candidate`
- `docs/architecture/` 其余 Markdown 归入 `supporting`，`INDEX.md` 单列为 `generated_reference`
- `architecture/*.md` 由 `repository-standards` trunk 承接，`INDEX.md` 作为 secondary index
- 零散 OpenSpec 边缘文件按实际语义归入 `supporting`、`report` 或 `plan`

## Validation Snapshot

执行口径：

- `python -c "from pathlib import Path; from scripts.governance.audit_documentation_system import build_report; import json; report=build_report(Path('.').resolve()); print(json.dumps(report['summary'], ensure_ascii=False, indent=2))"`

结果：

- `unclassified: 0`
- `duplicate_truths: 0`
- `blocked_delete_candidates: 0`
- `archive_candidate: 11`
- `canonical: 21`
- `generated_reference: 11`
- `plan: 421`
- `report: 1010`
- `supporting: 602`

## Expected Effect

- 文档治理基线从“仍有大批目录未纳管”提升为“全局 markdown 已全部纳入生命周期分类”
- 后续可以把重点从“补分类”切换到“按 decision register 分波次归档/删除”
- canonical trunk 不再被大量未分类历史目录稀释
