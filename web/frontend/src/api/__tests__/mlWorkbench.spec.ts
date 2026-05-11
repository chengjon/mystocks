import { describe, expect, it, vi, beforeEach } from 'vitest'

import { apiClient } from '../apiClient'
import {
  getMlRuntimeStatus,
  getMlWorkbenchModelDetail,
  listMlWorkbenchModels,
  predictMlWorkbenchModel,
  trainMlWorkbenchModel,
} from '../mlWorkbench'

vi.mock('../apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('mlWorkbench API client', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.post).mockReset()
  })

  it('calls canonical v1 ML workbench endpoints', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ success: true, code: 200, data: {} } as never)
    vi.mocked(apiClient.post).mockResolvedValue({ success: true, code: 200, data: {} } as never)

    await getMlRuntimeStatus()
    await listMlWorkbenchModels()
    await getMlWorkbenchModelDetail('svm_600519_abc')
    await trainMlWorkbenchModel({
      model_family: 'svm',
      symbol: '600519.SH',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      feature_window: 20,
      prediction_horizon: 5,
      parameters: {},
    })
    await predictMlWorkbenchModel({
      model_id: 'svm_600519_abc',
      symbol: '600519.SH',
      prediction_horizon: 5,
    })

    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/ml/runtime-status')
    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/ml/models')
    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/ml/models/svm_600519_abc')
    expect(apiClient.post).toHaveBeenCalledWith('/v1/strategies/ml/train', expect.objectContaining({ symbol: '600519.SH' }))
    expect(apiClient.post).toHaveBeenCalledWith('/v1/strategies/ml/predict', expect.objectContaining({ model_id: 'svm_600519_abc' }))
  })

  it('trims model detail IDs before encoding the canonical path', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ success: true, code: 200, data: {} } as never)

    await getMlWorkbenchModelDetail('  svm_600519_abc  ')

    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/ml/models/svm_600519_abc')
  })

  it('rejects blank model detail IDs before sending a request', async () => {
    await expect(getMlWorkbenchModelDetail('   ')).rejects.toThrow('Model ID is required')

    expect(apiClient.get).not.toHaveBeenCalled()
  })
})
