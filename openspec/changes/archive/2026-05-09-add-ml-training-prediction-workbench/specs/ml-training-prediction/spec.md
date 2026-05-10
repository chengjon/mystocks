## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

### Requirement: Canonical ML Training And Prediction Surface
The system SHALL provide a canonical v1 surface for `7.1 模型训练 / 预测推理`.

#### Scenario: Canonical API family is used
- **WHEN** a client performs first-batch ML training or prediction work
- **THEN** the client SHALL use the canonical `/api/v1/strategies/ml/*` route family
- **AND** the system SHALL return `UnifiedResponse` envelopes
- **AND** the legacy `/api/ml/models/*` route family SHALL remain compatibility-only

### Requirement: Runtime Readiness Reporting
The system SHALL expose machine-readable ML runtime readiness before training or prediction is attempted.

#### Scenario: Runtime status is requested
- **WHEN** the client calls `GET /api/v1/strategies/ml/runtime-status`
- **THEN** the response SHALL include service availability, model backend, optional dependency status, model directory status, supported operations, and warnings

#### Scenario: Optional ML dependency is missing
- **WHEN** an optional model backend dependency is unavailable
- **THEN** runtime status SHALL report the unavailable dependency
- **AND** train and predict requests SHALL fail with an explicit service-unavailable state
- **AND** the system SHALL NOT return an opaque internal server error for that dependency condition

### Requirement: Model Training Request Contract
The system SHALL support first-batch supervised model training requests with explicit data and feature context.

#### Scenario: Training succeeds
- **WHEN** a valid training request has enough market data and available ML runtime dependencies
- **THEN** the system SHALL train the model
- **AND** persist or register model artifact metadata
- **AND** return model identity, symbol scope, feature window, feature columns, sample counts, metrics, timestamp, and warnings

#### Scenario: Training data is insufficient
- **WHEN** the requested feature window cannot be built from available market data
- **THEN** the system SHALL return an explicit insufficient-samples error
- **AND** SHALL NOT persist a partial model artifact

### Requirement: Prediction Inference Contract
The system SHALL support prediction inference only through a trained or loadable model with compatible feature metadata.

#### Scenario: Prediction succeeds
- **WHEN** a valid prediction request references an existing trained model and compatible market data
- **THEN** the system SHALL return model identity, symbol, prediction horizon, generated timestamp, input feature context, prediction values, confidence or confidence-unavailable reason, and warnings

#### Scenario: Model is missing
- **WHEN** prediction references a model that cannot be loaded or found
- **THEN** the system SHALL return an explicit model-not-found error

#### Scenario: Feature contract is incompatible
- **WHEN** the model metadata cannot be matched to the generated prediction features
- **THEN** the system SHALL return an explicit model-incompatible error
- **AND** SHALL NOT return predictions computed from mismatched feature inputs

### Requirement: Prediction Safety Semantics
The system SHALL present ML prediction results as analytical inference only.

#### Scenario: Prediction result is displayed or returned
- **WHEN** the system returns or displays an ML prediction
- **THEN** it SHALL NOT describe the prediction as a broker instruction, executed trade, or guaranteed trading signal
- **AND** it SHALL include wording or metadata that distinguishes analytical prediction from trade execution

### Requirement: First-Batch Scope Limits
The system SHALL limit first-batch 7.1 delivery to supervised model training, prediction inference, model artifact inspection, and runtime readiness.

#### Scenario: Out-of-scope ML automation is requested
- **WHEN** a user expects automatic retraining, live streaming inference, production model governance, broker integration, or Kronos training/fine-tuning
- **THEN** the system SHALL treat that capability as out of first-batch scope
- **AND** SHALL NOT imply that it is completed by this change
