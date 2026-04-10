# Adjudication: consolidate-technical-debt-remediation

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `consolidate-technical-debt-remediation` 的阶段性裁定，不是仓库共享规则正文。
> 当前共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 当前为何不宜直接归档或直接删除。

## 1. Current Situation

`consolidate-technical-debt-remediation` 目前同时具备以下特征：

- 仍在 OpenSpec active list 中。
- 任务包试图把 4 个旧 change 合并为一个统一技术债执行盘。
- proposal 中声明要删除的 4 个源 change 目录现在都已经不存在于 active set。
- 仓内存在互相冲突的历史结论：
  - 某些检查报告把该 change 视为“fully complete”。
  - 当前 repo audit 又明确指出大量任务与能力并未在代码/验证中闭环。

## 2. Evidence

### Source-package drift

The proposal/tasks still treat the following as live merge sources:

- `improve-backend-code-quality`
- `remediate-phase7-technical-debt`
- `execute-phase6-tasks`
- `technical-debt-remediation`

But these are no longer present as active change directories. This means the consolidation package is now referencing a historical merge basis rather than a currently executable OpenSpec topology.

### Capability overlap with current trunks

The change introduces broad new capabilities such as:

- `code-quality-remediation`
- `test-coverage-enhancement`
- `architecture-optimization`
- `security-performance-hardening`

Those areas now overlap heavily with the current governance trunks already established through:

- `architecture/STANDARDS.md`
- `openspec/specs/code-quality/spec.md`
- `docs/standards/technical-debt-governance-charter-v1.md`
- `reports/governance/2026-04-10-tech-debt-governance-sot.md`

### Historical contradiction

Current repository evidence is inconsistent:

- `openspec/changes/check-report.md` claims the change is fully complete.
- `docs/reports/openspec_audit_summary.md` lists multiple major gaps: Pylint cleanup not verifiable, test coverage targets not verifiable, planned file splits not completed, security/performance remediation not evidenced.

This conflict means the package cannot be treated as a clean completed change.

## 3. Decision

Do **not** archive this change as completed.

Do **not** delete this change as a stale residual yet.

Current recommended status: **freeze and rebuild decision required**.

## 4. Why Not Archive

Archiving would be unsafe because it would promote broad, partially unverified remediation requirements into formal specs, creating new parallel capability trunks with unclear current ownership.

## 5. Why Not Delete Yet

Deleting would also be unsafe because this package still aggregates real unresolved technical-debt ambitions, and the current repo contains contradictory historical claims about what was already achieved. A deletion without replacement would erase that decision surface.

## 6. Recommended Next Move

Before any keep/remove action, perform one explicit rebuild choice:

1. **Retire-and-replace**
   - Freeze this umbrella package.
   - Create smaller bounded current-truth changes for the actually remaining debt areas.

2. **Narrow-and-reuse**
   - Strip this package down to only the still-unresolved scope that can be evidenced in the current repo.
   - Remove historical merged-source claims and broad speculative capabilities.

Given the current evidence, option **1. retire-and-replace** is the safer recommendation.

## 7. Immediate Rule For Future Sessions

Until that rebuild choice is made, treat `consolidate-technical-debt-remediation` as a **non-executable umbrella artifact**:

- do not continue its old 142-item checklist mechanically
- do not archive it as completed
- do not use it as the sole truth source for technical-debt priorities
