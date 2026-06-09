# ML Training and Prediction Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a shared backend ML runtime for first-batch tabular-model training and one-step prediction, then expose it through canonical generic `/ml/*` pages and strategy-domain ML shell without leaving duplicate training/prediction truth sources behind.

**Architecture:** Keep one canonical runtime under `web/backend/app/services/ml_runtime/`, backed by one registry surface and one feature-assembly pipeline. Route both `web/backend/app/api/ml.py` and `web/backend/app/api/v1/strategy/machine_learning.py` through that runtime while keeping domain semantics separate. On the frontend, add real `/ml/training` and `/ml/prediction` pages with one shared API/composable/component layer, then add a strategy-domain ML shell that consumes the same runtime output and maps predicted returns into signals.

**Tech Stack:** OpenSpec, FastAPI, Pydantic, SQLAlchemy repository wrappers, existing `DataService`, existing `src/ml_strategy` helpers, Vue 3, Vue Router 4, existing ArtDeco UI primitives, Vitest, Playwright, `UnifiedResponse`.

---

## File Structure

### OpenSpec

- Create: `openspec/changes/add-ml-training-and-prediction-runtime/proposal.md`
  Purpose: justify the shared runtime and dual-shell scope.
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/design.md`
  Purpose: freeze the approved architecture from the design spec.
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/tasks.md`
  Purpose: OpenSpec execution checklist aligned to this implementation plan.
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/specs/ml-training-prediction-runtime/spec.md`
  Purpose: define first-batch runtime capability requirements.
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/specs/frontend-routing/spec.md`
  Purpose: add `/ml/training`, `/ml/prediction`, and strategy-domain ML route expectations.

### Backend shared runtime

- Create: `web/backend/app/services/ml_runtime/schemas.py`
  Purpose: define `FeatureProfile`, `TrainingJobSpec`, `PredictionJobSpec`, and `ModelRegistryRecord`.
- Create: `web/backend/app/services/ml_runtime/errors.py`
  Purpose: explicit runtime exceptions for schema mismatch, stale snapshot, unsupported symbol scope, and missing dependencies.
- Create: `web/backend/app/services/ml_runtime/feature_assembly.py`
  Purpose: build canonical feature tables using `DataService`, `feature_engineering_service`, and wrapped `src/ml_strategy` helpers.
- Create: `web/backend/app/services/ml_runtime/financial_snapshot_source.py`
  Purpose: canonical backend access surface for first-batch financial snapshot features.
- Create: `web/backend/app/services/ml_runtime/training.py`
  Purpose: train first-batch tabular models and persist artifacts.
- Create: `web/backend/app/services/ml_runtime/prediction.py`
  Purpose: reconstruct feature rows and return `analysis_date`, `predicted_return`, `predicted_price`, and `confidence`.
- Create: `web/backend/app/services/ml_runtime/registry.py`
  Purpose: canonical registry wrapper over existing algorithm-model persistence.
- Create: `web/backend/app/services/ml_runtime/runtime.py`
  Purpose: orchestration façade for generic and strategy shells.

### Backend persistence and compatibility

- Modify: `web/backend/app/repositories/algorithm_model_repository/helpers.py`
  Purpose: extend persistence models to carry `domain`, `symbol_scope`, `feature_schema`, `feature_schema_signature`, `target_name`, and `artifact_path`.
- Modify: `web/backend/app/repositories/algorithm_model_repository/algorithm_model_repository.py`
  Purpose: expose registry create/list/detail methods needed by the shared runtime.
- Modify: `web/backend/requirements.txt`
  Purpose: hard-pin first-batch required ML dependencies.
- Modify: `web/backend/app/services/ml_prediction_service.py`
  Purpose: mark as compatibility/deprecated wrapper after generic shell migration.

### Backend route shells

- Modify: `web/backend/app/api/ml.py`
  Purpose: route canonical generic endpoints through shared runtime and classify remaining auxiliary endpoints.
- Modify: `web/backend/app/api/v1/strategy/machine_learning.py`
  Purpose: route strategy training/predict/list through shared runtime while keeping `/backtest` out of first-batch closure.
- Modify: `web/backend/app/api/VERSION_MAPPING.py`
  Purpose: align stale singular/plural strategy prefix metadata if still present.

### Backend tests

- Create: `web/backend/tests/test_ml_runtime_feature_assembly.py`
- Create: `web/backend/tests/test_ml_runtime_registry.py`
- Create: `web/backend/tests/test_ml_runtime_training.py`
- Create: `web/backend/tests/test_ml_runtime_prediction.py`
- Create: `web/backend/tests/test_ml_api_routes.py`
- Create: `web/backend/tests/test_ml_strategy_runtime_routes.py`

### Frontend generic ML shell

- Create: `web/frontend/src/api/mlRuntime.ts`
  Purpose: shared API client for generic and strategy shells.
- Create: `web/frontend/src/types/mlRuntime.ts`
  Purpose: canonical frontend types for model registry, prediction result, feature schema, and stale metadata.
- Create: `web/frontend/src/views/ml/Training.vue`
- Create: `web/frontend/src/views/ml/Prediction.vue`
- Create: `web/frontend/src/views/ml/composables/useMlTrainingWorkbench.ts`
- Create: `web/frontend/src/views/ml/composables/useMlPredictionWorkbench.ts`

### Frontend shared ML components

- Create: `web/frontend/src/components/ml/MlModelOverviewCards.vue`
- Create: `web/frontend/src/components/ml/MlTrainingConfigPanel.vue`
- Create: `web/frontend/src/components/ml/MlModelRegistryTable.vue`
- Create: `web/frontend/src/components/ml/MlPredictionResultPanel.vue`
- Create: `web/frontend/src/components/ml/MlFeatureSchemaPanel.vue`
- Create: `web/frontend/src/components/ml/MlStaleState.vue`
- Create: `web/frontend/src/components/ml/MlErrorState.vue`
- Create: `web/frontend/src/components/ml/MlEmptyState.vue`

### Frontend routing and strategy shell

- Modify: `web/frontend/src/router/index.ts`
  Purpose: add real `/ml/training`, `/ml/prediction`, and `/strategy/ml` route entries.
- Modify: `web/frontend/src/config/pageConfig.ts`
  Purpose: add canonical page metadata for new ML pages.
- Modify: `web/frontend/src/config/menu.config.js`
  Purpose: keep generic ML entries aligned and add strategy-domain ML shell entry if needed.
- Create: `web/frontend/src/views/strategy/MachineLearning.vue`
  Purpose: strategy-domain ML shell that consumes shared runtime output and maps it to signals.

### Frontend tests

- Create: `web/frontend/src/api/__tests__/mlRuntime.spec.ts`
- Create: `web/frontend/src/views/ml/__tests__/Training.spec.ts`
- Create: `web/frontend/src/views/ml/__tests__/Prediction.spec.ts`
- Create: `web/frontend/src/views/strategy/__tests__/MachineLearning.spec.ts`
- Create: `web/frontend/src/components/ml/__tests__/MlComponents.spec.ts`
- Create: `web/frontend/tests/e2e/ml-runtime-workbench.spec.ts`

### Governance closeout

- Modify: `docs/FUNCTION_TREE.md`
  Purpose: promote `7.1 模型训练` and `7.1 预测推理` only after both shells and runtime are verified.

---

### Task 1: OpenSpec Change For Shared ML Runtime

**Files:**
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/proposal.md`
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/design.md`
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/tasks.md`
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/specs/ml-training-prediction-runtime/spec.md`
- Create: `openspec/changes/add-ml-training-and-prediction-runtime/specs/frontend-routing/spec.md`

- [ ] **Step 1: Write the failing OpenSpec capability deltas**

```md
## ADDED Requirements
### Requirement: Shared ML Training And Prediction Runtime
The system SHALL provide one canonical runtime for first-batch tabular-model feature assembly, training, model registration, and one-step prediction.

#### Scenario: Generic and strategy shells share one runtime
- **WHEN** a generic `/api/ml/*` endpoint or a strategy `/api/v1/strategies/*` endpoint requests training or prediction
- **THEN** the system SHALL adapt the request into one shared runtime contract
- **AND** SHALL NOT compute training or prediction through separate canonical engines
```

- [ ] **Step 2: Write the frontend-routing delta**

```md
## ADDED Requirements
### Requirement: Canonical Generic ML Workbench Routes
The system SHALL expose router-backed canonical generic ML workbench routes.

#### Scenario: Generic training page is opened
- **WHEN** the user opens `/ml/training`
- **THEN** the router SHALL render the canonical model-training workbench

#### Scenario: Generic prediction page is opened
- **WHEN** the user opens `/ml/prediction`
- **THEN** the router SHALL render the canonical one-step prediction workbench
```

- [ ] **Step 3: Validate the OpenSpec change**

Run:

```bash
openspec validate add-ml-training-and-prediction-runtime --strict
```

Expected:

```text
Change 'add-ml-training-and-prediction-runtime' is valid
```

- [ ] **Step 4: Commit the OpenSpec slice**

```bash
git add \
  openspec/changes/add-ml-training-and-prediction-runtime/proposal.md \
  openspec/changes/add-ml-training-and-prediction-runtime/design.md \
  openspec/changes/add-ml-training-and-prediction-runtime/tasks.md \
  openspec/changes/add-ml-training-and-prediction-runtime/specs/ml-training-prediction-runtime/spec.md \
  openspec/changes/add-ml-training-and-prediction-runtime/specs/frontend-routing/spec.md
git commit -m "docs(openspec): add ml runtime change"
```

### Task 2: Shared Runtime Schemas, Registry, And Feature Assembly

**Files:**
- Create: `web/backend/app/services/ml_runtime/schemas.py`
- Create: `web/backend/app/services/ml_runtime/errors.py`
- Create: `web/backend/app/services/ml_runtime/feature_assembly.py`
- Create: `web/backend/app/services/ml_runtime/financial_snapshot_source.py`
- Create: `web/backend/app/services/ml_runtime/registry.py`
- Modify: `web/backend/app/repositories/algorithm_model_repository/helpers.py`
- Modify: `web/backend/app/repositories/algorithm_model_repository/algorithm_model_repository.py`
- Test: `web/backend/tests/test_ml_runtime_feature_assembly.py`
- Test: `web/backend/tests/test_ml_runtime_registry.py`

- [ ] **Step 1: Write the failing schema and registry tests**

```python
def test_model_registry_record_uses_model_name_as_external_identifier():
    record = ModelRegistryRecord(
        model_name="a_share_lgbm_v1",
        model_family="lightgbm",
        domain="generic",
        symbol_scope=["600519.SH"],
        start_date="2024-01-01",
        end_date="2024-12-31",
        feature_schema={"columns": ["close", "volume"], "types": {"close": "numeric", "volume": "numeric"}},
        feature_schema_signature="close|volume",
        target_name="future_1d_return",
        validation_metrics={"rmse": 0.12},
        artifact_path="./models/a_share_lgbm_v1.pkl",
        created_at="2026-05-08T00:00:00Z",
        extra_metadata={},
    )
    assert record.model_name == "a_share_lgbm_v1"


def test_feature_assembly_rejects_future_feature_leakage():
    assembler = FeatureAssembler(...)
    with pytest.raises(FutureFeatureLeakageError):
        assembler._validate_effective_dates(feature_date="2024-01-03", label_date="2024-01-02")
```

- [ ] **Step 2: Run the failing tests**

Run:

```bash
pytest web/backend/tests/test_ml_runtime_feature_assembly.py web/backend/tests/test_ml_runtime_registry.py -q --no-cov
```

Expected:

```text
FAILED ... ModuleNotFoundError: No module named 'app.services.ml_runtime'
```

- [ ] **Step 3: Implement minimal shared schemas and errors**

```python
class ModelRegistryRecord(BaseModel):
    model_name: str
    model_family: Literal["lightgbm", "random_forest"]
    domain: Literal["generic", "strategy"]
    symbol_scope: list[str] | Literal["ALL"]
    start_date: date
    end_date: date
    feature_schema: dict[str, Any]
    feature_schema_signature: str
    target_name: Literal["future_1d_return"]
    validation_metrics: dict[str, float]
    artifact_path: str
    created_at: datetime
    extra_metadata: dict[str, Any] = Field(default_factory=dict)
```

- [ ] **Step 4: Implement feature assembly and financial snapshot adapter**

```python
class FeatureAssembler:
    def assemble(self, spec: FeatureAssemblySpec) -> pd.DataFrame:
        frame, _ = self.data_service.get_daily_ohlcv(spec.symbol, spec.start_date, spec.end_date)
        enriched = self.feature_service.prepare_model_data(frame, step=spec.step, include_indicators=True)
        financials = self.financial_source.load_snapshot(spec.symbol, spec.end_date)
        return self._merge_and_validate(enriched, financials)
```

- [ ] **Step 5: Extend existing algorithm-model persistence instead of inventing a new store**

```python
class AlgorithmModel(Base):
    __tablename__ = "algorithm_models"
    model_name = Column(String, primary_key=True)
    domain = Column(String, nullable=False, default="generic")
    symbol_scope = Column(JSON, nullable=False)
    feature_schema = Column(JSON, nullable=False)
    feature_schema_signature = Column(String, nullable=False)
    target_name = Column(String, nullable=False, default="future_1d_return")
    artifact_path = Column(String, nullable=False)
```

- [ ] **Step 6: Re-run schema and registry tests**

Run:

```bash
pytest web/backend/tests/test_ml_runtime_feature_assembly.py web/backend/tests/test_ml_runtime_registry.py -q --no-cov
```

Expected:

```text
2 passed
```

- [ ] **Step 7: Commit**

```bash
git add \
  web/backend/app/services/ml_runtime/schemas.py \
  web/backend/app/services/ml_runtime/errors.py \
  web/backend/app/services/ml_runtime/feature_assembly.py \
  web/backend/app/services/ml_runtime/financial_snapshot_source.py \
  web/backend/app/services/ml_runtime/registry.py \
  web/backend/app/repositories/algorithm_model_repository/helpers.py \
  web/backend/app/repositories/algorithm_model_repository/algorithm_model_repository.py \
  web/backend/tests/test_ml_runtime_feature_assembly.py \
  web/backend/tests/test_ml_runtime_registry.py
git commit -m "feat(ml): add shared runtime schemas and registry"
```

### Task 3: Shared Training And Prediction Runtime

**Files:**
- Create: `web/backend/app/services/ml_runtime/training.py`
- Create: `web/backend/app/services/ml_runtime/prediction.py`
- Create: `web/backend/app/services/ml_runtime/runtime.py`
- Modify: `web/backend/requirements.txt`
- Modify: `web/backend/app/services/ml_prediction_service.py`
- Test: `web/backend/tests/test_ml_runtime_training.py`
- Test: `web/backend/tests/test_ml_runtime_prediction.py`

- [ ] **Step 1: Write the failing runtime tests**

```python
def test_training_runtime_persists_model_and_registry_record(tmp_path):
    runtime = MlRuntime(...)
    result = runtime.train(job_spec)
    assert result.model_name == "a_share_lgbm_v1"
    assert result.validation_metrics["rmse"] >= 0


def test_prediction_runtime_returns_analysis_date_and_predicted_price():
    runtime = MlRuntime(...)
    result = runtime.predict(prediction_spec)
    assert result.analysis_date == date(2024, 12, 31)
    assert "predicted_return" in result.model_dump()
    assert "predicted_price" in result.model_dump()
```

- [ ] **Step 2: Run the failing runtime tests**

Run:

```bash
pytest web/backend/tests/test_ml_runtime_training.py web/backend/tests/test_ml_runtime_prediction.py -q --no-cov
```

Expected:

```text
FAILED ... ImportError or AttributeError for missing MlRuntime
```

- [ ] **Step 3: Pin mandatory dependencies**

```txt
lightgbm==4.6.0
scikit-learn==1.7.1
joblib==1.5.1
```

- [ ] **Step 4: Implement bounded synchronous training**

```python
class MlTrainingService:
    MAX_SYMBOLS = 50
    MAX_YEARS = 3

    def train(self, job: TrainingJobSpec) -> TrainingResult:
        self._guard_scope(job)
        dataset = self.assembler.build_training_dataset(job)
        model = self._fit_model(job.model_family, dataset.features, dataset.target)
        artifact_path = self._persist_model(job.model_name, model)
        record = self.registry.save_from_training(job, dataset, artifact_path, model)
        return TrainingResult.from_record(record)
```

- [ ] **Step 5: Implement prediction reconstruction and stale semantics**

```python
class MlPredictionService:
    def predict(self, job: PredictionJobSpec) -> PredictionResult:
        record = self.registry.get(job.model_name)
        sample = self.assembler.build_prediction_sample(record, job.symbol)
        predicted_return = float(self._load_model(record).predict(sample)[0])
        base_close = float(sample["close"].iloc[-1])
        return PredictionResult(
            analysis_date=sample["trade_date"].iloc[-1].date(),
            predicted_return=predicted_return,
            predicted_price=base_close * (1 + predicted_return),
            confidence=None,
            model_domain=record.domain,
        )
```

- [ ] **Step 6: Mark legacy generic service as compatibility-only**

```python
class MLPredictionService:
    """
    Legacy compatibility wrapper.
    New canonical training and prediction behavior lives under app.services.ml_runtime.
    """
```

- [ ] **Step 7: Re-run runtime tests**

Run:

```bash
pytest web/backend/tests/test_ml_runtime_training.py web/backend/tests/test_ml_runtime_prediction.py -q --no-cov
```

Expected:

```text
2 passed
```

- [ ] **Step 8: Commit**

```bash
git add \
  web/backend/requirements.txt \
  web/backend/app/services/ml_runtime/training.py \
  web/backend/app/services/ml_runtime/prediction.py \
  web/backend/app/services/ml_runtime/runtime.py \
  web/backend/app/services/ml_prediction_service.py \
  web/backend/tests/test_ml_runtime_training.py \
  web/backend/tests/test_ml_runtime_prediction.py
git commit -m "feat(ml): add shared training and prediction runtime"
```

### Task 4: Generic `/api/ml/*` Route Migration

**Files:**
- Modify: `web/backend/app/api/ml.py`
- Test: `web/backend/tests/test_ml_api_routes.py`

- [ ] **Step 1: Write the failing generic route tests**

```python
async def test_post_models_train_routes_through_shared_runtime(client, mock_runtime):
    response = await client.post("/api/ml/models/train", json=train_payload)
    assert response.status_code == 200
    assert response.json()["model_name"] == "a_share_lgbm_v1"


async def test_post_models_predict_returns_analysis_date(client, mock_runtime):
    response = await client.post("/api/ml/models/predict", json={"model_name": "a_share_lgbm_v1", "symbol": "600519.SH"})
    assert response.status_code == 200
    assert response.json()["analysis_date"] == "2024-12-31"
```

- [ ] **Step 2: Run the failing generic route tests**

Run:

```bash
pytest web/backend/tests/test_ml_api_routes.py -q --no-cov
```

Expected:

```text
FAILED ... response shape mismatch or runtime not called
```

- [ ] **Step 3: Route canonical endpoints through shared runtime and classify legacy endpoints**

```python
@router.post("/models/train", response_model=ModelTrainResponse)
async def train_model(...):
    result = runtime.train(_to_training_job_spec(request))
    return ModelTrainResponse(...)


@router.post("/models/predict", response_model=ModelPredictResponse)
async def predict_with_model(...):
    result = runtime.predict(_to_prediction_job_spec(request))
    return ModelPredictResponse(...)
```

- [ ] **Step 4: Preserve auxiliary endpoints without letting them become a second runtime**

```python
# keep /features/generate and /tdx/* as auxiliary discovery/inspection surfaces
# keep /models/evaluate and /models/hyperparameter-search behind explicit legacy comments
```

- [ ] **Step 5: Re-run generic route tests**

Run:

```bash
pytest web/backend/tests/test_ml_api_routes.py -q --no-cov
```

Expected:

```text
2 passed
```

- [ ] **Step 6: Commit**

```bash
git add web/backend/app/api/ml.py web/backend/tests/test_ml_api_routes.py
git commit -m "feat(ml): route generic ml api through shared runtime"
```

### Task 5: Strategy `/api/v1/strategies/*` Migration

**Files:**
- Modify: `web/backend/app/api/v1/strategy/machine_learning.py`
- Modify: `web/backend/app/api/VERSION_MAPPING.py`
- Test: `web/backend/tests/test_ml_strategy_runtime_routes.py`

- [ ] **Step 1: Write the failing strategy route tests**

```python
async def test_strategy_train_stores_domain_strategy_metadata(client, mock_runtime):
    response = await client.post("/api/v1/strategies/train", json=strategy_train_payload)
    assert response.status_code == 200
    assert response.json()["data"]["strategy_id"]


async def test_strategy_predict_returns_signal_and_predicted_return(client, mock_runtime):
    response = await client.post("/api/v1/strategies/predict", json=strategy_predict_payload)
    assert response.status_code == 200
    assert response.json()["data"]["prediction"]["signal"] in {"buy", "hold", "sell"}
    assert "predicted_return" in response.json()["data"]
```

- [ ] **Step 2: Run the failing strategy route tests**

Run:

```bash
pytest web/backend/tests/test_ml_strategy_runtime_routes.py -q --no-cov
```

Expected:

```text
FAILED ... route still uses old logic
```

- [ ] **Step 3: Adapt strategy routes to shared runtime while leaving `/backtest` alone**

```python
@router.post("/train")
async def train_ml_strategy(...):
    result = runtime.train(_to_strategy_training_job_spec(request))
    runtime_store.upsert(...)
    return UnifiedResponse(success=True, code=200, message="ML strategy trained", data={...})


@router.post("/predict")
async def generate_strategy_prediction(...):
    result = runtime.predict(_to_strategy_prediction_job_spec(request))
    signal = _map_predicted_return_to_signal(result.predicted_return, request.parameters)
    return UnifiedResponse(success=True, code=200, message="ML strategy prediction generated", data={...})
```

- [ ] **Step 4: Fix stale route metadata**

```python
VERSION_MAPPING["strategy"]["prefix"] = "/api/v1/strategies"
```

- [ ] **Step 5: Re-run strategy route tests**

Run:

```bash
pytest web/backend/tests/test_ml_strategy_runtime_routes.py -q --no-cov
```

Expected:

```text
2 passed
```

- [ ] **Step 6: Commit**

```bash
git add \
  web/backend/app/api/v1/strategy/machine_learning.py \
  web/backend/app/api/VERSION_MAPPING.py \
  web/backend/tests/test_ml_strategy_runtime_routes.py
git commit -m "feat(ml): route strategy ml api through shared runtime"
```

### Task 6: Generic Frontend Routes, Pages, And Shared Components

**Files:**
- Create: `web/frontend/src/api/mlRuntime.ts`
- Create: `web/frontend/src/types/mlRuntime.ts`
- Create: `web/frontend/src/views/ml/Training.vue`
- Create: `web/frontend/src/views/ml/Prediction.vue`
- Create: `web/frontend/src/views/ml/composables/useMlTrainingWorkbench.ts`
- Create: `web/frontend/src/views/ml/composables/useMlPredictionWorkbench.ts`
- Create: `web/frontend/src/components/ml/*.vue`
- Modify: `web/frontend/src/router/index.ts`
- Modify: `web/frontend/src/config/pageConfig.ts`
- Modify: `web/frontend/src/config/menu.config.js`
- Test: `web/frontend/src/api/__tests__/mlRuntime.spec.ts`
- Test: `web/frontend/src/views/ml/__tests__/Training.spec.ts`
- Test: `web/frontend/src/views/ml/__tests__/Prediction.spec.ts`
- Test: `web/frontend/src/components/ml/__tests__/MlComponents.spec.ts`

- [ ] **Step 1: Write the failing frontend shared-layer tests**

```ts
it('loads model registry rows with family and domain filters', async () => {
  const { loadModels, models } = useMlTrainingWorkbench()
  await loadModels({ modelFamily: 'lightgbm', domain: 'generic' })
  expect(models.value[0].modelName).toBe('a_share_lgbm_v1')
})
```

- [ ] **Step 2: Write the failing route/page tests**

```ts
it('renders canonical training page at /ml/training', async () => {
  const wrapper = await mountWithRouter('/ml/training')
  expect(wrapper.text()).toContain('模型训练')
})

it('renders canonical prediction page at /ml/prediction', async () => {
  const wrapper = await mountWithRouter('/ml/prediction')
  expect(wrapper.text()).toContain('价格预测')
})
```

- [ ] **Step 3: Run the failing frontend tests**

Run:

```bash
cd web/frontend && npx vitest run src/api/__tests__/mlRuntime.spec.ts src/views/ml/__tests__/Training.spec.ts src/views/ml/__tests__/Prediction.spec.ts src/components/ml/__tests__/MlComponents.spec.ts
```

Expected:

```text
FAILED ... Cannot find module '@/views/ml/Training.vue'
```

- [ ] **Step 4: Implement shared API/types/composables**

```ts
export async function trainMlModel(payload: MlTrainRequest): Promise<MlTrainResponse> {
  return api.post('/api/ml/models/train', payload).then(normalizeMlTrainResponse)
}

export function useMlPredictionWorkbench() {
  const result = ref<MlPredictionResult | null>(null)
  async function runPrediction(payload: MlPredictRequest) {
    result.value = await predictMlModel(payload)
  }
  return { result, runPrediction }
}
```

- [ ] **Step 5: Implement router-backed pages and shared components**

```vue
<template>
  <section class="ml-training-page">
    <MlTrainingConfigPanel @submit="trainModel" />
    <MlModelRegistryTable :rows="models" />
    <MlModelOverviewCards :summary="summary" />
  </section>
</template>
```

- [ ] **Step 6: Add real router/pageConfig entries**

```ts
{
  path: 'ml',
  redirect: '/ml/training',
  meta: { title: '模型训练', group: 'strategy' },
  children: [
    { path: 'training', name: 'ml-training', component: () => import('@/views/ml/Training.vue') },
    { path: 'prediction', name: 'ml-prediction', component: () => import('@/views/ml/Prediction.vue') },
  ]
}
```

- [ ] **Step 7: Re-run frontend tests**

Run:

```bash
cd web/frontend && npx vitest run src/api/__tests__/mlRuntime.spec.ts src/views/ml/__tests__/Training.spec.ts src/views/ml/__tests__/Prediction.spec.ts src/components/ml/__tests__/MlComponents.spec.ts
```

Expected:

```text
4 files passed
```

- [ ] **Step 8: Commit**

```bash
git add \
  web/frontend/src/api/mlRuntime.ts \
  web/frontend/src/types/mlRuntime.ts \
  web/frontend/src/views/ml/Training.vue \
  web/frontend/src/views/ml/Prediction.vue \
  web/frontend/src/views/ml/composables/useMlTrainingWorkbench.ts \
  web/frontend/src/views/ml/composables/useMlPredictionWorkbench.ts \
  web/frontend/src/components/ml \
  web/frontend/src/router/index.ts \
  web/frontend/src/config/pageConfig.ts \
  web/frontend/src/config/menu.config.js \
  web/frontend/src/api/__tests__/mlRuntime.spec.ts \
  web/frontend/src/views/ml/__tests__/Training.spec.ts \
  web/frontend/src/views/ml/__tests__/Prediction.spec.ts \
  web/frontend/src/components/ml/__tests__/MlComponents.spec.ts
git commit -m "feat(frontend): add generic ml workbench"
```

### Task 7: Strategy-Domain ML Shell And Closeout

**Files:**
- Create: `web/frontend/src/views/strategy/MachineLearning.vue`
- Test: `web/frontend/src/views/strategy/__tests__/MachineLearning.spec.ts`
- Test: `web/frontend/tests/e2e/ml-runtime-workbench.spec.ts`
- Modify: `docs/FUNCTION_TREE.md`

- [ ] **Step 1: Write the failing strategy-shell unit test**

```ts
it('maps shared predicted return into buy/hold/sell signal semantics', async () => {
  const wrapper = mount(StrategyMachineLearningPage, { ... })
  expect(wrapper.text()).toContain('策略型 ML')
  expect(wrapper.text()).toContain('signal')
})
```

- [ ] **Step 2: Write the failing Playwright smoke**

```ts
test('generic and strategy ML shells both render', async ({ page }) => {
  await page.goto('/ml/training')
  await expect(page.getByText('模型训练')).toBeVisible()
  await page.goto('/strategy/ml')
  await expect(page.getByText('策略型 ML')).toBeVisible()
})
```

- [ ] **Step 3: Run the failing strategy tests**

Run:

```bash
cd web/frontend && npx vitest run src/views/strategy/__tests__/MachineLearning.spec.ts
```

Expected:

```text
FAILED ... Cannot find module '@/views/strategy/MachineLearning.vue'
```

- [ ] **Step 4: Implement the strategy shell**

```vue
<template>
  <section class="strategy-ml-page">
    <MlTrainingConfigPanel :variant="'strategy'" @submit="trainStrategy" />
    <MlPredictionResultPanel :result="predictionResult" />
    <ArtDecoCard title="信号映射">
      <p>{{ signalLabel }}</p>
    </ArtDecoCard>
  </section>
</template>
```

- [ ] **Step 5: Update router/menu/page metadata for strategy shell**

```ts
{
  path: 'ml',
  name: 'strategy-ml',
  component: () => import('@/views/strategy/MachineLearning.vue'),
  meta: { title: 'ML策略', requiresAuth: true, api: '/api/v1/strategies' }
}
```

- [ ] **Step 6: Re-run unit and E2E tests**

Run:

```bash
cd web/frontend && npx vitest run src/views/strategy/__tests__/MachineLearning.spec.ts
cd web/frontend && npx playwright test tests/e2e/ml-runtime-workbench.spec.ts --project=chromium
```

Expected:

```text
1 passed
1 passed
```

- [ ] **Step 7: Update FUNCTION_TREE and archive OpenSpec after all runtime tests pass**

```md
| 模型训练 | ✅ | `web/frontend/src/views/ml/Training.vue`, `web/backend/app/services/ml_runtime/` | 通用训练工作台与共享运行时已闭环 |
| 预测推理 | ✅ | `web/frontend/src/views/ml/Prediction.vue`, `web/frontend/src/views/strategy/MachineLearning.vue`, `web/backend/app/services/ml_runtime/` | 通用预测与策略信号均已共享统一运行时 |
```

- [ ] **Step 8: Run final targeted verification**

Run:

```bash
pytest \
  web/backend/tests/test_ml_runtime_feature_assembly.py \
  web/backend/tests/test_ml_runtime_registry.py \
  web/backend/tests/test_ml_runtime_training.py \
  web/backend/tests/test_ml_runtime_prediction.py \
  web/backend/tests/test_ml_api_routes.py \
  web/backend/tests/test_ml_strategy_runtime_routes.py \
  -q --no-cov

cd web/frontend && npx vitest run \
  src/api/__tests__/mlRuntime.spec.ts \
  src/views/ml/__tests__/Training.spec.ts \
  src/views/ml/__tests__/Prediction.spec.ts \
  src/views/strategy/__tests__/MachineLearning.spec.ts \
  src/components/ml/__tests__/MlComponents.spec.ts

cd web/frontend && npx playwright test tests/e2e/ml-runtime-workbench.spec.ts --project=chromium

pytest tests/unit/governance/test_function_tree_doc_sync.py tests/unit/governance/test_function_tree_catalog.py -q --no-cov
openspec validate add-ml-training-and-prediction-runtime --strict
```

Expected:

```text
backend targeted tests: all passed
frontend targeted tests: all passed
playwright chromium: passed
governance tests: passed
OpenSpec change: valid
```

- [ ] **Step 9: Commit closeout**

```bash
git add \
  web/frontend/src/views/strategy/MachineLearning.vue \
  web/frontend/src/views/strategy/__tests__/MachineLearning.spec.ts \
  web/frontend/tests/e2e/ml-runtime-workbench.spec.ts \
  docs/FUNCTION_TREE.md
git commit -m "feat(ml): close training and prediction runtime"
```

---

## Self-Review

### Spec coverage

- Shared runtime contract: covered by Tasks 2 and 3
- Generic `/api/ml/*` closure: covered by Task 4
- Strategy `/api/v1/strategies/*` closure: covered by Task 5
- Generic `/ml/*` router truth: covered by Task 6
- Strategy-domain ML shell: covered by Task 7
- Dependency pinning: covered by Task 3
- `FUNCTION_TREE` closure: covered by Task 7
- OpenSpec creation and validation: covered by Task 1

### Placeholder scan

- No `TODO`, `TBD`, or "implement later" placeholders remain.
- Each code-bearing task includes concrete file paths, commands, and target snippets.

### Type consistency

- First-batch external identifier is consistently `model_name`.
- Shared runtime paths consistently use `web/backend/app/services/ml_runtime/`.
- Generic canonical routes consistently use `/api/ml/models/*`.
- Strategy canonical routes consistently use `/api/v1/strategies/*`.
