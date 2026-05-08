# ML Training and Prediction Runtime Design

> **权威来源声明**:
> 本文件是专题设计说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Context

`FUNCTION_TREE` currently marks `7.1 模型训练` and `7.1 预测推理` as unfinished.

Current repository truth is split across two partially overlapping surfaces:

- `web/backend/app/api/ml.py`
  - exposes generic ML endpoints for feature generation, training, model listing, evaluation, and prediction
  - still depends on optional `MLPredictionService`
  - behaves like a generic model-workbench surface rather than a strategy-domain surface
- `web/backend/app/api/v1/strategy/machine_learning.py`
  - exposes runtime ML strategy training, prediction, and listing
  - behaves like a strategy-specific signal surface rather than a generic model-workbench surface

Current frontend truth is also incomplete:

- `web/frontend/src/config/menu.config.js`
  - already contains `/ml/training` and `/ml/prediction`
- `web/frontend/src/router/index.ts`
  - does not currently mount canonical `/ml/training` or `/ml/prediction` routes
- there is no canonical `web/frontend/src/views/ml/` workbench surface

This means the repository currently has:

- duplicated ML-shaped backend capability
- missing canonical shared runtime
- menu truth that is ahead of router truth
- no user-facing dual-entry closure for `7.1`

The next feature should close `7.1 模型训练 / 预测推理` as a formal repo-local capability without collapsing generic prediction and strategy-domain ML into one mixed page or one mixed API.

## Goals

- Add one shared ML runtime for:
  - feature assembly
  - training
  - model registration
  - single-step prediction
- Keep two business entry shells:
  - generic prediction workbench
  - strategy-domain ML workbench
- Use only repo-local data sources in the first batch:
  - daily market data
  - technical indicator features
  - financial snapshot features
- Lock the first-batch learning target to:
  - `future_1d_return`
- Support first-batch tabular model families through the shared runtime.
- Add canonical frontend routes and pages for generic ML workbench entry:
  - `/ml/training`
  - `/ml/prediction`
- Keep strategy-side ML inside the strategy domain rather than moving it into a generic ML page.

## Non-Goals

- Do not merge generic prediction and strategy ML into one single platform page in the first batch.
- Do not bring `LSTM` or other deep time-series models into the first batch.
- Do not introduce external sample-import pipelines or warehouse-outside training sets.
- Do not connect realtime streaming data into the training loop.
- Do not implement multi-step horizon orchestration in the first batch.
- Do not merge `7.1` with `7.3 情感分析`, `Kronos`, or GPU training into one larger AI platform batch.
- Do not leave the current duplicated ML training/prediction logic as two long-term canonical implementations.

## Chosen Scope

The approved first-batch scope is:

- shared runtime plus dual entry-shell architecture
- tabular models only
- one supervised target only:
  - `future_1d_return`
- repo-local features only
- generic prediction routes remain under `/api/ml/*`
- strategy ML routes remain under `/api/v1/strategies/*`
- generic frontend workbench routes become canonical under `/ml/*`
- strategy ML shell stays under the strategy domain

## Capability Boundary

This feature adds one shared ML runtime and two business-domain shells.

### Shared runtime

The shared runtime is the only canonical training and prediction truth source.

It owns:

- feature assembly
- target generation
- dataset validation
- model training
- model artifact registration
- prediction execution

### Dual shells

The first batch intentionally keeps shell semantics separate:

- generic ML shell
  - user intent: train a model, inspect model registry, run one-step prediction
- strategy ML shell
  - user intent: train a strategy-oriented model, map predicted returns into signals, keep strategy context

### Explicit non-truth surfaces

The following existing surfaces are not the future canonical runtime:

- direct training/prediction logic embedded inside `web/backend/app/api/ml.py`
- direct training/prediction logic embedded inside `web/backend/app/api/v1/strategy/machine_learning.py`
- menu-only `/ml/*` entries without router-backed canonical pages

### Relationship to `src/ml_strategy/`

The repository already contains a substantial lower-level ML package under `src/ml_strategy/`. The first batch must not ignore it and accidentally create a third independent ML stack.

The intended layering is:

- `src/ml_strategy/`
  - lower-level ML and strategy implementation surface
  - reusable sources for feature engineering, tabular-model behavior, and strategy-side ML semantics
- `web/backend/app/services/ml_runtime/`
  - canonical web-backend orchestration layer
  - adapts web/API requests into shared runtime jobs
  - may reuse lower-level functionality from `src/ml_strategy/` where practical

First-batch implementation should explicitly evaluate reuse of:

- `src/ml_strategy/feature_engineering.py`
- `src/ml_strategy/price_predictor.py`
- `src/ml_strategy/ml_strategy.py`
- `src/ml_strategy/strategy/ml_strategy_base.py`

The shared runtime should consolidate duplicated behavior from the current web-backend surfaces. It should not leave `src/ml_strategy/` and `web/backend/app/services/ml_runtime/` as long-term parallel canonical training engines.

## Shared Runtime Contract

The shared runtime should live under:

- `web/backend/app/services/ml_runtime/`

and should become the only canonical location for model training and prediction behavior.

Recommended first-batch module split:

- `web/backend/app/services/ml_runtime/feature_assembly.py`
- `web/backend/app/services/ml_runtime/training.py`
- `web/backend/app/services/ml_runtime/prediction.py`
- `web/backend/app/services/ml_runtime/registry.py`
- `web/backend/app/services/ml_runtime/schemas.py`
- `web/backend/app/services/ml_runtime/runtime.py`

### 1. FeatureAssembly

`FeatureAssembly` is the canonical first-stage contract.

Input:

- `symbol_scope`
- `market`
- `start_date`
- `end_date`
- `feature_profile`

Output:

- one normalized feature table

At minimum the output should contain:

- `trade_date`
- `open`
- `high`
- `low`
- `close`
- `volume`
- selected technical-indicator columns
- selected financial snapshot columns

`feature_profile` must explicitly carry:

- selected feature names
- feature order
- feature type (`numeric` or `categorical`)
- missing-value handling policy

All feature rows must be assembled from information known at `T-1` relative to the label date. The runtime must not permit future-feature leakage.

### 2. TrainingDataset

`TrainingDataset` is derived from `FeatureAssembly` by adding one supervised target.

The target is fixed in the first batch:

- `future_1d_return = (close_t+1 - close_t) / close_t`

This target definition intentionally aligns with the repository's general interval-return math used elsewhere, even though `future_1d_return` itself is introduced as a new standardized target in this batch. The runtime should not switch to log-return semantics in the first batch.

If `T+1` is missing, incomplete, or suspended, that sample must be filtered out before training rather than imputed silently.

### 3. ModelRegistryRecord

The model registry is the only truth source for model listing, detail lookup, reproducibility, and cleanup.

At minimum each record must include:

- `model_name`
- `model_family`
- `domain`
  - `generic`
  - `strategy`
- `symbol_scope`
- `start_date`
- `end_date`
- `feature_schema`
- `feature_schema_signature`
- `target_name`
- `validation_metrics`
- `artifact_path`
- `created_at`
- `extra_metadata`

`model_name` is the first-batch external identifier and should stay aligned with the current generic ML API surface. An internal surrogate key may still exist in persistence storage, but it is not the canonical first-batch API selector.

`feature_schema_signature` should be immutable and derived from feature names, order, type, and missing-value policy. Prediction requests must be validated against it.

`symbol_scope` may represent:

- one symbol
- one explicit symbol list
- `ALL`

Prediction should only be allowed for symbols that fall within the model's training scope.

Artifact persistence may use local filesystem paths in the first batch, but the runtime should still expose a deterministic retention policy. The recommended implementation target is to retain only the most recent bounded set of artifacts per domain/model family rather than keep unbounded historical artifacts indefinitely.

Registry persistence should be explicit in the first batch:

- registry rows should be stored in PostgreSQL through the existing SQLAlchemy model stack
- model artifacts may remain on local filesystem paths in the first batch
- registry writes and artifact persistence should be treated as one logical operation, with failure handling defined so that partially persisted models do not appear as healthy registry rows

## Data Source Dependencies

The first batch should not invent a new ML data pipeline. It should assemble features from existing repo-local truth surfaces.

### Daily market data

Use the existing daily OHLCV data surfaces already available in the repository.

Canonical first-batch access surface:

- `web/backend/app/services/data_service.py`
  - `DataService.get_daily_ohlcv(...)`

This data provides:

- `open`
- `high`
- `low`
- `close`
- `volume`

### Technical indicator features

Use existing indicator and feature-engineering surfaces already present in the repository.

Canonical first-batch reuse targets:

- `src/ml_strategy/feature_engineering.py`
  - `RollingFeatureGenerator`
- `web/backend/app/services/feature_engineering_service.py`

The first batch may include indicators such as:

- RSI
- MACD
- moving averages
- Bollinger-derived features
- volatility-derived features

### Financial snapshot features

Use repo-local financial and fundamentals enrichment surfaces already exposed through the current adapter stack.

Canonical first-batch enrichment surfaces should be named explicitly during implementation, rather than left as generic "adapter stack" references. At minimum this includes the currently available web-backend data access surfaces plus the existing financial/fundamental adapter layer already used elsewhere in the repository.

The first batch may include features such as:

- PE
- PB
- ROE
- market-cap derived fields

### Factor and freshness discipline

All feature snapshots must be aligned to the effective analysis date and must avoid future functions.

For current prediction:

- if a same-day complete snapshot is not available, the system must fall back to the most recent complete trading day
- the chosen date must be surfaced as `analysis_date`

If the fallback snapshot is materially stale relative to the most recent complete trading day, the response should surface explicit freshness metadata instead of silently claiming fully current inference.

## Dependency Requirements

The first batch should not assume ML training dependencies are already available. Current backend requirements do not explicitly pin the shared-runtime packages required by the existing optional ML surfaces.

The design target is:

- `lightgbm`
  - required for the first-batch canonical regression path
- `scikit-learn`
  - required for RandomForest and shared metrics
- `joblib`
  - recommended for artifact serialization if selected by implementation
- `xgboost`
  - optional and dependency-gated in the first batch

The implementation plan should explicitly decide:

- which of these are mandatory for the first-batch runtime
- how missing optional dependencies are surfaced
- whether unsupported model families are rejected or hidden from the UI

## Training Flow

The first-batch training flow should be fixed as:

1. shell endpoint receives request
2. request is normalized into `TrainingJobSpec`
3. shared runtime builds `FeatureAssembly`
4. shared runtime derives `TrainingDataset`
5. runtime splits train and validation sets
6. runtime trains the selected tabular model family
7. runtime persists model artifact
8. runtime writes `ModelRegistryRecord`
9. runtime returns canonical training result

The first batch should treat training as a synchronous request/response flow for bounded job sizes. Oversized training scopes should be rejected by explicit request guardrails rather than silently turned into long-running blocking HTTP requests.

The implementation plan should define concrete first-batch limits such as:

- maximum symbol-scope breadth for synchronous jobs
- maximum historical window for synchronous jobs
- maximum sample-count or feature-table size before the request is rejected

The first-batch model families should be constrained to classic tabular models already compatible with repo-local execution. The implementation plan must lock the exact supported family set based on installed runtime dependencies, but the design target is:

- `lightgbm`
- `random_forest`
- optionally `xgboost` when dependency availability is confirmed

## Prediction Flow

The first-batch prediction flow should be fixed as:

1. shell endpoint receives request
2. runtime resolves the selected model record
3. runtime reconstructs the current feature row using the stored `feature_schema`
4. runtime validates the reconstructed sample against `feature_schema_signature`
5. runtime produces `predicted_return`
6. generic shell returns prediction-oriented output
7. strategy shell maps predicted return into signal-oriented output

Prediction responses must include:

- `analysis_date`
- `predicted_return`
- `predicted_price`
- `confidence` when supported by the model/runtime

`predicted_price` should be derived from the aligned current reference close and the predicted one-day return, not from a disconnected price source.

`top_contributors`/strategy-signal semantics are not owned by the shared runtime. Those belong to upper shells.

## API Contract

### Generic workbench shell

Keep the generic shell under the existing route family:

- `POST /api/ml/models/train`
- `GET /api/ml/models`
- `GET /api/ml/models/{model_name}`
- `POST /api/ml/models/predict`

#### POST /api/ml/models/train

Input should include:

- `symbol_scope`
- `market`
- `start_date`
- `end_date`
- `model_family`
- `feature_profile`

Output should include:

- `model_name`
- `model_family`
- `feature_summary`
- `validation_metrics`
- `analysis_window`

#### GET /api/ml/models

This surface should be backed exclusively by the shared registry and should support filtering by:

- `model_family`
- `domain`
- date range

#### GET /api/ml/models/{model_name}

Should return full model metadata, validation metrics, feature schema, and artifact status.

#### POST /api/ml/models/predict

Input should include:

- `model_name`
- `symbol`

Output should include:

- `analysis_date`
- `predicted_return`
- `predicted_price`
- `confidence`
- `model_domain`

### Strategy shell

Keep the strategy shell under the existing v1 route family:

- `POST /api/v1/strategies/train`
- `POST /api/v1/strategies/predict`
- `GET /api/v1/strategies`

These endpoints should stop owning independent training/prediction internals and instead adapt requests to the shared runtime.

The existing strategy-side `/backtest` surface remains outside the first-batch shared-runtime closure. This batch focuses on training, prediction, registry/listing, and signal mapping.

#### POST /api/v1/strategies/train

Input should include strategy-specific metadata such as:

- holding period
- threshold rules
- stop-loss settings
- additional strategy parameters

These fields should be stored in `extra_metadata`, not turned into a second independent training core.

#### POST /api/v1/strategies/predict

Output should include:

- `analysis_date`
- `predicted_return`
- `confidence`
- `signal`
- `expected_return`
- `prediction_horizon`

The first batch fixes `prediction_horizon = 1`.

### Compatibility and deprecation

After the shared runtime lands:

- existing direct training/prediction logic in `web/backend/app/api/ml.py`
- existing direct training/prediction logic in `web/backend/app/api/v1/strategy/machine_learning.py`

should be marked as deprecated compatibility paths if they still exist behind a fallback switch.

The repository should not keep two long-term canonical ML implementations.

## Frontend Design

### Route truth

The first batch must fix the current menu/router drift.

Current repo truth has:

- menu entries for `/ml/training` and `/ml/prediction`
- no canonical router-backed pages for them

The first batch should make them real canonical routes.

### Generic ML pages

Add:

- `web/frontend/src/views/ml/Training.vue`
- `web/frontend/src/views/ml/Prediction.vue`

These pages become the canonical generic ML workbench surfaces.

### Strategy-side shell

Do not create a new top-level strategy-ML route family in the first batch.

Instead, keep the strategy ML shell inside the existing strategy domain, preferably as a dedicated ML view/tab within the existing strategy workbench hierarchy.

### Shared frontend component skeleton

The first batch should add shared components such as:

- `MlModelOverviewCards.vue`
- `MlTrainingConfigPanel.vue`
- `MlModelRegistryTable.vue`
- `MlPredictionResultPanel.vue`
- `MlFeatureSchemaPanel.vue`
- `MlStaleState.vue`
- `MlErrorState.vue`
- `MlEmptyState.vue`

The first batch should also add named shared frontend orchestration surfaces:

- `web/frontend/src/api/mlRuntime.ts`
- `web/frontend/src/views/ml/composables/useMlTrainingWorkbench.ts`
- `web/frontend/src/views/ml/composables/useMlPredictionWorkbench.ts`

The generic shell and strategy shell should consume the same canonical composable/API client/result model. They may differ only in:

- copy and page framing
- parameter panels
- result interpretation
- strategy signal mapping

`MlModelRegistryTable.vue` should support at least:

- model-family filtering
- domain filtering
- date-range filtering

## Migration Plan

The migration should be explicit and staged.

### Phase 1

- introduce shared runtime
- route both shell families through it
- optionally preserve legacy logic behind compatibility fallback

### Phase 2

- verify runtime stability
- remove duplicate old training/prediction logic
- keep only thin shell adapters

Long-term coexistence of two independent ML engines is not acceptable.

## Testing Strategy

The first batch should lock at least five layers of verification.

### Shared runtime unit tests

Cover:

- `T-1` feature discipline
- `future_1d_return` label generation
- missing `T+1` sample filtering
- `feature_schema_signature` stability
- `symbol_scope` validation
- minimal registry metadata completeness

### Backend contract tests

Cover:

- `/api/ml/models/train`
- `/api/ml/models`
- `/api/ml/models/{model_name}`
- `/api/ml/models/predict`
- `/api/v1/strategies/train`
- `/api/v1/strategies/predict`
- `/api/v1/strategies`

Must include:

- success cases
- missing model
- schema mismatch
- insufficient historical data
- stale snapshot signaling
- compatibility fallback behavior

### Frontend unit tests

Cover:

- generic training-page form flow
- generic model-registry filtering
- generic prediction result rendering
- strategy-shell signal mapping
- stale/empty/error states

### E2E / smoke

Cover at minimum:

- open `/ml/training`
- train a minimal model
- open `/ml/prediction`
- run a prediction with the trained model
- open the strategy-domain ML shell
- verify shared runtime output is mapped into strategy signal output

### Performance / engineering tests

Cover:

- large feature-assembly smoke
- artifact write/read flow
- model-retention cleanup behavior

The implementation plan should set an explicit minimum large-sample smoke bar, such as multi-year training across a material stock universe, rather than leaving this as an unbounded aspiration.

## FUNCTION_TREE Closure

`7.1 模型训练` and `7.1 预测推理` should only move from `🚧` to `✅` when all of the following are true:

- `/ml/training` exists as a router-backed canonical page
- `/ml/prediction` exists as a router-backed canonical page
- strategy-domain ML shell is connected to the shared runtime
- shared runtime owns training, prediction, and model registry
- old parallel canonical training/prediction logic no longer remains as a second truth source
- prediction output stably returns:
  - `analysis_date`
  - `model_name`
  - `predicted_return`
  - `predicted_price`
  - strategy signal mapping

## OpenSpec Impact

This design implies a new OpenSpec change, recommended as:

- `add-ml-training-and-prediction-runtime`

Affected capabilities should include at least:

- a new `ml-training-prediction-runtime` capability
- `frontend-routing`
- relevant API contract/spec surfaces as needed

## Implementation Order

Recommended execution order:

1. create OpenSpec change
2. define shared runtime contract and registry surface
3. route `/api/ml/*` through shared runtime
4. route `/api/v1/strategies/*` through shared runtime
5. add canonical frontend `/ml/*` pages
6. connect strategy-domain ML shell
7. mark legacy logic deprecated and gate fallback paths
8. run test closure
9. update `FUNCTION_TREE`
10. archive OpenSpec change

This order keeps route truth, runtime truth, and shell truth from drifting again during implementation.
