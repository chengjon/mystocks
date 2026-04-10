## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Evidence-Based Frontend Route Truth
The system SHALL treat the current frontend runtime route truth as the evidence-backed chain
`web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts` unless an approved
change updates all linked entry surfaces together.

#### Scenario: Resolve the canonical runtime route chain
- **WHEN** an operator audits the live frontend route entry
- **THEN** they identify `web/frontend/index.html` as the HTML entry
- **AND** that entry loads `/src/main-standard.ts`
- **AND** `/src/main-standard.ts` resolves the live router at `/src/router/index.ts`

#### Scenario: Reject historical router files as live truth
- **GIVEN** historical router assets such as `src/router/index.js`, `src/router/index.js.clean`, `src/router/index.js.backup-phase2.3`, or `src/router/phase4.routes.js` still exist
- **WHEN** the project classifies current route truth
- **THEN** those files SHALL NOT be treated as the current runtime route source
- **AND** they SHALL be handled through lifecycle classification before archive or removal

### Requirement: Historical Route Asset Classification
The system SHALL classify non-canonical router files before they can be archived, relocated, or removed.

#### Scenario: Classify legacy router assets before cleanup
- **WHEN** a frontend closure batch evaluates non-canonical router files
- **THEN** each file SHALL receive an explicit lifecycle status such as historical backup, broken working copy, stale route asset, or retained historical reference
- **AND** cleanup SHALL wait until that status and its retirement conditions are recorded
