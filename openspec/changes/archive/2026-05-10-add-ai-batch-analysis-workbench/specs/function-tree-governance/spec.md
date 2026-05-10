## MODIFIED Requirements
> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

### Requirement: FUNCTION_TREE Status Updates Must Follow Evidence
`docs/FUNCTION_TREE.md` status changes SHALL reflect implemented and verified repository behavior rather than proposal intent.

#### Scenario: Mark capability complete
- **WHEN** a function-tree node is updated from in-progress to complete
- **THEN** the update SHALL cite or be backed by implementation evidence, tests, and route/API truth
- **AND** proposal-only or design-only work SHALL NOT be sufficient for completion status

#### Scenario: Mark 7.1 training and prediction complete
- **WHEN** `7.1 机器学习策略 -> 模型训练` and `预测推理` are marked complete
- **THEN** the canonical v1 API, `/ai/ml` workbench route, runtime readiness, model training, prediction inference, safety semantics, and targeted tests SHALL all be implemented and verified

#### Scenario: Mark 7.2 batch analysis complete
- **WHEN** `7.2 批量分析` is marked or kept complete
- **THEN** `FUNCTION_TREE.md` SHALL reference the canonical `/ai/batch` page and `/api/v1/strategies/batch-analysis/*` route family
- **AND** the evidence note SHALL preserve first-batch limits and safety semantics
