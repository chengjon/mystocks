import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiClient } from '../apiClient'
import {
  getBatchAnalysisRuntimeStatus,
  getBatchAnalysisTaskDetail,
  listBatchAnalysisTasks,
  submitBatchAnalysisTask,
} from '../batchAnalysis'

vi.mock('../apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('batchAnalysis API client', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.post).mockReset()
  })

  it('calls canonical v1 batch analysis endpoints', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ success: true, code: 200, data: {} } as never)
    vi.mocked(apiClient.post).mockResolvedValue({ success: true, code: 200, data: {} } as never)

    await getBatchAnalysisRuntimeStatus()
    await listBatchAnalysisTasks()
    await getBatchAnalysisTaskDetail('batch_abc')
    await submitBatchAnalysisTask({
      operation: 'batch_screening',
      symbols: ['600519.SH'],
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      options: {},
    })

    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/batch-analysis/runtime-status')
    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/batch-analysis/tasks')
    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/batch-analysis/tasks/batch_abc')
    expect(apiClient.post).toHaveBeenCalledWith(
      '/v1/strategies/batch-analysis/submit',
      expect.objectContaining({ operation: 'batch_screening' }),
    )
  })

  it('rejects blank task detail IDs before sending a request', async () => {
    await expect(getBatchAnalysisTaskDetail('   ')).rejects.toThrow('Batch analysis task ID is required')

    expect(apiClient.get).not.toHaveBeenCalled()
  })

  it('trims task detail IDs before encoding the canonical path', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ success: true, code: 200, data: {} } as never)

    await getBatchAnalysisTaskDetail('  batch_abc  ')

    expect(apiClient.get).toHaveBeenCalledWith('/v1/strategies/batch-analysis/tasks/batch_abc')
  })
})
