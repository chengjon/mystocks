# Change: add ML training and prediction workbench

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Why

`FUNCTION_TREE` still marks `7.1 机器学习策略 -> 模型训练` and `预测推理` as in progress. The repository already contains two partially overlapping ML surfaces:

- Legacy model-file endpoints under `/api/ml/models/*`, backed by optional `MLPredictionService` and LightGBM.
- v1 runtime strategy endpoints under `/api/v1/strategies/*`, backed by `UnifiedResponse` and runtime state.

The next mainline needs one canonical route and API contract for model training and prediction inference, while keeping existing compatibility surfaces intact. The first batch should make model training and inference observable, dependency-aware, and clearly scoped as analytical output rather than trading execution or investment advice.

## What Changes

- Add a canonical AI-domain workbench route at `/ai/ml`.
- Add a visible AI navigation entry labelled `模型训练 / 预测`.
- Add canonical v1 API surfaces for:
  - ML runtime capability/status checks.
  - Model training request submission and result reporting.
  - Prediction inference using a trained model.
  - Model artifact listing and detail inspection.
- Preserve `/api/ml/models/*` as legacy compatibility endpoints and avoid using them as the new page dependency.
- Reuse existing feature-engineering and ML services where practical, but harden the canonical surface around optional dependencies, missing data, insufficient samples, model metadata, and explicit error states.
- Treat predictions as analytical inference only; they SHALL NOT be represented as broker instructions, trade signals, or execution facts.
- Keep first-batch scope to supervised price/return prediction and runtime model observability; exclude automatic retraining, live streaming inference, broker integration, and production model governance.

## Impact

Affected specs:

- `ml-training-prediction`
- `frontend-routing`
- `function-tree-governance`

Affected code:

- `web/backend/app/api/v1/strategy/machine_learning.py`
- `web/backend/app/api/v1/strategy/__init__.py`
- `web/backend/app/api/ml.py` only for compatibility annotation if needed
- `web/backend/app/services/ml_prediction_service.py`
- `web/backend/app/services/feature_engineering_service.py`
- `web/backend/app/schemas/ml_schemas.py`
- `web/frontend/src/router/index.ts`
- `web/frontend/src/config/menu.config.js`
- `web/frontend/src/views/ai/`
- `web/frontend/src/api/`
- `docs/FUNCTION_TREE.md`
- Targeted backend and frontend tests for the new canonical surface

## Non-Goals

- No broker order creation, cancellation, or execution integration.
- No claim that a prediction is a trading recommendation.
- No automatic retraining loop in the first batch.
- No real-time streaming inference in the first batch.
- No Kronos training or fine-tuning responsibility in this change.
- No removal of existing `/api/ml/models/*` compatibility endpoints.
