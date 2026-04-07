# Change: Tech Debt Governance Baseline (2026Q1)

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why
Technical debt tracking exists but lacks a single source of truth, clear ownership, and execution cadence. This change establishes a governance baseline with measurable artifacts so debt work can be planned and verified.

## What Changes
- Define an architecture source-of-truth document for authoritative references.
- Introduce a spec conflict matrix with explicit statuses and owners.
- Establish a debt register with owner/DDL/next-action fields.
- Create execution artifacts (TASK board and reports) to drive weekly cadence.
- Add an OpenSpec capability delta for architecture governance requirements.

## Impact
- Affected specs: `architecture-governance` (new)
- Affected docs: `technical_debt/governance/*`, `TASK*.md`
- No runtime behavior changes in this proposal.
