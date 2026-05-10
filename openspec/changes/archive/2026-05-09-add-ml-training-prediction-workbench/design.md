# Design: ML training and prediction workbench

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Current State

There are two ML-related route families:

- `/api/ml/*` is an older compatibility family registered under `/api`. It exposes model file training, prediction, evaluation, feature generation, and TDX data helpers. It can fail at runtime when optional dependencies such as LightGBM are missing.
- `/api/v1/strategies/*` is a v1 family that returns `UnifiedResponse` and currently supports lightweight runtime strategy training, prediction, backtesting, and listing.

The frontend route truth currently exposes `/ai/sentiment` as the AI-domain workbench route. The menu configuration still contains historical `/ml/training` and `/ml/prediction` entries that are not active router truth.

## Canonical Direction

The first batch establishes `/ai/ml` and `/api/v1/strategies/ml/*` as the 7.1 canonical user and API surfaces.

The page presents one workflow:

1. Inspect runtime readiness and optional dependency status.
2. Configure a training request.
3. Submit training and inspect model metrics/artifact metadata.
4. Select a trained model.
5. Run prediction inference and inspect prediction metadata, input context, and warning states.

## API Shape

The canonical API SHOULD remain in the v1 strategy route family and return `UnifiedResponse`.

Recommended first-batch endpoints:

- `GET /api/v1/strategies/ml/runtime-status`
- `POST /api/v1/strategies/ml/train`
- `POST /api/v1/strategies/ml/predict`
- `GET /api/v1/strategies/ml/models`
- `GET /api/v1/strategies/ml/models/{model_id}`

Existing `/api/v1/strategies/train`, `/api/v1/strategies/predict`, `/api/v1/strategies/backtest`, and `/api/v1/strategies` can remain as compatibility/runtime strategy endpoints. They should not be the canonical page dependency after this change lands.

## Runtime And Dependency Contract

The canonical surface must degrade explicitly:

- Missing LightGBM or other optional ML dependency returns a machine-readable service-unavailable state.
- Missing market data returns a data-unavailable state.
- Insufficient rows for the requested feature window returns an insufficient-samples state.
- Missing or incompatible model metadata returns an explicit model-incompatible state.
- Prediction without a trained or loaded model is rejected.

The runtime-status endpoint should include at least:

- `service_available`
- `model_backend`
- `optional_dependencies`
- `model_dir`
- `model_dir_writable`
- `legacy_api_available`
- `supported_operations`
- `warnings`

## Model Artifact Contract

Training results should include:

- model identity
- requested symbol and date range
- feature window and feature columns
- train/test sample counts
- metrics
- artifact path or registry key
- generated timestamp
- warnings

Prediction results should include:

- model identity
- symbol
- prediction horizon
- generated timestamp
- input feature context
- prediction values
- confidence or explanation of missing confidence
- warnings

## Frontend Workbench

`/ai/ml` should be a dense operational workbench rather than a marketing or demo page. It should include:

- runtime readiness summary
- training form
- model list/detail panel
- prediction form
- training metrics
- prediction result table
- empty, loading, dependency-missing, insufficient-data, and error states

The page copy must state that predictions are analytical outputs and do not execute trades.

## Compatibility

`/api/ml/models/*` remains available for existing callers. The new page does not depend on it as canonical. If compatibility annotations are added, they should describe legacy status without changing the existing response models unless a separate migration is approved.

## Verification

Targeted verification should cover:

- OpenSpec validation.
- Backend contract tests for runtime status, training success, prediction success, and explicit failure modes.
- Frontend route/menu tests for `/ai/ml`.
- Frontend page tests for readiness, training, prediction, empty, and error states.
- E2E smoke for `/ai/ml` after route implementation.
- `FUNCTION_TREE` update only after API, page, tests, and safety text are all closed.
