import { describe, expect, it, vi, beforeEach } from 'vitest'

import {
  getMlRuntimeStatus,
  listMlWorkbenchModels,
  predictMlWorkbenchModel,
  trainMlWorkbenchModel,
} from '@/api/mlWorkbench.ts'

import { useMlWorkbench } from '../useMlWorkbench'

vi.mock('@/api/mlWorkbench.ts', () => ({
  getMlRuntimeStatus: vi.fn(),
  listMlWorkbenchModels: vi.fn(),
  predictMlWorkbenchModel: vi.fn(),
  trainMlWorkbenchModel: vi.fn(),
}))

const successfulRuntimeStatus = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    service_available: true,
    model_backend: 'runtime_registry',
    optional_dependencies: {
      lightgbm: { available: true, package: 'lightgbm' },
    },
    legacy_api_available: true,
    supported_operations: ['train', 'predict'],
    warnings: [],
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-runtime',
}

const lightgbmUnavailableRuntimeStatus = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    service_available: true,
    model_backend: 'runtime_registry',
    optional_dependencies: {
      lightgbm: { available: false, package: 'lightgbm' },
    },
    legacy_api_available: true,
    supported_operations: ['train', 'predict'],
    warnings: ['lightgbm_unavailable'],
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-runtime-lightgbm-unavailable',
}

const serviceUnavailableRuntimeStatus = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    service_available: false,
    model_backend: 'runtime_registry',
    optional_dependencies: {
      lightgbm: { available: true, package: 'lightgbm' },
    },
    legacy_api_available: true,
    supported_operations: ['train', 'predict'],
    warnings: ['runtime_unavailable'],
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-runtime-service-unavailable',
}

const trainUnsupportedRuntimeStatus = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    service_available: true,
    model_backend: 'runtime_registry',
    optional_dependencies: {
      lightgbm: { available: true, package: 'lightgbm' },
    },
    legacy_api_available: true,
    supported_operations: ['predict'],
    warnings: ['train_unsupported'],
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-runtime-train-unsupported',
}

const predictUnsupportedRuntimeStatus = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    service_available: true,
    model_backend: 'runtime_registry',
    optional_dependencies: {
      lightgbm: { available: true, package: 'lightgbm' },
    },
    legacy_api_available: true,
    supported_operations: ['train'],
    warnings: ['predict_unsupported'],
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-runtime-predict-unsupported',
}

const emptyModelList = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    models: [],
    total: 0,
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-models',
}

const populatedModelList = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    models: [
      {
        model_id: 'svm_600519_abc',
        model_family: 'svm',
        symbol: '600519.SH',
        artifact_status: 'runtime_registered',
        feature_context: { feature_window: 20, prediction_horizon: 5 },
        metrics: { validation_score: 0.61 },
      },
    ],
    total: 1,
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-models-populated',
}

const multiSymbolModelList = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    models: [
      {
        model_id: 'svm_600519_abc',
        model_family: 'svm',
        symbol: '600519.SH',
        artifact_status: 'runtime_registered',
        feature_context: { feature_window: 20, prediction_horizon: 5 },
        metrics: { validation_score: 0.61 },
      },
      {
        model_id: 'svm_000001_def',
        model_family: 'svm',
        symbol: '000001.SZ',
        artifact_status: 'runtime_registered',
        feature_context: { feature_window: 20, prediction_horizon: 5 },
        metrics: { validation_score: 0.58 },
      },
    ],
    total: 2,
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-models-multi-symbol',
}

const successfulTrainingResult = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    model_id: 'svm_600519_abc',
    model_family: 'svm',
    symbol: '600519.SH',
    artifact_status: 'runtime_registered',
    feature_context: { feature_window: 20, prediction_horizon: 5 },
    metrics: { validation_score: 0.61 },
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-train',
}

const successfulPredictionResult = {
  success: true,
  code: 200,
  message: 'ok',
  data: {
    model_id: 'svm_600519_abc',
    model_family: 'svm',
    symbol: '600519.SH',
    prediction_horizon: 5,
    feature_context: { feature_window: 20, prediction_horizon: 5 },
    prediction: { signal: 'buy', expected_return: 0.018, prediction_horizon: 5 },
    confidence: 0.72,
  },
  timestamp: '2026-05-10T00:00:00Z',
  request_id: 'req-ml-predict',
}

describe('useMlWorkbench', () => {
  beforeEach(() => {
    vi.mocked(getMlRuntimeStatus).mockReset()
    vi.mocked(listMlWorkbenchModels).mockReset()
    vi.mocked(trainMlWorkbenchModel).mockReset()
    vi.mocked(predictMlWorkbenchModel).mockReset()
    vi.mocked(getMlRuntimeStatus).mockResolvedValue(successfulRuntimeStatus)
    vi.mocked(listMlWorkbenchModels).mockResolvedValue(emptyModelList)
  })

  it('surfaces machine-readable training backend errors from UnifiedResponse', async () => {
    vi.mocked(trainMlWorkbenchModel).mockResolvedValue({
      success: false,
      code: 503,
      message: 'Request failed with status code 503',
      data: null,
      errors: {
        detail: {
          error_code: 'ml_backend_unavailable',
          dependency: 'lightgbm',
          message: "Optional ML dependency 'lightgbm' is required for lightgbm models.",
        },
      },
      timestamp: '2026-05-10T00:00:00Z',
      request_id: 'req-ml-train-failed',
    } as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    workbench.trainingForm.model_family = 'lightgbm'
    await workbench.submitTraining()

    expect(workbench.lastTrainingResult.value).toBeNull()
    expect(workbench.runtimeMessage.value).toContain("Optional ML dependency 'lightgbm'")
  })

  it('does not submit training when selected model family is blocked by runtime readiness', async () => {
    vi.mocked(getMlRuntimeStatus).mockResolvedValue(lightgbmUnavailableRuntimeStatus as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    workbench.trainingForm.model_family = 'lightgbm'
    await workbench.submitTraining()

    expect(trainMlWorkbenchModel).not.toHaveBeenCalled()
    expect(workbench.runtimeMessage.value).toContain('当前模型族后端依赖不可用')
  })

  it('does not submit training when runtime service is unavailable', async () => {
    vi.mocked(getMlRuntimeStatus).mockResolvedValue(serviceUnavailableRuntimeStatus as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    await workbench.submitTraining()

    expect(trainMlWorkbenchModel).not.toHaveBeenCalled()
    expect(workbench.runtimeMessage.value).toContain('ML runtime is unavailable')
  })

  it('does not submit training when runtime does not advertise train support', async () => {
    vi.mocked(getMlRuntimeStatus).mockResolvedValue(trainUnsupportedRuntimeStatus as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    await workbench.submitTraining()

    expect(trainMlWorkbenchModel).not.toHaveBeenCalled()
    expect(workbench.runtimeMessage.value).toContain('当前 ML 运行时不支持训练')
  })

  it('surfaces machine-readable prediction backend errors from UnifiedResponse', async () => {
    vi.mocked(predictMlWorkbenchModel).mockResolvedValue({
      success: false,
      code: 503,
      message: 'Request failed with status code 503',
      data: null,
      errors: {
        detail: {
          error_code: 'ml_backend_unavailable',
          dependency: 'lightgbm',
          message: "Optional ML dependency 'lightgbm' is required for lightgbm models.",
        },
      },
      timestamp: '2026-05-10T00:00:00Z',
      request_id: 'req-ml-predict-failed',
    } as never)

    const workbench = useMlWorkbench()
    workbench.predictionForm.model_id = 'lightgbm_model'
    await workbench.submitPrediction()

    expect(workbench.lastPredictionResult.value).toBeNull()
    expect(workbench.runtimeMessage.value).toContain("Optional ML dependency 'lightgbm'")
  })

  it('clears stale training result when a later training request fails', async () => {
    vi.mocked(trainMlWorkbenchModel)
      .mockResolvedValueOnce(successfulTrainingResult as never)
      .mockResolvedValueOnce({
        success: false,
        code: 400,
        message: 'Insufficient samples for ML training',
        data: null,
        timestamp: '2026-05-10T00:00:00Z',
        request_id: 'req-ml-train-failed',
      } as never)

    const workbench = useMlWorkbench()
    await workbench.submitTraining()
    expect(workbench.lastTrainingResult.value?.model_id).toBe('svm_600519_abc')

    await workbench.submitTraining()

    expect(workbench.lastTrainingResult.value).toBeNull()
    expect(workbench.runtimeMessage.value).toContain('Insufficient samples')
  })

  it('clears stale prediction result when a later prediction request fails', async () => {
    vi.mocked(predictMlWorkbenchModel)
      .mockResolvedValueOnce(successfulPredictionResult as never)
      .mockResolvedValueOnce({
        success: false,
        code: 404,
        message: 'Unknown model_id: missing_model',
        data: null,
        timestamp: '2026-05-10T00:00:00Z',
        request_id: 'req-ml-predict-failed',
      } as never)

    const workbench = useMlWorkbench()
    workbench.predictionForm.model_id = 'svm_600519_abc'
    await workbench.submitPrediction()
    expect(workbench.lastPredictionResult.value?.prediction.signal).toBe('buy')

    workbench.predictionForm.model_id = 'missing_model'
    await workbench.submitPrediction()

    expect(workbench.lastPredictionResult.value).toBeNull()
    expect(workbench.runtimeMessage.value).toContain('Unknown model_id')
  })

  it('clears selected model when refreshed registry becomes empty', async () => {
    vi.mocked(listMlWorkbenchModels)
      .mockResolvedValueOnce(populatedModelList as never)
      .mockResolvedValueOnce(emptyModelList)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    expect(workbench.selectedModelId.value).toBe('svm_600519_abc')
    expect(workbench.predictionForm.model_id).toBe('svm_600519_abc')

    await workbench.refreshRuntime()

    expect(workbench.models.value).toEqual([])
    expect(workbench.selectedModelId.value).toBe('')
    expect(workbench.predictionForm.model_id).toBe('')
  })

  it('clears stale registry selection when model list refresh fails', async () => {
    vi.mocked(listMlWorkbenchModels)
      .mockResolvedValueOnce(populatedModelList as never)
      .mockResolvedValueOnce({
        success: false,
        code: 503,
        message: 'ML model registry unavailable',
        data: null,
        timestamp: '2026-05-10T00:00:00Z',
        request_id: 'req-ml-models-failed',
      } as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    expect(workbench.models.value).toHaveLength(1)
    expect(workbench.selectedModelId.value).toBe('svm_600519_abc')

    await workbench.refreshRuntime()

    expect(workbench.models.value).toEqual([])
    expect(workbench.selectedModelId.value).toBe('')
    expect(workbench.predictionForm.model_id).toBe('')
    expect(workbench.runtimeMessage.value).toContain('ML model registry unavailable')
  })

  it('clears stale runtime readiness when runtime status refresh fails', async () => {
    vi.mocked(getMlRuntimeStatus)
      .mockResolvedValueOnce(successfulRuntimeStatus)
      .mockResolvedValueOnce({
        success: false,
        code: 503,
        message: 'ML runtime unavailable',
        data: null,
        timestamp: '2026-05-10T00:00:00Z',
        request_id: 'req-ml-runtime-failed',
      } as never)
    vi.mocked(listMlWorkbenchModels).mockResolvedValue(emptyModelList)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    expect(workbench.runtimeStatus.value?.service_available).toBe(true)
    expect(workbench.readinessLabel.value).toBe('运行时可用')

    await workbench.refreshRuntime()

    expect(workbench.runtimeStatus.value).toBeNull()
    expect(workbench.readinessLabel.value).toBe('运行时待检查')
    expect(workbench.runtimeMessage.value).toContain('ML runtime unavailable')
  })

  it('syncs prediction symbol when selecting a model from registry', async () => {
    vi.mocked(listMlWorkbenchModels).mockResolvedValue(multiSymbolModelList as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    expect(workbench.predictionForm.model_id).toBe('svm_600519_abc')
    expect(workbench.predictionForm.symbol).toBe('600519.SH')

    workbench.selectModel('svm_000001_def')

    expect(workbench.selectedModelId.value).toBe('svm_000001_def')
    expect(workbench.predictionForm.model_id).toBe('svm_000001_def')
    expect(workbench.predictionForm.symbol).toBe('000001.SZ')
  })

  it('syncs prediction symbol from training result when registry has not refreshed the new model', async () => {
    vi.mocked(listMlWorkbenchModels).mockResolvedValue(emptyModelList)
    vi.mocked(trainMlWorkbenchModel).mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: {
        model_id: 'svm_000001_new',
        model_family: 'svm',
        symbol: '000001.SZ',
        artifact_status: 'runtime_registered',
        feature_context: { feature_window: 20, prediction_horizon: 5 },
        metrics: { validation_score: 0.59 },
      },
      timestamp: '2026-05-10T00:00:00Z',
      request_id: 'req-ml-train-new',
    } as never)

    const workbench = useMlWorkbench()
    await workbench.submitTraining()

    expect(workbench.selectedModelId.value).toBe('svm_000001_new')
    expect(workbench.predictionForm.model_id).toBe('svm_000001_new')
    expect(workbench.predictionForm.symbol).toBe('000001.SZ')
  })

  it('does not submit prediction without a selected model', async () => {
    const workbench = useMlWorkbench()
    await workbench.submitPrediction()

    expect(predictMlWorkbenchModel).not.toHaveBeenCalled()
    expect(workbench.runtimeMessage.value).toContain('请先选择模型')
  })

  it('does not submit prediction when manual symbol differs from the selected model', async () => {
    vi.mocked(listMlWorkbenchModels).mockResolvedValue(multiSymbolModelList as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    workbench.selectModel('svm_600519_abc')
    workbench.predictionForm.symbol = '000001.SZ'
    await workbench.submitPrediction()

    expect(predictMlWorkbenchModel).not.toHaveBeenCalled()
    expect(workbench.runtimeMessage.value).toContain('预测标的必须与所选模型一致')
  })

  it('does not submit prediction when runtime service is unavailable', async () => {
    vi.mocked(getMlRuntimeStatus).mockResolvedValue(serviceUnavailableRuntimeStatus as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    workbench.predictionForm.model_id = 'svm_600519_abc'
    await workbench.submitPrediction()

    expect(predictMlWorkbenchModel).not.toHaveBeenCalled()
    expect(workbench.runtimeMessage.value).toContain('ML runtime is unavailable')
  })

  it('does not submit prediction when runtime does not advertise predict support', async () => {
    vi.mocked(getMlRuntimeStatus).mockResolvedValue(predictUnsupportedRuntimeStatus as never)

    const workbench = useMlWorkbench()
    await workbench.refreshRuntime()
    workbench.predictionForm.model_id = 'svm_600519_abc'
    await workbench.submitPrediction()

    expect(predictMlWorkbenchModel).not.toHaveBeenCalled()
    expect(workbench.runtimeMessage.value).toContain('当前 ML 运行时不支持预测')
  })
})
