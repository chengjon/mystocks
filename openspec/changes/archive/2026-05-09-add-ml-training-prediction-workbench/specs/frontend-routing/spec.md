## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

### Requirement: AI ML Training And Prediction Workbench Route
The frontend routing system SHALL expose a dedicated AI-domain ML training and prediction workbench route.

#### Scenario: User navigates to the ML workbench
- **WHEN** the user opens `/ai/ml`
- **THEN** the router SHALL load the canonical ML training and prediction workbench page
- **AND** that page SHALL be the AI-domain route truth source for `7.1 模型训练 / 预测推理`

### Requirement: AI Navigation Label For ML Workbench
The frontend navigation SHALL expose a visible AI entry for the canonical ML workbench.

#### Scenario: AI navigation label is rendered
- **WHEN** the frontend renders the active navigation surfaces
- **THEN** the menu SHALL include a `/ai/ml` entry labelled `模型训练 / 预测`
- **AND** the entry SHALL be grouped under the AI domain

### Requirement: Legacy ML Menu Entries Do Not Become Route Truth
Historical `/ml/training` and `/ml/prediction` entries SHALL NOT be treated as canonical route truth for first-batch 7.1 unless a separate compatibility decision is approved.

#### Scenario: Route truth is audited
- **WHEN** the project audits 7.1 frontend route truth
- **THEN** `/ai/ml` SHALL be treated as canonical
- **AND** historical `/ml/training` and `/ml/prediction` menu entries SHALL be classified as legacy or redirected explicitly before use
