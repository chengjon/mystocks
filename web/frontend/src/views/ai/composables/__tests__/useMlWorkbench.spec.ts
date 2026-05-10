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
    workbench.trainingForm.model_family = 'lightgbm'
    await workbench.submitTraining()

    expect(workbench.lastTrainingResult.value).toBeNull()
    expect(workbench.runtimeMessage.value).toContain("Optional ML dependency 'lightgbm'")
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
})
