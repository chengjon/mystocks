## ADDED Requirements
> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

### Requirement: AI Batch Analysis Workbench Route
The frontend routing system SHALL expose a dedicated AI-domain batch analysis workbench route.

#### Scenario: User navigates to the batch analysis workbench
- **WHEN** a user navigates to `/ai/batch`
- **THEN** the router SHALL render the canonical AI batch analysis workbench
- **AND** that page SHALL be the AI-domain route truth source for `7.2 批量分析`

### Requirement: AI Navigation Label For Batch Analysis Workbench
The frontend navigation SHALL expose a visible AI entry for the canonical batch analysis workbench.

#### Scenario: AI navigation label is rendered
- **WHEN** the frontend renders the active navigation surfaces
- **THEN** the menu SHALL include a `/ai/batch` entry labelled `批量分析`
- **AND** the entry SHALL be grouped under the AI domain
