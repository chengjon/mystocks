## 1. OpenSpec

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

- [x] 1.1 Add `add-ml-training-prediction-workbench` proposal, design notes, tasks list, and spec deltas
- [x] 1.2 Validate `add-ml-training-prediction-workbench` with `openspec validate --strict`

## 2. Backend Canonical API

- [x] 2.1 Add canonical v1 ML runtime schemas and response examples
- [x] 2.2 Add `GET /api/v1/strategies/ml/runtime-status`
- [x] 2.3 Add `POST /api/v1/strategies/ml/train`
- [x] 2.4 Add `POST /api/v1/strategies/ml/predict`
- [x] 2.5 Add `GET /api/v1/strategies/ml/models`
- [x] 2.6 Add `GET /api/v1/strategies/ml/models/{model_id}`

## 3. Backend Runtime Hardening

- [x] 3.1 Normalize optional dependency checks into machine-readable runtime readiness
- [x] 3.2 Return explicit errors for missing data, insufficient samples, missing model, and incompatible model metadata
- [x] 3.3 Ensure prediction uses the trained model feature contract and rejects mismatched feature windows
- [x] 3.4 Preserve `/api/ml/models/*` compatibility and avoid making it the new canonical page dependency

## 4. Backend Tests

- [x] 4.1 Add contract tests for canonical route registration and `UnifiedResponse` response models
- [x] 4.2 Add runtime-status tests for dependency-available and dependency-unavailable states
- [x] 4.3 Add training tests for success and insufficient-sample failure
- [x] 4.4 Add prediction tests for success, missing model, and feature-contract mismatch

## 5. Frontend Workbench

- [x] 5.1 Add canonical `/ai/ml` route and AI navigation entry labelled `模型训练 / 预测`
- [x] 5.2 Add ML workbench API client and typed response normalization
- [x] 5.3 Add runtime readiness, training form, model list/detail, prediction form, metrics, result table, and warning/error states
- [x] 5.4 Ensure page copy states predictions are analytical outputs and do not execute trades
- [x] 5.5 Keep historical `/ml/training` and `/ml/prediction` menu entries from becoming active route truth unless a redirect/compatibility decision is explicitly approved

## 6. Frontend Tests

- [x] 6.1 Add router/menu tests for `/ai/ml`
- [x] 6.2 Add workbench unit tests for runtime readiness, training, prediction, empty state, and error state
- [x] 6.3 Add E2E smoke for `/ai/ml`

## 7. Governance And Closeout

- [x] 7.1 Run targeted backend tests
- [x] 7.2 Run targeted frontend tests
- [x] 7.3 Run route/layout E2E smoke through PM2 after frontend route changes
- [x] 7.4 Update `docs/FUNCTION_TREE.md` only after backend, frontend, safety wording, and tests are verified
- [x] 7.5 Archive the OpenSpec change after implementation is complete and validated
