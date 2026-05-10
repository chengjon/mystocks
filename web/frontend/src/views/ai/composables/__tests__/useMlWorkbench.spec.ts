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
})
